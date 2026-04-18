# 🎓 Système de Gestion des Examens — DSI
**Stack :** FastAPI · Next.js · PostgreSQL  
**Équipe :** 4 personnes · Session 2025/2026

---

## 🗂️ Vue d'ensemble du projet

```
gestion-examens/
├── backend/          ← API FastAPI + PostgreSQL
└── frontend/         ← Interface Next.js 14
```

---

## 🔵 Légende des responsabilités

| Couleur | Personne | Module |
|---------|----------|--------|
| 🔵 **P1** | Backend Planification | Algorithme génération automatique |
| 🟢 **P2** | Backend Surveillance | Algorithme affectation surveillants |
| 🟠 **P3** | Frontend Planification | Pages admin + emploi du temps |
| 🔴 **P4** | Frontend Surveillance | Convocations + composants UI communs |
| ⚪ **Tous** | Partagé | Config, types communs, README |

---

## 🗄️ BACKEND — FastAPI

```
backend/
```

### `backend/app/main.py` ⚪ Tous
**Rôle :** Point d'entrée de l'application FastAPI.  
**Contenu attendu :**
- Création de l'instance `FastAPI(title="Gestion Examens DSI")`
- Inclusion de tous les routers (`planifications`, `surveillances`, `referentiel`)
- Configuration CORS pour autoriser le frontend Next.js
- Middleware de logging des requêtes

```python
# Exemple attendu
app = FastAPI(title="Gestion Examens DSI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"])
app.include_router(planifications.router, prefix="/api")
app.include_router(surveillances.router, prefix="/api")
```

---

### `backend/app/database.py` ⚪ Tous
**Rôle :** Configuration de la connexion PostgreSQL avec SQLAlchemy.  
**Contenu attendu :**
- Création du moteur SQLAlchemy depuis `DATABASE_URL`
- Fonction `get_db()` utilisée comme dépendance dans tous les routers
- `SessionLocal` pour la gestion des sessions

```python
# Exemple attendu
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/examens_db")
engine = create_engine(DATABASE_URL)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### `backend/app/config.py` ⚪ Tous
**Rôle :** Variables d'environnement centralisées avec Pydantic Settings.  
**Contenu attendu :**
- Classe `Settings` avec `DATABASE_URL`, `SECRET_KEY`, `DEBUG`
- Instance `settings` importée partout dans le projet

---

### `backend/app/exceptions.py` ⚪ Tous (créé par P1 en S1)
**Rôle :** Exceptions HTTP personnalisées réutilisées par tous.  
**Contenu attendu :**
- `PlanificationNotFound`, `SurveillanceConflict`, `ContrainteViolation`
- Toutes héritent de `HTTPException`
- Messages d'erreur clairs pour le frontend

---

## 📁 `backend/app/models/` — Modèles SQLAlchemy

### `backend/app/models/base.py` ⚪ Tous
**Rôle :** Classe de base SQLAlchemy partagée par tous les modèles.  
**Contenu attendu :**
- `Base = declarative_base()`
- Colonnes communes : `created_at`, `updated_at` en mixin

---

### `backend/app/models/planification.py` 🔵 P1
**Rôle :** Modèles ORM pour les tables `planification_examen` et `planif_salle`.  
**Contenu attendu :**
- Classe `PlanificationExamen` avec colonnes : `id`, `session_id`, `section_matiere_id`, `creneau_id`, `type_epreuve`, `duree`, `mode_affectation`, `statut`, `nb_groupes`, `nb_surveillants_requis`
- Classe `PlanifSalle` avec colonnes : `planification_id`, `salle_id`, `groupe_id`
- Relations SQLAlchemy vers `Session`, `SectionMatiere`, `Creneau`, `Salle`, `Groupe`
- Propriété `@property` pour calculer `duree_effective` depuis `SectionMatiere`

```python
# Exemple attendu
class PlanificationExamen(Base):
    __tablename__ = "planification_examen"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("session.id"), nullable=False)
    # ... toutes les colonnes du DDL PostgreSQL
    surveillances = relationship("Surveillance", back_populates="planification")
```

---

### `backend/app/models/surveillance.py` 🟢 P2
**Rôle :** Modèles ORM pour les tables `surveillance` et `disponibilite_enseignant`.  
**Contenu attendu :**
- Classe `Surveillance` avec colonnes : `id`, `planification_id`, `enseignant_id`, `charge`, `presence`, `mode_affectation`
- Classe `DisponibiliteEnseignant` avec colonnes : `id`, `enseignant_id`, `date`, `heure_debut`, `heure_fin`, `type_dispo`, `motif`, `confirme`
- Relation vers `PlanificationExamen` et `Enseignant`
- Méthode `couvre(date, heure)` qui vérifie si le créneau est couvert

```python
# Exemple attendu
class DisponibiliteEnseignant(Base):
    __tablename__ = "disponibilite_enseignant"
    # ...
    def couvre(self, date: date, heure: time) -> bool:
        """Retourne True si cette indisponibilité couvre le créneau donné."""
        return self.date == date and self.heure_debut <= heure <= self.heure_fin
```

---

## 📁 `backend/app/schemas/` — Schémas Pydantic

### `backend/app/schemas/commun.py` ⚪ Tous (défini S1 ensemble)
**Rôle :** Schémas Pydantic partagés — **à définir en réunion S1 avant tout développement**.  
**Contenu attendu :**
- `class Config: from_attributes = True` dans tous les schémas
- Enums Pydantic : `TypeSession`, `TypeEpreuve`, `TypeEnseignement`, `ModeAffectation`, `StatutPlanification`

---

### `backend/app/schemas/planification.py` 🔵 P1
**Rôle :** Validation des données entrantes/sortantes pour le module planification.  
**Contenu attendu :**
- `PlanificationCreate` : champs requis pour créer manuellement une planification
- `PlanificationUpdate` : champs modifiables (creneau, salle, statut)
- `PlanificationOut` : réponse complète avec relations imbriquées (salle, groupe, créneaux)
- `PlanifSalleOut` : salle + groupe associés
- `GenerationRequest` : `session_id`, `mode` (AUTO/MANUEL)
- `GenerationResult` : `nb_crees`, `nb_conflits`, `conflits: List[str]`

```python
# Exemple attendu — ce schéma est consommé par P3
class PlanificationOut(BaseModel):
    id: int
    type_epreuve: TypeEpreuve
    duree: int
    statut: StatutPlanification
    matiere: MatiereOut
    section: SectionOut
    creneau: CreneauOut
    salles: List[PlanifSalleOut]
    class Config:
        from_attributes = True
```

---

### `backend/app/schemas/surveillance.py` 🟢 P2
**Rôle :** Validation des données pour le module surveillance.  
**Contenu attendu :**
- `SurveillanceOut` : enseignant + planification + charge
- `ConvocationOut` : toutes les surveillances d'un enseignant pour une session
- `ChargeOut` : `enseignant_id`, `charge_total`, `charge_restante`, `pourcentage`
- `DisponibiliteCreate` : date + heure_debut + heure_fin + type_dispo
- `DisponibiliteOut` : avec id et motif
- `AffectationResult` : `nb_affectes`, `nb_manquants`, `manquants: List[str]`

---

## 📁 `backend/app/routers/` — Endpoints FastAPI

### `backend/app/routers/referentiel.py` ⚪ Tous (P3 peut contribuer)
**Rôle :** CRUD des données de base : departement, niveau, section, salle, creneau, matiere, enseignant, session.  
**Endpoints attendus :**

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/departements` | Liste des départements |
| GET/POST | `/api/niveaux` | Niveaux d'études |
| GET/POST | `/api/sections` | Sections par niveau |
| GET/POST | `/api/salles` | Salles disponibles |
| GET/POST | `/api/creneaux` | Créneaux horaires |
| GET/POST | `/api/matieres` | Matières |
| GET/POST | `/api/enseignants` | Enseignants |
| GET/POST | `/api/sessions` | Sessions d'examens |

---

### `backend/app/routers/planifications.py` 🔵 P1
**Rôle :** Tous les endpoints du module planification.  
**Endpoints attendus :**

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/sessions/{id}/generer` | Génération automatique |
| GET | `/api/planifications` | Liste avec filtres (session, section, date) |
| GET | `/api/planifications/{id}` | Détail d'une planification |
| PUT | `/api/planifications/{id}` | Modification manuelle |
| DELETE | `/api/planifications/{id}` | Suppression |
| POST | `/api/planifications/{id}/salles` | Affecter salle + groupe |
| GET | `/api/sessions/{id}/emploi-du-temps` | Vue calendrier complète |

**Qualité attendue :**
- Chaque endpoint doit avoir `response_model` explicite
- Codes HTTP corrects : 200, 201, 404, 409 (conflit)
- Pagination pour les listes : `skip=0&limit=50`

---

### `backend/app/routers/surveillances.py` 🟢 P2
**Rôle :** Tous les endpoints du module surveillance.  
**Endpoints attendus :**

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/planifications/{id}/affecter` | Affectation auto surveillants |
| GET | `/api/surveillances` | Liste avec filtre planification |
| PUT | `/api/surveillances/{id}` | Modification manuelle |
| DELETE | `/api/surveillances/{id}` | Suppression |
| GET | `/api/enseignants/{id}/charge` | Charge d'un enseignant |
| GET | `/api/enseignants/{id}/convocation` | Convocation complète |
| POST | `/api/enseignants/{id}/disponibilites` | Déclarer indisponibilité |
| GET | `/api/enseignants/{id}/disponibilites` | Liste des indispos |
| GET | `/api/enseignants/disponibles` | Enseignants dispo pour un créneau |

---

## 📁 `backend/app/services/` — Logique métier

### `backend/app/services/planif_service.py` 🔵 P1
**Rôle :** Toute la logique métier de planification — jamais appelé directement par le router.  
**Fonctions attendues :**

```python
def generer_planifications(session_id: int, db: Session) -> GenerationResult:
    """
    Génère automatiquement toutes les planifications pour une session.
    Pour chaque SectionMatiere active :
      1. Cherche un créneau disponible
      2. Cherche une ou plusieurs salles selon nb_etudiants
      3. Crée les groupes si nécessaire
      4. Vérifie toutes les contraintes
      5. Enregistre en base
    Retourne le nombre de planifications créées et la liste des conflits.
    """

def affecter_salles(planif_id: int, salle_ids: List[int], db: Session) -> PlanificationOut:
    """Affecte manuellement des salles à une planification existante."""

def get_emploi_du_temps(session_id: int, db: Session) -> List[PlanificationOut]:
    """Retourne toutes les planifications d'une session, triées par date et créneau."""
```

---

### `backend/app/services/surv_service.py` 🟢 P2
**Rôle :** Logique métier d'affectation des surveillants.  
**Fonctions attendues :**

```python
def affecter_surveillants(planif_id: int, db: Session) -> AffectationResult:
    """
    Affecte automatiquement les surveillants à une planification.
    Algorithme :
      1. Récupère les enseignants triés par charge_restante DESC
      2. Pour chaque candidat, vérifie :
         - Disponible sur ce créneau (DisponibiliteEnseignant)
         - N'enseigne pas cette matière (Enseignement)
         - < 2 séances ce jour-là (ContrainteSeancesConsecutives)
         - Salle pas déjà pleine (ContrainteDisponibSalle)
      3. Affecte et met à jour charge_restante
    """

def get_convocation(enseignant_id: int, session_id: int, db: Session) -> ConvocationOut:
    """Retourne toutes les surveillances d'un enseignant pour une session."""
```

---

### `backend/app/services/charge_service.py` 🟢 P2
**Rôle :** Calcul et mise à jour des charges de surveillance.  
**Fonctions attendues :**

```python
def calculer_charge(type_epreuve: str, type_formation: str) -> float:
    """
    Retourne la valeur de charge selon le barème :
    - DS Prépa : 1.5  | DS DSI : 1.0
    - EX Prépa : 2.0  | EX DSI : 1.5
    """

def mettre_a_jour_charge_restante(enseignant_id: int, db: Session) -> float:
    """Recalcule charge_restante = charge_total - somme des surveillances confirmées."""

def get_tableau_charges(session_id: int, db: Session) -> List[ChargeOut]:
    """Retourne tous les enseignants avec leur taux d'utilisation pour une session."""
```

---

## 📁 `backend/app/algorithms/` — Algorithmes

### `backend/app/algorithms/contraintes.py` 🔵 P1
**Rôle :** Implémentation du pattern Stratégie pour les règles métier.  
**Contenu attendu :**

```python
from abc import ABC, abstractmethod

class Contrainte(ABC):
    """Classe abstraite — chaque sous-classe encode une règle métier."""
    def __init__(self, priorite: int, active: bool = True):
        self.priorite = priorite
        self.active = active

    @abstractmethod
    def verifier(self, planif: dict, enseignant: dict, db: Session) -> bool:
        """Retourne True si la contrainte est respectée."""

    @abstractmethod
    def get_message(self) -> str:
        """Message d'erreur si la contrainte est violée."""


class ContrainteChargeEnseignant(Contrainte):
    """Un enseignant sans charge restante ne peut pas surveiller."""
    def verifier(self, planif, enseignant, db) -> bool:
        return enseignant["charge_restante"] > 0

class ContraintePasLeurMatiere(Contrainte):
    """Un enseignant ne surveille pas sa propre matière."""
    def verifier(self, planif, enseignant, db) -> bool:
        # Vérifier dans table Enseignement
        ...

class ContrainteSeancesConsecutives(Contrainte):
    """Max 2 séances par jour par enseignant."""
    def __init__(self):
        super().__init__(priorite=2)
        self.max_seances_jour = 2

class ContrainteDisponibSalle(Contrainte):
    """Une salle ne peut pas être affectée deux fois sur le même créneau."""
    ...
```

---

### `backend/app/algorithms/planif_auto.py` 🔵 P1
**Rôle :** Algorithme principal de génération automatique des planifications.  
**Contenu attendu :**
- Fonction `generer(session_id, db)` qui itère sur toutes les `SectionMatiere`
- Pour chaque matière : cherche créneau libre + salle(s) disponible(s)
- Découpe en groupes si `section.nb_etudiants > salle.capacite`
- Appelle `ContrainteEngine.verifier_toutes()` avant chaque insertion
- En cas d'échec : enregistre le conflit et continue (mode best-effort)

---

### `backend/app/algorithms/surv_auto.py` 🟢 P2
**Rôle :** Algorithme d'affectation automatique des surveillants.  
**Contenu attendu :**
- Fonction `affecter(planif_id, db)` 
- Tri des enseignants par `charge_restante DESC` (priorité aux plus chargés)
- Boucle sur les candidats, vérifie toutes les contraintes
- Affecte `nb_surveillants_requis` enseignants par planification
- Met à jour `charge_restante` après chaque affectation

---

## 📁 `backend/app/crud/` — Accès base de données

### `backend/app/crud/crud_planif.py` 🔵 P1
**Rôle :** Toutes les opérations SQL pour le module planification.  
**Fonctions attendues :**
- `get_planification(db, id)` → `PlanificationExamen | None`
- `get_planifications(db, session_id, skip, limit)` → `List[PlanificationExamen]`
- `create_planification(db, data)` → `PlanificationExamen`
- `update_planification(db, id, data)` → `PlanificationExamen`
- `delete_planification(db, id)` → `bool`
- `get_salles_disponibles(db, creneau_id, capacite_min)` → `List[Salle]`
- `get_creneaux_libres(db, session_id, section_id)` → `List[Creneau]`

---

### `backend/app/crud/crud_surv.py` 🟢 P2
**Rôle :** Toutes les opérations SQL pour le module surveillance.  
**Fonctions attendues :**
- `get_enseignants_disponibles(db, creneau_id)` → `List[Enseignant]`
- `create_surveillance(db, planif_id, enseignant_id, charge)` → `Surveillance`
- `get_surveillances_enseignant(db, enseignant_id, session_id)` → `List[Surveillance]`
- `get_disponibilites(db, enseignant_id)` → `List[DisponibiliteEnseignant]`
- `create_disponibilite(db, data)` → `DisponibiliteEnseignant`

---

## 📁 `backend/alembic/versions/`

### `backend/alembic/versions/001_planif.py` 🔵 P1
**Rôle :** Migration Alembic pour créer `planification_examen` et `planif_salle`.  
**Contenu attendu :**
- Fonctions `upgrade()` et `downgrade()`
- Création des tables avec toutes les contraintes FK
- Index sur `session_id`, `creneau_id`, `section_matiere_id`

---

### `backend/alembic/versions/002_surv.py` 🟢 P2
**Rôle :** Migration Alembic pour créer `surveillance` et `disponibilite_enseignant`.  
**Contenu attendu :**
- Dépend de `001_planif.py` (champ `depends_on`)
- Index sur `enseignant_id`, `date` pour les disponibilités

---

## 📁 `backend/tests/`

### `backend/tests/test_planif.py` 🔵 P1
**Rôle :** Tests unitaires du module planification.  
**Tests attendus :**
- `test_generer_planification_simple` : section 15 étudiants, salle 30 places → 1 groupe
- `test_generer_planification_split` : section 35 étudiants, salle 20 places → 2 groupes
- `test_contrainte_salle_occupee` : même salle, même créneau → conflit détecté
- `test_mode_manuel` : création manuelle d'une planification
- `test_get_emploi_du_temps` : retourne les planifications triées par date

---

### `backend/tests/test_surv.py` 🟢 P2
**Rôle :** Tests unitaires du module surveillance.  
**Tests attendus :**
- `test_affecter_surveillant_disponible` : enseignant dispo → affecté
- `test_refuser_leur_matiere` : enseignant enseigne la matière → refusé
- `test_calcul_charge` : DS DSI → charge = 1.0, EX Prépa → charge = 2.0
- `test_max_seances_jour` : déjà 2 séances ce jour → refusé
- `test_convocation` : retourne toutes les séances d'un enseignant

---

## 🌐 FRONTEND — Next.js 14

```
frontend/src/
```

---

## 📁 `frontend/src/app/` — Pages (App Router)

### `frontend/src/app/layout.tsx` 🔴 P4
**Rôle :** Layout racine de l'application — englobe toutes les pages.  
**Contenu attendu :**
- Import des composants `Navbar` et `Sidebar`
- Provider React Query (`QueryClientProvider`)
- Métadonnées globales (`metadata`)
- Police et styles globaux

---

### `frontend/src/app/(admin)/planification/page.tsx` 🟠 P3
**Rôle :** Page principale de gestion des planifications.  
**Contenu attendu :**
- Tableau de toutes les planifications de la session active
- Bouton **"Générer automatiquement"** → appelle `POST /api/sessions/{id}/generer`
- Indicateur de chargement pendant la génération (peut durer quelques secondes)
- Filtres : par date, par section, par statut
- Lien vers la vue emploi du temps
- Message de succès avec `nb_crees` et liste des conflits si `nb_conflits > 0`

---

### `frontend/src/app/(admin)/planification/[id]/edit/page.tsx` 🟠 P3
**Rôle :** Formulaire d'édition manuelle d'une planification.  
**Contenu attendu :**
- Champs modifiables : créneau, salle(s), statut
- Select des salles disponibles (filtré selon le créneau choisi)
- Affichage des groupes et leur effectif
- Bouton "Valider" et "Annuler"
- Redirection vers la liste après sauvegarde

---

### `frontend/src/app/(admin)/surveillance/page.tsx` 🔴 P4
**Rôle :** Page de gestion des affectations de surveillance.  
**Contenu attendu :**
- Tableau des planifications avec leurs surveillants affectés
- Bouton **"Affecter automatiquement"** par planification
- Bouton **"Affecter manuellement"** → modal de sélection d'enseignant
- Code couleur sur la colonne charge : vert (< 50%), orange (50-80%), rouge (> 80%)
- Filtre par date et par enseignant

---

### `frontend/src/app/(admin)/salles/page.tsx` 🟠 P3
**Rôle :** CRUD des salles d'examen.  
**Contenu attendu :**
- Tableau avec colonnes : code, désignation, capacité, bâtiment
- Bouton "Ajouter une salle" → formulaire modal
- Actions par ligne : modifier, supprimer
- Validation : capacité > 0, code unique

---

### `frontend/src/app/(admin)/matieres/page.tsx` 🟠 P3
**Rôle :** CRUD des matières.  
**Contenu attendu :**
- Tableau avec colonnes : code, intitulé, coefficient, aExamenFinal, aDS
- Toggle pour activer/désactiver aExamenFinal et aDS
- Formulaire d'ajout/modification

---

### `frontend/src/app/(admin)/enseignants/page.tsx` 🔴 P4
**Rôle :** Liste des enseignants avec leur charge.  
**Contenu attendu :**
- Tableau avec colonnes : nom, grade, chargeTotal, chargeRestante, % utilisé
- Barre de progression visuelle pour la charge
- Lien vers les disponibilités de chaque enseignant
- Lien vers la convocation de chaque enseignant

---

### `frontend/src/app/(enseignant)/convocation/page.tsx` 🔴 P4
**Rôle :** Vue personnelle d'un enseignant — ses surveillances.  
**Contenu attendu :**
- Liste de toutes ses séances : date, heure, salle, matière
- Charge totale affectée
- Bouton **"Exporter en PDF"** → génère la convocation officielle
- Formulaire "Déclarer une indisponibilité" avec calendrier

---

## 📁 `frontend/src/components/` — Composants React

## `frontend/src/components/ui/` — Composants partagés 🔴 P4

### `DataTable.tsx`
**Rôle :** Tableau générique réutilisable par P3 et P4.  
**Props attendues :**
```typescript
interface Props<T> {
  data: T[]
  columns: Column<T>[]   // { key, label, render? }
  isLoading: boolean
  onEdit?: (row: T) => void
  onDelete?: (row: T) => void
  emptyMessage?: string
}
```

### `Modal.tsx`
**Rôle :** Modale réutilisable pour les formulaires.  
**Props attendues :** `isOpen`, `onClose`, `title`, `children`, `size`

### `LoadingSpinner.tsx`
**Rôle :** Indicateur de chargement centré.  
**Utilisation :** Affiché quand `isLoading = true` dans tous les hooks React Query.

### `Badge.tsx`
**Rôle :** Badge coloré pour les statuts.  
**Props attendues :** `status: 'BROUILLON' | 'VALIDEE' | 'PUBLIEE'` → couleur automatique.

### `Navbar.tsx`
**Rôle :** Barre de navigation supérieure.  
**Contenu attendu :** Logo, titre "Gestion Examens DSI", lien déconnexion.

### `Sidebar.tsx`
**Rôle :** Menu latéral de navigation.  
**Liens attendus :** Planification, Surveillance, Salles, Matières, Enseignants, Convocations.

---

## `frontend/src/components/planification/` 🟠 P3

### `EmploiDuTemps.tsx`
**Rôle :** Vue calendrier de l'emploi du temps par semaine.  
**Contenu attendu :**
- Grille : colonnes = jours, lignes = créneaux (8h30 / 11h00 / 14h00)
- Chaque cellule affiche : matière + section + salle
- Code couleur par section
- Clic sur une cellule → détail de la planification

### `PlanifCard.tsx`
**Rôle :** Carte d'une planification dans la liste.  
**Contenu attendu :**
- Matière + section + créneau + salle(s)
- Badge statut (`BROUILLON` / `VALIDEE` / `PUBLIEE`)
- Boutons : modifier, supprimer, affecter surveillants

### `GroupeTable.tsx`
**Rôle :** Tableau des groupes d'une planification.  
**Contenu attendu :**
- Colonnes : Groupe n°, Effectif, Salle affectée, Capacité salle
- Indicateur si effectif > capacité (anomalie en rouge)

---

## `frontend/src/components/surveillance/` 🔴 P4

### `ChargeTable.tsx`
**Rôle :** Tableau des charges de surveillance par enseignant.  
**Contenu attendu :**
- Colonnes : Nom, Grade, Charge totale, Affectée, Restante, % utilisé
- Barre de progression colorée (vert / orange / rouge)
- Tri par charge restante décroissante

### `ConvocationCard.tsx`
**Rôle :** Carte de convocation d'un enseignant (version écran).  
**Contenu attendu :**
- En-tête : nom, grade, email, téléphone
- Tableau des séances : date, heure, salle, matière surveillée
- Total des charges
- Bouton export PDF

### `DisponibiliteForm.tsx`
**Rôle :** Formulaire de déclaration d'indisponibilité.  
**Contenu attendu :**
- Champs : date, heure début, heure fin, type (CONGE / MISSION / COURS_PREVU), motif
- Validation : heure fin > heure debut, date dans la période de session
- Liste des indisponibilités existantes avec bouton supprimer

---

## 📁 `frontend/src/lib/` — Couche API et utilitaires

### `frontend/src/lib/api/client.ts` ⚪ Tous (P4 crée en S1)
**Rôle :** Client HTTP centralisé — seul fichier qui lit `NEXT_PUBLIC_API_URL`.  
**Contenu attendu :**
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
```

---

### `frontend/src/lib/api/planification.ts` 🟠 P3
**Rôle :** Toutes les fonctions d'appel API du module planification.  
**Fonctions attendues :**
```typescript
export const planificationApi = {
  generer: (sessionId: number) =>
    apiFetch<GenerationResult>(`/api/sessions/${sessionId}/generer`, { method: "POST" }),

  getAll: (sessionId: number) =>
    apiFetch<PlanificationOut[]>(`/api/planifications?session=${sessionId}`),

  getById: (id: number) =>
    apiFetch<PlanificationOut>(`/api/planifications/${id}`),

  update: (id: number, data: PlanificationUpdate) =>
    apiFetch<PlanificationOut>(`/api/planifications/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  getEmploiDuTemps: (sessionId: number) =>
    apiFetch<PlanificationOut[]>(`/api/sessions/${sessionId}/emploi-du-temps`),
}
```

---

### `frontend/src/lib/api/surveillance.ts` 🔴 P4
**Rôle :** Toutes les fonctions d'appel API du module surveillance.  
**Fonctions attendues :**
```typescript
export const surveillanceApi = {
  affecter: (planifId: number) =>
    apiFetch<AffectationResult>(`/api/planifications/${planifId}/affecter`, { method: "POST" }),

  getCharge: (enseignantId: number) =>
    apiFetch<ChargeOut>(`/api/enseignants/${enseignantId}/charge`),

  getConvocation: (enseignantId: number, sessionId: number) =>
    apiFetch<ConvocationOut>(`/api/enseignants/${enseignantId}/convocation?session=${sessionId}`),

  ajouterDisponibilite: (enseignantId: number, data: DisponibiliteCreate) =>
    apiFetch<DisponibiliteOut>(`/api/enseignants/${enseignantId}/disponibilites`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
}
```

---

### `frontend/src/lib/types/planification.ts` 🟠 P3
**Rôle :** Interfaces TypeScript miroir des schémas Pydantic de P1.  
**Contenu attendu :**
```typescript
// Ces types DOIVENT correspondre exactement aux schémas Pydantic de P1
export interface PlanificationOut {
  id: number
  type_epreuve: "EXAMEN_FINAL" | "DS"
  duree: number
  statut: "BROUILLON" | "VALIDEE" | "PUBLIEE"
  matiere: MatiereOut
  section: SectionOut
  creneau: CreneauOut
  salles: PlanifSalleOut[]
  nb_groupes: number
}

export interface GenerationResult {
  nb_crees: number
  nb_conflits: number
  conflits: string[]
}
```

---

### `frontend/src/lib/types/surveillance.ts` 🔴 P4
**Rôle :** Interfaces TypeScript miroir des schémas Pydantic de P2.  
**Contenu attendu :**
```typescript
export interface SurveillanceOut {
  id: number
  enseignant: EnseignantOut
  planification: PlanificationOut
  charge: number
  presence: boolean
}

export interface ConvocationOut {
  enseignant: EnseignantOut
  session: SessionOut
  surveillances: SurveillanceOut[]
  charge_totale: number
}

export interface ChargeOut {
  enseignant_id: number
  nom: string
  charge_total: number
  charge_affectee: number
  charge_restante: number
  pourcentage: number
}
```

---

## 📁 `frontend/src/hooks/` — React Query Hooks

### `frontend/src/hooks/usePlanification.ts` 🟠 P3
**Rôle :** Hooks React Query pour le module planification.  
**Contenu attendu :**
```typescript
// Chaque hook gère automatiquement isLoading, isError, data
export function usePlanifications(sessionId: number) {
  return useQuery({
    queryKey: ["planifications", sessionId],
    queryFn: () => planificationApi.getAll(sessionId),
  })
}

export function useGenererPlanification() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (sessionId: number) => planificationApi.generer(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planifications"] })
    },
  })
}
```

---

### `frontend/src/hooks/useSurveillance.ts` 🔴 P4
**Rôle :** Hooks React Query pour le module surveillance.  
**Contenu attendu :**
- `useConvocation(enseignantId, sessionId)` → données de la convocation
- `useChargeEnseignants(sessionId)` → tableau de charges pour tous
- `useAffecter()` → mutation pour déclencher l'affectation auto
- `useAjouterDisponibilite()` → mutation pour déclarer une indisponibilité

---

## ⚙️ Fichiers de configuration

### `backend/.env` ⚪ Tous
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/examens_db
SECRET_KEY=votre_cle_secrete_longue
DEBUG=True
```

### `backend/requirements.txt` ⚪ Tous
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.2
```

### `frontend/.env.local` ⚪ Tous
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### `frontend/package.json` — dépendances principales ⚪ Tous
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "^18",
    "typescript": "^5",
    "@tanstack/react-query": "^5.0.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "@react-pdf/renderer": "^3.1.0"
  }
}
```

---

## 🚀 Comment lancer le projet

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head            # Crée les tables
uvicorn app.main:app --reload   # Lance sur http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                     # Lance sur http://localhost:3000
```

### Documentation API automatique
```
http://localhost:8000/docs      ← Swagger UI (très utile pour la soutenance)
http://localhost:8000/redoc     ← ReDoc
```

---

## 📋 Checklist avant soutenance

### P1 — Backend Planification 🔵
- [ ] Tous les modèles SQLAlchemy avec relations correctes
- [ ] Schémas Pydantic avec `from_attributes = True`
- [ ] Algorithme de génération fonctionne sur les données réelles
- [ ] 4 contraintes implémentées et testées
- [ ] Endpoints documentés avec `response_model` et codes HTTP corrects
- [ ] Tests unitaires passent (`pytest tests/test_planif.py`)
- [ ] Capable d'expliquer l'algorithme de génération au jury

### P2 — Backend Surveillance 🟢
- [ ] Modèles `Surveillance` et `DisponibiliteEnseignant` complets
- [ ] Algorithme d'affectation trie par `charge_restante DESC`
- [ ] Vérification des 3 contraintes : disponibilité, matière, séances/jour
- [ ] `ChargeService` calcule et met à jour correctement
- [ ] Endpoint convocation retourne toutes les séances
- [ ] Tests unitaires passent (`pytest tests/test_surv.py`)
- [ ] Capable d'expliquer le calcul de charge au jury

### P3 — Frontend Planification 🟠
- [ ] Composants UI partagés de P4 intégrés
- [ ] Page génération affiche un spinner pendant l'attente
- [ ] Emploi du temps en grille (jours × créneaux)
- [ ] Formulaire d'édition manuelle fonctionnel
- [ ] Tous les appels API passent par `lib/api/planification.ts`
- [ ] Types TypeScript correspondent aux schémas Pydantic de P1
- [ ] Gestion `isLoading` et `isError` dans toutes les pages

### P4 — Frontend Surveillance 🔴
- [ ] Composants partagés livrés en S1 : `DataTable`, `Modal`, `LoadingSpinner`, `Badge`
- [ ] Tableau de charges avec code couleur
- [ ] Formulaire disponibilités avec validation Zod
- [ ] Page convocation affiche toutes les séances d'un enseignant
- [ ] Export PDF fonctionne avec react-pdf
- [ ] `lib/api/client.ts` lit `NEXT_PUBLIC_API_URL`

### Commun ⚪
- [ ] Le projet se lance en suivant les instructions ci-dessus
- [ ] Pas d'URL en dur dans le code
- [ ] Pas de `console.error` non gérés
- [ ] Git : chaque personne a commité sur sa branche
- [ ] La démo bout en bout fonctionne : générer → affecter → convocation → PDF

---

## 🌿 Branches Git

```
main              ← production (ne jamais pousser directement)
develop           ← intégration (PR obligatoire)
├── feat/p1-planif-backend
├── feat/p2-surv-backend
├── feat/p3-planif-frontend
└── feat/p4-surv-frontend
```

**Règle :** Avant de fusionner dans `develop`, l'autre personne du même module relit le code (P1 relit P2, P3 relit P4).