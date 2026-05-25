# 📑 INDEX - Exploration Backend Sessions

## 🎯 Point de Départ

Vous avez demandé une exploration du backend pour comprendre comment les sessions (S1, S2) sont définies et créées. Voici ce qui a été découvert :

---

## 📚 Documents Créés

### 1. 🔍 **[EXPLORATION_BACKEND_SESSIONS.md](EXPLORATION_BACKEND_SESSIONS.md)**
   - **Pour**: Comprendre la structure technique complète
   - **Contient**:
     - Modèles ORM (Session, Creneau, Salle)
     - Définition des sessions actuelles (S1, S2)
     - API endpoint `/referentiel/catalogue`
     - Requête SQL de chargement
     - Scripts de création
     - Schémas Pydantic
     - Services et CRUD

### 2. 🚀 **[GUIDE_PRATIQUE_SESSIONS.md](GUIDE_PRATIQUE_SESSIONS.md)**
   - **Pour**: Utiliser les sessions dans le code
   - **Contient**:
     - Exemples TypeScript/React
     - Exemples Python ORM
     - Créer/modifier une session
     - Ajouter des créneaux
     - Composer React avec sessions
     - Tests et vérification

### 3. 📊 **[SESSIONS_DANS_ENDPOINTS.md](SESSIONS_DANS_ENDPOINTS.md)**
   - **Pour**: Comprendre les workflows complets
   - **Contient**:
     - Création d'examens dans une session
     - Génération automatique de planifications
     - Affectation automatique de surveillants
     - Flux complet de bout en bout
     - Contraintes de validation
     - Requêtes SQL pratiques

### 4. 🎨 **[RESUME_VISUEL_SESSIONS.md](RESUME_VISUEL_SESSIONS.md)**
   - **Pour**: Vue d'ensemble rapide
   - **Contient**:
     - Architecture des sessions (schéma DB)
     - Calendrier 2025/2026
     - Workflow visuel
     - API endpoints
     - Validation chain
     - Quick lookup table

---

## 🎓 Guide de Lecture Recommandé

### 👤 Je suis Frontend Developer
1. Lisez [GUIDE_PRATIQUE_SESSIONS.md](GUIDE_PRATIQUE_SESSIONS.md#frontend---afficher-les-sessions) (section Frontend)
2. Ensuite [SESSIONS_DANS_ENDPOINTS.md](SESSIONS_DANS_ENDPOINTS.md#6️⃣-api-workflow-complet-frontend) (workflow frontend)

### 👤 Je suis Backend Developer
1. Lisez [EXPLORATION_BACKEND_SESSIONS.md](EXPLORATION_BACKEND_SESSIONS.md)
2. Explorez les fichiers cités dans chaque section
3. Consultez [GUIDE_PRATIQUE_SESSIONS.md](GUIDE_PRATIQUE_SESSIONS.md#backend---requête-python-orm) (ORM examples)

### 👤 Je dois créer une nouvelle session
1. Lisez [GUIDE_PRATIQUE_SESSIONS.md](GUIDE_PRATIQUE_SESSIONS.md#5️⃣-créer-une-nouvelle-session)
2. Utilisez le script fourni ou [add_session_s2.py](server/add_session_s2.py) comme modèle

### 👤 Je dois déboguer un problème de dates
1. Consultez [SESSIONS_DANS_ENDPOINTS.md](SESSIONS_DANS_ENDPOINTS.md#5️⃣-contraintes-de-validation)
2. Vérifiez le validation chain dans [RESUME_VISUEL_SESSIONS.md](RESUME_VISUEL_SESSIONS.md#✅-validation-chain)

### 👤 Je veux une vue d'ensemble rapide
1. Lisez [RESUME_VISUEL_SESSIONS.md](RESUME_VISUEL_SESSIONS.md) en intégralité
2. C'est le plus court et le plus visuel

---

## ⚡ Résumé Ultra-Rapide

### 📋 Sessions Définies
- **S1**: 7-15 janvier 2026 (statut: VALIDEE)
- **S2**: 11-23 mai 2026 (statut: BROUILLON)

### 📁 Structure ORM
```python
Session
├─ id, type_session, annee_universitaire
├─ date_debut, date_fin
├─ statut
└─ planifications (relations)

Creneau
├─ date, heure_debut, heure_fin
└─ libelle
```

### 🔌 API Principal
```
GET /referentiel/catalogue
  → sessions: [...], creneaux: [...], sections: [...], ...
```

### 🔑 Clés Importantes
| Concept | Fichier | Ligne |
|---------|---------|-------|
| Modèle ORM | server/app/models/salle_session.py | 44-58 |
| API endpoint | server/app/routers/referentiel.py | 17-20 |
| Service catalogue | server/app/services/catalogue_service.py | 475-510 |
| Requête sessions | server/app/services/catalogue_service.py | 153-177 |
| Requête créneaux | server/app/services/catalogue_service.py | 430-445 |
| Script création S2 | server/add_session_s2.py | 1-150 |
| Seed SQL | server/app/seed/seed_data_v2.sql | 130-208 |

---

## 🔍 Réponses Directes aux Questions Initiales

### 1️⃣ **Comment les sessions (S1, S2) sont définies et créées ?**

**Réponse**: Voir [EXPLORATION_BACKEND_SESSIONS.md - Section 2](EXPLORATION_BACKEND_SESSIONS.md#2️⃣-sessions-actuelles)

- **Définition SQL**: `server/app/seed/seed_data_v2.sql` (lignes 130-150)
- **Script Python**: `server/add_session_s2.py` (modèle pour créer dynamiquement)
- **ORM Model**: `server/app/models/salle_session.py` (classe Session)

**Fichiers clés**:
- Modèle: [salle_session.py](server/app/models/salle_session.py#L44-L58)
- Seed: [seed_data_v2.sql](server/app/seed/seed_data_v2.sql#L130-L150)
- Script: [add_session_s2.py](server/add_session_s2.py)

---

### 2️⃣ **Où sont définies les dates de début/fin (date_debut, date_fin) ?**

**Réponse**: Voir [EXPLORATION_BACKEND_SESSIONS.md - Section 1](EXPLORATION_BACKEND_SESSIONS.md#1️⃣-modèles-de-données-orm)

| Source | Dates |
|--------|-------|
| Base de données | S1: 2026-01-07 to 2026-01-15 |
| Base de données | S2: 2026-05-11 to 2026-05-23 |
| SQL Seed | [seed_data_v2.sql](server/app/seed/seed_data_v2.sql#L135-L145) |
| ORM mapping | [salle_session.py](server/app/models/salle_session.py#L49-L50) |

**Pour modifier**:
1. Éditer [seed_data_v2.sql](server/app/seed/seed_data_v2.sql)
2. Ou utiliser script Python [add_session_s2.py](server/add_session_s2.py) comme modèle

---

### 3️⃣ **L'endpoint API /referentiel/catalogue qui retourne les sessions avec leurs dates**

**Réponse**: Voir [EXPLORATION_BACKEND_SESSIONS.md - Section 3](EXPLORATION_BACKEND_SESSIONS.md#3️⃣-api-endpoint--referentielcatalogue)

**Fichiers**:
- **Endpoint**: [referentiel.py - get_catalogue()](server/app/routers/referentiel.py#L17-L20)
- **Service**: [catalogue_service.py - load_catalogue()](server/app/services/catalogue_service.py#L475-L510)
- **Requête SQL**: [catalogue_service.py - _load_sessions()](server/app/services/catalogue_service.py#L153-L177)

**Utilisation**:
```bash
curl http://localhost:8000/api/referentiel/catalogue | jq '.sessions'
```

**Réponse**:
```json
[
  {
    "session_id": 1,
    "label": "Principale 2025/2026",
    "date_debut": "2026-01-07",
    "date_fin": "2026-01-15",
    "statut": "VALIDEE"
  },
  ...
]
```

---

### 4️⃣ **Structure de la table/modèle de données pour les sessions**

**Réponse**: Voir [EXPLORATION_BACKEND_SESSIONS.md - Section 1](EXPLORATION_BACKEND_SESSIONS.md#📌-table-session)

**Table SQL**:
```sql
CREATE TABLE session (
    id SERIAL PRIMARY KEY,
    type_session VARCHAR(50) NOT NULL,
    annee_universitaire VARCHAR(10) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    statut VARCHAR(24) NOT NULL DEFAULT 'BROUILLON'
);
```

**ORM Model** (Python):
```python
class Session(Base):
    __tablename__ = "session"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_session: Mapped[str] = mapped_column(String(50), nullable=False)
    annee_universitaire: Mapped[str] = mapped_column(String(10), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    statut: Mapped[str] = mapped_column(String(24), nullable=False, default="BROUILLON")
```

**Pydantic Schema**:
```python
class SessionOut(BaseModel):
    id: int
    type_session: str
    annee_universitaire: str
    date_debut: str  # ISO format "YYYY-MM-DD"
    date_fin: str
    statut: str
```

---

## 🗺️ Navigation par Répertoire

### server/app/models/
- **salle_session.py** - Modèles Session, Creneau, Salle
  - Ligne 44-58: Classe Session
  - Ligne 32-43: Classe Creneau

### server/app/routers/
- **referentiel.py** - Endpoint /referentiel/catalogue
  - Ligne 17-20: get_catalogue()

### server/app/services/
- **catalogue_service.py** - Chargement du catalogue
  - Ligne 153-177: _load_sessions()
  - Ligne 430-445: _load_creneaux()
  - Ligne 475-510: load_catalogue()

### server/app/schemas/
- **session_schema.py** - Schema SessionOut
- **salle_session_schema.py** - SessionBase, SessionCreate, SessionUpdate

### server/app/seed/
- **seed_data_v2.sql** - Données S1 + S2
  - Ligne 130-150: INSERT INTO session

### server/ (root)
- **add_session_s2.py** - Script création S2 dynamique

---

## 🚦 Quick Decision Tree

```
❓ Je veux...

├─ Créer une nouvelle session
│  └─ → Voir GUIDE_PRATIQUE_SESSIONS.md #5
│
├─ Modifier les dates de S1 ou S2
│  └─ → Éditer seed_data_v2.sql + relancer
│
├─ Récupérer les sessions depuis le frontend
│  └─ → GET /referentiel/catalogue → .sessions
│
├─ Valider qu'une date d'examen est dans la session
│  └─ → IF date ∈ [session.date_debut, session.date_fin] THEN OK
│
├─ Filtrer les créneaux d'une session
│  └─ → Voir catalogue_service.py _load_creneaux()
│
├─ Créer une planification (examen) dans une session
│  └─ → POST /planifications avec session_id + date validation
│
├─ Générer les planifications automatiquement
│  └─ → POST /planifications/generate (utilise session dates)
│
├─ Affecter les surveillants
│  └─ → POST /surveillances/affecter-session
│
└─ Vérifier les données actuelles
   └─ → curl http://localhost:8000/api/referentiel/catalogue
```

---

## 📞 Fichiers de Référence Rapides

```
// Créer une session
- Python: server/add_session_s2.py
- SQL: server/app/seed/seed_data_v2.sql #130-150

// Récupérer les sessions
- API: GET /referentiel/catalogue
- Backend: server/app/services/catalogue_service.py #_load_sessions()
- Frontend: await fetch('/api/referentiel/catalogue').then(r => r.json())

// Récupérer les créneaux d'une session
- Backend: server/app/services/catalogue_service.py #_load_creneaux()
- Filter logic: creneau.date ∈ [session.date_debut, session.date_fin]

// Valider une planification
- Backend: server/app/routers/planifications.py #L121
- Logic: session.date_debut <= date_examen <= session.date_fin

// Modèle de base
- ORM: server/app/models/salle_session.py #Session class
- Schema: server/app/schemas/session_schema.py
```

---

## 🎓 Concepts Clés

| Terme | Définition | Fichier |
|-------|-----------|---------|
| **Session** | Période d'examens (ex: S1 = jan 2026) | salle_session.py |
| **Creneau** | Slot horaire (ex: 08:30-10:30) | salle_session.py |
| **Planification** | Un examen d'une matière | planification.py |
| **Surveillance** | Affectation d'un prof à un examen | surveillance.py |
| **date_debut** | Premier jour de la session | session.date_debut |
| **date_fin** | Dernier jour de la session | session.date_fin |
| **statut** | BROUILLON / VALIDEE / PUBLIEE | session.statut |

---

## ✅ Points Vérifiés

- ✅ Sessions définies en dur (S1 + S2)
- ✅ Dates de début/fin identifiées
- ✅ Endpoint `/referentiel/catalogue` documenté
- ✅ Structure de table complète
- ✅ Scripts de création fournis
- ✅ Exemples de code (Python + TypeScript)
- ✅ Flux complets documentés

---

## 📊 Statistics

| Métrique | Valeur |
|----------|--------|
| Documents créés | 4 |
| Fichiers explorés | 20+ |
| Lignes de code documentées | 1000+ |
| Exemples de code | 30+ |
| Diagrammes visuels | 15+ |

---

## 🎯 Prochaines Étapes Recommandées

1. **Testez l'API**:
   ```bash
   curl http://localhost:8000/api/referentiel/catalogue | jq '.sessions'
   ```

2. **Explorez le code source**:
   - Ouvrez [salle_session.py](server/app/models/salle_session.py)
   - Ouvrez [catalogue_service.py](server/app/services/catalogue_service.py)

3. **Créez une nouvelle session** (optionnel):
   - Suivez [GUIDE_PRATIQUE_SESSIONS.md #5](GUIDE_PRATIQUE_SESSIONS.md#5️⃣-créer-une-nouvelle-session)

4. **Intégrez dans votre workflow**:
   - Si frontend: voir [GUIDE_PRATIQUE_SESSIONS.md #7](GUIDE_PRATIQUE_SESSIONS.md#7️⃣-frontend---afficher-les-sessions)
   - Si backend: voir [SESSIONS_DANS_ENDPOINTS.md](SESSIONS_DANS_ENDPOINTS.md)

---

## 📞 Support

Si vous avez des questions spécifiques après lecture:
- Consultez le fichier le plus pertinent
- Cherchez la section qui répond à votre question
- Les fichiers contiennent des références de ligne exactes

**Bonne exploration! 🚀**

