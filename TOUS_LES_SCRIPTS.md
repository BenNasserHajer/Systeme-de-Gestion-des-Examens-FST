# 📜 Tous les Scripts Disponibles

## 🚀 Scripts de Démarrage

### `START_ALL.bat`
**Description:** Démarre automatiquement backend + frontend
**Usage:** Double-cliquer sur le fichier
**Ce qu'il fait:**
- Vérifie l'environnement
- Démarre le backend (port 8000)
- Démarre le frontend (port 3000)
- Ouvre le navigateur

---

## 🗄️ Scripts SQL

### `server/script.sql`
**Description:** Script SQL principal - Crée toute la structure de la base
**Usage:**
```bash
psql -U postgres -d exam_surveillance -f server/script.sql
```
**Ce qu'il fait:**
- Crée toutes les tables
- Crée les contraintes et index
- Insère des données de test

### `server/add_auth_tables.sql` ⭐ NOUVEAU
**Description:** Ajoute les tables d'authentification JWT
**Usage:**
```bash
psql -U postgres -d exam_surveillance -f server/add_auth_tables.sql
```
**Ce qu'il fait:**
- Crée `compte_enseignant`
- Crée `refresh_token`
- Crée `audit_log`
- Crée des comptes de test
- Crée un compte admin (username: admin, password: admin123)

### `server/fix_data.sql`
**Description:** Corrige les données qui causent des conflits d'affectation
**Usage:**
```bash
psql -U postgres -d exam_surveillance -f server/fix_data.sql
```
**Ce qu'il fait:**
- Fix `section_departement_id` NULL
- Vérifie les charges horaires
- Affiche les statistiques

---

## 🐍 Scripts Python

### `server/create_accounts.py` ⭐ NOUVEAU
**Description:** Gestion interactive des comptes enseignants
**Usage:**
```bash
cd server
.venv\Scripts\activate
python create_accounts.py
```
**Menu:**
1. Créer des comptes pour tous les enseignants
2. Créer un compte admin
3. Créer un compte spécifique
4. Lister tous les comptes
5. Réinitialiser un mot de passe
6. Quitter

### `server/diagnose_conflicts.py`
**Description:** Diagnostic des conflits d'affectation
**Usage:**
```bash
cd server
.venv\Scripts\python diagnose_conflicts.py
```
**Ce qu'il fait:**
- Analyse les planifications VALIDEE
- Vérifie les enseignants disponibles
- Vérifie les charges horaires
- Donne des recommandations

### `server/check_planifications.py`
**Description:** Vérifie l'état des planifications
**Usage:**
```bash
cd server
.venv\Scripts\python check_planifications.py
```

### `server/test_affectation_surveillance.py`
**Description:** Test de l'algorithme d'affectation
**Usage:**
```bash
cd server
.venv\Scripts\python test_affectation_surveillance.py
```

---

## 🔧 Scripts Git

### `COMMIT_FIXES.bat`
**Description:** Commite automatiquement les corrections
**Usage:** Double-cliquer sur le fichier
**Ce qu'il fait:**
- Ajoute les fichiers modifiés
- Crée un commit avec message descriptif
- Propose de pusher

### `PUSH_TO_REMOTE.bat`
**Description:** Push vers origin/Farah avec confirmation
**Usage:** Double-cliquer sur le fichier
**Ce qu'il fait:**
- Affiche l'état Git
- Affiche les commits à pusher
- Demande confirmation
- Push vers origin/Farah

### `VIEW_CHANGES.bat`
**Description:** Affiche les différences Git
**Usage:** Double-cliquer sur le fichier
**Ce qu'il fait:**
- Affiche `git diff` pour chaque fichier modifié
- Montre les changements ligne par ligne

---

## 📚 Documentation

### Guides Principaux

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation principale du projet |
| `GUIDE_DEMARRAGE_RAPIDE.md` | Guide de démarrage complet |
| `GUIDE_AUTHENTIFICATION.md` | Guide complet de l'authentification |
| `QUICK_AUTH_SETUP.md` | Configuration rapide de l'auth |

### Documentation Technique

| Fichier | Description |
|---------|-------------|
| `MERGE_RESOLUTION_COMPLETE.md` | Résolution du merge hajer2 |
| `RESUME_CORRECTIONS.md` | Résumé des corrections |
| `FIX_SALLE_ID_BUG.md` | Documentation du bug Salle.id |
| `TEST_AFFECTATION_FIX.md` | Guide de test de l'affectation |
| `STATUS_FINAL.md` | État final du projet |
| `TOUS_LES_SCRIPTS.md` | Ce fichier |

### Documentation Spécifique

| Fichier | Description |
|---------|-------------|
| `WORKFLOW_PLANIFICATION.md` | Workflow de planification |
| `README_PLANIFICATION.md` | Documentation planification |
| `UI_DESIGN_SUMMARY.md` | Résumé du design UI |
| `DEMARRAGE_RAPIDE.md` | Guide de démarrage (ancien) |
| `CORRECTIONS_SURVEILLANCE.md` | Corrections surveillance |
| `FIX_CATALOGUE_ERROR.md` | Fix erreur catalogue |

---

## 🎯 Workflows Recommandés

### Premier Démarrage

```bash
# 1. Créer la base de données
psql -U postgres -c "CREATE DATABASE exam_surveillance;"

# 2. Créer les tables principales
psql -U postgres -d exam_surveillance -f server/script.sql

# 3. Ajouter l'authentification
psql -U postgres -d exam_surveillance -f server/add_auth_tables.sql

# 4. Corriger les données
psql -U postgres -d exam_surveillance -f server/fix_data.sql

# 5. Démarrer le système
START_ALL.bat
```

### Développement Quotidien

```bash
# 1. Démarrer le système
START_ALL.bat

# 2. Faire des modifications

# 3. Tester

# 4. Commiter
COMMIT_FIXES.bat

# 5. Pusher
PUSH_TO_REMOTE.bat
```

### Gestion des Comptes

```bash
# 1. Créer des comptes
cd server
.venv\Scripts\activate
python create_accounts.py

# 2. Lister les comptes
# Choisir option 4

# 3. Réinitialiser un mot de passe
# Choisir option 5
```

### Diagnostic des Problèmes

```bash
# 1. Vérifier les planifications
cd server
.venv\Scripts\python check_planifications.py

# 2. Diagnostiquer les conflits
.venv\Scripts\python diagnose_conflicts.py

# 3. Corriger les données
psql -U postgres -d exam_surveillance -f fix_data.sql

# 4. Tester l'affectation
.venv\Scripts\python test_affectation_surveillance.py
```

---

## 🔍 Recherche Rapide

### Je veux...

**...démarrer le système**
→ `START_ALL.bat`

**...créer des comptes enseignants**
→ `python create_accounts.py`

**...corriger les conflits d'affectation**
→ `psql -f fix_data.sql`

**...voir les modifications Git**
→ `VIEW_CHANGES.bat`

**...pusher mes commits**
→ `PUSH_TO_REMOTE.bat`

**...diagnostiquer un problème**
→ `python diagnose_conflicts.py`

**...créer la base de données**
→ `psql -f script.sql` puis `psql -f add_auth_tables.sql`

**...réinitialiser un mot de passe**
→ `python create_accounts.py` (option 5)

**...tester l'authentification**
→ Voir `QUICK_AUTH_SETUP.md`

**...comprendre le système**
→ Lire `README.md` et `GUIDE_DEMARRAGE_RAPIDE.md`

---

## 📦 Structure Complète

```
projet/
├── 🚀 Scripts de Démarrage
│   └── START_ALL.bat
│
├── 🔧 Scripts Git
│   ├── COMMIT_FIXES.bat
│   ├── PUSH_TO_REMOTE.bat
│   └── VIEW_CHANGES.bat
│
├── 📚 Documentation
│   ├── README.md
│   ├── GUIDE_DEMARRAGE_RAPIDE.md
│   ├── GUIDE_AUTHENTIFICATION.md
│   ├── QUICK_AUTH_SETUP.md
│   ├── MERGE_RESOLUTION_COMPLETE.md
│   ├── STATUS_FINAL.md
│   └── TOUS_LES_SCRIPTS.md (ce fichier)
│
├── server/
│   ├── 🗄️ Scripts SQL
│   │   ├── script.sql
│   │   ├── add_auth_tables.sql ⭐
│   │   └── fix_data.sql
│   │
│   └── 🐍 Scripts Python
│       ├── create_accounts.py ⭐
│       ├── diagnose_conflicts.py
│       ├── check_planifications.py
│       └── test_affectation_surveillance.py
│
└── frontend/
    └── (code React/Next.js)
```

---

## ✅ Checklist de Vérification

Avant de commencer à travailler:

- [ ] Base de données créée
- [ ] Tables principales créées (`script.sql`)
- [ ] Tables d'authentification créées (`add_auth_tables.sql`)
- [ ] Données corrigées (`fix_data.sql`)
- [ ] Comptes enseignants créés
- [ ] Backend démarre sans erreur
- [ ] Frontend démarre sans erreur
- [ ] Authentification fonctionne
- [ ] Affectation automatique fonctionne

---

**Version:** 1.0.0
**Date:** 2026-05-24
**Status:** ✅ Complet
