import osmnx as ox


def cache_greater_vancouver_network(output_path='greater_vancouver.graphml'):
    print("Downloading Greater Vancouver road network...")
    G = ox.graph_from_place(
        "Metro Vancouver, British Columbia, Canada", network_type="drive")
    ox.save_graphml(G, output_path)
    print(f"Graph saved to {output_path}")
