"""
CRUD operations for user streak (days in a row) system.
"""

from datetime import date, datetime
from math import asin, cos, radians, sin, sqrt

from db_models import (
    JourneyData,
    Route,
    RouteStop,
    Stop,
    Ticket,
    User,
    UserJourney,
    UserJourneyStop,
    VehicleTrip,
)
from sqlalchemy import and_
from sqlalchemy.orm import Session

import crud

MAX_FREEZE_DAYS = 5
GPS_PROXIMITY_METERS = 100  # Distance threshold for "being at a stop"


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


def match_vehicle_trips_to_user_journey(
    db: Session,
    user_journey_id: str,
    journey_date: date,
    time_tolerance_minutes: int = 60,
) -> list[VehicleTrip]:
    """
    Find VehicleTrips that match the UserJourney based on:
    - Stop overlap (VehicleTrip route contains stops from UserJourney)
    - Time proximity (scheduled time close to journey planned_date)

    Returns list of matching VehicleTrips ordered by best match.
    """
    # Get UserJourney and its stops
    user_journey = (
        db.query(UserJourney).filter(UserJourney.id == user_journey_id).first()
    )
    if not user_journey:
        return []

    user_stops = (
        db.query(UserJourneyStop)
        .filter(UserJourneyStop.user_journey_id == user_journey_id)
        .order_by(UserJourneyStop.stop_order)
        .all()
    )

    if not user_stops:
        return []

    user_stop_ids = {str(stop.stop_id) for stop in user_stops}

    # Time range for matching
    date_start = datetime.combine(journey_date, datetime.min.time())
    date_end = datetime.combine(journey_date, datetime.max.time())

    # Find VehicleTrips scheduled on this date
    vehicle_trips = (
        db.query(VehicleTrip)
        .join(Route)
        .filter(
            and_(
                Route.scheduled_departure >= date_start,
                Route.scheduled_departure <= date_end,
            )
        )
        .all()
    )

    # Score each VehicleTrip by stop overlap
    matching_trips = []

    for trip in vehicle_trips:
        route = trip.route
        if not route:
            continue

        # Get stops on this route
        route_stops = (
            db.query(RouteStop).filter(RouteStop.route_id == str(route.id)).all()
        )

        route_stop_ids = {str(rs.stop_id) for rs in route_stops}

        # Calculate overlap percentage
        overlap = user_stop_ids.intersection(route_stop_ids)
        overlap_percentage = len(overlap) / len(user_stop_ids) if user_stop_ids else 0

        # Require at least 80% overlap to consider this a match
        if overlap_percentage >= 0.8:
            matching_trips.append(
                {
                    "trip": trip,
                    "overlap_percentage": overlap_percentage,
                    "overlap_count": len(overlap),
                }
            )

    # Sort by overlap percentage (best matches first)
    matching_trips.sort(key=lambda x: x["overlap_percentage"], reverse=True)

    return [item["trip"] for item in matching_trips]


def verify_user_was_on_vehicle_trip(
    db: Session,
    user_id: str,
    vehicle_trip_id: str,
    user_journey_stops: list[UserJourneyStop],
    required_percentage: float = 0.8,
) -> dict:
    """
    Verify that user was physically present on the VehicleTrip by checking GPS data.

    EXPERIMENTAL ML VALIDATION:
    ===========================
    Ta funkcja testuje również walidację ML (XGBoost/LightGBM) i loguje wyniki
    do porównania. Model ML trenowany jest na danych sensorowych i może potencjalnie
    zastąpić obecne podejście rule-based.

    TODO: MODEL TRANSFORMER (WYSOKI PRIORYTET)
    ===========================================
    Przyszły kierunek to model Transformer z mechanizmem atencji:

    DLACZEGO TRANSFORMER?
    1. Lepsze rozumienie temporalne (attention na całej sekwencji podróży)
    2. Brak manual feature engineering (uczy się optymalnych cech sam)
    3. Naturalnie obsługuje podróże o zmiennej długości
    4. Bardziej odporny na brakujące/zaszumione dane sensorowe

    ROZSZERZALNOŚĆ DLA EKO-MOBILNOŚCI:
    ==================================
    Po stworzeniu robust Transformer, można go rozszerzyć o:

    1. Klasyfikację multi-modal wszystkich środków transportu:
       - Transport publiczny (autobus, tramwaj, pociąg, metro)
       - Samochód prywatny
       - Rower
       - Pieszo
       - Hulajnoga elektryczna
       - Inne (motocykl, rolki, itp.)

    2. System nagród za eko-mobilność:
       - Punkty za używanie transportu publicznego
       - Odznaki za konsekwentne eko-wybory
       - Tracking śladu węglowego
       - Rankingi i wyzwania

    3. Spersonalizowane sugestie:
       - Rekomendacje eko tras
       - Optymalne kombinacje transportu
       - Trade-offy czas/koszt/węgiel

    4. Analityka miejska:
       - Agregowane wzorce mobilności
       - Identyfikacja potrzeb infrastruktury
       - Optymalizacja tras transportu publicznego

    ŚCIEŻKA IMPLEMENTACJI:
    1. [OBECNIE] Zbieranie danych z rule-based + ML validation
    2. [NASTĘPNIE] Implementacja architektury Transformer
    3. [TESTY] A/B test Transformer vs XGBoost
    4. [PRODUKCJA] Zastąpienie rule-based najlepszym modelem
    5. [ROZSZERZENIE] Rozbudowa o klasyfikację multi-modal
    6. [GAMIFIKACJA] Implementacja systemu nagród

    Returns dict with:
    - verified: bool
    - visited_stops: int
    - total_stops: int
    - percentage: float
    """
    if not user_journey_stops:
        return {
            "verified": False,
            "visited_stops": 0,
            "total_stops": 0,
            "percentage": 0.0,
            "reason": "No stops in journey",
        }

    # Get user's GPS data for this VehicleTrip
    gps_data = (
        db.query(JourneyData)
        .filter(
            and_(
                JourneyData.user_id == user_id,
                JourneyData.vehicle_trip_id == vehicle_trip_id,
            )
        )
        .all()
    )

    if not gps_data:
        return {
            "verified": False,
            "visited_stops": 0,
            "total_stops": len(user_journey_stops),
            "percentage": 0.0,
            "reason": "No GPS data found for this trip",
        }

    # For each stop, check if user's GPS was within proximity
    visited_stops = 0

    for journey_stop in user_journey_stops:
        stop = db.query(Stop).filter(Stop.id == str(journey_stop.stop_id)).first()
        if not stop:
            continue

        stop_lat = float(stop.latitude)  # type: ignore
        stop_lon = float(stop.longitude)  # type: ignore

        # Check if any GPS point was close to this stop
        was_at_stop = False
        for gps_point in gps_data:
            if gps_point.latitude is None or gps_point.longitude is None:
                continue

            distance = calculate_distance(
                float(gps_point.latitude),  # type: ignore
                float(gps_point.longitude),  # type: ignore
                stop_lat,
                stop_lon,
            )

            if distance <= GPS_PROXIMITY_METERS:
                was_at_stop = True
                break

        if was_at_stop:
            visited_stops += 1

    total_stops = len(user_journey_stops)
    percentage = visited_stops / total_stops if total_stops > 0 else 0.0

    result = {
        "verified": percentage >= required_percentage,
        "visited_stops": visited_stops,
        "total_stops": total_stops,
        "percentage": percentage,
        "validation_method": "rule_based_gps_proximity",
        "reason": (
            "Verified"
            if percentage >= required_percentage
            else f"Only visited {visited_stops}/{total_stops} stops ({percentage:.1%})"
        ),
    }

    # EXPERIMENTAL: Test ML-based validation
    # Działa równolegle z rule-based i loguje wyniki do porównania
    # NA RAZIE - TYLKO ZBIERANIE DANYCH (wynik ML nie wpływa na decyzję)
    try:
        # Konwertuj dane GPS do DataFrame dla modelu ML
        import pandas as pd

        gps_df_rows = []
        for gps_point in gps_data:
            gps_df_rows.append(
                {
                    "user_id": user_id,
                    "vehicle_trip_id": vehicle_trip_id,
                    "timestamp": gps_point.timestamp,
                    "latitude": gps_point.latitude,
                    "longitude": gps_point.longitude,
                    "altitude": gps_point.altitude,
                    "speed": gps_point.speed,
                    "bearing": gps_point.bearing,
                    "accuracy": gps_point.accuracy,
                    "satellite_count": gps_point.satellite_count,
                    "acceleration_x": gps_point.acceleration_x,
                    "acceleration_y": gps_point.acceleration_y,
                    "acceleration_z": gps_point.acceleration_z,
                    "linear_acceleration_x": gps_point.linear_acceleration_x,
                    "linear_acceleration_y": gps_point.linear_acceleration_y,
                    "linear_acceleration_z": gps_point.linear_acceleration_z,
                    "gyroscope_x": gps_point.gyroscope_x,
                    "gyroscope_y": gps_point.gyroscope_y,
                    "gyroscope_z": gps_point.gyroscope_z,
                    "pressure": gps_point.pressure,
                }
            )

        if len(gps_df_rows) > 0:
            gps_df = pd.DataFrame(gps_df_rows)

            # Test ML validation (EXPERIMENTAL - tylko logowanie)
            from ml.transport_classifier_inference import validate_transport_ml

            ml_verified, ml_confidence = validate_transport_ml(
                gps_df, result["verified"]
            )

            result["ml_validation"] = {
                "ml_verified": ml_verified,
                "ml_confidence": ml_confidence,
                "status": "experimental_logging_only",
                "note": "Przewidywania ML są logowane ale NIE używane do ostatecznej decyzji",
            }
    except Exception as e:
        # ML validation nie działa - kontynuuj z rule-based
        result["ml_validation"] = {"error": str(e), "status": "failed"}

    return result


def check_user_visited_stops_on_journey(
    db: Session,
    user_id: str,
    user_journey_id: str,
    journey_date: date,
    required_percentage: float = 0.8,
) -> bool:
    """
    Check if user visited at least required_percentage of stops on their UserJourney.
    Returns True if user's location appeared at required_percentage of the journey stops.

    This function:
    1. Finds matching VehicleTrips for the UserJourney
    2. Checks if user's GPS data shows they were on one of those trips
    3. Verifies they visited 80% of planned stops
    """
    # Get UserJourney stops
    user_stops = (
        db.query(UserJourneyStop)
        .filter(UserJourneyStop.user_journey_id == user_journey_id)
        .order_by(UserJourneyStop.stop_order)
        .all()
    )

    if not user_stops:
        return False

    # Find matching VehicleTrips
    matching_trips = match_vehicle_trips_to_user_journey(
        db, user_journey_id, journey_date, time_tolerance_minutes=60
    )

    if not matching_trips:
        # No matching public transport found
        return False

    # Try to verify with each matching trip
    for vehicle_trip in matching_trips:
        verification = verify_user_was_on_vehicle_trip(
            db,
            user_id,
            str(vehicle_trip.id),
            user_stops,
            required_percentage,
        )

        if verification["verified"]:
            # User was verified on this trip
            return True

    # User wasn't verified on any matching trip
    return False


def check_public_transport_availability(
    db: Session,
    user_journey_id: str,
    journey_date: date,
    time_tolerance_minutes: int = 60,
) -> bool:
    """
    Verify that public transport (VehicleTrip) was available for the UserJourney.
    Checks if VehicleTrip existed at the right time covering the journey stops.
    """
    matching_trips = match_vehicle_trips_to_user_journey(
        db, user_journey_id, journey_date, time_tolerance_minutes
    )

    # Return True if at least one matching trip was found
    return len(matching_trips) > 0


def check_user_has_valid_ticket(db: Session, user_id: str, check_date: date) -> bool:
    """
    Check if user had a valid time-based ticket on given date.
    Valid ticket = any time-based ticket covering the date (monthly, daily, etc.)
    """
    # TODO: Implement ticket validation
    # - Check if user has active ticket (monthly, daily, etc.) covering this date
    # - Query Ticket table with date range check

    # For now, check if user has any active ticket
    check_datetime_start = datetime.combine(check_date, datetime.min.time())
    check_datetime_end = datetime.combine(check_date, datetime.max.time())

    time_ticket = (
        db.query(Ticket)
        .filter(
            and_(
                Ticket.user_id == user_id,
                Ticket.valid_from <= check_datetime_end,
                Ticket.valid_to >= check_datetime_start,
            )
        )
        .first()
    )

    return time_ticket is not None


def verify_journey_completion(
    db: Session, user_id: str, user_journey_id: str, check_date: date
) -> dict:
    """
    Verify if user completed their UserJourney on given date using public transport.
    Requirements:
    - Had valid time-based ticket
    - Location appeared at 80% of journey stops
    - Public transport (VehicleTrip) was available on that route at that time

    Returns dict with verification details.
    """
    # Check valid ticket
    has_ticket = check_user_has_valid_ticket(db, user_id, check_date)
    if not has_ticket:
        return {
            "completed": False,
            "reason": "No valid ticket for this date",
            "has_ticket": False,
            "visited_stops": False,
            "transport_available": False,
        }

    # Check if user visited stops
    visited_stops = check_user_visited_stops_on_journey(
        db, user_id, user_journey_id, check_date, 0.8
    )
    if not visited_stops:
        return {
            "completed": False,
            "reason": "Did not visit 80% of journey stops",
            "has_ticket": True,
            "visited_stops": False,
            "transport_available": False,
        }

    # Check if public transport was available
    transport_available = check_public_transport_availability(
        db, user_journey_id, check_date
    )
    if not transport_available:
        return {
            "completed": False,
            "reason": "No public transport available on this route at this time",
            "has_ticket": True,
            "visited_stops": True,
            "transport_available": False,
        }

    return {
        "completed": True,
        "reason": "Journey verified successfully",
        "has_ticket": True,
        "visited_stops": True,
        "transport_available": True,
    }


def update_user_streak(db: Session, user_id: str, journey_date: date) -> User:
    """
    Update user's streak based on verified journey completion.
    Logic:
    - If journey is on consecutive day: streak_days += 1
    - If journey is same day: no change
    - If 1 day gap and has freeze_days: use 1 freeze_day, maintain streak
    - If >1 day gap or no freeze_days: reset streak to 1
    - Every 10 streak days: +1 freeze_day (max 5)
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise ValueError("User not found")

    last_date = user.last_journey_date.date() if user.last_journey_date else None
    current_streak = int(user.streak_days)
    current_freeze = int(user.freeze_days)

    # Same day - no change
    if last_date == journey_date:
        return user

    # First journey ever
    if not last_date:
        user.streak_days = 1  # type: ignore
        user.freeze_days = 0  # type: ignore
        user.last_journey_date = datetime.combine(journey_date, datetime.min.time())  # type: ignore
        db.commit()
        db.refresh(user)
        return user

    # Calculate day gap
    day_gap = (journey_date - last_date).days

    # Consecutive day - increase streak
    if day_gap == 1:
        new_streak = current_streak + 1
        user.streak_days = new_streak  # type: ignore
        user.last_journey_date = datetime.combine(journey_date, datetime.min.time())  # type: ignore

        # Award freeze day every 10 streak days (max 5)
        if new_streak % 10 == 0 and current_freeze < MAX_FREEZE_DAYS:
            user.freeze_days = min(current_freeze + 1, MAX_FREEZE_DAYS)  # type: ignore

    # 1 day gap with freeze available
    elif day_gap == 2 and current_freeze > 0:
        # Use one freeze day, maintain streak
        user.freeze_days = current_freeze - 1  # type: ignore
        user.streak_days = current_streak + 1  # type: ignore
        user.last_journey_date = datetime.combine(journey_date, datetime.min.time())  # type: ignore

    # Gap too large or no freeze - reset streak
    else:
        user.streak_days = 1  # type: ignore
        user.freeze_days = 0  # type: ignore
        user.last_journey_date = datetime.combine(journey_date, datetime.min.time())  # type: ignore

    db.commit()
    db.refresh(user)
    return user


def get_user_streak_info(db: Session, user_id: str) -> dict:
    """Get detailed streak information for a user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise ValueError("User not found")

    today = date.today()
    last_date = user.last_journey_date.date() if user.last_journey_date else None

    streak_days = int(user.streak_days)
    freeze_days = int(user.freeze_days)

    # Calculate days until streak breaks
    days_until_break = 0
    if last_date:
        day_gap = (today - last_date).days
        if day_gap == 0:
            days_until_break = 2 if freeze_days > 0 else 1
        elif day_gap == 1:
            days_until_break = 1 if freeze_days > 0 else 0
        else:
            days_until_break = 0

    # Calculate next freeze day milestone
    next_freeze_milestone = ((streak_days // 10) + 1) * 10
    days_to_next_freeze = next_freeze_milestone - streak_days

    return {
        "user_id": user_id,
        "streak_days": streak_days,
        "freeze_days": freeze_days,
        "last_journey_date": last_date,
        "days_until_break": days_until_break,
        "days_to_next_freeze": (
            days_to_next_freeze if freeze_days < MAX_FREEZE_DAYS else None
        ),
        "can_earn_freeze": freeze_days < MAX_FREEZE_DAYS,
    }
