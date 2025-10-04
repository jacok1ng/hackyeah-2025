from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import Ticket, TicketCreate, TicketUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: TicketCreate,
    user_id: str,
    db: Session = Depends(get_db),
):
    """
    Create a new ticket for a user.
    Ticket types:
    - MONTHLY, DAILY, TWO_HOUR, FOUR_HOUR, ONE_HOUR, THIRTY_MIN - time-based tickets for buses and trams
    - TRAIN_ROUTE - route-based ticket for trains (requires from_stop_id and to_stop_id)
    """
    return crud.create_ticket(db, ticket, user_id)


@router.get("/", response_model=List[Ticket])
def get_all_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tickets(db, skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=List[Ticket])
def get_user_tickets(
    user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all tickets for a specific user."""
    return crud.get_user_tickets(db, user_id, skip=skip, limit=limit)


@router.get("/user/{user_id}/active", response_model=List[Ticket])
def get_active_user_tickets(user_id: str, db: Session = Depends(get_db)):
    """Get currently valid tickets for a user."""
    return crud.get_active_user_tickets(db, user_id)


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    db_ticket = crud.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    return db_ticket


@router.put("/{ticket_id}", response_model=Ticket)
def update_ticket(
    ticket_id: str, ticket_update: TicketUpdate, db: Session = Depends(get_db)
):
    db_ticket = crud.update_ticket(db, ticket_id, ticket_update)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    return db_ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    success = crud.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
