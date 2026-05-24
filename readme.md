# 🎓 Système de Gestion des Examens et Surveillance

Système complet de planification d'examens et d'affectation automatique des surveillants pour établissements d'enseignement supérieur.

## 🌟 Fonctionnalités

### ✅ Planification des Examens
- Création et gestion des sessions d'examens
- Planification automatique avec contraintes
- Gestion des salles et créneaux horaires
- Validation et modification des planifications

### ✅ Affectation des Surveillants
- **Algorithme d'affectation automatique** avec 6 contraintes:
  - C1: Volume horaire suffisant
  - C2: Disponibilité déclarée
  - C3: Pas de conflit de matière
  - C4: Non-simultanéité
  - C5: Appartenance au département
  - C6: Équité de charge
- Résolution manuelle des conflits
- Visualisation en calendrier
- Gestion des charges horaires

### ✅ Authentification & Sécurité
- Authentification JWT
- Gestion des comptes enseignants
- Routes protégées
- Sessions sécurisées

### ✅ Gestion des Indisponibilités
- Déclaration des indisponibilités
- Validation par l'administration
- Prise en compte dans l'affectation
- Historique des indisponibilités

### ✅ Rapports & Statistiques
- Convocations PDF
- Statistiques de charge
- Rapports de session
- Export des données

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
```
server/
├── app/
│   ├── algorithms/      # Algorithme d'affectation
│   ├── crud/           # Opérations base de données
│   ├── models/         # Modèles SQLAlchemy
│   ├── routers/        # Routes API
│   ├── schemas/        # Schémas Pydantic
│   ├── services/       # Logique métier
│   └── utils/          # Utilitaires (JWT, etc.)
├── requirements.txt    # Dépendances Python
└── .env               # Configuration
```

### Frontend (Next.js + TypeScript)
```
frontend/
├── src/
│   ├── app/           # Pages Next.js
│   ├── components/    # Composants React
│   ├── hooks/         # Hooks personnalisés
│   ├── lib/           # API client & utils
│   └── types/         # Types TypeScript
├── package.json       # Dépendances Node
└── next.config.ts     # Configuration Next.js
```

## 🚀 Installation

### Prérequis
- Python 3.13+
- Node.js 18+
- PostgreSQL 14+

### 1. Cloner le Projet
```bash
git clone <repository-url>
cd projet
```

### 2. Configuration Backend
```bash
cd server

# Créer environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 3. Configuration Frontend
```bash
cd frontend

# Installer dépendances
npm install

# Configurer .env.local
cp .env.example .env.local
# Éditer .env.local avec vos paramètres
```

### 4. Base de Données
```bash
cd server

# Créer la base
psql -U postgres -c "CREATE DATABASE exam_surveillance;"

# Exécuter le script SQL
psql -U postgres -d exam_surveillance -f script.sql

# Corriger les données (important!)
psql -U postgres -d exam_surveillance -f fix_data.sql
```

## 🎯 Démarrage Rapide

### Option 1: Script Automatique (Windows)
```bash
# Double-cliquer sur:
START_ALL.bat
```

### Option 2: Manuel

**Terminal 1 - Backend:**
```bash
cd server
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Navigateur:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `GUIDE_DEMARRAGE_RAPIDE.md` | Guide de démarrage complet |
| `MERGE_RESOLUTION_COMPLETE.md` | Résolution du merge hajer2 |
| `RESUME_CORRECTIONS.md` | Corrections appliquées |
| `FIX_SALLE_ID_BUG.md` | Documentation bug Salle.id |
| `TEST_AFFECTATION_FIX.md` | Guide de test |

## 🔧 Scripts Utiles

| Script | Description |
|--------|-------------|
| `START_ALL.bat` | Démarre backend + frontend |
| `PUSH_TO_REMOTE.bat` | Push vers origin/Farah |
| `server/fix_data.sql` | Corrige les données |
| `server/diagnose_conflicts.py` | Diagnostic conflits |

## 🧪 Tests

### Backend
```bash
cd server
pytest
```

### Frontend
```bash
cd frontend
npm run test
npm run build  # Vérifier build
```

## 📡 API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/me` - Profil utilisateur

### Surveillance
- `POST /api/surveillances/affecter-session` - Affectation auto
- `POST /api/surveillances/manual-assignment` - Affectation manuelle
- `GET /api/surveillances/getallsurveillants` - Liste enseignants
- `GET /api/surveillances/{session_id}` - Surveillances session

### Indisponibilités
- `GET /api/disponibilites` - Liste
- `POST /api/disponibilites` - Créer
- `PUT /api/disponibilites/{id}` - Modifier
- `DELETE /api/disponibilites/{id}` - Supprimer

### Planification
- `GET /api/planifications` - Liste
- `POST /api/planifications` - Créer
- `PUT /api/planifications/{id}` - Modifier
- `DELETE /api/planifications/{id}` - Supprimer

Documentation complète: http://localhost:8000/docs

## 🐛 Problèmes Connus & Solutions

### Backend ne démarre pas
**Erreur:** `ModuleNotFoundError: No module named 'jose'`

**Solution:**
```bash
cd server
.venv\Scripts\pip install python-jose[cryptography] passlib[bcrypt]
```

### Tous les surveillants en conflit
**Cause:** `section_departement_id` est NULL

**Solution:**
```bash
cd server
psql -U postgres -d exam_surveillance -f fix_data.sql
```

### Erreur "AMPHI-INFO"
**Status:** ✅ Corrigé dans commit `10d22d4`

## 🔄 Workflow Git

### Branches
- `main` - Production
- `Farah` - Développement principal
- `hajer2` - Fonctionnalités Auth + Indispo (mergée)

### Commits Récents
```
10d22d4 - fix: Correction bugs critiques surveillance affectation
ebd4a2b - Merge branch origin/hajer2 and resolve conflicts
a47680d - examen-surv
```

### Pusher les Modifications
```bash
# Vérifier l'état
git status

# Pusher
git push origin Farah

# Ou utiliser le script
PUSH_TO_REMOTE.bat
```

## 👥 Contributeurs

- Farah - Développement principal, surveillance
- Hajer - Authentification, indisponibilités
- Nour - Planification
- Ahlem - Frontend

## 📄 Licence

[Votre licence ici]

## 🆘 Support

En cas de problème:
1. Consulter `GUIDE_DEMARRAGE_RAPIDE.md`
2. Vérifier les logs backend/frontend
3. Exécuter `diagnose_conflicts.py`
4. Consulter la documentation API

---

**Version:** 2.0.0
**Date:** 2026-05-24
**Status:** ✅ Production Ready
