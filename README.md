# Project Name

This project is a FastAPI-based REST API with PostgreSQL as the database, managed with SQLAlchemy and Alembic for migrations. It includes JWT-based authentication, background tasks with Celery, and Docker support for easy deployment.

## Project Overview

This API provides CRUD operations, authentication, and other API functionalities. It's set up to be scalable with asynchronous task handling and monitoring. You can use this API as a foundation for applications requiring user management and data handling with FastAPI and PostgreSQL.

## Features

- JWT Authentication
- User and candidate management with CRUD operations
- Background task management with Celery
- Migrations with Alembic
- Docker support for easy deployment
- Health checks and CSV report generation

## Technologies Used

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM for database modeling
- **Alembic** - Database migrations
- **JWT** - Authentication
- **Celery** - Background task processing
- **Docker** - Containerization
- **Poetry** - Dependency management
- **Pre-commit Hooks** - Linting and formatting checks
- **Pytest** - Testing

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HiraWaheed/fastapi_postgres_project
   cd task_project
   ```

2. **Install dependencies** using Poetry:
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root of the project with your environment-specific settings, such as database URL, JWT secret, etc.

4. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Start the application:**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

6. **Run Docker** (optional):
   To run the app in Docker, use:
   ```bash
   docker-compose up --build
   ```

## Project Structure

```plaintext
.
├── app
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── database.py          # Database setup and connection
│   ├── models               # SQLAlchemy models
│   ├── schemas              # Pydantic models
│   ├── api               # API routes
│   └── utils
├── alembic                  # Alembic migrations
│   ├── versions             # Migration files
│   └── env.py               # Alembic configuration
├── .env                     # Environment variables
├── docker-compose.yml       # Docker configuration
├── pyproject.toml           # Poetry dependencies
└── README.md                # Project documentation
```

## Endpoints

- **Auth Routes:**
  - `POST /login` - Login with JWT
  - `POST /user` - Register a new user
- `POST /me`  - Return logged in user

- **Candidate Routes:**
  - `GET /candidates/{id}` - Get a candidate
  - `POST /candidates` - Create a candidate
  - `PUT /candidates/{id}` - Update a candidate
  - `DELETE /candidates/{id}` - Delete a candidate
  - `GET /all-candidates/{id}` - List all candidates with pagination

- **Health Check:**
  - `GET /health` - Basic health check endpoint

## Database Migrations

To manage database schema changes:

1. **Generate a new migration:**
   ```bash
   alembic revision --autogenerate -m "Migration message"
   ```

2. **Apply migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Rollback migrations** (optional):
   ```bash
   alembic downgrade -1
   ```

## Running Tests

To run tests with `pytest`:

```bash
pytest
```


