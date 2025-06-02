"""add_food_analysis_tables

Revision ID: 422273f329ba
Revises: 68e8a59e4e19
Create Date: 2025-05-31 11:30:23.564799

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "422273f329ba"
down_revision: Union[str, None] = "68e8a59e4e19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create food_entries and food_items tables."""
    # Create food_entries table
    op.create_table(
        "food_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("image_path", sa.String(), nullable=False),
        sa.Column("total_calories", sa.Float(), nullable=True),
        sa.Column("raw_analysis", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create food_items table
    op.create_table(
        "food_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("food_name", sa.String(), nullable=False),
        sa.Column("portion_size", sa.String(), nullable=True),
        sa.Column("calories", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["entry_id"],
            ["food_entries.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop food_items and food_entries tables."""
    op.drop_table("food_items")
    op.drop_table("food_entries")
