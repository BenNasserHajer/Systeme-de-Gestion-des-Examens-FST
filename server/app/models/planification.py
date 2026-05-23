"""Planification & PlanifSalle ORM models — alignés sur le script SQL."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Planification(Base):
    __tablename__ = "planification_examen"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "section_matiere_id", "creneau_id", "type_epreuve",
            name="uq_planif_session_section_creneau_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("session.id", ondelete="CASCADE"), nullable=False, index=True
    )
    departement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departement.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_matiere_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("section_matiere.id", ondelete="CASCADE"), nullable=False, index=True
    )
    creneau_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("creneau.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_epreuve: Mapped[str] = mapped_column(String(50), nullable=False)  # EXAMEN_FINAL, DS
    # ✅ CHAMP MANQUANT dans l'ancien model — présent dans le SQL
    semestre: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 ou 2
    session_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    section_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    section_matiere_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    section_departement_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    matiere: Mapped[str] = mapped_column(String(120), nullable=False)
    type_epreuve: Mapped[str] = mapped_column(String(24), nullable=False, default="EXAMEN_FINAL")

    date_examen: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    heure_debut: Mapped[time] = mapped_column(Time, nullable=False)
    heure_fin: Mapped[time] = mapped_column(Time, nullable=False)

    session_date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    session_date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    session_statut: Mapped[str] = mapped_column(String(24), nullable=False, default="BROUILLON")

    duree: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    mode_affectation: Mapped[str] = mapped_column(String(50), nullable=False, default="AUTOMATIQUE")
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="BROUILLON")
    nb_groupes: Mapped[int] = mapped_column(Integer, default=1)
    nb_surveillants_requis: Mapped[int] = mapped_column(Integer, default=2)

    # Relations bidirectionnelles
    session: Mapped["Session"] = relationship("Session", back_populates="planifications")
    departement: Mapped["Departement"] = relationship("Departement", lazy="selectin")
    section_matiere: Mapped["SectionMatiere"] = relationship(
        "SectionMatiere", back_populates="planifications", lazy="selectin"
    )
    creneau: Mapped["Creneau"] = relationship("Creneau", back_populates="planifications", lazy="selectin")

    salles_affectees: Mapped[list["PlanifSalle"]] = relationship(
        "PlanifSalle",
        back_populates="planification",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    surveillances: Mapped[list["Surveillance"]] = relationship(
        "Surveillance",
        back_populates="planification",
        lazy="selectin",
    )


class PlanifSalle(Base):
    __tablename__ = "planif_salle"

    # Clé primaire composite
    planification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("planification_examen.id", ondelete="CASCADE"),
        primary_key=True, nullable=False, index=True,
    )
    salle_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    salle_capacite: Mapped[int] = mapped_column(Integer, nullable=False)
    salle_batiment: Mapped[str] = mapped_column(String(64), nullable=True)
    salle_departement_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    groupe_id: Mapped[int] = mapped_column(Integer, nullable=False)
    groupe_effectif: Mapped[int] = mapped_column(Integer, nullable=False)

    creneau_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    heure_debut: Mapped[time] = mapped_column(Time, nullable=False)

    planification: Mapped[Planification] = relationship("Planification", back_populates="salles_affectees")
