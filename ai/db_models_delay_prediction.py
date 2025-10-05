"""
Database model for storing delay predictions.

This is an extension to db_models.py for delay prediction storage.
Can be merged into main db_models.py if needed.
"""

from datetime import datetime

from database import Base
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship


def generate_uuid():
    """Generate UUID for primary keys."""
    from uuid import uuid4

    return str(uuid4())


class DelayPrediction(Base):
    """
    Historical delay predictions for vehicle trips.

    Stores predictions made by the monitoring system for:
    - Performance analysis
    - ML model training data
    - Historical comparison
    """

    __tablename__ = "delay_predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    vehicle_trip_id = Column(String, nullable=False, index=True)

    # Prediction details
    predicted_delay_minutes = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    prediction_method = Column(String, nullable=False)  # "rule_based", "ml_lstm", etc.

    # Prediction components (for analysis)
    current_delay = Column(Float, nullable=True)
    historical_average = Column(Float, nullable=True)
    incident_impact = Column(Float, nullable=True)
    historical_samples = Column(Integer, nullable=True)

    # GPS context
    vehicle_latitude = Column(Float, nullable=True)
    vehicle_longitude = Column(Float, nullable=True)

    # Actual outcome (filled later when trip completes)
    actual_delay_minutes = Column(Float, nullable=True)
    prediction_error = Column(Float, nullable=True)  # abs(predicted - actual)

    # Notification tracking
    notification_sent = Column(Boolean, default=False)
    users_notified = Column(Integer, default=0)

    # Timestamps
    predicted_at = Column(DateTime, default=datetime.now)
    trip_completed_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now)


# Migration SQL (to add table to existing database)
MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS delay_predictions (
    id TEXT PRIMARY KEY,
    vehicle_trip_id TEXT NOT NULL,
    predicted_delay_minutes REAL NOT NULL,
    confidence REAL NOT NULL,
    prediction_method TEXT NOT NULL,
    current_delay REAL,
    historical_average REAL,
    incident_impact REAL,
    historical_samples INTEGER,
    vehicle_latitude REAL,
    vehicle_longitude REAL,
    actual_delay_minutes REAL,
    prediction_error REAL,
    notification_sent BOOLEAN DEFAULT 0,
    users_notified INTEGER DEFAULT 0,
    predicted_at TIMESTAMP,
    trip_completed_at TIMESTAMP,
    created_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_delay_predictions_vehicle_trip 
ON delay_predictions(vehicle_trip_id);

CREATE INDEX IF NOT EXISTS idx_delay_predictions_predicted_at 
ON delay_predictions(predicted_at);
"""
