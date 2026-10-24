"""What PostgreSQL does inside: query plans and the B+-tree behind every index."""

import inspect
from datetime import time
from typing import Annotated

from fastapi import APIRouter, Query as Param
from pydantic import BaseModel, Field
from sqlalchemy import Select, extract, func, inspect as reflect, select

from ..db import DbSession, Explain, to_sql
from ..models import Base, City, Train
from .common import Query

router = APIRouter(prefix="/api", tags=["internals"])


class Plan(Query):
    title: str
    plan: list[str] = Field(description="EXPLAIN output, one line per item")


class Plans(BaseModel):
    rows: int = Field(description="Rows in `trains` when the plans were made")
    queries: list[Plan]


class IndexOut(BaseModel):
    """A B+-tree in the schema: behind a primary key, a unique constraint or an index of models.py."""
    table_name: str = Field(examples=["trains"])
    index_name: str = Field(examples=["trains_pkey"])
    definition: str = Field(examples=["CREATE UNIQUE INDEX trains_pkey ON public.trains USING btree (number)"])
    height: int = Field(description="Levels from the root page to the leaves", examples=[1])
    size: str = Field(examples=["16 kB"])


# The four searches. Each function builds a query; the API shows its source, its SQL and its plan.

def by_number(number: int) -> Select:
    return select(Train).where(Train.number == number)


def to_city(city: str) -> Select:
    return select(Train).join(Train.destination).where(City.name == city)


def departing_between(time_from: time, time_to: time) -> Select:
    return select(Train).where(Train.departure.between(time_from, time_to))


def on_the_hour() -> Select:
    return select(Train).where(extract("minute", Train.departure) == 0)


def index_info(name: str) -> Select:
    # bt_metap() comes with the pageinspect extension: the root page's level, 0 for a one-page tree.
    meta = func.bt_metap(name).table_valued("level")
    index = func.to_regclass(name)
    return select(
        func.pg_get_indexdef(index).label("definition"),
        (meta.c.level + 1).label("height"),
        func.pg_size_pretty(func.pg_relation_size(index)).label("size"),
    )


@router.get("/explain/", summary="Query plans for four searches")
def explain(
    session: DbSession,
    number: Annotated[int, Param(ge=1, le=9999, description="Train number for the key search")] = 50,
    city: Annotated[str, Param(min_length=1, max_length=100, description="City name for the JOIN search")] = "Москва",
    time_from: Annotated[time, Param(description="Start of the departure range")] = time(8, 0),
    time_to: Annotated[time, Param(description="End of the departure range")] = time(12, 0),
) -> Plans:
    """The `EXPLAIN` plans of four searches: three can use a B+-tree, one cannot.

    | Search | With enough rows |
    |---|---|
    | by number | `Index Scan using trains_pkey`: one walk down the tree |
    | trains to a city | a `JOIN`, searching two trees |
    | departure in a range | `trains_departure_idx`: a range of keys, part of an inorder traversal |
    | departure on the hour | `Seq Scan`: the condition is on an expression no tree is ordered by |

    For each search the answer has the Python that builds it, the SQL SQLAlchemy makes of it, and the plan.
    With the 9 demo trains every plan is a `Seq Scan`, because reading the whole table is cheaper.
    Run `POST /api/demo/bulk/` first to see the trees used.
    """
    searches = [
        ("Поиск по номеру: спуск по дереву первичного ключа", by_number, (number,)),
        ("Поезда до города: JOIN двух таблиц, поиск в двух деревьях", to_city, (city,)),
        ("Отправление в интервале: диапазон ключей = кусок симметричного обхода", departing_between, (time_from, time_to)),
        ("Ровно в начале часа: условие на выражение, дерево не помогает", on_the_hour, ()),
    ]
    plans = []
    for title, build, args in searches:
        query = build(*args)
        plans.append({
            "title": title,
            "python": inspect.getsource(build),
            "sql": to_sql(query),
            "plan": session.scalars(Explain(query)).all(),
        })
    return {"rows": session.scalar(select(func.count()).select_from(Train)), "queries": plans}


@router.get("/indexes/", summary="Every B+-tree in the schema")
def list_indexes(session: DbSession) -> list[IndexOut]:
    """Every B+-tree in the schema: one per primary key, one per UNIQUE constraint and one per explicit index.
    The names are read back from the database (reflection), for the tables of models.py.

    `height` is the number of levels from the root page to the leaves. A page holds hundreds of keys,
    so even 9999 trains fit in a tree of height 2, where the lab's binary tree needs at least 14 levels.
    """
    db = reflect(session.connection())
    result = []
    for table in sorted(Base.metadata.tables):
        names = [db.get_pk_constraint(table)["name"]]
        names += [unique["name"] for unique in db.get_unique_constraints(table)]
        names += [index["name"] for index in db.get_indexes(table) if not index.get("duplicates_constraint")]
        for name in sorted(names):
            info = session.execute(index_info(name)).mappings().one()
            result.append({"table_name": table, "index_name": name, **info})
    return result
