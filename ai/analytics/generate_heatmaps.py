"""
Heatmap generation system for traffic analysis.

Generates heatmaps from JourneyData GPS points to identify:
- High traffic areas
- Areas needing new stops
- Routes requiring more frequent service

Output formats:
- Static PNG heatmaps (matplotlib)
- Interactive HTML maps (folium)
- Statistical reports (CSV)

Aggregations:
- Weekly total (sum of entire week)
- Daily total (sum of single day)
- Per day of week (Monday, Tuesday, etc.)
- Per hour (00:00, 01:00, etc.)
- Per day and hour (Monday 08:00, etc.)

Metrics:
- SUM: Total number of GPS points in area
- AVERAGE: Average points per trip in area
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# These imports need to be after sys.path modification
if True:  # noqa: SIM102
    from database import SessionLocal
    from db_models import JourneyData


def load_journey_data(db, start_date=None, end_date=None, vehicle_type=None):
    """
    Load GPS data from JourneyData table.

    Args:
        db: Database session
        start_date: Start date filter (default: 7 days ago)
        end_date: End date filter (default: now)
        vehicle_type: Filter by vehicle type (optional)

    Returns:
        pandas DataFrame with columns: timestamp, lat, lon, vehicle_trip_id, user_id
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=7)
    if end_date is None:
        end_date = datetime.now()

    query = db.query(JourneyData).filter(
        JourneyData.timestamp >= start_date,
        JourneyData.timestamp <= end_date,
        JourneyData.latitude.isnot(None),
        JourneyData.longitude.isnot(None),
    )

    data = []
    for record in query.all():
        data.append(
            {
                "timestamp": record.timestamp,
                "latitude": float(record.latitude),  # type: ignore
                "longitude": float(record.longitude),  # type: ignore
                "vehicle_trip_id": (
                    str(record.vehicle_trip_id) if record.vehicle_trip_id else None
                ),
                "user_id": str(record.user_id),
            }
        )

    df = pd.DataFrame(data)

    if len(df) > 0:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["day_of_week"] = df["timestamp"].dt.day_name()
        df["hour"] = df["timestamp"].dt.hour
        df["date"] = df["timestamp"].dt.date

    return df


def create_grid(df, grid_size=0.001):
    """
    Create a grid overlay for the map.

    Args:
        df: DataFrame with latitude/longitude
        grid_size: Size of grid cells in degrees (default: ~111m)

    Returns:
        Grid bounds and cell assignments
    """
    lat_min, lat_max = df["latitude"].min(), df["latitude"].max()
    lon_min, lon_max = df["longitude"].min(), df["longitude"].max()

    # Add padding
    padding = grid_size * 5
    lat_min -= padding
    lat_max += padding
    lon_min -= padding
    lon_max += padding

    # Create grid
    lat_bins = np.arange(lat_min, lat_max + grid_size, grid_size)
    lon_bins = np.arange(lon_min, lon_max + grid_size, grid_size)

    # Assign each point to a grid cell
    df["lat_bin"] = pd.cut(df["latitude"], bins=lat_bins, labels=False)  # type: ignore
    df["lon_bin"] = pd.cut(df["longitude"], bins=lon_bins, labels=False)  # type: ignore

    return {
        "lat_bins": lat_bins,
        "lon_bins": lon_bins,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "lon_min": lon_min,
        "lon_max": lon_max,
    }


def generate_heatmap_sum(df, grid_info, title="Traffic Heatmap - Total"):
    """
    Generate heatmap showing SUM of GPS points in each grid cell.

    Higher values = more traffic = potential need for stops/more service
    """
    # Count points in each grid cell
    heatmap_data = df.groupby(["lat_bin", "lon_bin"]).size().reset_index(name="count")

    # Create 2D array
    max_lat_bin = int(df["lat_bin"].max()) + 1
    max_lon_bin = int(df["lon_bin"].max()) + 1

    grid = np.zeros((max_lat_bin, max_lon_bin))

    for _, row in heatmap_data.iterrows():
        if pd.notna(row["lat_bin"]) and pd.notna(row["lon_bin"]):
            grid[int(row["lat_bin"]), int(row["lon_bin"])] = row["count"]

    # Apply Gaussian smoothing for better visualization
    smoothed = gaussian_filter(grid, sigma=2)

    return grid, smoothed, heatmap_data


def generate_heatmap_average(df, grid_info, title="Traffic Heatmap - Average"):
    """
    Generate heatmap showing AVERAGE GPS points per trip in each grid cell.

    Shows areas where vehicles spend more time (frequent stops, slow traffic)
    """
    # Calculate average points per trip in each cell
    heatmap_data = (
        df.groupby(["lat_bin", "lon_bin", "vehicle_trip_id"])
        .size()
        .reset_index(name="trip_count")
    )

    avg_data = (
        heatmap_data.groupby(["lat_bin", "lon_bin"])["trip_count"]
        .mean()
        .reset_index(name="avg_count")
    )

    # Create 2D array
    max_lat_bin = int(df["lat_bin"].max()) + 1
    max_lon_bin = int(df["lon_bin"].max()) + 1

    grid = np.zeros((max_lat_bin, max_lon_bin))

    for _, row in avg_data.iterrows():
        if pd.notna(row["lat_bin"]) and pd.notna(row["lon_bin"]):
            grid[int(row["lat_bin"]), int(row["lon_bin"])] = row["avg_count"]

    # Apply Gaussian smoothing
    smoothed = gaussian_filter(grid, sigma=2)

    return grid, smoothed, avg_data


def plot_heatmap(
    grid,
    smoothed,
    grid_info,
    title,
    output_path,
    metric_type="sum",
):
    """
    Plot and save heatmap visualization.
    """
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))

    # Plot raw grid
    im1 = axes[0].imshow(
        grid.T,
        origin="lower",
        extent=[
            grid_info["lat_min"],
            grid_info["lat_max"],
            grid_info["lon_min"],
            grid_info["lon_max"],
        ],
        cmap="YlOrRd",
        aspect="auto",
    )
    axes[0].set_title(f"{title} - Raw Data")
    axes[0].set_xlabel("Latitude")
    axes[0].set_ylabel("Longitude")
    plt.colorbar(im1, ax=axes[0], label=f"{metric_type.capitalize()} count")

    # Plot smoothed
    im2 = axes[1].imshow(
        smoothed.T,
        origin="lower",
        extent=[
            grid_info["lat_min"],
            grid_info["lat_max"],
            grid_info["lon_min"],
            grid_info["lon_max"],
        ],
        cmap="YlOrRd",
        aspect="auto",
    )
    axes[1].set_title(f"{title} - Smoothed")
    axes[1].set_xlabel("Latitude")
    axes[1].set_ylabel("Longitude")
    plt.colorbar(im2, ax=axes[1], label=f"{metric_type.capitalize()} count")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✓ Saved: {output_path}")


def generate_interactive_heatmap(df, output_path, title="Interactive Traffic Map"):
    """
    Generate interactive HTML heatmap using folium.

    Allows zooming and clicking on points.
    """
    try:
        import folium  # type: ignore
        from folium.plugins import HeatMap  # type: ignore
    except ImportError:
        print("⚠️  folium not installed. Skipping interactive map.")
        print("   Install with: pip install folium")
        return

    # Calculate center
    center_lat = df["latitude"].mean()
    center_lon = df["longitude"].mean()

    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="OpenStreetMap",
    )

    # Prepare heatmap data
    heat_data = df[["latitude", "longitude"]].values.tolist()

    # Add heatmap layer
    HeatMap(
        heat_data,
        min_opacity=0.3,
        max_zoom=18,
        radius=15,
        blur=20,
        gradient={
            0.0: "blue",
            0.3: "cyan",
            0.5: "lime",
            0.7: "yellow",
            1.0: "red",
        },
    ).add_to(m)

    # Add title
    title_html = f"""
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 400px; height: 50px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:16px; padding: 10px">
            <b>{title}</b><br>
            Total points: {len(df):,}
        </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Save
    m.save(output_path)
    print(f"✓ Saved interactive map: {output_path}")


def generate_hotspot_report(df, grid_info, top_n=20):
    """
    Generate report of hottest spots (areas with most traffic).

    Returns DataFrame with top N areas sorted by traffic.
    """
    # Count points per grid cell
    hotspots = (
        df.groupby(["lat_bin", "lon_bin"])
        .agg(
            {
                "timestamp": "count",
                "latitude": "mean",
                "longitude": "mean",
                "vehicle_trip_id": "nunique",
            }
        )
        .reset_index()
    )

    hotspots.columns = [
        "lat_bin",
        "lon_bin",
        "total_points",
        "center_lat",
        "center_lon",
        "unique_trips",
    ]

    # Sort by traffic
    hotspots = hotspots.sort_values("total_points", ascending=False).head(top_n)

    # Add rank
    hotspots["rank"] = range(1, len(hotspots) + 1)

    return hotspots[
        [
            "rank",
            "center_lat",
            "center_lon",
            "total_points",
            "unique_trips",
            "lat_bin",
            "lon_bin",
        ]
    ]


def generate_all_heatmaps(output_dir="analytics/heatmaps"):
    """
    Generate all heatmap types:
    - Weekly total (sum + average)
    - Daily total (sum + average)
    - Per day of week (7 x 2 = 14 maps)
    - Per hour (24 x 2 = 48 maps)
    - Per day and hour (7 x 24 x 2 = 336 maps - optional, very detailed)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("HEATMAP GENERATION - Traffic Analysis")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Load data
        print("\n📊 Loading GPS data...")
        df = load_journey_data(db, start_date=datetime.now() - timedelta(days=7))

        if len(df) == 0:
            print("❌ No GPS data found in the last 7 days")
            return

        print(
            f"✓ Loaded {len(df):,} GPS points from {df['timestamp'].min()} to {df['timestamp'].max()}"
        )
        print(f"  - Unique trips: {df['vehicle_trip_id'].nunique()}")
        print(f"  - Unique users: {df['user_id'].nunique()}")

        # Create grid
        print("\n🗺️  Creating spatial grid...")
        grid_info = create_grid(df, grid_size=0.001)  # ~111m cells
        print(
            f"✓ Grid created: {len(grid_info['lat_bins'])} x {len(grid_info['lon_bins'])} cells"
        )

        # 1. WEEKLY HEATMAPS
        print("\n📅 Generating weekly heatmaps...")

        # Sum
        grid_sum, smoothed_sum, data_sum = generate_heatmap_sum(df, grid_info)
        plot_heatmap(
            grid_sum,
            smoothed_sum,
            grid_info,
            "Weekly Traffic - Total Count",
            output_path / "weekly_sum.png",
            metric_type="sum",
        )

        # Average
        grid_avg, smoothed_avg, data_avg = generate_heatmap_average(df, grid_info)
        plot_heatmap(
            grid_avg,
            smoothed_avg,
            grid_info,
            "Weekly Traffic - Average per Trip",
            output_path / "weekly_average.png",
            metric_type="average",
        )

        # Interactive
        generate_interactive_heatmap(
            df,
            output_path / "weekly_interactive.html",
            title="Weekly Traffic - Interactive Map",
        )

        # 2. PER DAY OF WEEK
        print("\n📆 Generating per-day heatmaps...")
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for day in days:
            df_day = df[df["day_of_week"] == day]

            if len(df_day) == 0:
                continue

            # Sum
            grid_sum, smoothed_sum, _ = generate_heatmap_sum(df_day, grid_info)
            plot_heatmap(
                grid_sum,
                smoothed_sum,
                grid_info,
                f"{day} - Total Count",
                output_path / f"day_{day.lower()}_sum.png",
                metric_type="sum",
            )

            # Average
            grid_avg, smoothed_avg, _ = generate_heatmap_average(df_day, grid_info)
            plot_heatmap(
                grid_avg,
                smoothed_avg,
                grid_info,
                f"{day} - Average per Trip",
                output_path / f"day_{day.lower()}_average.png",
                metric_type="average",
            )

        # 3. PER HOUR
        print("\n⏰ Generating per-hour heatmaps...")

        for hour in range(24):
            df_hour = df[df["hour"] == hour]

            if len(df_hour) == 0:
                continue

            # Sum
            grid_sum, smoothed_sum, _ = generate_heatmap_sum(df_hour, grid_info)
            plot_heatmap(
                grid_sum,
                smoothed_sum,
                grid_info,
                f"Hour {hour:02d}:00 - Total Count",
                output_path / f"hour_{hour:02d}_sum.png",
                metric_type="sum",
            )

            # Average
            grid_avg, smoothed_avg, _ = generate_heatmap_average(df_hour, grid_info)
            plot_heatmap(
                grid_avg,
                smoothed_avg,
                grid_info,
                f"Hour {hour:02d}:00 - Average per Trip",
                output_path / f"hour_{hour:02d}_average.png",
                metric_type="average",
            )

        # 4. PER DAY AND HOUR (detailed analysis - optional, generates many files)
        print("\n🔍 Generating per-day-hour heatmaps (detailed)...")
        print("   (This will create many files, can be skipped for quick analysis)")

        generate_detailed = (
            input("   Generate detailed day-hour maps? (y/n): ").lower() == "y"
        )

        if generate_detailed:
            detailed_path = output_path / "detailed"
            detailed_path.mkdir(exist_ok=True)

            for day in days:
                for hour in range(24):
                    df_detail = df[(df["day_of_week"] == day) & (df["hour"] == hour)]

                    if len(df_detail) < 10:  # Skip if too few points
                        continue

                    # Sum only (to reduce file count)
                    grid_sum, smoothed_sum, _ = generate_heatmap_sum(
                        df_detail, grid_info
                    )
                    plot_heatmap(
                        grid_sum,
                        smoothed_sum,
                        grid_info,
                        f"{day} {hour:02d}:00 - Total",
                        detailed_path / f"{day.lower()}_{hour:02d}_sum.png",
                        metric_type="sum",
                    )

        # 5. HOTSPOT REPORT
        print("\n🔥 Generating hotspot report...")
        hotspots = generate_hotspot_report(df, grid_info, top_n=20)

        report_path = output_path / "hotspots_report.csv"
        hotspots.to_csv(report_path, index=False)
        print(f"✓ Saved hotspot report: {report_path}")

        print("\n" + "=" * 60)
        print("TOP 10 HOTSPOTS (Areas Needing Attention)")
        print("=" * 60)
        print(hotspots.head(10).to_string(index=False))

        # 6. SUMMARY STATISTICS
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        print(f"Total GPS points: {len(df):,}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Unique trips: {df['vehicle_trip_id'].nunique()}")
        print(f"Unique users: {df['user_id'].nunique()}")
        print(f"\nBusiest day: {df['day_of_week'].value_counts().idxmax()}")
        print(f"Busiest hour: {df['hour'].value_counts().idxmax()}:00")
        print(f"\nHeatmaps saved to: {output_path.absolute()}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


def main():
    """Entry point for heatmap generation."""
    print("\n🗺️  Public Transport Traffic Heatmap Generator\n")

    try:
        generate_all_heatmaps()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation stopped by user")
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
