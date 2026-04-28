"""Salle, Creneau, Session ORM models — alignés sur le script SQL."""

from datetime import date, time

from sqlalchemy import Integer, String, Date, Time, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Salle(Base):
    __tablename__ = "salle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capacite: Mapped[int] = mapped_column(Integer, nullable=False)
    batiment: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relations
    planif_salles: Mapped[list["PlanifSalle"]] = relationship(
        "PlanifSalle", back_populates="salle", lazy="selectin"
    )
    surveillances: Mapped[list["Surveillance"]] = relationship(
        "Surveillance", back_populates="salle", lazy="selectin"
    )


class Creneau(Base):
    __tablename__ = "creneau"
    __table_args__ = (UniqueConstraint("date", "heure_debut", name="uq_creneau_date_heure"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    heure_debut: Mapped[time] = mapped_column(Time, nullable=False)
    heure_fin: Mapped[time] = mapped_column(Time, nullable=False)
    libelle: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relations
    planifications: Mapped[list["Planification"]] = relationship(
        "Planification", back_populates="creneau", lazy="selectin"
    )


class Session(Base):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type_session: Mapped[str] = mapped_column(String(50), nullable=False)   # PRINCIPALE, RATTRAPAGE
    annee_universitaire: Mapped[str] = mapped_column(String(10), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    statut: Mapped[str] = mapped_column(String(24), nullable=False, default="BROUILLON")

    # Relations
    planifications: Mapped[list["Planification"]] = relationship(
        "Planification", back_populates="session", lazy="selectin"
    )