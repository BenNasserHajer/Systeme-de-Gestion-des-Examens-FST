# 🚀 Configuration Rapide de l'Authentification

## Installation en 3 Étapes

### 1️⃣ Créer les Tables

```bash
cd server
psql -U postgres -d exam_surveillance -f add_auth_tables.sql
```

✅ Crée les tables `compte_enseignant`, `refresh_token`, `audit_log`
✅ Crée des comptes de test
✅ Crée un compte admin

### 2️⃣ Vérifier les Comptes Créés

```sql
SELECT username, email, is_admin 
FROM compte_enseignant;
```

Devrait afficher:
- `admin` (admin@university.edu) - Admin
- Plusieurs comptes enseignants avec password123

### 3️⃣ Tester la Connexion

**Via Swagger UI:**
1. Ouvrir: http://localhost:8000/docs
2. Section "Authentication"
3. POST /api/auth/login
4. Body: `{"username":"admin","password":"admin123"}`
5. Copier le `access_token`
6. Cliquer "Authorize" en haut
7. Coller le token
8. Tester GET /api/auth/me

**Via curl:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 🔑 Comptes par Défaut

| Username | Password | Email | Admin |
|----------|----------|-------|-------|
| admin | admin123 | admin@university.edu | ✅ Oui |
| nom.prenom | password123 | nom.prenom@university.edu | ❌ Non |

## 🛠️ Gestion des Comptes

### Créer des Comptes pour Tous les Enseignants

```bash
cd server
.venv\Scripts\activate
python create_accounts.py
# Choisir option 1
```

### Réinitialiser un Mot de Passe

```bash
python create_accounts.py
# Choisir option 5
```

### Créer un Compte Admin

```bash
python create_accounts.py
# Choisir option 2
```

## 📡 Utilisation dans le Frontend

```typescript
// Login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { access_token } = await response.json();

// Utiliser le token
const profile = await fetch('http://localhost:8000/api/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## ⚠️ IMPORTANT

**Changez les mots de passe par défaut en production!**

```sql
-- Réinitialiser le mot de passe admin
UPDATE compte_enseignant 
SET hashed_password = '$2b$12$NOUVEAU_HASH'
WHERE username = 'admin';
```

Pour générer un nouveau hash:
```bash
python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('nouveau_password'))"
```

## 📚 Documentation Complète

Voir `GUIDE_AUTHENTIFICATION.md` pour:
- Structure détaillée des tables
- Tous les endpoints API
- Requêtes SQL utiles
- Sécurité et bonnes pratiques
- Dépannage

---

**Prêt à l'emploi!** 🎉
