from typing import List, Optional

import db_models
from models import JourneyDataCreate, JourneyDataUpdate
from sqlalchemy.orm import Session


def create_journey_data(
    db: Session, journey_data: JourneyDataCreate
) -> db_models.JourneyData:
    db_journey_data = db_models.JourneyData(**journey_data.model_dump())
    db.add(db_journey_data)
    db.commit()
    db.refresh(db_journey_data)
    return db_journey_data


def get_journey_data(
    db: Session, journey_data_id: str
) -> Optional[db_models.JourneyData]:
    return (
        db.query(db_models.JourneyData)
        .filter(db_models.JourneyData.id == journey_data_id)
        .first()
    )


def get_journey_data_list(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.JourneyData]:
    return db.query(db_models.JourneyData).offset(skip).limit(limit).all()


def update_journey_data(
    db: Session, journey_data_id: str, journey_data_update: JourneyDataUpdate
) -> Optional[db_models.JourneyData]:
    db_journey_data = get_journey_data(db, journey_data_id)
    if not db_journey_data:
        return None

    update_data = journey_data_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_journey_data, field, value)

    db.commit()
    db.refresh(db_journey_data)
    return db_journey_data


def delete_journey_data(db: Session, journey_data_id: str) -> bool:
    db_journey_data = get_journey_data(db, journey_data_id)
    if not db_journey_data:
        return False
    db.delete(db_journey_data)
    db.commit()
    return True
