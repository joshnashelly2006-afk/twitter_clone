# Twitter Clone Backend (Enterprise Flask REST API v1)

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, enterprise-grade Flask REST API for a Twitter/X clone backend built with Python 3.13, Flask Application Factory, PostgreSQL, SQLAlchemy ORM, Flask-JWT-Extended, Flask-Bcrypt, Flask-Limiter rate limiting, rotating file logging, security headers, and Swagger UI documentation (Flasgger).

---

## Architecture Diagram

```mermaid
graph TD
    Client[Mobile / Web Clients] -->|HTTPS Requests| Nginx[Nginx Reverse Proxy]
    Nginx -->|Static Media /uploads/| FileSystem[(Media File Storage)]
    Nginx -->|Proxy Pass :5000| Gunicorn[Gunicorn WSGI Server]
    Gunicorn -->|Application Factory| FlaskApp[Flask REST API App]
    FlaskApp -->|Rate Limiter| Limiter[Flask-Limiter]
    FlaskApp -->|JWT Auth & Security| JWT[Flask-JWT-Extended]
    FlaskApp -->|ORM Queries| SQLAlchemy[SQLAlchemy ORM]
    SQLAlchemy -->|Database Connection| Postgres[(PostgreSQL DB)]
```

---

## Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ POSTS : creates
    USERS ||--o{ COMMENTS : writes
    USERS ||--o{ LIKES : gives
    USERS ||--o{ FOLLOWS : follows
    POSTS ||--o{ COMMENTS : contains
    POSTS ||--o{ LIKES : receives

    USERS {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        text bio
        string profile_picture
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    POSTS {
        uuid id PK
        uuid user_id FK
        text content
        string media_path
        string media_type
        timestamp created_at
        timestamp updated_at
    }

    COMMENTS {
        uuid id PK
        uuid user_id FK
        uuid post_id FK
        text comment
        timestamp created_at
        timestamp updated_at
    }

    LIKES {
        uuid id PK
        uuid user_id FK
        uuid post_id FK
        timestamp created_at
        timestamp updated_at
    }

    FOLLOWS {
        uuid id PK
        uuid follower_id FK
        uuid following_id FK
        timestamp created_at
        timestamp updated_at
    }
```

---

## Table of Contents

- [Architectural Highlights](#architectural-highlights)
- [Global Response & Error Format](#global-response--error-format)
- [API v1 Endpoints & Rate Limits](#api-v1-endpoints--rate-limits)
- [Local Installation & Setup](#local-installation--setup)
- [Docker Setup (Development & Production)](#docker-setup-development--production)
- [Environment Variables](#environment-variables)
- [PostgreSQL Database Migrations](#postgresql-database-migrations)
- [Running Pytest Test Suite](#running-pytest-test-suite)
- [Health Monitoring & Logging](#health-monitoring--logging)
- [Cloud Deployment (Render, Railway, AWS EC2)](#cloud-deployment-render-railway-aws-ec2)
- [Project Directory Structure](#project-directory-structure)

---

## Architectural Highlights

- **Application Factory Pattern**: Clean modular initialization (`create_app`) avoiding circular imports.
- **API Versioning**: Standardized RESTful routes under `/api/v1/`.
- **Global Response Serialization**: Uniform JSON schema for all successful and error HTTP responses.
- **Rate Limiting (Flask-Limiter)**: Endpoints protected against brute-force and spam attacks.
- **Rotating Application Logger**: Thread-safe logging to `logs/application.log` with file rotation.
- **N+1 Query Optimization**: Batch database fetching for feed posts, engagement counts, and user likes status.
- **Security Middleware**: Automatic injection of `X-Request-ID`, execution timers, and security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block`).

---

## Global Response & Error Format

### Success Response (HTTP 200 / 201)
```json
{
  "success": true,
  "message": "Resource created successfully.",
  "data": { ... }
}
```

### Error Response (HTTP 4xx / 5xx)
```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": {
    "password": "Password must be at least 8 characters long."
  }
}
```

---

## API v1 Endpoints & Rate Limits

| Method | Endpoint | Protection | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Public | Default | Health monitoring endpoint |
| `POST` | `/api/v1/auth/register` | Public | 3 / min | Register new user account |
| `POST` | `/api/v1/auth/login` | Public | 5 / min | Authenticate credentials & receive JWT |
| `GET` | `/api/v1/auth/me` | JWT | Default | Get current user auth status |
| `POST` | `/api/v1/auth/logout` | JWT | Default | Revoke JWT token |
| `POST` | `/api/v1/auth/refresh` | JWT (Refresh) | Default | Issue new access token |
| `GET` | `/api/v1/users/me` | JWT | Default | Get private user profile |
| `PUT` | `/api/v1/users/me` | JWT | Default | Update username, email, bio |
| `GET` | `/api/v1/users/<id>` | Public | Default | Get public user profile & stats |
| `GET` | `/api/v1/users/search?q=` | Public | Default | Search users by username |
| `POST` | `/api/v1/users/me/profile-picture` | JWT | 10 / min | Upload 5 MB profile image |
| `DELETE` | `/api/v1/users/me/profile-picture` | JWT | Default | Delete profile image |
| `POST` | `/api/v1/posts` | JWT | 20 / min | Create post with 50 MB image/video |
| `GET` | `/api/v1/posts/<id>` | Public / JWT | Default | Get post details |
| `GET` | `/api/v1/posts/me` | JWT | Default | Get logged-in user posts |
| `GET` | `/api/v1/posts/user/<id>` | Public | Default | Get public posts of user |
| `PUT` | `/api/v1/posts/<id>` | JWT | Default | Edit post content / replace media |
| `DELETE` | `/api/v1/posts/<id>` | JWT | Default | Delete post & media file |
| `GET` | `/api/v1/feed` | JWT | Default | Personalized feed from followed users |
| `GET` | `/api/v1/explore` | Public / JWT | Default | Global explore feed of latest posts |
| `POST` | `/api/v1/posts/<id>/like` | JWT | Default | Like a post |
| `DELETE` | `/api/v1/posts/<id>/like` | JWT | Default | Unlike a post |
| `GET` | `/api/v1/posts/<id>/likes` | Public | Default | Get list of users who liked post |
| `GET` | `/api/v1/posts/<id>/liked` | JWT | Default | Check if user liked post |
| `POST` | `/api/v1/posts/<id>/comments` | JWT | Default | Add comment to post |
| `GET` | `/api/v1/posts/<id>/comments` | Public | Default | Get comments for post |
| `PUT` | `/api/v1/comments/<id>` | JWT | Default | Edit comment text |
| `DELETE` | `/api/v1/comments/<id>` | JWT | Default | Delete comment |
| `POST` | `/api/v1/users/<id>/follow` | JWT | Default | Follow user |
| `DELETE` | `/api/v1/users/<id>/follow` | JWT | Default | Unfollow user |
| `GET` | `/api/v1/users/<id>/followers` | Public | Default | Get followers list |
| `GET` | `/api/v1/users/<id>/following` | Public | Default | Get following list |
| `GET` | `/api/v1/users/<id>/follow-status` | JWT | Default | Check mutual follow status |

---

## Local Installation & Setup

```bash
cd twitter_clone_backend

# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Docker Setup (Development & Production)

### Development (Live Reload):
```bash
docker compose up --build
```

### Production Stack (Gunicorn + Postgres + Nginx):
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-production-super-secret-key
JWT_SECRET_KEY=your-production-jwt-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/twitter_clone_db
UPLOAD_FOLDER=uploads
IMAGE_UPLOAD_FOLDER=uploads/images
VIDEO_UPLOAD_FOLDER=uploads/videos
MAX_CONTENT_LENGTH=52428800 # 50 MB
```

---

## PostgreSQL Database Migrations

```bash
# 1. Create PostgreSQL database in psql terminal
CREATE DATABASE twitter_clone_db;

# 2. Run migrations
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```

---

## Running Pytest Test Suite

Run automated unit and integration tests:

```bash
pytest -v
```

---

## Health Monitoring & Logging

- **Health Check Endpoint**: `GET /api/v1/health` returns status, DB connection check (`SELECT 1`), version, and server uptime.
- **Application Logs**: Logs server startup, API requests, execution times, authentication failures, and errors to `logs/application.log`.
- **Swagger UI**: Interactive documentation accessible at `http://localhost:5000/apidocs/`.

---

## Cloud Deployment (Render, Railway, AWS EC2)

- **Render**: Configured via `render.yaml`.
- **Railway**: Configured via `railway.json`.
- **AWS EC2**: Detailed deployment instructions in `docs/DEPLOYMENT_AWS.md`.

---

## Project Directory Structure

```
twitter_clone_backend/
│
├── .github/workflows/       # GitHub Actions CI/CD pipeline
│   └── ci.yml
├── app/
│   ├── __init__.py          # Application Factory, logging, middleware & v1 routing
│   ├── config.py            # Development, Testing, Production configurations
│   ├── extensions.py        # SQLAlchemy, Migrate, JWT, Bcrypt, Swagger, Limiter
│   ├── errors.py            # Centralized exception handlers
│   ├── health.py            # System health monitoring endpoint
│   │
│   ├── auth/                # Authentication Blueprint
│   ├── users/               # User Profile Management Blueprint
│   ├── posts/               # Post Management & Feed Blueprint
│   ├── comments/            # Comment System Blueprint
│   ├── likes/               # Like System Blueprint
│   ├── follows/             # Follow System Blueprint
│   └── models/              # SQLAlchemy ORM Models (User, Post, Comment, Like, Follow)
│
├── docs/                    # Cloud & Docker deployment guides
│   ├── DEPLOYMENT_AWS.md
│   └── DOCKER_GUIDE.md
├── nginx/conf.d/            # Nginx reverse proxy configuration
│   └── app.conf
├── scripts/                 # Database backup & restore scripts
│   ├── backup_db.sh
│   └── restore_db.sh
├── tests/                   # Pytest test suite
├── Dockerfile               # Production multi-stage Docker build
├── docker-compose.yml       # Local development Compose setup
├── docker-compose.prod.yml  # Production Compose setup (Web + DB + Nginx)
├── render.yaml              # Render platform config
├── railway.json             # Railway platform config
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── LICENSE                  # MIT License
├── CONTRIBUTING.md          # Contributing guidelines
├── CHANGELOG.md             # Project changelog
├── SECURITY.md              # Security policy
└── CODE_OF_CONDUCT.md       # Contributor Covenant Code of Conduct
```
