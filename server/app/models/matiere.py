"""Matiere & SectionMatiere ORM models."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Numeric, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.departement_niveau_section import Section


class Matiere(Base):
    __tablename__ = "matiere"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    intitule: Mapped[str] = mapped_column(String(150), nullable=False)
    coefficient: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=1.0)
    credit: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    a_examen_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    a_ds: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    duree_examen: Mapped[int] = mapped_column(Integer, nullable=True, default=120)
    duree_ds: Mapped[int] = mapped_column(Integer, nullable=True, default=60)

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
    __tablename__ = "section_matiere"
    __table_args__ = (UniqueConstraint("section_id", "matiere_id", name="uq_section_matiere"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    section_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("section.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    matiere_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("matiere.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    a_examen_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    a_ds: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    duree_examen: Mapped[int] = mapped_column(Integer, nullable=True, default=120)
    duree_ds: Mapped[int] = mapped_column(Integer, nullable=True, default=60)

    section: Mapped["Section"] = relationship("Section", back_populates="section_matieres")
    matiere: Mapped["Matiere"] = relationship("Matiere", back_populates="section_matieres")
