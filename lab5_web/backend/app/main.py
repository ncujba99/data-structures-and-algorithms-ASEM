"""Train-station information desk (lab5, Задание 1) as a REST API over PostgreSQL.

The lab keeps trains in a hand-written binary search tree. Here they are rows
in related tables (countries → cities → trains → train_stops), and PostgreSQL
keeps a B+-tree for every primary key, UNIQUE constraint and index.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError

from .db import SessionFactory, engine, integrity_error_handler
from .routers import cities, countries, demo, health, internals, reports, trains

DESCRIPTION = """
Lab 5, Task 1 (a train-station information desk) on a relational database instead of a binary search tree.

**Data:** `countries` → `cities` → `trains`, plus `train_stops`, the ordered intermediate stations of every train.
Every train departs from our station; the destination and each stop are cities.

**Errors** come as `{"detail": "..."}` with a message ready to show to the user (in Russian):
`404` not found, `409` duplicate or still referenced, `422` a rule is broken.
Most rules are database constraints, so they hold for every client, not only this API.

**Paths** all end with `/`.

**Try it:** `POST /api/demo/reset/` restores the demo data; city ids are then 1 Унгены … 10 Москва,
and the examples on this page use them.
"""

TAGS = [
    {"name": "health", "description": "Service checks."},
    {"name": "trains", "description": "The lab's records. Search by number (the key field), list in key order, filter."},
    {"name": "cities", "description": "Each city is stored once; trains refer to it by id."},
    {"name": "countries", "description": "Keyed by ISO 3166 code; cities refer to it."},
    {"name": "reports", "description": "Questions answered by one SQL query each; the query comes back with the rows."},
    {"name": "internals", "description": "Query plans and the B+-tree behind every index."},
    {"name": "demo", "description": "Reset the demo data, or fill the table so the indexes matter."},
]


@asynccontextmanager
async def lifespan(_app):
    # Migrations create the tables (alembic upgrade head runs before the app); data is not a migration.
    with SessionFactory.begin() as session:
        demo.load_demo_if_empty(session)
    yield
    engine.dispose()


app = FastAPI(
    title="Train station desk",
    version="1.0.0",
    summary="Lab 5, Task 1 as a REST API: React → FastAPI → PostgreSQL",
    description=DESCRIPTION,
    openapi_tags=TAGS,
    lifespan=lifespan,
    swagger_ui_parameters={"docExpansion": "list", "defaultModelsExpandDepth": 0, "tryItOutEnabled": True},
)
app.add_exception_handler(IntegrityError, integrity_error_handler)

for module in (health, trains, cities, countries, reports, internals, demo):
    app.include_router(module.router)
