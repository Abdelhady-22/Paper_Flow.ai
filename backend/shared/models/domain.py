"""
Domain Models — SQLAlchemy ORM Models

All database tables as SQLAlchemy ORM models. These are shared across services
and used by Alembic for migration generation.

Schema from Section 14.1:
- users, chat_sessions, chat_messages, papers, tool_results
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from infrastructure.postgres.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="user", cascade="all, delete-orphan")
    tool_results = relationship("ToolResult", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    input_type: Mapped[str] = mapped_column(
        String(20), default="text"
    )
    feedback: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="ck_message_role"),
        CheckConstraint(
            "input_type IN ('text', 'voice')", name="ck_message_input_type"
        ),
        CheckConstraint(
            "feedback IS NULL OR feedback IN ('like', 'dislike')",
            name="ck_message_feedback",
        ),
        Index("idx_chat_messages_session", "session_id"),
    )

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(
        String(20), default="upload"
    )
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    status: Mapped[str] = mapped_column(String(30), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "source IN ('upload', 'agent')", name="ck_paper_source"
        ),
        Index("idx_papers_user", "user_id"),
    )

    # Relationships
    user = relationship("User", back_populates="papers")
    tool_results = relationship("ToolResult", back_populates="paper", cascade="all, delete-orphan")


class ToolResult(Base):
    __tablename__ = "tool_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    tool_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mode_used: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        JSONB, default=dict, name="metadata"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_tool_results_paper", "paper_id"),
    )

    # Relationships
    paper = relationship("Paper", back_populates="tool_results")
    user = relationship("User", back_populates="tool_results")
