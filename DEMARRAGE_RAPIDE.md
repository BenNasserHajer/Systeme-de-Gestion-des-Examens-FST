# 🚀 Démarrage Rapide - PFA Planification

## Prérequis

- ✅ Python 3.13.5
- ✅ Node.js (pour le frontend)
- ✅ PostgreSQL (base de données)

## 1️⃣ Configuration de la Base de Données

### Créer la base de données
```sql
CREATE DATABASE plani;
```

### Vérifier la connexion
```bash
psql -U postgres -d plani
```

## 2️⃣ Démarrage du Backend

### Terminal 1 - Backend
```bash
cd PFA/server

# Appliquer les migrations
alembic upgrade head

# Démarrer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Vérification Backend
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- API Base: http://localhost:8000/api

## 3️⃣ Démarrage du Frontend

### Terminal 2 - Frontend
```bash
cd PFA/frontend

# Installer les dépendances (première fois seulement)
npm install

# Démarrer le serveur de développement
npm run dev
```

### Vérification Frontend
- Application: http://localhost:3000

## 4️⃣ Test Rapide

### Test Backend (API)
```bash
# Dans un nouveau terminal
curl http://localhost:8000/health
```

Réponse attendue:
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2026-04-25T..."
}
```

### Test des Planifications
```bash
curl http://localhost:8000/api/planifications/
```

## 📋 Routes API Principales

### Planifications
```
GET    /api/planifications/              - Liste
GET    /api/planifications/{id}          - Détail
POST   /api/planifications/              - Créer
PUT    /api/planifications/{id}          - Modifier
DELETE /api/planifications/{id}          - Supprimer
POST   /api/planifications/{id}/valider  - Valider
POST   /api/planifications/{id}/publier  - Publier
```

### Génération Automatique
```
POST   /api/sessions/{id}/generer        - Générer automatiquement
```

### Emploi du Temps
```
GET    /api/sessions/{id}/emploi-du-temps - Consulter l'emploi du temps
```

## 🔧 Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/plani
FRONTEND_ORIGIN=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## 🐛 Dépannage

### Erreur: "Connection refused" (Backend)
```bash
# Vérifier que PostgreSQL est démarré
sudo service postgresql status

# Redémarrer PostgreSQL si nécessaire
sudo service postgresql start
```

### Erreur: "Module not found" (Backend)
```bash
cd PFA/server
pip install -r requirements.txt
```

### Erreur: "Cannot find module" (Frontend)
```bash
cd PFA/frontend
rm -rf node_modules package-lock.json
npm install
```

### Erreur: "Port already in use"
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

## 📚 Documentation Complète

- **Backend**: `PFA/server/README.md`
- **Vérification**: `PFA/VERIFICATION_BACKEND.md`
- **Nettoyage**: `PFA/RESUME_NETTOYAGE.md`
- **Organisation**: `PFA/ORGANISATION_COMPLETE.md`

## ✅ Checklist de Démarrage

- [ ] PostgreSQL démarré
- [ ] Base de données `plani` créée
- [ ] Migrations appliquées (`alembic upgrade head`)
- [ ] Backend démarré (port 8000)
- [ ] Frontend démarré (port 3000)
- [ ] Health check OK
- [ ] API accessible

## 🎯 Prochaines Étapes

1. Tester les endpoints via http://localhost:8000/docs
2. Créer une session d'examen
3. Ajouter des matières et sections
4. Générer automatiquement les planifications
5. Consulter l'emploi du temps

---

**Bon développement! 🚀**
