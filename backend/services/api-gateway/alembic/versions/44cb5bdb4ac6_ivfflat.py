"""ivfflat

Revision ID: 44cb5bdb4ac6
Revises: 3ca93d6631fa
Create Date: 2025-08-13 13:45:56.375509

"""

from typing import Sequence, Union

from alembic import op
from shared_config import config

# revision identifiers, used by Alembic.
revision: str = "44cb5bdb4ac6"
down_revision: Union[str, Sequence[str], None] = "3ca93d6631fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
