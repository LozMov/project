### Vancouver House Recommendation System

A notebook-driven project that scores and ranks Vancouver properties using:
- Address proximity (road-network distance via OSMnx)
- Neighborhood safety (weighted crime rates per neighborhood)
- Price, total floor area, year built, and lot size

The main workflow lives in `house_score_system.ipynb`, which contains mock user input and result visualization.


## Prerequisites
- Python 3.10 or newer (3.11 recommended)
- macOS, Linux, or Windows

OSMnx and GeoPandas have native dependencies. If pip wheels fail on your machine, prefer Conda (see Notes below).


## Setup

1) Clone the repository

```bash
git clone <your-repo-url>
cd 5800-project
```

2) Create and activate a virtual environment

- Using venv (pip):
```bash
python3 -m venv .venv
source ./.venv/bin/activate   # macOS/Linux
# .\.venv\Scripts\activate  # Windows PowerShell
```

3) Install dependencies

```bash
pip install -r requirements.txt
```

4) (Optional) Google Maps API key for geocoding

Only needed if you plan to run `address_score/get_coordinates.py` to geocode raw addresses. Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_api_key_here
```


## Data preparation

The notebook expects a houses dataset with latitude/longitude and a mapped neighborhood for each house.

- Neighborhood join (produces `get_neighborhoods/houses_with_neighborhoods.csv`):
```bash
python get_neighborhoods/get_neighborhoods.py
```
Inputs expected by this script (already included in the repo):
- `get_neighborhoods/local-area-boundary.xlsx` (neighborhood boundaries)
- `get_neighborhoods/house_with_coordinates.csv` (house coordinates)

- Safety data is read directly from `safety_score/` CSVs by the notebook code.

- The OSM road network cache (`greater_vancouver.graphml`) is generated automatically by the notebook if missing.

(Optional) If you need to geocode addresses from an input CSV yourself:
```bash
python address_score/get_coordinates.py
```
Edit `INPUT_FILE`/`OUTPUT_FILE` in that script or adapt your filenames. Requires `.env` with `GOOGLE_API_KEY`.


## Run the notebook

1) Launch Jupyter
```bash
jupyter lab   # or: jupyter notebook
```

2) Open `house_score_system.ipynb` and run cells top-to-bottom.
- The notebook will:
  - Ensure the Vancouver road network graph is cached (`greater_vancouver.graphml`)
  - Compute driving distances from a chosen origin (`start_coords`) to each house
  - Compute address proximity scores
  - Compute neighborhood safety scores and join them by neighborhood
  - Compute additional scores (price, area, year built, lot size)
  - Aggregate into a weighted composite score and display top recommendations

You can adjust `MIN_PRICE`/`MAX_PRICE` and scoring weights directly in the notebook cells.


## Notes and troubleshooting
- If pip installation of GeoPandas/OSMnx fails on your machine, use Conda:
```bash
conda create -n vancouver-house python=3.11 -y
conda activate vancouver-house
pip install -r requirements.txt
```
Alternatively, install key geospatial deps from conda-forge first, then `pip install osmnx`.

- Neighborhood spatial join uses GeoPandas/Shapely; `openpyxl` is required for reading the Excel boundary file.

- The safety scoring reads from `safety_score/crime_data_clean.csv`, `safety_score/crime_types.csv`, and `safety_score/population.csv`.


## Repository layout
- `house_score_system.ipynb`: Main end-to-end workflow
- `address_score/`: Distance and address scoring utilities
  - `network_cache.py`: Caches Greater Vancouver road network (`.graphml`)
  - `compute_distances.py`: Dijkstra-based road distance computation
  - `get_address_score.py`: Converts distances to address proximity scores
  - `get_coordinates.py`: Optional Google Geocoding helper
- `get_neighborhoods/`: Neighborhood mapping workflow
  - `get_neighborhoods.py`: Spatial join to add `Neighborhood` column
- `safety_score/`: Safety scoring and visualization
  - `safety_score.py`: Weighted crime rate and safety score computation
  - `visualization.py`: Visualization helper functions



## Optional: Distance Algorithm Comparison
You can benchmark different pathfinding approaches on the Vancouver road network in `address_score/distance_algorithm_comparison.ipynb`.

- Requirements: `numpy`, `tqdm` (both included in `requirements.txt`). To ensure everything is installed:
```bash
pip install -r requirements.txt
# Quick check (should print 'ok')
python - <<'PY'
import pandas, osmnx, networkx, numpy, tqdm
print('ok')
PY
```

- Working directory and imports:
  - Open the notebook from its folder (`address_score/distance_algorithm_comparison.ipynb`). Jupyter sets the working directory to the notebook’s directory, so relative imports like `from network_cache import cache_greater_vancouver_network` will work.
  - If you start Jupyter in a different CWD and see import/path errors, `cd address_score` before launching or adjust paths in the first cell.

- Inputs and outputs:
  - Reads `house_with_coordinates.csv` located in the same `address_score/` folder.
  - Will download/cache `greater_vancouver.graphml` on first run if missing (may take several minutes).
  - Saves `distance_comparison_results.csv` to the same `address_score/` folder.

- How to run:
  1) Start Jupyter and open `address_score/distance_algorithm_comparison.ipynb`
  2) Run all cells. It will:
     - Load/cache the road network
     - Compute distances via Dijkstra, A*, single-source Dijkstra variants
     - Save results to `address_score/distance_comparison_results.csv`

- Notes:
  - The "Fast Dijkstra (Vector)" approach should be significantly faster while matching Dijkstra distances within tolerance.
  - Large graph downloads can be slow depending on your connection; re-runs will use the cached GraphML.