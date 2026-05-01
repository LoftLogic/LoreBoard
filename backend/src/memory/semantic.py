"""Semantic memory — pgvector similarity search over entity and chapter embeddings."""
from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Entity


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class SemanticMemory:
    def __init__(self, session: AsyncSession, embedder: EmbeddingProvider) -> None:
        self._s = session
        self._embedder = embedder

    async def store_entity_embedding(self, entity_id: uuid.UUID, description: str) -> None:
        vector = await self._embedder.embed(description)
        vec_str = "[" + ",".join(str(x) for x in vector) + "]"
        await self._s.execute(
            text("UPDATE entities SET embedding = CAST(:vec AS vector) WHERE id = :id"),
            {"vec": vec_str, "id": str(entity_id)},
        )

    async def find_similar_entities(
        self,
        query: str,
        story_id: uuid.UUID,
        top_k: int = 5,
        distance_threshold: float = 0.4,
    ) -> list[tuple[Entity, float]]:
        """Returns (entity, cosine_distance) pairs sorted by similarity."""
        vector = await self._embedder.embed(query)
        vec_str = "[" + ",".join(str(x) for x in vector) + "]"
        # pgvector cosine distance operator: <=>
        result = await self._s.execute(
            text("""
                SELECT id, (embedding <=> CAST(:vec AS vector)) AS distance
                FROM entities
                WHERE story_id = :story_id
                  AND embedding IS NOT NULL
                  AND (embedding <=> CAST(:vec AS vector)) < :threshold
                ORDER BY distance
                LIMIT :k
            """),
            {"vec": vec_str, "story_id": str(story_id), "threshold": distance_threshold, "k": top_k},
        )
        rows = result.fetchall()
        if not rows:
            return []

        ids = [r[0] for r in rows]
        distances = {r[0]: r[1] for r in rows}
        entities_result = await self._s.execute(
            select(Entity).where(Entity.id.in_(ids))
        )
        entities = {str(e.id): e for e in entities_result.scalars().all()}
        return [(entities[str(eid)], distances[eid]) for eid in ids if str(eid) in entities]

    async def find_similar_chunks(
        self,
        query: str,
        story_id: uuid.UUID,
        top_k: int = 5,
    ) -> list[dict]:
        """Placeholder for chunk-level semantic search (e.g. passage retrieval)."""
        # Extend this when chapter content embeddings are added
        return []
