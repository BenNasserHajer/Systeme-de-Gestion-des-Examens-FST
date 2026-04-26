"""Surveillance ORM model — aligné sur le script SQL."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, Numeric, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.enseignant import Enseignant
    from app.models.planification import Planification
    from app.models.departement_niveau_section import Groupe
    from app.models.salle_session import Salle


class Surveillance(Base):
    __tablename__ = "surveillance"
    __table_args__ = (
        UniqueConstraint(
            "planification_id", "enseignant_id", "groupe_id",
            name="uq_surv_planif_ens_groupe",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    planification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("planification_examen.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    enseignant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enseignant.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    groupe_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("groupe.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    # ✅ salle_id est un Integer FK vers salle.id — cohérent avec le SQL
    salle_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("salle.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    est_externe: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    motif_externe: Mapped[str | None] = mapped_column(String(200), nullable=True)
    charge: Mapped[float] = mapped_column(Numeric(4, 2), default=1.0, nullable=False)
    presence: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mode_affectation: Mapped[str] = mapped_column(String(24), default="AUTOMATIQUE", nullable=False)
    statut_surveillance: Mapped[str] = mapped_column(String(24), default="AFFECTE", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relations bidirectionnelles
    enseignant: Mapped["Enseignant"] = relationship(
        "Enseignant", back_populates="surveillances", lazy="selectin"
    )
    planification: Mapped["Planification"] = relationship(
        "Planification", back_populates="surveillances", lazy="selectin"
    )
    groupe: Mapped["Groupe | None"] = relationship("Groupe", lazy="selectin")
    salle: Mapped["Salle | None"] = relationship("Salle", back_populates="surveillances", lazy="selectin")