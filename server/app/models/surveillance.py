"""Surveillance ORM model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, Numeric, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.enseignant import Enseignant
    from app.models.planification_examen import PlanificationExamen


class Surveillance(Base):
    __tablename__ = "surveillance"
    __table_args__ = (UniqueConstraint("planification_id", "enseignant_id", name="uq_surv_planif_ens"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    planification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("planification_examen.id", ondelete="CASCADE"), nullable=False, index=True
    )
    enseignant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enseignant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Champs de surveillance
    est_externe: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    motif_externe: Mapped[str | None] = mapped_column(String(200), nullable=True)
    charge: Mapped[float] = mapped_column(Numeric(4, 2), default=1.0, nullable=False)
    presence: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mode_affectation: Mapped[str] = mapped_column(String(24), default="AUTOMATIQUE", nullable=False)
    statut_surveillance: Mapped[str] = mapped_column(
        String(24), default="AFFECTE", nullable=False
    )  # AFFECTE, CONFIRME
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    enseignant: Mapped["Enseignant"] = relationship("Enseignant", back_populates="surveillances")
    planification: Mapped["PlanificationExamen"] = relationship(
        "PlanificationExamen", back_populates="surveillances"
    )

