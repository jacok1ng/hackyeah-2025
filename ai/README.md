# Transportation Management API 🚌🚊

Modern FastAPI application for managing public transportation systems including buses, trams, and trains.

## Features 🌟

- **Authentication System** - Simple login with username/password
- **User Journeys** - Plan and track personal travel routes
- **Tickets** - Time-based (monthly, daily, hourly) and route-specific tickets
- **Vehicle Management** - Track buses, trams, and trains with real-time data
- **Route Planning** - GPS-based route segments with shape points
- **Reports** - User-generated incident reports
- **Real-time Data** - Sensor readings and vehicle tracking

## Authentication 🔐

The API uses JWT (JSON Web Token) authentication.

### Login

```bash
POST /auth/login
{
  "username": "user",
  "password": "user"
}
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "username": "user",
    "email": "user@example.com",
    "role": "PASSENGER",
    ...
  }
}
```

### Test Accounts

- `user:user` - PASSENGER role
- `user2:user2` - PASSENGER role
- `user3:user3` - PASSENGER role
- `driv:driv` - DRIVER role
- `disp:disp` - DISPATCHER role
- `admin:admin` - ADMIN role

### Using Authentication

After login, include the JWT token in all requests:

```bash
Authorization: Bearer <access_token>
```

**For Testing:** Tokens are configured to never expire.

#### Pre-generated Test Tokens

For convenience, you can use these pre-generated tokens without logging in:

```python
# In test_login.py
TEST_TOKENS = {
    "user": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user2": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    # ... etc
}
```

Just use: `Authorization: Bearer <token>` in your requests.

## API Endpoints 📡

### Public Endpoints (No Authentication)

- `POST /auth/login` - Login with username/password
- `GET /vehicle-types` - List all vehicle types
- `GET /stops` - List all stops
- `GET /routes` - List all routes
- `GET /route-segments` - View route segments (read-only)
- `GET /shape-points` - View GPS points (read-only)

### Protected Endpoints (Authentication Required)

#### User Journeys (Only Own Data)

- `POST /user-journeys` - Create journey
- `GET /user-journeys/my` - Get all my journeys
- `GET /user-journeys/my/saved` - Get saved journeys (max 10)
- `GET /user-journeys/my/active` - Get active journey
- `GET /user-journeys/{id}` - Get journey details
- `PUT /user-journeys/{id}` - Update journey
- `DELETE /user-journeys/{id}` - Delete journey
- `GET /user-journeys/{id}/full-route` - Get complete GPS route

#### Tickets (Only Own Data)

- `POST /tickets` - Create ticket
- `GET /tickets/my` - Get all my tickets
- `GET /tickets/my/active` - Get active tickets
- `GET /tickets/{id}` - Get ticket details
- `PUT /tickets/{id}` - Update ticket
- `DELETE /tickets/{id}` - Delete ticket

#### Reports

- `POST /reports` - Create incident report
- `GET /reports` - List reports
- `GET /reports/{id}` - Get report details

## Technology Stack 💻

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Project Structure 📁

```text
ai/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration
├── db_models.py         # SQLAlchemy models
├── models.py            # Pydantic schemas
├── enums.py             # Enum definitions
├── auth.py              # Authentication utilities
├── dependencies.py      # FastAPI dependencies
├── init_data.py         # System data initialization
├── seed_database.py     # Database seeding script
├── crud/                # CRUD operations (per entity)
│   ├── __init__.py
│   ├── user.py
│   ├── vehicle.py
│   ├── route.py
│   ├── ticket.py
│   ├── user_journey.py
│   └── ...
└── routers/             # API endpoints (per entity)
    ├── auth.py
    ├── users.py
    ├── vehicles.py
    ├── tickets.py
    ├── user_journeys.py
    └── ...
```

## Setup & Installation 🚀

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed Database

```bash
python seed_database.py
```

This will:

- Remove old database (if exists)
- Create new database with schema
- Populate with sample data:
  - 3 vehicle types (BUS, TRAM, TRAIN)
  - 10 stops
  - 6 users (3 passengers, 1 driver, 1 dispatcher, 1 admin)
  - 8 vehicles
  - 5 routes with stops
  - Route segments with GPS points
  - Sample tickets and journeys

### 3. Run API

```bash
python main.py
```

or with uvicorn:

```bash
uvicorn main:app --reload
```

### 4. Access Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Usage Examples 📝

### 1. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user"}'
```

Response includes JWT token:

```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "username": "user",
    "email": "user@example.com",
    "role": "PASSENGER"
  }
}
```

### 2. Get My Journeys

**Option A: Using token from login:**
```bash
curl -X GET "http://localhost:8000/user-journeys/my" \
  -H "Authorization: Bearer <access_token>"
```

**Option B: Using pre-generated test token:**
```bash
# For user "user"
curl -X GET "http://localhost:8000/user-journeys/my" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLXRlc3QtaWQtMSIsInVzZXJfaWQiOiJ1c2VyLXRlc3QtaWQtMSIsInVzZXJuYW1lIjoidXNlciIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsInJvbGUiOiJQQVNTRU5HRVIifQ.m82ObpD1kQlgu_gvBy9iXv-XhULNPyVEibTaiUs19O8"
```

Note: See all tokens in `test_login.py` file.

### 3. Create a Ticket

```bash
curl -X POST "http://localhost:8000/tickets" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "ticket_type": "MONTHLY",
    "valid_from": "2025-10-01T00:00:00",
    "valid_until": "2025-10-31T23:59:59"
  }'
```

Note: `user_id` is automatically set from the JWT token.

### 4. Get Full GPS Route for Journey

```bash
curl -X GET "http://localhost:8000/user-journeys/{journey_id}/full-route" \
  -H "Authorization: Bearer <access_token>"
```

## Key Concepts 🔑

### Vehicle Types

- **BUS** - City buses
- **TRAM** - Trams and light rail
- **TRAIN** - Regional and intercity trains

### Ticket Types

#### Time-Based (Universal for buses/trams)

- `MONTHLY` - 30 days
- `DAILY` - 24 hours
- `FOUR_HOUR` - 4 hours
- `TWO_HOUR` - 2 hours
- `ONE_HOUR` - 1 hour
- `THIRTY_MIN` - 30 minutes

#### Route-Based (For trains)

- `TRAIN_ROUTE` - Specific route with stops

### User Roles

- **PASSENGER** - Regular users, can create reports, journeys, tickets
- **DRIVER** - Vehicle operators
- **DISPATCHER** - Route managers
- **ADMIN** - Full system access

### Route Tracking Hierarchy

1. **ShapePoint** - Individual GPS coordinate
2. **RouteSegment** - Connection between two stops with GPS points
3. **RouteStop** - Stop within a route
4. **VehicleTrip** - Vehicle executing a route
5. **UserJourney** - User's planned travel

## Security 🔒

- JWT-based authentication (tokens never expire for testing)
- All user journey and ticket endpoints require authentication
- Users can only view/modify their own data
- Tokens are cryptographically signed and cannot be forged
- Passwords stored as plain text (for simplicity - change in production!)
- Pre-generated test tokens available in `test_login.py`
- Role-based access control (future enhancement)

## Database Schema 🗄️

### Core Tables

- `users` - User accounts
- `vehicle_types` - Vehicle categories (read-only)
- `vehicles` - Individual vehicles
- `stops` - Transit stops
- `routes` - Service routes
- `route_stops` - Stops in a route
- `route_segments` - GPS segment definitions
- `shape_points` - GPS coordinates
- `vehicle_trips` - Active vehicle trips
- `user_journeys` - User's travel plans
- `user_journey_stops` - Stops in user journey
- `tickets` - User tickets
- `reports` - Incident reports
- `journey_data` - Sensor readings

## Development 🛠️

### Testing Login

```bash
python test_login.py
```

### VSCode Debug Configuration

The project includes `.vscode/launch.json` for debugging:

- **Main** - Run `ai/main.py` with debugger

### Code Style

- Clean Architecture principles
- Modular CRUD operations
- Separation of concerns
- Type hints throughout
- English code, Polish comments (in chat)

## Future Enhancements 🚧

- Password hashing (bcrypt/argon2)
- Token refresh mechanism
- Real-time vehicle tracking
- Route optimization
- Predictive delays
- Mobile app integration
- Payment processing
- Multi-language support

## License 📄

MIT License

## Support 💬

For issues or questions, please contact the development team.