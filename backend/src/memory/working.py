"""Working memory — fast, ephemeral, Redis-backed. Scoped to a job or session."""
from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from src.config import get_settings

_settings = get_settings()


class WorkingMemory:
    """
    Key-value store with TTL, namespaced by job_id.
    Values are JSON-serialisable dicts or primitives.
    """

    def __init__(self, job_id: str, client: aioredis.Redis | None = None) -> None:
        self._job_id = job_id
        self._client = client
        self._ttl = _settings.working_memory_ttl
        self._local: dict[str, Any] = {}   # in-process fallback when Redis unavailable

    @classmethod
    async def create(cls, job_id: str) -> "WorkingMemory":
        try:
            client = aioredis.from_url(_settings.redis_url, decode_responses=True)
            await client.ping()
            return cls(job_id, client)
        except Exception:
            return cls(job_id, None)

    def _key(self, field: str) -> str:
        return f"wm:{self._job_id}:{field}"

    async def set(self, field: str, value: Any) -> None:
        serialized = json.dumps(value)
        if self._client:
            await self._client.setex(self._key(field), self._ttl, serialized)
        else:
            self._local[field] = value

    async def get(self, field: str, default: Any = None) -> Any:
        if self._client:
            raw = await self._client.get(self._key(field))
            return json.loads(raw) if raw is not None else default
        return self._local.get(field, default)

    async def delete(self, field: str) -> None:
        if self._client:
            await self._client.delete(self._key(field))
        else:
            self._local.pop(field, None)

    async def get_all(self) -> dict[str, Any]:
        if self._client:
            pattern = f"wm:{self._job_id}:*"
            keys = await self._client.keys(pattern)
            if not keys:
                return {}
            values = await self._client.mget(*keys)
            prefix = f"wm:{self._job_id}:"
            return {
                k[len(prefix):]: json.loads(v)
                for k, v in zip(keys, values)
                if v is not None
            }
        return dict(self._local)

    async def clear(self) -> None:
        if self._client:
            keys = await self._client.keys(f"wm:{self._job_id}:*")
            if keys:
                await self._client.delete(*keys)
        else:
            self._local.clear()

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
