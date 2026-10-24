"""What several routers share: field types, the error model, and base classes for response models.

Example ids in the docs are those of the demo data (POST /api/demo/reset/): 1 Унгены, 2 Бельцы,
3 Бендеры, 4 Тирасполь, 5 Страшены, 6 Яссы, 7 Бухарест, 8 Киев, 9 Одесса, 10 Москва.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
CountryCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{2}$"),
    Field(description="ISO 3166 code, two capital letters", examples=["MD"]),
]
CityId = Annotated[int, Field(ge=1, description="City id", examples=[10])]


class FromOrm(BaseModel):
    """A response model filled from the attributes of an ORM object (models.py).
    A route returns the ORM object; FastAPI turns it into this model's JSON."""
    model_config = ConfigDict(from_attributes=True)


class Query(BaseModel):
    """A query as the Python code that builds it and the SQL SQLAlchemy compiles it to."""
    python: str = Field(description="The function that builds the query")
    sql: str = Field(description="The SQL sent to PostgreSQL")


class Status(BaseModel):
    status: Literal["ok"]


class Error(BaseModel):
    """Every error the API raises itself: a message ready to show to the user."""
    detail: str = Field(examples=["Поезд № 99 не найден"])


def errors(not_found: str | None = None, conflicts: list[str] = ()) -> dict:
    """The `responses=` argument of a route: the errors it can return, with their real messages as examples.

    422 is documented by FastAPI itself (a list of field errors). A broken database rule also answers 422,
    but with an `Error` body; the route's description lists those messages.
    """
    responses = {}
    if not_found:
        responses[404] = {
            "model": Error,
            "description": "Not found",
            "content": {"application/json": {"example": {"detail": not_found}}},
        }
    if conflicts:
        responses[409] = {
            "model": Error,
            "description": "Conflicts with existing data: a duplicate, or a row other rows still refer to",
            "content": {"application/json": {"examples": {
                f"conflict{i}": {"summary": message, "value": {"detail": message}}
                for i, message in enumerate(conflicts, 1)
            }}},
        }
    return responses
