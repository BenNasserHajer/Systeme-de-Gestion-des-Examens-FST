# API Planification Examens

## Base URL

- API prefix: `http://127.0.0.1:8000/api`
- Swagger: `http://127.0.0.1:8000/docs`

## Endpoints principaux

### 1) Lister les planifications

- `GET /planifications`
- Alias legacy (deprecated): `GET /planification_examen`

Query params:
- `session_id` (int, optionnel)
- `section_id` (int, optionnel)
- `date_examen` (YYYY-MM-DD, optionnel)
- `type_epreuve` (`EXAMEN_FINAL` | `DS`, optionnel)
- `statut` (`BROUILLON` | `VALIDEE` | `PUBLIEE`, optionnel)
- `skip` (int >= 0, optionnel)
- `limit` (int 1..200, optionnel)

Exemple:

```bash
curl "http://127.0.0.1:8000/api/planifications?session_id=1&type_epreuve=EXAMEN_FINAL&statut=BROUILLON"
```

### 2) Détail d'une planification

- `GET /planifications/{planif_id}`
- Alias legacy (deprecated): `GET /planification_examen/{planif_id}`

### 3) Créer une planification manuelle

- `POST /planifications`
- Alias legacy (deprecated): `POST /planification_examen`

Body minimal valide (exemple):

```json
{
  "session_id": 1,
  "section_id": 1,
  "section_matiere_id": 10,
  "matiere": "Algorithmique",
  "type_epreuve": "EXAMEN_FINAL",
  "mode_affectation": "MANUEL",
  "statut": "BROUILLON",
  "date_examen": "2026-06-08",
  "heure_debut": "08:30:00",
  "heure_fin": "10:30:00",
  "session_date_debut": "2026-06-01",
  "session_date_fin": "2026-06-20",
  "session_statut": "BROUILLON",
  "duree": 120,
  "coefficient": 2,
  "section_nb_etudiants": 45,
  "nb_groupes": 1,
  "nb_surveillants_requis": 2,
  "a_examen_final": true,
  "a_ds": true,
  "salles": [
    {
      "salle_id": "A1",
      "salle_capacite": 60,
      "salle_batiment": "Bloc A",
      "groupe_id": 1,
      "groupe_effectif": 45
    }
  ]
}
```

### 4) Mettre à jour

- `PUT /planifications/{planif_id}`
- Alias legacy (deprecated): `PUT /planification_examen/{planif_id}`

### 5) Supprimer

- `DELETE /planifications/{planif_id}`
- Alias legacy (deprecated): `DELETE /planification_examen/{planif_id}`

### 6) Générer automatiquement

- `POST /sessions/{session_id}/generer`
- Alias legacy (deprecated): `POST /sessions/{session_id}/planification_examen/generer`

Body: `GenerationRequest`

Réponse:

```json
{
  "nb_crees": 10,
  "nb_conflits": 0,
  "conflits": []
}
```

### 7) Emploi du temps d'une session

- `GET /sessions/{session_id}/emploi-du-temps`
- Alias legacy (deprecated): `GET /sessions/{session_id}/planification_examen/emploi-du-temps`

Query params optionnels:
- `section_id`
- `type_epreuve`
- `statut`

### 8) Affectation manuelle des salles

- `POST /planifications/{planif_id}/salles`
- Alias legacy (deprecated): `POST /planification_examen/{planif_id}/salles`

Body attendu: **liste JSON** de `PlanifSalleAssign` (pas un objet enveloppe)

```json
[
  {
    "salle_id": "A1",
    "salle_capacite": 60,
    "salle_batiment": "Bloc A",
    "groupe_id": 1,
    "groupe_effectif": 30
  },
  {
    "salle_id": "A2",
    "salle_capacite": 40,
    "salle_batiment": "Bloc A",
    "groupe_id": 2,
    "groupe_effectif": 15
  }
]
```

### 9) Changement de statut

- `POST /planifications/{planif_id}/valider`
- `POST /planifications/{planif_id}/publier`
- Alias legacy (deprecated):
  - `POST /planification_examen/{planif_id}/valider`
  - `POST /planification_examen/{planif_id}/publier`

## Codes HTTP

- `200` OK
- `201` Created
- `204` No Content
- `404` Not Found
- `409` Conflict
- `422` Validation error

## Références techniques

- Router: `app/routers/planifications.py`
- Schémas: `app/schemas/planification.py`
- Service: `app/services/planif_service.py`
- CRUD: `app/crud/crud_planif.py`
