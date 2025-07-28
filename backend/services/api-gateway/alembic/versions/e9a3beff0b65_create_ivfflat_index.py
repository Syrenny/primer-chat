"""Create ivfflat index

Revision ID: e9a3beff0b65
Revises: 83d9b51b8071
Create Date: 2025-07-28 17:48:40.129357

"""

from typing import Sequence, Union

from alembic import op
from shared_config import config

# revision identifiers, used by Alembic.
revision: str = "e9a3beff0b65"
down_revision: Union[str, Sequence[str], None] = "83d9b51b8071"
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
