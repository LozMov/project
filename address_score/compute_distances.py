# compute_distances.py

import os
import pandas as pd
import osmnx as ox
import networkx as nx


def compute_road_distances(start_coords, house_csv_path="house_with_coordinates.csv", graph_filename="greater_vancouver.graphml"):
    """
    Compute driving distances from a start coordinate to all houses using fast Dijkstra.

    Parameters:
        start_coords (tuple): (lat, lon)
        house_csv_path (str): Path to the CSV file with Latitude and Longitude columns
        graph_filename (str): Name of the cached graphml file

    Returns:
        pd.DataFrame: Original DataFrame with added 'Driving_Distance_m' column
    """
    # Load graph
    graph_path = os.path.abspath(graph_filename)
    if not os.path.exists(graph_path):
        raise FileNotFoundError(
            f"Graph file '{graph_filename}' not found. Please run 'network_cache.py' first.")

    print("Loading Vancouver road network...")
    G = ox.load_graphml(graph_path)

    # Load house dataset
    df = pd.read_csv(house_csv_path)
    if not {'Latitude', 'Longitude'}.issubset(df.columns):
        raise ValueError(
            "CSV must contain 'Latitude' and 'Longitude' columns.")

    # Get start node from user's coordinates
    start_node = ox.distance.nearest_nodes(
        G, X=start_coords[1], Y=start_coords[0])

    print("Running fast Dijkstra (single-source)...")
    # Compute shortest paths from start node to all reachable nodes
    path_lengths = nx.single_source_dijkstra_path_length(
        G, start_node, weight='length')

    # Vectorized nearest node lookup for all house locations
    house_nodes = ox.distance.nearest_nodes(
        G,
        X=df['Longitude'].values,
        Y=df['Latitude'].values,
        return_dist=False
    )

    # Map each house node to its shortest path length
    distances = [path_lengths.get(node, None) for node in house_nodes]

    # Save to DataFrame
    df['Driving_Distance_m'] = distances

    return df
