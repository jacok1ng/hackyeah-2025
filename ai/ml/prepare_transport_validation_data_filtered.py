"""
Prepare training data with GPS outlier filtering using KNN and DBSCAN.

This extended version filters out unreliable GPS data caused by:
- Weak GPS signal (low accuracy, few satellites)
- GPS jumps (sudden large distance changes)
- Outliers detected by DBSCAN clustering
- Points inconsistent with KNN neighbors

Output: Cleaner CSV file for training with filtered GPS data.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import SessionLocal
from db_models import JourneyData, User, UserJourney, Vehicle, VehicleTrip
from sqlalchemy import and_


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in meters."""
    R = 6371000  # Earth radius in meters

    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


def filter_by_gps_quality(df, min_accuracy=50, min_satellites=4):
    """
    Filter out GPS points with poor signal quality.

    Args:
        df: DataFrame with GPS data
        min_accuracy: Maximum acceptable GPS accuracy in meters (lower is better)
        min_satellites: Minimum number of satellites required

    Returns:
        DataFrame with filtered rows
    """
    print(f"\n[GPS QUALITY FILTER]")
    print(f"  Min satellites: {min_satellites}")
    print(f"  Max accuracy: {min_accuracy}m")

    initial_count = len(df)

    # Filter by accuracy (lower is better in GPS terms)
    mask_accuracy = (df["accuracy"].isna()) | (df["accuracy"] <= min_accuracy)

    # Filter by satellite count
    mask_satellites = (df["satellite_count"].isna()) | (
        df["satellite_count"] >= min_satellites
    )

    # Combine filters
    mask = mask_accuracy & mask_satellites
    df_filtered = df[mask].copy()

    removed_count = initial_count - len(df_filtered)
    print(f"  Removed: {removed_count} points ({removed_count/initial_count*100:.1f}%)")
    print(f"  Remaining: {len(df_filtered)} points")

    return df_filtered


def detect_gps_jumps(df, max_speed_kmh=200, time_threshold_seconds=1):
    """
    Detect and remove GPS jumps (sudden large movements).

    A GPS jump is detected when the implied speed between consecutive points
    exceeds max_speed_kmh (accounting for time difference).

    Args:
        df: DataFrame sorted by user_id, vehicle_trip_id, timestamp
        max_speed_kmh: Maximum realistic speed in km/h
        time_threshold_seconds: Minimum time between points to calculate speed

    Returns:
        DataFrame with GPS jumps marked for removal
    """
    print(f"\n[GPS JUMP DETECTION]")
    print(f"  Max realistic speed: {max_speed_kmh} km/h")

    df = df.copy()
    df["is_gps_jump"] = False

    initial_count = len(df)

    for (user_id, trip_id), group in df.groupby(["user_id", "vehicle_trip_id"]):
        if len(group) < 2:
            continue

        indices = group.index
        lats = group["latitude"].values
        lons = group["longitude"].values
        times = pd.to_datetime(group["timestamp"]).values

        for i in range(1, len(group)):
            if pd.isna(lats[i]) or pd.isna(lons[i]):
                continue
            if pd.isna(lats[i - 1]) or pd.isna(lons[i - 1]):
                continue

            # Calculate distance and time difference
            distance_m = calculate_haversine_distance(
                lats[i - 1], lons[i - 1], lats[i], lons[i]
            )

            time_diff = (times[i] - times[i - 1]) / np.timedelta64(1, "s")

            if time_diff < time_threshold_seconds:
                continue

            # Calculate implied speed
            speed_ms = distance_m / time_diff
            speed_kmh = speed_ms * 3.6

            # Mark as jump if speed exceeds threshold
            if speed_kmh > max_speed_kmh:
                df.loc[indices[i], "is_gps_jump"] = True

    # Remove GPS jumps
    df_filtered = df[~df["is_gps_jump"]].drop("is_gps_jump", axis=1)

    removed_count = initial_count - len(df_filtered)
    print(f"  Detected GPS jumps: {removed_count}")
    print(f"  Removed: {removed_count} points ({removed_count/initial_count*100:.1f}%)")
    print(f"  Remaining: {len(df_filtered)} points")

    return df_filtered


def filter_gps_outliers_dbscan(df, eps_meters=100, min_samples=3):
    """
    Use DBSCAN to detect and remove GPS outliers.

    DBSCAN groups nearby GPS points into clusters. Points that don't
    belong to any cluster (noise) are considered outliers.

    Args:
        df: DataFrame with GPS data
        eps_meters: Maximum distance between points in a cluster (meters)
        min_samples: Minimum points to form a dense region

    Returns:
        DataFrame with outliers removed
    """
    print(f"\n[DBSCAN OUTLIER DETECTION]")
    print(f"  Epsilon: {eps_meters}m")
    print(f"  Min samples: {min_samples}")

    df = df.copy()
    df["is_outlier_dbscan"] = False

    initial_count = len(df)

    for (user_id, trip_id), group in df.groupby(["user_id", "vehicle_trip_id"]):
        if len(group) < min_samples:
            continue

        # Get GPS coordinates
        coords = group[["latitude", "longitude"]].dropna()
        if len(coords) < min_samples:
            continue

        # Convert lat/lon to approximate meters using a simple projection
        # (more accurate near equator, but sufficient for outlier detection)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        mean_lat = coords["latitude"].mean()
        coords_meters = coords.copy()
        coords_meters["latitude"] = coords["latitude"] * 111000
        coords_meters["longitude"] = (
            coords["longitude"] * 111000 * np.cos(np.radians(mean_lat))
        )

        # Run DBSCAN
        dbscan = DBSCAN(eps=eps_meters, min_samples=min_samples)
        labels = dbscan.fit_predict(coords_meters.values)

        # Mark outliers (label = -1)
        outlier_mask = labels == -1
        df.loc[coords.index[outlier_mask], "is_outlier_dbscan"] = True

    # Remove outliers
    df_filtered = df[~df["is_outlier_dbscan"]].drop("is_outlier_dbscan", axis=1)

    removed_count = initial_count - len(df_filtered)
    print(f"  Detected outliers: {removed_count}")
    print(f"  Removed: {removed_count} points ({removed_count/initial_count*100:.1f}%)")
    print(f"  Remaining: {len(df_filtered)} points")

    return df_filtered


def filter_gps_outliers_knn(df, n_neighbors=5, distance_threshold_meters=200):
    """
    Use KNN to detect GPS outliers based on distance to neighbors.

    Points that are too far from their K nearest neighbors are considered outliers.

    Args:
        df: DataFrame with GPS data
        n_neighbors: Number of nearest neighbors to consider
        distance_threshold_meters: Maximum average distance to neighbors

    Returns:
        DataFrame with outliers removed
    """
    print(f"\n[KNN OUTLIER DETECTION]")
    print(f"  K neighbors: {n_neighbors}")
    print(f"  Distance threshold: {distance_threshold_meters}m")

    df = df.copy()
    df["is_outlier_knn"] = False

    initial_count = len(df)

    for (user_id, trip_id), group in df.groupby(["user_id", "vehicle_trip_id"]):
        if len(group) < n_neighbors + 1:
            continue

        # Get GPS coordinates
        coords = group[["latitude", "longitude"]].dropna()
        if len(coords) < n_neighbors + 1:
            continue

        # Convert to approximate meters
        mean_lat = coords["latitude"].mean()
        coords_meters = coords.copy()
        coords_meters["latitude"] = coords["latitude"] * 111000
        coords_meters["longitude"] = (
            coords["longitude"] * 111000 * np.cos(np.radians(mean_lat))
        )

        # Fit KNN
        knn = NearestNeighbors(n_neighbors=n_neighbors + 1)  # +1 to exclude self
        knn.fit(coords_meters.values)

        # Find distances to K nearest neighbors (excluding self)
        distances, _ = knn.kneighbors(coords_meters.values)
        avg_distances = distances[:, 1:].mean(axis=1)  # Skip first (self)

        # Mark outliers
        outlier_mask = avg_distances > distance_threshold_meters
        df.loc[coords.index[outlier_mask], "is_outlier_knn"] = True

    # Remove outliers
    df_filtered = df[~df["is_outlier_knn"]].drop("is_outlier_knn", axis=1)

    removed_count = initial_count - len(df_filtered)
    print(f"  Detected outliers: {removed_count}")
    print(f"  Removed: {removed_count} points ({removed_count/initial_count*100:.1f}%)")
    print(f"  Remaining: {len(df_filtered)} points")

    return df_filtered


def apply_gps_filtering_pipeline(df):
    """
    Apply complete GPS filtering pipeline.

    Steps:
    1. Filter by GPS quality (accuracy, satellites)
    2. Detect and remove GPS jumps
    3. Remove outliers using DBSCAN
    4. Remove outliers using KNN

    Returns:
        Filtered DataFrame
    """
    print("\n" + "=" * 60)
    print("GPS FILTERING PIPELINE")
    print("=" * 60)

    initial_count = len(df)
    print(f"Initial data: {initial_count} points")

    # Step 1: GPS quality
    df = filter_by_gps_quality(df, min_accuracy=50, min_satellites=4)

    # Step 2: GPS jumps
    df = detect_gps_jumps(df, max_speed_kmh=200, time_threshold_seconds=1)

    # Step 3: DBSCAN outliers
    df = filter_gps_outliers_dbscan(df, eps_meters=100, min_samples=3)

    # Step 4: KNN outliers
    df = filter_gps_outliers_knn(df, n_neighbors=5, distance_threshold_meters=200)

    final_count = len(df)
    total_removed = initial_count - final_count

    print("\n" + "=" * 60)
    print("FILTERING SUMMARY")
    print("=" * 60)
    print(f"Initial points: {initial_count}")
    print(f"Final points: {final_count}")
    print(f"Total removed: {total_removed} ({total_removed/initial_count*100:.1f}%)")
    print(f"Data quality improvement: {final_count/initial_count*100:.1f}% retained")
    print("=" * 60 + "\n")

    return df


def main():
    """Main function - extends the base preparation script with GPS filtering."""
    print("=" * 60)
    print("Transport Validation Classifier - Data Preparation")
    print("WITH GPS OUTLIER FILTERING (KNN + DBSCAN)")
    print("=" * 60)
    print()

    # Import the base preparation functions
    from ml.prepare_transport_validation_data import (
        add_temporal_features,
        add_vehicle_type_encoding,
        clean_data,
        extract_features_from_journey_data,
        print_statistics,
        save_training_data,
    )

    # Connect to database
    db = SessionLocal()

    try:
        # Step 1: Extract raw high-frequency features
        print("Step 1: Extracting raw data from database...")
        df = extract_features_from_journey_data(db)

        if len(df) == 0:
            print("ERROR: No journey data found in database!")
            return

        # Step 2: Apply GPS filtering (NEW!)
        print("\nStep 2: Applying GPS filtering pipeline...")
        df = apply_gps_filtering_pipeline(df)

        if len(df) == 0:
            print(
                "ERROR: All data was filtered out! Consider relaxing filter parameters."
            )
            return

        # Step 3: Add temporal features
        print("\nStep 3: Adding temporal features...")
        df = add_temporal_features(df)

        # Step 4: Add vehicle type encoding
        print("\nStep 4: Encoding vehicle types...")
        df = add_vehicle_type_encoding(df)

        # Step 5: Clean data
        print("\nStep 5: Cleaning data...")
        df = clean_data(df)

        # Step 6: Print statistics
        print_statistics(df)

        # Step 7: Save to CSV
        output_df = save_training_data(
            df, output_path="ml/transport_validation_data_filtered.csv"
        )

        print("\n" + "=" * 60)
        print("Data preparation complete (with GPS filtering)!")
        print("=" * 60)
        print("\nOutput file: ml/transport_validation_data_filtered.csv")
        print("\nThis dataset has improved GPS quality through outlier removal.")
        print("Use this for training if you want to reduce GPS noise effects.")
        print()

    finally:
        db.close()


if __name__ == "__main__":
    main()
