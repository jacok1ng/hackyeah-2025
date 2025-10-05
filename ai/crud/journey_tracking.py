"""
Functions for real-time journey tracking and progress calculation.
"""

from math import asin, cos, radians, sin, sqrt
from typing import Optional

from db_models import RouteSegment, ShapePoint, Stop, UserJourneyStop
from sqlalchemy.orm import Session


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on earth (in meters).
    Uses Haversine formula.
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Radius of earth in meters
    r = 6371000

    return c * r


def find_nearest_stop_on_journey(
    db: Session,
    user_journey_id: str,
    current_lat: float,
    current_lon: float,
) -> Optional[dict]:
    """
    Find the nearest stop on the user's journey based on current GPS position.
    Returns dict with stop info and distance.
    """
    journey_stops = (
        db.query(UserJourneyStop)
        .filter(UserJourneyStop.user_journey_id == user_journey_id)
        .order_by(UserJourneyStop.stop_order)
        .all()
    )

    if not journey_stops:
        return None

    nearest = None
    min_distance = float("inf")

    for journey_stop in journey_stops:
        stop = db.query(Stop).filter(Stop.id == str(journey_stop.stop_id)).first()
        if not stop:
            continue

        distance = calculate_distance(
            current_lat,
            current_lon,
            float(stop.latitude),  # type: ignore
            float(stop.longitude),  # type: ignore
        )

        if distance < min_distance:
            min_distance = distance
            nearest = {
                "stop": stop,
                "journey_stop": journey_stop,
                "distance": distance,
                "stop_index": journey_stop.stop_order,
            }

    return nearest


def calculate_total_route_distance(
    db: Session, user_journey_id: str
) -> Optional[float]:
    """
    Calculate total distance of the journey using route segments and shape points.
    Returns distance in meters.
    """
    journey_stops = (
        db.query(UserJourneyStop)
        .filter(UserJourneyStop.user_journey_id == user_journey_id)
        .order_by(UserJourneyStop.stop_order)
        .all()
    )

    if len(journey_stops) < 2:
        return 0.0

    total_distance = 0.0

    for i in range(len(journey_stops) - 1):
        from_stop_id = str(journey_stops[i].stop_id)
        to_stop_id = str(journey_stops[i + 1].stop_id)

        # Try to get precise distance from route segment
        segment = (
            db.query(RouteSegment)
            .filter(
                RouteSegment.from_stop_id == from_stop_id,
                RouteSegment.to_stop_id == to_stop_id,
            )
            .first()
        )

        if segment:
            # Get last shape point's distance_traveled
            last_point = (
                db.query(ShapePoint)
                .filter(ShapePoint.shape_id == segment.shape_id)
                .order_by(ShapePoint.shape_pt_sequence.desc())
                .first()
            )

            if last_point:
                dist_traveled = last_point.shape_dist_traveled
                if dist_traveled is not None:
                    total_distance += float(dist_traveled)  # type: ignore
                    continue

        # Fallback: straight-line distance between stops
        from_stop = db.query(Stop).filter(Stop.id == from_stop_id).first()
        to_stop = db.query(Stop).filter(Stop.id == to_stop_id).first()

        if from_stop and to_stop:
            distance = calculate_distance(
                float(from_stop.latitude),  # type: ignore
                float(from_stop.longitude),  # type: ignore
                float(to_stop.latitude),  # type: ignore
                float(to_stop.longitude),  # type: ignore
            )
            total_distance += distance

    return total_distance


def calculate_remaining_distance(
    db: Session,
    user_journey_id: str,
    current_stop_index: int,
    current_lat: float,
    current_lon: float,
) -> dict:
    """
    Calculate remaining distance to next stop and to journey end.
    Returns dict with distances in meters.
    """
    journey_stops = (
        db.query(UserJourneyStop)
        .filter(UserJourneyStop.user_journey_id == user_journey_id)
        .order_by(UserJourneyStop.stop_order)
        .all()
    )

    if not journey_stops or current_stop_index >= len(journey_stops):
        return {
            "distance_to_next_stop": None,
            "distance_to_end": None,
            "next_stop": None,
        }

    # Distance to next stop
    next_stop_index = current_stop_index
    next_journey_stop = journey_stops[next_stop_index]
    next_stop = db.query(Stop).filter(Stop.id == str(next_journey_stop.stop_id)).first()

    distance_to_next = None
    if next_stop:
        distance_to_next = calculate_distance(
            current_lat,
            current_lon,
            float(next_stop.latitude),  # type: ignore
            float(next_stop.longitude),  # type: ignore
        )

    # Distance to end (sum of remaining segments + current distance)
    distance_to_end = distance_to_next if distance_to_next else 0.0

    for i in range(next_stop_index, len(journey_stops) - 1):
        from_stop_id = str(journey_stops[i].stop_id)
        to_stop_id = str(journey_stops[i + 1].stop_id)

        # Try route segment first
        segment = (
            db.query(RouteSegment)
            .filter(
                RouteSegment.from_stop_id == from_stop_id,
                RouteSegment.to_stop_id == to_stop_id,
            )
            .first()
        )

        if segment:
            last_point = (
                db.query(ShapePoint)
                .filter(ShapePoint.shape_id == segment.shape_id)
                .order_by(ShapePoint.shape_pt_sequence.desc())
                .first()
            )

            if last_point:
                dist_traveled = last_point.shape_dist_traveled
                if dist_traveled is not None:
                    distance_to_end += float(dist_traveled)  # type: ignore
                    continue

        # Fallback: straight-line
        from_stop = db.query(Stop).filter(Stop.id == from_stop_id).first()
        to_stop = db.query(Stop).filter(Stop.id == to_stop_id).first()

        if from_stop and to_stop:
            dist = calculate_distance(
                float(from_stop.latitude),  # type: ignore
                float(from_stop.longitude),  # type: ignore
                float(to_stop.latitude),  # type: ignore
                float(to_stop.longitude),  # type: ignore
            )
            distance_to_end += dist

    return {
        "distance_to_next_stop": distance_to_next,
        "distance_to_end": distance_to_end,
        "next_stop": next_stop,
    }


def estimate_time_to_arrival(
    distance_meters: float, average_speed_kmh: float = 30.0
) -> float:
    """
    Estimate time to arrival in minutes based on distance and average speed.
    Default speed: 30 km/h (typical for public transport in city).
    """
    if distance_meters <= 0:
        return 0.0

    # Convert to km
    distance_km = distance_meters / 1000.0

    # Time in hours
    time_hours = distance_km / average_speed_kmh

    # Convert to minutes
    return time_hours * 60.0


def check_if_on_time(
    db: Session,
    user_journey_id: str,
    current_stop_index: int,
    elapsed_minutes: float,
) -> dict:
    """
    Check if journey is on time by comparing with average travel time.
    Returns dict with on_time status and delay in minutes.

    TODO: Implement historical data comparison with average times for different hours.
    For now, uses simple estimation.
    """
    journey_stops = (
        db.query(UserJourneyStop)
        .filter(UserJourneyStop.user_journey_id == user_journey_id)
        .order_by(UserJourneyStop.stop_order)
        .all()
    )

    if not journey_stops:
        return {"on_time": True, "delay_minutes": 0.0}

    # Calculate expected progress
    expected_progress = (elapsed_minutes / 60.0) * 0.5  # Rough estimate: 0.5 stops/min

    actual_progress = current_stop_index
    expected_index = int(expected_progress)

    # Simple comparison
    delay_stops = actual_progress - expected_index

    # Convert to minutes (assuming ~5 min per stop)
    delay_minutes = delay_stops * 5.0

    return {
        "on_time": abs(delay_minutes) <= 5.0,  # Within 5 minutes = on time
        "delay_minutes": delay_minutes,
    }
