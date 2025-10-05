from typing import List

import crud
from database import get_db
from dependencies import get_current_user, require_admin_or_dispatcher
from enums import UserRole
from fastapi import APIRouter, Depends, HTTPException, status
from models import Report, ReportCreate, ReportUpdate, User
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
    """
    return crud.create_report(db, report, str(current_user.id), current_user.role)


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
