import uuid
from datetime import datetime
from enum import Enum as PyEnum

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Index, Integer,
    String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AnalysisState(str, PyEnum):
    PENDING = "pending"
    ANALYZED = "analyzed"
    STALE = "stale"          # chapter edited after last analysis


class EntityType(str, PyEnum):
    CHARACTER = "character"
    LOCATION = "location"
    ITEM = "item"
    EVENT = "event"
    CONCEPT = "concept"
    CUSTOM = "custom"


class JobStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlagSeverity(str, PyEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Story & Chapter
# ---------------------------------------------------------------------------

class Story(Base):
    __tablename__ = "stories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter", back_populates="story", order_by="Chapter.order", cascade="all, delete-orphan"
    )
    entities: Mapped[list["Entity"]] = relationship(
        "Entity", back_populates="story", cascade="all, delete-orphan"
    )
    flags: Mapped[list["StoryFlag"]] = relationship(
        "StoryFlag", back_populates="story", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["JobRecord"]] = relationship(
        "JobRecord", back_populates="story"
    )


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, default="")
    analysis_state: Mapped[AnalysisState] = mapped_column(
        Enum(AnalysisState, name="analysis_state"), default=AnalysisState.PENDING
    )
    last_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    story: Mapped["Story"] = relationship("Story", back_populates="chapters")
    mentions: Mapped[list["EntityMention"]] = relationship(
        "EntityMention", back_populates="chapter", cascade="all, delete-orphan"
    )
    flags: Mapped[list["StoryFlag"]] = relationship(
        "StoryFlag", back_populates="chapter", cascade="all, delete-orphan"
    )
    overrides: Mapped[list["ChapterOverride"]] = relationship(
        "ChapterOverride", back_populates="chapter", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["JobRecord"]] = relationship("JobRecord", back_populates="chapter")

    __table_args__ = (Index("ix_chapters_story_order", "story_id", "order"),)


# ---------------------------------------------------------------------------
# Entities & Mentions
# ---------------------------------------------------------------------------

class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    entity_type: Mapped[EntityType] = mapped_column(Enum(EntityType, name="entity_type"), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Embedding stored here for vector similarity search (pgvector)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    story: Mapped["Story"] = relationship("Story", back_populates="entities")
    mentions: Mapped[list["EntityMention"]] = relationship(
        "EntityMention", back_populates="entity", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_entities_story_name", "story_id", "name"),)


class EntityMention(Base):
    __tablename__ = "entity_mentions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"))
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"))
    position_start: Mapped[int] = mapped_column(Integer, nullable=False)
    position_end: Mapped[int] = mapped_column(Integer, nullable=False)
    context_snippet: Mapped[str | None] = mapped_column(Text)

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="mentions")
    entity: Mapped["Entity"] = relationship("Entity", back_populates="mentions")


# ---------------------------------------------------------------------------
# Flags & Overrides
# ---------------------------------------------------------------------------

class StoryFlag(Base):
    __tablename__ = "story_flags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"))
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"))
    flag_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[FlagSeverity] = mapped_column(Enum(FlagSeverity, name="flag_severity"), default=FlagSeverity.WARNING)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    story: Mapped["Story"] = relationship("Story", back_populates="flags")
    chapter: Mapped["Chapter | None"] = relationship("Chapter", back_populates="flags")


class ChapterOverride(Base):
    __tablename__ = "chapter_overrides"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="overrides")

    __table_args__ = (Index("ix_overrides_chapter_key", "chapter_id", "key", unique=True),)


# ---------------------------------------------------------------------------
# Agent Runs & Feedback
# ---------------------------------------------------------------------------

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False)
    input_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    output_data: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tokens_used: Mapped[int | None] = mapped_column(Integer)
    elapsed_ms: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)

    feedback: Mapped[list["FeedbackEntry"]] = relationship(
        "FeedbackEntry", back_populates="run", cascade="all, delete-orphan"
    )
    llm_calls: Mapped[list["LlmCall"]] = relationship(
        "LlmCall", back_populates="run", cascade="all, delete-orphan", order_by="LlmCall.created_at"
    )


class FeedbackEntry(Base):
    __tablename__ = "feedback_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"))
    rating: Mapped[int | None] = mapped_column(Integer)   # 1–5
    notes: Mapped[str | None] = mapped_column(Text)
    calibration_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    calibration_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped["AgentRun"] = relationship("AgentRun", back_populates="feedback")


# ---------------------------------------------------------------------------
# LLM Call Telemetry
# ---------------------------------------------------------------------------

class LlmCall(Base):
    __tablename__ = "llm_calls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True
    )
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stop_reason: Mapped[str | None] = mapped_column(String(100))
    tool_calls: Mapped[list] = mapped_column(JSONB, default=list)
    input_messages: Mapped[dict] = mapped_column(JSONB, default=dict)
    output_content: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped["AgentRun"] = relationship("AgentRun", back_populates="llm_calls")


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class JobRecord(Base):
    __tablename__ = "job_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    celery_task_id: Mapped[str | None] = mapped_column(String(200), index=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus, name="job_status"), default=JobStatus.PENDING)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[dict | None] = mapped_column(JSONB)
    story_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="SET NULL"))
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"))
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    story: Mapped["Story | None"] = relationship("Story", back_populates="jobs")
    chapter: Mapped["Chapter | None"] = relationship("Chapter", back_populates="jobs")

    __table_args__ = (
        Index("ix_jobs_status_priority", "status", "priority"),
        Index("ix_jobs_story_status", "story_id", "status"),
    )
