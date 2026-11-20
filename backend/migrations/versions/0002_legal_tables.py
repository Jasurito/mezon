"""legal tables (docs/INGESTION.md section 6)

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-20
"""
import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "legal_documents",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("document_key", sa.Text, nullable=False, unique=True),
        sa.Column("document_type", sa.Text),
        sa.Column("document_number", sa.Text),
        sa.Column("title", postgresql.JSONB),
        sa.Column("adoption_date", sa.Date),
        sa.Column("issuing_body", sa.Text),
        sa.Column("source_url", sa.Text),
        sa.Column("status", sa.Text),
    )
    op.create_table(
        "document_versions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("document_id", sa.Integer, sa.ForeignKey("legal_documents.id"), nullable=False),
        sa.Column("language", sa.Text, nullable=False),
        sa.Column("is_official_text", sa.Boolean),
        sa.Column("effective_from", sa.Date),
        sa.Column("effective_to", sa.Date),
        sa.Column("review_status", sa.Text),
        sa.Column("version_label", sa.Text),
        sa.Column("source_url", sa.Text),
        sa.Column("raw_file_path", sa.Text),
        sa.Column("content_hash", sa.Text, nullable=False),
        sa.Column("retrieved_at", sa.Date),
        sa.Column("verified_by", sa.Text),
        sa.Column("last_verified_at", sa.Date),
        sa.UniqueConstraint("document_id", "language", "content_hash"),
    )
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("version_id", sa.Integer, sa.ForeignKey("document_versions.id"), nullable=False),
        sa.Column("section", sa.Text),
        sa.Column("chapter", sa.Text),
        sa.Column("article_number", sa.Text, nullable=False),
        sa.Column("article_title", sa.Text),
        sa.Column("status", sa.Text),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("content_normalized", sa.Text),
        sa.UniqueConstraint("version_id", "article_number"),
    )
    op.execute(
        "CREATE INDEX ix_articles_article_title_trgm ON articles "
        "USING gin (article_title gin_trgm_ops)"
    )
    op.create_table(
        "article_parts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("article_id", sa.Integer, sa.ForeignKey("articles.id"), nullable=False),
        sa.Column("part_number", sa.Integer, nullable=False),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("content_normalized", sa.Text),
    )
    op.create_table(
        "chunks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("article_id", sa.Integer, sa.ForeignKey("articles.id"), nullable=False),
        sa.Column("part_from", sa.Integer),
        sa.Column("part_to", sa.Integer),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("text_normalized", sa.Text, nullable=False),
        # Размерность не задана: модель эмбеддингов ещё не выбрана.
        sa.Column("embedding", Vector()),
        sa.Column(
            "tsv",
            postgresql.TSVECTOR,
            sa.Computed("to_tsvector('simple', text_normalized)", persisted=True),
        ),
        sa.Column("token_count", sa.Integer),
    )
    op.create_index("ix_chunks_tsv", "chunks", ["tsv"], postgresql_using="gin")
    op.create_table(
        "citations",
        sa.Column("citation_id", sa.Text, primary_key=True),
        sa.Column("document_id", sa.Integer, sa.ForeignKey("legal_documents.id"), nullable=False),
        sa.Column("article_number", sa.Text, nullable=False),
        sa.Column("part", sa.Integer),
        sa.Column("topic", sa.Text),
        sa.Column("verified_by", sa.Text),
    )


def downgrade() -> None:
    op.drop_table("citations")
    op.drop_index("ix_chunks_tsv", table_name="chunks")
    op.drop_table("chunks")
    op.drop_table("article_parts")
    op.execute("DROP INDEX IF EXISTS ix_articles_article_title_trgm")
    op.drop_table("articles")
    op.drop_table("document_versions")
    op.drop_table("legal_documents")
