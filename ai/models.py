from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from enums import JourneyStatus, RouteStatus, UserRole
from pydantic import BaseModel, EmailStr, Field


class VehicleTypeBase(BaseModel):
    name: str
    code: str


class VehicleTypeCreate(VehicleTypeBase):
    pass


class VehicleType(VehicleTypeBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class VehicleBase(BaseModel):
    vehicle_type_id: UUID
    registration_number: str
    capacity: int
    last_inspection_date: Optional[datetime] = None
    issues: Optional[str] = None
    current_driver_id: Optional[UUID] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    vehicle_type_id: Optional[UUID] = None
    registration_number: Optional[str] = None
    capacity: Optional[int] = None
    last_inspection_date: Optional[datetime] = None
    issues: Optional[str] = None
    current_driver_id: Optional[UUID] = None


class Vehicle(VehicleBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StopBase(BaseModel):
    external_id: Optional[str] = None
    name: str
    vehicle_type_id: UUID
    latitude: float
    longitude: float


class StopCreate(StopBase):
    pass


class StopUpdate(BaseModel):
    external_id: Optional[str] = None
    name: Optional[str] = None
    vehicle_type_id: Optional[UUID] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Stop(StopBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class RouteBase(BaseModel):
    vehicle_id: UUID
    starting_stop_id: UUID
    ending_stop_id: UUID
    scheduled_departure: datetime
    scheduled_arrival: datetime
    current_status: RouteStatus


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    vehicle_id: Optional[UUID] = None
    starting_stop_id: Optional[UUID] = None
    ending_stop_id: Optional[UUID] = None
    scheduled_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None
    current_status: Optional[RouteStatus] = None


class Route(RouteBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        from_attributes = True


class RouteStopBase(BaseModel):
    route_id: UUID
    stop_id: UUID
    scheduled_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None


class RouteStopCreate(RouteStopBase):
    pass


class RouteStopUpdate(BaseModel):
    route_id: Optional[UUID] = None
    stop_id: Optional[UUID] = None
    scheduled_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None


class RouteStop(RouteStopBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        from_attributes = True


class JourneyBase(BaseModel):
    route_id: UUID
    driver_id: Optional[UUID] = None
    actual_departure: Optional[datetime] = None
    last_stop_arrival: Optional[datetime] = None
    next_stop_departure: Optional[datetime] = None
    current_status: JourneyStatus = JourneyStatus.PLANNED


class JourneyCreate(JourneyBase):
    pass


class JourneyUpdate(BaseModel):
    route_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    actual_departure: Optional[datetime] = None
    last_stop_arrival: Optional[datetime] = None
    next_stop_departure: Optional[datetime] = None
    current_status: Optional[JourneyStatus] = None


class Journey(JourneyBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    reputation_points: int = 0
    verified: bool = False
    badge: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    reputation_points: Optional[int] = None
    verified: Optional[bool] = None
    badge: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JourneyDataBase(BaseModel):
    journey_id: UUID
    user_id: Optional[UUID] = None
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None
    accuracy: Optional[float] = None
    vertical_accuracy: Optional[float] = None
    satellite_count: Optional[int] = None
    acceleration_x: Optional[float] = None
    acceleration_y: Optional[float] = None
    acceleration_z: Optional[float] = None
    linear_acceleration_x: Optional[float] = None
    linear_acceleration_y: Optional[float] = None
    linear_acceleration_z: Optional[float] = None
    gyroscope_x: Optional[float] = None
    gyroscope_y: Optional[float] = None
    gyroscope_z: Optional[float] = None
    rotation_vector_x: Optional[float] = None
    rotation_vector_y: Optional[float] = None
    rotation_vector_z: Optional[float] = None
    rotation_vector_w: Optional[float] = None
    magnetic_x: Optional[float] = None
    magnetic_y: Optional[float] = None
    magnetic_z: Optional[float] = None
    light: Optional[float] = None
    pressure: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    source: str
    step_count: Optional[int] = None
    heart_rate: Optional[int] = None
    battery_level: Optional[float] = None
    connectivity: Optional[str] = None


class JourneyDataCreate(JourneyDataBase):
    pass


class JourneyDataUpdate(BaseModel):
    journey_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None
    accuracy: Optional[float] = None
    vertical_accuracy: Optional[float] = None
    satellite_count: Optional[int] = None
    acceleration_x: Optional[float] = None
    acceleration_y: Optional[float] = None
    acceleration_z: Optional[float] = None
    linear_acceleration_x: Optional[float] = None
    linear_acceleration_y: Optional[float] = None
    linear_acceleration_z: Optional[float] = None
    gyroscope_x: Optional[float] = None
    gyroscope_y: Optional[float] = None
    gyroscope_z: Optional[float] = None
    rotation_vector_x: Optional[float] = None
    rotation_vector_y: Optional[float] = None
    rotation_vector_z: Optional[float] = None
    rotation_vector_w: Optional[float] = None
    magnetic_x: Optional[float] = None
    magnetic_y: Optional[float] = None
    magnetic_z: Optional[float] = None
    light: Optional[float] = None
    pressure: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    source: Optional[str] = None
    step_count: Optional[int] = None
    heart_rate: Optional[int] = None
    battery_level: Optional[float] = None
    connectivity: Optional[str] = None


class JourneyData(JourneyDataBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        from_attributes = True
