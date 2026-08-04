# Docker Architecture & Usage Guide

## Local Development Setup

To run locally with live reloading:

```bash
docker compose up --build
```

Access API at `http://localhost:5000/api/v1/health`.

## Production Stack Setup

To run the complete production stack (Web + Postgres + Nginx):

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## Running Database Migrations in Docker

```bash
docker compose -f docker-compose.prod.yml exec web flask db upgrade
```

## Viewing Logs

```bash
docker compose -f docker-compose.prod.yml logs -f web
```
