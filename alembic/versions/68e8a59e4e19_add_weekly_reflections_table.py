"""add_weekly_reflections_table

Revision ID: 68e8a59e4e19
Revises: cead22bc05ab
Create Date: 2025-05-31 10:45:23.564799

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "68e8a59e4e19"
down_revision: Union[str, None] = "cead22bc05ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create weekly_reflections table."""
    op.create_table(
        "weekly_reflections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("proud_of", sa.String(), nullable=True),
        sa.Column("principles_upheld", sa.String(), nullable=True),
        sa.Column("learnings", sa.String(), nullable=True),
        sa.Column("do_differently", sa.String(), nullable=True),
        sa.Column("challenges", sa.String(), nullable=True),
        sa.Column("week_word", sa.String(), nullable=True),
        sa.Column("week_feeling", sa.String(), nullable=True),
        sa.Column("additional_notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", "timestamp", name="uq_reflection_email_timestamp"),
    )


def downgrade() -> None:
    """Drop weekly_reflections table."""
    op.drop_table("weekly_reflections")
