"""Feedback and calibration loop — writers can rate runs and force re-calibration."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import AgentRun, FeedbackEntry
from src.telemetry.tracer import get_logger

log = get_logger("calibration")


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class FeedbackRequest(BaseModel):
    run_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    notes: str | None = None
    # Optional structured overrides the writer wants to enforce
    calibration_data: dict = Field(default_factory=dict)


class CalibrationContext(BaseModel):
    """Aggregated calibration context injected into future prompts for this agent type."""
    agent_type: str
    avg_rating: float
    low_rated_patterns: list[str] = Field(default_factory=list)
    writer_overrides: list[dict] = Field(default_factory=list)
    sample_count: int = 0


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class CalibrationService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def record_feedback(self, req: FeedbackRequest) -> FeedbackEntry:
        entry = FeedbackEntry(
            run_id=req.run_id,
            rating=req.rating,
            notes=req.notes,
            calibration_data=req.calibration_data,
        )
        self._s.add(entry)
        await self._s.flush()
        log.info("feedback.recorded", run_id=str(req.run_id), rating=req.rating)
        return entry

    async def force_calibration(self, run_id: uuid.UUID) -> None:
        """Mark feedback entries for this run as needing calibration application."""
        await self._s.execute(
            update(FeedbackEntry)
            .where(FeedbackEntry.run_id == run_id)
            .values(calibration_applied=False)
        )
        log.info("calibration.forced", run_id=str(run_id))

    async def get_calibration_context(self, agent_type: str, limit: int = 50) -> CalibrationContext:
        """
        Build a calibration context block from recent feedback for this agent type.
        Injected into the system prompt so the agent self-corrects based on past ratings.
        """
        result = await self._s.execute(
            select(FeedbackEntry, AgentRun)
            .join(AgentRun, AgentRun.id == FeedbackEntry.run_id)
            .where(AgentRun.agent_type == agent_type)
            .order_by(FeedbackEntry.created_at.desc())
            .limit(limit)
        )
        rows = result.all()

        if not rows:
            return CalibrationContext(agent_type=agent_type, avg_rating=0.0)

        ratings = [fb.rating for fb, _ in rows if fb.rating]
        avg = sum(ratings) / len(ratings) if ratings else 0.0

        low_patterns: list[str] = []
        overrides: list[dict] = []
        for fb, _ in rows:
            if fb.rating and fb.rating <= 2 and fb.notes:
                low_patterns.append(fb.notes)
            if fb.calibration_data:
                overrides.append(fb.calibration_data)  # type: ignore[arg-type]

        return CalibrationContext(
            agent_type=agent_type,
            avg_rating=round(avg, 2),
            low_rated_patterns=low_patterns[:10],
            writer_overrides=overrides[:10],
            sample_count=len(rows),
        )

    def calibration_to_prompt_block(self, ctx: CalibrationContext) -> str:
        if ctx.sample_count == 0:
            return ""
        lines = [f"[Calibration: avg rating {ctx.avg_rating}/5 over {ctx.sample_count} runs]"]
        if ctx.low_rated_patterns:
            lines.append("Avoid patterns the writer disliked:")
            lines.extend(f"  - {p}" for p in ctx.low_rated_patterns)
        if ctx.writer_overrides:
            lines.append("Writer-specified overrides:")
            for o in ctx.writer_overrides:
                lines.extend(f"  {k}: {v}" for k, v in o.items())
        return "\n".join(lines)
