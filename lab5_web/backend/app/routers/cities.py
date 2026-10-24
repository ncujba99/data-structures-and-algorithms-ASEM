from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from pydantic import AliasPath, BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, undefer_group

from ..db import MESSAGES, STILL_REFERENCED, DbSession
from ..models import City
from .common import CountryCode, FromOrm, Name, errors

router = APIRouter(prefix="/api/cities", tags=["cities"])


class CityIn(BaseModel):
    name: Name = Field(examples=["Сороки"])
    country_code: CountryCode | None = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"name": "Сороки", "country_code": "MD"}]})


class CityPatch(BaseModel):
    """Only the fields present in the request are changed; `country_code: null` clears the country."""
    name: Name | None = Field(None, examples=["Кишинёв"])
    country_code: CountryCode | None = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"name": "Киев"}, {"country_code": "UA"}]})


class CityOut(FromOrm):
    id: int = Field(examples=[8])
    name: str = Field(examples=["Киев"])
    country_code: str | None = Field(examples=["UA"])
    country: str | None = Field(None, validation_alias=AliasPath("country", "name"), examples=["Украина"])
    trains_to: int = Field(description="Trains whose destination is this city", examples=[1])
    trains_via: int = Field(description="Trains that stop here on the way", examples=[2])

CityIdPath = Annotated[int, Path(ge=1, description="City id", examples=[8])]

# What a CityOut needs: the country (one JOIN) and the train counts, deferred in models.py.
WITH_DETAILS = (joinedload(City.country), undefer_group("counts"))


def get_city_or_404(session: Session, city_id: int) -> City:
    # populate_existing: read the row again, so counts and country are fresh after a change.
    city = session.get(City, city_id, options=WITH_DETAILS, populate_existing=True)
    if city is None:
        raise HTTPException(404, f"Город № {city_id} не найден")
    return city


@router.get("/", summary="List cities")
def list_cities(session: DbSession) -> list[CityOut]:
    """All cities sorted by name, with their country and two counts:
    `trains_to` (trains that end there) and `trains_via` (trains that pass through)."""
    return session.scalars(select(City).options(*WITH_DETAILS).order_by(City.name)).all()


@router.get("/{city_id}/", summary="Get one city", responses=errors(not_found="Город № 99 не найден"))
def get_city(session: DbSession, city_id: CityIdPath) -> CityOut:
    """One city with its country and train counts."""
    return get_city_or_404(session, city_id)


@router.post("/", status_code=201, summary="Add a city", responses=errors(conflicts=[MESSAGES["cities_name_key"]]))
def add_city(session: DbSession, city: CityIn) -> CityOut:
    """Adds a city; trains can then use it as a destination or a stop. The country is optional.

    **Errors**
    - `409` a city with this name exists (`UNIQUE` on `cities.name`).
    - `422` "Такой страны нет в справочнике": `country_code` is not in `countries` (foreign key).
    """
    new = City(**city.model_dump())
    session.add(new)
    session.flush()             # the database checks its rules here and assigns the id
    return get_city_or_404(session, new.id)


@router.patch(
    "/{city_id}/", summary="Rename a city or change its country",
    responses=errors(not_found="Город № 99 не найден", conflicts=[MESSAGES["cities_name_key"]]),
)
def update_city(session: DbSession, city_id: CityIdPath, patch: CityPatch) -> CityOut:
    """Changes only the fields sent: `name`, `country_code`, or both. `"country_code": null` clears the country.

    The name is stored in one row only, so every train that ends or stops here shows the new name at once.
    In the lab the name is copied into every train, and renaming means visiting every node.

    **Errors**
    - `404` no such city.
    - `409` another city has this name.
    - `422` "Нечего менять" (empty body), or "Такой страны нет в справочнике".
    """
    changes = patch.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(422, "Нечего менять")
    city = get_city_or_404(session, city_id)
    for field, value in changes.items():
        setattr(city, field, value)
    session.flush()
    return get_city_or_404(session, city_id)


@router.delete(
    "/{city_id}/", summary="Delete a city",
    response_description="The deleted city",
    responses=errors(
        not_found="Город № 99 не найден",
        conflicts=[STILL_REFERENCED["trains_destination_id_fkey"], STILL_REFERENCED["train_stops_city_id_fkey"]],
    ),
)
def delete_city(session: DbSession, city_id: CityIdPath) -> CityOut:
    """Deletes a city that no train uses.

    The database refuses while any train ends or stops there (foreign keys from `trains` and
    `train_stops`), so a train can never point to a missing city.
    """
    city = get_city_or_404(session, city_id)
    session.delete(city)
    session.flush()             # refused here (409) while trains use the city
    return city
