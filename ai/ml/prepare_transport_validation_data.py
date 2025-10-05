"""
Prepare training data for transport validation classifier.

This script extracts JourneyData with sensor readings and combines it with
Vehicle information to create features for XGBoost/LightGBM classifier.

The classifier validates whether a user is actually traveling on a specific
public transport vehicle based on sensor data.

Output: CSV file with features and labels for training.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

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

    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(
        delta_lon / 2
    ) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


def calculate_bearing_difference(bearing1, bearing2):
    """Calculate absolute difference between two bearings (0-360 degrees)."""
    diff = abs(bearing1 - bearing2)
    if diff > 180:
        diff = 360 - diff
    return diff


def extract_features_from_journey_data(db):
    """
    Extract features from JourneyData combined with Vehicle information.

    Aggregates high-frequency sensor data (100Hz) to 1Hz with statistics:
    - min, max, avg (mean), median, std for each sensor feature

    Features per 1-second window:
    - GPS: latitude, longitude, altitude, speed, bearing, accuracy
    - Accelerometer: acceleration_x, y, z, linear_acceleration_x, y, z
    - Gyroscope: gyroscope_x, y, z, rotation_vector_x, y, z, w
    - Barometer: pressure
    - Vehicle: type (train/tram/bus), capacity
    - Derived: acceleration_magnitude, gyroscope_magnitude

    Label:
    - is_valid_trip: whether user was actually on this vehicle (boolean)
    """
    print("Fetching JourneyData from database...")

    # Query all journey data with vehicle information
    query = (
        db.query(
            JourneyData,
            Vehicle.vehicle_type_id,
            Vehicle.capacity,
            UserJourney.id.label("user_journey_id"),
        )
        .join(VehicleTrip, JourneyData.vehicle_trip_id == VehicleTrip.id)
        .join(Vehicle, VehicleTrip.vehicle_id == Vehicle.id)
        .outerjoin(
            UserJourney,
            and_(
                JourneyData.user_journey_id == UserJourney.id,
                UserJourney.user_id == JourneyData.user_id,
            ),
        )
        .all()
    )

    print(f"Found {len(query)} journey data records (high-frequency)")

    # First, collect all raw data into a DataFrame
    raw_data_rows = []

    for journey_data, vehicle_type_id, vehicle_capacity, user_journey_id in query:
        # Collect raw sensor data
        row = {
            "journey_data_id": str(journey_data.id),
            "vehicle_trip_id": str(journey_data.vehicle_trip_id),
            "user_id": str(journey_data.user_id) if journey_data.user_id else None,
            "timestamp": journey_data.timestamp,
            # GPS
            "latitude": journey_data.latitude,
            "longitude": journey_data.longitude,
            "altitude": journey_data.altitude,
            "speed": journey_data.speed,
            "bearing": journey_data.bearing,
            "accuracy": journey_data.accuracy,
            "vertical_accuracy": journey_data.vertical_accuracy,
            "satellite_count": journey_data.satellite_count,
            # Accelerometer
            "acceleration_x": journey_data.acceleration_x,
            "acceleration_y": journey_data.acceleration_y,
            "acceleration_z": journey_data.acceleration_z,
            "linear_acceleration_x": journey_data.linear_acceleration_x,
            "linear_acceleration_y": journey_data.linear_acceleration_y,
            "linear_acceleration_z": journey_data.linear_acceleration_z,
            # Gyroscope
            "gyroscope_x": journey_data.gyroscope_x,
            "gyroscope_y": journey_data.gyroscope_y,
            "gyroscope_z": journey_data.gyroscope_z,
            "rotation_vector_x": journey_data.rotation_vector_x,
            "rotation_vector_y": journey_data.rotation_vector_y,
            "rotation_vector_z": journey_data.rotation_vector_z,
            "rotation_vector_w": journey_data.rotation_vector_w,
            # Barometer
            "pressure": journey_data.pressure,
            # Vehicle info
            "vehicle_type_id": vehicle_type_id,
            "vehicle_capacity": vehicle_capacity,
            # Label
            "is_valid_trip": user_journey_id is not None,
        }

        # Calculate derived magnitudes
        if (
            journey_data.acceleration_x is not None
            and journey_data.acceleration_y is not None
            and journey_data.acceleration_z is not None
        ):
            row["acceleration_magnitude"] = np.sqrt(
                journey_data.acceleration_x**2
                + journey_data.acceleration_y**2
                + journey_data.acceleration_z**2
            )
        else:
            row["acceleration_magnitude"] = None

        if (
            journey_data.linear_acceleration_x is not None
            and journey_data.linear_acceleration_y is not None
            and journey_data.linear_acceleration_z is not None
        ):
            row["linear_acceleration_magnitude"] = np.sqrt(
                journey_data.linear_acceleration_x**2
                + journey_data.linear_acceleration_y**2
                + journey_data.linear_acceleration_z**2
            )
        else:
            row["linear_acceleration_magnitude"] = None

        if (
            journey_data.gyroscope_x is not None
            and journey_data.gyroscope_y is not None
            and journey_data.gyroscope_z is not None
        ):
            row["gyroscope_magnitude"] = np.sqrt(
                journey_data.gyroscope_x**2
                + journey_data.gyroscope_y**2
                + journey_data.gyroscope_z**2
            )
        else:
            row["gyroscope_magnitude"] = None

        raw_data_rows.append(row)

    # Convert to DataFrame
    raw_df = pd.DataFrame(raw_data_rows)
    print(f"Created raw dataframe with {len(raw_df)} rows")

    if len(raw_df) == 0:
        return raw_df

    # Aggregate to 1Hz (1 sample per second)
    print("Aggregating 100Hz data to 1Hz with statistics (min, max, avg, median, std)...")
    aggregated_df = aggregate_to_1hz(raw_df)

    print(f"Aggregated to {len(aggregated_df)} rows (1Hz)")
    return aggregated_df


def aggregate_to_1hz(df):
    """
    Aggregate high-frequency sensor data to 1Hz with statistics.

    For each 1-second window, calculates:
    - min, max, mean (avg), median, std for numeric sensor features
    - mode for categorical features (vehicle_type_id, vehicle_capacity)
    - first value for identifiers and timestamps
    """
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Create 1-second window bins
    df["timestamp_1s"] = df["timestamp"].dt.floor("1S")

    # Define sensor features to aggregate
    sensor_features = [
        "latitude",
        "longitude",
        "altitude",
        "speed",
        "bearing",
        "accuracy",
        "vertical_accuracy",
        "satellite_count",
        "acceleration_x",
        "acceleration_y",
        "acceleration_z",
        "linear_acceleration_x",
        "linear_acceleration_y",
        "linear_acceleration_z",
        "gyroscope_x",
        "gyroscope_y",
        "gyroscope_z",
        "rotation_vector_x",
        "rotation_vector_y",
        "rotation_vector_z",
        "rotation_vector_w",
        "pressure",
        "acceleration_magnitude",
        "linear_acceleration_magnitude",
        "gyroscope_magnitude",
    ]

    # Group by user, vehicle trip, and 1-second window
    groupby_cols = ["user_id", "vehicle_trip_id", "timestamp_1s"]

    # Build aggregation dictionary
    agg_dict = {}

    # For each sensor feature, calculate min, max, mean, median, std
    for feature in sensor_features:
        if feature in df.columns:
            agg_dict[f"{feature}_min"] = (feature, "min")
            agg_dict[f"{feature}_max"] = (feature, "max")
            agg_dict[f"{feature}_avg"] = (feature, "mean")
            agg_dict[f"{feature}_median"] = (feature, "median")
            agg_dict[f"{feature}_std"] = (feature, "std")

    # Keep first value for identifiers and categorical features
    agg_dict["journey_data_id"] = ("journey_data_id", "first")
    agg_dict["timestamp"] = ("timestamp", "first")
    agg_dict["vehicle_type_id"] = ("vehicle_type_id", "first")
    agg_dict["vehicle_capacity"] = ("vehicle_capacity", "first")
    agg_dict["is_valid_trip"] = ("is_valid_trip", "first")

    # Perform aggregation
    aggregated = df.groupby(groupby_cols, as_index=False).agg(**agg_dict)

    # Drop the timestamp_1s column (used only for grouping)
    aggregated = aggregated.drop("timestamp_1s", axis=1)

    return aggregated


def add_temporal_features(df):
    """
    Add time-based features for each user's journey.

    Features:
    - hour_of_day
    - day_of_week
    - is_weekend
    - rolling speed/acceleration statistics (over last N samples at 1Hz)
    """
    print("Adding temporal features...")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # Sort by user and timestamp
    df = df.sort_values(["user_id", "vehicle_trip_id", "timestamp"]).reset_index(
        drop=True
    )

    # Calculate rolling statistics (window of 5 samples at 1Hz = 5 seconds)
    window_size = 5

    for user_id in df["user_id"].dropna().unique():
        user_mask = df["user_id"] == user_id

        # Rolling speed statistics (using the avg from 1Hz aggregation)
        if "speed_avg" in df.columns and df.loc[user_mask, "speed_avg"].notna().any():
            df.loc[user_mask, "speed_rolling_std"] = (
                df.loc[user_mask, "speed_avg"]
                .rolling(window_size, min_periods=1)
                .std()
            )
            df.loc[user_mask, "speed_rolling_range"] = (
                df.loc[user_mask, "speed_max"] - df.loc[user_mask, "speed_min"]
            )

        # Rolling acceleration statistics
        if (
            "acceleration_magnitude_avg" in df.columns
            and df.loc[user_mask, "acceleration_magnitude_avg"].notna().any()
        ):
            df.loc[user_mask, "acceleration_rolling_std"] = (
                df.loc[user_mask, "acceleration_magnitude_avg"]
                .rolling(window_size, min_periods=1)
                .std()
            )

        # Bearing change rate (using avg bearing)
        if (
            "bearing_avg" in df.columns
            and df.loc[user_mask, "bearing_avg"].notna().any()
        ):
            df.loc[user_mask, "bearing_change_rate"] = (
                df.loc[user_mask, "bearing_avg"].diff().abs()
            )

    return df


def add_vehicle_type_encoding(df):
    """
    One-hot encode vehicle types.

    Creates binary columns:
    - is_train
    - is_tram
    - is_bus
    """
    print("Encoding vehicle types...")

    # Map vehicle_type_id to vehicle type
    # Assuming: train, tram, bus based on your seed data
    df["is_train"] = (df["vehicle_type_id"] == "train").astype(int)
    df["is_tram"] = (df["vehicle_type_id"] == "tram").astype(int)
    df["is_bus"] = (df["vehicle_type_id"] == "bus").astype(int)

    return df


def clean_data(df):
    """
    Clean and prepare data for training.

    - Handle missing values
    - Remove rows with critical missing data
    - Convert boolean labels to int
    """
    print("Cleaning data...")

    initial_rows = len(df)

    # Remove rows with missing GPS coordinates (critical)
    df = df.dropna(subset=["latitude", "longitude"])

    # Convert label to int
    df["is_valid_trip"] = df["is_valid_trip"].astype(int)

    # Fill missing numeric values with 0 or median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().any():
            # Use median for sensor readings, 0 for derived features
            if col.startswith("speed") or col.startswith("acceleration"):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(0)

    final_rows = len(df)
    print(f"Removed {initial_rows - final_rows} rows with critical missing data")
    print(f"Final dataset: {final_rows} rows")

    return df


def save_training_data(df, output_path="ml/transport_validation_data.csv"):
    """Save processed data to CSV file."""
    print(f"Saving training data to {output_path}...")

    # Select feature columns and label
    feature_cols = [
        col
        for col in df.columns
        if col
        not in [
            "journey_data_id",
            "vehicle_trip_id",
            "user_id",
            "timestamp",
            "user_journey_id",
            "vehicle_type_id",
        ]
    ]

    output_df = df[feature_cols + ["is_valid_trip"]]

    output_df.to_csv(output_path, index=False)
    print(f"Saved {len(output_df)} rows to {output_path}")

    # Print feature summary
    print("\n=== Feature Summary ===")
    print(f"Total features: {len(feature_cols)}")
    print(f"Label distribution:")
    print(output_df["is_valid_trip"].value_counts())
    print("\nFeature list:")
    for i, col in enumerate(feature_cols, 1):
        print(f"  {i:2d}. {col}")

    return output_df


def print_statistics(df):
    """Print dataset statistics."""
    print("\n=== Dataset Statistics ===")
    print(f"Total records: {len(df)}")
    print(f"Unique users: {df['user_id'].nunique()}")
    print(f"Unique vehicle trips: {df['vehicle_trip_id'].nunique()}")
    print(f"\nLabel distribution:")
    print(df["is_valid_trip"].value_counts())
    print(f"\nVehicle type distribution:")
    print(f"  Trains: {df['is_train'].sum()}")
    print(f"  Trams: {df['is_tram'].sum()}")
    print(f"  Buses: {df['is_bus'].sum()}")
    print(f"\nMissing values by feature:")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if len(missing) > 0:
        for col, count in missing.items():
            pct = (count / len(df)) * 100
            print(f"  {col}: {count} ({pct:.1f}%)")
    else:
        print("  No missing values")


def main():
    """Main function to prepare training data."""
    print("=" * 60)
    print("Transport Validation Classifier - Data Preparation")
    print("=" * 60)
    print()

    # Connect to database
    db = SessionLocal()

    try:
        # Step 1: Extract features from JourneyData
        df = extract_features_from_journey_data(db)

        if len(df) == 0:
            print("ERROR: No journey data found in database!")
            print("Please run the application and collect some journey data first.")
            return

        # Step 2: Add temporal features
        df = add_temporal_features(df)

        # Step 3: Add vehicle type encoding
        df = add_vehicle_type_encoding(df)

        # Step 4: Clean data
        df = clean_data(df)

        # Step 5: Print statistics
        print_statistics(df)

        # Step 6: Save to CSV
        output_df = save_training_data(df)

        print("\n" + "=" * 60)
        print("Data preparation complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the generated CSV file: ml/transport_validation_data.csv")
        print("2. Run the training script to build XGBoost/LightGBM models")
        print("3. Evaluate model performance on test set")
        print()

    finally:
        db.close()


if __name__ == "__main__":
    main()
