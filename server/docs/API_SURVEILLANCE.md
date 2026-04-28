# Documentation du Module Surveillance

## Vue d'Ensemble

Le module Surveillance gère complètement l'affectation des surveillants aux examens selon des règles métier strictes et deux modes d'affectation: **Automatique** et **Manuel Total**.

## Architecture

```
app/
├── models/
│   └── surveillance.py           # Modèle ORM Surveillance
├── schemas/
│   └── surveillance_schema.py    # Schemas Pydantic pour validations
├── crud/
│   └── crud_surv.py              # Opérations CRUD de bas niveau
├── services/
│   └── surv_service.py           # Logique métier (couche service)
├── algorithms/
│   └── surv_auto.py              # Algorithme d'affectation automatique
└── routers/
    └── surveillances.py          # Endpoints FastAPI
```

## Modèle de Base de Données

### Table `surveillance`

```sql
CREATE TABLE surveillance (
    id                   SERIAL PRIMARY KEY,
    planification_id     INTEGER             NOT NULL REFERENCES planification_examen(id),
    enseignant_id        INTEGER             NOT NULL REFERENCES enseignant(id),
    est_externe          BOOLEAN             NOT NULL DEFAULT FALSE,
    motif_externe        VARCHAR(200),
    charge               NUMERIC(4,2)        DEFAULT 1.0,
    presence             BOOLEAN             DEFAULT FALSE,
    mode_affectation     mode_affectation    NOT NULL DEFAULT 'AUTOMATIQUE',
    statut_surveillance  statut_surveillance DEFAULT 'AFFECTE',
    created_at           TIMESTAMP DEFAULT NOW(),
    updated_at           TIMESTAMP DEFAULT NOW(),
    UNIQUE (planification_id, enseignant_id)
);
```

**Champs clés:**
- `est_externe`: Indique si l'enseignant est d'un autre département
- `motif_externe`: Raison du recours à un enseignant externe (ex: "Manque de personnel")
- `charge`: Heures imputées à l'enseignant
- `mode_affectation`: AUTOMATIQUE ou MANUELLE
- `statut_surveillance`: AFFECTE ou CONFIRME

## 5 Contraintes d'Affectation

### 1. Disponibilité Temporelle (HARD - Toujours)

L'enseignant doit être disponible sur le créneau. Toute indisponibilité (INDISPONIBLE, COURS_PREVU, MISSION, CONGE) qui chevauche exclut l'enseignant.

```python
# Vérification
if not service._check_disponibilite_temporelle(enseignant_id, planif):
    # Exclusion
```

### 2. Conflit de Matière (SOFT en Auto, Ignorée en Manuel)

**Mode Automatique**: L'enseignant ne peut pas surveiller sa propre matière (COURS ou TD). Contrainte souple: peut être levée en dernier recours.

**Mode Manuel**: Jamais vérifiée.

```python
a_conflit = service._check_conflit_matiere(enseignant_id, planif)
```

### 3. Volume Horaire (HARD en Auto, Ignorée en Manuel)

**Mode Automatique**: Respecter la tolérance ±0.05%

```
tolerance = volume_horaire × 0.0005
volume_max = volume_horaire + tolerance
volume_restant = volume_horaire - SUM(charge AFFECTE/CONFIRME)

Si volume_restant < -tolerance → EXCLU
```

**Mode Manuel**: Jamais vérifiée (mais avertissement affiché).

### 4. Non-Simultanéité (HARD - Toujours)

L'enseignant ne peut pas surveiller deux examens en même temps (même créneau).

```python
if service._check_conflit_simultaneite(enseignant_id, planif):
    # Exclusion
```

### 5. Département (HARD en Auto, Ignorée en Manuel)

**Mode Automatique**: Seul les enseignants du même département sont affectés.

**Mode Manuel**: Tous les départements autorisés, mais avec flag `est_externe=TRUE` et motif requis.

```python
est_externe = ens.departement_id != planif.departement_id
```

## Algorithme d'Affectation Automatique

### Flux Complet

```
POST /surveillances/affecter-session
├─ Récupérer toutes planifications VALIDEE de la session
├─ Récupérer l'année universitaire de la session
└─ BOUCLE: Pour chaque planification (ordre chronologique)
    ├─ Étape 1: Calculer volume restant pour chaque enseignant
    │   (uniquement année universitaire de la session)
    ├─ Étape 2: Filtrer selon 5 contraintes
    │   ├─ Exclure indisponibles (Contrainte 1)
    │   ├─ Exclure conflits simulta néité (Contrainte 4)
    │   ├─ Exclure volume épuisé (Contrainte 3)
    │   └─ Marquer conflits matière (Contrainte 2)
    ├─ Étape 3: Trier candidats
    │   ├─ Priorité 1: Sans conflit matière
    │   └─ Priorité 2: Avec conflit (dernier recours)
    ├─ Étape 4: Sélectionner surveillants
    │   └─ Insérer immédiatement en BD
    └─ Étape 5: Décider statut
        ├─ Si complet → AFFECTEE
        └─ Si manquants → CONFLIT
```

### Classe `AutomaticAffectationAlgorithm`

**Localistion**: `app/algorithms/surv_auto.py`

**Méthodes principales**:

- `affecter_session(session_id)` → Entrée principale
- `_affecter_planification(planif, annee_univ)` → Traiter une planification
- `_get_enseignants_departement(dept_id)` → Récupérer candidats
- `_get_charge_consumed(ens_id, year)` → Calculer charge consommée
- `_check_disponibilite_temporelle()` → Vérifier Contrainte 1
- `_check_conflit_simultaneite()` → Vérifier Contrainte 4
- `_check_conflit_matiere()` → Vérifier Contrainte 2
- `_creer_surveillance()` → Persister en BD

## Couche Service

**Localisation**: `app/services/surv_service.py`

La classe `SurvService` expose:

### Consultation

```python
get_all_surveillances()
get_surveillance_by_id()
get_surveillances_for_planification()
get_surveillances_for_enseignant()
```

### Affectation Automatique

```python
affecter_session_automatique(session_id)
```

### Affectation Manuelle

```python
# Conflits (une planification)
affecter_planification_manuellement(request: ManualAssignmentRequest)

# Mode manuel total (session entière)
affecter_session_manuellement(request: ManualAssignmentBatchRequest)
```

### Gestion

```python
create_surveillance()
update_surveillance()
delete_surveillance()
replace_surveillance()
```

### Analytics

```python
get_volume_restant_enseignant()
get_enseignants_disponibles_pour_planification()
```

## CRUD

**Localisation**: `app/crud/crud_surv.py`

Opérations de base de données:

```python
# Listing
list_surveillances()
get_surveillance()
get_surveillances_for_planification()
get_surveillances_for_enseignant()
get_surveillance_by_planif_and_enseignant()

# Création
create_surveillance()
create_surveillances_batch()

# Mise à jour
update_surveillance()

# Suppression
delete_surveillance()
delete_surveillance_by_id()
delete_surveillances_for_planification()

# Remplacement
replace_surveillance()

# Analytics
get_surveillance_stats_for_session()
get_enseignant_charge_for_year()
count_surveillances_for_enseignant()
```

## Endpoints API

### Affectation Automatique

**POST /surveillances/affecter-session**

```json
{
  "session_id": 1
}
```

**Réponse** (HTTP 200):
```json
{
  "session_id": 1,
  "total_planifications": 20,
  "affectees_automatiquement": 17,
  "en_conflit": 3,
  "message": "...",
  "resultats": [
    {
      "planification_id": 5,
      "statut": "AFFECTEE",
      "surveillants_requis": 2,
      "surveillants_affectes": 2,
      "manquants": 0,
      "raisons_exclusion": []
    },
    {
      "planification_id": 8,
      "statut": "CONFLIT",
      "surveillants_requis": 2,
      "surveillants_affectes": 1,
      "manquants": 1,
      "raisons_exclusion": [
        {
          "enseignant_id": 22,
          "nom": "Abed",
          "prenom": "Rahma",
          "raison": "INDISPONIBLE"
        }
      ]
    }
  ]
}
```

### Affectation Manuelle (Conflit Simple)

**POST /surveillances/manual-assignment**

```json
{
  "session_id": 1,
  "planification_id": 8,
  "enseignant_ids": [55, 23],
  "motifs_externes": {
    "55": null,
    "23": "Manque de personnel DSI"
  }
}
```

**Réponse** (HTTP 200):
```json
{
  "planification_id": 8,
  "statut": "CONFLIT_RESOLU",
  "surveillants_inseres": 2
}
```

**Erreur** (HTTP 409):
```json
{
  "planification_id": 8,
  "erreur": "Validation échouée",
  "details": [
    {"enseignant_id": 55, "raison": "INDISPONIBLE"}
  ]
}
```

### Affectation Manuelle (Mode Total)

**POST /surveillances/manual-assignment-batch**

```json
{
  "session_id": 1,
  "affectations": {
    "5": [12, 34],
    "8": [55, 23],
    "10": [42]
  },
  "motifs_externes": {
    "55": null,
    "23": "Manque de personnel DSI",
    "42": "Expert externe"
  }
}
```

**Réponse** (HTTP 200):
```json
{
  "session_id": 1,
  "statut": "SUCCES",
  "total_surveillances_inserees": 5
}
```

### Consultation

**GET /surveillances/{session_id}**

Récupérer toutes les surveillances d'une session.

**GET /surveillances/getallsurveillants**

Récupérer tous les enseignants disponibles (pagination).

**GET /surveillances/disponibles/{planif_id}**

Récupérer les enseignants disponibles pour une planification.

### Gestion

**PATCH /surveillances/{surveillance_id}**

Mettre à jour une surveillance.

**POST /surveillances/{surveillance_id}/remplacer**

Remplacer un enseignant.

**DELETE /surveillances/{surveillance_id}**

Supprimer une surveillance (suppression physique).

## Schemas Pydantic

**Localisation**: `app/schemas/surveillance_schema.py`

Schemas principaux:

```python
SurveillanceCreate
SurveillanceUpdate
SurveillanceOut
ManualAssignmentRequest
ManualAssignmentBatchRequest
RemplacementRequest
EnseignantDisponible
...
```

## Règles Métier

1. **Volume Annuel**: Calculé uniquement sur l'année universitaire de la session
2. **Suppression Physique**: Annulation = suppression BD (pas de soft delete)
3. **Persistance Immédiate**: Chaque affectation auto est persisted avant la suivante
4. **Non-Blocage**: Un conflit n'arrête pas le traitement des suivants
5. **Transaction par Planification (Auto)**: Succès/échecs indépendants
6. **Transaction Globale (Manuel Batch)**: Tout ou rien
7. **Tri Chronologique**: Garantit cohérence volume inter-planifications
8. **Traçabilité Externe**: Flags `est_externe` + `motif_externe`

## Exemple d'Utilisation

### Mode Automatique

```python
from app.services.surv_service import SurvService
from sqlalchemy.orm import Session

def affecter_automatique(session_id: int, db: Session):
    service = SurvService(db)
    results, message = service.affecter_session_automatique(session_id)
    
    for r in results:
        if r.statut == "AFFECTEE":
            print(f"✓ Planif {r.planification_id}: {len(r.surveillants_affectes)} affectés")
        else:
            print(f"✗ Planif {r.planification_id}: {r.manquants} manquants")
            for v in r.violations:
                print(f"  - {v.nom}: {v.raison.value}")
```

### Mode Manuel (Conflit)

```python
from app.schemas.surveillance_schema import ManualAssignmentRequest

request = ManualAssignmentRequest(
    session_id=1,
    planification_id=8,
    enseignant_ids=[55, 23],
    motifs_externes={
        "55": None,
        "23": "Manque de personnel DSI"
    }
)

result = service.affecter_planification_manuellement(request)
print(f"✓ Conflit résolu: {result['surveillants_inseres']} enseignants affectés")
```

### Mode Manuel Total

```python
from app.schemas.surveillance_schema import ManualAssignmentBatchRequest

request = ManualAssignmentBatchRequest(
    session_id=1,
    affectations={
        "5": [12, 34],
        "8": [55, 23],
        "10": [42]
    },
    motifs_externes={
        "23": "Manque de personnel DSI"
    }
)

result = service.affecter_session_manuellement(request)
print(f"✓ Session affectée: {result['total_surveillances_inserees']} surveillances")
```

## Tests

Tests unitaires et d'intégration recommandés:

1. **Test algorithme automatique**: Vérifier tous les cas de conflit
2. **Test contraintes**: Chacune des 5 contraintes
3. **Test tolérances**: ±0.05% volume
4. **Test non-blocage**: Conflits n'arrêtent pas suite
5. **Test transactions**: Tout ou rien par mode
6. **Test externes**: Flags est_externe correctement positionnés
7. **Test volumes annuels**: Calculés correctement par année

## Performance

- **Indexation**: `idx_surv_planif`, `idx_surv_ens`, `idx_surv_externe`
- **Pagination**: Endpoints de listing supportent pagination
- **Batch**: Opérations batch pour multiples insertions
- **Requêtes optimisées**: Joins et selects minimisés

## Sécurité

- Validation Pydantic obligatoire
- Contrainte 1 (disponibilité) toujours vérifiée
- Contrainte 4 (non-simultanéité) toujours vérifiée
- Tolérance volume limitée ±0.05%
- Suppression physique (pas de données fantômes)
