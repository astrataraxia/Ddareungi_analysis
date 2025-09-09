# Research Findings for Seoul Public Bicycle "Ddareungi" Data Analysis

## 1. Project Management and Environment Setup

### Decision: `uv` for Project Management and Virtual Environments
- **Rationale**: `uv` is a modern, high-performance Python package and project manager written in Rust. It offers significantly faster package installation and dependency resolution (10-100x faster than `pip`), integrated virtual environment management, and `pip`-compatible interface. It is cross-platform and can manage multiple Python versions, making it an ideal choice for efficient and reproducible development.
- **Alternatives considered**: `pip`, `pip-tools`, `poetry`, `pyenv`, `virtualenv`. Rejected due to `uv`'s superior performance and integrated functionalities.

### Decision: Python 3.13
- **Rationale**: Python 3.13 was officially released on October 7, 2024, and includes significant performance improvements (experimental free-threaded CPython, JIT compiler), enhanced debugging tools, and a new interactive interpreter. Utilizing the latest stable version ensures access to the newest features and optimizations.
- **Alternatives considered**: Older Python versions. Rejected to leverage the latest advancements.

## 2. Data Analysis and Visualization Libraries

### Decision: `pandas` for Data Manipulation
- **Rationale**: `pandas` is the de facto standard for data manipulation and analysis in Python, providing powerful data structures like DataFrames and tools for reading/writing various data formats (including CSV and Parquet). It is essential for handling the Ddareungi usage data, population data, and bicycle station data.
- **Alternatives considered**: None, `pandas` is indispensable for this type of project.

### Decision: `matplotlib` and `seaborn` for Static Visualization
- **Rationale**: `matplotlib` provides foundational plotting capabilities and extensive customization, while `seaborn` builds on `matplotlib` to offer a higher-level interface for creating aesthetically pleasing and informative statistical graphics, especially useful for exploratory data analysis. They are complementary and widely used for generating static plots.
- **Alternatives considered**: Plotly, Bokeh. While powerful for interactive plots, `matplotlib` and `seaborn` are sufficient for initial static analysis and can be integrated with `streamlit` for interactivity.

### Decision: `streamlit` for Interactive Web Application and Dashboarding
- **Rationale**: `streamlit` allows for rapid development of interactive web applications directly from Python scripts without requiring front-end development knowledge. This is crucial for presenting the analysis results (e.g., hourly usage patterns, popular stations) in an accessible and interactive manner to stakeholders. It seamlessly integrates with `matplotlib` and `seaborn` plots.
- **Alternatives considered**: Dash, Flask/Django with custom frontend. Rejected due to `streamlit`'s ease of use and rapid prototyping capabilities, which align with the project's goal of efficient problem identification and solution proposal.

## 3. Geographic Information System (GIS) Libraries

### Decision: `geopandas` and `folium` for Geospatial Analysis and Visualization
- **Rationale**: `geopandas` extends `pandas` to enable spatial operations on geometric types, making it easy to work with vector geospatial data. This will be essential for analyzing bicycle station locations and routes. `folium` allows for the creation of interactive maps leveraging Leaflet.js, which is ideal for visualizing popular rental stations and routes on a map.
- **Alternatives considered**: `GDAL/OGR`, `Fiona`, `Shapely`, `Rasterio`, `PyProj` (for core data handling); `Cartopy`, `Geoplot`, `Geemap` (for visualization). While these are powerful, `geopandas` provides a high-level interface for common geospatial tasks, and `folium` is excellent for interactive web maps, which aligns with the `streamlit` dashboarding approach. Other libraries can be integrated if more specialized geospatial operations are required.
