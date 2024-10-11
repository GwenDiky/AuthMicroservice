"""added role

Revision ID: 58b3ec47bf00
Revises: 1c86261e8896
Create Date: 2024-10-08 11:16:53.807850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58b3ec47bf00'
down_revision: Union[str, None] = '1c86261e8896'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
