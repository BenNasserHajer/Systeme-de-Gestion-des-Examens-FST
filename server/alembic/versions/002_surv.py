"""create surveillances table

Revision ID: 002_surv
Revises: 001_planif
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa

revision = "002_surv"
down_revision = "001_planif"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "surveillances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("planification_id", sa.Integer(), sa.ForeignKey("planifications.id"), nullable=False),
        sa.Column("enseignant", sa.String(length=120), nullable=False),
        sa.Column("statut", sa.String(length=40), nullable=False, server_default="AFFECTEE"),
        sa.Column("charge", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_surveillances_planification_id", "surveillances", ["planification_id"])


def downgrade() -> None:
    op.drop_index("ix_surveillances_planification_id", table_name="surveillances")
    op.drop_table("surveillances")
