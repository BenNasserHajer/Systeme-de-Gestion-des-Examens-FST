"""Matiere & SectionMatiere ORM models — alignés sur le script SQL."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Numeric, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.departement_niveau_section import Section
    from app.models.enseignant import Enseignement


class Matiere(Base):
    __tablename__ = "matiere"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    intitule: Mapped[str] = mapped_column(String(150), nullable=False)
    coefficient: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=1.0)
    credit: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    a_examen_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    a_ds: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    duree_examen: Mapped[int | None] = mapped_column(Integer, nullable=True, default=120)
    duree_ds: Mapped[int | None] = mapped_column(Integer, nullable=True, default=60)

    # Relations
    section_matieres: Mapped[list["SectionMatiere"]] = relationship(
        "SectionMatiere",
        back_populates="matiere",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    enseignements: Mapped[list["Enseignement"]] = relationship(
        "Enseignement",
        back_populates="matiere",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SectionMatiere(Base):
    """
    Liaison Section ↔ Matière pour une période donnée (annee_sem).
    Le champ annee_sem est OBLIGATOIRE (ex: '2025/2026-S1') — présent dans le SQL.
    """
    __tablename__ = "section_matiere"
    __table_args__ = (
        UniqueConstraint("section_id", "matiere_id", "annee_sem", name="uq_section_matiere_annee"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("section.id", ondelete="CASCADE"), nullable=False, index=True
    )
    matiere_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("matiere.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # ✅ CHAMP MANQUANT dans l'ancien model — présent dans le SQL
    annee_sem: Mapped[str] = mapped_column(String(20), nullable=False)  # ex: "2025/2026-S1"
    a_examen_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    a_ds: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    duree_examen: Mapped[int | None] = mapped_column(Integer, nullable=True, default=120)
    duree_ds: Mapped[int | None] = mapped_column(Integer, nullable=True, default=60)

    # Relations
    section: Mapped["Section"] = relationship("Section", back_populates="section_matieres")
    matiere: Mapped["Matiere"] = relationship("Matiere", back_populates="section_matieres")
    planifications: Mapped[list["Planification"]] = relationship(
        "Planification", back_populates="section_matiere", lazy="selectin"
    )