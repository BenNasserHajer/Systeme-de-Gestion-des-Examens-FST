# Résolution Finale - Problème de Login Admin

## 📌 Contexte

**Problème initial**: Login échoue avec "Email ou mot de passe incorrect" malgré l'utilisation des credentials corrects.

**Credentials admin hardcodés**:
- Email: `admin@fst.utm.tn`
- Mot de passe: `Admin@2026`

---

## ✅ Corrections Appliquées

### 1. Backend - `server/app/main.py`

**Problème**: Références à des attributs inexistants `settings.backend_host` et `settings.backend_port`

**Correction ligne ~105** (health check):
```python
# AVANT
return {
    "status": "ok" if is_db_connected else "degraded",
    "database": "connected" if is_db_connected else "disconnected",
    "timestamp": datetime.now().isoformat(),
    "server": {
        "host": settings.backend_host,  # ❌ N'existe pas
        "port": settings.backend_port,  # ❌ N'existe pas
    },
}

# APRÈS
return {
    "status": "ok" if is_db_connected else "degraded",
    "database": "connected" if is_db_connected else "disconnected",
    "timestamp": datetime.now().isoformat(),
    "app": {
        "name": settings.app_name,      # ✅ Existe
        "version": settings.app_version, # ✅ Existe
    },
}
```

**Correction ligne ~115** (main execution):
```python
# AVANT
if __name__ == "__main__":
    print(f" Starting {settings.app_name} v{settings.app_version}")
    print(f" Server: http://{settings.backend_host}:{settings.backend_port}")  # ❌
    print(f" API Docs: http://{settings.backend_host}:{settings.backend_port}/docs")  # ❌
    
    uvicorn.run(
        "main:app",
        host=settings.backend_host,  # ❌
        port=settings.backend_port,  # ❌
        reload=True,
    )

# APRÈS
if __name__ == "__main__":
    print(f" Starting {settings.app_name} v{settings.app_version}")
    print(f" Server: http://localhost:8000")  # ✅
    print(f" API Docs: http://localhost:8000/docs")  # ✅
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # ✅
        port=8000,       # ✅
        reload=True,
    )
```

---

## 🔍 Vérification de la Configuration

### Backend - Authentification

**Fichier**: `server/app/crud/crud_auth.py`

```python
# Credentials admin hardcodés (lignes 18-19)
ADMIN_EMAIL    = "admin@fst.utm.tn"
ADMIN_PASSWORD = "Admin@2026"

# Fonction de login (ligne 35+)
def login_admin(payload: LoginRequest, response: Response) -> LoginResponse:
    if payload.email != ADMIN_EMAIL or payload.mot_de_passe != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    # ... reste du code
```

**Fichier**: `server/app/schemas/auth_schema.py`

```python
# Schéma de requête (ligne 12+)
class LoginRequest(BaseModel):
    email:       str          # ✅ Champ attendu
    mot_de_passe: str         # ✅ Champ attendu (pas "password")
```

**Fichier**: `server/app/routers/auth_router.py`

```python
# Route de login (ligne 18+)
@router.post("/login", response_model=LoginResponse)
def route_login(
    payload:  LoginRequest,
    response: Response,
    db:       Session = Depends(get_db),
):
    return login(payload, response, db)  # ✅ Appelle crud_auth.login()
```

### Frontend - Page de Login

**Fichier**: `frontend/src/app/login/page.tsx`

```typescript
// État du formulaire (ligne 11+)
const [formData, setFormData] = useState({
  email: "",           // ✅ Correspond au backend
  mot_de_passe: "",    // ✅ Correspond au backend
});

// Soumission (ligne 28+)
const response = await fetch("http://localhost:8000/api/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(formData),  // ✅ Envoie { email, mot_de_passe }
});

// Redirection après succès (ligne 48)
router.push("/planification");  // ✅ Redirige vers planification
```

**Credentials affichés** (ligne 350+):
```typescript
<div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
  <span className="text-xs font-semibold text-blue-700">
    👑 Administrateur
  </span>
  <div className="space-y-1">
    <div className="flex items-center justify-between text-sm">
      <span className="text-gray-600">Email:</span>
      <code className="font-mono text-gray-700">admin@fst.utm.tn</code>  {/* ✅ */}
    </div>
    <div className="flex items-center justify-between text-sm">
      <span className="text-gray-600">Mot de passe:</span>
      <code className="font-mono text-gray-700">Admin@2026</code>  {/* ✅ */}
    </div>
  </div>
</div>
```

### Navigation - Sidebar

**Fichier**: `frontend/src/components/ui/Sidebar.tsx`

```typescript
const links = [
  { href: "/planification", label: "Planification" },  // ✅
  { href: "/surveillance", label: "Surveillance" },    // ✅
  { href: "/surveillance/affectation", label: "Affectation" },
  { href: "/surveillance/charge", label: "Charges" },
  { href: "/salles", label: "Salles" },
];
```

---

## 🚀 Instructions de Test

### Étape 1: Démarrer le Backend

```bash
cd c:\Users\dongm\OneDrive\Desktop\projet\server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Vérifications**:
- ✅ Aucune erreur `AttributeError: 'Settings' object has no attribute 'backend_host'`
- ✅ Message: `[startup] database: connected`
- ✅ Message: `[startup] app: PFA Project v1.0.0`
- ✅ Message: `[startup] CORS allowed: ['http://localhost:3000', ...]`

### Étape 2: Tester l'API (Optionnel)

**Option A - Script de diagnostic complet**:
```bash
cd c:\Users\dongm\OneDrive\Desktop\projet
python diagnose_auth.py
```

**Option B - Test simple**:
```bash
python test_login.py
```

**Résultat attendu**:
```
Testing admin login...
URL: http://localhost:8000/api/auth/login
Payload: {
  "email": "admin@fst.utm.tn",
  "mot_de_passe": "Admin@2026"
}

Status Code: 200
Response: {
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

✅ Login successful!
```

### Étape 3: Démarrer le Frontend

```bash
cd c:\Users\dongm\OneDrive\Desktop\projet\frontend
npm run dev
```

**Vérifications**:
- ✅ Frontend démarre sur http://localhost:3000
- ✅ Aucune erreur de compilation

### Étape 4: Tester le Login via l'Interface

1. **Ouvrir**: http://localhost:3000/login
2. **Entrer les credentials**:
   - Email: `admin@fst.utm.tn`
   - Mot de passe: `Admin@2026`
3. **Cliquer**: "Se connecter"
4. **Vérifier**:
   - ✅ Pas d'erreur "Email ou mot de passe incorrect"
   - ✅ Redirection vers http://localhost:3000/planification
   - ✅ Sidebar visible avec liens "Planification" et "Surveillance"
   - ✅ Token stocké dans localStorage (DevTools → Application → Local Storage)

---

## 🐛 Diagnostic des Problèmes

### Si le login échoue toujours

**1. Vérifier les logs backend**:
```
INFO:     127.0.0.1:xxxxx - "POST /api/auth/login HTTP/1.1" 401 Unauthorized
```
→ Credentials incorrects dans le backend

```
INFO:     127.0.0.1:xxxxx - "POST /api/auth/login HTTP/1.1" 422 Unprocessable Content
```
→ Champs manquants ou mal nommés

**2. Vérifier la console du navigateur** (F12):
```
POST http://localhost:8000/api/auth/login 401 (Unauthorized)
```
→ Backend rejette les credentials

```
Access to fetch at 'http://localhost:8000/api/auth/login' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```
→ Problème CORS (vérifier `_cors_origins` dans main.py)

**3. Vérifier la requête réseau** (F12 → Network → login):
```json
Request Payload:
{
  "email": "admin@fst.utm.tn",
  "mot_de_passe": "Admin@2026"
}
```
→ Doit correspondre exactement à ces champs

**4. Exécuter le script de diagnostic**:
```bash
python diagnose_auth.py
```
→ Identifie automatiquement le problème

---

## 📁 Fichiers Créés

1. **`test_login.py`**: Script simple pour tester le login admin
2. **`diagnose_auth.py`**: Script de diagnostic complet (5 tests)
3. **`GUIDE_LOGIN_ADMIN.md`**: Guide détaillé avec checklist
4. **`RESOLUTION_LOGIN_FINAL.md`**: Ce document (résumé des corrections)

---

## 📋 Checklist Finale

### Backend
- [x] `server/app/main.py` corrigé (pas de `backend_host`/`backend_port`)
- [x] `server/app/crud/crud_auth.py` contient admin hardcodé
- [x] `server/app/schemas/auth_schema.py` définit `email` et `mot_de_passe`
- [x] `server/app/routers/auth_router.py` expose `/api/auth/login`
- [x] CORS autorise `http://localhost:3000`

### Frontend
- [x] `frontend/src/app/login/page.tsx` envoie les bons champs
- [x] Credentials admin affichés correctement
- [x] Redirection vers `/planification` après login
- [x] Pages `/planification` et `/surveillance` existent
- [x] Sidebar affiche les liens de navigation

### Tests
- [ ] Backend démarre sans erreur
- [ ] `python test_login.py` retourne 200 OK
- [ ] `python diagnose_auth.py` passe tous les tests
- [ ] Login via interface fonctionne
- [ ] Redirection vers `/planification` réussie
- [ ] Navigation vers `/surveillance` fonctionne

---

## 🎯 Résultat Attendu

Après avoir appliqué ces corrections et suivi les étapes de test:

1. ✅ **Backend démarre** sans erreur `AttributeError`
2. ✅ **Login admin fonctionne** avec `admin@fst.utm.tn` / `Admin@2026`
3. ✅ **Token JWT créé** et stocké dans localStorage
4. ✅ **Redirection automatique** vers `/planification`
5. ✅ **Sidebar affiche** les liens Planification et Surveillance
6. ✅ **Navigation fonctionne** entre les pages admin

---

## 📞 Si le Problème Persiste

1. **Exécuter le diagnostic**:
   ```bash
   python diagnose_auth.py
   ```

2. **Vérifier les logs**:
   - Backend: Console où tourne uvicorn
   - Frontend: DevTools (F12) → Console + Network

3. **Consulter les guides**:
   - `GUIDE_LOGIN_ADMIN.md`: Guide détaillé
   - `STATUS_FINAL.md`: État global du projet
   - `MERGE_RESOLUTION_COMPLETE.md`: Détails du merge

4. **Tester l'API directement**:
   - Utiliser Postman/Insomnia
   - Ou curl: `curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@fst.utm.tn\",\"mot_de_passe\":\"Admin@2026\"}"`

---

## ✨ Conclusion

**Corrections appliquées**:
- ✅ Backend: Suppression des références à `backend_host` et `backend_port`
- ✅ Frontend: Déjà correctement configuré
- ✅ Scripts de test créés pour faciliter le diagnostic

**Prochaines étapes**:
1. Démarrer backend et frontend
2. Tester le login avec les credentials admin
3. Vérifier la redirection et la navigation
4. Si tout fonctionne → Passer à la génération de surveillance

**Commandes rapides**:
```bash
# Terminal 1 - Backend
cd server && python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev

# Terminal 3 - Test (optionnel)
python diagnose_auth.py
```
