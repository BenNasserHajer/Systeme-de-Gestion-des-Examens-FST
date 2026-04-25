"""Planification ORM models used by the P1 exam-planning module."""

from datetime import date, time

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Planification(Base):
    __tablename__ = "planifications"
    __table_args__ = (
        UniqueConstraint(
            "section_matiere_id",
            "session_id",
            "type_epreuve",
            name="uq_planif_section_matiere_session_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
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
    coefficient: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    section_nb_etudiants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    mode_affectation: Mapped[str] = mapped_column(String(24), nullable=False, default="AUTO")
    statut: Mapped[str] = mapped_column(String(24), nullable=False, default="BROUILLON")
    nb_groupes: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    nb_surveillants_requis: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    salles_affectees: Mapped[list["PlanifSalle"]] = relationship(
        "PlanifSalle",
        back_populates="planification",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    surveillances: Mapped[list["Surveillance"]] = relationship("Surveillance", lazy="selectin")

    @property
    def duree_effective(self) -> int:
        return self.duree


class PlanifSalle(Base):
    __tablename__ = "planif_salle"
    __table_args__ = (
        UniqueConstraint("planification_id", "salle_id", name="uq_planif_salle_planif_salle"),
        UniqueConstraint("planification_id", "groupe_id", name="uq_planif_salle_planif_groupe"),
        UniqueConstraint("salle_id", "creneau_date", "heure_debut", name="uq_salle_creneau_unique"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    planification_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("planifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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
