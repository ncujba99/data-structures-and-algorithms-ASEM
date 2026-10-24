from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, undefer_group

from ..db import MESSAGES, STILL_REFERENCED, DbSession
from ..models import Country
from .common import CountryCode, FromOrm, Name, errors

router = APIRouter(prefix="/api/countries", tags=["countries"])


class CountryIn(BaseModel):
    code: CountryCode       # the primary key
    name: Name = Field(examples=["Болгария"])

    model_config = ConfigDict(json_schema_extra={"examples": [{"code": "BG", "name": "Болгария"}]})


class CountryPatch(BaseModel):
    name: Name = Field(examples=["Республика Молдова"])


class CountryOut(FromOrm):
    code: CountryCode
    name: str = Field(examples=["Молдова"])
    cities: int = Field(description="How many cities belong to the country", examples=[5])


CodePath = Annotated[str, Path(pattern=r"^[A-Z]{2}$", description="ISO 3166 code", examples=["MD"])]

# The city count is deferred in models.py; the country endpoints always want it.
WITH_COUNTS = undefer_group("counts")


def get_country_or_404(session: Session, code: str) -> Country:
    # populate_existing: read the row again, so the count is fresh after a change.
    country = session.get(Country, code, options=[WITH_COUNTS], populate_existing=True)
    if country is None:
        raise HTTPException(404, f"Страна {code} не найдена")
    return country


@router.get("/", summary="List countries")
def list_countries(session: DbSession) -> list[CountryOut]:
    """All countries sorted by name, with the number of cities in each."""
    return session.scalars(select(Country).options(WITH_COUNTS).order_by(Country.name)).all()


@router.get("/{code}/", summary="Get one country", responses=errors(not_found="Страна XX не найдена"))
def get_country(session: DbSession, code: CodePath) -> CountryOut:
    """One country with the number of its cities."""
    return get_country_or_404(session, code)


@router.post(
    "/", status_code=201, summary="Add a country",
    responses=errors(conflicts=[MESSAGES["countries_pkey"], MESSAGES["countries_name_key"]]),
)
def add_country(session: DbSession, country: CountryIn) -> CountryOut:
    """Adds a country. The ISO 3166 code is its primary key: short, well known and never changing.

    **Errors**
    - `409` the code or the name is taken.
    - `422` the code is not two capital letters, or the name is empty.
    """
    session.add(Country(**country.model_dump()))
    session.flush()             # the database checks its rules here, inside the route
    return get_country_or_404(session, country.code)


@router.patch(
    "/{code}/", summary="Rename a country",
    responses=errors(not_found="Страна XX не найдена", conflicts=[MESSAGES["countries_name_key"]]),
)
def rename_country(session: DbSession, code: CodePath, patch: CountryPatch) -> CountryOut:
    """Changes the name; the code, being the key, stays.
    One row changes, and every city and train in that country shows the new name."""
    country = get_country_or_404(session, code)
    country.name = patch.name
    session.flush()
    return country


@router.delete(
    "/{code}/", summary="Delete a country",
    response_description="The deleted country",
    responses=errors(not_found="Страна XX не найдена", conflicts=[STILL_REFERENCED["cities_country_code_fkey"]]),
)
def delete_country(session: DbSession, code: CodePath) -> CountryOut:
    """Deletes a country with no cities.
    The database refuses while any city belongs to it (foreign key from `cities.country_code`)."""
    country = get_country_or_404(session, code)
    session.delete(country)
    session.flush()             # refused here (409) while cities belong to it
    return country
