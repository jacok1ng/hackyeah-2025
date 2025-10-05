from typing import List

import crud
from database import get_db
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    FullRouteResponse,
    UserJourney,
    UserJourneyCreate,
    UserJourneyStop,
    UserJourneyStopCreate,
    UserJourneyStopUpdate,
    UserJourneyUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user-journeys", tags=["user-journeys"])


@router.post("/", response_model=UserJourney, status_code=status.HTTP_201_CREATED)
def create_user_journey(
    journey: UserJourneyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new user journey for the authenticated user.
    Journey is automatically assigned to the authenticated user.
    """
    return crud.create_user_journey(db, journey, str(current_user.id))


@router.get("/my", response_model=List[UserJourney])
def get_my_journeys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all journeys for the authenticated user."""
    return crud.get_user_journeys(db, str(current_user.id), skip=skip, limit=limit)


@router.get("/my/saved", response_model=List[UserJourney])
def get_my_saved_journeys(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get saved (not active) journeys for the authenticated user (max 10)."""
    return crud.get_user_saved_journeys(db, str(current_user.id))


@router.get("/my/active", response_model=UserJourney | None)
def get_my_active_journey(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get the active journey for the authenticated user."""
    return crud.get_user_active_journey(db, str(current_user.id))


@router.get("/{journey_id}", response_model=UserJourney)
def get_user_journey(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get a specific user journey by ID.
    User can only view their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own journeys",
        )

    return db_journey


@router.put("/{journey_id}", response_model=UserJourney)
def update_user_journey(
    journey_id: str,
    journey: UserJourneyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a user journey.
    User can only update their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own journeys",
        )

    db_journey = crud.update_user_journey(db, journey_id, journey)
    return db_journey


@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_journey(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a user journey.
    User can only delete their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own journeys",
        )

    success = crud.delete_user_journey(db, journey_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )


# UserJourneyStop endpoints
@router.post(
    "/{journey_id}/stops",
    response_model=UserJourneyStop,
    status_code=status.HTTP_201_CREATED,
)
def create_user_journey_stop(
    journey_id: str,
    stop: UserJourneyStopCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Add a stop to a user journey.
    User can only add stops to their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add stops to your own journeys",
        )

    return crud.create_user_journey_stop(db, journey_id, stop)


@router.get("/{journey_id}/stops", response_model=List[UserJourneyStop])
def get_user_journey_stops(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all stops for a user journey.
    User can only view stops for their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view stops for your own journeys",
        )

    return crud.get_user_journey_stops(db, journey_id)


@router.put("/stops/{stop_id}", response_model=UserJourneyStop)
def update_user_journey_stop(
    stop_id: str,
    stop: UserJourneyStopUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a user journey stop.
    User can only update stops in their own journeys.
    """
    db_stop = crud.get_user_journey_stop(db, stop_id)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey stop not found"
        )

    db_journey = crud.get_user_journey(db, str(db_stop.user_journey_id))
    if db_journey and str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update stops in your own journeys",
        )

    db_stop = crud.update_user_journey_stop(db, stop_id, stop)
    return db_stop


@router.delete("/stops/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_journey_stop(
    stop_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Delete a user journey stop.
    User can only delete stops from their own journeys.
    """
    db_stop = crud.get_user_journey_stop(db, stop_id)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey stop not found"
        )

    db_journey = crud.get_user_journey(db, str(db_stop.user_journey_id))
    if db_journey and str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete stops from your own journeys",
        )

    success = crud.delete_user_journey_stop(db, stop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey stop not found"
        )


@router.delete("/{journey_id}/stops", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_stops_from_journey(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete all stops from a user journey.
    User can only delete stops from their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete stops from your own journeys",
        )

    crud.delete_all_user_journey_stops(db, journey_id)


@router.get("/{journey_id}/full-route", response_model=FullRouteResponse)
def get_user_journey_full_route(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get the complete GPS route for a user journey.
    Returns all route segments and their GPS points in order.
    User can only view routes for their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view routes for your own journeys",
        )

    journey_stops = crud.get_user_journey_stops(db, journey_id)

    if len(journey_stops) < 2:
        return FullRouteResponse(
            total_stops=len(journey_stops),
            total_segments=0,
            total_points=0,
            segments=[],
        )

    segments = []
    total_points = 0

    for i in range(len(journey_stops) - 1):
        from_stop = journey_stops[i]
        to_stop = journey_stops[i + 1]

        segment = crud.get_route_segment_by_stops(
            db, str(from_stop.stop_id), str(to_stop.stop_id)
        )

        if segment:
            points = crud.get_shape_points_by_shape_id(db, str(segment.shape_id))
            total_points += len(points)

            segments.append(
                {
                    "from_stop_id": from_stop.stop_id,
                    "to_stop_id": to_stop.stop_id,
                    "shape_id": segment.shape_id,
                    "point_count": len(points),
                    "points": [
                        {
                            "lat": p.shape_pt_lat,
                            "lon": p.shape_pt_lon,
                            "sequence": p.shape_pt_sequence,
                            "distance": p.shape_dist_traveled,
                        }
                        for p in points
                    ],
                }
            )
        else:
            segments.append(
                {
                    "from_stop_id": from_stop.stop_id,
                    "to_stop_id": to_stop.stop_id,
                    "shape_id": None,
                    "point_count": 0,
                    "points": [],
                    "note": "No route segment defined between these stops",
                }
            )

    return FullRouteResponse(
        total_stops=len(journey_stops),
        total_segments=len(segments),
        total_points=total_points,
        segments=segments,
    )
