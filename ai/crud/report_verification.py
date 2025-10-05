"""
CRUD operations for report verification system.
"""

from datetime import datetime, timedelta
from typing import List

from db_models import JourneyData, Report, ReportVerification, User, UserJourney
from sqlalchemy import and_
from sqlalchemy.orm import Session


def get_users_on_vehicle_trip(
    db: Session, vehicle_trip_id: str, time_window_minutes: int = 30
) -> List[User]:
    """
    Find all users currently on this vehicle trip.

    Logic:
    - Users who have recent JourneyData for this vehicle_trip_id (within time_window)
    - OR users with active UserJourney linked to this vehicle_trip

    Args:
        db: Database session
        vehicle_trip_id: VehicleTrip ID
        time_window_minutes: Time window for "recent" GPS data (default 30 min)

    Returns:
        List of User objects on this vehicle
    """
    time_threshold = datetime.now() - timedelta(minutes=time_window_minutes)

    # Find users with recent GPS data on this vehicle
    users_with_gps = (
        db.query(User)
        .join(JourneyData)
        .filter(
            and_(
                JourneyData.vehicle_trip_id == vehicle_trip_id,
                JourneyData.timestamp >= time_threshold,
            )
        )
        .distinct()
        .all()
    )

    # Find users with active journey for this vehicle
    users_with_active_journey = (
        db.query(User)
        .join(UserJourney)
        .join(JourneyData, JourneyData.user_journey_id == UserJourney.id)
        .filter(
            and_(
                UserJourney.is_in_progress == True,  # noqa: E712
                JourneyData.vehicle_trip_id == vehicle_trip_id,
            )
        )
        .distinct()
        .all()
    )

    # Combine and deduplicate
    all_users = {user.id: user for user in users_with_gps}
    for user in users_with_active_journey:
        all_users[user.id] = user

    return list(all_users.values())


def create_report_verification(
    db: Session, report_id: str, user_id: str, verified: bool
) -> ReportVerification:
    """
    Create a verification entry for a report.

    Args:
        report_id: Report ID
        user_id: User who is verifying
        verified: True = confirm, False = deny

    Returns:
        Created ReportVerification
    """
    db_verification = ReportVerification(
        report_id=report_id,
        user_id=user_id,
        verified=verified,
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    return db_verification


def get_report_verifications(db: Session, report_id: str) -> List[ReportVerification]:
    """Get all verifications for a report."""
    return (
        db.query(ReportVerification)
        .filter(ReportVerification.report_id == report_id)
        .all()
    )


def get_user_verification(
    db: Session, report_id: str, user_id: str
) -> ReportVerification | None:
    """Check if user already verified this report."""
    return (
        db.query(ReportVerification)
        .filter(
            and_(
                ReportVerification.report_id == report_id,
                ReportVerification.user_id == user_id,
            )
        )
        .first()
    )


def check_verification_requirements(db: Session, report_id: str) -> dict:
    """
    Check if report meets verification requirements.

    Requirements:
    1. Driver/Dispatcher verification → immediate verification
    2. Passenger verification:
       - Minimum 3 confirmations
       - At least 50% of users on vehicle

    Returns:
        Dict with verification status and details
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return {"error": "Report not found"}

    # Get all verifications
    verifications = get_report_verifications(db, report_id)

    confirmations = [v for v in verifications if bool(v.verified)]  # type: ignore
    denials = [v for v in verifications if not bool(v.verified)]  # type: ignore

    # Check if verified by admin (driver/dispatcher)
    for verification in confirmations:
        user = db.query(User).filter(User.id == verification.user_id).first()
        if user and user.role in ["DRIVER", "DISPATCHER", "ADMIN"]:
            return {
                "should_verify": True,
                "reason": "Verified by admin/driver/dispatcher",
                "verified_by_admin": True,
                "confirmations_count": len(confirmations),
                "denials_count": len(denials),
                "total_verifications": len(verifications),
            }

    # Passenger verification requirements
    users_on_vehicle = get_users_on_vehicle_trip(
        db, str(report.vehicle_trip_id), time_window_minutes=30
    )
    total_users = len(users_on_vehicle)

    confirmations_count = len(confirmations)
    verification_percentage = (
        (confirmations_count / total_users * 100) if total_users > 0 else 0
    )

    # Requirements: >= 3 confirmations AND >= 50%
    required_confirmations = max(3, int(total_users * 0.5))
    should_verify = (
        confirmations_count >= required_confirmations
        and verification_percentage >= 50.0
    )

    return {
        "should_verify": should_verify,
        "reason": (
            f"Passenger verification: {confirmations_count}/{total_users} "
            f"({verification_percentage:.1f}%)"
        ),
        "verified_by_admin": False,
        "confirmations_count": confirmations_count,
        "denials_count": len(denials),
        "total_verifications": len(verifications),
        "total_users_on_vehicle": total_users,
        "required_confirmations": required_confirmations,
        "verification_percentage": verification_percentage,
    }


def verify_report_if_requirements_met(db: Session, report_id: str) -> bool:
    """
    Check and verify report if requirements are met.
    Also awards reputation points to report author.

    Returns:
        True if report was verified, False otherwise
    """
    requirements = check_verification_requirements(db, report_id)

    if requirements.get("error"):
        return False

    if not requirements["should_verify"]:
        return False

    # Verify the report
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return False

    # Check if already verified
    is_verified = bool(report.is_verified)  # type: ignore
    if is_verified:
        return False

    report.is_verified = True  # type: ignore
    report.verified_at = datetime.now()  # type: ignore
    report.verified_by_admin = requirements["verified_by_admin"]  # type: ignore
    report.confidence = 100  # type: ignore

    # Award points to report author
    author = db.query(User).filter(User.id == str(report.user_id)).first()
    if author:
        # Award reputation points (10 points for verified report)
        current_points = int(author.reputation_points)  # type: ignore
        author.reputation_points = current_points + 10  # type: ignore

        # Increment verified reports count
        verified_count = int(author.verified_reports_count)  # type: ignore
        author.verified_reports_count = verified_count + 1  # type: ignore

        # Update badge based on verified reports
        if verified_count >= 50:
            author.badge = "Expert Reporter"  # type: ignore
        elif verified_count >= 20:
            author.badge = "Experienced Reporter"  # type: ignore
        elif verified_count >= 5:
            author.badge = "Active Reporter"  # type: ignore
        elif verified_count >= 1:
            author.badge = "New Reporter"  # type: ignore

    db.commit()

    # Check if this is a delay-related report
    from enums import ReportCategory

    from crud.delay_detection import handle_delay_detection

    delay_categories = [
        ReportCategory.VEHICLE_BREAKDOWN.value,
        ReportCategory.TRAFFIC_JAM.value,
    ]

    report_category = str(report.category)  # type: ignore
    if report_category in delay_categories:
        # Trigger delay detection and notifications
        vehicle_trip_id = str(report.vehicle_trip_id)
        delay_result = handle_delay_detection(db, vehicle_trip_id)

        print("[DELAY DETECTION] Verified report triggered delay handling:")
        print(f"  - Report ID: {report_id}")
        print(f"  - Category: {report_category}")
        print(f"  - Alternative routes sent: {delay_result['alternative_routes_sent']}")
        print(
            f"  - Family notifications sent: {delay_result['family_notifications_sent']}"
        )

    return True
