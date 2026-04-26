"""Enseignant, ChargeHoraire, Enseignement ORM models — alignés sur le script SQL."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.departement_niveau_section import Departement
    from app.models.matiere import Matiere
    from app.models.surveillance import Surveillance
    from app.models.disponibilite import DisponibiliteEnseignant


class Enseignant(Base):
    __tablename__ = "enseignant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(60), nullable=False)
    prenom: Mapped[str] = mapped_column(String(60), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    telephone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    departement_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departement.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relations
    departement: Mapped["Departement"] = relationship("Departement", back_populates="enseignants")
    charges_horaires: Mapped[list["ChargeHoraire"]] = relationship(
        "ChargeHoraire", back_populates="enseignant", cascade="all, delete-orphan", lazy="selectin"
    )
    enseignements: Mapped[list["Enseignement"]] = relationship(
        "Enseignement", back_populates="enseignant", cascade="all, delete-orphan", lazy="selectin"
    )
    disponibilites: Mapped[list["DisponibiliteEnseignant"]] = relationship(
        "DisponibiliteEnseignant", back_populates="enseignant", cascade="all, delete-orphan", lazy="selectin"
    )
    surveillances: Mapped[list["Surveillance"]] = relationship(
        "Surveillance", back_populates="enseignant", lazy="selectin"
    )


class ChargeHoraire(Base):
    __tablename__ = "charge_horaire"
    __table_args__ = (UniqueConstraint("enseignant_id", "annee_univ", name="uq_charge_ens_annee"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    enseignant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enseignant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    annee_univ: Mapped[str] = mapped_column(String(10), nullable=False)
    volume_horaire: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0.0)

    enseignant: Mapped["Enseignant"] = relationship("Enseignant", back_populates="charges_horaires")


class Enseignement(Base):
    """
    Enseignant ↔ Matière : qui enseigne quoi.
    La contrainte unique inclut annee_sem — alignée avec le SQL.
    """
    __tablename__ = "enseignement"
    __table_args__ = (
        UniqueConstraint(
            "enseignant_id", "matiere_id", "type_enseignement", "annee_sem",
            name="uq_enseignement_ens_mat_type_sem"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    enseignant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enseignant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    matiere_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("matiere.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_enseignement: Mapped[str] = mapped_column(String(50), nullable=False)  # COURS, TD, TP
    nb_heures: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    # ✅ PRÉSENT dans le SQL — inclus dans la contrainte unique
    annee_sem: Mapped[str | None] = mapped_column(String(20), nullable=True)

    enseignant: Mapped["Enseignant"] = relationship("Enseignant", back_populates="enseignements")
    matiere: Mapped["Matiere"] = relationship("Matiere", back_populates="enseignements")