from database import init_db_with_data
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    auth,
    journey_data,
    reports,
    route_segments,
    route_stops,
    routes,
    shape_points,
    stops,
    tickets,
    user_journeys,
    users,
    vehicle_trips,
    vehicle_types,
    vehicles,
)

app = FastAPI(
    title="Transportation Management API",
    description="API for managing transportation routes, journeys, and sensor data",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    """Initialize database and system data on startup."""
    init_db_with_data()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

modules = [
    auth,
    vehicle_types,
    vehicles,
    stops,
    routes,
    route_stops,
    route_segments,
    shape_points,
    vehicle_trips,
    users,
    journey_data,
    reports,
    tickets,
    user_journeys,
]
for module in modules:
    app.include_router(module.router)


@app.get("/")
def root():
    return {
        "message": "Transportation Management API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
