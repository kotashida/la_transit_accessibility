import os
import zipfile
import geopandas as gpd
import gtfs_kit as gk
import pandas as pd
import osmnx as ox
from shapely.geometry import Polygon, Point
import numpy as np
import folium
from folium.plugins import HeatMap

# Define file paths
DATA_DIR = r"C:\Users\shida\OneDrive\Programming\la-transit-accessibility\data"
GTFS_ZIP_PATH = os.path.join(DATA_DIR, "gtfs_bus.zip")
LA_COUNTY_BOUNDARY_PATH = os.path.join(DATA_DIR, "la_county_boundary.geojson") # Will be created by osmnx
GTFS_EXTRACT_PATH = os.path.join(DATA_DIR, "gtfs_bus_extracted")

# Extract GTFS data
if not os.path.exists(GTFS_EXTRACT_PATH):
    with zipfile.ZipFile(GTFS_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(GTFS_EXTRACT_PATH)
    print(f"GTFS data extracted to {GTFS_EXTRACT_PATH}")
else:
    print(f"GTFS data already extracted to {GTFS_EXTRACT_PATH}")

# Load LA County Boundary using OSMnx
if not os.path.exists(LA_COUNTY_BOUNDARY_PATH):
    place = "Los Angeles County, California, USA"
    gdf = ox.geocode_to_gdf(place)
    gdf.to_file(LA_COUNTY_BOUNDARY_PATH, driver='GeoJSON')
    print("LA County boundary downloaded and saved.")
else:
    print("LA County boundary already exists.")

# Load GTFS data
feed = gk.read_feed(GTFS_EXTRACT_PATH, dist_units='mi')
print("GTFS feed loaded.")

# Load LA County Boundary
la_county_boundary = gpd.read_file(LA_COUNTY_BOUNDARY_PATH)
print("LA County boundary loaded.")

# Calculate service frequency for each stop
dates = feed.get_dates()
if not dates:
    raise ValueError("No service dates found in GTFS feed.")
date = dates[0]

calendar_df = feed.calendar.copy()
calendar_df['start_date'] = pd.to_datetime(calendar_df['start_date'], format='%Y%m%d')
calendar_df['end_date'] = pd.to_datetime(calendar_df['end_date'], format='%Y%m%d')
date_dt = pd.to_datetime(date, format='%Y%m%d')
weekday_name = date_dt.strftime('%A').lower()

active_service_ids = calendar_df[
    (calendar_df['start_date'] <= date_dt) &
    (calendar_df['end_date'] >= date_dt) &
    (calendar_df[weekday_name] == 1)
]['service_id'].tolist()

if feed.calendar_dates is not None and not feed.calendar_dates.empty:
    calendar_dates_df = feed.calendar_dates.copy()
    calendar_dates_df['date'] = pd.to_datetime(calendar_dates_df['date'], format='%Y%m%d')
    added_services = calendar_dates_df[
        (calendar_dates_df['date'] == date_dt) &
        (calendar_dates_df['exception_type'] == 1)
    ]['service_id'].tolist()
    active_service_ids.extend(added_services)
    removed_services = calendar_dates_df[
        (calendar_dates_df['date'] == date_dt) &
        (calendar_dates_df['exception_type'] == 2)
    ]['service_id'].tolist()
    active_service_ids = [sid for sid in active_service_ids if sid not in removed_services]

trips_on_date = feed.trips[feed.trips['service_id'].isin(active_service_ids)].copy()
stop_times_filtered = feed.stop_times.merge(trips_on_date[['trip_id']], on='trip_id', how='inner')

def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

stop_times_filtered['arrival_sec'] = stop_times_filtered['arrival_time'].apply(time_to_seconds)
start_sec = time_to_seconds('07:00:00')
end_sec = time_to_seconds('19:00:00')
stop_times_in_range = stop_times_filtered[(stop_times_filtered['arrival_sec'] >= start_sec) & (stop_times_filtered['arrival_sec'] <= end_sec)]
stop_frequencies = stop_times_in_range.groupby('stop_id')['trip_id'].nunique().reset_index(name='num_trips')
stops = feed.stops.copy()
stops = stops.merge(stop_frequencies, on='stop_id', how='left')
stops['num_trips'] = stops['num_trips'].fillna(0)
stops_gdf = gpd.GeoDataFrame(
    stops,
    geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat),
    crs="EPSG:4326"
)

# Visualize the results using Folium
la_county_boundary_4326 = la_county_boundary.to_crs(epsg=4326)
map_center = [la_county_boundary_4326.geometry.centroid.y.mean(), la_county_boundary_4326.geometry.centroid.x.mean()]
m = folium.Map(location=map_center, zoom_start=10, tiles="CartoDB dark_matter")

# Add LA County boundary
folium.GeoJson(
    la_county_boundary_4326,
    name='LA County Boundary',
    style_function=lambda x: {'color': 'white', 'weight': 2, 'fillOpacity': 0}
).add_to(m)

# Create heatmap data
heat_data = [[row.stop_lat, row.stop_lon, row.num_trips] for idx, row in stops_gdf.iterrows() if row['num_trips'] > 0]

# Add HeatMap layer
HeatMap(heat_data, name="Transit Service Heatmap", radius=15, blur=20).add_to(m)

# Add transit stops as a separate layer (optional, can be toggled)
transit_stops_layer = folium.FeatureGroup(name='Transit Stops', show=False)
for idx, row in stops_gdf.iterrows():
    if row['num_trips'] > 0:
        folium.CircleMarker(
            location=[row.stop_lat, row.stop_lon],
            radius=2,
            color='cyan',
            fill=True,
            fill_color='cyan',
            fill_opacity=0.7,
            tooltip=f"Stop: {row.stop_name}<br>Trips: {int(row.num_trips)}"
        ).add_to(transit_stops_layer)
transit_stops_layer.add_to(m)

# Add Layer Control
folium.LayerControl().add_to(m)

# Save the map
map_output_path = os.path.join(DATA_DIR, "la_transit_accessibility_map.html")
m.save(map_output_path)
print(f"Interactive map saved to {map_output_path}")
