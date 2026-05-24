"""add annee groupe and annee semestre

Revision ID: 003
Revises: 002
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Migration déjà appliquée manuellement
    pass


def downgrade() -> None:
    # Migration déjà appliquée manuellement
    pass
