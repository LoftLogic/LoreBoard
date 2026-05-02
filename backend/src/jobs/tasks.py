"""Celery tasks — each delegates to an agent via the run_job lifecycle wrapper."""
from __future__ import annotations

import uuid

from celery import Task

from src.agents.orchestrator import OrchestratorAgent
from src.context.assembler import ContextAssembler, ScopeType, TaskScope
from src.db.session import AsyncSessionLocal
from src.jobs.helpers import run_job
from src.jobs.worker import celery_app
from src.memory.canonical import CanonicalMemory
from src.memory.working import WorkingMemory
from src.output.schemas import AgentType
from src.telemetry.tracer import get_logger, trace_job

log = get_logger("tasks")


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="src.jobs.tasks.run_orchestrator")
@trace_job
def run_orchestrator(self: Task, job_id: str, story_id: str, directive: str) -> dict:
    async def _core() -> dict:
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            working = await WorkingMemory.create(job_id)
            assembler = ContextAssembler(canonical, working=working)
            scope = TaskScope(scope_type=ScopeType.STORY, story_id=uuid.UUID(story_id))
            context = await assembler.assemble(AgentType.ORCHESTRATOR, directive, scope)
            output = await OrchestratorAgent().run(context, job_id)
            await session.commit()
        _dispatch_planned_jobs(output.planned_jobs, story_id)
        return output.model_dump(mode="json")

    try:
        return run_job(uuid.UUID(job_id), _core)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.analyze_chapter")
@trace_job
def analyze_chapter(self: Task, job_id: str, chapter_id: str) -> dict:
    async def _core() -> dict:
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            chapter = await canonical.get_chapter(uuid.UUID(chapter_id))
            if not chapter:
                raise ValueError(f"Chapter {chapter_id} not found")
            working = await WorkingMemory.create(job_id)
            assembler = ContextAssembler(canonical, working=working)
            scope = TaskScope(
                scope_type=ScopeType.CHAPTER,
                story_id=chapter.story_id,
                chapter_id=uuid.UUID(chapter_id),
            )
            _context = await assembler.assemble(AgentType.CHAPTER_ANALYZER, "Analyze this chapter", scope)
            # TODO: await ChapterAnalyzerAgent().run(_context, job_id)
            log.warning("analyze_chapter.not_implemented", chapter_id=chapter_id)
            await canonical.mark_chapter_analyzed(uuid.UUID(chapter_id))
            await session.commit()
        return {"chapter_id": chapter_id, "status": "stub"}

    try:
        return run_job(uuid.UUID(job_id), _core)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.extract_entities")
@trace_job
def extract_entities(self: Task, job_id: str, chapter_id: str) -> dict:
    async def _core() -> dict:
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            chapter = await canonical.get_chapter(uuid.UUID(chapter_id))
            if not chapter:
                raise ValueError(f"Chapter {chapter_id} not found")
            working = await WorkingMemory.create(job_id)
            assembler = ContextAssembler(canonical, working=working)
            scope = TaskScope(
                scope_type=ScopeType.CHAPTER,
                story_id=chapter.story_id,
                chapter_id=uuid.UUID(chapter_id),
            )
            _context = await assembler.assemble(AgentType.ENTITY_EXTRACTOR, "Extract entities", scope)
            # TODO: await EntityExtractorAgent().run(_context, job_id)
            log.warning("extract_entities.not_implemented", chapter_id=chapter_id)
            await session.commit()
        return {"chapter_id": chapter_id, "entities_found": 0, "status": "stub"}

    try:
        return run_job(uuid.UUID(job_id), _core)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.check_consistency")
@trace_job
def check_consistency(self: Task, job_id: str, story_id: str) -> dict:
    async def _core() -> dict:
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            working = await WorkingMemory.create(job_id)
            assembler = ContextAssembler(canonical, working=working)
            scope = TaskScope(scope_type=ScopeType.STORY, story_id=uuid.UUID(story_id))
            _context = await assembler.assemble(AgentType.CONSISTENCY_CHECKER, "Check consistency", scope)
            # TODO: await ConsistencyCheckerAgent().run(_context, job_id)
            log.warning("check_consistency.not_implemented", story_id=story_id)
            await session.commit()
        return {"story_id": story_id, "issues_found": 0, "status": "stub"}

    try:
        return run_job(uuid.UUID(job_id), _core)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="src.jobs.tasks.autofill")
@trace_job
def autofill(self: Task, job_id: str, chapter_id: str, placeholder: str, context_window: str) -> dict:
    async def _core() -> dict:
        async with AsyncSessionLocal() as session:
            canonical = CanonicalMemory(session)
            chapter = await canonical.get_chapter(uuid.UUID(chapter_id))
            if not chapter:
                raise ValueError(f"Chapter {chapter_id} not found")
            working = await WorkingMemory.create(job_id)
            assembler = ContextAssembler(canonical, working=working)
            scope = TaskScope(
                scope_type=ScopeType.CHAPTER,
                story_id=chapter.story_id,
                chapter_id=uuid.UUID(chapter_id),
            )
            _context = await assembler.assemble(AgentType.AUTOFILL, f"Fill placeholder: {placeholder}", scope, semantic_query=placeholder)
            # TODO: await AutofillAgent().run(_context, job_id)
            log.warning("autofill.not_implemented", chapter_id=chapter_id, placeholder=placeholder)
            await session.commit()
        return {"placeholder": placeholder, "suggestions": [], "status": "stub"}

    try:
        return run_job(uuid.UUID(job_id), _core)
    except Exception as exc:
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _dispatch_planned_jobs(planned_jobs, story_id: str) -> None:
    """Dispatch orchestrator-planned jobs to Celery queues."""
    task_map = {
        "analyze_chapter": analyze_chapter,
        "extract_entities": extract_entities,
        "check_consistency": check_consistency,
        "autofill": autofill,
    }
    for job in planned_jobs:
        task_fn = task_map.get(job.job_type)
        if not task_fn:
            log.warning("dispatch.unknown_job_type", job_type=job.job_type)
            continue
        new_job_id = str(uuid.uuid4())
        queue = "high" if job.priority >= 8 else "default"
        task_fn.apply_async(
            kwargs={"job_id": new_job_id, "story_id": story_id, **job.payload},
            queue=queue,
        )
        log.info("job.dispatched", job_type=job.job_type, job_id=new_job_id, queue=queue)
