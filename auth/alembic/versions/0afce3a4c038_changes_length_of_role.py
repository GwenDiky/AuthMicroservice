"""changes length of role

Revision ID: 0afce3a4c038
Revises: aa150abba55e
Create Date: 2024-10-08 11:26:20.238846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0afce3a4c038'
down_revision: Union[str, None] = 'aa150abba55e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
