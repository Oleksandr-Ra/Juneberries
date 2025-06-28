"""Status field -> delete qnique -> order table

Revision ID: 215850378032
Revises: dcec5970a5f0
Create Date: 2025-06-28 08:06:21.252108

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "215850378032"
down_revision: Union[str, None] = "dcec5970a5f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("uq_orders_status"), "orders", type_="unique")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(
        op.f("uq_orders_status"),
        "orders",
        ["status"],
        postgresql_nulls_not_distinct=False,
    )
