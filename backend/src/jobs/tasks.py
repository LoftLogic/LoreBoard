"""Celery tasks. Each task updates JobRecord state and delegates to an agent."""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from celery import Task
from sqlalchemy import update

from src.context.assembler import ContextAssembler, ScopeType, TaskScope
from src.db.models import AnalysisState, Chapter, JobRecord, JobStatus
from src.db.session import AsyncSessionLocal, SyncSessionLocal
from src.jobs.worker import celery_app
from src.memory.canonical import CanonicalMemory
from src.memory.working import WorkingMemory
from src.output.schemas import AgentType
from src.telemetry.tracer import get_logger, trace_job

log = get_logger("tasks")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    """Run an async coroutine from sync Celery task context."""
    return asyncio.get_event_loop().run_until_complete(coro)


def _update_job(session, job_id: uuid.UUID, **kwargs) -> None:
    session.execute(
        update(JobRecord).where(JobRecord.id == job_id).values(**kwargs)
    )
    session.commit()


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="src.jobs.tasks.run_orchestrator")
@trace_job
def run_orchestrator(self: Task, job_id: str, story_id: str, directive: str) -> dict:
    from src.agents.orchestrator import OrchestratorAgent

    jid = uuid.UUID(job_id)
    sid = uuid.UUID(story_id)

    with SyncSessionLocal() as session:
        _update_job(session, jid, status=JobStatus.RUNNING, started_at=datetime.now(tz=timezone.utc))

    async def _run_async():
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            working = await WorkingMemory.create(job_id)
            assembler = ContextAssembler(canonical, working=working)
            scope = TaskScope(scope_type=ScopeType.STORY, story_id=sid)
            context = await assembler.assemble(AgentType.ORCHESTRATOR, directive, scope)
            agent = OrchestratorAgent()
            output = await agent.run(context, job_id)
            await session.commit()
            return output

    try:
        output = _run(_run_async())
        result = output.model_dump(mode="json")
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.DONE, result=result, finished_at=datetime.now(tz=timezone.utc))
        # Dispatch planned jobs
        _dispatch_planned_jobs(output.planned_jobs, story_id)
        return result
    except Exception as exc:
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.FAILED, error=str(exc), finished_at=datetime.now(tz=timezone.utc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.analyze_chapter")
@trace_job
def analyze_chapter(self: Task, job_id: str, chapter_id: str) -> dict:
    from src.agents.base import Agent  # imported here to avoid circular at module load

    jid = uuid.UUID(job_id)
    cid = uuid.UUID(chapter_id)

    with SyncSessionLocal() as session:
        _update_job(session, jid, status=JobStatus.RUNNING, started_at=datetime.now(tz=timezone.utc))

    async def _run_async():
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            chapter = await canonical.get_chapter(cid)
            if not chapter:
                raise ValueError(f"Chapter {chapter_id} not found")

            working = await WorkingMemory.create(job_id)
            assembler = ContextAssembler(canonical, working=working)
            scope = TaskScope(scope_type=ScopeType.CHAPTER, story_id=chapter.story_id, chapter_id=cid)

            from src.output.schemas import AgentType as AT
            context = await assembler.assemble(AT.CHAPTER_ANALYZER, "Analyze this chapter", scope)

            # Chapter analyzer agent (stubbed — implement in agents/chapter_analyzer.py)
            # output = await ChapterAnalyzerAgent().run(context, job_id)

            await canonical.mark_chapter_analyzed(cid)
            await session.commit()
            return {"chapter_id": chapter_id, "status": "analyzed"}

    try:
        result = _run(_run_async())
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.DONE, result=result, finished_at=datetime.now(tz=timezone.utc))
        return result
    except Exception as exc:
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.FAILED, error=str(exc), finished_at=datetime.now(tz=timezone.utc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.extract_entities")
@trace_job
def extract_entities(self: Task, job_id: str, chapter_id: str) -> dict:
    jid = uuid.UUID(job_id)
    cid = uuid.UUID(chapter_id)

    with SyncSessionLocal() as session:
        _update_job(session, jid, status=JobStatus.RUNNING, started_at=datetime.now(tz=timezone.utc))

    async def _run_async():
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            chapter = await canonical.get_chapter(cid)
            if not chapter:
                raise ValueError(f"Chapter {chapter_id} not found")
            # EntityExtractorAgent().run(...) goes here
            await session.commit()
            return {"chapter_id": chapter_id, "entities_found": 0}

    try:
        result = _run(_run_async())
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.DONE, result=result, finished_at=datetime.now(tz=timezone.utc))
        return result
    except Exception as exc:
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.FAILED, error=str(exc), finished_at=datetime.now(tz=timezone.utc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.check_consistency")
@trace_job
def check_consistency(self: Task, job_id: str, story_id: str) -> dict:
    jid = uuid.UUID(job_id)
    with SyncSessionLocal() as session:
        _update_job(session, jid, status=JobStatus.RUNNING, started_at=datetime.now(tz=timezone.utc))
    try:
        # ConsistencyCheckerAgent().run(...) goes here
        result = {"story_id": story_id, "issues_found": 0}
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.DONE, result=result, finished_at=datetime.now(tz=timezone.utc))
        return result
    except Exception as exc:
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.FAILED, error=str(exc), finished_at=datetime.now(tz=timezone.utc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.autofill")
@trace_job
def autofill(self: Task, job_id: str, chapter_id: str, placeholder: str, context_window: str) -> dict:
    jid = uuid.UUID(job_id)
    with SyncSessionLocal() as session:
        _update_job(session, jid, status=JobStatus.RUNNING, started_at=datetime.now(tz=timezone.utc))
    try:
        # AutofillAgent().run(...) goes here
        result = {"placeholder": placeholder, "suggestions": []}
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.DONE, result=result, finished_at=datetime.now(tz=timezone.utc))
        return result
    except Exception as exc:
        with SyncSessionLocal() as session:
            _update_job(session, jid, status=JobStatus.FAILED, error=str(exc), finished_at=datetime.now(tz=timezone.utc))
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _dispatch_planned_jobs(planned_jobs, story_id: str) -> None:
    """Dispatch orchestrator-planned jobs to Celery."""
    dispatched: list[str] = []
    for i, job in enumerate(planned_jobs):
        new_job_id = str(uuid.uuid4())
        jtype = job.job_type
        payload = {**job.payload, "story_id": story_id, "job_id": new_job_id}

        task_map = {
            "analyze_chapter": analyze_chapter,
            "extract_entities": extract_entities,
            "check_consistency": check_consistency,
            "autofill": autofill,
        }

        task_fn = task_map.get(jtype)
        if task_fn:
            queue = "high" if job.priority >= 8 else "default"
            task_fn.apply_async(kwargs=payload, queue=queue)
            dispatched.append(new_job_id)
            log.info("job.dispatched", job_type=jtype, job_id=new_job_id)
