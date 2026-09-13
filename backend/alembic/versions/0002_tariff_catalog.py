"""Add official tariff nomenclature catalog.

Revision ID: 0002_tariff_catalog
Revises: 0001_initial
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_tariff_catalog"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tariff_catalog",
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_index(
        "ix_tariff_catalog_level",
        "tariff_catalog",
        ["level"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_tariff_catalog_level", table_name="tariff_catalog")
    op.drop_table("tariff_catalog")
