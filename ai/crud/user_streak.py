"""
CRUD operations for user streak (days in a row) system.
"""

from datetime import date, datetime

from db_models import Ticket, User
from sqlalchemy import and_
from sqlalchemy.orm import Session

import crud

MAX_FREEZE_DAYS = 5


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
    """
    # TODO: Implement algorithm to check if user was at 80% of journey stops
    # - Get UserJourney and its stops
    # - Get user's GPS data (JourneyData) for this date
    # - Check proximity to each stop (e.g., within 100 meters)
    # - Return True if visited >= 80% of stops

    # For now, return True for testing
    return True


def check_public_transport_availability(
    db: Session,
    user_journey_id: str,
    journey_date: date,
    time_tolerance_minutes: int = 30,
) -> bool:
    """
    Verify that public transport (VehicleTrip) was available for the UserJourney.
    Checks if VehicleTrip existed at the right time covering the journey stops.
    """
    # TODO: Implement algorithm to verify public transport availability
    # - Get UserJourney stops
    # - Find VehicleTrips scheduled on this date
    # - Check if any VehicleTrip covers >= 80% of journey stops
    # - Optionally: check timing (was trip at the right time when user traveled?)
    # - Return True if appropriate public transport was available

    # For now, return True for testing
    return True


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
