"""added role

Revision ID: 1aa3f54218b1
Revises: 58b3ec47bf00
Create Date: 2024-10-08 11:17:57.663714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1aa3f54218b1'
down_revision: Union[str, None] = '58b3ec47bf00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
