"""Create orders_service and order_items tables

Revision ID: 34d1f8bc5dd6
Revises:
Create Date: 2025-06-12 12:33:20.782468

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "34d1f8bc5dd6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "created",
                "processing",
                "shipped",
                "delivered",
                "cancelled",
                name="order_status_enum",
            ),
            server_default="created",
            nullable=False,
        ),
        sa.Column(
            "total_price", sa.Numeric(precision=10, scale=2), nullable=False
        ),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "unit_price", sa.Numeric(precision=10, scale=2), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders_service.id"],
            name=op.f("fk_order_items_order_id_orders"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_items")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("order_items")
    op.drop_table("orders")
