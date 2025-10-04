from datetime import datetime
from typing import List, Optional

import db_models
from models import UserJourneyCreate, UserJourneyUpdate
from sqlalchemy.orm import Session


def create_user_journey(
    db: Session, user_journey: UserJourneyCreate, user_id: str
) -> db_models.UserJourney:
    journey_data = user_journey.model_dump()
    journey_data["user_id"] = user_id
    db_user_journey = db_models.UserJourney(**journey_data)
    db.add(db_user_journey)
    db.commit()
    db.refresh(db_user_journey)
    return db_user_journey


def get_user_journey(
    db: Session, journey_id: str
) -> Optional[db_models.UserJourney]:
    return (
        db.query(db_models.UserJourney)
        .filter(db_models.UserJourney.id == journey_id)
        .first()
    )


def get_user_journeys(
    db: Session, user_id: str, skip: int = 0, limit: int = 100
) -> List[db_models.UserJourney]:
    return (
        db.query(db_models.UserJourney)
        .filter(db_models.UserJourney.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_saved_journeys(
    db: Session, user_id: str
) -> List[db_models.UserJourney]:
    """Get user's saved journeys (up to 10)."""
    return (
        db.query(db_models.UserJourney)
        .filter(
            db_models.UserJourney.user_id == user_id,
            db_models.UserJourney.is_saved == True,
        )
        .limit(10)
        .all()
    )


def get_user_active_journey(
    db: Session, user_id: str
) -> Optional[db_models.UserJourney]:
    """Get user's currently active journey."""
    return (
        db.query(db_models.UserJourney)
        .filter(
            db_models.UserJourney.user_id == user_id,
            db_models.UserJourney.is_active == True,
        )
        .first()
    )


def update_user_journey(
    db: Session, journey_id: str, journey_update: UserJourneyUpdate
) -> Optional[db_models.UserJourney]:
    db_user_journey = get_user_journey(db, journey_id)
    if not db_user_journey:
        return None

    update_data = journey_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user_journey, field, value)

    setattr(db_user_journey, "updated_at", datetime.now())

    db.commit()
    db.refresh(db_user_journey)
    return db_user_journey


def delete_user_journey(db: Session, journey_id: str) -> bool:
    db_user_journey = get_user_journey(db, journey_id)
    if not db_user_journey:
        return False
    db.delete(db_user_journey)
    db.commit()
    return True
