from enum import Enum


class UserRole(str, Enum):
    PASSENGER = "PASSENGER"
    DRIVER = "DRIVER"
    DISPATCHER = "DISPATCHER"
    ADMIN = "ADMIN"


class RouteStatus(str, Enum):
    ON_TIME = "ON_TIME"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class JourneyStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    DELAYED = "DELAYED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
