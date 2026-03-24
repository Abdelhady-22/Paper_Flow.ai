"""Initial schema — all tables

Revision ID: 001_initial_schema
Revises: None
Create Date: 2024-01-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Users ──────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_pwd", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ── Chat Sessions ──────────────────────────────────────────────
    op.create_table(
        "chat_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ── Chat Messages ──────────────────────────────────────────────
    op.create_table(
        "chat_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("citations", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("input_type", sa.String(20), server_default="text"),
        sa.Column("feedback", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="ck_message_role"),
        sa.CheckConstraint("input_type IN ('text', 'voice')", name="ck_message_input_type"),
        sa.CheckConstraint("feedback IS NULL OR feedback IN ('like', 'dislike')", name="ck_message_feedback"),
    )
    op.create_index("idx_chat_messages_session", "chat_messages", ["session_id"])

    # ── Papers ─────────────────────────────────────────────────────
    op.create_table(
        "papers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.Text, nullable=False),
        sa.Column("extracted_text", sa.Text, nullable=True),
        sa.Column("source", sa.String(20), server_default="upload"),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("language", sa.String(10), server_default="en"),
        sa.Column("status", sa.String(30), server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.CheckConstraint("source IN ('upload', 'agent')", name="ck_paper_source"),
    )
    op.create_index("idx_papers_user", "papers", ["user_id"])

    # ── Tool Results ───────────────────────────────────────────────
    op.create_table(
        "tool_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("paper_id", UUID(as_uuid=True), sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tool_type", sa.String(50), nullable=False),
        sa.Column("mode_used", sa.String(20), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("idx_tool_results_paper", "tool_results", ["paper_id"])


def downgrade() -> None:
    op.drop_table("tool_results")
    op.drop_table("papers")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("users")
