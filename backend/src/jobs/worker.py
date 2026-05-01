"""Celery application and queue configuration."""
from celery import Celery

from src.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "loreboard",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
    include=["src.jobs.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,          # only ack after task completes (safe for retries)
    worker_prefetch_multiplier=1, # one task at a time per worker for long-running jobs
    task_routes={
        "src.jobs.tasks.analyze_chapter": {"queue": "default"},
        "src.jobs.tasks.extract_entities": {"queue": "default"},
        "src.jobs.tasks.check_consistency": {"queue": "default"},
        "src.jobs.tasks.run_orchestrator": {"queue": "high"},
        "src.jobs.tasks.autofill": {"queue": "high"},
    },
    task_queues={
        "high": {"exchange": "high", "routing_key": "high"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low": {"exchange": "low", "routing_key": "low"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    # Retry policy for transient failures
    task_annotations={
        "*": {
            "max_retries": 3,
            "default_retry_delay": 10,
        }
    },
)
