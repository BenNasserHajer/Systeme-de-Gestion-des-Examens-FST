"""DisponibiliteEnseignant ORM model."""

from datetime import date, time

from sqlalchemy import Integer, String, Boolean, ForeignKey, Date, Time, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DisponibiliteEnseignant(Base):
    __tablename__ = "disponibilite_enseignant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    enseignant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("enseignant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    heure_debut: Mapped[time] = mapped_column(Time, nullable=False)
    heure_fin: Mapped[time] = mapped_column(Time, nullable=False)
    type_dispo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="INDISPONIBLE",
    )  # DISPONIBLE, INDISPONIBLE, COURS_PREVU, MISSION, CONGE
    motif: Mapped[str] = mapped_column(String(200), nullable=True)
    confirme: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    enseignant: Mapped["Enseignant"] = relationship("Enseignant", back_populates="disponibilites")
