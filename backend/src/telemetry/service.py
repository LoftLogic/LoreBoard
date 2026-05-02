"""Telemetry query service — aggregates and retrieves run and LLM call data."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import AgentRun, LlmCall


def _run_summary(run: AgentRun) -> dict[str, Any]:
    return {
        "id": str(run.id),
        "job_id": run.job_id,
        "agent_type": run.agent_type,
        "status": run.status,
        "tokens_used": run.tokens_used or 0,
        "elapsed_ms": run.elapsed_ms or 0,
        "error": run.error,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "llm_call_count": len(run.llm_calls),
    }


def _call_detail(call: LlmCall) -> dict[str, Any]:
    return {
        "id": str(call.id),
        "model": call.model,
        "input_tokens": call.input_tokens,
        "output_tokens": call.output_tokens,
        "latency_ms": call.latency_ms,
        "stop_reason": call.stop_reason,
        "tool_calls": call.tool_calls,
        "input_messages": call.input_messages,
        "output_content": call.output_content,
        "created_at": call.created_at.isoformat() if call.created_at else None,
    }


class TelemetryService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_runs(
        self,
        agent_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        q = (
            select(AgentRun)
            .options(selectinload(AgentRun.llm_calls))
            .order_by(AgentRun.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if agent_type:
            q = q.where(AgentRun.agent_type == agent_type)
        rows = (await self._db.execute(q)).scalars().all()
        return [_run_summary(r) for r in rows]

    async def get_run_detail(self, run_id: uuid.UUID) -> dict[str, Any] | None:
        result = await self._db.execute(
            select(AgentRun)
            .options(selectinload(AgentRun.llm_calls))
            .where(AgentRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if run is None:
            return None
        return {
            **_run_summary(run),
            "input_data": run.input_data,
            "output_data": run.output_data,
            "llm_calls": [_call_detail(c) for c in run.llm_calls],
        }

    async def get_summary(self, since_hours: int = 24) -> dict[str, Any]:
        since = datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)
        rows = (
            await self._db.execute(
                select(
                    AgentRun.agent_type,
                    func.count(AgentRun.id).label("run_count"),
                    func.coalesce(func.sum(AgentRun.tokens_used), 0).label("total_tokens"),
                    func.coalesce(func.avg(AgentRun.elapsed_ms), 0).label("avg_latency_ms"),
                    func.sum(case((AgentRun.status == "failed", 1), else_=0)).label("error_count"),
                )
                .where(AgentRun.started_at >= since)
                .group_by(AgentRun.agent_type)
            )
        ).all()

        by_agent = [
            {
                "agent_type": r.agent_type,
                "run_count": r.run_count,
                "total_tokens": int(r.total_tokens),
                "avg_latency_ms": int(r.avg_latency_ms),
                "error_count": int(r.error_count),
            }
            for r in rows
        ]
        return {
            "total_runs": sum(r["run_count"] for r in by_agent),
            "total_tokens": sum(r["total_tokens"] for r in by_agent),
            "error_count": sum(r["error_count"] for r in by_agent),
            "since_hours": since_hours,
            "by_agent": by_agent,
        }
