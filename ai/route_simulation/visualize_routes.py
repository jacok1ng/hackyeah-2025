"""
Script to visualize simulated route data from CSV.

Reads simulated_routes.csv and creates visualizations:
- Graph with all routes
- Separate graphs for each vehicle type
- Weight distribution histogram
- Route statistics
"""

import csv
from collections import defaultdict

import matplotlib.pyplot as plt
import networkit as nk
import numpy as np


# Colors for different vehicle types
VEHICLE_COLORS = {
    "TRAIN": "#FF6B6B",  # Red
    "TRAM": "#4ECDC4",   # Teal
    "BUS": "#FFE66D",    # Yellow
}


def load_routes_from_csv(filename: str = "simulated_routes.csv"):
    """
    Load route data from CSV file.
    
    Returns:
        dict: Routes organized by vehicle type
              {vehicle_type: [(route_id, from_node, to_node, weight), ...]}
    """
    print(f"📖 Loading routes from {filename}...")
    
    routes_by_type = defaultdict(list)
    all_routes = []
    
    with open(filename, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            route_data = (
                int(row["route_id"]),
                int(row["from_node"]),
                int(row["to_node"]),
                float(row["weight"]),
            )
            vehicle_type = row["vehicle_type"]
            routes_by_type[vehicle_type].append(route_data)
            all_routes.append(route_data)
    
    print(f"✓ Loaded {len(all_routes)} route segments")
    for vehicle_type, routes in routes_by_type.items():
        print(f"  {vehicle_type}: {len(routes)} segments")
    
    return dict(routes_by_type), all_routes


def create_graph_from_routes(routes_data: list, num_nodes: int = 1000):
    """
    Create NetworkIt graph from route data.
    
    Args:
        routes_data: List of (route_id, from_node, to_node, weight) tuples
        num_nodes: Number of nodes in graph
    
    Returns:
        NetworkIt graph object
    """
    graph = nk.Graph(n=num_nodes, weighted=True, directed=False)
    
    for _, from_node, to_node, weight in routes_data:
        if not graph.hasEdge(from_node, to_node):
            graph.addEdge(from_node, to_node, w=weight)
    
    return graph


def plot_weight_distribution(routes_by_type: dict, all_routes: list):
    """Plot histogram of edge weights by vehicle type."""
    print("\n📊 Creating weight distribution plot...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Route Weight Distribution", fontsize=16, fontweight="bold")
    
    # Plot for each vehicle type
    for idx, (vehicle_type, routes) in enumerate(routes_by_type.items()):
        ax = axes[idx // 2, idx % 2]
        weights = [r[3] for r in routes]
        
        ax.hist(weights, bins=30, color=VEHICLE_COLORS[vehicle_type], 
                alpha=0.7, edgecolor="black")
        ax.set_title(f"{vehicle_type} (n={len(routes)})", fontsize=12, fontweight="bold")
        ax.set_xlabel("Weight")
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        stats_text = f"Mean: {np.mean(weights):.2f}\nMedian: {np.median(weights):.2f}\nStd: {np.std(weights):.2f}"
        ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
                verticalalignment="top", horizontalalignment="right",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    
    # Plot all routes combined
    ax = axes[1, 1]
    all_weights = [r[3] for r in all_routes]
    ax.hist(all_weights, bins=30, color="gray", alpha=0.7, edgecolor="black")
    ax.set_title(f"All Routes Combined (n={len(all_routes)})", fontsize=12, fontweight="bold")
    ax.set_xlabel("Weight")
    ax.set_ylabel("Frequency")
    ax.grid(True, alpha=0.3)
    
    stats_text = f"Mean: {np.mean(all_weights):.2f}\nMedian: {np.median(all_weights):.2f}\nStd: {np.std(all_weights):.2f}"
    ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
            verticalalignment="top", horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig("route_weight_distribution.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: route_weight_distribution.png")
    plt.close()


def plot_route_statistics(routes_by_type: dict):
    """Plot statistics about routes."""
    print("\n📊 Creating route statistics plot...")
    
    # Calculate statistics
    stats = {}
    for vehicle_type, routes in routes_by_type.items():
        route_ids = set(r[0] for r in routes)
        route_lengths = defaultdict(int)
        for route_id, _, _, _ in routes:
            route_lengths[route_id] += 1
        
        stats[vehicle_type] = {
            "num_routes": len(route_ids),
            "total_segments": len(routes),
            "avg_length": np.mean(list(route_lengths.values())),
            "min_length": min(route_lengths.values()),
            "max_length": max(route_lengths.values()),
        }
    
    # Create plot
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Route Statistics by Vehicle Type", fontsize=16, fontweight="bold")
    
    vehicle_types = list(routes_by_type.keys())
    colors = [VEHICLE_COLORS[vt] for vt in vehicle_types]
    
    # Number of routes
    ax = axes[0]
    num_routes = [stats[vt]["num_routes"] for vt in vehicle_types]
    bars = ax.bar(vehicle_types, num_routes, color=colors, edgecolor="black", linewidth=1.5)
    ax.set_ylabel("Number of Routes")
    ax.set_title("Routes per Vehicle Type", fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f"{int(height)}", ha="center", va="bottom", fontweight="bold")
    
    # Total segments
    ax = axes[1]
    total_segments = [stats[vt]["total_segments"] for vt in vehicle_types]
    bars = ax.bar(vehicle_types, total_segments, color=colors, edgecolor="black", linewidth=1.5)
    ax.set_ylabel("Total Segments")
    ax.set_title("Total Segments per Vehicle Type", fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f"{int(height)}", ha="center", va="bottom", fontweight="bold")
    
    # Average route length
    ax = axes[2]
    avg_lengths = [stats[vt]["avg_length"] for vt in vehicle_types]
    bars = ax.bar(vehicle_types, avg_lengths, color=colors, edgecolor="black", linewidth=1.5)
    ax.set_ylabel("Average Route Length (segments)")
    ax.set_title("Average Route Length", fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f"{height:.1f}", ha="center", va="bottom", fontweight="bold")
    
    plt.tight_layout()
    plt.savefig("route_statistics.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: route_statistics.png")
    plt.close()


def plot_graph_visualization(routes_by_type: dict, all_routes: list):
    """Plot graph visualizations using Cartesian coordinates."""
    print("\n🎨 Creating graph visualizations...")
    
    # Combined graph with different colors for each vehicle type
    print("  Creating combined graph with vehicle type colors...")
    
    fig, ax = plt.subplots(figsize=(14, 14))
    fig.suptitle("Combined Route Network - Colored by Vehicle Type", 
                 fontsize=16, fontweight="bold")
    
    # Use Cartesian coordinates: node ID determines position
    # Place nodes in a grid pattern
    grid_size = int(np.ceil(np.sqrt(1000)))
    
    def get_cartesian_position(node_id):
        """Convert node ID to Cartesian coordinates."""
        x = node_id % grid_size
        y = node_id // grid_size
        return x, y
    
    # Draw edges for each vehicle type with different colors
    for vehicle_type, routes in routes_by_type.items():
        print(f"  Drawing {vehicle_type} routes...")
        color = VEHICLE_COLORS[vehicle_type]
        
        for _, from_node, to_node, weight in routes:
            x1, y1 = get_cartesian_position(from_node)
            x2, y2 = get_cartesian_position(to_node)
            ax.plot([x1, x2], [y1, y2], color=color, alpha=0.5, 
                   linewidth=0.8, zorder=1)
    
    # Draw nodes
    node_positions = [get_cartesian_position(i) for i in range(1000)]
    node_x = [pos[0] for pos in node_positions]
    node_y = [pos[1] for pos in node_positions]
    ax.scatter(node_x, node_y, c="white", s=15, edgecolors="black", 
               linewidth=0.3, alpha=0.9, zorder=2)
    
    ax.set_xlabel("X Coordinate", fontsize=12)
    ax.set_ylabel("Y Coordinate", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_aspect("equal")
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], color=VEHICLE_COLORS["TRAIN"], linewidth=3, 
                   label="Train Routes", alpha=0.7),
        plt.Line2D([0], [0], color=VEHICLE_COLORS["TRAM"], linewidth=3, 
                   label="Tram Routes", alpha=0.7),
        plt.Line2D([0], [0], color=VEHICLE_COLORS["BUS"], linewidth=3, 
                   label="Bus Routes", alpha=0.7),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=11, 
             framealpha=0.9, edgecolor="black")
    
    # Add statistics
    total_edges = sum(len(routes) for routes in routes_by_type.values())
    stats_text = f"Nodes: 1000\nTotal Edges: {total_edges}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            verticalalignment="top", fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="black"))
    
    plt.tight_layout()
    plt.savefig("combined_route_network.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: combined_route_network.png")
    plt.close()
    
    # Individual graphs per vehicle type in Cartesian layout
    for vehicle_type, routes in routes_by_type.items():
        print(f"  Creating Cartesian graph for {vehicle_type}...")
        
        fig, ax = plt.subplots(figsize=(12, 12))
        fig.suptitle(f"{vehicle_type} Route Network (Cartesian Layout)", 
                     fontsize=16, fontweight="bold")
        
        color = VEHICLE_COLORS[vehicle_type]
        
        # Draw edges
        for _, from_node, to_node, weight in routes:
            x1, y1 = get_cartesian_position(from_node)
            x2, y2 = get_cartesian_position(to_node)
            ax.plot([x1, x2], [y1, y2], color=color, alpha=0.6, 
                   linewidth=1.0, zorder=1)
        
        # Draw nodes
        node_x = [pos[0] for pos in node_positions]
        node_y = [pos[1] for pos in node_positions]
        ax.scatter(node_x, node_y, c=color, s=20, edgecolors="black", 
                  linewidth=0.4, alpha=0.8, zorder=2)
        
        ax.set_xlabel("X Coordinate", fontsize=12)
        ax.set_ylabel("Y Coordinate", fontsize=12)
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_aspect("equal")
        
        stats_text = f"Nodes: 1000\nEdges: {len(routes)}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment="top", fontsize=10,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="black"))
        
        plt.tight_layout()
        filename = f"{vehicle_type.lower()}_route_network.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {filename}")
        plt.close()


def calculate_node_degrees(routes_by_type: dict, all_routes: list):
    """
    Calculate node degrees (number of connections per node).
    
    Returns:
        dict: Node degrees by vehicle type and combined
    """
    # Calculate for each vehicle type
    degrees_by_type = {}
    for vehicle_type, routes in routes_by_type.items():
        degree_count = defaultdict(int)
        for _, from_node, to_node, _ in routes:
            degree_count[from_node] += 1
            degree_count[to_node] += 1
        degrees_by_type[vehicle_type] = dict(degree_count)
    
    # Calculate combined degrees
    combined_degrees = defaultdict(int)
    for _, from_node, to_node, _ in all_routes:
        combined_degrees[from_node] += 1
        combined_degrees[to_node] += 1
    
    return degrees_by_type, dict(combined_degrees)


def plot_node_degree_analysis(routes_by_type: dict, all_routes: list):
    """Create visualizations for node degree analysis."""
    print("\n📊 Creating node degree analysis...")
    
    degrees_by_type, combined_degrees = calculate_node_degrees(routes_by_type, all_routes)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Combined degree distribution histogram
    ax1 = plt.subplot(2, 3, 1)
    degree_values = list(combined_degrees.values())
    ax1.hist(degree_values, bins=50, color="steelblue", alpha=0.7, edgecolor="black")
    ax1.set_xlabel("Node Degree", fontsize=11)
    ax1.set_ylabel("Frequency", fontsize=11)
    ax1.set_title("Combined Degree Distribution", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    
    stats_text = (f"Mean: {np.mean(degree_values):.2f}\n"
                  f"Median: {np.median(degree_values):.0f}\n"
                  f"Max: {max(degree_values)}\n"
                  f"Min: {min(degree_values)}")
    ax1.text(0.95, 0.95, stats_text, transform=ax1.transAxes,
             verticalalignment="top", horizontalalignment="right",
             bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    
    # 2. Degree distribution by vehicle type
    ax2 = plt.subplot(2, 3, 2)
    for vehicle_type, degrees in degrees_by_type.items():
        values = list(degrees.values())
        ax2.hist(values, bins=30, alpha=0.5, label=vehicle_type,
                color=VEHICLE_COLORS[vehicle_type], edgecolor="black", linewidth=0.5)
    ax2.set_xlabel("Node Degree", fontsize=11)
    ax2.set_ylabel("Frequency", fontsize=11)
    ax2.set_title("Degree Distribution by Vehicle Type", fontsize=12, fontweight="bold")
    ax2.legend(loc="upper right", fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 3. Top 20 nodes with highest degree
    ax3 = plt.subplot(2, 3, 3)
    sorted_nodes = sorted(combined_degrees.items(), key=lambda x: x[1], reverse=True)[:20]
    nodes, degrees = zip(*sorted_nodes)
    bars = ax3.barh(range(len(nodes)), degrees, color="coral", edgecolor="black")
    ax3.set_yticks(range(len(nodes)))
    ax3.set_yticklabels([f"Node {n}" for n in nodes], fontsize=9)
    ax3.set_xlabel("Degree", fontsize=11)
    ax3.set_title("Top 20 Nodes by Degree", fontsize=12, fontweight="bold")
    ax3.grid(True, alpha=0.3, axis="x")
    ax3.invert_yaxis()
    
    # 4. Average degree by vehicle type
    ax4 = plt.subplot(2, 3, 4)
    vehicle_types = list(degrees_by_type.keys())
    avg_degrees = [np.mean(list(degrees_by_type[vt].values())) for vt in vehicle_types]
    colors = [VEHICLE_COLORS[vt] for vt in vehicle_types]
    bars = ax4.bar(vehicle_types, avg_degrees, color=colors, edgecolor="black", linewidth=1.5)
    ax4.set_ylabel("Average Degree", fontsize=11)
    ax4.set_title("Average Node Degree by Vehicle Type", fontsize=12, fontweight="bold")
    ax4.grid(True, alpha=0.3, axis="y")
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f"{height:.1f}", ha="center", va="bottom", fontweight="bold")
    
    # 5. Degree distribution comparison (box plot)
    ax5 = plt.subplot(2, 3, 5)
    data_for_boxplot = [list(degrees_by_type[vt].values()) for vt in vehicle_types]
    bp = ax5.boxplot(data_for_boxplot, labels=vehicle_types, patch_artist=True,
                     medianprops=dict(color="red", linewidth=2))
    for patch, vt in zip(bp['boxes'], vehicle_types):
        patch.set_facecolor(VEHICLE_COLORS[vt])
        patch.set_alpha(0.7)
    ax5.set_ylabel("Node Degree", fontsize=11)
    ax5.set_title("Degree Distribution Comparison", fontsize=12, fontweight="bold")
    ax5.grid(True, alpha=0.3, axis="y")
    
    # 6. Nodes with zero degree (isolated nodes)
    ax6 = plt.subplot(2, 3, 6)
    all_nodes = set(range(1000))
    connected_nodes = set(combined_degrees.keys())
    isolated_nodes = all_nodes - connected_nodes
    
    categories = ["Connected Nodes", "Isolated Nodes"]
    counts = [len(connected_nodes), len(isolated_nodes)]
    colors_pie = ["lightgreen", "lightcoral"]
    
    wedges, texts, autotexts = ax6.pie(counts, labels=categories, colors=colors_pie,
                                        autopct="%1.1f%%", startangle=90,
                                        textprops=dict(fontsize=11, fontweight="bold"))
    ax6.set_title("Node Connectivity", fontsize=12, fontweight="bold")
    
    # Add count text
    for i, (text, count) in enumerate(zip(texts, counts)):
        text.set_text(f"{text.get_text()}\n({count})")
    
    plt.suptitle("Node Degree Analysis", fontsize=16, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig("node_degree_analysis.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: node_degree_analysis.png")
    plt.close()


def print_degree_statistics(routes_by_type: dict, all_routes: list):
    """Print detailed node degree statistics."""
    print("\n" + "=" * 60)
    print("NODE DEGREE STATISTICS")
    print("=" * 60)
    
    degrees_by_type, combined_degrees = calculate_node_degrees(routes_by_type, all_routes)
    
    # Combined statistics
    degree_values = list(combined_degrees.values())
    print("\nCombined Network:")
    print(f"  Total nodes with connections: {len(combined_degrees)}")
    print(f"  Isolated nodes:               {1000 - len(combined_degrees)}")
    print(f"  Average degree:               {np.mean(degree_values):.2f}")
    print(f"  Median degree:                {np.median(degree_values):.0f}")
    print(f"  Min degree:                   {min(degree_values)}")
    print(f"  Max degree:                   {max(degree_values)}")
    print(f"  Std deviation:                {np.std(degree_values):.2f}")
    
    # Top nodes
    sorted_nodes = sorted(combined_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\n  Top 10 nodes by degree:")
    for node, degree in sorted_nodes:
        print(f"    Node {node:4d}: {degree:3d} connections")
    
    # Statistics by vehicle type
    print("\nBy Vehicle Type:")
    for vehicle_type, degrees in degrees_by_type.items():
        values = list(degrees.values())
        print(f"\n  {vehicle_type}:")
        print(f"    Nodes with connections: {len(degrees)}")
        print(f"    Average degree:         {np.mean(values):.2f}")
        print(f"    Median degree:          {np.median(values):.0f}")
        print(f"    Min degree:             {min(values)}")
        print(f"    Max degree:             {max(values)}")
        print(f"    Std deviation:          {np.std(values):.2f}")
    
    print("=" * 60)


def main():
    """Main execution function."""
    print("=" * 60)
    print("ROUTE VISUALIZATION SCRIPT")
    print("=" * 60)
    
    # Load data
    routes_by_type, all_routes = load_routes_from_csv()
    
    # Create visualizations
    plot_weight_distribution(routes_by_type, all_routes)
    plot_route_statistics(routes_by_type)
    plot_graph_visualization(routes_by_type, all_routes)
    plot_node_degree_analysis(routes_by_type, all_routes)
    
    # Print statistics
    print_degree_statistics(routes_by_type, all_routes)
    
    print("\n" + "=" * 60)
    print("✅ All visualizations created successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - route_weight_distribution.png")
    print("  - route_statistics.png")
    print("  - combined_route_network.png")
    print("  - train_route_network.png")
    print("  - tram_route_network.png")
    print("  - bus_route_network.png")
    print("  - node_degree_analysis.png")


if __name__ == "__main__":
    main()
