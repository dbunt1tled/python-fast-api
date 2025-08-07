# FastAPI Boilerplate

A modern, production-ready FastAPI boilerplate with built-in authentication, user management, and notification features. This project follows best practices for API development and includes essential tools and configurations out of the box.

## 🚀 Features

- **FastAPI** - Modern, fast (high-performance), web framework for building APIs
- **SQLAlchemy 2.0** - Full async SQL toolkit and ORM
- **Alembic** - Database migrations
- **JWT Authentication** - Secure token-based authentication
- **Pydantic v2** - Data validation and settings management
- **Dependency Injection** - Clean architecture with dependency injection
- **Async MySQL** - Async database support with aiomysql
- **Environment Configuration** - Easy environment variable management
- **CORS** - Built-in CORS middleware
- **Structured Logging** - Ready for production logging
- **Type Hints** - Full Python type support
- **Testing** - Pytest setup included

## 📦 Prerequisites

- Python 3.13+
- MySQL 8.0+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:{your_username}/python-fast-api.git
   cd python-fast-api
   ```

2. Create and activate a virtual environment using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies with uv:
   ```bash
   uv pip install -e .
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

## 🚀 Running the Application

Start the development server:
```bash
uvicorn server:app --reload
```

The API will be available at `http://localhost:8000`

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🏗️ Project Structure

```
src/
├── app/                    # Application components
│   ├── auth/              # Authentication module
│   ├── user/              # User management
│   └── user_notification/ # Notification system
├── core/                  # Core functionality
│   ├── di/               # Dependency injection
│   ├── exception/         # Custom exceptions
│   └── http/             # HTTP-related code
└── database/              # Database configuration
```

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/confirm-email` - Confirm email address
- `POST /auth/resend-confirm-email` - Resend confirmation email

### Users
- `GET /users/me` - Get current user profile
- `PATCH /users/me` - Update current user
- `GET /users` - List users (admin only)
- `GET /users/{user_id}` - Get user by ID

### Notifications
- `GET /notifications` - List user notifications
- `GET /notifications/{id}` - Get notification by ID
- `PATCH /notifications/{id}/read` - Mark notification as read

## 🔒 Environment Variables

Required environment variables are defined in `.env.example`. Copy this to `.env` and update the values:

```
# Database
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=ES256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# App
DEBUG=True
ENVIRONMENT=development
```

## 🧪 Testing

Run tests with pytest:
```bash
pytest
```

## 🛠️ Development

### Code Quality

This project enforces strict code quality standards using:

- **Ruff** - An extremely fast Python linter and code formatter
- **Mypy** - Static type checking
- **Black** - Code formatting (via Ruff)
- **isort** - Import sorting (via Ruff)

#### Running Linters and Type Checking

Run Ruff linter:
```bash
ruff check .
```

Run Ruff formatter:
```bash
ruff format .
```

Run Mypy type checking:
```bash
mypy .
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.