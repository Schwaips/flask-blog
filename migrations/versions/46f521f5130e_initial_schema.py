"""initial schema

Revision ID: 46f521f5130e
Revises: 
Create Date: 2026-10-26 19:55:22.821577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46f521f5130e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.UniqueConstraint("username"),
        sqlite_autoincrement=True,
    )

    op.create_table(
        "post",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column(
            "created",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sqlite_autoincrement=True,
    )

def downgrade() -> None:
    op.drop_table("post")
    op.drop_table("user")
