"""Surveillance ORM model."""

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Boolean, Numeric, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.enseignant import Enseignant


class Surveillance(Base):
    __tablename__ = "surveillances"
    __table_args__ = (UniqueConstraint("planification_id", "enseignant_id", name="uq_surv_planif_ens"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    planification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("planifications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    enseignant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enseignant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    charge: Mapped[float] = mapped_column(Numeric(4, 2), default=1.0, nullable=False)
    presence: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mode_affectation: Mapped[str] = mapped_column(String(24), default="AUTOMATIQUE", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    enseignant: Mapped["Enseignant"] = relationship("Enseignant", back_populates="surveillances")
