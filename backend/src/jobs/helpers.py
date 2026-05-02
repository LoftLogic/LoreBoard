"""Shared utilities for Celery job lifecycle management."""
import asyncio
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import TypeVar

from sqlalchemy import update

from src.db.models import JobRecord, JobStatus
from src.db.session import SyncSessionLocal
from src.telemetry.tracer import get_logger

log = get_logger("jobs")
T = TypeVar("T")


def mark_job(job_id: uuid.UUID, **kwargs) -> None:
    """Update a JobRecord column set synchronously (for use inside Celery tasks)."""
    with SyncSessionLocal() as session:
        session.execute(update(JobRecord).where(JobRecord.id == job_id).values(**kwargs))
        session.commit()


def run_job(job_id: uuid.UUID, coro_fn: Callable[[], Awaitable[T]]) -> T:
    """
    Lifecycle wrapper for Celery tasks.

    Marks the job RUNNING, executes ``coro_fn`` via asyncio.run, then marks
    DONE or FAILED. Callers should catch the re-raised exception and call
    ``self.retry(exc=exc)`` if retries are desired.
    """
    mark_job(job_id, status=JobStatus.RUNNING, started_at=datetime.now(tz=timezone.utc))
    try:
        result = asyncio.run(coro_fn())
        mark_job(job_id, status=JobStatus.DONE, result=result, finished_at=datetime.now(tz=timezone.utc))
        return result
    except Exception as exc:
        log.error("job.failed", job_id=str(job_id), error=str(exc))
        mark_job(job_id, status=JobStatus.FAILED, error=str(exc), finished_at=datetime.now(tz=timezone.utc))
        raise
