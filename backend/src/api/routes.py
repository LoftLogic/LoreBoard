"""FastAPI route handlers. Request/response schemas live in api/schemas.py."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    ChapterContentUpdate,
    ChapterCreate,
    ChapterOverrideSet,
    ChapterResponse,
    JobStatusResponse,
    OrchestratorJobRequest,
    StoryCreate,
    StoryResponse,
)
from src.db.models import Chapter, JobRecord, Story, StoryFlag
from src.db.session import get_async_session
from src.feedback.calibration import CalibrationService, FeedbackRequest
from src.jobs.tasks import analyze_chapter, check_consistency, extract_entities, run_orchestrator
from src.memory.canonical import CanonicalMemory
from src.telemetry.tracer import get_logger

log = get_logger("api")
router = APIRouter()
Db = Annotated[AsyncSession, Depends(get_async_session)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_or_404(db: AsyncSession, model, id_: uuid.UUID):
    result = await db.execute(select(model).where(model.id == id_))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, f"{model.__name__} not found")
    return obj


async def _submit_job(
    db: AsyncSession,
    job_type: str,
    task_fn,
    task_kwargs: dict,
    queue: str,
    story_id: uuid.UUID | None = None,
    chapter_id: uuid.UUID | None = None,
) -> dict:
    """Create a JobRecord, dispatch to Celery, attach celery_task_id."""
    job = JobRecord(job_type=job_type, story_id=story_id, chapter_id=chapter_id, payload={})
    db.add(job)
    await db.commit()
    await db.refresh(job)
    task = task_fn.apply_async(kwargs={"job_id": str(job.id), **task_kwargs}, queue=queue)
    job.celery_task_id = task.id
    await db.commit()
    log.info("job.submitted", job_id=str(job.id), job_type=job_type)
    return {"job_id": str(job.id)}


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------

@router.post("/stories", response_model=StoryResponse, status_code=201)
async def create_story(body: StoryCreate, db: Db) -> StoryResponse:
    canonical = CanonicalMemory(db)
    story = await canonical.create_story(body.title, body.meta)
    await db.commit()
    return story  # type: ignore[return-value]


@router.get("/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: uuid.UUID, db: Db) -> StoryResponse:
    return await _get_or_404(db, Story, story_id)


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

@router.post("/chapters", response_model=ChapterResponse, status_code=201)
async def create_chapter(body: ChapterCreate, db: Db) -> ChapterResponse:
    chapter = Chapter(
        story_id=body.story_id,
        order=body.order,
        title=body.title,
        content=body.content,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter  # type: ignore[return-value]


@router.patch("/chapters/{chapter_id}/content")
async def update_chapter_content(chapter_id: uuid.UUID, body: ChapterContentUpdate, db: Db) -> dict:
    canonical = CanonicalMemory(db)
    await _get_or_404(db, Chapter, chapter_id)
    await canonical.upsert_chapter_content(chapter_id, body.content)
    await db.commit()
    return {"status": "ok", "analysis_state": "stale"}


@router.post("/chapters/{chapter_id}/overrides")
async def set_chapter_override(chapter_id: uuid.UUID, body: ChapterOverrideSet, db: Db) -> dict:
    canonical = CanonicalMemory(db)
    await canonical.set_override(chapter_id, body.key, body.value)
    await db.commit()
    return {"status": "ok"}


@router.get("/chapters/{chapter_id}/overrides")
async def get_chapter_overrides(chapter_id: uuid.UUID, db: Db) -> dict:
    canonical = CanonicalMemory(db)
    return {"overrides": await canonical.get_overrides(chapter_id)}


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@router.post("/jobs/orchestrate", status_code=202)
async def submit_orchestrator_job(body: OrchestratorJobRequest, db: Db) -> dict:
    job = JobRecord(
        job_type="run_orchestrator",
        priority=body.priority,
        story_id=body.story_id,
        payload={"directive": body.directive},
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    task = run_orchestrator.apply_async(
        kwargs={"job_id": str(job.id), "story_id": str(body.story_id), "directive": body.directive},
        queue="high",
    )
    job.celery_task_id = task.id
    await db.commit()
    log.info("job.submitted", job_id=str(job.id), job_type="orchestrate")
    return {"job_id": str(job.id), "celery_task_id": task.id}


@router.post("/jobs/analyze-chapter/{chapter_id}", status_code=202)
async def submit_analyze_chapter(chapter_id: uuid.UUID, db: Db) -> dict:
    return await _submit_job(
        db, "analyze_chapter", analyze_chapter,
        {"chapter_id": str(chapter_id)}, "default",
        chapter_id=chapter_id,
    )


@router.post("/jobs/extract-entities/{chapter_id}", status_code=202)
async def submit_extract_entities(chapter_id: uuid.UUID, db: Db) -> dict:
    return await _submit_job(
        db, "extract_entities", extract_entities,
        {"chapter_id": str(chapter_id)}, "default",
        chapter_id=chapter_id,
    )


@router.post("/jobs/check-consistency/{story_id}", status_code=202)
async def submit_consistency_check(story_id: uuid.UUID, db: Db) -> dict:
    return await _submit_job(
        db, "check_consistency", check_consistency,
        {"story_id": str(story_id)}, "default",
        story_id=story_id,
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: uuid.UUID, db: Db) -> JobStatusResponse:
    return await _get_or_404(db, JobRecord, job_id)


@router.get("/jobs/story/{story_id}")
async def list_story_jobs(story_id: uuid.UUID, db: Db) -> list[dict]:
    result = await db.execute(
        select(JobRecord)
        .where(JobRecord.story_id == story_id)
        .order_by(JobRecord.created_at.desc())
        .limit(50)
    )
    return [
        {"id": str(j.id), "job_type": j.job_type, "status": j.status, "priority": j.priority}
        for j in result.scalars().all()
    ]


# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------

@router.get("/stories/{story_id}/flags")
async def get_story_flags(story_id: uuid.UUID, db: Db, resolved: bool = False) -> list[dict]:
    result = await db.execute(
        select(StoryFlag).where(
            StoryFlag.story_id == story_id,
            StoryFlag.resolved == resolved,
        )
    )
    return [
        {
            "id": str(f.id),
            "flag_type": f.flag_type,
            "message": f.message,
            "severity": f.severity,
            "chapter_id": str(f.chapter_id) if f.chapter_id else None,
        }
        for f in result.scalars().all()
    ]


@router.patch("/flags/{flag_id}/resolve")
async def resolve_flag(flag_id: uuid.UUID, db: Db) -> dict:
    canonical = CanonicalMemory(db)
    await canonical.resolve_flag(flag_id)
    await db.commit()
    return {"status": "resolved"}


# ---------------------------------------------------------------------------
# Feedback & Calibration
# ---------------------------------------------------------------------------

@router.post("/feedback", status_code=201)
async def submit_feedback(body: FeedbackRequest, db: Db) -> dict:
    svc = CalibrationService(db)
    entry = await svc.record_feedback(body)
    await db.commit()
    return {"feedback_id": str(entry.id)}


@router.post("/feedback/force-calibration/{run_id}")
async def force_calibration(run_id: uuid.UUID, db: Db) -> dict:
    svc = CalibrationService(db)
    await svc.force_calibration(run_id)
    await db.commit()
    return {"status": "calibration_queued"}


@router.get("/feedback/calibration/{agent_type}")
async def get_calibration(agent_type: str, db: Db) -> dict:
    svc = CalibrationService(db)
    ctx = await svc.get_calibration_context(agent_type)
    return ctx.model_dump()
