"""Initial export analytics schema."""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tariff_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("digits", sa.SmallInteger(), nullable=False),
        sa.Column("chapter", sa.String(length=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tariff_items_code", "tariff_items", ["code"], unique=True)
    op.create_index("ix_tariff_items_chapter", "tariff_items", ["chapter"], unique=False)

    op.create_table(
        "export_values",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tariff_item_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("value_usd", sa.BigInteger(), nullable=False),
        sa.Column("is_provisional", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tariff_item_id"],
            ["tariff_items.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tariff_item_id",
            "year",
            name="uq_export_item_year",
        ),
    )
    op.create_index(
        "ix_export_values_tariff_item_id",
        "export_values",
        ["tariff_item_id"],
        unique=False,
    )
    op.create_index(
        "ix_export_values_year",
        "export_values",
        ["year"],
        unique=False,
    )
    op.create_index(
        "ix_export_values_year_item",
        "export_values",
        ["year", "tariff_item_id"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_export_values_year_item", table_name="export_values")
    op.drop_index("ix_export_values_year", table_name="export_values")
    op.drop_index("ix_export_values_tariff_item_id", table_name="export_values")
    op.drop_table("export_values")
    op.drop_index("ix_tariff_items_chapter", table_name="tariff_items")
    op.drop_index("ix_tariff_items_code", table_name="tariff_items")
    op.drop_table("tariff_items")
