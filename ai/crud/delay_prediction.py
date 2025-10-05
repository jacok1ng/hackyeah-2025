"""
Delay prediction algorithm for public transport.

USAGE:
======
This module is called AUTOMATICALLY by the monitoring system (monitor_delays.py)
which runs every 1-3 minutes to check all active vehicle trips.

You can also call it manually via API endpoints if needed.

CURRENT APPROACH: Rule-based algorithm with historical data analysis
FUTURE IMPROVEMENT: Time series models (LSTM, Prophet, SARIMA)

This module predicts delays for vehicle trips based on:
- Current position vs. scheduled position
- Historical delay patterns for the route
- Active incidents (traffic jams, breakdowns)
- Time of day and day of week patterns
- Weather conditions (if available)

TODO: REPLACE WITH TIME SERIES MODEL (PRIORITY: HIGH)
=====================================================
The current rule-based approach works, but a proper time series model
would provide significantly better predictions:

RECOMMENDED MODELS:
1. **LSTM/GRU (Deep Learning)**
   - Best for complex patterns
   - Can handle multiple features
   - Learns long-term dependencies
   - Framework: PyTorch/TensorFlow

2. **Prophet (Meta)**
   - Easy to use and tune
   - Handles seasonality automatically
   - Good for multiple seasonalities (hourly, daily, weekly)
   - Framework: Prophet library

3. **SARIMA (Statistical)**
   - Classical approach
   - Good for seasonal patterns
   - Explainable results
   - Framework: statsmodels

4. **Transformer (State-of-the-art)**
   - Attention mechanism for temporal data
   - Best performance on large datasets
   - Can capture complex patterns
   - Framework: PyTorch

IMPLEMENTATION PLAN:
1. [CURRENT] Collect training data (JourneyData + actual delays)
2. [NEXT] Implement baseline LSTM model
3. [TESTING] A/B test LSTM vs rule-based
4. [PRODUCTION] Deploy best performing model
5. [ADVANCED] Ensemble of multiple models

FEATURES FOR ML MODEL:
- Historical delays on this route (last 7 days)
- Time of day (rush hour effect)
- Day of week (weekday vs weekend)
- Weather conditions
- Number of stops remaining
- Current speed vs. average speed
- Active incidents on route
- Passenger load (if available)
- Driver experience (if available)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from db_models import JourneyData, Report, RouteStop, VehicleTrip
from enums import ReportCategory
from sqlalchemy import and_, func
from sqlalchemy.orm import Session


def calculate_current_delay(
    db: Session,
    vehicle_trip_id: str,
    current_location_lat: float,
    current_location_lon: float,
) -> Optional[float]:
    """
    Calculate current delay based on actual vs scheduled position.

    Returns delay in minutes (positive = late, negative = early, None = no data).

    Algorithm:
    1. Find nearest scheduled stop
    2. Check scheduled time for that stop
    3. Compare with current time
    4. Return difference
    """
    from crud.journey_tracking import calculate_distance

    trip = db.query(VehicleTrip).filter(VehicleTrip.id == vehicle_trip_id).first()
    if not trip:
        return None

    # Get all route stops for this trip
    route_stops = (
        db.query(RouteStop)
        .filter(RouteStop.route_id == str(trip.route_id))
        .order_by(RouteStop.stop_order)
        .all()
    )

    if not route_stops:
        return None

    # Find nearest stop
    min_distance = float("inf")
    nearest_stop = None
    nearest_index = 0

    for idx, route_stop in enumerate(route_stops):
        stop = route_stop.stop
        if not stop:
            continue

        distance = calculate_distance(
            current_location_lat,
            current_location_lon,
            float(stop.latitude),  # type: ignore
            float(stop.longitude),  # type: ignore
        )

        if distance < min_distance:
            min_distance = distance
            nearest_stop = route_stop
            nearest_index = idx

    if not nearest_stop or not nearest_stop.scheduled_arrival:
        return None

    # Calculate delay
    scheduled_time = nearest_stop.scheduled_arrival
    current_time = datetime.now()

    # If we're past this stop, check if we're actually late
    if current_time > scheduled_time:
        delay_minutes = (current_time - scheduled_time).total_seconds() / 60
        return delay_minutes
    else:
        # We're early or on time
        delay_minutes = -(scheduled_time - current_time).total_seconds() / 60
        return delay_minutes


def get_historical_delays(
    db: Session,
    route_id: str,
    time_of_day_hours: int,
    day_of_week: int,
    lookback_days: int = 7,
) -> List[float]:
    """
    Get historical delays for similar trips (same route, time, day).

    Returns list of delays in minutes from past trips.

    This data is used to predict future delays based on patterns.

    TODO: This should be cached/pre-computed for performance
    """
    # Time window: +/- 1 hour from target time
    time_start = time_of_day_hours - 1
    time_end = time_of_day_hours + 1

    # Date range
    date_start = datetime.now() - timedelta(days=lookback_days)

    # Query historical trips
    historical_trips = (
        db.query(VehicleTrip)
        .filter(
            and_(
                VehicleTrip.route_id == route_id,
                VehicleTrip.scheduled_departure >= date_start,
            )
        )
        .all()
    )

    delays = []

    for trip in historical_trips:
        # Check if trip matches time pattern
        if trip.scheduled_departure:
            trip_hour = trip.scheduled_departure.hour
            trip_day = trip.scheduled_departure.weekday()

            # Match time of day
            if not (time_start <= trip_hour <= time_end):
                continue

            # Match day of week pattern (weekday vs weekend)
            is_weekend = day_of_week >= 5
            trip_is_weekend = trip_day >= 5
            if is_weekend != trip_is_weekend:
                continue

            # Calculate actual delay for this trip
            # TODO: This should come from stored metrics, not calculated each time
            trip_delay = _calculate_trip_delay(db, str(trip.id))
            if trip_delay is not None:
                delays.append(trip_delay)

    return delays


def _calculate_trip_delay(db: Session, vehicle_trip_id: str) -> Optional[float]:
    """
    Calculate average delay for a completed trip.

    TODO: Store this as a metric when trip completes for faster access
    """
    # Get actual journey data
    journey_data = (
        db.query(JourneyData)
        .filter(JourneyData.vehicle_trip_id == vehicle_trip_id)
        .order_by(JourneyData.timestamp)
        .all()
    )

    if not journey_data:
        return None

    trip = db.query(VehicleTrip).filter(VehicleTrip.id == vehicle_trip_id).first()
    if not trip or not trip.scheduled_departure or not trip.scheduled_arrival:
        return None

    # Get actual arrival time (last GPS point)
    if not journey_data[-1].timestamp:
        return None

    actual_arrival = journey_data[-1].timestamp
    scheduled_arrival = trip.scheduled_arrival

    # Calculate delay in minutes
    delay = (actual_arrival - scheduled_arrival).total_seconds() / 60
    return delay


def get_incident_impact(
    db: Session,
    route_id: str,
    vehicle_trip_id: str,
) -> float:
    """
    Calculate delay impact from active incidents on the route.

    Returns estimated additional delay in minutes.

    Incident types and their impact:
    - TRAFFIC_JAM: +10-20 minutes
    - VEHICLE_BREAKDOWN: +30-60 minutes
    - MEDICAL_HELP: +15-30 minutes
    - OTHER: +5-10 minutes
    """
    # Time window for active incidents (last 30 minutes)
    time_threshold = datetime.now() - timedelta(minutes=30)

    # Get active incidents
    incidents = (
        db.query(Report)
        .filter(
            and_(
                Report.vehicle_trip_id == vehicle_trip_id,
                Report.created_at >= time_threshold,
                Report.resolved_at.is_(None),
            )
        )
        .all()
    )

    total_impact = 0.0

    for incident in incidents:
        category = str(incident.category)  # type: ignore

        # Impact based on category (simplified)
        if category == ReportCategory.TRAFFIC_JAM.value:
            impact = 15.0
        elif category == ReportCategory.VEHICLE_BREAKDOWN.value:
            impact = 45.0
        elif category == ReportCategory.MEDICAL_HELP.value:
            impact = 20.0
        else:
            impact = 7.5

        # Weight by confidence (if verified, full impact)
        confidence = float(incident.confidence) / 100.0  # type: ignore
        total_impact += impact * confidence

    return total_impact


def predict_delay(
    db: Session,
    vehicle_trip_id: str,
    current_location_lat: Optional[float] = None,
    current_location_lon: Optional[float] = None,
) -> Dict:
    """
    MAIN FUNCTION: Predict delay for a vehicle trip.

    Combines multiple signals:
    1. Current delay (if vehicle is in progress)
    2. Historical patterns for this route/time
    3. Active incidents impact

    Returns:
    {
        "predicted_delay_minutes": float,
        "confidence": float (0-1),
        "components": {
            "current_delay": float,
            "historical_average": float,
            "incident_impact": float,
        },
        "prediction_method": "rule_based",
        "note": "Replace with time series model for better accuracy"
    }

    TODO: REPLACE WITH ML MODEL
    ===========================
    This rule-based approach should be replaced with a proper
    time series model (LSTM, Prophet, or SARIMA) for:
    - Better accuracy (especially during rush hours)
    - Confidence intervals
    - Multiple horizon predictions (5min, 15min, 30min)
    - Automatic pattern learning
    """
    trip = db.query(VehicleTrip).filter(VehicleTrip.id == vehicle_trip_id).first()

    if not trip:
        return {
            "predicted_delay_minutes": 0.0,
            "confidence": 0.0,
            "error": "Trip not found",
        }

    # Component 1: Current delay (if available)
    current_delay = None
    if current_location_lat and current_location_lon:
        current_delay = calculate_current_delay(
            db, vehicle_trip_id, current_location_lat, current_location_lon
        )

    # Component 2: Historical patterns
    if trip.scheduled_departure:
        time_of_day = trip.scheduled_departure.hour
        day_of_week = trip.scheduled_departure.weekday()
    else:
        time_of_day = datetime.now().hour
        day_of_week = datetime.now().weekday()

    historical_delays = get_historical_delays(
        db, str(trip.route_id), time_of_day, day_of_week
    )

    historical_avg = 0.0
    if historical_delays:
        historical_avg = sum(historical_delays) / len(historical_delays)

    # Component 3: Active incidents
    incident_impact = get_incident_impact(db, str(trip.route_id), vehicle_trip_id)

    # Combine components with weights
    if current_delay is not None:
        # If we have current position, weight it heavily
        predicted_delay = (
            current_delay * 0.6 + historical_avg * 0.2 + incident_impact * 0.2
        )
        confidence = 0.8
    else:
        # No current position, rely on historical + incidents
        predicted_delay = historical_avg * 0.6 + incident_impact * 0.4
        confidence = 0.5

    # Adjust confidence based on data quality
    if len(historical_delays) > 10:
        confidence += 0.1
    if incident_impact > 0:
        confidence += 0.05

    confidence = min(confidence, 1.0)

    return {
        "predicted_delay_minutes": round(predicted_delay, 1),
        "confidence": round(confidence, 2),
        "components": {
            "current_delay": round(current_delay, 1) if current_delay else None,
            "historical_average": round(historical_avg, 1),
            "incident_impact": round(incident_impact, 1),
            "historical_samples": len(historical_delays),
        },
        "prediction_method": "rule_based",
        "note": (
            "This is a simple rule-based prediction. "
            "For better accuracy, this should be replaced with a time series model "
            "(LSTM, Prophet, SARIMA) trained on historical delay patterns."
        ),
    }


def predict_delays_for_route(
    db: Session,
    route_id: str,
    next_hours: int = 2,
) -> List[Dict]:
    """
    Predict delays for all upcoming trips on a route.

    Returns list of predictions for trips in the next N hours.

    Useful for:
    - Journey planning
    - Alternative route suggestions
    - Notifications to users
    """
    # Get upcoming trips
    now = datetime.now()
    end_time = now + timedelta(hours=next_hours)

    upcoming_trips = (
        db.query(VehicleTrip)
        .filter(
            and_(
                VehicleTrip.route_id == route_id,
                VehicleTrip.scheduled_departure >= now,
                VehicleTrip.scheduled_departure <= end_time,
            )
        )
        .order_by(VehicleTrip.scheduled_departure)
        .all()
    )

    predictions = []

    for trip in upcoming_trips:
        prediction = predict_delay(db, str(trip.id))
        prediction["vehicle_trip_id"] = str(trip.id)
        prediction["scheduled_departure"] = (
            trip.scheduled_departure.isoformat() if trip.scheduled_departure else None
        )
        predictions.append(prediction)

    return predictions


def get_delay_statistics(
    db: Session,
    route_id: str,
    days: int = 30,
) -> Dict:
    """
    Get delay statistics for a route over the past N days.

    Useful for:
    - Route reliability analysis
    - Identifying problematic routes
    - Training data for ML models

    Returns:
    {
        "route_id": str,
        "period_days": int,
        "total_trips": int,
        "average_delay_minutes": float,
        "median_delay_minutes": float,
        "max_delay_minutes": float,
        "on_time_percentage": float (within 5 min),
        "delay_by_hour": {...},  # Average delay per hour of day
        "delay_by_day": {...},  # Average delay per day of week
    }
    """
    # TODO: Implement full statistics
    # This would query all completed trips and calculate metrics

    date_start = datetime.now() - timedelta(days=days)

    trips = (
        db.query(VehicleTrip)
        .filter(
            and_(
                VehicleTrip.route_id == route_id,
                VehicleTrip.scheduled_departure >= date_start,
            )
        )
        .all()
    )

    delays = []
    for trip in trips:
        delay = _calculate_trip_delay(db, str(trip.id))
        if delay is not None:
            delays.append(delay)

    if not delays:
        return {
            "route_id": route_id,
            "period_days": days,
            "total_trips": 0,
            "error": "No data available",
        }

    # Calculate statistics
    avg_delay = sum(delays) / len(delays)
    sorted_delays = sorted(delays)
    median_delay = sorted_delays[len(sorted_delays) // 2]
    max_delay = max(delays)

    # On-time = within 5 minutes of schedule
    on_time_count = sum(1 for d in delays if -5 <= d <= 5)
    on_time_pct = (on_time_count / len(delays)) * 100

    return {
        "route_id": route_id,
        "period_days": days,
        "total_trips": len(trips),
        "trips_with_data": len(delays),
        "average_delay_minutes": round(avg_delay, 1),
        "median_delay_minutes": round(median_delay, 1),
        "max_delay_minutes": round(max_delay, 1),
        "on_time_percentage": round(on_time_pct, 1),
        "note": "Detailed hourly/daily breakdown not yet implemented",
    }
