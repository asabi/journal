"""add_is_busy_to_calendar_events

Revision ID: cead22bc05ab
Revises: a881731162fd
Create Date: 2025-05-31 10:17:12.564799

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cead22bc05ab"
down_revision: Union[str, None] = "a881731162fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_busy column with default value of True
    op.add_column("calendar_events", sa.Column("is_busy", sa.Boolean(), nullable=False, server_default="1"))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_busy column
    op.drop_column("calendar_events", "is_busy")
