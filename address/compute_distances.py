# compute_distances.py

import os
import pandas as pd
import osmnx as ox
import networkx as nx
from tqdm import tqdm

# -------------------------------
# Load cached graph
# -------------------------------
filename = "greater_vancouver.graphml"
graph_path = os.path.join(os.path.dirname(__file__), filename)

if not os.path.exists(graph_path):
    raise FileNotFoundError(
        f"Graph file '{filename}' not found. Please run 'network_cache.py' first.")

print("Loading Vancouver road network...")
G = ox.load_graphml(graph_path)

# -------------------------------
# Load house data with coordinates
# -------------------------------
df = pd.read_csv("house_with_coordinates.csv")
if not {'Latitude', 'Longitude'}.issubset(df.columns):
    raise ValueError("CSV must contain 'Latitude' and 'Longitude' columns.")

# -------------------------------
# Define the reference coordinate
# -------------------------------
start_coords = (49.28069261104817, -123.11572527879807)
start_node = ox.distance.nearest_nodes(G, X=start_coords[1], Y=start_coords[0])

# -------------------------------
# Compute distances using Dijkstra
# -------------------------------
distances = []
for _, row in tqdm(df.iterrows(), total=len(df)):
    try:
        house_coords = (row['Latitude'], row['Longitude'])
        house_node = ox.distance.nearest_nodes(
            G, X=house_coords[1], Y=house_coords[0])
        length = nx.shortest_path_length(
            G, start_node, house_node, weight='length')
    except Exception:
        length = None  # Node not found or path not reachable
    distances.append(length)

# -------------------------------
# Save results
# -------------------------------
df['Driving_Distance_m'] = distances
df.to_csv("House_with_road_distance.csv", index=False)
print("✅ Results saved to 'House_with_road_distance.csv'")
