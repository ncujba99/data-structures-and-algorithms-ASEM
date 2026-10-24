"""The database connection: engine and sessions, errors turned into HTTP answers, EXPLAIN, ANALYZE and TRUNCATE."""

import os
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from psycopg import errors
from sqlalchemy import URL, Executable, create_engine, make_url
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import ClauseElement


def database_url() -> URL:
    """DATABASE_URL is a plain postgresql:// URL; SQLAlchemy also needs the driver: psycopg 3."""
    return make_url(os.environ["DATABASE_URL"]).set(drivername="postgresql+psycopg")


engine = create_engine(database_url(), pool_pre_ping=True)
# expire_on_commit=False: objects stay readable after the commit, while FastAPI turns them into JSON.
SessionFactory = sessionmaker(engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """One request is one transaction: committed when the route returns, rolled back if it raises."""
    with SessionFactory.begin() as session:
        yield session


# A route asks for a session by declaring a parameter of this type.
DbSession = Annotated[Session, Depends(get_session)]


# The database enforces the rules; these turn its constraint names into messages.
# The names come from the naming convention in models.py.
MESSAGES = {
    "trains_pkey": "Поезд с таким номером уже есть",
    "trains_number_range": "Номер поезда должен быть от 1 до 9999",
    "trains_destination_id_fkey": "Города назначения нет в справочнике",
    "train_stops_city_id_fkey": "Промежуточной станции нет в справочнике",
    "train_stops_train_number_city_id_key": "Город повторяется в маршруте",
    "cities_name_key": "Такой город уже есть",
    "cities_name_not_blank": "Название города не может быть пустым",
    "cities_country_code_fkey": "Такой страны нет в справочнике",
    "countries_pkey": "Страна с таким кодом уже есть",
    "countries_name_key": "Страна с таким названием уже есть",
}

# The same foreign keys, violated by deleting the referenced row instead.
STILL_REFERENCED = {
    "trains_destination_id_fkey": "Город — конечная станция поездов. Сначала удалите эти поезда.",
    "train_stops_city_id_fkey": "Через город проходят поезда. Сначала удалите эти поезда.",
    "cities_country_code_fkey": "В стране есть города. Сначала удалите их или перенесите в другую страну.",
}


def integrity_error_handler(_request: Request, exc: IntegrityError):
    error = exc.orig        # the psycopg error SQLAlchemy wraps
    constraint = error.diag.constraint_name
    if isinstance(error, errors.ForeignKeyViolation) and "still referenced" in (error.diag.message_detail or ""):
        return JSONResponse(status_code=409, content={"detail": STILL_REFERENCED.get(constraint, str(error))})
    status = 409 if isinstance(error, errors.UniqueViolation) else 422
    return JSONResponse(status_code=status, content={"detail": MESSAGES.get(constraint, error.diag.message_primary)})


# --- EXPLAIN, ANALYZE and TRUNCATE -----------------------------------------
# SQLAlchemy has no construct for these PostgreSQL commands; its compiler extension adds them:
#     session.execute(Explain(select(Train).where(Train.number == 50)))
#     session.execute(Analyze(Train, City))
#     session.execute(Truncate(TrainStop, Train))

class Explain(Executable, ClauseElement):
    """EXPLAIN <query>: the plan PostgreSQL chose, one line per row."""
    inherit_cache = False

    def __init__(self, statement):
        self.statement = statement


class Analyze(Executable, ClauseElement):
    """ANALYZE <tables>: refresh the statistics the planner uses to choose between a scan and an index."""
    inherit_cache = False

    def __init__(self, *models):
        self.tables = [model.__table__ for model in models]


class Truncate(Analyze):
    """TRUNCATE <tables>: empty them at once. Unlike DELETE, the tables and their index trees
    start again from empty pages, so the trees shrink back to height 1."""


@compiles(Explain, "postgresql")
def _explain(element, compiler, **kw):
    return "EXPLAIN " + compiler.process(element.statement, **kw)


@compiles(Analyze, "postgresql")
def _analyze(element, compiler, **kw):
    return "ANALYZE " + ", ".join(compiler.preparer.format_table(table) for table in element.tables)


@compiles(Truncate, "postgresql")
def _truncate(element, compiler, **kw):
    return "TRUNCATE " + ", ".join(compiler.preparer.format_table(table) for table in element.tables)


def to_sql(statement) -> str:
    """The SQL SQLAlchemy sends for a query, with the parameters filled in: for showing, not for running."""
    return str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
