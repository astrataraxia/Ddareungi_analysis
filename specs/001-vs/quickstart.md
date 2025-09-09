# Quickstart Guide: Setting up the Development Environment

This guide will walk you through setting up your development environment for the Seoul Public Bicycle "Ddareungi" Data Analysis project using `uv` and Python 3.13.


## Prerequisites

- Python 3.13 installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- `uv` already installed and available on system.

## 1. Create and Activate a Virtual Environment with uv

First, navigate to the project root directory (or the location where you want the environment), then create a new virtual environment with Python 3.13:

```bash
uv venv -p 3.13
```

Activate the virtual environment:

**On Windows:**

```bash
.venv\Scripts\activate
```

**On macOS/Linux:**

```bash
source .venv/bin/activate
```
## 2. Initialize the Project and Manage Dependencies with uv

Instead of using requirements.txt, initialize the project with uv:

```bash
uv init .
```

This will generate:
    - pyproject.toml → project configuration & dependencies
    uv.lock → locked dependency versions

To add dependencies (for example, pandas):
```bash
uv add pandas matplotlib seaborn streamlit geopandas folium ruff
```

## 3. Verify Installation

After adding the required dependencies, you can verify that the main libraries are installed by running a simple Python command:

```bash
python -c "import pandas; import matplotlib; import seaborn; import streamlit; import geopandas; import folium; print('All libraries installed successfully!')"
```

## 4. Linting and Formatting with Ruff

To ensure code quality and adherence to style guidelines, `ruff` is used for linting and formatting.

To check for linting issues:
```bash
uv run ruff check .
```

To automatically fix linting issues and format code:
```bash
uv run ruff format .
```

## 5. Running the Streamlit Application (Future Step)

When you initialize the project with uv init ., a main.py file is automatically created in the project root.
Later, during the implementation phase, you can build your Streamlit app logic directly inside this file.

To run the app:

```bash
streamlit run src/main.py
```

(Note: `src/main.py` is the main Streamlit application file once you implement the analysis and visualization components.)