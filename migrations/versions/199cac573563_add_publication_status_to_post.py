"""add publication status to post

Revision ID: 199cac573563
Revises: 46f521f5130e
Create Date: 2026-10-26 20:00:11.194654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '199cac573563'
down_revision: Union[str, Sequence[str], None] = '46f521f5130e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(
          sa.Column(
              'is_published', 
              sa.Boolean(), 
              server_default=sa.text('1'), 
              nullable=False
          )
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('is_published')

    # ### end Alembic commands ###
