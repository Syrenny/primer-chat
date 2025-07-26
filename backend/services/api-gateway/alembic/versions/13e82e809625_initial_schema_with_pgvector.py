"""Initial schema with pgvector

Revision ID: 13e82e809625
Revises:
Create Date: 2025-07-26 16:02:14.441246

"""

from typing import Sequence, Union

from alembic import op
from shared_config import config

# revision identifiers, used by Alembic.
revision: str = "13e82e809625"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # embedding column (safety check внутри DO $$)
    op.execute(f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='chunks' AND column_name='embedding'
        ) THEN
            ALTER TABLE chunks ADD COLUMN embedding vector({config.embeddings.dimensions});
        END IF;
    END$$;
    """)

    # index
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE tablename = 'chunks' AND indexname = 'chunks_embedding_idx'
        ) THEN
            CREATE INDEX chunks_embedding_idx
            ON chunks USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        END IF;
    END$$;
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS chunks_embedding_idx")
    op.execute("ALTER TABLE chunks DROP COLUMN IF EXISTS embedding")
    op.execute("DROP EXTENSION IF EXISTS vector")
