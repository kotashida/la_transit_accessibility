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

# Set up the file paths for our data.
DATA_DIR = "data"
GTFS_ZIP_PATH = os.path.join(DATA_DIR, "gtfs_bus.zip")
LA_COUNTY_BOUNDARY_PATH = os.path.join(DATA_DIR, "la_county_boundary.geojson") # This file will be created by OSMnx if it doesn't exist.
GTFS_EXTRACT_PATH = os.path.join(DATA_DIR, "gtfs_bus_extracted")

# Check if the GTFS data has already been extracted. If not, extract it from the zip file.
if not os.path.exists(GTFS_EXTRACT_PATH):
    with zipfile.ZipFile(GTFS_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(GTFS_EXTRACT_PATH)
    print(f"GTFS data extracted to {GTFS_EXTRACT_PATH}")
else:
    print(f"GTFS data already extracted to {GTFS_EXTRACT_PATH}")

# Load the LA County Boundary. If the GeoJSON file doesn't exist, download it using OSMnx and save it.
if not os.path.exists(LA_COUNTY_BOUNDARY_PATH):
    gdf = ox.geocode_to_gdf("Los Angeles County, California")
    gdf.to_file(LA_COUNTY_BOUNDARY_PATH, driver='GeoJSON')
    print("LA County boundary downloaded and saved.")
else:
    print("LA County boundary already exists.")

# Load the GTFS (General Transit Feed Specification) data into a feed object for analysis.
feed = gk.read_feed(GTFS_EXTRACT_PATH, dist_units='mi')
print("GTFS feed loaded.")

# Load the LA County boundary GeoJSON file into a GeoPandas DataFrame.
la_county_boundary = gpd.read_file(LA_COUNTY_BOUNDARY_PATH)
print("LA County boundary loaded.")

# Determine the service frequency for each transit stop.
# First, get all available service dates from the GTFS feed.
dates = feed.get_dates()
if not dates:
    raise ValueError("No service dates found in GTFS feed.")

# Find a typical weekday with active transit service to use for our analysis.
typical_weekday_date = None
for d in dates:
    date_dt_candidate = pd.to_datetime(d, format='%Y%m%d')
    weekday_name_candidate = date_dt_candidate.strftime('%A').lower()
    # Check if the current date is a weekday (Monday to Friday).
    if weekday_name_candidate in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        # Create a copy of the calendar DataFrame to check for active service on this specific date.
        calendar_df_candidate = feed.calendar.copy()
        calendar_df_candidate['start_date'] = pd.to_datetime(calendar_df_candidate['start_date'], format='%Y%m%d')
        calendar_df_candidate['end_date'] = pd.to_datetime(calendar_df_candidate['end_date'], format='%Y%m%d')

        # Identify service IDs that are active on this candidate weekday based on the calendar.
        active_service_ids_candidate = calendar_df_candidate[
            (calendar_df_candidate['start_date'] <= date_dt_candidate) &
            (calendar_df_candidate['end_date'] >= date_dt_candidate) &
            (calendar_df_candidate[weekday_name_candidate] == 1)
        ]['service_id'].tolist()

        # Account for exceptions to the regular service calendar (e.g., added or removed services).
        if feed.calendar_dates is not None and not feed.calendar_dates.empty:
            calendar_dates_df_candidate = feed.calendar_dates.copy()
            calendar_dates_df_candidate['date'] = pd.to_datetime(calendar_dates_df_candidate['date'], format='%Y%m%d')
            # Add services that are specifically added on this date.
            added_services_candidate = calendar_dates_df_candidate[
                (calendar_dates_df_candidate['date'] == date_dt_candidate) &
                (calendar_dates_df_candidate['exception_type'] == 1)
            ]['service_id'].tolist()
            active_service_ids_candidate.extend(added_services_candidate)
            # Remove services that are specifically removed on this date.
            removed_services_candidate = calendar_dates_df_candidate[
                (calendar_dates_df_candidate['date'] == date_dt_candidate) &
                (calendar_dates_df_candidate['exception_type'] == 2)
            ]['service_id'].tolist()
            active_service_ids_candidate = [sid for sid in active_service_ids_candidate if sid not in removed_services_candidate]

        # If we found active services for this weekday, we'll use it as our typical weekday.
        if active_service_ids_candidate:
            typical_weekday_date = d
            break

# If no typical weekday with active service is found after checking all dates, raise an error.
if not typical_weekday_date:
    raise ValueError("No typical weekday with active service found in GTFS feed.")

# Set the chosen typical weekday date for further calculations.
date = typical_weekday_date

# Prepare calendar data for the chosen typical weekday.
calendar_df = feed.calendar.copy()
calendar_df['start_date'] = pd.to_datetime(calendar_df['start_date'], format='%Y%m%d')
calendar_df['end_date'] = pd.to_datetime(calendar_df['end_date'], format='%Y%m%d')
date_dt = pd.to_datetime(date, format='%Y%m%d')
weekday_name = date_dt.strftime('%A').lower()

# Re-prepare calendar data (this block is a duplicate and can be removed if not intended).
calendar_df = feed.calendar.copy()
calendar_df['start_date'] = pd.to_datetime(calendar_df['start_date'], format='%Y%m%d')
calendar_df['end_date'] = pd.to_datetime(calendar_df['end_date'], format='%Y%m%d')
date_dt = pd.to_datetime(date, format='%Y%m%d')
weekday_name = date_dt.strftime('%A').lower()

# Get the service IDs that are active on the chosen typical weekday.
active_service_ids = calendar_df[
    (calendar_df['start_date'] <= date_dt) &
    (calendar_df['end_date'] >= date_dt) &
    (calendar_df[weekday_name] == 1)
]['service_id'].tolist()

# Incorporate calendar date exceptions (added or removed services) for the chosen date.
if feed.calendar_dates is not None and not feed.calendar_dates.empty:
    calendar_dates_df = feed.calendar_dates.copy()
    calendar_dates_df['date'] = pd.to_datetime(calendar_dates_df['date'], format='%Y%m%d')
    # Add services that are specifically added on this date.
    added_services = calendar_dates_df[
        (calendar_dates_df['date'] == date_dt) &
        (calendar_dates_df['exception_type'] == 1)
    ]['service_id'].tolist()
    active_service_ids.extend(added_services)
    # Remove services that are specifically removed on this date.
    removed_services = calendar_dates_df[
        (calendar_dates_df['date'] == date_dt) &
        (calendar_dates_df['exception_type'] == 2)
    ]['service_id'].tolist()
    active_service_ids = [sid for sid in active_service_ids if sid not in removed_services]

# Filter trips and stop times to only include those active on our chosen typical weekday.
trips_on_date = feed.trips[feed.trips['service_id'].isin(active_service_ids)].copy()
stop_times_filtered = feed.stop_times.merge(trips_on_date[['trip_id']], on='trip_id', how='inner')

# Helper function to convert time strings (HH:MM:SS) into total seconds for easier comparison.
def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

# Convert arrival times to seconds and filter for trips within the 7 AM to 7 PM range.
stop_times_filtered['arrival_sec'] = stop_times_filtered['arrival_time'].apply(time_to_seconds)
start_sec = time_to_seconds('07:00:00')
end_sec = time_to_seconds('19:00:00')
stop_times_in_range = stop_times_filtered[(stop_times_filtered['arrival_sec'] >= start_sec) & (stop_times_filtered['arrival_sec'] <= end_sec)]

# Calculate the number of unique trips (frequency) for each stop within the specified time range.
stop_frequencies = stop_times_in_range.groupby('stop_id')['trip_id'].nunique().reset_index(name='num_trips')

# Merge the calculated frequencies back into the stops DataFrame and create a GeoDataFrame.
stops = feed.stops.copy()
stops = stops.merge(stop_frequencies, on='stop_id', how='left')
stops['num_trips'] = stops['num_trips'].fillna(0) # Fill stops with no trips in the range with 0.
stops_gdf = gpd.GeoDataFrame(
    stops,
    geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat),
    crs="EPSG:4326" # Set the Coordinate Reference System to WGS84 (latitude/longitude).
)

# Prepare to visualize the results using Folium, an interactive mapping library.
# Ensure the LA County boundary is in the correct CRS (WGS84) for Folium.
la_county_boundary_4326 = la_county_boundary.to_crs(epsg=4326)

# Reproject the boundary to a suitable projected CRS (UTM Zone 10N for LA) to accurately calculate its centroid.
la_county_boundary_projected = la_county_boundary_4326.to_crs(epsg=26910)

# Calculate the centroid in the projected CRS, then reproject it back to WGS84 for use with Folium.
centroid_projected = la_county_boundary_projected.geometry.centroid
centroid_4326 = centroid_projected.to_crs(epsg=4326)
# Set the map's initial center to the calculated centroid of LA County.
map_center = [centroid_4326.y.mean(), centroid_4326.x.mean()]
# Create a Folium map centered on LA County with a dark matter basemap.
m = folium.Map(location=map_center, zoom_start=10, tiles="CartoDB dark_matter")

# Add the LA County boundary as a GeoJSON layer to the map.
folium.GeoJson(
    la_county_boundary_4326,
    name='LA County Boundary',
    style_function=lambda x: {'color': 'white', 'weight': 2, 'fillOpacity': 0} # Style the boundary line.
).add_to(m)

# Prepare the data for the heatmap: latitude, longitude, and the number of trips for each stop.
heat_data = [[row.stop_lat, row.stop_lon, row.num_trips] for idx, row in stops_gdf.iterrows() if row['num_trips'] > 0]

# Add a HeatMap layer to the map, showing areas with higher transit service frequency.
HeatMap(heat_data, name="Transit Service Heatmap", radius=15, blur=20).add_to(m)

# Add a separate layer for individual transit stops, which can be toggled on/off by the user.
transit_stops_layer = folium.FeatureGroup(name='Transit Stops', show=False)
# Iterate through stops with active trips and add them as circle markers to the map.
for idx, row in stops_gdf[stops_gdf['num_trips'] > 0].iterrows():
    folium.CircleMarker(
        location=[row.stop_lat, row.stop_lon],
        radius=2,
        color='cyan',
        fill=True,
        fill_color='cyan',
        fill_opacity=0.7,
        tooltip=f"Stop: {row.stop_name}<br>Trips: {int(row.num_trips)}"
    ).add_to(transit_stops_layer)
# Add the transit stops layer to the map.
transit_stops_layer.add_to(m)

# Add a layer control to the map, allowing users to toggle different layers (boundary, heatmap, stops).
folium.LayerControl().add_to(m)

# Define the output path for the interactive HTML map and save it.
map_output_path = os.path.join(DATA_DIR, "la_transit_accessibility_map.html")
m.save(map_output_path)
print(f"Interactive map saved to {map_output_path}")
