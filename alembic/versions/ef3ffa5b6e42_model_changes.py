"""Model changes

Revision ID: ef3ffa5b6e42
Revises: cd87dbb45d79
Create Date: 2024-11-11 06:12:40.029758

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ef3ffa5b6e42"
down_revision: Union[str, None] = "cd87dbb45d79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
