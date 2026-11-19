# Purely Sports

Purely Sports is a single-application, AI-assisted sports newsroom proof of concept. PostgreSQL is the system of record, and external publication remains under human authority.

## Requirements

- Python 3.12 or newer
- Docker Engine and Docker Compose v2 for local PostgreSQL

## Configure

Copy .env.example to .env. The sample values are for local development only. Do not commit production credentials or a populated .env file.

PowerShell: Copy-Item .env.example .env
macOS/Linux: cp .env.example .env

## Run with Docker Compose

Start the API and PostgreSQL with:

docker compose up --build

The API is available at http://localhost:8000 and the health endpoint at http://localhost:8000/health. Stop services with docker compose down. Use docker compose down -v only when intentionally deleting local database data.

## Run locally

Start PostgreSQL with docker compose up -d db. Create and activate a virtual environment, then install the development extras.

Windows PowerShell:

    py -3.12 -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -e ".[dev]"

macOS/Linux:

    python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install -e ".[dev]"

With .env configured and PostgreSQL running, start the API with:

    uvicorn app.main:app --reload

## Tests and quality checks

With PostgreSQL running:

    pytest
    ruff check .
    ruff format --check .
    mypy app

The health endpoint test does not require PostgreSQL; the database connectivity test does.

## Database migrations

Alembic is configured for PostgreSQL and SQLAlchemy metadata discovery. No migration is included in Phase 1. The initial migration is deferred until the Phase 2 model layer is complete and reviewed against docs/02_DATABASE_SCHEMA.md.

## Approved documentation

- docs/00_PROJECT_VISION.md
- docs/01_ARCHITECTURE.md
- docs/02_DATABASE_SCHEMA.md
- docs/03_IMPLEMENTATION_PLAN.md
