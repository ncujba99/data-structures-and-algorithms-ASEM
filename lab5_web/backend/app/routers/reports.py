"""Questions answered by one query each; with the lab's tree every one is a new traversal."""

import inspect
from datetime import time

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import Select, distinct, func, literal, select, union_all

from ..db import DbSession, to_sql
from ..models import City, Country, Train, TrainStop
from .common import Query

router = APIRouter(prefix="/api/reports", tags=["reports"])


class CountryReportRow(BaseModel):
    country: str
    cities: int
    trains: int = Field(description="Trains whose destination is in the country")
    first_departure: time | None
    last_departure: time | None


class CityReportRow(BaseModel):
    city: str
    country: str | None
    trains_to: int
    trains_via: int
    total: int


class CountryReport(Query):
    rows: list[CountryReportRow]


class CityReport(Query):
    rows: list[CityReportRow]


def trains_per_country() -> Select:
    return (
        select(
            Country.name.label("country"),
            func.count(distinct(City.id)).label("cities"),
            func.count(Train.number).label("trains"),
            func.min(Train.departure).label("first_departure"),
            func.max(Train.departure).label("last_departure"),
        )
        .outerjoin(City, City.country_code == Country.code)
        .outerjoin(Train, Train.destination_id == City.id)
        .group_by(Country.code)
        .order_by(func.count(Train.number).desc(), Country.name)
    )


def busiest_cities() -> Select:
    # One row per (city, train) link: the train ends there ('to') or stops there ('via').
    links = union_all(
        select(Train.destination_id.label("city_id"), literal("to").label("kind")),
        select(TrainStop.city_id, literal("via")),
    ).subquery("links")
    total = func.count().label("total")
    return (
        select(
            City.name.label("city"),
            Country.name.label("country"),
            func.count().filter(links.c.kind == "to").label("trains_to"),
            func.count().filter(links.c.kind == "via").label("trains_via"),
            total,
        )
        .join(City, City.id == links.c.city_id)
        .outerjoin(Country, Country.code == City.country_code)
        .group_by(City.id, Country.name)
        .order_by(total.desc(), City.name)
        .limit(10)
    )


def report(session, build) -> dict:
    query = build()
    return {"python": inspect.getsource(build), "sql": to_sql(query), "rows": session.execute(query).mappings().all()}


@router.get("/countries/", summary="Trains per country")
def by_country(session: DbSession) -> CountryReport:
    """For every country: its cities, the trains that end there, and the first and last departure.

    One query with `LEFT JOIN` and `GROUP BY`; countries with no trains are listed too, with zero trains.
    The answer includes the Python that builds the query and the SQL it becomes.
    With the lab's tree this would be a new traversal function.
    """
    return report(session, trains_per_country)


@router.get("/cities/", summary="Ten busiest cities")
def busiest(session: DbSession) -> CityReport:
    """The ten cities with the most trains, counting trains that end there (`trains_to`)
    and trains that pass through (`trains_via`). The answer includes the Python and the SQL."""
    return report(session, busiest_cities)
