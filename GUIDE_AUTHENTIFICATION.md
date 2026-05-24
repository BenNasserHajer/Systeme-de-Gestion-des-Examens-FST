# 🔐 Guide d'Authentification - Système de Surveillance

## 📋 Vue d'Ensemble

Le système utilise l'authentification JWT (JSON Web Tokens) pour sécuriser l'accès aux fonctionnalités de surveillance et de planification.

## 🗄️ Structure des Tables

### Table `compte_enseignant`
Stocke les informations d'authentification des enseignants.

**Colonnes:**
- `id` - Identifiant unique du compte
- `enseignant_id` - Référence vers la table enseignant (UNIQUE)
- `username` - Nom d'utilisateur unique
- `email` - Email unique
- `hashed_password` - Mot de passe hashé avec bcrypt
- `is_active` - Compte actif/inactif
- `is_admin` - Droits administrateur
- `created_at` - Date de création
- `updated_at` - Date de dernière modification
- `last_login` - Date de dernière connexion

### Table `refresh_token` (optionnel)
Stocke les tokens de rafraîchissement JWT.

### Table `audit_log` (optionnel)
Journal d'audit des connexions et actions.

## 🚀 Installation

### Méthode 1: Script SQL Complet

```bash
cd server
psql -U postgres -d exam_surveillance -f add_auth_tables.sql
```

Ce script va:
1. ✅ Créer les tables nécessaires
2. ✅ Créer les index pour les performances
3. ✅ Créer des comptes de test
4. ✅ Créer un compte admin

### Méthode 2: Script Python Interactif

```bash
cd server
.venv\Scripts\activate
python create_accounts.py
```

Menu interactif pour:
- Créer des comptes pour tous les enseignants
- Créer un compte admin
- Créer un compte spécifique
- Lister tous les comptes
- Réinitialiser un mot de passe

## 🔑 Comptes par Défaut

Après l'exécution du script SQL:

### Compte Admin
```
Username: admin
Password: admin123
Email: admin@university.edu
Droits: Administrateur
```

### Comptes Enseignants
```
Username: nom.prenom (en minuscules, sans espaces)
Password: password123
Email: nom.prenom@university.edu
Droits: Utilisateur standard
```

**⚠️ IMPORTANT:** Changez ces mots de passe en production!

## 📡 Endpoints API

### Authentification

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Réponse:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@university.edu",
    "is_admin": true,
    "enseignant": {
      "id": 1,
      "nom": "Dupont",
      "prenom": "Jean"
    }
  }
}
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

#### Profil Utilisateur
```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Réponse:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@university.edu",
  "is_admin": true,
  "enseignant": {
    "id": 1,
    "nom": "Dupont",
    "prenom": "Jean",
    "grade": "Professeur",
    "departement": {
      "id": 1,
      "nom": "Informatique"
    }
  }
}
```

## 🔧 Gestion des Comptes

### Créer un Compte (SQL)

```sql
-- Générer le hash du mot de passe avec Python:
-- python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('mon_password'))"

INSERT INTO compte_enseignant (
    enseignant_id, 
    username, 
    email, 
    hashed_password, 
    is_active, 
    is_admin
) VALUES (
    5,  -- ID de l'enseignant
    'martin.paul',
    'martin.paul@university.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6',
    TRUE,
    FALSE
);
```

### Créer un Compte (Python)

```python
from create_accounts import create_account, SessionLocal

db = SessionLocal()
compte = create_account(
    db=db,
    enseignant_id=5,
    username="martin.paul",
    email="martin.paul@university.edu",
    password="mon_password",
    is_admin=False
)
db.close()
```

### Activer/Désactiver un Compte

```sql
-- Désactiver
UPDATE compte_enseignant 
SET is_active = FALSE 
WHERE username = 'martin.paul';

-- Activer
UPDATE compte_enseignant 
SET is_active = TRUE 
WHERE username = 'martin.paul';
```

### Réinitialiser un Mot de Passe

**Méthode 1: Python**
```bash
python create_accounts.py
# Choisir option 5
```

**Méthode 2: SQL**
```sql
-- Hash pour "password123"
UPDATE compte_enseignant 
SET hashed_password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'
WHERE username = 'martin.paul';
```

### Promouvoir en Admin

```sql
UPDATE compte_enseignant 
SET is_admin = TRUE 
WHERE username = 'martin.paul';
```

## 🔍 Requêtes Utiles

### Lister Tous les Comptes

```sql
SELECT 
    ce.id,
    ce.username,
    ce.email,
    e.nom,
    e.prenom,
    e.grade,
    d.nom as departement,
    ce.is_active,
    ce.is_admin,
    ce.last_login
FROM compte_enseignant ce
JOIN enseignant e ON ce.enseignant_id = e.id
LEFT JOIN departement d ON e.departement_id = d.id
ORDER BY ce.id;
```

### Comptes Actifs

```sql
SELECT username, email, is_admin
FROM compte_enseignant
WHERE is_active = TRUE
ORDER BY username;
```

### Dernières Connexions

```sql
SELECT 
    ce.username,
    e.nom || ' ' || e.prenom as enseignant,
    ce.last_login,
    ce.is_active
FROM compte_enseignant ce
JOIN enseignant e ON ce.enseignant_id = e.id
ORDER BY ce.last_login DESC NULLS LAST
LIMIT 20;
```

### Comptes Sans Connexion

```sql
SELECT 
    ce.username,
    e.nom || ' ' || e.prenom as enseignant,
    ce.created_at
FROM compte_enseignant ce
JOIN enseignant e ON ce.enseignant_id = e.id
WHERE ce.last_login IS NULL
ORDER BY ce.created_at DESC;
```

### Historique d'Audit

```sql
SELECT 
    al.created_at,
    ce.username,
    al.action,
    al.success,
    al.ip_address
FROM audit_log al
LEFT JOIN compte_enseignant ce ON al.compte_enseignant_id = ce.id
ORDER BY al.created_at DESC
LIMIT 50;
```

## 🔐 Sécurité

### Bonnes Pratiques

1. **Mots de Passe Forts**
   - Minimum 8 caractères
   - Mélange de majuscules, minuscules, chiffres, symboles
   - Pas de mots du dictionnaire

2. **Changement Régulier**
   - Forcer le changement tous les 90 jours
   - Ne pas réutiliser les anciens mots de passe

3. **Comptes Inactifs**
   - Désactiver les comptes non utilisés
   - Supprimer les comptes obsolètes

4. **Audit**
   - Surveiller les tentatives de connexion échouées
   - Alerter sur les activités suspectes

### Configuration JWT

Dans `server/.env`:

```env
# JWT Configuration
JWT_SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ IMPORTANT:** Générez une clé secrète forte:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🧪 Tests

### Test de Connexion (curl)

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Profil (remplacer <TOKEN> par le token reçu)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"

# Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer <TOKEN>"
```

### Test de Connexion (Python)

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
data = response.json()
token = data["access_token"]

# Profil
response = requests.get(
    "http://localhost:8000/api/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

## 🐛 Dépannage

### Erreur: "Invalid credentials"

**Causes:**
- Username ou password incorrect
- Compte désactivé (`is_active = FALSE`)
- Mot de passe mal hashé

**Solution:**
```sql
-- Vérifier le compte
SELECT username, is_active FROM compte_enseignant WHERE username = 'admin';

-- Réinitialiser le mot de passe
UPDATE compte_enseignant 
SET hashed_password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'
WHERE username = 'admin';
```

### Erreur: "Token expired"

**Cause:** Le token JWT a expiré (30 minutes par défaut)

**Solution:** Se reconnecter pour obtenir un nouveau token

### Erreur: "User not found"

**Cause:** Le compte n'existe pas

**Solution:**
```bash
python create_accounts.py
# Créer le compte manquant
```

## 📚 Documentation API Complète

Accéder à la documentation Swagger:
```
http://localhost:8000/docs
```

Section "Authentication" pour tous les endpoints.

## 🔄 Migration depuis Ancien Système

Si vous avez déjà des enseignants sans comptes:

```bash
cd server
.venv\Scripts\activate
python create_accounts.py
# Choisir option 1: Créer des comptes pour tous les enseignants
```

Cela créera automatiquement des comptes pour tous les enseignants existants.

---

**Version:** 1.0.0
**Date:** 2026-05-24
**Status:** ✅ Prêt à l'emploi
