"""Initial schema: conversations, messages, documents with pgvector.

Revision ID: 001
Revises: None
Create Date: 2026-02-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "conversations",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("phone_number", sa.String(20), nullable=False, index=True),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "last_active_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("metadata", sa.dialects.postgresql.JSONB, nullable=True),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "conversation_id",
            sa.BigInteger,
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("intent", sa.String(50), nullable=True),
        sa.Column("tool_name", sa.String(100), nullable=True),
        sa.Column("tool_input", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("tool_output", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("embedding", Vector(1536)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_index(
        "ix_documents_embedding",
        "documents",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_table("messages")
    op.drop_table("conversations")
