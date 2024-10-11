"""changes length of role

Revision ID: aa150abba55e
Revises: ffa09c9f9719
Create Date: 2024-10-08 11:24:26.973308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa150abba55e'
down_revision: Union[str, None] = 'ffa09c9f9719'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
