# 🚀 Système de Gestion des Examens - Backend FastAPI

## 📚 Documentation Complète

**Toute la documentation est organisée dans le dossier [`docs/`](docs/)**

### 🎯 Accès Rapide

| Besoin | Document |
|--------|----------|
| 🚀 **Démarrer rapidement** | [`docs/guides/QUICK_START.md`](docs/guides/QUICK_START.md) |
| 📡 **API Documentation** | [`docs/api/API_PLANIFICATION.md`](docs/api/API_PLANIFICATION.md) |
| 🧪 **Exemples Swagger** | [`docs/api/SWAGGER_EXAMPLES.md`](docs/api/SWAGGER_EXAMPLES.md) |
| 🎨 **Guide Frontend P3** | [`docs/api/GUIDE_P3_FRONTEND.md`](docs/api/GUIDE_P3_FRONTEND.md) |
| 🏗️ **Architecture** | [`docs/architecture/ALGORITHME_PLANIFICATION.md`](docs/architecture/ALGORITHME_PLANIFICATION.md) |
| 🎤 **Démo Soutenance** | [`docs/demo/SOUTENANCE_GUIDE.md`](docs/demo/SOUTENANCE_GUIDE.md) |
| 🗂️ **Organisation Soutenance** | [`docs/soutenance/ORGANISATION_SOUTENANCE.md`](docs/soutenance/ORGANISATION_SOUTENANCE.md) |

### 📁 Structure Documentation

```
docs/
├── guides/          # Guides d'utilisation
├── api/             # Documentation API
├── architecture/    # Architecture et algorithmes
├── demo/            # Guide de démonstration
└── soutenance/      # Préparation soutenance
```

---

## 📋 Vue d'Ensemble

Système complet de gestion des examens universitaires avec **génération automatique d'emplois du temps** respectant 18 contraintes métier.

### Stack Technique
- **Backend** : FastAPI (Python 3.10+)
- **ORM** : SQLAlchemy 2.0
- **Database** : PostgreSQL 14+
- **Validation** : Pydantic v2
- **Migrations** : Alembic
- **Tests** : pytest

### Modules Principaux
- **P1 - Planification** : Génération automatique d'emplois du temps d'examens
- **P2 - Surveillance** : Affectation des surveillants aux examens
- **Référentiel** : Gestion des données de base (salles, matières, enseignants)

---

## ⚡ Démarrage Rapide

### 1. Prérequis

```bash
# Vérifier Python
python --version  # Doit être >= 3.10

# Vérifier PostgreSQL
psql --version    # Doit être >= 14
```

### 2. Installation

```bash
# Naviguer vers le dossier serveur
cd PFA/server

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration Base de Données

```bash
# Créer la base de données
createdb pfa_examens

# Créer le fichier .env
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/pfa_examens
FRONTEND_ORIGIN=http://localhost:3000
APP_NAME=PFA Exam Planning API
APP_VERSION=1.0.0
EOF

# Appliquer les migrations
alembic upgrade head

# (Optionnel) Charger les données de test
psql -d pfa_examens -f app/seed/script.sql
```

### 4. Démarrer le Serveur

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**URLs** :
- API : http://127.0.0.1:8000
- Documentation interactive : http://127.0.0.1:8000/docs
- Health check : http://127.0.0.1:8000/health

---

## 🏗️ Architecture

### Structure des Dossiers

```
PFA/server/
├── app/
│   ├── algorithms/          # Algorithmes de planification
│   │   ├── contraintes.py   # 18 contraintes métier
│   │   ├── planif_auto.py   # Génération automatique
│   │   └── surv_auto.py     # Affectation surveillants
│   ├── crud/                # Accès données (CRUD)
│   │   ├── crud_planif.py
│   │   └── crud_surv.py
│   ├── models/              # Modèles SQLAlchemy
│   │   ├── planification.py
│   │   └── surveillance.py
│   ├── routers/             # Endpoints FastAPI
│   │   ├── planifications.py
│   │   ├── surveillances.py
│   │   └── referentiel.py
│   ├── schemas/             # Schémas Pydantic
│   │   ├── planification.py
│   │   └── surveillance.py
│   ├── services/            # Business logic
│   │   ├── planif_service.py
│   │   └── surv_service.py
│   ├── config.py            # Configuration
│   ├── database.py          # Connexion DB
│   └── main.py              # Point d'entrée
├── alembic/                 # Migrations DB
├── tests/                   # Tests unitaires
├── requirements.txt         # Dépendances Python
└── .env                     # Variables d'environnement
```

### Flux de Données

```
Router → Service → Algorithm → CRUD → Database
  ↓         ↓          ↓
HTTP    Business   Pure Logic
Layer    Logic     (testable)
```

---

## 🎯 Fonctionnalités Principales

### 1. Génération Automatique d'Emplois du Temps

**Endpoint** : `POST /api/sessions/{id}/generer`

**Algorithme** : Glouton avec scoring des contraintes souples

**Contraintes Respectées** :
- ✅ 11 contraintes dures (respect obligatoire)
- ✅ 7 contraintes souples (optimisation)

**Exemple** :
```bash
curl -X POST http://127.0.0.1:8000/api/sessions/1/generer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "session_date_debut": "2026-01-07",
    "session_date_fin": "2026-01-15",
    "tasks": [...],
    "creneaux": [...],
    "salles": [...]
  }'
```

**Résultat** :
```json
{
  "nb_crees": 10,
  "nb_conflits": 0,
  "conflits": []
}
```

### 2. Gestion des Planifications

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/planifications` | GET | Liste des planifications |
| `/api/planifications/{id}` | GET | Détail d'une planification |
| `/api/planifications` | POST | Création manuelle |
| `/api/planifications/{id}` | PUT | Mise à jour |
| `/api/planifications/{id}` | DELETE | Suppression |
| `/api/sessions/{id}/emploi-du-temps` | GET | Emploi du temps complet |

### 3. Affectation des Salles

**Endpoint** : `POST /api/planifications/{id}/salles`

**Fonctionnalités** :
- Affectation manuelle des salles
- Découpage automatique en groupes
- Validation des contraintes (capacité, disponibilité)

---

## 🧪 Tests

### Exécuter les Tests

```bash
# Tous les tests
pytest

# Tests de planification uniquement
pytest tests/test_planif.py -v

# Avec couverture de code
pytest --cov=app tests/
```

### Tests Disponibles

1. **test_decoupage_groupes_equilibre** : Vérification de l'équilibrage des groupes (C9)
2. **test_contrainte_salle_occupee_detectee** : Détection des conflits de salles (C1)
3. **test_generation_simple_et_split_best_effort** : Génération avec découpage automatique
4. **test_emploi_du_temps_trie** : Tri chronologique de l'emploi du temps

### Scripts de Test

```bash
# Test de génération avec données réelles
python test_generation_example.py

# Vérification des 18 contraintes
python verify_constraints.py
```

---

## 📚 Documentation

### Documents Disponibles

| Document | Description |
|----------|-------------|
| `docs/api/API_PLANIFICATION.md` | Contrat API planification (à jour) |
| `docs/api/SWAGGER_EXAMPLES.md` | Exemples de tests Swagger |
| `docs/guides/QUICK_START.md` | Guide de démarrage rapide |
| `docs/architecture/ALGORITHME_PLANIFICATION.md` | Documentation exhaustive de l'algorithme |
| `docs/architecture/IMPLEMENTATION_STATUS.md` | État d'implémentation détaillé |
| `docs/demo/SOUTENANCE_GUIDE.md` | Guide de démonstration |
| `docs/soutenance/ORGANISATION_SOUTENANCE.md` | Organisation de soutenance |

### API Documentation

- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

---

## 🔧 Configuration

### Variables d'Environnement

```bash
# Obligatoires
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
FRONTEND_ORIGIN=http://localhost:3000

# Optionnelles
APP_NAME=PFA Exam Planning API
APP_VERSION=1.0.0
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=False
DATABASE_TIMEOUT=30
```

### Migrations Alembic

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Revenir à la migration précédente
alembic downgrade -1

# Voir l'historique
alembic history
```

---

## 🚀 Déploiement

### Production avec Gunicorn

```bash
# Installer Gunicorn
pip install gunicorn

# Démarrer avec 4 workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optionnel)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔄 Workflow de Développement

### Ajouter une Dépendance

```bash
# Installer le package
pip install package_name

# Mettre à jour requirements.txt
pip freeze > requirements.txt

# Commit
git add requirements.txt
git commit -m "Add package_name dependency"
```

### Avant de Merger une PR

```bash
# Pull les dernières modifications
git pull origin main

# Activer l'environnement
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Exécuter les tests
pytest

# Vérifier les migrations
alembic upgrade head
```

---

## 📊 Métriques de Performance

### Benchmarks

| Jeu de Données | Matières | Créneaux | Salles | Temps | Taux Succès |
|----------------|----------|----------|--------|-------|-------------|
| Petit | 10 | 23 | 28 | < 100ms | 100% |
| Moyen | 50 | 60 | 50 | < 500ms | 94% |
| Grand | 100 | 120 | 80 | < 2s | 88% |

### Complexité Algorithmique

- **Temps** : O(M × C × S) où M = matières, C = créneaux, S = salles
- **Espace** : O(M + C + S) pour le cache mémoire

---

## 🆘 Dépannage

### Problème : "Connection refused" (PostgreSQL)

```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql  # Linux
brew services list  # Mac

# Démarrer PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # Mac
```

### Problème : "ModuleNotFoundError"

```bash
# Vérifier l'environnement virtuel
which python  # Doit pointer vers .venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : Tests échouent

```bash
# Vérifier les dépendances de test
pip install pytest httpx

# Exécuter en mode verbose
pytest -v -s
```

---

## 🤝 Contribution

### Standards de Code

- **Style** : PEP 8 (vérifier avec `flake8`)
- **Type Hints** : Obligatoires pour les fonctions publiques
- **Docstrings** : Format Google
- **Tests** : Couverture minimale 80%

### Commit Messages

```
feat: Add automatic room assignment
fix: Resolve constraint C1 violation
docs: Update API documentation
test: Add test for group splitting
refactor: Simplify scoring algorithm
```

---

## 📞 Support

- **Documentation** : Consulter `ALGORITHME_PLANIFICATION.md`
- **Issues** : Ouvrir un ticket sur le dépôt Git
- **Email** : contact@pfa-examens.tn

---

## 📄 Licence

Ce projet est développé dans le cadre du PFA (Projet de Fin d'Année) - Faculté des Sciences de Tunis.

---

**🚀 Bon développement !**



