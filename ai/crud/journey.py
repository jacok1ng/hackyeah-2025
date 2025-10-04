from typing import List, Optional

import db_models
from models import JourneyCreate, JourneyUpdate
from sqlalchemy.orm import Session


def create_journey(db: Session, journey: JourneyCreate) -> db_models.Journey:
    db_journey = db_models.Journey(**journey.model_dump())
    db.add(db_journey)
    db.commit()
    db.refresh(db_journey)
    return db_journey


def get_journey(db: Session, journey_id: str) -> Optional[db_models.Journey]:
    return (
        db.query(db_models.Journey).filter(db_models.Journey.id == journey_id).first()
    )


def get_journeys(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.Journey]:
    return db.query(db_models.Journey).offset(skip).limit(limit).all()


def update_journey(
    db: Session, journey_id: str, journey_update: JourneyUpdate
) -> Optional[db_models.Journey]:
    db_journey = get_journey(db, journey_id)
    if not db_journey:
        return None

    update_data = journey_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_journey, field, value)

    db.commit()
    db.refresh(db_journey)
    return db_journey


def delete_journey(db: Session, journey_id: str) -> bool:
    db_journey = get_journey(db, journey_id)
    if not db_journey:
        return False
    db.delete(db_journey)
    db.commit()
    return True
