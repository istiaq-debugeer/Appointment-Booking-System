# Appointment Booking System

A web-based Appointment Booking System for managing user registrations, appointment scheduling, and reporting. Built with Python and FastAPI, using SQLAlchemy for ORM and Alembic for migrations.

## Features
- User registration and authentication
- Book, view, and manage appointments
- Admin dashboard for managing users and appointments
- Doctor schedule management
- Automated report generation
- Celery integration for background tasks

## Project Structure
```
src/
  api/            # API route handlers
  core/           # Core configuration, database, and middleware
  dependency/     # Dependency injection modules
  models/         # SQLAlchemy models
  repositories/   # Data access layer
  schemas/        # Pydantic schemas
  services/       # Business logic
  tasks/          # Celery tasks
  templates/      # HTML templates
  utils/          # Utility functions
```

## Getting Started

### Prerequisites
- Python 3.12+
- pip
- (Optional) Redis for Celery

### Installation
1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd Appointment-Booking-System
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up the database:
   ```sh
   alembic upgrade head
   ```
4. Start the FastAPI server:
   ```sh
   uvicorn src.main:app --reload
   ```
5. (Optional) Start Celery worker:
   ```sh
   celery -A src.core.celery worker --loglevel=info
   ```

## Usage
- Access the app at `http://localhost:8000`
- Register a new user or log in
- Book and manage appointments
- Admins can access the dashboard for reports and user management

