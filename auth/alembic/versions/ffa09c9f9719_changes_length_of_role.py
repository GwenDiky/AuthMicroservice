"""changes length of role

Revision ID: ffa09c9f9719
Revises: 1aa3f54218b1
Create Date: 2024-10-08 11:23:32.159119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffa09c9f9719'
down_revision: Union[str, None] = '1aa3f54218b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
