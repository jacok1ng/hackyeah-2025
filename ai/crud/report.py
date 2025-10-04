from datetime import datetime
from typing import List, Optional

import db_models
from models import ReportCreate, ReportUpdate
from sqlalchemy.orm import Session


def create_report(
    db: Session, report: ReportCreate, user_id: str, user_role: str
) -> db_models.Report:
    # Automatically set confidence based on user role
    confidence = 100 if user_role != "PASSENGER" else 50

    report_data = report.model_dump()
    report_data["user_id"] = user_id
    report_data["confidence"] = confidence

    db_report = db_models.Report(**report_data)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_report(db: Session, report_id: str) -> Optional[db_models.Report]:
    return db.query(db_models.Report).filter(db_models.Report.id == report_id).first()


def get_reports(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.Report]:
    return db.query(db_models.Report).offset(skip).limit(limit).all()


def get_reports_by_vehicle_trip(
    db: Session, vehicle_trip_id: str, skip: int = 0, limit: int = 100
) -> List[db_models.Report]:
    return (
        db.query(db_models.Report)
        .filter(db_models.Report.vehicle_trip_id == vehicle_trip_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_reports_by_vehicle(
    db: Session, vehicle_id: str, skip: int = 0, limit: int = 100
) -> List[db_models.Report]:
    return (
        db.query(db_models.Report)
        .filter(db_models.Report.vehicle_id == vehicle_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_reports_by_category(
    db: Session, category: str, skip: int = 0, limit: int = 100
) -> List[db_models.Report]:
    return (
        db.query(db_models.Report)
        .filter(db_models.Report.category == category)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_report(
    db: Session, report_id: str, report_update: ReportUpdate
) -> Optional[db_models.Report]:
    db_report = get_report(db, report_id)
    if not db_report:
        return None

    update_data = report_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)

    db.commit()
    db.refresh(db_report)
    return db_report


def resolve_report(db: Session, report_id: str) -> Optional[db_models.Report]:
    db_report = get_report(db, report_id)
    if not db_report:
        return None

    setattr(db_report, "resolved_at", datetime.now())
    db.commit()
    db.refresh(db_report)
    return db_report


def delete_report(db: Session, report_id: str) -> bool:
    db_report = get_report(db, report_id)
    if not db_report:
        return False
    db.delete(db_report)
    db.commit()
    return True
