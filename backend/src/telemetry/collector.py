"""Instrumented Anthropic client — records every LLM API call to the database."""
from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

import anthropic
from anthropic.types import Message

from src.config import get_settings
from src.telemetry.tracer import get_logger

log = get_logger("telemetry.collector")
_settings = get_settings()


async def _persist_call(
    run_id: uuid.UUID,
    kwargs: dict[str, Any],
    response: Message,
    elapsed_ms: int,
) -> None:
    """Persist a single LlmCall row. Errors are logged, never raised to the caller."""
    # Local imports to avoid circular dependency at module load time
    from src.db.models import LlmCall
    from src.db.session import AsyncSessionLocal

    try:
        tool_calls = [
            {"id": b.id, "name": b.name, "input": b.input}
            for b in response.content
            if b.type == "tool_use"
        ]
        output_content = [
            {"type": b.type, "text": b.text} if b.type == "text"
            else {"type": b.type, "name": getattr(b, "name", None)}
            for b in response.content
        ]
        call = LlmCall(
            run_id=run_id,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=elapsed_ms,
            stop_reason=response.stop_reason,
            tool_calls=tool_calls,
            input_messages={
                "system": kwargs.get("system", ""),
                "messages": kwargs.get("messages", []),
            },
            output_content=output_content,
        )
        async with AsyncSessionLocal() as session:
            session.add(call)
            await session.commit()
    except Exception as exc:
        log.warning("telemetry.persist_failed", error=str(exc))


class _MessagesProxy:
    """Mirrors client.messages, intercepting create() to record each call."""

    def __init__(self, real_messages: Any, run_id_ref: list[uuid.UUID | None]) -> None:
        self._real = real_messages
        self._run_id_ref = run_id_ref

    async def create(self, **kwargs: Any) -> Message:
        t0 = time.perf_counter()
        response: Message = await self._real.create(**kwargs)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        if (run_id := self._run_id_ref[0]) is not None:
            asyncio.create_task(_persist_call(run_id, kwargs, response, elapsed_ms))

        return response


class InstrumentedAnthropic:
    """Drop-in replacement for AsyncAnthropic that instruments every messages.create() call."""

    def __init__(self) -> None:
        self._real = anthropic.AsyncAnthropic(api_key=_settings.anthropic_api_key)
        self._run_id_ref: list[uuid.UUID | None] = [None]
        self.messages = _MessagesProxy(self._real.messages, self._run_id_ref)

    def set_run_id(self, run_id: uuid.UUID | None) -> None:
        self._run_id_ref[0] = run_id
