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


class Stop(Base):
    __tablename__ = "stops"

    id = Column(String, primary_key=True, default=generate_uuid)
    external_id = Column(String, nullable=True)
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
    journeys = relationship("Journey", back_populates="route")


class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(String, primary_key=True, default=generate_uuid)
    route_id = Column(String, ForeignKey("routes.id"), nullable=False)
    stop_id = Column(String, ForeignKey("stops.id"), nullable=False)
    scheduled_departure = Column(DateTime, nullable=True)
    scheduled_arrival = Column(DateTime, nullable=True)

    route = relationship("Route", back_populates="route_stops")
    stop = relationship("Stop", back_populates="route_stops")


class Journey(Base):
    __tablename__ = "journeys"

    id = Column(String, primary_key=True, default=generate_uuid)
    route_id = Column(String, ForeignKey("routes.id"), nullable=False)
    driver_id = Column(String, ForeignKey("users.id"), nullable=True)
    actual_departure = Column(DateTime, nullable=True)
    last_stop_arrival = Column(DateTime, nullable=True)
    next_stop_departure = Column(DateTime, nullable=True)
    current_status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    route = relationship("Route", back_populates="journeys")
    driver = relationship("User", back_populates="journeys")
    journey_data = relationship("JourneyData", back_populates="journey")


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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    journeys = relationship("Journey", back_populates="driver")
    journey_data = relationship("JourneyData", back_populates="user")
    assigned_vehicles = relationship("Vehicle", back_populates="current_driver")


class JourneyData(Base):
    __tablename__ = "journey_data"

    id = Column(String, primary_key=True, default=generate_uuid)
    journey_id = Column(String, ForeignKey("journeys.id"), nullable=False)
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

    journey = relationship("Journey", back_populates="journey_data")
    user = relationship("User", back_populates="journey_data")
