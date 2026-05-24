# Guide de Connexion Admin - Résolution Complète

## ✅ Corrections Effectuées

### 1. Backend - Fichier `server/app/main.py`
- **Problème**: Références à `settings.backend_host` et `settings.backend_port` qui n'existent pas
- **Solution**: Remplacé par des valeurs fixes et `settings.app_name` / `settings.app_version`
- **Lignes modifiées**: 
  - Health check endpoint (ligne ~105)
  - Main execution block (ligne ~115)

### 2. Frontend - Fichier `frontend/src/app/login/page.tsx`
- **État actuel**: ✅ Déjà configuré correctement
- **Credentials affichés**: `admin@fst.utm.tn` / `Admin@2026`
- **Redirection**: `/planification` après login réussi
- **Champs envoyés**: `email` et `mot_de_passe` (format correct)

### 3. Backend - Authentification
- **Fichier**: `server/app/crud/crud_auth.py`
- **Admin hardcodé**: 
  ```python
  ADMIN_EMAIL = "admin@fst.utm.tn"
  ADMIN_PASSWORD = "Admin@2026"
  ```
- **Logique**: Si email == ADMIN_EMAIL → vérifie le mot de passe hardcodé
- **Token JWT**: Créé avec type="ADMIN"

---

## 🚀 Comment Tester

### Étape 1: Démarrer le Backend

```bash
cd server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Vérifications**:
- ✅ Le serveur démarre sans erreur
- ✅ Message: `[startup] database: connected`
- ✅ Message: `[startup] app: PFA Project v1.0.0`
- ✅ Accessible sur: http://localhost:8000/docs

### Étape 2: Tester l'API Directement

**Option A - Avec le script Python**:
```bash
cd c:\Users\dongm\OneDrive\Desktop\projet
python test_login.py
```

**Option B - Avec curl**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@fst.utm.tn\",\"mot_de_passe\":\"Admin@2026\"}"
```

**Option C - Avec Postman/Insomnia**:
- URL: `POST http://localhost:8000/api/auth/login`
- Headers: `Content-Type: application/json`
- Body (JSON):
  ```json
  {
    "email": "admin@fst.utm.tn",
    "mot_de_passe": "Admin@2026"
  }
  ```

**Réponse attendue** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "type": "ADMIN",
    "id": null,
    "email": "admin@fst.utm.tn",
    "enseignant_id": null,
    "nom": null,
    "prenom": null
  }
}
```

### Étape 3: Démarrer le Frontend

```bash
cd frontend
npm run dev
```

**Vérifications**:
- ✅ Frontend accessible sur: http://localhost:3000
- ✅ Page de login: http://localhost:3000/login

### Étape 4: Tester le Login via l'Interface

1. Ouvrir http://localhost:3000/login
2. Entrer les credentials:
   - **Email**: `admin@fst.utm.tn`
   - **Mot de passe**: `Admin@2026`
3. Cliquer sur "Se connecter"
4. **Résultat attendu**: Redirection vers `/planification`

---

## 🔍 Diagnostic des Erreurs

### Erreur: "Email ou mot de passe incorrect"

**Causes possibles**:

1. **Backend non démarré**
   - Vérifier: http://localhost:8000/docs doit être accessible
   - Solution: Démarrer le backend

2. **CORS bloqué**
   - Ouvrir la console du navigateur (F12)
   - Chercher: "CORS policy" ou "Access-Control-Allow-Origin"
   - Solution: Vérifier que `http://localhost:3000` est dans `_cors_origins` (main.py ligne 30)

3. **Mauvais format de requête**
   - Ouvrir Network tab (F12)
   - Vérifier la requête POST vers `/api/auth/login`
   - Body doit contenir: `{"email":"admin@fst.utm.tn","mot_de_passe":"Admin@2026"}`

4. **Erreur 422 Unprocessable Content**
   - Signifie: Champs manquants ou mal nommés
   - Vérifier: Le frontend envoie bien `email` et `mot_de_passe` (pas `username` et `password`)

### Erreur: "Cannot connect to backend"

**Solutions**:
1. Vérifier que le backend tourne sur le bon port:
   ```bash
   netstat -ano | findstr :8000
   ```
2. Tester l'endpoint health:
   ```bash
   curl http://localhost:8000/health
   ```

### Erreur: Redirection ne fonctionne pas

**Vérifications**:
1. Le token est bien stocké dans localStorage:
   - Ouvrir DevTools → Application → Local Storage
   - Chercher: `access_token` et `user`
2. La page `/planification` existe et est accessible

---

## 📋 Checklist de Vérification

### Backend
- [ ] `server/app/main.py` ne référence plus `backend_host` et `backend_port`
- [ ] `server/app/crud/crud_auth.py` contient les credentials admin hardcodés
- [ ] Backend démarre sans erreur
- [ ] Endpoint `/api/auth/login` répond 200 avec les bons credentials
- [ ] CORS autorise `http://localhost:3000`

### Frontend
- [ ] `frontend/src/app/login/page.tsx` envoie `email` et `mot_de_passe`
- [ ] Credentials affichés: `admin@fst.utm.tn` / `Admin@2026`
- [ ] Redirection vers `/planification` après login
- [ ] Page `/planification` existe et affiche le contenu
- [ ] Sidebar affiche les liens "Planification" et "Surveillance"

### Test End-to-End
- [ ] Login avec admin fonctionne
- [ ] Token JWT stocké dans localStorage
- [ ] Redirection vers `/planification` réussie
- [ ] Navigation vers `/surveillance` fonctionne
- [ ] Sidebar affiche tous les liens

---

## 🎯 Prochaines Étapes

### 1. Sécurité (Production)
- [ ] Changer le mot de passe admin hardcodé
- [ ] Utiliser des variables d'environnement pour les secrets
- [ ] Implémenter bcrypt pour les mots de passe enseignants
- [ ] Ajouter refresh tokens
- [ ] Configurer HTTPS

### 2. Fonctionnalités
- [ ] Créer des comptes enseignants dans la base
- [ ] Tester le login enseignant
- [ ] Implémenter la page d'indisponibilité
- [ ] Ajouter la gestion des permissions (RBAC)

### 3. UX
- [ ] Ajouter un AuthProvider global
- [ ] Protéger les routes admin
- [ ] Afficher le nom de l'utilisateur dans la navbar
- [ ] Ajouter un bouton de déconnexion

---

## 📞 Support

Si le problème persiste après avoir suivi ce guide:

1. **Vérifier les logs backend**:
   - Regarder la console où tourne uvicorn
   - Chercher les erreurs 401, 422, ou 500

2. **Vérifier les logs frontend**:
   - Ouvrir DevTools (F12) → Console
   - Chercher les erreurs réseau ou JavaScript

3. **Tester l'API directement**:
   - Utiliser `test_login.py` pour isoler le problème
   - Si le script fonctionne mais pas le frontend → problème frontend
   - Si le script échoue → problème backend

4. **Vérifier la base de données**:
   ```sql
   -- Vérifier la structure de la table
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'compte_enseignant';
   ```

---

## ✨ Résumé

**Ce qui a été corrigé**:
- ✅ Backend: Suppression des références à `backend_host` et `backend_port`
- ✅ Frontend: Déjà configuré avec les bons credentials et redirection
- ✅ Auth: Admin hardcodé fonctionne correctement

**Ce qui devrait fonctionner maintenant**:
- ✅ Login avec `admin@fst.utm.tn` / `Admin@2026`
- ✅ Redirection vers `/planification`
- ✅ Accès aux pages Surveillance et Planification
- ✅ Navigation via la Sidebar

**Pour tester**:
1. Démarrer backend: `cd server && python -m uvicorn app.main:app --reload`
2. Démarrer frontend: `cd frontend && npm run dev`
3. Ouvrir: http://localhost:3000/login
4. Se connecter avec les credentials admin
5. Vérifier la redirection vers `/planification`
