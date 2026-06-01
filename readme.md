# 📚 Système de Gestion des Examens - FST

> Plateforme complète de planification et surveillance des examens pour la Faculté des Sciences de Tunis

[![Next.js](https://img.shields.io/badge/Next.js-16.2-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)

## 🖥️ Application Overview

**Admin Side :**
<br></br>
<img width="1842" height="899" alt="image" src="https://github.com/user-attachments/assets/3d4da2c1-c3fe-4f05-89cf-90f37fc561c1" />
<br>
<img width="1854" height="886" alt="image" src="https://github.com/user-attachments/assets/16290532-fa3d-41be-9471-389ea9c1edac" />
<img width="1839" height="879" alt="image" src="https://github.com/user-attachments/assets/6f57063a-226b-4ed2-8295-e84dccb0c3bb" />
<br>
<img width="1852" height="889" alt="image" src="https://github.com/user-attachments/assets/c71fccab-259e-427d-86a7-7f860b96cbac" />

<br></br>
**Teacher side :**
<br></br>
<img width="1842" height="889" alt="image" src="https://github.com/user-attachments/assets/194d37cd-5e20-4fd3-8680-ab9814df9dce" />
<br>
<img width="1860" height="887" alt="image" src="https://github.com/user-attachments/assets/5f90be00-1b49-4176-b8be-a52eec1a416c" />



## 🎯 Vue d'ensemble

Système web moderne pour automatiser la gestion des examens universitaires, incluant :

- 📅 **Planification intelligente** des examens avec génération automatique
- 👥 **Gestion de surveillance** et affectation des enseignants
- 🏫 **Gestion des salles** et capacités
- 📄 **Génération de documents** (convocations, emplois du temps)
- 🔐 **Authentification sécurisée** avec gestion des rôles (Admin/Enseignant)

## ✨ Fonctionnalités principales

### Pour les Administrateurs
- ✅ Créer et gérer les planifications d'examens
- ✅ Générer automatiquement les emplois du temps
- ✅ Affecter les surveillants aux examens
- ✅ Gérer les salles et leurs capacités
- ✅ Visualiser la charge de surveillance par enseignant
- ✅ Exporter les planifications en PDF

### Pour les Enseignants
- ✅ Consulter leurs convocations de surveillance
- ✅ Déclarer leurs indisponibilités
- ✅ Visualiser leur emploi du temps de surveillance

## 🏗️ Architecture

```
projet/
├── frontend/          # Application Next.js (React 19 + TypeScript)
│   ├── src/
│   │   ├── app/           # Pages et routes (App Router)
│   │   │   ├── (admin)/   # Routes administrateur
│   │   │   ├── (enseigant)/ # Routes enseignant
│   │   │   └── login/     # Authentification
│   │   └── components/    # Composants réutilisables
│   └── public/        # Assets statiques
│
├── server/            # API FastAPI (Python)
│   ├── app/
│   │   ├── routers/       # Endpoints API
│   │   ├── services/      # Logique métier
│   │   ├── models/        # Modèles SQLAlchemy
│   │   ├── schemas/       # Schémas Pydantic
│   │   ├── crud/          # Opérations base de données
│   │   ├── algorithms/    # Algorithmes de génération
│   │   └── middleware/    # Middleware (auth, CORS)
│   ├── alembic/       # Migrations de base de données
│   └── tests/         # Tests unitaires et d'intégration
│
├── START_ALL.bat      # Démarrer frontend + backend
├── START_FRONTEND.bat # Démarrer uniquement le frontend
└── START_BACKEND.bat  # Démarrer uniquement le backend
```

## 🚀 Installation

### Prérequis

- **Node.js** 20+ et npm
- **Python** 3.13+
- **PostgreSQL** 14+ (ou SQLite pour développement)
- **Git**

### 1. Cloner le projet

```bash
git clone <repository-url>
cd projet
```

### 2. Configuration du Backend

```bash
cd server

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
copy .env.example .env
# Éditer .env avec vos paramètres
```

**Configuration `.env` :**

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/exam_db
# Ou pour SQLite (développement):
# DATABASE_URL=sqlite:///./app.db

# Application
APP_NAME=Exam Management System
APP_VERSION=1.0.0
FRONTEND_ORIGIN=http://localhost:3000

# JWT Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Initialiser la base de données :**

```bash
# Créer les tables
alembic upgrade head

# Créer un compte administrateur
python create_admin_account.sql
```

### 3. Configuration du Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Configurer les variables d'environnement
# Créer un fichier .env.local
```

**Configuration `.env.local` :**

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## 🎮 Démarrage

### Option 1 : Démarrage automatique (Windows)

```bash
# Démarrer frontend + backend ensemble
START_ALL.bat

# Ou séparément :
START_BACKEND.bat   # Backend sur http://localhost:8000
START_FRONTEND.bat  # Frontend sur http://localhost:3000
```

### Option 2 : Démarrage manuel

**Backend :**

```bash
cd server
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
python app/main.py
```

**Frontend :**

```bash
cd frontend
npm run dev
```

### Accès à l'application

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🛠️ Stack technique

### Frontend
- **Framework** : Next.js 16.2 (App Router)
- **UI** : React 19.2
- **Styling** : Tailwind CSS 4.0
- **Language** : TypeScript 5
- **PDF** : @react-pdf/renderer
- **HTTP** : Fetch API native

### Backend
- **Framework** : FastAPI 0.136
- **ORM** : SQLAlchemy 2.0
- **Validation** : Pydantic 2.13
- **Auth** : JWT (python-jose + passlib)
- **Database** : PostgreSQL / SQLite
- **Migrations** : Alembic
- **Server** : Uvicorn

### Algorithmes
- **Génération de planification** : Algorithmes d'optimisation personnalisés
- **Affectation de surveillance** : Algorithmes de répartition équitable
- **Gestion des contraintes** : Validation multi-critères

## 📁 Structure de la base de données

### Tables principales

- **users** : Comptes utilisateurs (admin, enseignants)
- **planifications** : Sessions d'examens
- **examens** : Examens individuels
- **salles** : Salles disponibles
- **surveillances** : Affectations de surveillance
- **indisponibilites** : Indisponibilités des enseignants
- **sections** : Sections académiques
- **matieres** : Matières enseignées
- **groupes** : Groupes d'étudiants

## 🔒 Sécurité

- ✅ Authentification JWT avec tokens sécurisés
- ✅ Hachage des mots de passe avec bcrypt
- ✅ Protection CORS configurée
- ✅ Validation des entrées avec Pydantic
- ✅ Gestion des sessions côté serveur
- ✅ Protection contre les injections SQL (ORM)

## 📊 API Endpoints

### Authentification
```
POST   /api/auth/login          # Connexion
POST   /api/auth/logout         # Déconnexion
GET    /api/auth/me             # Profil utilisateur
```

### Planifications
```
GET    /api/planifications      # Liste des planifications
POST   /api/planifications      # Créer une planification
GET    /api/planifications/{id} # Détails d'une planification
PUT    /api/planifications/{id} # Modifier une planification
DELETE /api/planifications/{id} # Supprimer une planification
POST   /api/planifications/generate # Générer automatiquement
```

### Examens
```
GET    /api/examens             # Liste des examens
POST   /api/examens             # Créer un examen
PUT    /api/examens/{id}        # Modifier un examen
DELETE /api/examens/{id}        # Supprimer un examen
```

### Surveillance
```
GET    /api/surveillances       # Liste des surveillances
POST   /api/surveillances       # Affecter un surveillant
GET    /api/surveillances/charge # Charge par enseignant
GET    /api/surveillances/convocations/{id} # Convocations
```

### Salles
```
GET    /api/salles              # Liste des salles
POST   /api/salles              # Créer une salle
PUT    /api/salles/{id}         # Modifier une salle
DELETE /api/salles/{id}         # Supprimer une salle
```

## 🧪 Tests

```bash
cd server

# Exécuter tous les tests
pytest

# Tests spécifiques
pytest tests/test_planif.py
pytest tests/test_surv.py

# Avec couverture
pytest --cov=app tests/
```

## 📦 Build et déploiement

### Frontend

```bash
cd frontend

# Build de production
npm run build

# Démarrer en production
npm start
```

### Backend

```bash
cd server

# Avec Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Avec Gunicorn (production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🐛 Dépannage

### Le backend ne démarre pas
- Vérifier que l'environnement virtuel est activé
- Vérifier la connexion à la base de données
- Vérifier que le port 8000 n'est pas déjà utilisé

### Le frontend ne se connecte pas au backend
- Vérifier que `NEXT_PUBLIC_API_BASE_URL` est correctement configuré
- Vérifier que le backend est démarré
- Vérifier la configuration CORS dans `server/app/main.py`

### Erreurs de base de données
- Exécuter les migrations : `alembic upgrade head`
- Vérifier les credentials dans `.env`
- Vérifier que PostgreSQL est démarré

## 📝 Scripts utiles

```bash
# Backend
python create_accounts.py              # Créer des comptes de test
python check_admin.py                  # Vérifier les comptes admin
python gestion_comptes_enseignants.py  # Gérer les enseignants

# Frontend
npm run lint                           # Linter le code
npm run build                          # Build de production
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence privée - Faculté des Sciences de Tunis

## 👥 Équipe

Développé pour la Faculté des Sciences de Tunis (FST)

## 📞 Support

Pour toute question ou problème :
- 📧 Email : support@fst.utm.tn


---

<div align="center">
  <p>Fait avec ❤️ pour la FST</p>
  <p>© 2026 Faculté des Sciences de Tunis • Tous droits réservés</p>
</div>
