# FastAPI Development Guidelines

## Project Overview

This is a modern, production-ready FastAPI boilerplate with built-in authentication, user management, and notification features. The project follows best practices for API development and includes essential tools and configurations out of the box.

### Key Features
- **FastAPI** - Modern, fast (high-performance), web framework for building APIs
- **SQLAlchemy 2.0** - Full async SQL toolkit and ORM with aiomysql driver
- **Alembic** - Database migrations
- **JWT Authentication** - Secure token-based authentication with RS256/ES512 algorithms
- **Pydantic v2** - Data validation and settings management
- **Dependency Injection** - Clean architecture with dependency-injector
- **RabbitMQ Integration** - Message queuing with aio-pika for email notifications
- **Async MySQL** - Full async database support
- **Structured Logging** - Production-ready logging with optional Loki integration
- **Email Service** - Built-in SMTP email service with HTML templates
- **CLI Workers** - Background task processing with RabbitMQ workers

## Build/Configuration Instructions

### Dependencies and Environment Setup

This project uses **uv** for dependency management with Python 3.13+.

#### Main Dependencies
- `fastapi>=0.115.14` - Web framework
- `sqlalchemy>=2.0.41` - Async ORM
- `alembic>=1.16.2` - Database migrations
- `aiomysql>=0.2.0` - MySQL async driver
- `pyjwt>=2.10.1` - JWT token handling
- `aio-pika>=9.5.7` - RabbitMQ client
- `dependency-injector>=4.48.1` - DI container
- `argon2-cffi>=25.1.0` - Password hashing
- `python-logging-loki>=0.3.1` - Loki logging integration

#### Development Dependencies
- `ruff>=0.12.1` - Linting and formatting
- `mypy>=1.16.1` - Type checking
- `isort>=6.0.1` - Import sorting
- `pytest` - Testing framework

```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --dev

# Alternative installation methods
uv pip install -e .  # Install in development mode
```

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Environment
ENVIRONMENT=development  # or production

# Database
SQLALCHEMY_DATABASE_URI=mysql+aiomysql://user:password@localhost/database_name

# JWT Configuration
JWT_PUBLIC_KEY=""  # Base64 encoded public key
JWT_PRIVATE_KEY=""  # Base64 encoded private key
JWT_ALGORITHM=ES512  # or RS256
JWT_ACCESS_EXPIRATION_HOURS=8
JWT_REFRESH_EXPIRATION_HOURS=24
JWT_CONFIRM_TOKEN_EXP_HOURS=24

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
APP_PASSWORD=your_app_password
FROM_EMAIL=your_email@example.com
APP_URL=http://localhost:8000

# API Security
X_API_KEY=your-api-key-here

# Logging (Optional)
LOKI_URL=http://localhost:3100
LOKI_ENABLED=false
LOG_REQUEST=false
APP_NAME=FastAPI
SERVICE_NAME=api

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost/
```

### Database Setup

The project uses **Alembic** for database migrations with async SQLAlchemy:

```bash
# Generate new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Downgrade migrations
uv run alembic downgrade -1
```

### Running the Application

```bash
# Development server
uv run python server.py

# Or with uvicorn directly
uv run uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

## Testing Information

### Test Configuration

The project uses **pytest** with the following configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_example.py -v

# Run with coverage (if coverage is added to dev dependencies)
uv run pytest --cov=src tests/
```

### Adding New Tests

1. Create test files in the `tests/` directory with `test_` prefix
2. Import modules using `from src.module import ...`
3. Use `TestClient` from `fastapi.testclient` for API endpoint testing:

```python
import pytest
from fastapi.testclient import TestClient
from src.api import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_endpoint(client):
    response = client.get("/your-endpoint")
    assert response.status_code == 200
```

### Test Example

A working test example is provided in `tests/test_example.py` demonstrating:
- FastAPI application testing
- Middleware configuration verification  
- Basic application properties validation

## Additional Development Information

### Project Architecture

- **Dependency Injection**: Uses `dependency-injector` with container pattern in `src/core/di/container.py`
- **Database**: Async SQLAlchemy with aiomysql driver
- **API Documentation**: FastAPI auto-generated docs at `/docs` and `/redoc`
- **Middleware**: Custom middleware for auth, logging, CORS, and request body saving
- **Background Tasks**: RabbitMQ integration with aio-pika for message queuing
- **CLI Commands**: Custom CLI commands in `src/cmd/` using base CLI pattern

### Code Style Configuration

The project uses **ruff** and **isort** for code formatting:

```bash
# Format code
uv run ruff format

# Check and fix linting issues
uv run ruff check --fix

# Sort imports
uv run isort .
```

Configuration details:
- Line length: 120 characters
- Target Python version: 3.13
- Uses Black-compatible formatting profile
- Import sorting with sections for STDLIB, THIRDPARTY, FIRSTPARTY, LOCALFOLDER

## Additional Development Information

### Project Architecture

- **Dependency Injection**: Uses `dependency-injector` with container pattern in `src/core/di/container.py`
- **Database**: Async SQLAlchemy with aiomysql driver
- **API Documentation**: FastAPI auto-generated docs at `/docs` and `/redoc`
- **Middleware**: Custom middleware for auth, logging, CORS, and request body saving
- **Background Tasks**: RabbitMQ integration with aio-pika for message queuing
- **CLI Commands**: Custom CLI commands in `src/cmd/` using base CLI pattern

### Code Style Configuration

The project uses **ruff** and **isort** for code formatting:

```bash
# Format code
uv run ruff format

# Check and fix linting issues
uv run ruff check --fix

# Sort imports
uv run isort .
```

Configuration details:
- Line length: 120 characters
- Target Python version: 3.13
- Uses Black-compatible formatting profile
- Import sorting with sections for STDLIB, THIRDPARTY, FIRSTPARTY, LOCALFOLDER

### Email Worker

The project includes an email worker system:

```bash
# Run email worker
uv run python src/cmd/email_worker.py
```

### Key Development Notes

1. **Database Models**: All models inherit from `src.core.db.entity.Entity` base class
2. **Error Handling**: Custom exception handling with domain-specific exceptions in `src.core.exception/`
3. **Logging**: Structured logging with Loki integration support
4. **API Response Format**: Uses JSON:API specification for consistent response formatting
5. **Authentication**: JWT-based authentication with RS256/ES512 algorithms and bearer token middleware
6. **Environment-Specific Behavior**: Production mode hides sensitive error details and stack traces

### Important File Locations

- **Main Application**: `src/api.py`
- **Settings**: `src/core/settings/setting.py`
- **DI Container**: `src/core/di/container.py`
- **Database Models**: `src/app/*/model/`
- **Controllers**: `src/app/*/controller/`
- **Services**: `src/app/*/service/`
- **Migrations**: `src/database/migrations/versions/`

### Development Workflow

1. Make code changes
2. Run tests: `uv run pytest`
3. Format code: `uv run ruff format && uv run isort .`
4. Check linting: `uv run ruff check`
5. Generate migrations if models changed: `uv run alembic revision --autogenerate -m "description"`
6. Apply migrations: `uv run alembic upgrade head`