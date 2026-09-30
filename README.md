# ISP Billing Assessment

A subscription-based billing and onboarding system for ISP/telecom-style services built with Django REST Framework and Vue.

---

## Tech Stack

- **Backend:** Django 6.1, Django REST Framework
- **Authentication:** JWT via `djangorestframework-simplejwt` (access + refresh with token rotation & blacklisting)
- **Frontend:** Vue 2.7, Vuex 3, Vue Router 3, Axios, Vite
- **Database:** PostgreSQL 16 (production/Docker) & SQLite (local fallback/testing)
- **Containerization:** Docker Compose (Nginx reverse-proxy + Gunicorn WSGI + PostgreSQL)

---

## Architecture & Design Decisions

- **Two Focused Apps (`accounts` & `billing`):**
  - `Accounts` encapsulates user identity, auth, and onboarding. `billing` manages packages, subscriptions, and immutable invoice generation.
- **Role Scoping (`is_staff`):**
  - `is_staff=True` designates administrative staff. Standard customers cannot assign/cancel services or view other users' subscriptions/invoices.
  - Access control is enforced strictly at the database query level (`get_queryset()`) in addition to DRF permissions.
- **Immutable Invoice Snapshots:**
  - When subscriptions are assigned, an `Invoice` is generated with snapshot line items (`package_name`, `package_type`, `price`). Changing a package's price later does not alter previously issued invoices.
- **No Response Caching / Redis:**
  - Per requirements, kept lean without unnecessary cache layers that risk leaking scoped billing data.
- **Nginx Reverse Proxy in Docker:**
  - Same-origin reverse proxy for `/api/` in production, simplifying CORS and deployment.

---

## Super Admin Creation

With Docker, the first admin user will create automatically.

Add the below values to `backend/.env` before starting Docker:

```env
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your-password
```

For local setup, use the command in the local backend section below.

---

## Running with Docker Compose (Recommended)

1. Create the backend environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Open `backend/.env` and set the database and admin values.

   Use `POSTGRES_HOST=db` for Docker Compose.

3. Start the app:
   ```bash
   docker compose up --build
   ```

Docker will start the database, run migrations, and create the admin user.

Open these URLs:

- Frontend: **http://localhost:5173**
- Backend: **http://localhost:8000**
- Django Admin: **http://localhost:8000/admin/**
- API docs: **http://localhost:8000/api/v1/docs/**

---

## Running Locally for Development

### What you need

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20+ and npm

### Backend Setup

```bash
cd backend

# Install backend packages
uv sync

# If you use PostgreSQL on your own computer, set POSTGRES_HOST=localhost in backend/.env.

# Create database tables
uv run python manage.py migrate

# Create an admin user
uv run python manage.py ensure_adminuser --email=admin@example.com --password=change-me

# Start the backend
uv run python manage.py runserver
```

### Backend tests

```bash
cd backend
uv run pytest
```

### Frontend Setup

```bash
cd frontend

# Install frontend packages
npm install

# Start the frontend
npm run dev
```

Open `http://localhost:5173`.

---

## Key API Endpoints

- `POST /api/v1/auth/login/` — Log in
- `POST /api/v1/auth/refresh/` — Get a new access token
- `POST /api/v1/auth/logout/` — Log out
- `GET|PATCH /api/v1/auth/me/` — View or update your profile
- `GET|POST /api/v1/users/` — Admin: list or create users
- `GET|POST|PATCH /api/v1/packages/` — Admin: manage packages
- `GET|POST /api/v1/subscriptions/` — View or add subscriptions
- `GET|PATCH /api/v1/subscriptions/{id}/` — View or update a subscription
- `GET /api/v1/invoices/` — View invoices

---
