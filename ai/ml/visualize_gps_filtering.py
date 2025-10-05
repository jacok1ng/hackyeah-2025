"""
Visualize the effect of GPS filtering.

Compares raw GPS data vs filtered data to show the improvement.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")


def load_data():
    """Load both raw and filtered datasets."""
    try:
        df_raw = pd.read_csv("ml/transport_validation_data.csv")
        print(f"Loaded raw data: {len(df_raw)} samples")
    except FileNotFoundError:
        print("ERROR: ml/transport_validation_data.csv not found!")
        print("Run: python ml/prepare_transport_validation_data.py first")
        return None, None

    try:
        df_filtered = pd.read_csv("ml/transport_validation_data_filtered.csv")
        print(f"Loaded filtered data: {len(df_filtered)} samples")
    except FileNotFoundError:
        print("ERROR: ml/transport_validation_data_filtered.csv not found!")
        print("Run: python ml/prepare_transport_validation_data_filtered.py first")
        return None, None

    return df_raw, df_filtered


def plot_gps_accuracy_comparison(df_raw, df_filtered):
    """Plot GPS accuracy distribution before and after filtering."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Raw data
    if "accuracy_avg" in df_raw.columns:
        accuracy_raw = df_raw["accuracy_avg"].dropna()
        axes[0].hist(accuracy_raw, bins=50, alpha=0.7, color="red", edgecolor="black")
        axes[0].axvline(
            accuracy_raw.median(),
            color="darkred",
            linestyle="--",
            linewidth=2,
            label=f"Median: {accuracy_raw.median():.1f}m",
        )
        axes[0].set_title("Raw Data - GPS Accuracy", fontsize=14, fontweight="bold")
        axes[0].set_xlabel("Accuracy (meters)")
        axes[0].set_ylabel("Count")
        axes[0].legend()
        axes[0].set_xlim(0, 100)

    # Filtered data
    if "accuracy_avg" in df_filtered.columns:
        accuracy_filtered = df_filtered["accuracy_avg"].dropna()
        axes[1].hist(
            accuracy_filtered, bins=50, alpha=0.7, color="green", edgecolor="black"
        )
        axes[1].axvline(
            accuracy_filtered.median(),
            color="darkgreen",
            linestyle="--",
            linewidth=2,
            label=f"Median: {accuracy_filtered.median():.1f}m",
        )
        axes[1].set_title(
            "Filtered Data - GPS Accuracy", fontsize=14, fontweight="bold"
        )
        axes[1].set_xlabel("Accuracy (meters)")
        axes[1].set_ylabel("Count")
        axes[1].legend()
        axes[1].set_xlim(0, 100)

    plt.tight_layout()
    plt.savefig("ml/gps_accuracy_comparison.png", dpi=300, bbox_inches="tight")
    print("Saved: ml/gps_accuracy_comparison.png")
    plt.close()


def plot_satellite_count_comparison(df_raw, df_filtered):
    """Plot satellite count distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Raw data
    if "satellite_count_avg" in df_raw.columns:
        sat_raw = df_raw["satellite_count_avg"].dropna()
        axes[0].hist(
            sat_raw, bins=range(0, 21), alpha=0.7, color="red", edgecolor="black"
        )
        axes[0].axvline(
            sat_raw.median(),
            color="darkred",
            linestyle="--",
            linewidth=2,
            label=f"Median: {sat_raw.median():.1f}",
        )
        axes[0].set_title("Raw Data - Satellite Count", fontsize=14, fontweight="bold")
        axes[0].set_xlabel("Number of Satellites")
        axes[0].set_ylabel("Count")
        axes[0].legend()

    # Filtered data
    if "satellite_count_avg" in df_filtered.columns:
        sat_filtered = df_filtered["satellite_count_avg"].dropna()
        axes[1].hist(
            sat_filtered, bins=range(0, 21), alpha=0.7, color="green", edgecolor="black"
        )
        axes[1].axvline(
            sat_filtered.median(),
            color="darkgreen",
            linestyle="--",
            linewidth=2,
            label=f"Median: {sat_filtered.median():.1f}",
        )
        axes[1].set_title(
            "Filtered Data - Satellite Count", fontsize=14, fontweight="bold"
        )
        axes[1].set_xlabel("Number of Satellites")
        axes[1].set_ylabel("Count")
        axes[1].legend()

    plt.tight_layout()
    plt.savefig("ml/satellite_count_comparison.png", dpi=300, bbox_inches="tight")
    print("Saved: ml/satellite_count_comparison.png")
    plt.close()


def plot_speed_distribution(df_raw, df_filtered):
    """Plot speed distribution to show GPS jump removal."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Raw data
    if "speed_avg" in df_raw.columns:
        speed_raw = df_raw["speed_avg"].dropna()
        # Limit to reasonable range for visualization
        speed_raw_clipped = speed_raw[speed_raw < 100]
        axes[0].hist(
            speed_raw_clipped, bins=50, alpha=0.7, color="red", edgecolor="black"
        )
        axes[0].axvline(
            speed_raw_clipped.median(),
            color="darkred",
            linestyle="--",
            linewidth=2,
            label=f"Median: {speed_raw_clipped.median():.1f} m/s",
        )
        axes[0].set_title("Raw Data - Speed", fontsize=14, fontweight="bold")
        axes[0].set_xlabel("Speed (m/s)")
        axes[0].set_ylabel("Count")
        axes[0].legend()
        axes[0].text(
            0.98,
            0.98,
            f"Outliers > 100 m/s: {len(speed_raw[speed_raw >= 100])}",
            transform=axes[0].transAxes,
            ha="right",
            va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    # Filtered data
    if "speed_avg" in df_filtered.columns:
        speed_filtered = df_filtered["speed_avg"].dropna()
        speed_filtered_clipped = speed_filtered[speed_filtered < 100]
        axes[1].hist(
            speed_filtered_clipped, bins=50, alpha=0.7, color="green", edgecolor="black"
        )
        axes[1].axvline(
            speed_filtered_clipped.median(),
            color="darkgreen",
            linestyle="--",
            linewidth=2,
            label=f"Median: {speed_filtered_clipped.median():.1f} m/s",
        )
        axes[1].set_title("Filtered Data - Speed", fontsize=14, fontweight="bold")
        axes[1].set_xlabel("Speed (m/s)")
        axes[1].set_ylabel("Count")
        axes[1].legend()
        axes[1].text(
            0.98,
            0.98,
            f"Outliers > 100 m/s: {len(speed_filtered[speed_filtered >= 100])}",
            transform=axes[1].transAxes,
            ha="right",
            va="top",
            bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.5),
        )

    plt.tight_layout()
    plt.savefig("ml/speed_distribution_comparison.png", dpi=300, bbox_inches="tight")
    print("Saved: ml/speed_distribution_comparison.png")
    plt.close()


def plot_data_statistics(df_raw, df_filtered):
    """Plot overall statistics comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))

    stats = {
        "Total Samples": [len(df_raw), len(df_filtered)],
        "Removed (%)": [0, (len(df_raw) - len(df_filtered)) / len(df_raw) * 100],
    }

    x = np.arange(len(stats))
    width = 0.35

    raw_values = [stats[key][0] for key in stats]
    filtered_values = [stats[key][1] for key in stats]

    bars1 = ax.bar(
        x - width / 2, raw_values, width, label="Raw", color="red", alpha=0.7
    )
    bars2 = ax.bar(
        x + width / 2,
        filtered_values,
        width,
        label="Filtered",
        color="green",
        alpha=0.7,
    )

    ax.set_ylabel("Value")
    ax.set_title("Data Statistics: Raw vs Filtered", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(stats.keys())
    ax.legend()

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                )

    plt.tight_layout()
    plt.savefig("ml/data_statistics_comparison.png", dpi=300, bbox_inches="tight")
    print("Saved: ml/data_statistics_comparison.png")
    plt.close()


def print_comparison_summary(df_raw, df_filtered):
    """Print detailed comparison summary."""
    print("\n" + "=" * 60)
    print("FILTERING COMPARISON SUMMARY")
    print("=" * 60)

    print(f"\nDataset sizes:")
    print(f"  Raw data:      {len(df_raw):,} samples")
    print(f"  Filtered data: {len(df_filtered):,} samples")
    print(
        f"  Removed:       {len(df_raw) - len(df_filtered):,} samples ({(len(df_raw) - len(df_filtered))/len(df_raw)*100:.1f}%)"
    )

    if "accuracy_avg" in df_raw.columns and "accuracy_avg" in df_filtered.columns:
        print(f"\nGPS Accuracy (meters):")
        print(f"  Raw median:      {df_raw['accuracy_avg'].median():.2f}m")
        print(f"  Filtered median: {df_filtered['accuracy_avg'].median():.2f}m")
        print(
            f"  Improvement:     {((df_raw['accuracy_avg'].median() - df_filtered['accuracy_avg'].median()) / df_raw['accuracy_avg'].median() * 100):.1f}%"
        )

    if (
        "satellite_count_avg" in df_raw.columns
        and "satellite_count_avg" in df_filtered.columns
    ):
        print(f"\nSatellite Count:")
        print(f"  Raw median:      {df_raw['satellite_count_avg'].median():.1f}")
        print(f"  Filtered median: {df_filtered['satellite_count_avg'].median():.1f}")

    if "speed_avg" in df_raw.columns and "speed_avg" in df_filtered.columns:
        print(f"\nSpeed (m/s):")
        print(f"  Raw median:      {df_raw['speed_avg'].median():.2f} m/s")
        print(f"  Filtered median: {df_filtered['speed_avg'].median():.2f} m/s")
        print(
            f"  Raw outliers (>55 m/s / 200 km/h): {len(df_raw[df_raw['speed_avg'] > 55])}"
        )
        print(
            f"  Filtered outliers (>55 m/s / 200 km/h): {len(df_filtered[df_filtered['speed_avg'] > 55])}"
        )

    print("\n" + "=" * 60)


def main():
    """Main visualization function."""
    print("=" * 60)
    print("GPS Filtering Visualization")
    print("=" * 60)
    print()

    # Load data
    df_raw, df_filtered = load_data()

    if df_raw is None or df_filtered is None:
        return

    # Generate plots
    print("\nGenerating visualizations...")
    plot_gps_accuracy_comparison(df_raw, df_filtered)
    plot_satellite_count_comparison(df_raw, df_filtered)
    plot_speed_distribution(df_raw, df_filtered)
    plot_data_statistics(df_raw, df_filtered)

    # Print summary
    print_comparison_summary(df_raw, df_filtered)

    print("\n" + "=" * 60)
    print("Visualization complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - ml/gps_accuracy_comparison.png")
    print("  - ml/satellite_count_comparison.png")
    print("  - ml/speed_distribution_comparison.png")
    print("  - ml/data_statistics_comparison.png")
    print()


if __name__ == "__main__":
    main()
