# Los Angeles Public Transit Accessibility Map

## Project Overview

This project aims to analyze and visualize the accessibility of public transit across Los Angeles County. By leveraging GTFS (General Transit Feed Specification) data for bus services and geographic data for the county boundaries, it generates an interactive HTML map. The map visually represents transit service frequency, allowing users to identify areas with high or low bus accessibility during typical weekday daytime hours.

## Interactive Map Features

The primary output of this project is an interactive map, `la_transit_accessibility_map.html`, located in the `data` directory. This map offers the following interactive and visual elements:

*   **Basemap:** Utilizes a dark-themed "CartoDB dark_matter" basemap, providing a high-contrast background that enhances the visibility of the transit data layers.
*   **LA County Boundary:** Displays a distinct white outline of Los Angeles County, clearly delineating the area of analysis.
*   **Transit Service Heatmap:** A core feature, this layer visualizes the density and frequency of transit service. Brighter and more intense areas on the heatmap indicate a higher concentration of bus trips, signifying better transit accessibility. The intensity is weighted by the number of trips at each stop.
*   **Transit Stops (Toggleable Layer):** An optional layer showing individual transit stops as cyan circular markers. This layer can be toggled on/off using the layer control, providing flexibility for a cleaner map view or detailed stop-level information.
    *   **Pop-up Information:** When a transit stop marker is clicked, a pop-up displays:
        *   **Stop:** The official name of the transit stop.
        *   **Trips:** The calculated total number of bus trips servicing that specific stop between 7 AM and 7 PM on a typical weekday.

## Data Sources

The project relies on two main data sources:

*   **LA Metro GTFS Data (`gtfs_bus.zip`):** This compressed file contains the General Transit Feed Specification data for Los Angeles bus routes. It is the foundational dataset for extracting information about stop locations, route geometries, and detailed schedules. The `main.py` script extracts this data into the `data/gtfs_bus_extracted` directory.
*   **Los Angeles County Boundary (`la_county_boundary.geojson`):** The geographical boundary of Los Angeles County is programmatically fetched using the `osmnx` Python library. This library retrieves the data from OpenStreetMap (specifically, using the relation ID for Los Angeles County, California: 207359) and saves it as a GeoJSON file within the `data` directory. This ensures accurate spatial context for the analysis.

## Methodology

The `main.py` script orchestrates the entire analysis and map generation process, following these key steps:

1.  **Data Preparation and Loading:**
    *   **GTFS Extraction:** The `gtfs_bus.zip` file is automatically extracted into `data/gtfs_bus_extracted` if not already present.
    *   **LA County Boundary Acquisition:** The script checks for the existence of `la_county_boundary.geojson`. If it doesn't exist, `osmnx` is used to download the Los Angeles County boundary data from OpenStreetMap and save it. This step leverages caching to avoid redundant downloads.
    *   **Data Loading:** Both the extracted GTFS feed and the LA County boundary GeoJSON are loaded into appropriate data structures (using `gtfs_kit` for GTFS and `geopandas` for the GeoJSON).

2.  **Service Frequency Calculation:**
    *   **Typical Weekday Identification:** The script intelligently identifies a representative weekday (Monday-Friday) from the GTFS `calendar.txt` and `calendar_dates.txt` to ensure the analysis reflects regular service patterns.
    *   **Trip Filtering:** Bus trips are filtered to include only those operating on the identified typical weekday and arriving at stops between 7:00 AM and 7:00 PM (inclusive).
    *   **Stop Frequency Aggregation:** For each transit stop, the number of unique trips serving it within the specified time window is calculated. This count serves as the primary metric for transit accessibility.

3.  **Geospatial Processing and Map Data Preparation:**
    *   **Coordinate System Transformation:** The LA County boundary is reprojected to a suitable projected coordinate system (UTM Zone 10N, EPSG:26910) for accurate centroid calculation, then reprojected back to WGS84 (EPSG:4326) for compatibility with Folium.
    *   **Heatmap Data Structuring:** A list of data points is prepared for the heatmap, where each point includes the latitude, longitude, and the calculated number of trips for a given stop.

4.  **Interactive Map Visualization (Folium):**
    *   **Map Initialization:** An interactive Folium map is initialized, centered on the calculated centroid of Los Angeles County.
    *   **Layer Addition:** The LA County boundary is added as a GeoJSON layer. The transit service heatmap is added using `folium.plugins.HeatMap`. An optional `folium.FeatureGroup` is created for individual transit stops, allowing them to be toggled.
    *   **Layer Control:** A `folium.LayerControl` is added to the map, enabling users to switch between or hide different map layers.
    *   **Map Saving:** The final interactive map is saved as `la_transit_accessibility_map.html` in the `data` directory.

## How to Run the Project

To execute the analysis and generate the interactive transit accessibility map, follow these steps:

1.  **Prerequisites:** Ensure you have Python 3.x installed on your system.

2.  **Project Structure:** Verify that your project directory contains:
    *   `main.py` (the main script)
    *   `requirements.txt` (lists Python dependencies)
    *   A `data` directory containing `gtfs_bus.zip`.

3.  **Install Dependencies:** Open your terminal or command prompt, navigate to the project's root directory, and install all required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute the Script:** Run the main Python script from your terminal:
    ```bash
    python main.py
    ```
    The script will display progress messages in the console. It will download the LA County boundary (if not already cached) and process the GTFS data. Upon successful completion, it will save the interactive map.

5.  **View the Map:** Once the script finishes, open the generated HTML file in your web browser to explore the interactive visualization:
    ```
    data/la_transit_accessibility_map.html
    ```
    You can simply double-click the file in your file explorer or open it directly from your browser.