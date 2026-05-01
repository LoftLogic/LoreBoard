"""Pydantic schemas for all agent outputs. Every agent must return a subclass of AgentOutput."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    ENTITY_EXTRACTOR = "entity_extractor"
    CONSISTENCY_CHECKER = "consistency_checker"
    CHAPTER_ANALYZER = "chapter_analyzer"
    AUTOFILL = "autofill"
    SUMMARIZER = "summarizer"


class AgentOutput(BaseModel):
    """Base output for every agent run."""
    run_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    job_id: str
    agent_type: AgentType
    success: bool
    reasoning: str | None = None
    tokens_used: int = 0
    elapsed_ms: int = 0
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class PlannedJob(BaseModel):
    job_type: str
    priority: int = 5
    payload: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)   # job_ids this must wait for


class OrchestratorOutput(AgentOutput):
    agent_type: AgentType = AgentType.ORCHESTRATOR
    directive: str
    planned_jobs: list[PlannedJob] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Entity Extraction
# ---------------------------------------------------------------------------

class ExtractedEntity(BaseModel):
    name: str
    entity_type: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    mentions: list[dict[str, Any]] = Field(default_factory=list)  # [{start, end, snippet}]
    confidence: float = 1.0


class EntityExtractionOutput(AgentOutput):
    agent_type: AgentType = AgentType.ENTITY_EXTRACTOR
    chapter_id: str
    entities: list[ExtractedEntity] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Consistency Checker
# ---------------------------------------------------------------------------

class ConsistencyIssue(BaseModel):
    flag_type: str
    severity: str   # info | warning | error
    message: str
    chapter_id: str | None = None
    entity_id: str | None = None


class ConsistencyCheckOutput(AgentOutput):
    agent_type: AgentType = AgentType.CONSISTENCY_CHECKER
    story_id: str
    issues: list[ConsistencyIssue] = Field(default_factory=list)
    checked_chapters: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Chapter Analysis
# ---------------------------------------------------------------------------

class ChapterAnalysisOutput(AgentOutput):
    agent_type: AgentType = AgentType.CHAPTER_ANALYZER
    chapter_id: str
    summary: str = ""
    themes: list[str] = Field(default_factory=list)
    pov_character: str | None = None
    word_count: int = 0
    flags: list[ConsistencyIssue] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Auto-fill
# ---------------------------------------------------------------------------

class AutofillSuggestion(BaseModel):
    text: str
    confidence: float
    rationale: str = ""


class AutofillOutput(AgentOutput):
    agent_type: AgentType = AgentType.AUTOFILL
    placeholder: str
    suggestions: list[AutofillSuggestion] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Summarizer
# ---------------------------------------------------------------------------

class SummarizerOutput(AgentOutput):
    agent_type: AgentType = AgentType.SUMMARIZER
    scope: str   # "story" | "chapter" | "entity"
    scope_id: str
    summary: str = ""
