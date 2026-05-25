# 🔍 Exploration Backend - Gestion des Sessions

## 📋 Résumé Exécutif

Ce document détaille la structure et le fonctionnement de la gestion des sessions (S1, S2) dans le backend Flask/SQLAlchemy, incluant :
- Les modèles de données
- Les endpoints API
- Les créneaux d'examens
- Les dates de début/fin
- Les scripts de création

---

## 1️⃣ Modèles de Données ORM

### 📌 Table `session`

**Fichier**: [server/app/models/salle_session.py](server/app/models/salle_session.py#L44-L58)

```python
class Session(Base):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type_session: Mapped[str] = mapped_column(String(50), nullable=False)   # PRINCIPALE, RATTRAPAGE
    annee_universitaire: Mapped[str] = mapped_column(String(10), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    statut: Mapped[str] = mapped_column(String(24), nullable=False, default="BROUILLON")

    # Relations
    planifications: Mapped[list["Planification"]] = relationship(
        "Planification", back_populates="session", lazy="selectin"
    )
```

**Champs**:
| Champ | Type | Description |
|-------|------|-------------|
| `id` | INT | Clé primaire |
| `type_session` | VARCHAR(50) | "PRINCIPALE" ou "RATTRAPAGE" |
| `annee_universitaire` | VARCHAR(10) | Ex: "2025/2026" |
| `date_debut` | DATE | Début de la session d'examens |
| `date_fin` | DATE | Fin de la session d'examens |
| `statut` | VARCHAR(24) | "BROUILLON", "VALIDEE", "PUBLIEE" |

---

### 📌 Table `creneau`

**Fichier**: [server/app/models/salle_session.py](server/app/models/salle_session.py#L32-L43)

```python
class Creneau(Base):
    __tablename__ = "creneau"
    __table_args__ = (UniqueConstraint("date", "heure_debut", name="uq_creneau_date_heure"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    heure_debut: Mapped[time] = mapped_column(Time, nullable=False)
    heure_fin: Mapped[time] = mapped_column(Time, nullable=False)
    libelle: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relations
    planifications: Mapped[list["Planification"]] = relationship(
        "Planification", back_populates="creneau", lazy="selectin"
    )
```

**Constraint**: Unique(date, heure_debut)

---

## 2️⃣ Sessions Actuelles

### 📅 Définition Actuelle

**Fichier**: [server/app/seed/seed_data_v2.sql](server/app/seed/seed_data_v2.sql#L130-L150)

```sql
-- Session S1 (Semestre 1)
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut)
SELECT 'PRINCIPALE', '2025/2026', DATE '2026-01-07', DATE '2026-01-15', 'VALIDEE'
WHERE NOT EXISTS (...);

-- Session S2 (Semestre 2)
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut)
SELECT 'PRINCIPALE', '2025/2026', DATE '2026-05-11', DATE '2026-05-23', 'BROUILLON'
WHERE NOT EXISTS (...);
```

### 📊 Détails des Sessions

| Session | Année | Début | Fin | Jours | Statut |
|---------|-------|-------|-----|-------|--------|
| S1 | 2025/2026 | 2026-01-07 | 2026-01-15 | 8 jours | VALIDEE |
| S2 | 2025/2026 | 2026-05-11 | 2026-05-23 | 12 jours | BROUILLON |

### 📋 Créneaux pour S1 (7-15 janvier 2026)

**Fichier**: [server/app/seed/seed_data_v2.sql](server/app/seed/seed_data_v2.sql#L400-L420)

```sql
-- Créneaux générés pour chaque jour ouvrable (Lun-Sam)
-- Lundi 7 janvier (Mercredi)
- 08:30 → 10:30 (M1)
- 11:00 → 13:00 (M2)
- 14:00 → 16:00 (M3)

-- Suivi pour chaque jour jusqu'au 15 janvier
-- Total: ~24 créneaux (3 créneaux x 8 jours = 24)
```

### 📋 Créneaux pour S2 (11-23 mai 2026)

**Fichier**: [server/app/seed/seed_data_v2.sql](server/app/seed/seed_data_v2.sql#L160-L208)

```sql
-- Semaine 1: 11-16 mai (Lundi-Samedi)
-- Lundi 11 mai
- 08:00 → 10:00 (Matin)
- 10:30 → 12:30 (Midi)
- 14:00 → 16:00 (Après-midi)

-- Semaine 2: 18-23 mai (Lundi-Samedi, pas dimanche 17)
-- Même schéma horaire

-- Total: ~36 créneaux (3 créneaux x 12 jours = 36)
```

---

## 3️⃣ API Endpoint `/referentiel/catalogue`

### 📌 Route

**Fichier**: [server/app/routers/referentiel.py](server/app/routers/referentiel.py#L17-L20)

```python
@router.get("/catalogue")
def get_catalogue(db: Session = Depends(get_db)) -> dict:
    """Full referentiel for planification form (niveaux, sections, sessions, salles, creneaux)."""
    return load_catalogue(db)
```

### 🔧 Service de Chargement

**Fichier**: [server/app/services/catalogue_service.py](server/app/services/catalogue_service.py#L475-L510)

```python
def load_catalogue(db: Session | None = None) -> dict[str, Any]:
    catalogue = _default_catalogue()
    if db is None:
        return catalogue

    try:
        sessions = _load_sessions(db)
        sections, matieres_by_section = _load_sections_and_matieres(db)
        salles = _load_salles(db)
        creneaux = _load_creneaux(db)

        if sessions:
            catalogue["sessions"] = sessions
        if sections:
            catalogue["sections"] = sections
            catalogue["matieres_by_section"] = matieres_by_section
            catalogue["source"] = "database"
        catalogue["salles"] = salles if salles else list(SAMPLE_SALLES)
        if creneaux:
            catalogue["creneaux"] = creneaux
    except Exception as exc:
        catalogue["message"] = f"Erreur chargement BD: {exc}"

    return catalogue
```

### 📡 Requête SQL pour les Sessions

**Fichier**: [server/app/services/catalogue_service.py](server/app/services/catalogue_service.py#L153-L177)

```python
def _load_sessions(db: Session) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    if _table_exists(db, "session"):
        rows = db.execute(
            text(
                """
                SELECT id, COALESCE(annee_universitaire, '') AS annee,
                       date_debut, date_fin, COALESCE(statut, 'BROUILLON') AS statut
                FROM session ORDER BY date_debut, id
                """
            )
        ).mappings().all()
        for row in rows:
            label = f"Principale {row['annee']}".strip() if row["annee"] else f"Session {row['id']}"
            sessions.append(
                {
                    "label": label,
                    "session_id": int(row["id"]),
                    "date_debut": str(row["date_debut"]),
                    "date_fin": str(row["date_fin"]),
                    "statut": str(row["statut"]).upper(),
                }
            )
    return sessions
```

### 📤 Structure de Réponse

```json
{
  "source": "database",
  "message": "Catalogue chargé depuis la base de données",
  "sessions": [
    {
      "label": "Principale 2025/2026",
      "session_id": 1,
      "date_debut": "2026-01-07",
      "date_fin": "2026-01-15",
      "statut": "VALIDEE"
    },
    {
      "label": "Principale 2025/2026",
      "session_id": 2,
      "date_debut": "2026-05-11",
      "date_fin": "2026-05-23",
      "statut": "BROUILLON"
    }
  ],
  "sections": [...],
  "matieres_by_section": {...},
  "creneaux": [
    {
      "date_examen": "2026-01-07",
      "heure_debut": "08:30:00",
      "heure_fin": "10:30:00"
    },
    ...
  ],
  "salles": [
    {
      "salle_id": "AMPHI-INFO",
      "capacite": 106,
      "batiment": "A"
    },
    ...
  ],
  "semestres": ["S1", "S2"],
  "types_epreuve": [
    {"value": "EXAMEN_FINAL", "label": "Examen Final"},
    {"value": "DS", "label": "DS"}
  ]
}
```

---

## 4️⃣ Filtrage des Créneaux par Session

### 🔍 Logique de Filtrage

**Fichier**: [server/test_real_data.py](server/test_real_data.py#L87-L105)

```python
def display_creneaux(creneaux: list[Creneau], session: Session, limit: int = 10):
    """Affiche les créneaux disponibles pour une session."""
    
    # Filtrer les créneaux dans la période de la session
    creneaux_session = [
        c for c in creneaux 
        if session.date_debut <= c.date <= session.date_fin
    ]
    
    # Grouper par date
    creneaux_par_date = {}
    for creneau in creneaux_session:
        if creneau.date not in creneaux_par_date:
            creneaux_par_date[creneau.date] = []
        creneaux_par_date[creneau.date].append(creneau)
```

**Principe**: Les créneaux sont filtrés en comparant leur date avec `date_debut` et `date_fin` de la session.

---

## 5️⃣ Scripts de Création des Sessions

### 🐍 Script Python pour S2

**Fichier**: [server/add_session_s2.py](server/add_session_s2.py)

```python
def add_session_s2():
    """Ajoute la session S2 et ses créneaux."""
    db: Session = SessionLocal()
    
    # Créer la session S2
    session_s2 = SessionModel(
        type_session="PRINCIPALE",
        annee_universitaire="2025/2026",
        date_debut=date(2026, 5, 11),
        date_fin=date(2026, 5, 23),
        statut="BROUILLON"
    )
    db.add(session_s2)
    db.commit()
    
    # Ajouter les créneaux
    creneaux_s2 = [
        (date(2026, 5, 11), time(8, 0), time(10, 0), "Lun 11/05 Matin"),
        (date(2026, 5, 11), time(10, 30), time(12, 30), "Lun 11/05 Midi"),
        # ... 34 autres créneaux
    ]
    
    for creneau_date, heure_debut, heure_fin, libelle in creneaux_s2:
        creneau = Creneau(
            date=creneau_date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            libelle=libelle
        )
        db.add(creneau)
    
    db.commit()
```

**Utilisation**:
```bash
python server/add_session_s2.py
```

### 💾 SQL Seed

**Fichier**: [server/app/seed/seed_data_v2.sql](server/app/seed/seed_data_v2.sql#L130-L208)

Les sessions et créneaux sont insérés avec un mécanisme `ON CONFLICT ... DO NOTHING` pour éviter les doublons.

---

## 6️⃣ Schémas Pydantic

### 📝 Schema Session

**Fichier**: [server/app/schemas/session_schema.py](server/app/schemas/session_schema.py)

```python
class SessionOut(BaseModel):
    """Schéma de sortie pour une session."""
    id: int
    type_session: str
    annee_universitaire: str
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    statut: str

    class Config:
        from_attributes = True
```

**Fichier alternatif**: [server/app/schemas/salle_session_schema.py](server/app/schemas/salle_session_schema.py#L42-L58)

```python
class SessionBase(BaseModel):
    type_session: str = Field(min_length=1, max_length=50)
    annee_universitaire: str = Field(min_length=1, max_length=10)
    date_debut: date
    date_fin: date
    statut: str = Field(default="BROUILLON", max_length=24)

class SessionOut(SessionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

---

## 7️⃣ CRUD et Services

### 📌 Fichiers CRUD

**Fichier**: [server/app/crud/](server/app/crud/)

Structure:
- `crud_planif.py` - Planifications
- `crud_salle.py` - Salles
- `crud_surv.py` - Surveillances
- `crud_auth.py` - Authentification
- `crud_indisponibilite.py` - Indisponibilités

### 📌 Service de Planification

**Fichier**: [server/app/services/planif_service.py](server/app/services/planif_service.py#L113-L140)

```python
def _resolve_session_context(self, request: GenerationRequest) -> GenerationRequest:
    """Charge les informations de session depuis la base."""
    row = self.db.execute(
        text(
            """
            SELECT id, annee_universitaire, date_debut, date_fin, statut
            FROM session
            WHERE id = :session_id
            """
        ),
        {"session_id": request.session_id},
    ).mappings().first()

    if row is None:
        raise ConstraintViolationError(f"[C16] session {request.session_id} introuvable")

    return request.model_copy(
        update={
            "annee_universitaire": row.get("annee_universitaire"),
            # ... autres mises à jour
        }
    )
```

---

## 8️⃣ Flux Complet

```
┌────────────────────────────────────────────────────────┐
│         Frontend demande /referentiel/catalogue        │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│  referentiel.py::get_catalogue(db)                     │
│  - Appelle load_catalogue(db)                          │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│  catalogue_service.py::load_catalogue(db)              │
│                                                        │
│  1️⃣ _load_sessions(db)                                │
│     SELECT id, annee_universitaire, date_debut, ...   │
│     FROM session ORDER BY date_debut, id              │
│                                                        │
│  2️⃣ _load_sections_and_matieres(db)                   │
│                                                        │
│  3️⃣ _load_salles(db)                                  │
│                                                        │
│  4️⃣ _load_creneaux(db)                                │
│     SELECT date AS date_examen, heure_debut, ...      │
│     FROM creneau ORDER BY date, heure_debut           │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│  Retour dict contenant :                              │
│  - sessions (avec dates)                              │
│  - creneaux (filtrés par db)                          │
│  - sections, matieres_by_section                      │
│  - salles, semestres, types_epreuve                   │
└────────────────────────────────────────────────────────┘
```

---

## 9️⃣ Points Clés

### ✅ Sessions définies en dur dans la seed SQL
- S1: 7-15 janvier 2026 (VALIDEE)
- S2: 11-23 mai 2026 (BROUILLON)

### ✅ Dates flexibles
- Peuvent être modifiées/créées dynamiquement via Python (voir `add_session_s2.py`)
- Modifiable par admin si besoin

### ✅ Créneaux liés à la session
- Filtrage automatique dans le catalogue
- Condition: `session.date_debut <= creneau.date <= session.date_fin`

### ✅ API centralisée
- Un seul endpoint `/referentiel/catalogue` fournit tout
- Frontend reçoit sessions + créneaux + sections en une requête

### ✅ Schémas bien structurés
- Modèles ORM + Schemas Pydantic + CRUD
- Migration Alembic pour évolutivité

---

## 🔟 Fichiers de Référence

| Fichier | Fonction |
|---------|----------|
| [server/app/models/salle_session.py](server/app/models/salle_session.py) | Modèles ORM (Session, Creneau, Salle) |
| [server/app/schemas/session_schema.py](server/app/schemas/session_schema.py) | Schemas Pydantic pour Session |
| [server/app/routers/referentiel.py](server/app/routers/referentiel.py) | Endpoints `/referentiel/*` |
| [server/app/services/catalogue_service.py](server/app/services/catalogue_service.py) | Chargement du catalogue |
| [server/add_session_s2.py](server/add_session_s2.py) | Script création S2 |
| [server/app/seed/seed_data_v2.sql](server/app/seed/seed_data_v2.sql) | SQL seed avec S1 + S2 |
| [server/app/crud/crud_planif.py](server/app/crud/crud_planif.py) | CRUD planifications |
| [server/app/services/planif_service.py](server/app/services/planif_service.py) | Service planifications |

---

## 📚 Pour Aller Plus Loin

- **Modifier les dates S1/S2**: Éditer `seed_data_v2.sql` et relancer le seed
- **Ajouter une nouvelle session**: Utiliser script `add_session_s2.py` comme template
- **Filtrer les créneaux**: Modifier la logique dans `catalogue_service.py`
- **Créer créneaux dynamiques**: Voir `add_session_s2.py` pour exemple d'insertion en boucle

