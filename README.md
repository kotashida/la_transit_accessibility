# Los Angeles Public Transit Accessibility Map

## Project Objective

This project analyzes and visualizes public transit accessibility across Los Angeles County. The primary goal is to create an interactive map that clearly illustrates the level of transit service available in different areas. Accessibility is quantified based on the frequency of bus services during peak daytime hours (7 AM to 7 PM) on a typical weekday.

The project serves as a practical example of geospatial analysis, demonstrating how to process and combine different types of data—GTFS for transit schedules and geographic data for county boundaries—to derive meaningful insights.

## Interactive Map Features

The output of this project is an interactive map (`la_transit_accessibility_map.html`) with the following features:

*   **Basemap:** Uses a dark-themed "CartoDB dark_matter" map to provide a high-contrast background for the heatmap.
*   **LA County Boundary:** A clear white outline of Los Angeles County.
*   **Transit Service Heatmap:** A heatmap layer that visualizes the concentration of transit service. The intensity of the heatmap is weighted by the number of trips at each stop, so brighter areas indicate a higher frequency of service.
*   **Transit Stops (Optional Layer):** A layer with cyan circular markers for each transit stop, which can be toggled on and off. This allows for a less cluttered view while still providing the option to see the exact location of stops.
    *   **Pop-up Information:** Clicking on a marker reveals a pop-up with:
        *   **Stop:** The official name of the transit stop.
        *   **Trips:** The total number of bus trips that service that stop between 7 AM and 7 PM on a typical weekday.

## Data Sources

*   **LA Metro GTFS Data:** The General Transit Feed Specification (GTFS) data for bus routes in Los Angeles. This dataset provides crucial information, including stop locations, route details, and schedules. It is sourced from the `gtfs_bus.zip` file.
*   **Los Angeles County Boundary:** The geographic boundary of Los Angeles County is obtained using the OSMnx library, which retrieves data from OpenStreetMap.

## Methodology

The analysis is performed in the `main.py` script and involves the following steps:

1.  **Data Extraction and Loading:**
    *   The GTFS data is extracted from the provided zip file.
    *   The LA County boundary is downloaded using OSMnx and saved as a GeoJSON file.

2.  **Service Frequency Calculation:**
    *   The script identifies a typical weekday from the GTFS feed.
    *   It calculates the number of trips that serve each transit stop between 7 AM and 7 PM on that day.

3.  **Heatmap Data Preparation:**
    *   The script creates a list of coordinates and weights, where each entry corresponds to a transit stop. The weight is the number of trips at that stop.

4.  **Interactive Map Visualization:**
    *   An interactive map is created using the Folium library.
    *   The map includes the LA County boundary, the transit service heatmap, and the optional layer of transit stops.
    *   The final map is saved as `la_transit_accessibility_map.html` in the `data` directory.

## How to Run the Project

To run the analysis and regenerate the map, follow these steps:

1.  **Ensure you have the required files:**
    *   `main.py`
    *   `requirements.txt`
    *   The `data` directory containing `gtfs_bus.zip`.

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the main script from the command line:**
    ```bash
    python main.py
    ```
    The script will print its progress to the console and, upon completion, will save the updated interactive map to `data/la_transit_accessibility_map.html`.

4.  **View the Map:**
    *   Open the `la_transit_accessibility_map.html` file in any modern web browser to explore the interactive visualization.
