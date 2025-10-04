from datetime import datetime
from typing import List, Optional

import db_models
from models import UserCreate, UserUpdate
from sqlalchemy.orm import Session

from crud.utils import hash_password


def create_user(db: Session, user: UserCreate) -> db_models.User:
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hash_password(user.password)
    db_user = db_models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str) -> Optional[db_models.User]:
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.User]:
    return db.query(db_models.User).offset(skip).limit(limit).all()


def update_user(
    db: Session, user_id: str, user_update: UserUpdate
) -> Optional[db_models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True, exclude={"password"})

    if user_update.password:
        update_data["hashed_password"] = hash_password(user_update.password)

    update_data["updated_at"] = datetime.now()

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    # Soft delete
    setattr(db_user, "deleted_at", datetime.now())
    db.commit()
    return True
