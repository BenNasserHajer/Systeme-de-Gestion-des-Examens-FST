"""Surveillance ORM model."""

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Surveillance(Base):
    __tablename__ = "surveillances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    planification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("planifications.id"), nullable=False, index=True
    )
    enseignant: Mapped[str] = mapped_column(String(120), nullable=False)
    statut: Mapped[str] = mapped_column(String(40), default="AFFECTEE", nullable=False)
    charge: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
