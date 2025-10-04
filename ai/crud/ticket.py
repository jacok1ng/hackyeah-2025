from datetime import datetime
from typing import List, Optional

import db_models
from models import TicketCreate, TicketUpdate
from sqlalchemy.orm import Session


def create_ticket(
    db: Session, ticket: TicketCreate, user_id: str
) -> db_models.Ticket:
    ticket_data = ticket.model_dump()
    ticket_data["user_id"] = user_id
    db_ticket = db_models.Ticket(**ticket_data)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_ticket(db: Session, ticket_id: str) -> Optional[db_models.Ticket]:
    return db.query(db_models.Ticket).filter(db_models.Ticket.id == ticket_id).first()


def get_tickets(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.Ticket]:
    return db.query(db_models.Ticket).offset(skip).limit(limit).all()


def get_user_tickets(
    db: Session, user_id: str, skip: int = 0, limit: int = 100
) -> List[db_models.Ticket]:
    return (
        db.query(db_models.Ticket)
        .filter(db_models.Ticket.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_active_user_tickets(
    db: Session, user_id: str
) -> List[db_models.Ticket]:
    """Get user's currently active (valid) tickets."""
    now = datetime.now()
    return (
        db.query(db_models.Ticket)
        .filter(
            db_models.Ticket.user_id == user_id,
            db_models.Ticket.valid_from <= now,
            db_models.Ticket.valid_to >= now,
        )
        .all()
    )


def update_ticket(
    db: Session, ticket_id: str, ticket_update: TicketUpdate
) -> Optional[db_models.Ticket]:
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None

    update_data = ticket_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def delete_ticket(db: Session, ticket_id: str) -> bool:
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return False
    db.delete(db_ticket)
    db.commit()
    return True
