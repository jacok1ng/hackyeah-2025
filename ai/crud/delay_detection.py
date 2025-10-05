"""
Delay detection and notification system.

Detects delays based on:
1. Historical data - comparing current time with average times (+/- 1h)
2. Verified reports - confirmed by driver/dispatcher or group of passengers
"""

import json
from typing import Dict, List, Optional
from uuid import UUID

from db_models import Report, User, UserJourney, VehicleTrip
from enums import NotificationType, ReportCategory
from models import SystemNotification
from sqlalchemy import and_
from sqlalchemy.orm import Session

from crud.report_verification import get_users_on_vehicle_trip


def detect_delay_from_historical_data(
    db: Session,
    vehicle_trip_id: str,
    current_stop_index: int,
    elapsed_minutes: float,
    time_tolerance_hours: int = 1,
) -> Optional[Dict]:
    """
    Detect delay by comparing current progress with historical average.

    Compares elapsed time to reach current_stop_index with average times
    from similar journeys (same route, +/- time_tolerance_hours).

    Returns dict with delay info if detected, None otherwise.
    """
    # Get current trip info
    vehicle_trip = (
        db.query(VehicleTrip).filter(VehicleTrip.id == vehicle_trip_id).first()
    )
    if not vehicle_trip:
        return None

    # Get current time of day
    # current_time = datetime.now()
    # time_window_start = current_time - timedelta(hours=time_tolerance_hours)
    # time_window_end = current_time + timedelta(hours=time_tolerance_hours)

    # Find historical trips on same route within time window
    # This is a simplified placeholder - in production, you'd need:
    # - Journey duration tracking (actual_departure to current time)
    # - Historical average for this route at this time
    # - Stop-by-stop progress tracking

    # TODO: Implement full historical comparison logic
    # For now, return placeholder detection
    # A real implementation would:
    # 1. Query past VehicleTrips on same route
    # 2. Calculate average time to reach current_stop_index
    # 3. Compare with elapsed_minutes
    # 4. Return delay info if difference > threshold (e.g., 10 minutes)

    return None  # Placeholder - no delay detected


def detect_delay_from_verified_report(
    db: Session, vehicle_trip_id: str
) -> Optional[Dict]:
    """
    Check if there's a verified delay-related report for this vehicle trip.

    Returns dict with delay info if verified report exists, None otherwise.
    """
    # Find verified reports for this trip in delay-related categories
    delay_categories = [
        ReportCategory.VEHICLE_BREAKDOWN.value,
        ReportCategory.TRAFFIC_JAM.value,
    ]

    verified_report = (
        db.query(Report)
        .filter(
            and_(
                Report.vehicle_trip_id == vehicle_trip_id,
                Report.category.in_(delay_categories),
                Report.is_verified == True,  # noqa: E712
            )
        )
        .first()
    )

    if verified_report:
        return {
            "detected": True,
            "reason": "verified_report",
            "report_id": str(verified_report.id),
            "category": verified_report.category,
            "description": verified_report.description,
        }

    return None


def send_alternative_route_to_users(
    db: Session, vehicle_trip_id: str, delay_info: Dict
) -> List[SystemNotification]:
    """
    Send alternative route suggestions to all users currently in the vehicle.

    Returns list of SystemNotification objects sent to users.
    """
    # Get users currently on this vehicle
    users_on_vehicle = get_users_on_vehicle_trip(
        db, vehicle_trip_id, time_window_minutes=30
    )

    notifications = []

    for user in users_on_vehicle:
        # Get user's active journey
        user_journey = (
            db.query(UserJourney)
            .filter(
                and_(
                    UserJourney.user_id == str(user.id),
                    UserJourney.is_in_progress == True,  # noqa: E712
                )
            )
            .first()
        )

        if user_journey:
            # TODO: Calculate alternative route using Google Maps API
            # For now, create notification with placeholder message

            notification = SystemNotification(
                notification_type=NotificationType.DELAY_DETECTED,
                message=(
                    f"Delay detected on your route. "
                    f"Reason: {delay_info.get('reason', 'unknown')}. "
                    f"Calculating alternative route..."
                ),
                related_journey_id=UUID(str(user_journey.id)),
                related_report_id=(
                    UUID(delay_info["report_id"])
                    if delay_info.get("report_id")
                    else None
                ),
            )

            # In production, this would be sent via push notification, SMS, etc.
            print(f"[NOTIFICATION] To user {user.name}: {notification.message}")
            notifications.append(notification)

    return notifications


def send_delay_notification_to_families(
    db: Session, vehicle_trip_id: str, delay_info: Dict
) -> List[SystemNotification]:
    """
    Send delay notifications to family members of users in the delayed vehicle.

    Returns list of SystemNotification objects sent to family members.
    """
    # Get users currently on this vehicle
    users_on_vehicle = get_users_on_vehicle_trip(
        db, vehicle_trip_id, time_window_minutes=30
    )

    notifications = []

    for user in users_on_vehicle:
        # Parse family members (stored as JSON array)
        family_members_str = str(user.family_members) if user.family_members else None  # type: ignore
        if not family_members_str:
            continue

        try:
            family_member_ids = json.loads(family_members_str)
        except (json.JSONDecodeError, TypeError):
            continue

        # Get family member users
        family_members = (
            db.query(User).filter(User.id.in_(family_member_ids)).all()  # type: ignore
        )

        for family_member in family_members:
            notification = SystemNotification(
                notification_type=NotificationType.FAMILY_MEMBER_DELAYED,
                message=(
                    f"{user.name} is experiencing a delay on their journey. "  # type: ignore
                    f"Reason: {delay_info.get('reason', 'unknown')}. "
                    f"Estimated additional delay: {delay_info.get('estimated_delay_minutes', '?')} minutes."
                ),
            )

            # In production, this would be sent via push notification, SMS, etc.
            print(
                f"[FAMILY NOTIFICATION] To {family_member.name}: {notification.message}"  # type: ignore
            )
            notifications.append(notification)

    return notifications


def handle_delay_detection(
    db: Session,
    vehicle_trip_id: str,
    current_stop_index: Optional[int] = None,
    elapsed_minutes: Optional[float] = None,
) -> Dict:
    """
    Main function to detect delays and send notifications.

    Checks both historical data and verified reports.
    If delay detected, sends:
    - Alternative routes to users in vehicle
    - Delay notifications to their family members

    Returns dict with detection results and sent notifications.
    """
    delay_detected = False
    delay_info = None

    # Check historical data (if provided)
    if current_stop_index is not None and elapsed_minutes is not None:
        historical_delay = detect_delay_from_historical_data(
            db, vehicle_trip_id, current_stop_index, elapsed_minutes
        )
        if historical_delay:
            delay_detected = True
            delay_info = historical_delay

    # Check verified reports
    report_delay = detect_delay_from_verified_report(db, vehicle_trip_id)
    if report_delay:
        delay_detected = True
        delay_info = report_delay

    if not delay_detected:
        return {
            "delay_detected": False,
            "alternative_routes_sent": 0,
            "family_notifications_sent": 0,
        }

    # Send notifications
    alternative_route_notifications = send_alternative_route_to_users(
        db, vehicle_trip_id, delay_info or {}
    )

    family_notifications = send_delay_notification_to_families(
        db, vehicle_trip_id, delay_info or {}
    )

    return {
        "delay_detected": True,
        "delay_info": delay_info,
        "alternative_routes_sent": len(alternative_route_notifications),
        "family_notifications_sent": len(family_notifications),
        "alternative_route_notifications": alternative_route_notifications,
        "family_notifications": family_notifications,
    }
