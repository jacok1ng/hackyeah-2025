from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import Report, ReportCreate, ReportUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=Report, status_code=status.HTTP_201_CREATED)
def create_report(
    report: ReportCreate,
    user_id: str,
    user_role: str,
    db: Session = Depends(get_db),
):
    """
    Create a new report/incident.
    Confidence is automatically set to 100% for non-passengers and 50% for passengers.
    """
    return crud.create_report(db, report, user_id, user_role)


@router.get("/", response_model=List[Report])
def get_all_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_reports(db, skip=skip, limit=limit)


@router.get("/journey/{journey_id}", response_model=List[Report])
def get_reports_by_journey(
    journey_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_reports_by_journey(db, journey_id, skip=skip, limit=limit)


@router.get("/vehicle/{vehicle_id}", response_model=List[Report])
def get_reports_by_vehicle(
    vehicle_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_reports_by_vehicle(db, vehicle_id, skip=skip, limit=limit)


@router.get("/category/{category}", response_model=List[Report])
def get_reports_by_category(
    category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_reports_by_category(db, category, skip=skip, limit=limit)


@router.get("/{report_id}", response_model=Report)
def get_report(report_id: str, db: Session = Depends(get_db)):
    db_report = crud.get_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return db_report


@router.put("/{report_id}", response_model=Report)
def update_report(
    report_id: str, report_update: ReportUpdate, db: Session = Depends(get_db)
):
    db_report = crud.update_report(db, report_id, report_update)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return db_report


@router.post("/{report_id}/resolve", response_model=Report)
def resolve_report(report_id: str, db: Session = Depends(get_db)):
    """Mark report as resolved"""
    db_report = crud.resolve_report(db, report_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return db_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: str, db: Session = Depends(get_db)):
    success = crud.delete_report(db, report_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
