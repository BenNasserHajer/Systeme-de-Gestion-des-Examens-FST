"""Salle model."""

from sqlalchemy import Column, Integer, String
from app.database import Base


class Salle(Base):
    __tablename__ = "salle"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False, unique=True)
    capacite = Column(Integer, nullable=True)