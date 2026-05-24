"""
models/compte_enseignant.py
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base


class CompteEnseignant(Base):
    __tablename__ = "compte_enseignant"

    id            = Column(Integer, primary_key=True, index=True)
    enseignant_id = Column(Integer, ForeignKey("enseignant.id", ondelete="CASCADE"),
                           nullable=False, unique=True)
    email         = Column(String(100), nullable=False, unique=True, index=True)
    mot_de_passe  = Column(String(255), nullable=False)
    type_compte   = Column(String(30),  nullable=False, default="ENSEIGNANT")
    actif         = Column(Boolean,     nullable=False, default=True)
    created_at    = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    updated_at    = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))

    enseignant = relationship("Enseignant", back_populates="compte")