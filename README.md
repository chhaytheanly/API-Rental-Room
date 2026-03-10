# Room Management API

A RESTful API for managing rental properties — rooms, tenants, invoices, and payments — built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **APScheduler**.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Database Setup (Docker)](#database-setup-docker)
  - [Install Dependencies](#install-dependencies)
  - [Run Migrations](#run-migrations)
  - [Seed the Database](#seed-the-database)
  - [Start the Server](#start-the-server)
- [API Reference](#api-reference)
  - [Authentication](#authentication)
  - [Users](#users)
  - [Rooms](#rooms)
  - [Tenants](#tenants)
  - [Billing](#billing)
- [Data Models](#data-models)
- [Scheduled Jobs](#scheduled-jobs)
- [Authorization](#authorization)
- [Database Seeder](#database-seeder)

---

## Features

- JWT-based authentication with device tracking
- Role-based access control (Admin / Staff / Tenant)
- Full CRUD for users, rooms, and tenants
- Automatic monthly invoice generation
- Daily late-fee processing via APScheduler
- File upload support for user/tenant profile images
- Database seeding CLI for development and testing

---

## Tech Stack

| Layer            | Technology                     |
| ---------------- | ------------------------------ |
| Framework        | FastAPI 0.133                  |
| ORM              | SQLAlchemy 2.0                 |
| Database         | PostgreSQL 16                  |
| Migrations       | Alembic                        |
| Auth             | python-jose (JWT), argon2-cffi |
| Scheduler        | APScheduler 3.11               |
| Server           | Uvicorn                        |
| Containerization | Docker Compose                 |

---

## Project Structure

```
.
├── docker-compose.yml          # PostgreSQL + pgAdmin containers
├── alembic.ini                 # Alembic config
├── alembic/versions/           # Migration files
├── requirements.txt
└── src/
    ├── main.py                 # FastAPI app entry point
    └── app/
        ├── config/
        │   ├── base.py         # SQLAlchemy declarative base
        │   ├── config.py       # Environment settings
        │   ├── logger.py       # Logging setup
        │   ├── scheduler.py    # APScheduler setup
        │   └── session.py      # DB session factory
        ├── database/
        │   ├── index.py        # Seeder CLI entry point
        │   └── seed/           # Seeder classes (role, user, room, tenant, invoice, payment)
        ├── middleware/
        │   ├── jwt_service.py  # JWT encode/decode/verify
        │   └── guard/
        │       └── permission.py  # PermissionGuard (admin_only)
        ├── model/              # SQLAlchemy ORM models
        ├── routes/             # FastAPI routers
        ├── schema/             # Pydantic request/response schemas
        ├── services/           # Business logic layer
        └── utils/
            ├── argon2.py       # Password hashing
            ├── color.py        # Colored terminal output
            └── device_tracker.py  # Client IP / device info
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- `pip` or a virtual environment manager

---

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:admin2026@localhost:5432/db_room
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

### Database Setup (Docker)

Start PostgreSQL and pgAdmin with Docker Compose:

Create a `docker-compose.yml` file in the project root:

```docker-compose.yml
version: "3.8"

services:
  postgres:
    image: postgres:16
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: db_room
    ports:
      - "5432:5432"
    volumes:
      - postgres:/var/lib/postgresql/data
    networks:
      - rental_room

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@gmail.com
      PGADMIN_DEFAULT_PASSWORD: your_password
    ports:
      - "5050:80"
    depends_on:
      - postgres
    volumes:
      - pgadmin:/var/lib/pgadmin
    networks:
      - rental_room

volumes:
  postgres:
  pgadmin:

networks:
  rental_room:
    driver: bridge

```

after creating the file, run this:

```bash
docker compose up -d
```

| Service  | URL                   | Credentials                     |
| -------- | --------------------- | ------------------------------- |
| Postgres | `localhost:5432`      | `postgres` / `admin2026`        |
| pgAdmin  | http://localhost:5050 | `admin@gmail.com` / `admin2026` |

---

### Install Dependencies

If you want to use uv, Run this:

```bash
uv sync
```

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### Run Migrations

First, After cloning this project, You will need to remove the alembic, Run this:

```bash
rm -rf alembic/
```

then start fresh:

```bash
alembic init alembic
```

Right after init run this command to generate the database in postgres by sqlalchemy:

```bash
alembic upgrade head
```

To generate a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

---

### Seed the Database

Run the seeder from the project root using the `-m` flag:

```bash
python -m src.app.database.index
```

**Available options:**

```
--rooms N        Number of rooms to seed (default: 20)
--tenants N      Number of tenants to seed (default: 20)
--no-clear       Skip clearing existing data before seeding
--dry-run        Show what would be seeded without executing
```

**Examples:**

```bash
# Default seed (clears existing data, creates 20 rooms, 20 tenants)
python -m src.app.database.index

# Custom counts
python -m src.app.database.index --rooms 15 --tenants 10

# Add data without clearing
python -m src.app.database.index --no-clear

# Preview only
python -m src.app.database.index --dry-run
```

**Seeded accounts:**

| Role  | Email             | Password |
| ----- | ----------------- | -------- |
| Admin | admin@example.com | admin123 |
| Staff | john@rental.com   | staff123 |
| Staff | emma@rental.com   | staff123 |
| Staff | mike@rental.com   | staff123 |

---

### Start the Server

```bash
uvicorn src.main:app --reload
```

The API will be available at:

- **API Base URL:** http://localhost:8000/api/v1
- **Interactive Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## API Reference

All endpoints are prefixed with `/api/v1`.

Protected routes require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### Authentication

#### `POST /api/v1/login`

Login with email and password. Returns a JWT access token.

**Request body:**

```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Response:**

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "info": {
    "device": "...",
    "os": "...",
    "browser": "..."
  }
}
```

---

### Users

> All user routes are protected (Admin only), except `GET /users/{id}` and `GET /users/`.

| Method | Endpoint      | Description            | Auth Required |
| ------ | ------------- | ---------------------- | ------------- |
| POST   | `/users`      | Create a new user      | Admin         |
| GET    | `/users/`     | List all users (paged) | Yes           |
| GET    | `/users/{id}` | Get user by ID         | Yes           |
| PUT    | `/users/{id}` | Update user            | Yes           |
| DELETE | `/users/{id}` | Delete user            | Yes           |

**Query params for `GET /users/`:**

- `page` (int, default: 1)
- `limit` (int, default: 10)

**Create user** — multipart form with optional image upload:

```
name, email, password, role_id, image (file, optional)
```

---

### Rooms

| Method | Endpoint                  | Description                         |
| ------ | ------------------------- | ----------------------------------- |
| POST   | `/rooms/`                 | Create a new room                   |
| GET    | `/rooms/`                 | List all rooms (with query filters) |
| GET    | `/rooms/{room_id}`        | Get room by ID                      |
| PUT    | `/rooms/{room_id}`        | Update room details                 |
| DELETE | `/rooms/{room_id}`        | Delete room                         |
| POST   | `/rooms/{room_id}/assign` | Assign a tenant to a room           |
| POST   | `/rooms/{room_id}/pay`    | Record a payment for an invoice     |
| GET    | `/rooms/reports/monthly`  | Monthly payment report              |

**Assign tenant:**

```
POST /rooms/{room_id}/assign?tenant_id={tenant_id}
```

**Record payment:**

```
POST /rooms/{room_id}/pay?invoice_id={invoice_id}&amount={amount}
```

**Monthly report:**

```
GET /rooms/reports/monthly?month=2&year=2026
```

---

### Tenants

| Method | Endpoint               | Description               |
| ------ | ---------------------- | ------------------------- |
| POST   | `/tenants/`            | Create a new tenant       |
| GET    | `/tenants/`            | List all tenants          |
| GET    | `/tenants/{tenant_id}` | Get tenant by ID          |
| DELETE | `/tenants/{tenant_id}` | Remove / check out tenant |

**Create tenant body:**

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "012-345-6789",
  "id_card": "1234567890",
  "room_id": 3
}
```

---

### Billing

| Method | Endpoint                     | Description                                 |
| ------ | ---------------------------- | ------------------------------------------- |
| POST   | `/billing/trigger-monthly`   | Manually trigger monthly invoice generation |
| POST   | `/billing/trigger-late-fees` | Manually trigger late-fee processing        |
| GET    | `/billing/scheduler-status`  | Get APScheduler status and job list         |

---

## Data Models

### User

| Column   | Type    | Notes                |
| -------- | ------- | -------------------- |
| id       | Integer | Primary key          |
| name     | String  |                      |
| email    | String  | Unique               |
| password | String  | Argon2 hashed        |
| image    | String  | File path (optional) |
| role_id  | Integer | FK → roles.id        |

### Room

| Column       | Type     | Notes         |
| ------------ | -------- | ------------- |
| id           | Integer  | Primary key   |
| name         | String   |               |
| description  | String   | Optional      |
| price        | Float    | Monthly rent  |
| is_available | Boolean  | True = vacant |
| updated_at   | DateTime |               |

### Tenant

| Column         | Type     | Notes                  |
| -------------- | -------- | ---------------------- |
| id             | Integer  | Primary key            |
| room_id        | Integer  | FK → rooms.id (unique) |
| name           | String   |                        |
| email          | String   | Optional               |
| phone          | String   | Optional               |
| id_card        | String   | Optional               |
| photo          | String   | Optional               |
| is_active      | Boolean  | False = checked out    |
| check_in_date  | DateTime |                        |
| check_out_date | DateTime | Optional               |

### Invoice

| Column      | Type     | Notes                         |
| ----------- | -------- | ----------------------------- |
| id          | Integer  | Primary key                   |
| room_id     | Integer  | FK → rooms.id                 |
| tenant_id   | Integer  | FK → tenants.id               |
| month       | Integer  | 1–12                          |
| year        | Integer  |                               |
| amount      | Float    | Total due                     |
| amount_paid | Float    | Amount paid so far            |
| due_date    | Date     |                               |
| status      | Enum     | `pending` \| `paid` \| `late` |
| created_at  | DateTime |                               |
| paid_at     | DateTime | Optional, set when fully paid |

---

## Scheduled Jobs

APScheduler runs automatically on server startup with two background jobs:

| Job               | Schedule              | Description                                       |
| ----------------- | --------------------- | ------------------------------------------------- |
| `monthly_billing` | 1st of month, 2:00 AM | Generates invoices for all active tenants/rooms   |
| `daily_late_fees` | Every day, 3:00 AM    | Marks overdue invoices as `late` and applies fees |

Both jobs can also be triggered manually via the [Billing endpoints](#billing).

---

## Authorization

Routes are protected using `PermissionGuard.admin_only`, which validates the JWT from the `Authorization: Bearer` header and checks the user's role.

**Public routes** (no token required):

- `POST /api/v1/login`

**Protected routes** (token required):

- All `/users`, `/rooms`, `/tenants`, `/billing` endpoints.

Token payload structure:

```json
{
  "sub": "<user_id>",
  "role": "<role_id>",
  "exp": "<expiry_timestamp>"
}
```

---

## Database Seeder

The seeder is a CLI tool located at `src/app/database/index.py`. It orchestrates the following steps in order:

1. **Clear** — Truncates all tables and resets auto-increment IDs
2. **Roles** — Seeds Admin, Staff, Tenant roles
3. **Users** — Seeds admin + staff accounts
4. **Rooms** — Seeds N rooms (mix of available and occupied)
5. **Tenants** — Seeds tenants assigned to occupied rooms
6. **Invoices** — Seeds monthly invoices for each tenant
7. **Payments** — Seeds partial/full payments for invoices

Always run the seeder as a module from the project root:

```bash
python -m src.app.database.index
```
