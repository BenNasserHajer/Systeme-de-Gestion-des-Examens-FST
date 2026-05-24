# 🚀 Démarrage Rapide - Authentification Admin

## ⚡ Démarrage en 3 Étapes

### 1️⃣ Démarrer le Backend
```bash
# Double-cliquer sur:
START_BACKEND.bat

# OU en ligne de commande:
cd server
python -m uvicorn app.main:app --reload
```

**Vérification**: http://localhost:8000/docs doit être accessible

---

### 2️⃣ Démarrer le Frontend
```bash
# Double-cliquer sur:
START_FRONTEND.bat

# OU en ligne de commande:
cd frontend
npm run dev
```

**Vérification**: http://localhost:3000 doit être accessible

---

### 3️⃣ Se Connecter
1. Ouvrir: http://localhost:3000/login
2. Entrer:
   - **Email**: `admin@fst.utm.tn`
   - **Mot de passe**: `Admin@2026`
3. Cliquer: "Se connecter"
4. **Résultat**: Redirection vers `/planification`

---

## 🧪 Test Automatique

```bash
# Double-cliquer sur:
TEST_AUTH.bat

# OU en ligne de commande:
python diagnose_auth.py
```

Ce script vérifie automatiquement:
- ✅ Backend accessible
- ✅ API documentation disponible
- ✅ Login admin fonctionne
- ✅ Token JWT valide
- ✅ CORS configuré

---

## 📋 Credentials Admin

| Champ | Valeur |
|-------|--------|
| **Email** | `admin@fst.utm.tn` |
| **Mot de passe** | `Admin@2026` |
| **Type** | ADMIN (hardcodé) |

---

## 🔗 URLs Importantes

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Login** | http://localhost:3000/login |
| **Planification** | http://localhost:3000/planification |
| **Surveillance** | http://localhost:3000/surveillance |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

---

## 🛠️ Scripts Disponibles

| Script | Description |
|--------|-------------|
| `START_BACKEND.bat` | Démarre le serveur FastAPI |
| `START_FRONTEND.bat` | Démarre le serveur Next.js |
| `TEST_AUTH.bat` | Teste l'authentification |
| `test_login.py` | Test simple du login |
| `diagnose_auth.py` | Diagnostic complet (5 tests) |

---

## 📖 Documentation Complète

| Document | Contenu |
|----------|---------|
| `RESOLUTION_LOGIN_FINAL.md` | Résumé des corrections appliquées |
| `GUIDE_LOGIN_ADMIN.md` | Guide détaillé avec troubleshooting |
| `STATUS_FINAL.md` | État global du projet |

---

## ✅ Checklist de Vérification

### Avant de commencer
- [ ] PostgreSQL est démarré
- [ ] Base de données existe et est accessible
- [ ] Python 3.x installé
- [ ] Node.js installé

### Backend
- [ ] `cd server && python -m uvicorn app.main:app --reload` démarre sans erreur
- [ ] http://localhost:8000/docs est accessible
- [ ] http://localhost:8000/health retourne `{"status": "ok"}`

### Frontend
- [ ] `cd frontend && npm run dev` démarre sans erreur
- [ ] http://localhost:3000 est accessible
- [ ] http://localhost:3000/login affiche la page de connexion

### Authentification
- [ ] Login avec `admin@fst.utm.tn` / `Admin@2026` fonctionne
- [ ] Redirection vers `/planification` après login
- [ ] Token stocké dans localStorage
- [ ] Sidebar affiche les liens de navigation

---

## 🐛 Problèmes Courants

### Backend ne démarre pas

**Erreur**: `ModuleNotFoundError: No module named 'jose'`
```bash
cd server
pip install python-jose[cryptography] passlib[bcrypt]
```

**Erreur**: `AttributeError: 'Settings' object has no attribute 'backend_host'`
→ ✅ Déjà corrigé dans `server/app/main.py`

**Erreur**: `Database connection failed`
```bash
# Vérifier PostgreSQL
psql -U postgres -d mydb -c "SELECT 1"
```

### Frontend ne démarre pas

**Erreur**: `Cannot find module 'next'`
```bash
cd frontend
npm install
```

**Erreur**: Port 3000 déjà utilisé
```bash
# Changer le port
npm run dev -- -p 3001
```

### Login échoue

**Erreur**: "Email ou mot de passe incorrect"
```bash
# Tester l'API directement
python test_login.py
```

**Erreur**: CORS bloqué
→ Vérifier `_cors_origins` dans `server/app/main.py` ligne 30

**Erreur**: 422 Unprocessable Content
→ Vérifier que le frontend envoie `email` et `mot_de_passe` (pas `username` et `password`)

---

## 🎯 Workflow Complet

```
1. Démarrer PostgreSQL
   ↓
2. Démarrer Backend (START_BACKEND.bat)
   ↓
3. Vérifier: http://localhost:8000/docs
   ↓
4. Démarrer Frontend (START_FRONTEND.bat)
   ↓
5. Vérifier: http://localhost:3000
   ↓
6. Tester Auth (TEST_AUTH.bat) [Optionnel]
   ↓
7. Se connecter: http://localhost:3000/login
   ↓
8. Utiliser l'application
```

---

## 💡 Conseils

1. **Toujours démarrer le backend avant le frontend**
2. **Utiliser `TEST_AUTH.bat` pour diagnostiquer les problèmes**
3. **Consulter les logs** en cas d'erreur:
   - Backend: Console où tourne uvicorn
   - Frontend: DevTools (F12) → Console
4. **Vérifier la base de données** si les données ne s'affichent pas
5. **Redémarrer les serveurs** après modification du code

---

## 🔐 Sécurité (Production)

⚠️ **Important**: Ces credentials sont pour le développement uniquement!

Pour la production:
- [ ] Changer le mot de passe admin
- [ ] Utiliser des variables d'environnement
- [ ] Implémenter bcrypt pour les mots de passe
- [ ] Configurer HTTPS
- [ ] Ajouter rate limiting
- [ ] Implémenter refresh tokens

---

## 📞 Support

Si vous rencontrez des problèmes:

1. **Exécuter le diagnostic**: `python diagnose_auth.py`
2. **Consulter les guides**: `GUIDE_LOGIN_ADMIN.md`
3. **Vérifier les logs**: Backend + Frontend
4. **Tester l'API**: `python test_login.py`

---

## ✨ Résumé

**Pour démarrer rapidement**:
1. Double-cliquer sur `START_BACKEND.bat`
2. Double-cliquer sur `START_FRONTEND.bat`
3. Ouvrir http://localhost:3000/login
4. Se connecter avec `admin@fst.utm.tn` / `Admin@2026`

**Pour tester**:
- Double-cliquer sur `TEST_AUTH.bat`

**Pour diagnostiquer**:
- Consulter `GUIDE_LOGIN_ADMIN.md`
- Consulter `RESOLUTION_LOGIN_FINAL.md`

🎉 **C'est tout! Vous êtes prêt à utiliser l'application.**
