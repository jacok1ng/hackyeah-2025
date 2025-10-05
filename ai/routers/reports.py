from typing import List
from uuid import UUID

import crud
from crud import report_verification
from database import get_db
from dependencies import get_current_user, require_admin_or_dispatcher
from enums import ReportCategory, UserRole
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    Report,
    ReportCreate,
    ReportUpdate,
    ReportVerificationCreate,
    ReportVerificationStatus,
    User,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=Report, status_code=status.HTTP_201_CREATED)
def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new report/incident. Requires authentication.
    Confidence is automatically set to 100% for non-passengers and 50% for passengers.

    Triggers:
    - For VEHICLE_BREAKDOWN, TRAFFIC_JAM, or MEDICAL_HELP reports, finds alternative route
    """
    created_report = crud.create_report(
        db, report, str(current_user.id), current_user.role
    )

    # Trigger 2: Find alternative route for critical reports
    critical_categories = [
        ReportCategory.VEHICLE_BREAKDOWN,
        ReportCategory.TRAFFIC_JAM,
        ReportCategory.MEDICAL_HELP,
    ]

    if report.category in critical_categories:
        # TODO: Implement algorithm to find alternative faster route
        # In production, this would trigger a notification service
        print(
            f"[NOTIFICATION] Finding alternative route for user {current_user.name} due to {report.category.value}"
        )

    return created_report


@router.get("/", response_model=List[Report])
def get_all_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Get all reports. Requires ADMIN or DISPATCHER role."""
    return crud.get_reports(db, skip=skip, limit=limit)


@router.get("/journey/{journey_id}", response_model=List[Report])
def get_reports_by_journey(
    journey_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get reports for a specific journey. Public endpoint."""
    return crud.get_reports_by_journey(db, journey_id, skip=skip, limit=limit)


@router.get("/vehicle/{vehicle_id}", response_model=List[Report])
def get_reports_by_vehicle(
    vehicle_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get reports for a specific vehicle. Public endpoint."""
    return crud.get_reports_by_vehicle(db, vehicle_id, skip=skip, limit=limit)


@router.get("/category/{category}", response_model=List[Report])
def get_reports_by_category(
    category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get reports by category. Public endpoint."""
    return crud.get_reports_by_category(db, category, skip=skip, limit=limit)


@router.get("/{report_id}", response_model=Report)
def get_report(report_id: str, db: Session = Depends(get_db)):
    """Get a specific report. Public endpoint."""
    db_report = crud.get_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return db_report


@router.put("/{report_id}", response_model=Report)
def update_report(
    report_id: str,
    report_update: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a report. Requires authentication.
    Only report owner, ADMIN, or DISPATCHER can edit.
    """
    db_report = crud.get_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Check authorization: owner, admin, or dispatcher
    is_owner = str(db_report.user_id) == str(current_user.id)
    is_admin_or_dispatcher = current_user.role in [
        UserRole.ADMIN.value,
        UserRole.DISPATCHER.value,
    ]

    if not (is_owner or is_admin_or_dispatcher):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reports or must be ADMIN/DISPATCHER",
        )

    db_report = crud.update_report(db, report_id, report_update)
    return db_report


@router.post("/{report_id}/resolve", response_model=Report)
def resolve_report(
    report_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Mark report as resolved. Requires ADMIN or DISPATCHER role."""
    db_report = crud.resolve_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return db_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a report. Requires authentication.
    Only report owner or ADMIN can delete.
    """
    db_report = crud.get_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Check authorization: owner or admin
    is_owner = str(db_report.user_id) == str(current_user.id)
    is_admin = current_user.role == UserRole.ADMIN.value

    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reports or must be ADMIN",
        )

    success = crud.delete_report(db, report_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )


@router.post("/{report_id}/verify", response_model=ReportVerificationStatus)
def verify_report(
    report_id: str,
    verification: ReportVerificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify or deny a report.

    Verification logic:
    1. Driver/Dispatcher/Admin → immediate verification
    2. Passengers:
       - Requires minimum 3 confirmations
       - Requires at least 50% of users on vehicle

    Only users currently on the same vehicle can verify.
    User cannot verify their own report.

    Awards 10 reputation points to report author upon verification.
    """
    # Get report
    db_report = crud.get_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Check if already verified
    if bool(db_report.is_verified):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is already verified",
        )

    # Check if user is trying to verify their own report
    if str(db_report.user_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot verify your own report",
        )

    # Check if user already verified this report
    existing_verification = report_verification.get_user_verification(
        db, report_id, str(current_user.id)
    )
    if existing_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already verified this report",
        )

    # Check if user is on the same vehicle
    users_on_vehicle = report_verification.get_users_on_vehicle_trip(
        db, str(db_report.vehicle_trip_id), time_window_minutes=30
    )

    user_on_vehicle = any(str(u.id) == str(current_user.id) for u in users_on_vehicle)
    is_admin = current_user.role in ["DRIVER", "DISPATCHER", "ADMIN"]

    if not user_on_vehicle and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be on the same vehicle to verify this report",
        )

    # Create verification entry
    report_verification.create_report_verification(
        db, report_id, str(current_user.id), verification.verified
    )

    # Check if report should be verified now
    report_verification.verify_report_if_requirements_met(db, report_id)

    # Get current status
    return get_report_verification_status(report_id, db, current_user)


@router.get("/{report_id}/verification-status", response_model=ReportVerificationStatus)
def get_report_verification_status(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current verification status of a report.

    Shows:
    - Is verified
    - Number of confirmations/denials
    - Total users on vehicle
    - Percentage verified
    - Whether current user can verify
    """
    # Get report
    db_report = crud.get_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Get verification requirements
    requirements = report_verification.check_verification_requirements(db, report_id)

    # Check if current user already verified
    user_verification = report_verification.get_user_verification(
        db, report_id, str(current_user.id)
    )
    user_verified = bool(user_verification.verified) if user_verification else None  # type: ignore

    # Check if user can verify
    users_on_vehicle = report_verification.get_users_on_vehicle_trip(
        db, str(db_report.vehicle_trip_id), time_window_minutes=30
    )
    user_on_vehicle = any(str(u.id) == str(current_user.id) for u in users_on_vehicle)
    is_owner = str(db_report.user_id) == str(current_user.id)

    can_verify = (
        user_on_vehicle
        and not is_owner
        and user_verification is None
        and not bool(db_report.is_verified)
    )

    return ReportVerificationStatus(
        report_id=UUID(report_id),
        is_verified=bool(db_report.is_verified),
        verified_by_admin=bool(db_report.verified_by_admin),
        verifications_count=requirements.get("total_verifications", 0),
        confirmations_count=requirements.get("confirmations_count", 0),
        denials_count=requirements.get("denials_count", 0),
        total_users_on_vehicle=requirements.get("total_users_on_vehicle", 0),
        required_confirmations=requirements.get("required_confirmations", 3),
        verification_percentage=requirements.get("verification_percentage", 0.0),
        can_verify=can_verify,
        user_verified=user_verified,
    )
