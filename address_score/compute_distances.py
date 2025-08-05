# compute_distances.py

import os
import pandas as pd
import osmnx as ox
import networkx as nx
from tqdm import tqdm


def compute_road_distances(start_coords, house_csv_path="house_with_coordinates.csv", graph_filename="greater_vancouver.graphml"):
    """
    Compute driving distances from a start coordinate to all houses in a CSV.

    Parameters:
        start_coords (tuple): (lat, lon)
        house_csv_path (str): Path to the CSV file with Latitude and Longitude columns
        graph_filename (str): Name of the cached graphml file

    Returns:
        pd.DataFrame: Original DataFrame with added 'Driving_Distance_m' column
    """
    # Load cached graph
    graph_path = os.path.abspath(graph_filename)
    if not os.path.exists(graph_path):
        raise FileNotFoundError(
            f"Graph file '{graph_filename}' not found. Please run 'network_cache.py' first.")

    print("Loading Vancouver road network...")
    G = ox.load_graphml(graph_path)

    # Load house data
    df = pd.read_csv(house_csv_path)
    if not {'Latitude', 'Longitude'}.issubset(df.columns):
        raise ValueError(
            "CSV must contain 'Latitude' and 'Longitude' columns.")

    # Find start node
    start_node = ox.distance.nearest_nodes(
        G, X=start_coords[1], Y=start_coords[0])

    # Compute distances
    distances = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        try:
            house_coords = (row['Latitude'], row['Longitude'])
            house_node = ox.distance.nearest_nodes(
                G, X=house_coords[1], Y=house_coords[0])
            length = nx.shortest_path_length(
                G, start_node, house_node, weight='length')
        except Exception:
            length = None
        distances.append(length)

    df['Driving_Distance_m'] = distances
    return df
