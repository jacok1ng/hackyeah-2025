from datetime import datetime
from uuid import uuid4

from database import Base
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


def generate_uuid():
    return str(uuid4())


class VehicleType(Base):
    __tablename__ = "vehicle_types"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    stops = relationship("Stop", back_populates="vehicle_type")
    vehicles = relationship("Vehicle", back_populates="vehicle_type")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, default=generate_uuid)
    vehicle_type_id = Column(String, ForeignKey("vehicle_types.id"), nullable=False)
    registration_number = Column(String, unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    last_inspection_date = Column(DateTime, nullable=True)
    issues = Column(String, nullable=True)
    current_driver_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)

    vehicle_type = relationship("VehicleType", back_populates="vehicles")
    current_driver = relationship("User", back_populates="assigned_vehicles")
    routes = relationship("Route", back_populates="vehicle")
    reports = relationship("Report", back_populates="vehicle")


class Stop(Base):
    __tablename__ = "stops"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    vehicle_type_id = Column(String, ForeignKey("vehicle_types.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    vehicle_type = relationship("VehicleType", back_populates="stops")
    route_stops = relationship("RouteStop", back_populates="stop")
    starting_routes = relationship(
        "Route", foreign_keys="Route.starting_stop_id", back_populates="starting_stop"
    )
    ending_routes = relationship(
        "Route", foreign_keys="Route.ending_stop_id", back_populates="ending_stop"
    )


class Route(Base):
    __tablename__ = "routes"

    id = Column(String, primary_key=True, default=generate_uuid)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    starting_stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    ending_stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    scheduled_departure = Column(DateTime, nullable=False)
    scheduled_arrival = Column(DateTime, nullable=False)
    current_status = Column(String, nullable=False)

    vehicle = relationship("Vehicle", back_populates="routes")
    starting_stop = relationship(
        "Stop", foreign_keys=[starting_stop_id], back_populates="starting_routes"
    )
    ending_stop = relationship(
        "Stop", foreign_keys=[ending_stop_id], back_populates="ending_routes"
    )
    route_stops = relationship("RouteStop", back_populates="route")
    vehicle_trips = relationship("VehicleTrip", back_populates="route")


class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(String, primary_key=True, default=generate_uuid)
    route_id = Column(String, ForeignKey("routes.id"), nullable=False)
    stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    scheduled_departure = Column(DateTime, nullable=True)
    scheduled_arrival = Column(DateTime, nullable=True)
    stop_sequence = Column(Integer, nullable=False)

    route = relationship("Route", back_populates="route_stops")
    stop = relationship("Stop", back_populates="route_stops")


class VehicleTrip(Base):
    __tablename__ = "vehicle_trips"

    id = Column(String, primary_key=True, default=generate_uuid)
    route_id = Column(String, ForeignKey("routes.id"), nullable=False)
    driver_id = Column(String, ForeignKey("users.id"), nullable=True)
    actual_departure = Column(DateTime, nullable=True)
    last_stop_arrival = Column(DateTime, nullable=True)
    next_stop_departure = Column(DateTime, nullable=True)
    current_status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    route = relationship("Route", back_populates="vehicle_trips")
    driver = relationship("User", back_populates="vehicle_trips")
    journey_data = relationship("JourneyData", back_populates="vehicle_trip")
    reports = relationship("Report", back_populates="vehicle_trip")
    tickets = relationship("Ticket", back_populates="vehicle_trip")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    reputation_points = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    badge = Column(String, nullable=True)
    verified_reports_count = Column(Integer, default=0)
    is_disabled = Column(Boolean, default=False)
    is_super_sporty = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    vehicle_trips = relationship("VehicleTrip", back_populates="driver")
    journey_data = relationship("JourneyData", back_populates="user")
    assigned_vehicles = relationship("Vehicle", back_populates="current_driver")
    reports = relationship("Report", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")
    user_journeys = relationship("UserJourney", back_populates="user")


class JourneyData(Base):
    __tablename__ = "journey_data"

    id = Column(String, primary_key=True, default=generate_uuid)
    vehicle_trip_id = Column(String, ForeignKey("vehicle_trips.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    bearing = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    vertical_accuracy = Column(Float, nullable=True)
    satellite_count = Column(Integer, nullable=True)

    acceleration_x = Column(Float, nullable=True)
    acceleration_y = Column(Float, nullable=True)
    acceleration_z = Column(Float, nullable=True)
    linear_acceleration_x = Column(Float, nullable=True)
    linear_acceleration_y = Column(Float, nullable=True)
    linear_acceleration_z = Column(Float, nullable=True)

    gyroscope_x = Column(Float, nullable=True)
    gyroscope_y = Column(Float, nullable=True)
    gyroscope_z = Column(Float, nullable=True)
    rotation_vector_x = Column(Float, nullable=True)
    rotation_vector_y = Column(Float, nullable=True)
    rotation_vector_z = Column(Float, nullable=True)
    rotation_vector_w = Column(Float, nullable=True)

    magnetic_x = Column(Float, nullable=True)
    magnetic_y = Column(Float, nullable=True)
    magnetic_z = Column(Float, nullable=True)

    light = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)

    source = Column(String, nullable=False)
    step_count = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    battery_level = Column(Float, nullable=True)
    connectivity = Column(String, nullable=True)

    vehicle_trip = relationship("VehicleTrip", back_populates="journey_data")
    user = relationship("User", back_populates="journey_data")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    vehicle_trip_id = Column(String, ForeignKey("vehicle_trips.id"), nullable=False)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    confidence = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime, nullable=True)

    vehicle_trip = relationship("VehicleTrip", back_populates="reports")
    vehicle = relationship("Vehicle", back_populates="reports")
    user = relationship("User", back_populates="reports")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    ticket_type = Column(String, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    vehicle_trip_id = Column(String, ForeignKey("vehicle_trips.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="tickets")
    vehicle_trip = relationship("VehicleTrip", back_populates="tickets")


class UserJourney(Base):
    __tablename__ = "user_journeys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    is_saved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    planned_date = Column(DateTime, nullable=True)
    notification_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="user_journeys")
    stops = relationship("UserJourneyStop", back_populates="user_journey")


class UserJourneyStop(Base):
    __tablename__ = "user_journey_stops"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_journey_id = Column(String, ForeignKey("user_journeys.id"), nullable=False)
    stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user_journey = relationship("UserJourney", back_populates="stops")
    stop = relationship("Stop")


class RouteSegment(Base):
    __tablename__ = "route_segments"

    id = Column(String, primary_key=True, default=generate_uuid)
    from_stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    to_stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    shape_id = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)

    from_stop = relationship("Stop", foreign_keys=[from_stop_id])
    to_stop = relationship("Stop", foreign_keys=[to_stop_id])
    shape_points = relationship("ShapePoint", back_populates="route_segment")


class ShapePoint(Base):
    __tablename__ = "shape_points"

    id = Column(String, primary_key=True, default=generate_uuid)
    shape_id = Column(
        String, ForeignKey("route_segments.shape_id"), nullable=False, index=True
    )
    shape_pt_lat = Column(Float, nullable=False)
    shape_pt_lon = Column(Float, nullable=False)
    shape_pt_sequence = Column(Integer, nullable=False)
    shape_dist_traveled = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    route_segment = relationship("RouteSegment", back_populates="shape_points")
