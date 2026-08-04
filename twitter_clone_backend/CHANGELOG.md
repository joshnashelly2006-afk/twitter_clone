# Changelog

All notable changes to the Twitter Clone Backend REST API project will be documented in this file.

## [1.0.0] - 2026-08-03
### Added
- Complete REST API Application Factory (`create_app`).
- PostgreSQL database integration via SQLAlchemy ORM & Flask-Migrate.
- Authentication module with Flask-Bcrypt & Flask-JWT-Extended token revocation blocklist.
- User Profile Management module with 5 MB profile image upload.
- Post Management module with 50 MB media uploads (.mp4, .mov, .jpg, .png).
- Like System & Comment System.
- Follow System & Personalized News Feed (`GET /api/v1/feed`) & Explore (`GET /api/v1/explore`).
- Production DevOps setup: Dockerfile, Docker Compose, Nginx conf, GitHub Actions CI/CD.
- Health Monitoring endpoint (`GET /api/v1/health`).
