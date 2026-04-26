# 📡 API Planification - Documentation Complète

## 📋 Vue d'Ensemble

Cette API permet de gérer la planification automatique des examens.

**Base URL** : `http://127.0.0.1:8000/api`

**Format** : JSON

**Authentication** : Aucune (à implémenter en production)

---

## 🎯 Endpoints Disponibles

### 1. Lister les Planifications

**GET** `/planifications`

Liste toutes les planifications avec filtres optionnels.

#### Paramètres Query (optionnels)

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `session_id` | integer | Filtrer par session | `?session_id=1` |
| `section_id` | integer | Filtrer par section | `?section_id=1` |
| `type_epreuve` | string | Filtrer par type | `?type_epreuve=EXAMEN_FINAL` |
| `statut` | string | Filtrer par statut | `?statut=BROUILLON` |
| `skip` | integer | Pagination (offset) | `?skip=0` |
| `limit` | integer | Pagination (limite) | `?limit=100` |

#### Exemple de Requête

```bash
curl -X GET "http://127.0.0.1:8000/api/planifications?session_id=1&type_epreuve=EXAMEN_FINAL" \
  -H "Accept: application/json"
```

#### Réponse Attendue (200 OK)

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
    ],
    "matiere": {
      "id": 10,
      "code": "IGL4-ML-DL",
      "intitule": "Machine Learning & Deep Learning",
      "coefficient": 2.5,
      "credit": 3
    },
    "section": {
      "id": 1,
      "nom": "IGL4",
      "nb_etudiants": 53
    }
  }
]
```

---

### 2. Récupérer une Planification

**GET** `/planifications/{id}`

Récupère les détails d'une planification spécifique.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | integer | ID de la planification |

#### Exemple de Requête

```bash
curl -X GET "http://127.0.0.1:8000/api/planifications/1" \
  -H "Accept: application/json"
```

#### Réponse Attendue (200 OK)

```json
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
  "salles": [...],
  "matiere": {...},
  "section": {...}
}
```

#### Erreurs Possibles

- **404 Not Found** : Planification introuvable

```json
{
  "detail": "Planification not found"
}
```

---

### 3. Créer une Planification Manuelle

**POST** `/planifications`

Crée une planification manuellement (sans l'algorithme).

#### Body (JSON)

```json
{
  "session_id": 1,
  "section_id": 1,
  "section_matiere_id": 10,
  "type_epreuve": "EXAMEN_FINAL",
  "date_examen": "2026-01-07",
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

#### Exemple de Requête

```bash
curl -X POST "http://127.0.0.1:8000/api/planifications" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "session_id": 1,
    "section_id": 1,
    "section_matiere_id": 10,
    "type_epreuve": "EXAMEN_FINAL",
    "date_examen": "2026-01-07",
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
  }'
```

#### Réponse Attendue (201 Created)

```json
{
  "id": 15,
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
  "salles": [...]
}
```

#### Erreurs Possibles

- **409 Conflict** : Contrainte violée (ex: salle déjà occupée)
- **422 Unprocessable Entity** : Données invalides

---

### 4. Mettre à Jour une Planification

**PUT** `/planifications/{id}`

Met à jour une planification existante.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | integer | ID de la planification |

#### Body (JSON)

```json
{
  "date_examen": "2026-01-08",
  "heure_debut": "11:00:00",
  "heure_fin": "13:00:00",
  "salles": [
    {
      "salle_id": "S30A",
      "groupe_numero": 1,
      "groupe_effectif": 53
    }
  ]
}
```

#### Exemple de Requête

```bash
curl -X PUT "http://127.0.0.1:8000/api/planifications/1" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "date_examen": "2026-01-08",
    "heure_debut": "11:00:00",
    "heure_fin": "13:00:00"
  }'
```

#### Réponse Attendue (200 OK)

```json
{
  "id": 1,
  "date_examen": "2026-01-08",
  "heure_debut": "11:00:00",
  "heure_fin": "13:00:00",
  ...
}
```

---

### 5. Supprimer une Planification

**DELETE** `/planifications/{id}`

Supprime une planification.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | integer | ID de la planification |

#### Exemple de Requête

```bash
curl -X DELETE "http://127.0.0.1:8000/api/planifications/1" \
  -H "Accept: application/json"
```

#### Réponse Attendue (204 No Content)

Pas de contenu dans la réponse.

#### Erreurs Possibles

- **404 Not Found** : Planification introuvable
- **409 Conflict** : Planification déjà publiée (non supprimable)

---

### 6. Générer Automatiquement (⭐ PRINCIPAL)

**POST** `/sessions/{session_id}/generer`

Génère automatiquement les planifications pour une session.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `session_id` | integer | ID de la session |

#### Body (JSON)

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
    }
  ],
  "creneaux": [
    {
      "date_examen": "2026-01-07",
      "heure_debut": "08:30:00",
      "heure_fin": "10:30:00"
    }
  ],
  "salles": [
    {
      "salle_id": "AMPHI-INFO",
      "capacite": 150,
      "batiment": "Info"
    }
  ]
}
```

#### Exemple de Requête

```bash
curl -X POST "http://127.0.0.1:8000/api/sessions/1/generer" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d @generation_request.json
```

#### Réponse Attendue (200 OK)

```json
{
  "nb_crees": 13,
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
    }
  ]
}
```

#### Réponse avec Conflits (200 OK)

```json
{
  "nb_crees": 10,
  "nb_conflits": 3,
  "conflits": [
    "[C12] Section-1 / Optimisation Combinatoire - Subject already planned",
    "[C1] Section-2 / Physique - No available room",
    "[C7] Section-3 / Mathématiques - Section already has exam at this time"
  ],
  "planifications": [...]
}
```

---

### 7. Récupérer l'Emploi du Temps

**GET** `/sessions/{session_id}/emploi-du-temps`

Récupère l'emploi du temps complet d'une session.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `session_id` | integer | ID de la session |

#### Paramètres Query (optionnels)

| Paramètre | Type | Description |
|-----------|------|-------------|
| `section_id` | integer | Filtrer par section |
| `type_epreuve` | string | Filtrer par type |

#### Exemple de Requête

```bash
curl -X GET "http://127.0.0.1:8000/api/sessions/1/emploi-du-temps?section_id=1" \
  -H "Accept: application/json"
```

#### Réponse Attendue (200 OK)

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
      }
    ]
  }
]
```

---

### 8. Valider une Planification

**POST** `/planifications/{id}/valider`

Change le statut d'une planification de BROUILLON à VALIDEE.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | integer | ID de la planification |

#### Exemple de Requête

```bash
curl -X POST "http://127.0.0.1:8000/api/planifications/1/valider" \
  -H "Accept: application/json"
```

#### Réponse Attendue (200 OK)

```json
{
  "id": 1,
  "statut": "VALIDEE",
  "date_validation": "2026-01-07T10:30:00",
  ...
}
```

---

### 9. Publier une Planification

**POST** `/planifications/{id}/publier`

Change le statut d'une planification de VALIDEE à PUBLIEE.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | integer | ID de la planification |

#### Exemple de Requête

```bash
curl -X POST "http://127.0.0.1:8000/api/planifications/1/publier" \
  -H "Accept: application/json"
```

#### Réponse Attendue (200 OK)

```json
{
  "id": 1,
  "statut": "PUBLIEE",
  "date_publication": "2026-01-07T11:00:00",
  ...
}
```

---

### 10. Affecter des Salles

**POST** `/planifications/{id}/salles`

Affecte ou modifie les salles d'une planification.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | integer | ID de la planification |

#### Body (JSON)

```json
{
  "salles": [
    {
      "salle_id": "S30A",
      "groupe_numero": 1,
      "groupe_effectif": 27
    },
    {
      "salle_id": "S30B",
      "groupe_numero": 2,
      "groupe_effectif": 26
    }
  ]
}
```

#### Exemple de Requête

```bash
curl -X POST "http://127.0.0.1:8000/api/planifications/1/salles" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "salles": [
      {"salle_id": "S30A", "groupe_numero": 1, "groupe_effectif": 27},
      {"salle_id": "S30B", "groupe_numero": 2, "groupe_effectif": 26}
    ]
  }'
```

#### Réponse Attendue (200 OK)

```json
{
  "id": 1,
  "nb_groupes": 2,
  "salles": [
    {
      "salle_id": "S30A",
      "groupe_numero": 1,
      "groupe_effectif": 27
    },
    {
      "salle_id": "S30B",
      "groupe_numero": 2,
      "groupe_effectif": 26
    }
  ]
}
```

---

## 📊 Codes de Statut HTTP

| Code | Signification | Quand |
|------|---------------|-------|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée |
| 204 | No Content | Suppression réussie |
| 400 | Bad Request | Données invalides |
| 404 | Not Found | Ressource introuvable |
| 409 | Conflict | Contrainte violée |
| 422 | Unprocessable Entity | Validation échouée |
| 500 | Internal Server Error | Erreur serveur |

---

## 🔧 Modèles de Données

### Planification

```typescript
interface Planification {
  id: number;
  session_id: number;
  section_id: number;
  section_matiere_id: number;
  type_epreuve: "EXAMEN_FINAL" | "DS" | "RATTRAPAGE";
  date_examen: string; // Format: YYYY-MM-DD
  heure_debut: string; // Format: HH:MM:SS
  heure_fin: string; // Format: HH:MM:SS
  duree: number; // En minutes
  statut: "BROUILLON" | "VALIDEE" | "PUBLIEE";
  nb_groupes: number;
  salles: PlanifSalle[];
  matiere?: Matiere;
  section?: Section;
}
```

### PlanifSalle

```typescript
interface PlanifSalle {
  id: number;
  planification_id: number;
  salle_id: string;
  salle_code: string;
  salle_designation: string;
  salle_capacite: number;
  groupe_numero: number;
  groupe_effectif: number;
}
```

### GenerationRequest

```typescript
interface GenerationRequest {
  session_id: number;
  session_date_debut: string;
  session_date_fin: string;
  session_statut: string;
  mode: "AUTO" | "MANUAL";
  tasks: Task[];
  creneaux: Creneau[];
  salles: Salle[];
}
```

---

## 🧪 Exemples d'Utilisation

### Scénario 1 : Génération Complète

```bash
# 1. Générer automatiquement
curl -X POST "http://127.0.0.1:8000/api/sessions/1/generer" \
  -H "Content-Type: application/json" \
  -d @generation_data.json

# 2. Récupérer l'emploi du temps
curl "http://127.0.0.1:8000/api/sessions/1/emploi-du-temps" | jq

# 3. Valider toutes les planifications
for id in {1..13}; do
  curl -X POST "http://127.0.0.1:8000/api/planifications/$id/valider"
done

# 4. Publier
for id in {1..13}; do
  curl -X POST "http://127.0.0.1:8000/api/planifications/$id/publier"
done
```

### Scénario 2 : Modification Manuelle

```bash
# 1. Lister les planifications
curl "http://127.0.0.1:8000/api/planifications?session_id=1"

# 2. Modifier une planification
curl -X PUT "http://127.0.0.1:8000/api/planifications/5" \
  -H "Content-Type: application/json" \
  -d '{"date_examen": "2026-01-08"}'

# 3. Changer les salles
curl -X POST "http://127.0.0.1:8000/api/planifications/5/salles" \
  -H "Content-Type: application/json" \
  -d '{"salles": [{"salle_id": "AMPHI-INFO", "groupe_numero": 1, "groupe_effectif": 53}]}'
```

---

## 📞 Support

- **Documentation Swagger** : http://127.0.0.1:8000/docs
- **Documentation ReDoc** : http://127.0.0.1:8000/redoc
- **Health Check** : http://127.0.0.1:8000/health

---

**📡 API complète et documentée !**
