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
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=False),
        sa.Column("section_matiere_id", sa.Integer(), nullable=False),
        sa.Column("matiere", sa.String(length=120), nullable=False),
        sa.Column("type_epreuve", sa.String(length=24), nullable=False, server_default="EXAMEN_FINAL"),
        sa.Column("date_examen", sa.Date(), nullable=False),
        sa.Column("heure_debut", sa.Time(), nullable=False),
        sa.Column("heure_fin", sa.Time(), nullable=False),
        sa.Column("session_date_debut", sa.Date(), nullable=False),
        sa.Column("session_date_fin", sa.Date(), nullable=False),
        sa.Column("session_statut", sa.String(length=24), nullable=False, server_default="BROUILLON"),
        sa.Column("duree", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("coefficient", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("section_nb_etudiants", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mode_affectation", sa.String(length=24), nullable=False, server_default="AUTO"),
        sa.Column("statut", sa.String(length=24), nullable=False, server_default="BROUILLON"),
        sa.Column("nb_groupes", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("nb_surveillants_requis", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint(
            "section_matiere_id",
            "session_id",
            "type_epreuve",
            name="uq_planif_section_matiere_session_type",
        ),
    )
    op.create_index("ix_planifications_session_id", "planifications", ["session_id"])
    op.create_index("ix_planifications_section_id", "planifications", ["section_id"])
    op.create_index("ix_planifications_section_matiere_id", "planifications", ["section_matiere_id"])
    op.create_index("ix_planifications_date_examen", "planifications", ["date_examen"])

    op.create_table(
        "planif_salle",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("planification_id", sa.Integer(), sa.ForeignKey("planifications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("salle_id", sa.String(length=80), nullable=False),
        sa.Column("salle_capacite", sa.Integer(), nullable=False),
        sa.Column("salle_batiment", sa.String(length=64), nullable=True),
        sa.Column("groupe_id", sa.Integer(), nullable=False),
        sa.Column("groupe_effectif", sa.Integer(), nullable=False),
        sa.Column("creneau_date", sa.Date(), nullable=False),
        sa.Column("heure_debut", sa.Time(), nullable=False),
        sa.UniqueConstraint("planification_id", "salle_id", name="uq_planif_salle_planif_salle"),
        sa.UniqueConstraint("planification_id", "groupe_id", name="uq_planif_salle_planif_groupe"),
        sa.UniqueConstraint("salle_id", "creneau_date", "heure_debut", name="uq_salle_creneau_unique"),
    )
    op.create_index("ix_planif_salle_planification_id", "planif_salle", ["planification_id"])
    op.create_index("ix_planif_salle_salle_id", "planif_salle", ["salle_id"])
    op.create_index("ix_planif_salle_creneau_date", "planif_salle", ["creneau_date"])


def downgrade() -> None:
    op.drop_index("ix_planif_salle_creneau_date", table_name="planif_salle")
    op.drop_index("ix_planif_salle_salle_id", table_name="planif_salle")
    op.drop_index("ix_planif_salle_planification_id", table_name="planif_salle")
    op.drop_table("planif_salle")

    op.drop_index("ix_planifications_date_examen", table_name="planifications")
    op.drop_index("ix_planifications_section_matiere_id", table_name="planifications")
    op.drop_index("ix_planifications_section_id", table_name="planifications")
    op.drop_index("ix_planifications_session_id", table_name="planifications")
    op.drop_table("planifications")
