# Los Angeles Public Transit Accessibility Analysis

## Project Summary

This project conducts a quantitative analysis of public transit accessibility across Los Angeles County using GTFS (General Transit Feed Specification) data. It applies temporal filtering, frequency analysis, and geospatial techniques to measure and visualize the service intensity of the LA Metro bus system. The primary output is an interactive heatmap that reveals spatial disparities in transit availability, allowing for data-driven insights into the region's transportation infrastructure. This README provides a detailed walkthrough of the methodology, key quantitative findings, and a summary of the analytical skills demonstrated.

## Key Quantitative Skills

*   **Statistical Analysis:** Frequency analysis, descriptive statistics (mean, median, min/max), and data aggregation to measure transit service levels.
*   **Data Engineering:** ETL (Extract, Transform, Load) processes for cleaning, filtering, and structuring large-scale GTFS schedule data for analysis.
*   **Geospatial Analysis:** Coordinate system reprojection (WGS84 to UTM), programmatic data acquisition from OpenStreetMap, and kernel density visualization (heatmap).
*   **Programming & Automation:** Scripting in Python with `pandas` and `geopandas` for data manipulation, and `gtfs-kit` for specialized transit data processing.
*   **Data Visualization:** Creation of interactive maps with `folium` to communicate complex spatial and quantitative data effectively.

## Methodology

The analysis is orchestrated by the `main.py` script, which follows a systematic, multi-stage methodology to ensure accuracy and reproducibility.

### 1. Data Ingestion and Preprocessing

*   **GTFS Data Extraction:** The script begins by extracting the LA Metro bus service data from the `gtfs_bus.zip` archive into a structured format using the `gtfs-kit` library.
*   **Geospatial Boundary Acquisition:** The official boundary for Los Angeles County is programmatically fetched from OpenStreetMap using the `osmnx` library. This data is saved as a GeoJSON file (`la_county_boundary.geojson`) to serve as the geographic container for the analysis. Caching is implemented to prevent redundant downloads.

### 2. Temporal Filtering and Service Frequency Analysis

To accurately quantify transit accessibility, the analysis focuses on a representative period of service.

*   **Defining a "Typical Weekday":** The script algorithmically identifies a representative weekday (Monday-Friday) by parsing the GTFS `calendar.txt` and `calendar_dates.txt` files. This controls for variations between weekday, weekend, and holiday schedules, ensuring the analysis reflects a standard service day.
*   **Temporal Filtering:** A time-based filter is applied to isolate bus trips occurring between **7:00 AM and 7:00 PM**. This 12-hour window was chosen to represent the core daytime hours when demand for transit is typically highest for work, appointments, and other daily activities.
*   **Frequency Aggregation:** For each unique transit stop, the script calculates the total number of bus trips that service it within the defined time window. This metric, **trips per stop**, serves as the primary quantitative measure of transit service intensity.

### 3. Geospatial Analysis and Visualization

*   **Coordinate System Reprojection:** To ensure accurate geospatial calculations, the LA County boundary is temporarily reprojected from the standard WGS84 (EPSG:4326) to a projected coordinate system (UTM Zone 10N, EPSG:26910). This allows for a precise calculation of the county's geographic centroid, which is used to center the map.
*   **Heatmap as Kernel Density Visualization:** The service frequencies are visualized using a heatmap. This technique is a form of **kernel density estimation**, where the "heat" at any given point on the map represents the density of bus trips. The intensity is weighted by the `num_trips` metric, providing a powerful visual summary of which areas have the highest concentration of transit service.
*   **Interactive Map Generation:** The final visualization is built using `folium`. The map includes the LA County boundary, the transit service heatmap, and a toggleable layer of individual bus stops with pop-up tooltips displaying the stop name and its specific trip count.

## Quantitative Results & Visualization

The analysis of the GTFS data for a typical weekday (7 AM - 7 PM) yielded the following key metrics:

*   **Total Transit Stops Analyzed:** 13,033
*   **Stops with Active Service:** 9,146 (70.2% of total stops)
*   **Total Bus Trips:** 105,978
*   **Service Frequency Distribution:**
    *   **Mean Trips per Stop:** 11.6
    *   **Median Trips per Stop:** 9
    *   **Maximum Trips at a Single Stop:** 226
    *   **Minimum Trips at an Active Stop:** 1

The primary output, `la_transit_accessibility_map.html`, provides an interactive platform to explore these results spatially. The heatmap clearly shows that transit service is heavily concentrated in the central and southern parts of Los Angeles County, while northern and more remote areas exhibit significantly lower service levels.

## How to Run the Project

1.  **Prerequisites:** Ensure you have Python 3.x installed.
2.  **Project Structure:** Your directory must contain `main.py`, `requirements.txt`, and a `data` directory with `gtfs_bus.zip`.
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Execute the Script:**
    ```bash
    python main.py
    ```
5.  **View the Map:** Open `data/la_transit_accessibility_map.html` in a web browser to explore the interactive visualization.