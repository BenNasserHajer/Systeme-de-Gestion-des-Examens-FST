# 🚀 Guide de Démarrage Rapide - Système de Planification

## 📋 Prérequis

- Python 3.10+
- PostgreSQL 14+
- pip (gestionnaire de paquets Python)

---

## ⚡ Installation en 5 Minutes

### 1️⃣ Cloner et Configurer l'Environnement

```bash
# Naviguer vers le dossier serveur
cd PFA/server

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2️⃣ Configurer la Base de Données

```bash
# Créer la base de données PostgreSQL
createdb pfa_examens

# Créer le fichier .env
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/pfa_examens
FRONTEND_ORIGIN=http://localhost:3000
APP_NAME=PFA Exam Planning API
APP_VERSION=1.0.0
EOF
```

### 3️⃣ Initialiser la Base de Données

```bash
# Appliquer les migrations Alembic
alembic upgrade head

# (Optionnel) Charger les données de test
psql -d pfa_examens -f app/seed/script.sql
```

### 4️⃣ Démarrer le Serveur

```bash
# Démarrer FastAPI avec rechargement automatique
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Le serveur est maintenant accessible sur :**
- API : http://127.0.0.1:8000
- Documentation interactive : http://127.0.0.1:8000/docs
- Health check : http://127.0.0.1:8000/health

---

## 🧪 Tester l'Installation

### Test 1 : Health Check

```bash
curl http://127.0.0.1:8000/health
```

**Réponse attendue :**
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2026-01-07T10:30:00"
}
```

### Test 2 : Lister les Planifications

```bash
curl http://127.0.0.1:8000/api/planifications
```

### Test 3 : Exécuter les Tests Unitaires

```bash
pytest tests/test_planif.py -v
```

**Résultat attendu :**
```
tests/test_planif.py::test_decoupage_groupes_equilibre PASSED
tests/test_planif.py::test_contrainte_salle_occupee_detectee PASSED
tests/test_planif.py::test_generation_simple_et_split_best_effort PASSED
tests/test_planif.py::test_emploi_du_temps_trie PASSED

====== 4 passed in 0.5s ======
```

---

## 📝 Exemple d'Utilisation : Génération Automatique

### Scénario : Planifier 10 Examens pour la Section INF/IOT MR2

#### 1. Préparer les Données

**Créneaux disponibles** (23 créneaux sur 8 jours) :
- 07/01/2026 : 08:30-10:30, 11:00-13:00, 14:00-16:00
- 08/01/2026 : 08:30-10:30, 11:00-13:00, 14:00-16:00
- ... (jusqu'au 15/01/2026)

**Salles disponibles** (28 salles) :
- S22 (capacité 25)
- AMPHI INFO (capacité 150)
- I106 (capacité 30)
- ... (autres salles)

**Matières à planifier** (10 matières) :
- Optimisation Combinatoire
- IDM pour les systèmes complexes Temps Réels
- Bases de données avancées
- Sécurité IOT
- Blockchain
- Fouilles de Données
- Big Data
- Applications et plateforme IoT
- Calcul de Haute Performance
- Réseaux IoT

#### 2. Envoyer la Requête de Génération

```bash
curl -X POST http://127.0.0.1:8000/api/sessions/1/generer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "session_date_debut": "2026-01-07",
    "session_date_fin": "2026-01-15",
    "session_statut": "BROUILLON",
    "mode": "AUTO",
    "tasks": [
      {
        "section_id": 1,
        "section_matiere_id": 10,
        "matiere": "Optimisation Combinatoire",
        "type_epreuve": "EXAMEN_FINAL",
        "duree": 120,
        "section_nb_etudiants": 15,
        "coefficient": 2.0,
        "nb_surveillants_requis": 2,
        "a_examen_final": true,
        "a_ds": true
      },
      {
        "section_id": 1,
        "section_matiere_id": 11,
        "matiere": "Bases de données avancées",
        "type_epreuve": "EXAMEN_FINAL",
        "duree": 120,
        "section_nb_etudiants": 15,
        "coefficient": 2.0,
        "nb_surveillants_requis": 2,
        "a_examen_final": true,
        "a_ds": true
      }
    ],
    "creneaux": [
      {
        "date_examen": "2026-01-07",
        "heure_debut": "08:30:00",
        "heure_fin": "10:30:00"
      },
      {
        "date_examen": "2026-01-07",
        "heure_debut": "14:00:00",
        "heure_fin": "16:00:00"
      }
    ],
    "salles": [
      {
        "salle_id": "S22",
        "capacite": 25,
        "batiment": "A"
      },
      {
        "salle_id": "I106",
        "capacite": 30,
        "batiment": "I"
      }
    ]
  }'
```

#### 3. Analyser le Résultat

**Réponse attendue :**
```json
{
  "nb_crees": 2,
  "nb_conflits": 0,
  "conflits": []
}
```

**Interprétation :**
- ✅ 2 planifications créées avec succès
- ✅ 0 conflit détecté
- ✅ Toutes les contraintes respectées

#### 4. Récupérer l'Emploi du Temps

```bash
curl http://127.0.0.1:8000/api/sessions/1/emploi-du-temps
```

**Réponse :**
```json
[
  {
    "id": 1,
    "matiere": "Optimisation Combinatoire",
    "date_examen": "2026-01-07",
    "heure_debut": "08:30:00",
    "heure_fin": "10:30:00",
    "salles": [
      {
        "salle_id": "S22",
        "salle_capacite": 25,
        "groupe_effectif": 15
      }
    ],
    "nb_groupes": 1,
    "statut": "BROUILLON"
  },
  {
    "id": 2,
    "matiere": "Bases de données avancées",
    "date_examen": "2026-01-07",
    "heure_debut": "14:00:00",
    "heure_fin": "16:00:00",
    "salles": [
      {
        "salle_id": "S22",
        "salle_capacite": 25,
        "groupe_effectif": 15
      }
    ],
    "nb_groupes": 1,
    "statut": "BROUILLON"
  }
]
```

---

## 🔍 Cas d'Usage Avancés

### Cas 1 : Section Volumineuse (Découpage Automatique)

**Problème :** 85 étudiants, salle max = 40 places

**Solution :** L'algorithme découpe automatiquement en 3 groupes équilibrés

```json
{
  "section_nb_etudiants": 85,
  "salles": [
    {"salle_id": "A101", "capacite": 40},
    {"salle_id": "A102", "capacite": 40},
    {"salle_id": "B201", "capacite": 35}
  ]
}
```

**Résultat :**
- Groupe 1 : 29 étudiants → Salle A101
- Groupe 2 : 28 étudiants → Salle A102
- Groupe 3 : 28 étudiants → Salle B201
- ✅ Écart max = 1 étudiant (contrainte C9 respectée)

### Cas 2 : Conflit de Salle (Mode Best-Effort)

**Problème :** 2 sections veulent la même salle au même créneau

**Solution :** L'algorithme planifie la première, enregistre le conflit pour la seconde

```json
{
  "nb_crees": 1,
  "nb_conflits": 1,
  "conflits": [
    "[C1] Section L3-INFO / Physique - No slot satisfies all hard constraints"
  ]
}
```

**Action :** L'admin peut :
1. Ajouter des créneaux supplémentaires
2. Ajouter des salles
3. Planifier manuellement la matière en conflit

### Cas 3 : Optimisation Contraintes Souples

**Objectif :** Minimiser les déplacements étudiants (C5)

**Stratégie :** L'algorithme privilégie les salles du même bâtiment

```json
{
  "date_examen": "2026-01-07",
  "salles": [
    {"salle_id": "A101", "batiment": "A"},
    {"salle_id": "A102", "batiment": "A"}
  ]
}
```

**Score :**
- Même bâtiment : score = -5 (bonus)
- Bâtiment différent : score = +10 (pénalité)

---

## 🛠️ Commandes Utiles

### Gestion de l'Environnement

```bash
# Activer l'environnement virtuel
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Désactiver l'environnement
deactivate

# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt

# Geler les dépendances
pip freeze > requirements.txt
```

### Gestion de la Base de Données

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Revenir à la migration précédente
alembic downgrade -1

# Voir l'historique des migrations
alembic history

# Réinitialiser la base (ATTENTION : perte de données)
alembic downgrade base
alembic upgrade head
```

### Tests

```bash
# Exécuter tous les tests
pytest

# Exécuter un test spécifique
pytest tests/test_planif.py::test_decoupage_groupes_equilibre

# Exécuter avec couverture de code
pytest --cov=app tests/

# Exécuter en mode verbose
pytest -v

# Exécuter en mode watch (rechargement automatique)
pytest-watch
```

### Débogage

```bash
# Démarrer avec logs détaillés
uvicorn app.main:app --reload --log-level debug

# Vérifier la connexion à la base
python -c "from app.database import check_connection, SessionLocal; print(check_connection(SessionLocal()))"

# Inspecter les tables
psql -d pfa_examens -c "\dt"

# Voir les planifications en base
psql -d pfa_examens -c "SELECT * FROM planifications;"
```

---

## 📚 Ressources Complémentaires

### Documentation

- **Architecture** : `ALGORITHME_PLANIFICATION.md`
- **État d'implémentation** : `IMPLEMENTATION_STATUS.md`
- **Base de données** : `DB_redme.md`
- **API interactive** : http://127.0.0.1:8000/docs

### Endpoints Principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/planifications` | GET | Liste des planifications |
| `/api/planifications/{id}` | GET | Détail d'une planification |
| `/api/sessions/{id}/generer` | POST | **Génération automatique** |
| `/api/sessions/{id}/emploi-du-temps` | GET | Emploi du temps |
| `/api/planifications/{id}/valider` | POST | Valider une planification |

### Codes d'Erreur

| Code | Signification | Action |
|------|---------------|--------|
| 200 | Succès | - |
| 201 | Créé | - |
| 404 | Non trouvé | Vérifier l'ID |
| 409 | Conflit | Vérifier les contraintes |
| 422 | Validation échouée | Vérifier le payload JSON |
| 500 | Erreur serveur | Consulter les logs |

---

## 🆘 Dépannage

### Problème : "ModuleNotFoundError: No module named 'app'"

**Solution :**
```bash
# Vérifier que l'environnement virtuel est activé
which python  # Doit pointer vers .venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : "Connection refused" (PostgreSQL)

**Solution :**
```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql  # Linux
brew services list  # Mac

# Démarrer PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # Mac
```

### Problème : "Alembic migration failed"

**Solution :**
```bash
# Réinitialiser les migrations
alembic downgrade base
alembic upgrade head

# Si échec persistant, recréer la base
dropdb pfa_examens
createdb pfa_examens
alembic upgrade head
```

### Problème : Tests échouent

**Solution :**
```bash
# Vérifier les dépendances de test
pip install pytest httpx

# Exécuter en mode verbose pour voir les détails
pytest -v -s

# Vérifier que SQLite est disponible
python -c "import sqlite3; print(sqlite3.version)"
```

---

## 🎯 Prochaines Étapes

1. ✅ **Tester l'API** : Utiliser Swagger UI (http://127.0.0.1:8000/docs)
2. ✅ **Charger les données** : Exécuter `app/seed/script.sql`
3. ✅ **Générer un emploi du temps** : POST `/api/sessions/1/generer`
4. ✅ **Intégrer le frontend** : Connecter Next.js à l'API
5. ✅ **Déployer en production** : Configurer Nginx + Gunicorn

---

## 📞 Support

- **Documentation** : Consulter `ALGORITHME_PLANIFICATION.md`
- **Issues** : Ouvrir un ticket sur le dépôt Git
- **Email** : contact@pfa-examens.tn

---

**🚀 Bon développement !**
