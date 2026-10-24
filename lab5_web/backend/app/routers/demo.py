"""Demo data: back to the starting rows, or enough rows for the indexes to matter."""

import random
from datetime import time

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from .. import demo_data
from ..db import Analyze, DbSession, Truncate
from ..models import City, Country, Train, TrainStop
from .common import Status

router = APIRouter(prefix="/api/demo", tags=["demo"])


class BulkResult(BaseModel):
    added: int = Field(description="How many trains were added", examples=[9990])


def load_demo(session: Session) -> None:
    """Replaces all data with the demo data."""
    # All four at once, so no foreign key stands in the way; the index trees start from empty pages.
    session.execute(Truncate(TrainStop, Train, City, Country))
    session.execute(insert(Country), demo_data.COUNTRIES)
    session.execute(insert(City), demo_data.CITIES)
    session.execute(insert(Train), demo_data.train_rows())
    session.execute(insert(TrainStop), demo_data.stop_rows())
    # The demo cities have fixed ids; new cities continue after the largest one.
    session.execute(select(func.setval(func.pg_get_serial_sequence(City.__tablename__, "id"), func.max(City.id))))
    session.execute(Analyze(Country, City, Train, TrainStop))


def load_demo_if_empty(session: Session) -> None:
    """Called at startup: a fresh database gets the demo data, an existing one is left alone."""
    if session.scalar(select(func.count()).select_from(City)) == 0:
        load_demo(session)


@router.post("/bulk/", summary="Fill numbers 1…9999")
def bulk_fill(session: DbSession) -> BulkResult:
    """Adds a train for every free number from 1 to 9999, with a random destination, departure and stops.

    With so many rows the planner switches from `Seq Scan` to the indexes; see `GET /api/explain/`.
    Existing trains are kept. Undo with `POST /api/demo/reset/`.
    """
    city_ids = session.scalars(select(City.id)).all()
    taken = set(session.scalars(select(Train.number)))
    trains, stops = [], []
    for number in range(1, 10_000):
        if number in taken:
            continue
        destination = random.choice(city_ids)
        others = [c for c in city_ids if c != destination]
        trains.append({
            "number": number,
            "destination_id": destination,
            "departure": time(random.randrange(24), random.randrange(60)),
        })
        route = random.sample(others, k=min(len(others), random.choice([0, 0, 1, 1, 2, 3])))
        stops += [{"train_number": number, "stop_no": i, "city_id": city} for i, city in enumerate(route, 1)]
    if trains:
        session.execute(insert(Train), trains)
    if stops:
        session.execute(insert(TrainStop), stops)
    session.execute(Analyze(Train, TrainStop))
    return {"added": len(trains)}


@router.post("/reset/", summary="Restore the demo data")
def reset_demo(session: DbSession) -> Status:
    """Deletes **all** data and loads the demo again: 4 countries, 10 cities and the lab's 9 trains with their routes.

    The cities get ids 1 … 10 again (1 Унгены … 10 Москва), so the examples in these docs match.
    """
    load_demo(session)
    return {"status": "ok"}
