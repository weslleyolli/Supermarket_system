"""remove_manager_role

Revision ID: 0b032b7864b1
Revises: 4a71a61f0f97
Create Date: 2025-07-15 16:34:53.783777

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b032b7864b1"
down_revision: Union[str, None] = "4a71a61f0f97"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
