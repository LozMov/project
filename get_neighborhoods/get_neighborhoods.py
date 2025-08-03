import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import shape

# 1. Load neighborhood boundaries from your Excel file
boundaries_df = pd.read_excel('local-area-boundary.xlsx')

# Parse the JSON in the 'Geom' column into real Polygon/MultiPolygon objects
boundaries_df['geometry'] = boundaries_df['Geom'].apply(
    lambda geojson_str: shape(json.loads(geojson_str))
)

# Turn it into a GeoDataFrame and set the CRS to WGS84 (lat/lon)
boundaries_gdf = gpd.GeoDataFrame(
    boundaries_df[['Name', 'geometry']],
    geometry='geometry',
    crs='EPSG:4326'
)

# 2. Load your house data
houses_df = pd.read_csv('house_with_coordinates.csv')

# Create Point geometries from the Latitude/Longitude columns
houses_gdf = gpd.GeoDataFrame(
    houses_df,
    geometry=gpd.points_from_xy(houses_df.Longitude, houses_df.Latitude),
    crs='EPSG:4326'
)

# 3. Spatial join: find which polygon (neighborhood) each house point falls within
houses_with_nbhd = gpd.sjoin(
    houses_gdf,
    boundaries_gdf[['Name', 'geometry']],
    how='left',
    predicate='within'
)

# 4. Clean up and save
# Rename the joined column for clarity
houses_with_nbhd = houses_with_nbhd.rename(columns={'Name': 'Neighborhood'})

# Drop the spatial join index column
houses_with_nbhd = houses_with_nbhd.drop(columns=['index_right'])

# Write out a CSV with a new 'Neighborhood' column
houses_with_nbhd.to_csv(
    'houses_with_neighborhoods.csv',
    index=False
)

print("Saved houses_with_neighborhoods.csv with an added ‘Neighborhood’ column.")
