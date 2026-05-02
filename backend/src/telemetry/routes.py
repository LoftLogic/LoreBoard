"""Telemetry read-only API endpoints."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.telemetry.service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["telemetry"])
Db = Annotated[AsyncSession, Depends(get_async_session)]


@router.get("/runs")
async def list_runs(
    db: Db,
    agent_type: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    return await TelemetryService(db).list_runs(agent_type=agent_type, limit=limit, offset=offset)


@router.get("/runs/{run_id}")
async def get_run(run_id: uuid.UUID, db: Db) -> dict:
    detail = await TelemetryService(db).get_run_detail(run_id)
    if detail is None:
        raise HTTPException(404, "Run not found")
    return detail


@router.get("/summary")
async def get_summary(
    db: Db,
    since_hours: int = Query(24, ge=1, le=720),
) -> dict:
    return await TelemetryService(db).get_summary(since_hours=since_hours)
