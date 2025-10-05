# Import all CRUD functions to maintain backward compatibility
from crud.delay_detection import (
    detect_delay_from_historical_data,
    detect_delay_from_verified_report,
    handle_delay_detection,
    send_alternative_route_to_users,
    send_delay_notification_to_families,
)
from crud.delay_prediction import (
    calculate_current_delay,
    get_delay_statistics,
    get_historical_delays,
    get_incident_impact,
    predict_delay,
    predict_delays_for_route,
)
from crud.feedback import create_feedback, get_all_feedbacks
from crud.journey_data import (
    create_journey_data,
    get_journey_data,
    get_journey_data_list,
    update_journey_data,
)
from crud.report import (
    create_report,
    delete_report,
    get_report,
    get_reports,
    get_reports_by_category,
    get_reports_by_journey,
    get_reports_by_vehicle,
    get_reports_by_vehicle_trip,
    resolve_report,
    update_report,
)
from crud.report_verification import (
    check_verification_requirements,
    create_report_verification,
    get_report_verifications,
    get_user_verification,
    get_users_on_vehicle_trip,
    verify_report_if_requirements_met,
)
from crud.route import create_route, delete_route, get_route, get_routes, update_route
from crud.route_segment import (
    create_route_segment,
    delete_route_segment,
    get_route_segment,
    get_route_segment_by_shape_id,
    get_route_segment_by_stops,
    get_route_segments,
    update_route_segment,
)
from crud.route_stop import (
    create_route_stop,
    delete_route_stop,
    get_route_stop,
    get_route_stops,
    update_route_stop,
)
from crud.shape_point import (
    create_shape_point,
    create_shape_points_batch,
    delete_all_shape_points,
    delete_shape_point,
    get_shape_point,
    get_shape_points,
    get_shape_points_by_shape_id,
    update_shape_point,
)
from crud.stop import create_stop, delete_stop, get_stop, get_stops, update_stop
from crud.ticket import (
    create_ticket,
    delete_ticket,
    get_active_user_tickets,
    get_ticket,
    get_tickets,
    get_user_tickets,
    update_ticket,
)
from crud.user import create_user, delete_user, get_user, get_users, update_user
from crud.user_journey import (
    create_user_journey,
    delete_user_journey,
    get_user_active_journey,
    get_user_journey,
    get_user_journeys,
    get_user_saved_journeys,
    update_user_journey,
)
from crud.user_journey_stop import (
    create_user_journey_stop,
    delete_all_user_journey_stops,
    delete_user_journey_stop,
    get_user_journey_stop,
    get_user_journey_stops,
    update_user_journey_stop,
)
from crud.vehicle import (
    create_vehicle,
    delete_vehicle,
    get_vehicle,
    get_vehicles,
    update_vehicle,
)
from crud.vehicle_trip import (
    create_vehicle_trip,
    delete_vehicle_trip,
    get_vehicle_trip,
    get_vehicle_trips,
    update_vehicle_trip,
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
    # VehicleTrip
    "create_vehicle_trip",
    "get_vehicle_trip",
    "get_vehicle_trips",
    "update_vehicle_trip",
    "delete_vehicle_trip",
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
    # Feedback
    "create_feedback",
    "get_all_feedbacks",
    # Delay Detection
    "detect_delay_from_historical_data",
    "detect_delay_from_verified_report",
    "send_alternative_route_to_users",
    "send_delay_notification_to_families",
    "handle_delay_detection",
    # Delay Prediction
    "predict_delay",
    "predict_delays_for_route",
    "calculate_current_delay",
    "get_historical_delays",
    "get_incident_impact",
    "get_delay_statistics",
    # Report
    "create_report",
    "get_report",
    "get_reports",
    "get_reports_by_journey",
    "get_reports_by_vehicle_trip",
    "get_reports_by_vehicle",
    "get_reports_by_category",
    "update_report",
    "resolve_report",
    "delete_report",
    # Report Verification
    "create_report_verification",
    "get_report_verifications",
    "get_user_verification",
    "check_verification_requirements",
    "verify_report_if_requirements_met",
    "get_users_on_vehicle_trip",
    # Ticket
    "create_ticket",
    "get_ticket",
    "get_tickets",
    "get_user_tickets",
    "get_active_user_tickets",
    "update_ticket",
    "delete_ticket",
    # User Journey
    "create_user_journey",
    "get_user_journey",
    "get_user_journeys",
    "get_user_saved_journeys",
    "get_user_active_journey",
    "update_user_journey",
    "delete_user_journey",
    # User Journey Stop
    "create_user_journey_stop",
    "get_user_journey_stop",
    "get_user_journey_stops",
    "update_user_journey_stop",
    "delete_user_journey_stop",
    "delete_all_user_journey_stops",
    # Route Segment
    "create_route_segment",
    "get_route_segment",
    "get_route_segment_by_shape_id",
    "get_route_segment_by_stops",
    "get_route_segments",
    "update_route_segment",
    "delete_route_segment",
    # Shape Point
    "create_shape_point",
    "create_shape_points_batch",
    "get_shape_point",
    "get_shape_points",
    "get_shape_points_by_shape_id",
    "update_shape_point",
    "delete_shape_point",
    "delete_all_shape_points",
]
