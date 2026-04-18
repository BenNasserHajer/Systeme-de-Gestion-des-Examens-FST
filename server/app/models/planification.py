"""Planification ORM model."""

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Planification(Base):
    __tablename__ = "planifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    matiere: Mapped[str] = mapped_column(String(120), nullable=False)
    salle: Mapped[str] = mapped_column(String(80), nullable=False)
    date_examen: Mapped[Date] = mapped_column(Date, nullable=False)
    statut: Mapped[str] = mapped_column(String(40), default="BROUILLON", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
