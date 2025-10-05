from typing import List

import crud
from database import get_db
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from models import Ticket, TicketCreate, TicketUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new ticket for the authenticated user.
    Ticket is automatically assigned to the authenticated user.
    """
    return crud.create_ticket(db, ticket, str(current_user.id))


@router.get("/my", response_model=List[Ticket])
def get_my_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all tickets for the authenticated user."""
    all_tickets = crud.get_tickets(db, skip=0, limit=1000)
    user_tickets = [t for t in all_tickets if str(t.user_id) == str(current_user.id)]
    return user_tickets[skip : skip + limit]


@router.get("/my/active", response_model=List[Ticket])
def get_my_active_tickets(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get active (valid) tickets for the authenticated user."""
    from datetime import datetime

    all_tickets = crud.get_tickets(db, skip=0, limit=1000)
    user_tickets = [t for t in all_tickets if str(t.user_id) == str(current_user.id)]

    now = datetime.now()
    active_tickets = [
        t for t in user_tickets if t.valid_from <= now and t.valid_until >= now  # type: ignore
    ]

    return active_tickets


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get a specific ticket by ID.
    User can only view their own tickets.
    """
    db_ticket = crud.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    if str(db_ticket.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tickets",
        )

    return db_ticket


@router.put("/{ticket_id}", response_model=Ticket)
def update_ticket(
    ticket_id: str,
    ticket: TicketUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a ticket.
    User can only update their own tickets.
    """
    db_ticket = crud.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    if str(db_ticket.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tickets",
        )

    db_ticket = crud.update_ticket(db, ticket_id, ticket)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    return db_ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a ticket.
    User can only delete their own tickets.
    """
    db_ticket = crud.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    if str(db_ticket.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tickets",
        )

    success = crud.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
