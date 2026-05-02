"""Abstract base agent. All agents subclass this."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import update

from src.config import get_settings
from src.context.assembler import Context
from src.db.models import AgentRun
from src.db.session import AsyncSessionLocal
from src.output.schemas import AgentOutput, AgentType
from src.telemetry.collector import InstrumentedAnthropic
from src.telemetry.tracer import get_logger, trace_agent

log = get_logger("agents")
_settings = get_settings()


class Agent(ABC):
    agent_type: AgentType

    def __init__(self) -> None:
        self._client = InstrumentedAnthropic()

    @abstractmethod
    async def _execute(self, context: Context, job_id: str) -> AgentOutput:
        """Core agent logic. Subclasses implement this."""
        ...

    async def run(self, context: Context, job_id: str) -> AgentOutput:
        """Creates an AgentRun record, instruments the client, then delegates to _execute."""
        run_id = uuid.uuid4()
        async with AsyncSessionLocal() as session:
            run = AgentRun(
                id=run_id,
                job_id=job_id,
                agent_type=self.agent_type.value,
                input_data=context.to_prompt_dict(),
                status="running",
                started_at=datetime.now(tz=timezone.utc),
            )
            session.add(run)
            await session.commit()

        self._client.set_run_id(run_id)
        try:
            output = await self._execute(context, job_id)
            output.run_id = run_id

            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(AgentRun)
                    .where(AgentRun.id == run_id)
                    .values(
                        output_data=output.model_dump(mode="json"),
                        status="done",
                        finished_at=datetime.now(tz=timezone.utc),
                        tokens_used=output.tokens_used,
                        elapsed_ms=output.elapsed_ms,
                    )
                )
                await session.commit()
            return output

        except Exception as exc:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(AgentRun)
                    .where(AgentRun.id == run_id)
                    .values(
                        status="failed",
                        error=str(exc),
                        finished_at=datetime.now(tz=timezone.utc),
                    )
                )
                await session.commit()
            raise
        finally:
            self._client.set_run_id(None)

    def _build_system_prompt(self, context: Context, extra: str = "") -> str:
        ctx_dict = context.to_prompt_dict()
        entities_summary = ", ".join(e["name"] for e in ctx_dict.get("entities", []))
        overrides = ctx_dict.get("overrides", {})

        lines = [
            f"You are a {self.agent_type.value} agent for a creative writing assistant.",
            f"Story: {ctx_dict.get('story_title', 'Unknown')}",
            f"Task: {ctx_dict.get('task', '')}",
        ]
        if entities_summary:
            lines.append(f"Known entities: {entities_summary}")
        if overrides:
            lines.append(f"Writer overrides in effect: {overrides}")
        if extra:
            lines.append(extra)
        return "\n".join(lines)
