"""Canonical state — the authoritative source of truth stored in PostgreSQL."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import (
    AnalysisState, Chapter, ChapterOverride, Entity,
    EntityMention, Story, StoryFlag,
)


class CanonicalMemory:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    # ------------------------------------------------------------------
    # Stories
    # ------------------------------------------------------------------

    async def get_story(self, story_id: uuid.UUID) -> Story | None:
        result = await self._s.execute(
            select(Story).where(Story.id == story_id).options(selectinload(Story.chapters))
        )
        return result.scalar_one_or_none()

    async def create_story(self, title: str, meta: dict | None = None) -> Story:
        story = Story(title=title, meta=meta or {})
        self._s.add(story)
        await self._s.flush()
        return story

    # ------------------------------------------------------------------
    # Chapters
    # ------------------------------------------------------------------

    async def get_chapter(self, chapter_id: uuid.UUID) -> Chapter | None:
        result = await self._s.execute(
            select(Chapter).where(Chapter.id == chapter_id)
            .options(selectinload(Chapter.overrides))
        )
        return result.scalar_one_or_none()

    async def get_chapters_by_story(self, story_id: uuid.UUID) -> list[Chapter]:
        result = await self._s.execute(
            select(Chapter).where(Chapter.story_id == story_id).order_by(Chapter.order)
        )
        return list(result.scalars().all())

    async def upsert_chapter_content(self, chapter_id: uuid.UUID, content: str) -> None:
        """Update content and mark chapter as STALE (edited after analysis)."""
        await self._s.execute(
            update(Chapter)
            .where(Chapter.id == chapter_id)
            .values(
                content=content,
                analysis_state=AnalysisState.STALE,
                updated_at=datetime.now(tz=timezone.utc),
            )
        )

    async def mark_chapter_analyzed(self, chapter_id: uuid.UUID) -> None:
        await self._s.execute(
            update(Chapter)
            .where(Chapter.id == chapter_id)
            .values(
                analysis_state=AnalysisState.ANALYZED,
                last_analyzed_at=datetime.now(tz=timezone.utc),
            )
        )

    async def get_stale_chapters(self, story_id: uuid.UUID) -> list[Chapter]:
        result = await self._s.execute(
            select(Chapter).where(
                Chapter.story_id == story_id,
                Chapter.analysis_state == AnalysisState.STALE,
            )
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Entities
    # ------------------------------------------------------------------

    async def get_entities(self, story_id: uuid.UUID) -> list[Entity]:
        result = await self._s.execute(
            select(Entity).where(Entity.story_id == story_id)
        )
        return list(result.scalars().all())

    async def upsert_entity(
        self,
        story_id: uuid.UUID,
        name: str,
        entity_type: str,
        attributes: dict,
    ) -> Entity:
        result = await self._s.execute(
            select(Entity).where(Entity.story_id == story_id, Entity.name == name)
        )
        entity = result.scalar_one_or_none()
        if entity:
            entity.attributes = {**entity.attributes, **attributes}
        else:
            entity = Entity(story_id=story_id, name=name, entity_type=entity_type, attributes=attributes)
            self._s.add(entity)
        await self._s.flush()
        return entity

    async def add_mention(
        self,
        chapter_id: uuid.UUID,
        entity_id: uuid.UUID,
        start: int,
        end: int,
        snippet: str | None = None,
    ) -> EntityMention:
        mention = EntityMention(
            chapter_id=chapter_id,
            entity_id=entity_id,
            position_start=start,
            position_end=end,
            context_snippet=snippet,
        )
        self._s.add(mention)
        await self._s.flush()
        return mention

    # ------------------------------------------------------------------
    # Flags
    # ------------------------------------------------------------------

    async def add_flag(
        self,
        story_id: uuid.UUID,
        flag_type: str,
        message: str,
        severity: str = "warning",
        chapter_id: uuid.UUID | None = None,
    ) -> StoryFlag:
        flag = StoryFlag(
            story_id=story_id,
            chapter_id=chapter_id,
            flag_type=flag_type,
            message=message,
            severity=severity,
        )
        self._s.add(flag)
        await self._s.flush()
        return flag

    async def resolve_flag(self, flag_id: uuid.UUID) -> None:
        await self._s.execute(
            update(StoryFlag).where(StoryFlag.id == flag_id).values(resolved=True)
        )

    # ------------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------------

    async def set_override(self, chapter_id: uuid.UUID, key: str, value: str) -> None:
        result = await self._s.execute(
            select(ChapterOverride).where(
                ChapterOverride.chapter_id == chapter_id,
                ChapterOverride.key == key,
            )
        )
        override = result.scalar_one_or_none()
        if override:
            override.value = value
        else:
            self._s.add(ChapterOverride(chapter_id=chapter_id, key=key, value=value))
        await self._s.flush()

    async def get_overrides(self, chapter_id: uuid.UUID) -> dict[str, str]:
        result = await self._s.execute(
            select(ChapterOverride).where(ChapterOverride.chapter_id == chapter_id)
        )
        return {o.key: o.value for o in result.scalars().all()}
