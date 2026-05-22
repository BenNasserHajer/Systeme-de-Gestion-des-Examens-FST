

"""Salle model."""

from sqlalchemy import Column, Integer, String
from app.database import Base


class Salle(Base):
    __tablename__ = "salle"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), nullable=False, unique=True)
    designation = Column(String(100), nullable=True)
    capacite = Column(Integer, nullable=True)
    batiment = Column(String(50), nullable=True)