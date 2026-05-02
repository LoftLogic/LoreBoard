"""Structured logging + tracing for all agent and job activity."""
from __future__ import annotations

import functools
import logging
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

import structlog
from structlog.typing import FilteringBoundLogger

from src.config import get_settings

_settings = get_settings()

# Context variables threaded through async call stacks
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_job_id: ContextVar[str] = ContextVar("job_id", default="")
_agent_type: ContextVar[str] = ContextVar("agent_type", default="")


def _add_context(logger: Any, method: str, event_dict: dict) -> dict:  # noqa: ANN401
    if tid := _trace_id.get():
        event_dict["trace_id"] = tid
    if jid := _job_id.get():
        event_dict["job_id"] = jid
    if at := _agent_type.get():
        event_dict["agent_type"] = at
    return event_dict


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_context,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer() if _settings.app_env != "development"
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, _settings.log_level)
        ),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "loreboard") -> FilteringBoundLogger:
    return structlog.get_logger(name)


# ---------------------------------------------------------------------------
# Trace context helpers
# ---------------------------------------------------------------------------

def new_trace_id() -> str:
    return uuid.uuid4().hex


def set_trace_context(*, trace_id: str | None = None, job_id: str = "", agent_type: str = "") -> str:
    tid = trace_id or new_trace_id()
    _trace_id.set(tid)
    _job_id.set(job_id)
    _agent_type.set(agent_type)
    return tid


# ---------------------------------------------------------------------------
# Decorator for automatic run telemetry
# ---------------------------------------------------------------------------

def trace_agent(agent_type: str) -> Callable:
    """Wraps an async agent `run` method: logs start/end, measures elapsed_ms."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = get_logger()
            tid = set_trace_context(agent_type=agent_type, job_id=kwargs.get("job_id", ""))
            log.info("agent.start", agent=agent_type, trace_id=tid)
            t0 = time.perf_counter()
            try:
                result = await fn(*args, **kwargs)
                elapsed = int((time.perf_counter() - t0) * 1000)
                log.info("agent.done", agent=agent_type, elapsed_ms=elapsed, tokens=getattr(result, "tokens_used", None))
                if hasattr(result, "elapsed_ms"):
                    result.elapsed_ms = elapsed
                return result
            except Exception as exc:
                elapsed = int((time.perf_counter() - t0) * 1000)
                log.error("agent.error", agent=agent_type, elapsed_ms=elapsed, error=str(exc))
                raise
        return wrapper
    return decorator


def trace_job(fn: Callable) -> Callable:
    """Wraps a Celery task: logs start/end with job context."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        log = get_logger()
        job_id = kwargs.get("job_id", args[0] if args else "unknown")
        set_trace_context(job_id=str(job_id))
        log.info("job.start", job_type=fn.__name__)
        t0 = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
            log.info("job.done", job_type=fn.__name__, elapsed_ms=int((time.perf_counter() - t0) * 1000))
            return result
        except Exception as exc:
            log.error("job.error", job_type=fn.__name__, error=str(exc))
            raise
    return wrapper
