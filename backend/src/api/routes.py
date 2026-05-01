"""FastAPI route definitions."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Chapter, JobRecord, JobStatus, Story
from src.db.session import get_async_session
from src.feedback.calibration import CalibrationService, FeedbackRequest
from src.jobs.tasks import analyze_chapter, check_consistency, extract_entities, run_orchestrator
from src.memory.canonical import CanonicalMemory
from src.telemetry.tracer import get_logger

log = get_logger("api")
router = APIRouter()
Db = Annotated[AsyncSession, Depends(get_async_session)]


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------

class StoryCreate(BaseModel):
    title: str
    meta: dict = Field(default_factory=dict)


class StoryResponse(BaseModel):
    id: uuid.UUID
    title: str
    meta: dict

    model_config = {"from_attributes": True}


@router.post("/stories", response_model=StoryResponse, status_code=201)
async def create_story(body: StoryCreate, db: Db):
    canonical = CanonicalMemory(db)
    story = await canonical.create_story(body.title, body.meta)
    await db.commit()
    return story


@router.get("/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: uuid.UUID, db: Db):
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(404, "Story not found")
    return story


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

class ChapterCreate(BaseModel):
    story_id: uuid.UUID
    order: int
    title: str | None = None
    content: str = ""


class ChapterContentUpdate(BaseModel):
    content: str


class ChapterOverrideSet(BaseModel):
    key: str
    value: str


class ChapterResponse(BaseModel):
    id: uuid.UUID
    story_id: uuid.UUID
    order: int
    title: str | None
    analysis_state: str
    content: str

    model_config = {"from_attributes": True}


@router.post("/chapters", response_model=ChapterResponse, status_code=201)
async def create_chapter(body: ChapterCreate, db: Db):
    chapter = Chapter(
        story_id=body.story_id,
        order=body.order,
        title=body.title,
        content=body.content,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter


@router.patch("/chapters/{chapter_id}/content")
async def update_chapter_content(chapter_id: uuid.UUID, body: ChapterContentUpdate, db: Db):
    canonical = CanonicalMemory(db)
    chapter = await canonical.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(404, "Chapter not found")
    await canonical.upsert_chapter_content(chapter_id, body.content)
    await db.commit()
    return {"status": "ok", "analysis_state": "stale"}


@router.post("/chapters/{chapter_id}/overrides")
async def set_chapter_override(chapter_id: uuid.UUID, body: ChapterOverrideSet, db: Db):
    canonical = CanonicalMemory(db)
    await canonical.set_override(chapter_id, body.key, body.value)
    await db.commit()
    return {"status": "ok"}


@router.get("/chapters/{chapter_id}/overrides")
async def get_chapter_overrides(chapter_id: uuid.UUID, db: Db):
    canonical = CanonicalMemory(db)
    overrides = await canonical.get_overrides(chapter_id)
    return {"overrides": overrides}


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class OrchestratorJobRequest(BaseModel):
    story_id: uuid.UUID
    directive: str
    priority: int = 5


class JobStatusResponse(BaseModel):
    id: uuid.UUID
    job_type: str
    status: str
    priority: int
    result: dict | None
    error: str | None

    model_config = {"from_attributes": True}


@router.post("/jobs/orchestrate", status_code=202)
async def submit_orchestrator_job(body: OrchestratorJobRequest, db: Db):
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
    log.info("job.submitted", job_id=str(job.id), type="orchestrate")
    return {"job_id": str(job.id), "celery_task_id": task.id}


@router.post("/jobs/analyze-chapter/{chapter_id}", status_code=202)
async def submit_analyze_chapter(chapter_id: uuid.UUID, db: Db):
    job = JobRecord(job_type="analyze_chapter", chapter_id=chapter_id, payload={})
    db.add(job)
    await db.commit()
    await db.refresh(job)

    task = analyze_chapter.apply_async(
        kwargs={"job_id": str(job.id), "chapter_id": str(chapter_id)},
        queue="default",
    )
    job.celery_task_id = task.id
    await db.commit()
    return {"job_id": str(job.id)}


@router.post("/jobs/extract-entities/{chapter_id}", status_code=202)
async def submit_extract_entities(chapter_id: uuid.UUID, db: Db):
    job = JobRecord(job_type="extract_entities", chapter_id=chapter_id, payload={})
    db.add(job)
    await db.commit()
    await db.refresh(job)

    task = extract_entities.apply_async(
        kwargs={"job_id": str(job.id), "chapter_id": str(chapter_id)},
        queue="default",
    )
    job.celery_task_id = task.id
    await db.commit()
    return {"job_id": str(job.id)}


@router.post("/jobs/check-consistency/{story_id}", status_code=202)
async def submit_consistency_check(story_id: uuid.UUID, db: Db):
    job = JobRecord(job_type="check_consistency", story_id=story_id, payload={})
    db.add(job)
    await db.commit()
    await db.refresh(job)

    task = check_consistency.apply_async(
        kwargs={"job_id": str(job.id), "story_id": str(story_id)},
        queue="default",
    )
    job.celery_task_id = task.id
    await db.commit()
    return {"job_id": str(job.id)}


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: uuid.UUID, db: Db):
    result = await db.execute(select(JobRecord).where(JobRecord.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/jobs/story/{story_id}")
async def list_story_jobs(story_id: uuid.UUID, db: Db):
    result = await db.execute(
        select(JobRecord)
        .where(JobRecord.story_id == story_id)
        .order_by(JobRecord.created_at.desc())
        .limit(50)
    )
    jobs = result.scalars().all()
    return [
        {"id": str(j.id), "job_type": j.job_type, "status": j.status, "priority": j.priority}
        for j in jobs
    ]


# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------

@router.get("/stories/{story_id}/flags")
async def get_story_flags(story_id: uuid.UUID, resolved: bool = False, db: Db = None):
    from src.db.models import StoryFlag
    result = await db.execute(
        select(StoryFlag).where(
            StoryFlag.story_id == story_id,
            StoryFlag.resolved == resolved,
        )
    )
    flags = result.scalars().all()
    return [
        {
            "id": str(f.id),
            "flag_type": f.flag_type,
            "message": f.message,
            "severity": f.severity,
            "chapter_id": str(f.chapter_id) if f.chapter_id else None,
        }
        for f in flags
    ]


@router.patch("/flags/{flag_id}/resolve")
async def resolve_flag(flag_id: uuid.UUID, db: Db):
    canonical = CanonicalMemory(db)
    await canonical.resolve_flag(flag_id)
    await db.commit()
    return {"status": "resolved"}


# ---------------------------------------------------------------------------
# Feedback & Calibration
# ---------------------------------------------------------------------------

@router.post("/feedback", status_code=201)
async def submit_feedback(body: FeedbackRequest, db: Db):
    svc = CalibrationService(db)
    entry = await svc.record_feedback(body)
    await db.commit()
    return {"feedback_id": str(entry.id)}


@router.post("/feedback/force-calibration/{run_id}")
async def force_calibration(run_id: uuid.UUID, db: Db):
    svc = CalibrationService(db)
    await svc.force_calibration(run_id)
    await db.commit()
    return {"status": "calibration_queued"}


@router.get("/feedback/calibration/{agent_type}")
async def get_calibration(agent_type: str, db: Db):
    svc = CalibrationService(db)
    ctx = await svc.get_calibration_context(agent_type)
    return ctx.model_dump()
