"""Add user table

Revision ID: 6be1d70f3933
Revises: 
Create Date: 2023-12-31 06:34:43.382476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6be1d70f3933'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("posts", sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column("title", sa.String(), nullable=False),
                    sa.Column("content", sa.String(), nullable=False),
                    sa.Column("published", sa.Boolean(), nullable=False, server_default="TRUE"))
    pass


def downgrade() -> None:
    op.drop_table("post")
    pass
