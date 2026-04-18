"""create planifications table

Revision ID: 001_planif
Revises:
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa

revision = "001_planif"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "planifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("matiere", sa.String(length=120), nullable=False),
        sa.Column("salle", sa.String(length=80), nullable=False),
        sa.Column("date_examen", sa.Date(), nullable=False),
        sa.Column("statut", sa.String(length=40), nullable=False, server_default="BROUILLON"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("planifications")
