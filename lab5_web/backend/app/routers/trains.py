from datetime import time
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import AliasPath, BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import Select, exists, func, or_, select
from sqlalchemy.orm import Session, aliased, joinedload, selectinload

from ..db import MESSAGES, DbSession
from ..models import City, Train, TrainStop
from .common import CityId, FromOrm, errors

router = APIRouter(prefix="/api/trains", tags=["trains"])


class TrainIn(BaseModel):
    number: int = Field(ge=1, le=9999, description="Train number, the key field", examples=[90])
    destination_id: CityId
    departure: time = Field(description="Departure from our station", examples=["07:30"])
    stops: list[int] = Field(
        default=[], max_length=20,
        description="Intermediate stations as city ids, in route order; the destination is not one of them",
        examples=[[2, 8]],
    )

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"number": 90, "destination_id": 10, "departure": "07:30", "stops": [2, 8]}],
    })

    @model_validator(mode="after")
    def destination_is_not_a_stop(self):
        if self.destination_id in self.stops:
            raise ValueError("Конечная станция не может быть промежуточной")
        return self


class StopOut(FromOrm):
    id: int = Field(examples=[8])
    name: str = Field(examples=["Киев"])


class DestinationOut(StopOut):
    country: str | None = Field(None, validation_alias=AliasPath("country", "name"), examples=["Россия"])


class TrainOut(FromOrm):
    number: int = Field(examples=[50])
    departure: time = Field(examples=["08:15:00"])
    destination: DestinationOut
    # Train.stop_cities: the City of every stop, in route order.
    stops: list[StopOut] = Field(validation_alias="stop_cities", description="Intermediate stations in route order")


class TrainPage(BaseModel):
    total: int = Field(description="How many trains match; `items` holds at most `limit` of them", examples=[9])
    items: list[TrainOut]


Match = Literal["to", "via", "both"]

TrainNumberPath = Annotated[int, Path(ge=1, le=9999, description="Train number", examples=[50])]


# What a TrainOut needs: the destination with its country (one JOIN), the stops with their cities
# (one more query for all trains of the page, not one per train).
WITH_ROUTE = (
    joinedload(Train.destination).joinedload(City.country),
    selectinload(Train.stops).joinedload(TrainStop.city),
)


def get_train_or_404(session: Session, number: int) -> Train:
    # Search by primary key. populate_existing: read it again, so a just-added train comes with its route.
    train = session.get(Train, number, options=WITH_ROUTE, populate_existing=True)
    if train is None:
        raise HTTPException(404, f"Поезд № {number} не найден")
    return train


def departing_between(query: Select, time_from: time | None, time_to: time | None) -> Select:
    if time_from is not None:
        query = query.where(Train.departure >= time_from)
    if time_to is not None:
        query = query.where(Train.departure <= time_to)
    return query


@router.get("/", summary="List and filter trains", response_description="One page of matching trains and their total")
def list_trains(
    session: DbSession,
    city_id: Annotated[CityId | None, Query(description="Only trains linked to this city; see `match`")] = None,
    match: Annotated[Match, Query(
        description="How the train is linked to `city_id`: `to` ends there, `via` stops there on the way, "
                    "`both` either. Ignored without `city_id`.",
    )] = "to",
    time_from: Annotated[time | None, Query(description="Departure at or after", examples=["08:00"])] = None,
    time_to: Annotated[time | None, Query(description="Departure at or before", examples=["12:00"])] = None,
    limit: Annotated[int, Query(ge=1, le=1000, description="At most this many trains in `items`")] = 200,
) -> TrainPage:
    """Trains sorted by number, like the lab's inorder traversal of the tree.

    All filters are optional and combine with AND:

    | Filter | Matches |
    |---|---|
    | `city_id` + `match=to` | trains whose destination is the city |
    | `city_id` + `match=via` | trains that stop there on the way (passing trains) |
    | `city_id` + `match=both` | either of the two |
    | `time_from`, `time_to` | departure in the range, both ends included |

    `total` counts every matching train; `items` holds at most `limit` of them.
    In the lab each of these searches is a full traversal; here the city filter uses the index on
    `trains.destination_id` or `train_stops.city_id`, and the time range uses `trains_departure_idx`.

    Example: `GET /api/trains/?city_id=8&match=via` - trains passing through Киев.
    """
    query = select(Train)
    if city_id is not None:
        ends_there = Train.destination_id == city_id
        stops_there = Train.stops.any(TrainStop.city_id == city_id)
        query = query.where({"to": ends_there, "via": stops_there, "both": or_(ends_there, stops_there)}[match])
    query = departing_between(query, time_from, time_to)

    total = session.scalar(select(func.count()).select_from(query.subquery()))
    items = session.scalars(query.options(*WITH_ROUTE).order_by(Train.number).limit(limit)).all()
    return {"total": total, "items": items}


# Declared before /{number}/, so "search" is never taken for a train number.
@router.get("/search/", summary="Search trains from one city to another",
            response_description="Matching trains, earliest departure first")
def search_trains(
    session: DbSession,
    to_id: Annotated[CityId, Query(description="Where the passenger goes: the destination or any stop")],
    from_id: Annotated[CityId | None, Query(
        description="Where the passenger gets on: a stop that comes before `to_id`. Omit for our station, "
                    "where every train starts.",
    )] = None,
    time_from: Annotated[time | None, Query(description="Departure from our station at or after", examples=["06:00"])] = None,
    time_to: Annotated[time | None, Query(description="Departure from our station at or before", examples=["12:00"])] = None,
) -> TrainPage:
    """The passenger's search: trains that take you from `from_id` to `to_id`.

    A route is our station → its stops in order → its destination. A train matches when `to_id` is on
    its route and, if `from_id` is given, `from_id` comes **before** `to_id`. So Бельцы → Киев finds
    train 50 (Бельцы → Киев → Москва), and Киев → Бельцы finds nothing.

    Trains run every day and only the departure from our station is stored, so the time filters apply to it.
    Sorted by departure time. `from_id` equal to `to_id` matches nothing.
    """
    arrives = or_(Train.destination_id == to_id, Train.stops.any(TrainStop.city_id == to_id))
    if from_id is None:
        # Every train starts at our station: it is enough that to_id is on the route.
        condition = arrives
    else:
        # from_id is a stop; to_id is the destination or a later stop.
        boarding, alighting = aliased(TrainStop), aliased(TrainStop)
        later_stop = exists().where(
            alighting.train_number == boarding.train_number,
            alighting.city_id == to_id,
            alighting.stop_no > boarding.stop_no,
        )
        condition = exists().where(
            boarding.train_number == Train.number,
            boarding.city_id == from_id,
            or_(Train.destination_id == to_id, later_stop),
        )
    query = departing_between(select(Train).where(condition), time_from, time_to)

    items = session.scalars(query.options(*WITH_ROUTE).order_by(Train.departure, Train.number)).all()
    return {"total": len(items), "items": items}


@router.get("/{number}/", summary="Get one train", responses=errors(not_found="Поезд № 99 не найден"))
def get_train(session: DbSession, number: TrainNumberPath) -> TrainOut:
    """Search by the key field, the lab's main search.

    The lab walks down its binary search tree from the root; PostgreSQL walks down `trains_pkey`,
    the B+-tree behind `PRIMARY KEY (number)`. Both take O(height) steps.
    """
    return get_train_or_404(session, number)


@router.post(
    "/", status_code=201, summary="Add a train with its route",
    response_description="The saved train, as GET returns it",
    responses=errors(conflicts=[MESSAGES["trains_pkey"], MESSAGES["train_stops_train_number_city_id_key"]]),
)
def add_train(session: DbSession, train: TrainIn) -> TrainOut:
    """Saves the train and its intermediate stops in **one transaction**: all of it, or nothing.
    If any stop is refused, the train is not saved either.

    `stops` are city ids in route order; the destination must not be one of them.

    **Errors**
    - `409` the number is taken, or a city appears twice in the route (both are UNIQUE in the database).
    - `422` a broken rule, checked by the request schema or by the database:
      "Конечная станция не может быть промежуточной", "Города назначения нет в справочнике",
      "Промежуточной станции нет в справочнике".
    """
    new = Train(
        number=train.number,
        destination_id=train.destination_id,
        departure=train.departure,
        stops=[TrainStop(city_id=city_id) for city_id in train.stops],   # numbered 1, 2, ... by ordering_list
    )
    session.add(new)
    session.flush()             # the database checks its rules here, inside the route
    return get_train_or_404(session, new.number)


@router.delete(
    "/{number}/", summary="Delete a train",
    response_description="The deleted train: POST it back to undo",
    responses=errors(not_found="Поезд № 99 не найден"),
)
def delete_train(session: DbSession, number: TrainNumberPath) -> TrainOut:
    """Deletes the train; its stops go with it (`ON DELETE CASCADE` on `train_stops`).

    The answer is the deleted train itself, so a client can undo by sending it back to `POST /api/trains/`.
    """
    train = get_train_or_404(session, number)
    session.delete(train)
    session.flush()
    return train
