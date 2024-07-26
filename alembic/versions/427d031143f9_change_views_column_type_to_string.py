"""Change views column type to string

Revision ID: 427d031143f9
Revises: 84a6db597a95
Create Date: 2024-07-26 15:10:35.725181

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "427d031143f9"
down_revision: Union[str, None] = "84a6db597a95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("videos") as batch_op:
        batch_op.alter_column(
            "views",
            existing_type=sa.Integer(),
            type_=sa.String(),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("videos") as batch_op:
        batch_op.alter_column(
            "views",
            existing_type=sa.String(),
            type_=sa.Integer(),
            existing_nullable=False,
        )
