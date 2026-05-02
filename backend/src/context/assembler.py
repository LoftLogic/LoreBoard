"""ContextAssembler: agent_type + task + scope → Context."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.db.models import Chapter, Entity
from src.memory.canonical import CanonicalMemory
from src.memory.semantic import SemanticMemory
from src.memory.working import WorkingMemory
from src.output.schemas import AgentType


class ScopeType(str, Enum):
    STORY = "story"
    CHAPTER = "chapter"
    ENTITY = "entity"
    GLOBAL = "global"


@dataclass
class TaskScope:
    scope_type: ScopeType
    story_id: uuid.UUID | None = None
    chapter_id: uuid.UUID | None = None
    entity_id: uuid.UUID | None = None


@dataclass
class Context:
    agent_type: AgentType
    task_description: str
    scope: TaskScope

    # Canonical state pulled from PG
    story_title: str | None = None
    chapters: list[Chapter] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    overrides: dict[str, str] = field(default_factory=dict)

    # Semantic hits from pgvector
    similar_entities: list[tuple[Entity, float]] = field(default_factory=list)

    # Hot data from working memory (prior steps in this job)
    working: dict[str, Any] = field(default_factory=dict)

    def to_prompt_dict(self) -> dict[str, Any]:
        """Serialize context into a dict suitable for injecting into a prompt."""
        return {
            "agent_type": self.agent_type.value,
            "task": self.task_description,
            "scope": {
                "type": self.scope.scope_type.value,
                "story_id": str(self.scope.story_id) if self.scope.story_id else None,
                "chapter_id": str(self.scope.chapter_id) if self.scope.chapter_id else None,
            },
            "story_title": self.story_title,
            "chapters": [
                {"id": str(c.id), "order": c.order, "title": c.title, "content_preview": c.content[:500]}
                for c in self.chapters
            ],
            "entities": [
                {"id": str(e.id), "name": e.name, "type": e.entity_type, "attributes": e.attributes}
                for e in self.entities
            ],
            "similar_entities": [
                {"name": e.name, "type": e.entity_type, "distance": round(d, 4)}
                for e, d in self.similar_entities
            ],
            "overrides": self.overrides,
            "working_memory": self.working,
        }


class ContextAssembler:
    """
    Assembles a Context object from all three memory layers.

    The depth of each layer pulled is determined by agent_type and scope:
    - ORCHESTRATOR: full story overview, entity roster, no semantic search
    - CHAPTER_ANALYZER: full chapter content + entity roster + semantic hits on chapter text
    - ENTITY_EXTRACTOR: chapter content only, no pre-loaded entities (to avoid anchoring)
    - CONSISTENCY_CHECKER: all chapters + all entities + semantic search
    - AUTOFILL: single chapter context + entity roster + semantic hits on placeholder query
    """

    def __init__(
        self,
        canonical: CanonicalMemory,
        semantic: SemanticMemory | None = None,
        working: WorkingMemory | None = None,
    ) -> None:
        self._canonical = canonical
        self._semantic = semantic
        self._working = working

    async def assemble(
        self,
        agent_type: AgentType,
        task_description: str,
        scope: TaskScope,
        semantic_query: str | None = None,
    ) -> Context:
        ctx = Context(agent_type=agent_type, task_description=task_description, scope=scope)

        if scope.story_id:
            story = await self._canonical.get_story(scope.story_id)
            if story:
                ctx.story_title = story.title

        ctx.chapters = await self._pull_chapters(agent_type, scope)
        ctx.entities = await self._pull_entities(agent_type, scope)
        ctx.overrides = await self._pull_overrides(agent_type, scope)

        if self._semantic and semantic_query and scope.story_id:
            ctx.similar_entities = await self._semantic.find_similar_entities(
                semantic_query, scope.story_id
            )

        if self._working:
            ctx.working = await self._working.get_all()

        return ctx

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _pull_chapters(self, agent_type: AgentType, scope: TaskScope) -> list[Chapter]:
        if scope.chapter_id:
            ch = await self._canonical.get_chapter(scope.chapter_id)
            return [ch] if ch else []

        if scope.story_id and agent_type in (
            AgentType.ORCHESTRATOR,
            AgentType.CONSISTENCY_CHECKER,
            AgentType.SUMMARIZER,
        ):
            return await self._canonical.get_chapters_by_story(scope.story_id)

        return []

    async def _pull_entities(self, agent_type: AgentType, scope: TaskScope) -> list[Entity]:
        # Entity extractor intentionally receives no pre-loaded entities
        if agent_type == AgentType.ENTITY_EXTRACTOR:
            return []

        if scope.story_id:
            return await self._canonical.get_entities(scope.story_id)

        return []

    async def _pull_overrides(self, agent_type: AgentType, scope: TaskScope) -> dict[str, str]:
        if scope.chapter_id:
            return await self._canonical.get_overrides(scope.chapter_id)
        return {}
