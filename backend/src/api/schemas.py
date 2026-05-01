"""Request and response schemas for the API layer."""
import uuid

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------

class StoryCreate(BaseModel):
    title: str
    meta: dict = Field(default_factory=dict)


class StoryResponse(BaseModel):
    id: uuid.UUID
    title: str
    meta: dict

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

class ChapterCreate(BaseModel):
    story_id: uuid.UUID
    order: int
    title: str | None = None
    content: str = ""


class ChapterContentUpdate(BaseModel):
    content: str


class ChapterOverrideSet(BaseModel):
    key: str
    value: str


class ChapterResponse(BaseModel):
    id: uuid.UUID
    story_id: uuid.UUID
    order: int
    title: str | None
    analysis_state: str
    content: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class OrchestratorJobRequest(BaseModel):
    story_id: uuid.UUID
    directive: str
    priority: int = 5


class JobStatusResponse(BaseModel):
    id: uuid.UUID
    job_type: str
    status: str
    priority: int
    result: dict | None
    error: str | None

    model_config = {"from_attributes": True}
