"""changes length of role

Revision ID: f05538a32329
Revises: 0afce3a4c038
Create Date: 2024-10-08 11:36:10.243957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f05538a32329'
down_revision: Union[str, None] = '0afce3a4c038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
