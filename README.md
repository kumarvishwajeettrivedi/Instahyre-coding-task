# Place Review API

A Django-based REST API that allows users to review places (shops, restaurants, etc.). This project uses PostgreSQL for data persistence and Django REST Framework for the API layer.

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- PostgreSQL
- pip

### 2. Database Setup
First, create the database and user in PostgreSQL:

```sql
CREATE DATABASE place_review_db;
CREATE USER place_user WITH PASSWORD 'password';
ALTER ROLE place_user SET client_encoding TO 'utf8';
ALTER ROLE place_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE place_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE place_review_db TO place_user;
GRANT ALL ON SCHEMA public TO place_user;
```

### 3. Installation & Running
Clone the project and run the following commands:

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Populate database with sample data
python manage.py populate_db

# Start the server
python manage.py runserver
```

The API will be running at `http://127.0.0.1:8000/`.

## Design Decisions & Assumptions

- **Database**: I chose PostgreSQL over SQLite as specifically requested for better production compatibility.
- **Search Logic**: The requirements mentioned a "category" filter, but since places don't have a category field, I've interpreted this as the "minimum rating" filter mentioned in the adjacent requirement.
- **Authentication**: Usage of built-in Token Authentication for simplicity and valid stateless behavior.
- **Project Structure**: I've kept the structure standard: `api` app for all endpoints and logic, with the main settings in `place_review_project`.

## API Overview

**Auth**
- `POST /api/register/`
- `POST /api/login/`

**Places & Reviews**
- `POST /api/reviews/` (Add a review; creates place if it doesn't exist)
- `GET /api/places/search/` (Supports `query` for name match and `min_rating`)
- `GET /api/places/<id>/` (Details with reviews sorted by current user first)

