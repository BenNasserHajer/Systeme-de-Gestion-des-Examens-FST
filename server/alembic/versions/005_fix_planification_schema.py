"""fix planification schema

Revision ID: 005
Revises: 004
Create Date: 2026-05-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Mise à jour du schéma de planification_examen pour correspondre au modèle SQLAlchemy.
    """
    
    # 1. Rendre departement_id nullable (actuellement NOT NULL dans la DB)
    op.alter_column('planification_examen', 'departement_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # 2. Rendre creneau_id nullable (actuellement NOT NULL dans la DB)
    op.alter_column('planification_examen', 'creneau_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # 3. Rendre coefficient de type FLOAT au lieu de INTEGER
    op.alter_column('planification_examen', 'coefficient',
                    existing_type=sa.Integer(),
                    type_=sa.Float(),
                    nullable=False,
                    existing_nullable=True)
    
    # 4. Rendre section_nb_etudiants NOT NULL
    op.alter_column('planification_examen', 'section_nb_etudiants',
                    existing_type=sa.Integer(),
                    nullable=False,
                    existing_nullable=True)
    
    # 5. Rendre a_examen_final NOT NULL avec default True
    op.alter_column('planification_examen', 'a_examen_final',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default='true',
                    existing_nullable=True)
    
    # 6. Rendre a_ds NOT NULL avec default True
    op.alter_column('planification_examen', 'a_ds',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default='true',
                    existing_nullable=True)
    
    # 7. Rendre section_id NOT NULL
    op.alter_column('planification_examen', 'section_id',
                    existing_type=sa.Integer(),
                    nullable=False,
                    existing_nullable=True)
    
    # 8. Modifier la clé primaire de planif_salle pour être composite
    # D'abord, supprimer l'ancienne contrainte de clé primaire
    op.drop_constraint('planif_salle_pkey', 'planif_salle', type_='primary')
    
    # Créer la nouvelle clé primaire composite
    op.create_primary_key('planif_salle_pkey', 'planif_salle', 
                          ['planification_id', 'groupe_id'])


def downgrade() -> None:
    """
    Revenir à l'ancien schéma.
    """
    
    # Restaurer la clé primaire simple de planif_salle
    op.drop_constraint('planif_salle_pkey', 'planif_salle', type_='primary')
    op.create_primary_key('planif_salle_pkey', 'planif_salle', ['planification_id'])
    
    # Restaurer les colonnes
    op.alter_column('planification_examen', 'section_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    op.alter_column('planification_examen', 'a_ds',
                    existing_type=sa.Boolean(),
                    nullable=True,
                    server_default=None)
    
    op.alter_column('planification_examen', 'a_examen_final',
                    existing_type=sa.Boolean(),
                    nullable=True,
                    server_default=None)
    
    op.alter_column('planification_examen', 'section_nb_etudiants',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    op.alter_column('planification_examen', 'coefficient',
                    existing_type=sa.Float(),
                    type_=sa.Integer(),
                    nullable=True)
    
    op.alter_column('planification_examen', 'creneau_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    
    op.alter_column('planification_examen', 'departement_id',
                    existing_type=sa.Integer(),
                    nullable=False)
