# 📖 Exemples Swagger - API Planification

## 🎯 Comment Utiliser Swagger

### Accéder à Swagger UI

1. **Démarrer le serveur** :
```bash
cd PFA/server
uvicorn app.main:app --reload
```

2. **Ouvrir Swagger** : http://127.0.0.1:8000/docs

3. **Tester les endpoints** directement dans l'interface

---

## 📡 Exemples par Endpoint

### 1. GET /api/planifications

**Description** : Liste toutes les planifications avec filtres

**Swagger UI** :
1. Cliquer sur `GET /api/planifications`
2. Cliquer sur "Try it out"
3. Remplir les paramètres (optionnels) :
   - `session_id`: 1
   - `type_epreuve`: EXAMEN_FINAL
4. Cliquer sur "Execute"

**Réponse Attendue** :
```json
[
  {
    "id": 1,
    "session_id": 1,
    "section_id": 1,
    "section_matiere_id": 10,
    "type_epreuve": "EXAMEN_FINAL",
    "date_examen": "2026-01-07",
    "heure_debut": "08:30:00",
    "heure_fin": "10:30:00",
    "duree": 120,
    "statut": "BROUILLON",
    "nb_groupes": 1,
    "salles": [
      {
        "id": 1,
        "salle_id": "AMPHI-INFO",
        "salle_code": "AMPHI-INFO",
        "salle_designation": "Amphithéâtre Informatique",
        "salle_capacite": 150,
        "groupe_numero": 1,
        "groupe_effectif": 53
      }
    ]
  }
]
```

---

### 2. POST /api/sessions/{session_id}/generer

**Description** : Génère automatiquement les planifications (⭐ PRINCIPAL)

**Swagger UI** :
1. Cliquer sur `POST /api/sessions/{session_id}/generer`
2. Cliquer sur "Try it out"
3. Entrer `session_id`: 1
4. Copier-coller le JSON ci-dessous dans le body
5. Cliquer sur "Execute"

**Body Exemple** :
```json
{
  "session_id": 1,
  "session_date_debut": "2026-01-07",
  "session_date_fin": "2026-01-15",
  "session_statut": "BROUILLON",
  "mode": "AUTO",
  "tasks": [
    {
      "section_id": 1,
      "section_matiere_id": 10,
      "matiere": "Machine Learning & Deep Learning",
      "type_epreuve": "EXAMEN_FINAL",
      "duree": 120,
      "section_nb_etudiants": 53,
      "coefficient": 2.5,
      "nb_surveillants_requis": 2,
      "a_examen_final": true,
      "a_ds": true
    },
    {
      "section_id": 1,
      "section_matiere_id": 11,
      "matiere": "Big Data",
      "type_epreuve": "EXAMEN_FINAL",
      "duree": 120,
      "section_nb_etudiants": 53,
      "coefficient": 2.5,
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
      "heure_debut": "11:00:00",
      "heure_fin": "13:00:00"
    },
    {
      "date_examen": "2026-01-07",
      "heure_debut": "14:00:00",
      "heure_fin": "16:00:00"
    }
  ],
  "salles": [
    {
      "salle_id": "AMPHI-INFO",
      "capacite": 150,
      "batiment": "Info"
    },
    {
      "salle_id": "S30A",
      "capacite": 30,
      "batiment": "A"
    },
    {
      "salle_id": "S30B",
      "capacite": 30,
      "batiment": "A"
    }
  ]
}
```

**Réponse Attendue (Succès)** :
```json
{
  "nb_crees": 2,
  "nb_conflits": 0,
  "conflits": [],
  "planifications": [
    {
      "id": 1,
      "matiere": "Machine Learning & Deep Learning",
      "date_examen": "2026-01-07",
      "heure_debut": "08:30:00",
      "heure_fin": "10:30:00",
      "salles": ["AMPHI-INFO"],
      "nb_groupes": 1
    },
    {
      "id": 2,
      "matiere": "Big Data",
      "date_examen": "2026-01-07",
      "heure_debut": "11:00:00",
      "heure_fin": "13:00:00",
      "salles": ["AMPHI-INFO"],
      "nb_groupes": 1
    }
  ]
}
```

**Réponse Attendue (Avec Conflits)** :
```json
{
  "nb_crees": 1,
  "nb_conflits": 1,
  "conflits": [
    "[C1] Section-1 / Big Data - No available room for slot 2026-01-07 11:00-13:00"
  ],
  "planifications": [
    {
      "id": 1,
      "matiere": "Machine Learning & Deep Learning",
      "date_examen": "2026-01-07",
      "heure_debut": "08:30:00",
      "heure_fin": "10:30:00",
      "salles": ["AMPHI-INFO"],
      "nb_groupes": 1
    }
  ]
}
```

---

### 3. GET /api/sessions/{session_id}/emploi-du-temps

**Description** : Récupère l'emploi du temps complet

**Swagger UI** :
1. Cliquer sur `GET /api/sessions/{session_id}/emploi-du-temps`
2. Cliquer sur "Try it out"
3. Entrer `session_id`: 1
4. (Optionnel) Filtrer par `section_id`: 1
5. Cliquer sur "Execute"

**Réponse Attendue** :
```json
[
  {
    "date_examen": "2026-01-07",
    "examens": [
      {
        "heure_debut": "08:30:00",
        "heure_fin": "10:30:00",
        "matiere": "Machine Learning & Deep Learning",
        "section": "IGL4",
        "type_epreuve": "EXAMEN_FINAL",
        "salles": [
          {
            "code": "AMPHI-INFO",
            "capacite": 150,
            "effectif": 53,
            "groupe": 1
          }
        ],
        "nb_groupes": 1,
        "statut": "BROUILLON"
      },
      {
        "heure_debut": "11:00:00",
        "heure_fin": "13:00:00",
        "matiere": "Big Data",
        "section": "IGL4",
        "type_epreuve": "EXAMEN_FINAL",
        "salles": [
          {
            "code": "AMPHI-INFO",
            "capacite": 150,
            "effectif": 53,
            "groupe": 1
          }
        ],
        "nb_groupes": 1,
        "statut": "BROUILLON"
      }
    ]
  }
]
```

---

### 4. POST /api/planifications

**Description** : Créer une planification manuellement

**Swagger UI** :
1. Cliquer sur `POST /api/planifications`
2. Cliquer sur "Try it out"
3. Copier-coller le JSON ci-dessous
4. Cliquer sur "Execute"

**Body Exemple** :
```json
{
  "session_id": 1,
  "section_id": 1,
  "section_matiere_id": 12,
  "type_epreuve": "EXAMEN_FINAL",
  "date_examen": "2026-01-08",
  "heure_debut": "08:30:00",
  "heure_fin": "10:30:00",
  "duree": 120,
  "nb_groupes": 1,
  "salles": [
    {
      "salle_id": "AMPHI-INFO",
      "groupe_numero": 1,
      "groupe_effectif": 53
    }
  ]
}
```

**Réponse Attendue** :
```json
{
  "id": 15,
  "session_id": 1,
  "section_id": 1,
  "section_matiere_id": 12,
  "type_epreuve": "EXAMEN_FINAL",
  "date_examen": "2026-01-08",
  "heure_debut": "08:30:00",
  "heure_fin": "10:30:00",
  "duree": 120,
  "statut": "BROUILLON",
  "nb_groupes": 1,
  "salles": [
    {
      "id": 20,
      "salle_id": "AMPHI-INFO",
      "salle_code": "AMPHI-INFO",
      "salle_designation": "Amphithéâtre Informatique",
      "salle_capacite": 150,
      "groupe_numero": 1,
      "groupe_effectif": 53
    }
  ]
}
```

---

### 5. PUT /api/planifications/{id}

**Description** : Mettre à jour une planification

**Swagger UI** :
1. Cliquer sur `PUT /api/planifications/{id}`
2. Cliquer sur "Try it out"
3. Entrer `id`: 1
4. Modifier les champs souhaités dans le JSON
5. Cliquer sur "Execute"

**Body Exemple** :
```json
{
  "date_examen": "2026-01-08",
  "heure_debut": "14:00:00",
  "heure_fin": "16:00:00"
}
```

**Réponse Attendue** :
```json
{
  "id": 1,
  "date_examen": "2026-01-08",
  "heure_debut": "14:00:00",
  "heure_fin": "16:00:00",
  ...
}
```

---

### 6. POST /api/planifications/{id}/valider

**Description** : Valider une planification (BROUILLON → VALIDEE)

**Swagger UI** :
1. Cliquer sur `POST /api/planifications/{id}/valider`
2. Cliquer sur "Try it out"
3. Entrer `id`: 1
4. Cliquer sur "Execute"

**Réponse Attendue** :
```json
{
  "id": 1,
  "statut": "VALIDEE",
  "date_validation": "2026-01-07T10:30:00",
  ...
}
```

---

### 7. POST /api/planifications/{id}/publier

**Description** : Publier une planification (VALIDEE → PUBLIEE)

**Swagger UI** :
1. Cliquer sur `POST /api/planifications/{id}/publier`
2. Cliquer sur "Try it out"
3. Entrer `id`: 1
4. Cliquer sur "Execute"

**Réponse Attendue** :
```json
{
  "id": 1,
  "statut": "PUBLIEE",
  "date_publication": "2026-01-07T11:00:00",
  ...
}
```

---

### 8. DELETE /api/planifications/{id}

**Description** : Supprimer une planification

**Swagger UI** :
1. Cliquer sur `DELETE /api/planifications/{id}`
2. Cliquer sur "Try it out"
3. Entrer `id`: 1
4. Cliquer sur "Execute"

**Réponse Attendue** :
- **Code 204** : No Content (suppression réussie)

---

## 🎨 Tester avec des Données Réelles

### Prérequis

```bash
# 1. Charger les données IGL4
cd PFA/server
psql -d pfa_examens -f app/seed/seed_igl4.sql

# 2. Démarrer le serveur
uvicorn app.main:app --reload

# 3. Ouvrir Swagger
# http://127.0.0.1:8000/docs
```

### Scénario Complet

#### Étape 1 : Lister les Planifications Existantes

**Endpoint** : `GET /api/planifications`

**Paramètres** :
- `session_id`: 1

**Résultat** : Liste vide (si première utilisation)

#### Étape 2 : Générer Automatiquement

**Endpoint** : `POST /api/sessions/1/generer`

**Body** : Utiliser l'exemple complet ci-dessus avec les 13 matières IGL4

**Résultat** : 13 planifications créées, 0 conflit

#### Étape 3 : Récupérer l'Emploi du Temps

**Endpoint** : `GET /api/sessions/1/emploi-du-temps`

**Paramètres** :
- `section_id`: 1

**Résultat** : Emploi du temps complet sur 8 jours

#### Étape 4 : Modifier une Planification

**Endpoint** : `PUT /api/planifications/1`

**Body** :
```json
{
  "date_examen": "2026-01-08"
}
```

**Résultat** : Planification mise à jour

#### Étape 5 : Valider Toutes les Planifications

**Endpoint** : `POST /api/planifications/{id}/valider`

Répéter pour chaque ID (1 à 13)

**Résultat** : Toutes les planifications passent en statut VALIDEE

---

## 🔍 Codes de Réponse

| Code | Signification | Exemple |
|------|---------------|---------|
| 200 | OK | Requête réussie |
| 201 | Created | Planification créée |
| 204 | No Content | Suppression réussie |
| 400 | Bad Request | Données invalides |
| 404 | Not Found | Planification introuvable |
| 409 | Conflict | Contrainte violée (ex: salle occupée) |
| 422 | Unprocessable Entity | Validation Pydantic échouée |
| 500 | Internal Server Error | Erreur serveur |

---

## 🧪 Tests Automatisés avec Swagger

### Test 1 : Health Check

**Endpoint** : `GET /health`

**Résultat Attendu** :
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2026-01-07T10:30:00"
}
```

### Test 2 : Génération Simple

1. Charger les données IGL4
2. Générer avec 2 matières
3. Vérifier : `nb_crees = 2`, `nb_conflits = 0`

### Test 3 : Gestion des Conflits

1. Générer avec peu de créneaux
2. Vérifier : `nb_conflits > 0`
3. Lire les messages de conflit

---

## 📞 Support

- **Documentation API** : [`API_PLANIFICATION.md`](API_PLANIFICATION.md)
- **Guide Frontend** : [`GUIDE_P3_FRONTEND.md`](GUIDE_P3_FRONTEND.md)
- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

---

**📖 Testez facilement avec Swagger !**
