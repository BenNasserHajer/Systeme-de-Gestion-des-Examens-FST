"""add annee to groupe and annee_semestre to section_matiere

Revision ID: 003_add_annee_groupe_and_annee_semestre
Revises: 002_surv
Create Date: 2026-04-25
"""

from alembic import op
import sqlalchemy as sa

revision = "003_add_annee_groupe_and_annee_semestre"
down_revision = "002_surv"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add annee column to groupe table
    op.add_column(
        "groupe",
        sa.Column("annee", sa.String(length=10), nullable=True)
    )
    
    # Add annee_semestre column to section_matiere table
    op.add_column(
        "section_matiere",
        sa.Column("annee_semestre", sa.String(length=20), nullable=True)
    )
    
    # Update existing data with default values if needed
    # For groupe: set annee based on section's niveau
    op.execute("""
        UPDATE groupe g
        SET annee = CONCAT(
            CAST(EXTRACT(YEAR FROM CURRENT_DATE) AS TEXT),
            '-',
            CAST(EXTRACT(YEAR FROM CURRENT_DATE) + 1 AS TEXT)
        )
        WHERE annee IS NULL
    """)
    
    # For section_matiere: set default to current year S1
    op.execute("""
        UPDATE section_matiere
        SET annee_semestre = CONCAT(
            CAST(EXTRACT(YEAR FROM CURRENT_DATE) AS TEXT),
            '-',
            CAST(EXTRACT(YEAR FROM CURRENT_DATE) + 1 AS TEXT),
            ' S1'
        )
        WHERE annee_semestre IS NULL
    """)
    
    # Make columns NOT NULL after setting default values
    op.alter_column("groupe", "annee", nullable=False)
    op.alter_column("section_matiere", "annee_semestre", nullable=False)


def downgrade() -> None:
    # Remove annee_semestre column from section_matiere
    op.drop_column("section_matiere", "annee_semestre")
    
    # Remove annee column from groupe
    op.drop_column("groupe", "annee")
