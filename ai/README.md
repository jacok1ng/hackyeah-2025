# Transportation Management API

FastAPI-based REST API for managing transportation routes, journeys, and sensor data.

## Features

- **CRUD operations** for all entities:
  - Stops (bus/tram/train stations)
  - Routes (scheduled transportation routes)
  - Route Stops (stops on routes)
  - Journeys (actual trips)
  - Users (with roles: PASSENGER, DRIVER, DISPATCHER, ADMIN)
  - Journey Data (sensor data from trips)

- **SQLite database** for persistent storage
- **SQLAlchemy ORM** with proper relationships
- **Pydantic validation** for all inputs/outputs
- **Interactive API docs** (Swagger UI)
- **Clean Architecture** with separated layers (models, database, CRUD, routers)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

### From command line:
```bash
python main.py
```

### Using VS Code debugger:
Use the "Main" configuration from launch.json

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

**Note:** On first startup, the API automatically initializes 3 vehicle types (Bus, Tram, Train) in the database. These are system-defined and read-only.

## API Endpoints

All entities follow standard REST patterns:

- `POST /{entity}/` - Create new item
- `GET /{entity}/` - Get all items
- `GET /{entity}/{id}` - Get specific item
- `PUT /{entity}/{id}` - Update item
- `DELETE /{entity}/{id}` - Delete item

### Available endpoints:
- `/vehicle-types` - Vehicle type definitions (bus, tram, train) - **READ ONLY**
- `/stops` - Stop locations (linked to vehicle types)
- `/routes` - Transportation routes (linked to vehicle types)
- `/route-stops` - Stops on specific routes
- `/journeys` - Actual trips/journeys
- `/users` - System users
- `/journey-data` - Sensor data from journeys

## Project Structure

```
ai/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── db_models.py         # SQLAlchemy ORM models
├── models.py            # Pydantic models for validation
├── crud.py              # CRUD operations layer
├── enums.py             # Enum definitions
├── routers/             # API route handlers
│   ├── stops.py
│   ├── routes.py
│   ├── route_stops.py
│   ├── journeys.py
│   ├── users.py
│   └── journey_data.py
├── requirements.txt
├── transportation.db    # SQLite database (auto-created)
└── .gitignore
```

## Example Usage

### Create a stop:
```bash
curl -X POST "http://localhost:8000/stops/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Central Station",
    "type": "TRAIN",
    "latitude": 52.2297,
    "longitude": 21.0122
  }'
```

### Get all stops:
```bash
curl "http://localhost:8000/stops/"
```

## Database Seeding

Populate the database with sample data:

```bash
python seed_database.py
```

This script is fully self-contained and will:
1. Remove old database if it exists
2. Create new database with proper structure
3. Initialize 3 vehicle types (Bus, Tram, Train)
4. Populate with sample data:
   - 10 stops (each assigned to a vehicle type)
   - 6 users (drivers, passengers, dispatcher, admin)
   - 5 routes (linked to vehicle types)
   - 5 journeys (in various states)
   - 20+ sensor readings from active journeys

**Note:** Vehicle types are system-defined and read-only via the API.

## Testing

Test the API with real HTTP requests:

```bash
python test_api.py
```

This will create sample data via API and test all major endpoints.

## Database

The application uses SQLite with the following features:
- Automatic database creation on first run
- Foreign key relationships between entities
- UUID primary keys
- Proper indexes on frequently queried fields
- Soft delete for users (deleted_at timestamp)

Database file: `transportation.db` (auto-created in the `ai/` directory)

