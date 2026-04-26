"""Departement, Niveau, Section, Groupe ORM models."""

from sqlalchemy import Integer, String, UniqueConstraint, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Departement(Base):
    __tablename__ = "departement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)

    niveaux: Mapped[list["Niveau"]] = relationship(
        "Niveau",
        back_populates="departement",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    enseignants: Mapped[list["Enseignant"]] = relationship(
        "Enseignant",
        back_populates="departement",
        lazy="selectin",
    )


class Niveau(Base):
    __tablename__ = "niveau"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    # ❌ SUPPRIMÉ : annee (n'existe plus dans votre schéma)
    type_formation: Mapped[str] = mapped_column(String(50), nullable=False)
    departement_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departement.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    departement: Mapped["Departement"] = relationship("Departement", back_populates="niveaux")
    sections: Mapped[list["Section"]] = relationship(
        "Section",
        back_populates="niveau",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Section(Base):
    __tablename__ = "section"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # ❌ SUPPRIMÉ : nb_etudiants (n'existe plus dans votre schéma)
    niveau_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("niveau.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    niveau: Mapped["Niveau"] = relationship("Niveau", back_populates="sections")
    groupes: Mapped[list["Groupe"]] = relationship(
        "Groupe",
        back_populates="section",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    section_matieres: Mapped[list["SectionMatiere"]] = relationship(
        "SectionMatiere",
        back_populates="section",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Groupe(Base):
    __tablename__ = "groupe"
    __table_args__ = (UniqueConstraint("section_id", "numero", name="uq_groupe_section_numero"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    effectif: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # ✅ AJOUTÉ : nb_etudiants (nouvelle colonne dans votre schéma)
    nb_etudiants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # ✅ AJOUTÉ : annee (nouvelle colonne dans votre schéma)
    annee: Mapped[str] = mapped_column(String(10), nullable=False)
    section_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("section.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    section: Mapped["Section"] = relationship("Section", back_populates="groupes")