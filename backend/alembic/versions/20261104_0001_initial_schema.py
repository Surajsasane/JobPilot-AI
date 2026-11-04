"""Bootstrap the current JobPilot schema.

This baseline migration is safe for existing MVP databases: tables already
created by the earlier create_all startup are left intact, while new tables
are added. Future schema changes should use explicit incremental revisions.
"""
from alembic import op
from sqlalchemy import inspect

from app.db import Base
import app.models  # noqa: F401

revision = "20261104_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    existing_tables = set(inspect(bind).get_table_names())
    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            table.create(bind=bind, checkfirst=True)

def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, checkfirst=True)
