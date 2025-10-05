from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from enums import (
    JourneyStatus,
    NotificationType,
    ReportCategory,
    RouteStatus,
    TicketType,
    UserRole,
)
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


class VehicleTripBase(BaseModel):
    route_id: UUID
    driver_id: Optional[UUID] = None
    actual_departure: Optional[datetime] = None
    last_stop_arrival: Optional[datetime] = None
    next_stop_departure: Optional[datetime] = None
    current_status: JourneyStatus = JourneyStatus.PLANNED


class VehicleTripCreate(VehicleTripBase):
    pass


class VehicleTripUpdate(BaseModel):
    route_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    actual_departure: Optional[datetime] = None
    last_stop_arrival: Optional[datetime] = None
    next_stop_departure: Optional[datetime] = None
    current_status: Optional[JourneyStatus] = None


class VehicleTrip(VehicleTripBase):
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
    is_disabled: bool = False
    is_super_sporty: bool = False


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
    is_disabled: Optional[bool] = None
    is_super_sporty: Optional[bool] = None


class User(UserBase):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    verified_reports_count: int = 0

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user profile with limited information."""

    id: UUID
    name: str
    badge: Optional[str] = None
    verified_reports_count: int = 0

    class Config:
        from_attributes = True


class JourneyDataBase(BaseModel):
    vehicle_trip_id: UUID
    user_id: Optional[UUID] = None
    user_journey_id: Optional[UUID] = None
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
    vehicle_trip_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    user_journey_id: Optional[UUID] = None
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


class ReportBase(BaseModel):
    vehicle_trip_id: UUID
    vehicle_id: UUID
    user_id: UUID
    category: ReportCategory
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ReportCreate(BaseModel):
    vehicle_trip_id: UUID
    vehicle_id: UUID
    category: ReportCategory
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ReportUpdate(BaseModel):
    category: Optional[ReportCategory] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resolved_at: Optional[datetime] = None


class Report(ReportBase):
    id: UUID = Field(default_factory=uuid4)
    confidence: int
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    user_id: UUID
    ticket_type: TicketType
    valid_from: datetime
    valid_to: datetime
    vehicle_trip_id: Optional[UUID] = None


class TicketCreate(BaseModel):
    """Ticket creation model. user_id will be set automatically from auth."""

    ticket_type: TicketType
    valid_from: datetime
    valid_to: datetime
    vehicle_trip_id: Optional[UUID] = None


class TicketUpdate(BaseModel):
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    vehicle_trip_id: Optional[UUID] = None


class Ticket(TicketBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class UserJourneyBase(BaseModel):
    user_id: UUID
    name: str
    is_saved: bool = False
    is_active: bool = False
    planned_date: Optional[datetime] = None
    notification_time: Optional[datetime] = None
    is_in_progress: bool = False
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    current_stop_index: int = 0


class UserJourneyCreate(BaseModel):
    """UserJourney creation model. user_id will be set automatically from auth."""

    name: str
    is_saved: bool = False
    is_active: bool = False
    planned_date: Optional[datetime] = None


class UserJourneyUpdate(BaseModel):
    name: Optional[str] = None
    is_saved: Optional[bool] = None
    is_active: Optional[bool] = None
    planned_date: Optional[datetime] = None
    notification_time: Optional[datetime] = None
    is_in_progress: Optional[bool] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    current_stop_index: Optional[int] = None


class UserJourney(UserJourneyBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserJourneyStopBase(BaseModel):
    user_journey_id: UUID
    stop_id: UUID
    stop_order: int


class UserJourneyStopCreate(BaseModel):
    stop_id: UUID
    stop_order: int


class UserJourneyStopUpdate(BaseModel):
    stop_id: Optional[UUID] = None
    stop_order: Optional[int] = None


class UserJourneyStop(UserJourneyStopBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class RouteSegmentBase(BaseModel):
    from_stop_id: UUID
    to_stop_id: UUID
    shape_id: str


class RouteSegmentCreate(BaseModel):
    from_stop_id: UUID
    to_stop_id: UUID
    shape_id: str


class RouteSegmentUpdate(BaseModel):
    shape_id: Optional[str] = None


class RouteSegment(RouteSegmentBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ShapePointBase(BaseModel):
    shape_id: str
    shape_pt_lat: float
    shape_pt_lon: float
    shape_pt_sequence: int
    shape_dist_traveled: Optional[float] = None


class ShapePointCreate(BaseModel):
    shape_pt_lat: float
    shape_pt_lon: float
    shape_pt_sequence: int
    shape_dist_traveled: Optional[float] = None


class ShapePointUpdate(BaseModel):
    shape_pt_lat: Optional[float] = None
    shape_pt_lon: Optional[float] = None
    shape_pt_sequence: Optional[int] = None
    shape_dist_traveled: Optional[float] = None


class ShapePoint(ShapePointBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class FullRouteResponse(BaseModel):
    """Full GPS route with all shape points for a journey."""

    total_stops: int
    total_segments: int
    total_points: int
    segments: List[
        dict
    ]  # List of {from_stop, to_stop, shape_id, points: List[ShapePoint]}

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login credentials."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token and user information."""

    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    user: Optional[dict] = None


class RouteProposalRequest(BaseModel):
    """Request for route proposals from Google Maps."""

    start_point: str
    destination: str
    departure_datetime: datetime
    api_key: Optional[str] = None  # Optional - will use env variable if not provided


class StepInfo(BaseModel):
    """Information about a single step in a journey."""

    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    gtfs_route_type: Optional[int] = None
    gtfs_mode: str
    departure_time: Optional[str] = None  # Czas odjazdu (dla transportu publicznego)
    arrival_time: Optional[str] = None  # Czas przyjazdu (dla transportu publicznego)
    duration: Optional[str] = None  # Czas trwania kroku


class RouteProposal(BaseModel):
    """A single route proposal from Google Maps."""

    summary: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration: str
    steps_info: List[StepInfo]


class RouteProposalsResponse(BaseModel):
    """Response containing multiple route proposals."""

    proposals: List[RouteProposal]
    total_proposals: int


class SystemNotification(BaseModel):
    """System notification (not stored in database)."""

    notification_type: NotificationType
    message: str
    related_journey_id: Optional[UUID] = None
    related_report_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.now)


class JourneyProgressResponse(BaseModel):
    """Real-time journey progress information."""

    on_time: bool
    delay_minutes: Optional[float] = None
    distance_to_next_stop_meters: Optional[float] = None
    time_to_next_stop_minutes: Optional[float] = None
    next_stop_name: Optional[str] = None
    distance_to_end_meters: Optional[float] = None
    time_to_end_minutes: Optional[float] = None
    remaining_stops: int
    remaining_stop_names: List[str]
    current_stop_index: int
    total_stops: int
    progress_percentage: float


class StartJourneyResponse(BaseModel):
    """Response when starting a journey."""

    success: bool
    message: str
    journey_id: UUID
    started_at: datetime
    estimated_arrival: Optional[datetime] = None
    total_stops: int
    total_distance_meters: Optional[float] = None
