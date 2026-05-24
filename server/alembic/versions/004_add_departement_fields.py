"""add departement fields

Revision ID: 004
Revises: 003
Create Date: 2026-04-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add section_departement_id to planifications table
    op.add_column('planifications', sa.Column('section_departement_id', sa.Integer(), nullable=True))
    
    # Add salle_departement_id to planif_salle table
    op.add_column('planif_salle', sa.Column('salle_departement_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove salle_departement_id from planif_salle table
    op.drop_column('planif_salle', 'salle_departement_id')
    
    # Remove section_departement_id from planifications table
    op.drop_column('planifications', 'section_departement_id')
