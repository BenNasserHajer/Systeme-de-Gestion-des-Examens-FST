# 📊 Sessions dans les Endpoints de Planification et Surveillance

## 🎯 Vue d'Ensemble

Les sessions (S1, S2) sont utilisées par les endpoints de **planification** et **surveillance** pour:
1. Délimiter la période des examens
2. Filtrer les créneaux disponibles
3. Valider les dates d'examen
4. Affecter automatiquement les surveillants

---

## 1️⃣ Planification - Création d'un Examen

### 📌 Endpoint

**POST** `/api/planifications/`

### 💾 Payload

```json
{
  \"session_id\": 1,
  \"section_id\": 5,
  \"section_matiere_id\": 42,
  \"matiere\": \"Mathématiques\",
  \"semestre\": \"S1\",
  \"type_epreuve\": \"EXAMEN_FINAL\",
  \"date_examen\": \"2026-01-10\",
  \"heure_debut\": \"08:30\",
  \"heure_fin\": \"10:30\",
  \"duree\": 120,
  \"coefficient\": 2.0,
  \"statut\": \"BROUILLON\"
}
```

### 🔍 Validation (Backend)

**Fichier**: [server/app/routers/planifications.py](server/app/routers/planifications.py#L121)

```python
# Validation: date_examen DOIT être dans la période de la session
if not (session.date_debut <= exam_date <= session.date_fin):
    raise ApiError(
        f\"La date {data.date} doit etre entre {session.date_debut} et {session.date_fin}.\"
    )
```

### 📊 Résultat

```json
{
  \"id\": 123,
  \"session_id\": 1,
  \"matiere\": \"Mathématiques\",
  \"date_examen\": \"2026-01-10\",
  \"heure_debut\": \"08:30\",
  \"heure_fin\": \"10:30\",
  \"statut\": \"BROUILLON\"
}
```

---

## 2️⃣ Planification - Génération Automatique

### 📌 Endpoint

**POST** `/api/planifications/generate`

### 💾 Payload

```json
{
  \"session_id\": 1,
  \"scope_section_ids\": [5, 6, 7],
  \"type_epreuve\": \"EXAMEN_FINAL\",
  \"semestre\": \"S1\",
  \"mode\": \"AUTO\"
}
```

### 🔧 Logique (Backend)

**Fichier**: [server/app/services/planif_service.py](server/app/services/planif_service.py#L113-L140)

```python
def _resolve_session_context(self, request: GenerationRequest) -> GenerationRequest:
    \"\"\"Charge les infos de session pour valider et remplir le contexte.\"\"\"
    
    # 1. Récupérer la session depuis la BDD
    row = self.db.execute(
        text(
            \"\"\"
            SELECT id, annee_universitaire, date_debut, date_fin, statut
            FROM session
            WHERE id = :session_id
            \"\"\"
        ),
        {\"session_id\": request.session_id},
    ).mappings().first()
    
    if row is None:
        raise ConstraintViolationError(
            f\"[C16] session {request.session_id} introuvable\"
        )
    
    # 2. Vérifier que la session n'est pas publiée
    statut = str(row[\"statut\"]).upper()
    if statut not in {\"BROUILLON\", \"VALIDEE\"}:
        raise ConstraintViolationError(
            \"[C17] session publiee, generation impossible\"
        )
    
    # 3. Enrichir la requête avec les infos de session
    return request.model_copy(
        update={
            \"annee_universitaire\": row.get(\"annee_universitaire\"),
            \"session_date_debut\": row.get(\"date_debut\"),
            \"session_date_fin\": row.get(\"date_fin\"),
            \"session_statut\": statut,
        }
    )
```

### 🎯 Algorithme de Génération

```
1. Charger session (date_debut, date_fin)
2. Pour chaque matière:
   a. Déterminer la durée et nombre de groupes
   b. Chercher des créneaux libres dans [date_debut, date_fin]
   c. Affecter les salles
   d. Créer les planifications
3. Retourner le résultat (ex: 42 planifications générées)
```

**Fichier**: [server/app/algorithms/planif_auto.py](server/app/algorithms/planif_auto.py)

```python
def generate_for_section(
    section_id: int,
    session_date_debut: date,
    session_date_fin: date,
    # ... autres params
) -> list[PlanificationGeneration]:
    \"\"\"Génère les planifications pour une section dans la période donnée.\"\"\"
    
    # Charger tous les créneaux disponibles
    all_creneaux = db.query(Creneau).order_by(Creneau.date).all()
    
    # Filtrer les créneaux dans la période de session
    creneaux_session = [
        c for c in all_creneaux
        if session_date_debut <= c.date <= session_date_fin
    ]
    
    # Utiliser ces créneaux pour assigner les examens
    # ...
```

---

## 3️⃣ Surveillance - Affectation Automatique

### 📌 Endpoint

**POST** `/api/surveillances/affecter-session`

### 💾 Payload

```json
{
  \"session_id\": 1,
  \"section_nom\": \"INF-L3\",
  \"periode\": \"2025/2026-S1\",
  \"type_epreuve\": \"EXAMEN_FINAL\",
  \"save\": true
}
```

### 🔧 Logique (Backend)

**Fichier**: [server/app/routers/surveillances.py](server/app/routers/surveillances.py#L274-L320)

```python
@router.post(\"/affecter-session\", response_model=AffecterSessionResponse)
def affecter_session_automatique(
    payload: AffecterSessionRequest,
    db: Session = Depends(get_db),
):
    \"\"\"
    Lance l'algorithme d'affectation automatique des surveillants pour une session.
    \"\"\"
    
    try:
        # 1. Appeler le service d'affectation
        results, msg = surv_service.affecter_session_automatique(
            session_id=payload.session_id,
            section_nom=payload.section_nom,
            periode=payload.periode,
            type_epreuve=payload.type_epreuve,
            dry_run=not payload.save,  # Si save=False, simulation seulement
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 2. Récupérer les détails de la session
    session_orm = db.query(SessionModel).filter(
        SessionModel.id == payload.session_id
    ).first()
    
    # 3. Construire la réponse
    return AffecterSessionResponse(
        session=SessionOut(
            id=session_orm.id,
            type_session=session_orm.type_session,
            annee_universitaire=session_orm.annee_universitaire,
            date_debut=str(session_orm.date_debut),
            date_fin=str(session_orm.date_fin),
            statut=session_orm.statut,
        ),
        total_planifications=len(results),
        affectees_automatiquement=len([r for r in results if r.statut == \"OK\"]),
        # ...
    )
```

### 📊 Résultat

```json
{
  \"session\": {
    \"id\": 1,
    \"type_session\": \"PRINCIPALE\",
    \"annee_universitaire\": \"2025/2026\",
    \"date_debut\": \"2026-01-07\",
    \"date_fin\": \"2026-01-15\",
    \"statut\": \"VALIDEE\"
  },
  \"total_planifications\": 42,
  \"affectees_automatiquement\": 40,
  \"affectees_manuellement\": 2,
  \"manquantes\": 0,
  \"detailles\": [
    {
      \"planification_id\": 123,
      \"matiere\": \"Mathématiques\",
      \"date_examen\": \"2026-01-10\",
      \"heure_debut\": \"08:30\",
      \"statut\": \"OK\",
      \"surveillants_requis\": 2,
      \"surveillants_affectes\": 2,
      \"surveillants\": [
        {\"id\": 5, \"nom\": \"Dupont\", \"prenom\": \"Jean\"},
        {\"id\": 7, \"nom\": \"Martin\", \"prenom\": \"Marie\"}
      ]
    },
    // ... autres planifications
  ]
}
```

---

## 4️⃣ Flux Complet: De la Session aux Surveillances

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CRÉATION DE SESSION (S1)                         │
│  - Type: PRINCIPALE                                                 │
│  - Année: 2025/2026                                                 │
│  - Période: 7 janvier → 15 janvier 2026                             │
│  - Créneaux: 24 slots (08:30, 11:00, 14:00 × 8 jours)              │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│             GÉNÉRATION DE PLANIFICATIONS (P1-P42)                   │
│  - Récupérer session → date_debut, date_fin                        │
│  - Filtrer créneaux dans [7-15 jan]                                │
│  - Pour chaque matière:                                            │
│    • Chercher créneaux libres                                      │
│    • Assigner dates/salles/groupes                                 │
│  - Résultat: 42 planifications (exams + salles)                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│           AFFECTATION AUTOMATIQUE SURVEILLANTS (A1-A84)             │
│  - Récupérer session → date_debut, date_fin                        │
│  - Pour chaque planification P:                                    │
│    • Récupérer la date d'examen                                    │
│    • Chercher les enseignants disponibles                          │
│    • Vérifier les indisponibilités                                 │
│    • Assigner les surveillants (2-4 par exam)                      │
│  - Résultat: 84 affectations (2 survs × 42 exams)                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5️⃣ Contraintes de Validation

### ✅ Date d'Examen

```
date_debut <= date_examen <= date_fin
```

**Exemple**:
```
Session S1: [2026-01-07, 2026-01-15]
Exam le 10 janvier: ✓ Valide
Exam le 1er janvier: ✗ Avant la session
Exam le 20 janvier: ✗ Après la session
```

### ✅ Statut de Session

```
Generation possible: BROUILLON, VALIDEE
Generation impossible: PUBLIEE
```

**Exemple**:
```
Session S1 (VALIDEE): Génération ✓ possible
Session S2 (BROUILLON): Génération ✓ possible
Session Ancienne (PUBLIEE): Génération ✗ impossible
```

### ✅ Créneaux Disponibles

Les créneaux doivent:
1. Être dans la période [date_debut, date_fin]
2. Ne pas être en conflit (même salle, même heure)
3. Correspondre aux horaires valides

---

## 6️⃣ API Workflow Complet (Frontend)

```typescript
// 1. Récupérer les sessions disponibles
const catalogue = await fetch('/api/referentiel/catalogue').then(r => r.json());
const sessions = catalogue.sessions; // [{id: 1, label: "S1", ...}, ...]

// 2. Sélectionner une session (ex: S1)
const selectedSession = sessions[0]; // {id: 1, date_debut: \"2026-01-07\", ...}

// 3. Créer une planification dans cette session
const newPlanif = await fetch('/api/planifications', {
  method: 'POST',
  body: JSON.stringify({
    session_id: selectedSession.id,
    section_id: 5,
    section_matiere_id: 42,
    date_examen: \"2026-01-10\",  // DOIT être dans [date_debut, date_fin]
    // ...
  })
});

// 4. Générer des planifications automatiquement
const generated = await fetch('/api/planifications/generate', {
  method: 'POST',
  body: JSON.stringify({
    session_id: selectedSession.id,
    scope_section_ids: [5, 6, 7],
    // ...
  })
});

// 5. Affecter automatiquement les surveillants
const affectation = await fetch('/api/surveillances/affecter-session', {
  method: 'POST',
  body: JSON.stringify({
    session_id: selectedSession.id,
    section_nom: \"INF-L3\",
    // ...
  })
});

// 6. Résultat: Tous les exams de S1 ont des surveillants affectés
console.log(`Session ${selectedSession.label}: ${affectation.affectees_automatiquement}/${affectation.total_planifications}`);
```

---

## 7️⃣ Tableau des Dépendances

| Ressource | Dépend de | Raison |
|-----------|-----------|--------|
| Planification | Session | Validation de date_examen ∈ [date_debut, date_fin] |
| Creneau | Session | Filtrage: creneau.date ∈ [date_debut, date_fin] |
| Affectation | Planification | Chaque affectation concerne une planification |
| Affectation | Enseignant | Vérifier disponibilité et indisponibilités |
| Affectation | Session | Valider que session n'est pas publiée |

---

## 8️⃣ Exemples de Requêtes SQL

### 🔍 Récupérer les Planifications d'une Session

```sql
SELECT p.id, p.matiere, p.date_examen, p.heure_debut, p.heure_fin, s.statut
FROM planifications p
JOIN session s ON s.id = p.session_id
WHERE p.session_id = 1
ORDER BY p.date_examen, p.heure_debut;
```

### 🔍 Compter les Affectations par Session

```sql
SELECT 
  s.id,
  s.annee_universitaire,
  s.date_debut,
  s.date_fin,
  COUNT(DISTINCT p.id) AS nb_planifications,
  COUNT(DISTINCT a.id) AS nb_affectations
FROM session s
LEFT JOIN planifications p ON p.session_id = s.id
LEFT JOIN surveillance a ON a.planification_id = p.id
GROUP BY s.id, s.annee_universitaire, s.date_debut, s.date_fin
ORDER BY s.date_debut;
```

### 🔍 Vérifier les Créneaux d'une Session

```sql
SELECT 
  COUNT(*) AS total_creneaux,
  MIN(c.date) AS premiere_date,
  MAX(c.date) AS derniere_date,
  COUNT(DISTINCT c.date) AS nb_jours
FROM creneau c
JOIN session s ON c.date BETWEEN s.date_debut AND s.date_fin
WHERE s.id = 1;
```

---

## 9️⃣ Notes Importantes

### ⚠️ Ordre des Opérations

1. **D'abord créer la session** → Récupère date_debut, date_fin
2. **Puis créer les créneaux** → Filtrés automatiquement par la période
3. **Puis générer les planifications** → Validées contre la session
4. **Enfin affecter les surveillants** → Sur les planifications générées

### ⚠️ Modifications Dangereuses

```
❌ Ne pas modifier une session avec des planifications générées
   (sauf cas urgent avec validation)

❌ Ne pas publier une session avec des affectations incomplètes

✅ Ajouter des créneaux: OK (tant que dans [date_debut, date_fin])

✅ Modifier les dates: Attention! Requiert revalidation
```

### ⚠️ Filtrage Côté Client vs Serveur

**Backend** filtre automatiquement:
- Créneaux dans la période de session
- Planifications dans la période de session

**Frontend** affiche ce qui lui est retourné du backend

---

## 🔟 Diagramme des Relations

```
Session (1)
  ├─ has many Planifications (N)
  │  ├─ has many PlanifSalle (M)
  │  │  ├─ has 1 Salle
  │  │  ├─ has 1 Creneau
  │  │  └─ has 1 Groupe
  │  └─ has many Surveillance (K)
  │     ├─ has 1 Enseignant
  │     └─ has 1 Creneau (implicite via Planif)
  └─ has many Creneau (J)
     └─ date ∈ [session.date_debut, session.date_fin]
```

---

## 📚 Fichiers de Référence

| Fichier | Fonction |
|---------|----------|
| routers/planifications.py | POST /planifications, POST /generate |
| routers/surveillances.py | POST /affecter-session |
| services/planif_service.py | _resolve_session_context, generate |
| algorithms/planif_auto.py | Algorithme génération automatique |
| algorithms/surv_auto.py | Algorithme affectation automatique |

