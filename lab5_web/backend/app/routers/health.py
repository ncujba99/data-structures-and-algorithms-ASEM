from fastapi import APIRouter
from sqlalchemy import select

from ..db import DbSession
from .common import Status

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/", summary="Is the database reachable")
def health(session: DbSession) -> Status:
    """Runs `SELECT 1`. Answers `{"status": "ok"}`, or `500` when the database does not answer."""
    session.execute(select(1))
    return {"status": "ok"}
