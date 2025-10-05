"""
Script to generate simulated route data using networkit.

Creates:
- 1000 nodes
- 40 routes per vehicle type (120 routes total)
- Each route has 10-20 connections
- Edge weights calculated based on node distance and vehicle type

Output: CSV file with route data
"""

import csv
import random
from math import sqrt

import networkit as nk

# Vehicle types and their weight divisors
VEHICLE_TYPES = {
    "TRAIN": 90,
    "TRAM": 60,
    "BUS": 40,
}

# Number of nodes in graph
NUM_NODES = 1000

# Routes per vehicle type
ROUTES_PER_TYPE = 40

# Connection range per route
MIN_CONNECTIONS = 10
MAX_CONNECTIONS = 20


def calculate_edge_weight(node1: int, node2: int, vehicle_divisor: int) -> float:
    """
    Calculate edge weight based on node distance and vehicle type.

    Formula: sqrt(|node1 - node2|) * 100 / vehicle_divisor

    Args:
        node1: First node ID
        node2: Second node ID
        vehicle_divisor: Vehicle type divisor (90 for train, 60 for tram, 40 for bus)

    Returns:
        Edge weight as float
    """
    distance = abs(node1 - node2)
    weight = (sqrt(distance) * 100) / vehicle_divisor
    return weight


def generate_route(graph: nk.Graph, num_connections: int, vehicle_type: str) -> list:
    """
    Generate a single route by randomly selecting connected nodes.

    Algorithm:
    1. Randomly select 2 initial nodes
    2. Second node becomes first node
    3. Randomly select new second node within distance 30 (not already visited, except for closing cycle)
    4. Repeat until desired number of connections

    Rules:
    - A node can only repeat if it's the first and last node (closed cycle)
    - Second node is always selected within distance 30 from current node

    Args:
        graph: NetworkIt graph object
        num_connections: Number of connections (edges) in this route
        vehicle_type: Type of vehicle (TRAIN, TRAM, or BUS)

    Returns:
        List of route segments (dicts with node pairs and weights)
    """
    vehicle_divisor = VEHICLE_TYPES[vehicle_type]
    route_segments = []
    visited_nodes = set()

    # Select first two random nodes
    first_node = random.randint(0, NUM_NODES - 1)

    # Select second node within distance 30 from first node
    min_node = max(0, first_node - 30)
    max_node = min(NUM_NODES - 1, first_node + 30)
    second_node = random.randint(min_node, max_node)

    # Ensure they're different
    while second_node == first_node:
        second_node = random.randint(min_node, max_node)

    # Track first node for potential cycle closure
    starting_node = first_node
    visited_nodes.add(first_node)
    visited_nodes.add(second_node)

    # Generate connections
    for i in range(num_connections):
        # Calculate weight
        weight = calculate_edge_weight(first_node, second_node, vehicle_divisor)

        # Add edge to graph if not exists
        if not graph.hasEdge(first_node, second_node):
            graph.addEdge(first_node, second_node, w=weight)
        else:
            # Update weight if edge exists
            graph.setWeight(first_node, second_node, weight)

        # Record segment
        route_segments.append(
            {
                "vehicle_type": vehicle_type,
                "connection_order": i + 1,
                "from_node": first_node,
                "to_node": second_node,
                "weight": round(weight, 2),
            }
        )

        # Second node becomes first node for next iteration
        first_node = second_node

        # Select new second node within distance 30
        min_node = max(0, first_node - 30)
        max_node = min(NUM_NODES - 1, first_node + 30)

        if i == num_connections - 1:
            # Last connection - can optionally close the cycle (20% chance)
            if random.random() < 0.2 and num_connections > 3:
                second_node = starting_node
            else:
                # Find unvisited node within distance 30
                second_node = random.randint(min_node, max_node)
                attempts = 0
                while second_node in visited_nodes and attempts < 100:
                    second_node = random.randint(min_node, max_node)
                    attempts += 1

                # If couldn't find in range, try full range
                if attempts >= 100:
                    second_node = random.randint(0, NUM_NODES - 1)
                    attempts2 = 0
                    while second_node in visited_nodes and attempts2 < 100:
                        second_node = random.randint(0, NUM_NODES - 1)
                        attempts2 += 1
        else:
            # Not last connection - must be unvisited node within distance 30
            second_node = random.randint(min_node, max_node)
            attempts = 0
            # Try to find unvisited node within distance 30 (max 100 attempts)
            while second_node in visited_nodes and attempts < 100:
                second_node = random.randint(min_node, max_node)
                attempts += 1

            # If we couldn't find unvisited node in range, expand search to full range
            if attempts >= 100:
                second_node = random.randint(0, NUM_NODES - 1)
                attempts2 = 0
                while second_node in visited_nodes and attempts2 < 100:
                    second_node = random.randint(0, NUM_NODES - 1)
                    attempts2 += 1

                # Last resort - just ensure it's different from current
                if attempts2 >= 100:
                    second_node = random.randint(0, NUM_NODES - 1)
                    while second_node == first_node:
                        second_node = random.randint(0, NUM_NODES - 1)

            visited_nodes.add(second_node)

    return route_segments


def generate_all_routes():
    """
    Generate all routes for all vehicle types.

    Returns:
        tuple: (graph, all_routes_data)
    """
    # Create weighted graph
    print(f"Creating graph with {NUM_NODES} nodes...")
    graph = nk.Graph(n=NUM_NODES, weighted=True, directed=False)

    all_routes_data = []
    route_id = 1

    # Generate routes for each vehicle type
    for vehicle_type, _ in VEHICLE_TYPES.items():
        print(f"\nGenerating {ROUTES_PER_TYPE} routes for {vehicle_type}...")

        for route_num in range(1, ROUTES_PER_TYPE + 1):
            # Random number of connections for this route
            num_connections = random.randint(MIN_CONNECTIONS, MAX_CONNECTIONS)

            # Generate route
            route_segments = generate_route(graph, num_connections, vehicle_type)

            # Add route_id to each segment
            for segment in route_segments:
                segment["route_id"] = route_id
                all_routes_data.append(segment)

            route_id += 1

            if route_num % 10 == 0:
                print(f"  Generated {route_num}/{ROUTES_PER_TYPE} routes")

    print(f"\n✓ Generated {len(all_routes_data)} total route segments")
    print(f"✓ Graph has {graph.numberOfEdges()} unique edges")

    return graph, all_routes_data


def save_to_csv(routes_data: list, filename: str = "simulated_routes.csv"):
    """
    Save route data to CSV file.

    Args:
        routes_data: List of route segment dictionaries
        filename: Output CSV filename
    """
    print(f"\nSaving data to {filename}...")

    fieldnames = [
        "route_id",
        "vehicle_type",
        "connection_order",
        "from_node",
        "to_node",
        "weight",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(routes_data)

    print(f"✓ Saved {len(routes_data)} route segments to {filename}")


def print_statistics(graph: nk.Graph, routes_data: list):
    """Print statistics about generated data."""
    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)
    print(f"Total nodes:           {graph.numberOfNodes()}")
    print(f"Total unique edges:    {graph.numberOfEdges()}")
    print(f"Total route segments:  {len(routes_data)}")

    # Count by vehicle type
    for vehicle_type in VEHICLE_TYPES.keys():
        count = sum(1 for r in routes_data if r["vehicle_type"] == vehicle_type)
        routes_count = count // (
            (MIN_CONNECTIONS + MAX_CONNECTIONS) // 2
        )  # Approximate
        print(f"  {vehicle_type:10s} routes: ~{routes_count} ({count} segments)")

    # Weight statistics
    weights = [r["weight"] for r in routes_data]
    print(f"\nWeight statistics:")
    print(f"  Min weight:  {min(weights):.2f}")
    print(f"  Max weight:  {max(weights):.2f}")
    print(f"  Avg weight:  {sum(weights)/len(weights):.2f}")
    print("=" * 60)


def main():
    """Main execution function."""
    print("=" * 60)
    print("ROUTE SIMULATION DATA GENERATOR")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Nodes:                 {NUM_NODES}")
    print(f"  Routes per type:       {ROUTES_PER_TYPE}")
    print(f"  Connections per route: {MIN_CONNECTIONS}-{MAX_CONNECTIONS}")
    print(f"  Vehicle types:         {', '.join(VEHICLE_TYPES.keys())}")
    print("=" * 60)

    # Set random seed for reproducibility
    random.seed(42)

    # Generate routes
    graph, routes_data = generate_all_routes()

    # Save to CSV
    save_to_csv(routes_data)

    # Print statistics
    print_statistics(graph, routes_data)

    print("\n✅ Route simulation data generation complete!")


if __name__ == "__main__":
    main()
