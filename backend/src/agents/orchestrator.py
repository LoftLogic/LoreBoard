"""Orchestrator agent — decomposes a high-level directive into a job plan."""
from __future__ import annotations

import json

from src.context.assembler import Context
from src.output.schemas import AgentType, OrchestratorOutput, PlannedJob
from src.telemetry.tracer import trace_agent

from .base import Agent


class OrchestratorAgent(Agent):
    agent_type = AgentType.ORCHESTRATOR

    @trace_agent("orchestrator")
    async def _execute(self, context: Context, job_id: str) -> OrchestratorOutput:
        system = self._build_system_prompt(
            context,
            extra=(
                "You plan work for a creative writing analysis pipeline. "
                "Given a directive, produce a JSON list of jobs. "
                "Each job has: job_type (string), priority (1-10), payload (dict), depends_on (list of prior job indices).\n"
                "Valid job_types: analyze_chapter, extract_entities, check_consistency, summarize, autofill."
            ),
        )

        prompt = (
            f"Directive: {context.task_description}\n\n"
            f"Story has {len(context.chapters)} chapter(s). "
            f"Chapters: {[c.title or f'Chapter {c.order}' for c in context.chapters]}.\n\n"
            "Return ONLY a JSON array of job objects, no other text."
        )

        response = await self._client.messages.create(
            model="claude-haiku-4-5-20251001",  # fast model for planning
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        tokens = response.usage.input_tokens + response.usage.output_tokens

        try:
            jobs_data = json.loads(raw)
            planned = [PlannedJob(**j) for j in jobs_data]
        except Exception:
            # Graceful degradation: return empty plan, let caller retry or escalate
            planned = []

        return OrchestratorOutput(
            job_id=job_id,
            success=True,
            directive=context.task_description,
            planned_jobs=planned,
            tokens_used=tokens,
        )
