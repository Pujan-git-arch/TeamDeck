"""add primary super admin flag

Revision ID: c3bc86458ee5
Revises: 233f01707e37
Create Date: 2026-09-16 00:36:43.786402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3bc86458ee5'
down_revision: Union[str, Sequence[str], None] = '233f01707e37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add primary super administrator flag to users."""
    op.add_column(
        "users",
        sa.Column(
            "is_primary_super_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Remove primary super administrator flag from users."""
    op.drop_column("users", "is_primary_super_admin")