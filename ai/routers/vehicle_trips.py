from typing import List

import crud
from database import get_db
from dependencies import require_admin, require_driver_or_dispatcher
from fastapi import APIRouter, Depends, HTTPException, status
from models import FullRouteResponse, VehicleTrip, VehicleTripCreate, VehicleTripUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vehicle-trips", tags=["vehicle-trips"])


@router.post("/", response_model=VehicleTrip, status_code=status.HTTP_201_CREATED)
def create_vehicle_trip(
    vehicle_trip: VehicleTripCreate,
    db: Session = Depends(get_db),
    _=Depends(require_driver_or_dispatcher),
):
    """Create a new vehicle trip (execution of a route by a specific vehicle). Requires DRIVER or DISPATCHER role."""
    return crud.create_vehicle_trip(db, vehicle_trip)


@router.get("/", response_model=List[VehicleTrip])
def get_all_vehicle_trips(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_vehicle_trips(db, skip=skip, limit=limit)


@router.get("/{vehicle_trip_id}", response_model=VehicleTrip)
def get_vehicle_trip(vehicle_trip_id: str, db: Session = Depends(get_db)):
    db_vehicle_trip = crud.get_vehicle_trip(db, vehicle_trip_id)
    if not db_vehicle_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle trip not found"
        )
    return db_vehicle_trip


@router.put("/{vehicle_trip_id}", response_model=VehicleTrip)
def update_vehicle_trip(
    vehicle_trip_id: str,
    vehicle_trip_update: VehicleTripUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_driver_or_dispatcher),
):
    """
    Update a vehicle trip. Requires DRIVER or DISPATCHER role.
    Note: In production, DRIVER should only update their assigned trips.
    """
    db_vehicle_trip = crud.update_vehicle_trip(db, vehicle_trip_id, vehicle_trip_update)
    if not db_vehicle_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle trip not found"
        )
    return db_vehicle_trip


@router.delete("/{vehicle_trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_trip(
    vehicle_trip_id: str, db: Session = Depends(get_db), _=Depends(require_admin)
):
    """Delete a vehicle trip. Requires ADMIN role."""
    success = crud.delete_vehicle_trip(db, vehicle_trip_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle trip not found"
        )


@router.get("/{vehicle_trip_id}/full-route", response_model=FullRouteResponse)
def get_vehicle_trip_full_route(vehicle_trip_id: str, db: Session = Depends(get_db)):
    """
    Get the complete GPS route for a vehicle trip.
    Returns all route segments and their GPS points in order.
    """
    # Get vehicle trip
    db_vehicle_trip = crud.get_vehicle_trip(db, vehicle_trip_id)
    if not db_vehicle_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle trip not found"
        )

    # Get route stops for this trip
    route_stops = crud.get_route_stops(db)
    route_stops = [
        rs for rs in route_stops if str(rs.route_id) == str(db_vehicle_trip.route_id)
    ]

    # Sort by scheduled time (arrival or departure)
    def get_sort_key(rs):
        arrival = getattr(rs, "scheduled_arrival", None)
        departure = getattr(rs, "scheduled_departure", None)
        return arrival if arrival else (departure if departure else "")

    route_stops = sorted(route_stops, key=get_sort_key)

    if not route_stops:
        return FullRouteResponse(
            total_stops=0, total_segments=0, total_points=0, segments=[]
        )

    # Build segments between consecutive stops
    segments = []
    total_points = 0

    for i in range(len(route_stops) - 1):
        from_stop = route_stops[i]
        to_stop = route_stops[i + 1]

        # Find route segment between these stops
        segment = crud.get_route_segment_by_stops(
            db, str(from_stop.stop_id), str(to_stop.stop_id)
        )

        if segment:
            # Get all GPS points for this segment
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

    return FullRouteResponse(
        total_stops=len(route_stops),
        total_segments=len(segments),
        total_points=total_points,
        segments=segments,
    )
