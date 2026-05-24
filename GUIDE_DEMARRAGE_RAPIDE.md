# 🚀 Guide de Démarrage Rapide - Surveillance System

## ✅ État Actuel du Projet

- ✅ Merge `origin/hajer2` complété
- ✅ Bugs critiques corrigés
- ✅ Dépendances JWT installées
- ✅ Backend et Frontend fonctionnels
- ⏳ Prêt à pusher vers origin/Farah

## 📋 Prérequis

- ✅ Python 3.13 installé
- ✅ Node.js installé
- ✅ PostgreSQL en cours d'exécution
- ✅ Base de données créée et configurée

## 🎯 Démarrage en 3 Étapes

### Option 1: Démarrage Automatique (Recommandé)

Double-cliquez sur: **`START_ALL.bat`**

Ce script va:
1. Vérifier l'environnement
2. Démarrer le backend (port 8000)
3. Démarrer le frontend (port 3000)
4. Ouvrir le navigateur automatiquement

### Option 2: Démarrage Manuel

#### Terminal 1 - Backend
```bash
cd server
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

#### Navigateur
Ouvrir: http://localhost:3000

## 🔧 Correction des Données (Important!)

Les 12 planifications sont en conflit car `section_departement_id` est NULL.

### Méthode 1: Via psql
```bash
cd server
psql -U postgres -d votre_base -f fix_data.sql
```

### Méthode 2: Via pgAdmin
1. Ouvrir pgAdmin
2. Connecter à votre base
3. Ouvrir Query Tool
4. Copier le contenu de `server/fix_data.sql`
5. Exécuter

### Méthode 3: SQL Direct
```sql
UPDATE planification_examen 
SET section_departement_id = 1 
WHERE session_id = 1 AND statut = 'VALIDEE';
```

## 🧪 Test de l'Affectation

1. **Ouvrir:** http://localhost:3000/surveillance/affectation
2. **Sélectionner:** Session 1
3. **Cliquer:** "Lancer l'affectation automatique"
4. **Vérifier:** Des surveillants sont affectés (pas tous en conflit)

## 📚 URLs Importantes

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Interface utilisateur |
| Backend | http://localhost:8000 | API REST |
| API Docs | http://localhost:8000/docs | Documentation Swagger |
| Surveillance | http://localhost:3000/surveillance | Page principale |
| Affectation | http://localhost:3000/surveillance/affectation | Affectation auto |
| Charge | http://localhost:3000/surveillance/charge | Charge enseignants |

## 🔐 Nouvelles Fonctionnalités (de hajer2)

### Authentification JWT
- **Login:** `POST /api/auth/login`
- **Logout:** `POST /api/auth/logout`
- **Profil:** `GET /api/auth/me`

### Indisponibilités
- **Liste:** `GET /api/disponibilites`
- **Créer:** `POST /api/disponibilites`
- **Modifier:** `PUT /api/disponibilites/{id}`
- **Supprimer:** `DELETE /api/disponibilites/{id}`

## 🐛 Dépannage

### Backend ne démarre pas

**Erreur:** `ModuleNotFoundError: No module named 'jose'`

**Solution:**
```bash
cd server
.venv\Scripts\pip install python-jose[cryptography] passlib[bcrypt]
```

### Frontend ne démarre pas

**Erreur:** `Cannot find module`

**Solution:**
```bash
cd frontend
npm install
```

### Erreur "AMPHI-INFO" dans les logs

**Status:** ✅ CORRIGÉ dans le commit `10d22d4`

Si vous voyez encore cette erreur:
```bash
git pull origin Farah
```

### Tous les surveillants en conflit

**Cause:** `section_departement_id` est NULL

**Solution:** Exécuter `fix_data.sql` (voir section ci-dessus)

## 📊 Vérification de l'Installation

### Backend
```bash
cd server
.venv\Scripts\python -c "from app.main import app; print('✅ OK')"
```

### Frontend
```bash
cd frontend
npm run build
```

### Base de Données
```sql
SELECT COUNT(*) FROM planification_examen WHERE session_id = 1 AND statut = 'VALIDEE';
-- Devrait retourner: 12
```

## 🚀 Pusher les Modifications

Une fois que tout fonctionne:

```bash
git status
# Vérifier que tout est commité

git push origin Farah
# Pusher vers le remote
```

## 📝 Scripts Disponibles

| Script | Description |
|--------|-------------|
| `START_ALL.bat` | Démarre backend + frontend |
| `COMMIT_FIXES.bat` | Commite les corrections |
| `VIEW_CHANGES.bat` | Voir les différences Git |
| `server/fix_data.sql` | Corrige les données |
| `server/diagnose_conflicts.py` | Diagnostic des conflits |

## 📖 Documentation Complète

- `MERGE_RESOLUTION_COMPLETE.md` - Résolution complète du merge
- `RESUME_CORRECTIONS.md` - Résumé des corrections
- `FIX_SALLE_ID_BUG.md` - Documentation du bug Salle.id
- `TEST_AFFECTATION_FIX.md` - Guide de test détaillé

## ✅ Checklist de Démarrage

- [ ] Backend démarre sans erreur
- [ ] Frontend démarre sans erreur
- [ ] Page http://localhost:3000 s'affiche
- [ ] API Docs http://localhost:8000/docs accessible
- [ ] Script `fix_data.sql` exécuté
- [ ] Affectation automatique testée
- [ ] Surveillants affectés (pas tous en conflit)
- [ ] Commits pushés vers origin/Farah

## 🎯 Prochaines Étapes

1. ✅ Démarrer le système (START_ALL.bat)
2. ✅ Corriger les données (fix_data.sql)
3. ✅ Tester l'affectation
4. ✅ Vérifier les nouvelles fonctionnalités (Auth + Indispo)
5. ✅ Pusher vers origin/Farah
6. 🔄 Déployer en production (si applicable)

## 💡 Conseils

- **Développement:** Utilisez `--reload` pour le hot-reload
- **Production:** Utilisez `gunicorn` pour le backend
- **Tests:** Exécutez les tests avant de pusher
- **Logs:** Consultez les logs en cas d'erreur

## 🆘 Support

En cas de problème:
1. Vérifier les logs backend et frontend
2. Consulter `MERGE_RESOLUTION_COMPLETE.md`
3. Exécuter `diagnose_conflicts.py` pour diagnostic
4. Vérifier que les dépendances sont installées

---

**Version:** 1.0.0
**Date:** 2026-05-24
**Status:** ✅ PRÊT À L'EMPLOI
