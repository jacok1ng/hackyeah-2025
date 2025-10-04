# Import all CRUD functions to maintain backward compatibility
from crud.journey import (
    create_journey,
    delete_journey,
    get_journey,
    get_journeys,
    update_journey,
)
from crud.journey_data import (
    create_journey_data,
    delete_journey_data,
    get_journey_data,
    get_journey_data_list,
    update_journey_data,
)
from crud.route import create_route, delete_route, get_route, get_routes, update_route
from crud.route_stop import (
    create_route_stop,
    delete_route_stop,
    get_route_stop,
    get_route_stops,
    update_route_stop,
)
from crud.stop import create_stop, delete_stop, get_stop, get_stops, update_stop
from crud.user import create_user, delete_user, get_user, get_users, update_user
from crud.vehicle import (
    create_vehicle,
    delete_vehicle,
    get_vehicle,
    get_vehicles,
    update_vehicle,
)
from crud.vehicle_type import create_vehicle_type, get_vehicle_type, get_vehicle_types

__all__ = [
    # Vehicle Type
    "create_vehicle_type",
    "get_vehicle_type",
    "get_vehicle_types",
    # Vehicle
    "create_vehicle",
    "get_vehicle",
    "get_vehicles",
    "update_vehicle",
    "delete_vehicle",
    # Stop
    "create_stop",
    "get_stop",
    "get_stops",
    "update_stop",
    "delete_stop",
    # Route
    "create_route",
    "get_route",
    "get_routes",
    "update_route",
    "delete_route",
    # Route Stop
    "create_route_stop",
    "get_route_stop",
    "get_route_stops",
    "update_route_stop",
    "delete_route_stop",
    # Journey
    "create_journey",
    "get_journey",
    "get_journeys",
    "update_journey",
    "delete_journey",
    # User
    "create_user",
    "get_user",
    "get_users",
    "update_user",
    "delete_user",
    # Journey Data
    "create_journey_data",
    "get_journey_data",
    "get_journey_data_list",
    "update_journey_data",
    "delete_journey_data",
]
