# Backend

This folder contains the Django REST API.

For the full project setup, see the [main README](../README.md).

## Local Setup

You need Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py ensure_adminuser --email=admin@example.com --password=change-me
uv run python manage.py runserver
```

The API runs at `http://localhost:8000`.

Useful URLs:

- Django Admin: **http://localhost:8000/admin/**
- API docs: **http://localhost:8000/api/v1/docs/**

## Tests

```bash
cd backend
uv run pytest
```

## Database

Without `POSTGRES_HOST`, Django uses SQLite for local work.

If you use PostgreSQL on your own computer, set `POSTGRES_HOST=localhost` in `backend/.env`.
