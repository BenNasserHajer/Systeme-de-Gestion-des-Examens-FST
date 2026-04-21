"""Model exports for metadata and imports.

IMPORTANT: Imports ordered by dependencies to avoid circular import issues.
"""

from app.models.base import Base

# 1. Base models (no external dependencies)
from app.models.departement_niveau_section import Departement, Niveau, Section, Groupe
from app.models.salle_session import Salle, Creneau, Session
from app.models.matiere import Matiere, SectionMatiere

# 2. Models depending on base models
from app.models.enseignant import Enseignant, ChargeHoraire, Enseignement
from app.models.disponibilite import DisponibiliteEnseignant

# 3. Planification models
from app.models.planification import PlanifSalle, Planification

# 4. Surveillance model (depends on Enseignant and Planification)
from app.models.surveillance import Surveillance

__all__ = [
    "Base",
    # Departement/Niveau/Section
    "Departement",
    "Niveau",
    "Section",
    "Groupe",
    # Salle/Creneau/Session
    "Salle",
    "Creneau",
    "Session",
    # Matiere
    "Matiere",
    "SectionMatiere",
    # Enseignant
    "Enseignant",
    "ChargeHoraire",
    "Enseignement",
    "DisponibiliteEnseignant",
    # Planification
    "Planification",
    "PlanifSalle",
    # Surveillance
    "Surveillance",
]