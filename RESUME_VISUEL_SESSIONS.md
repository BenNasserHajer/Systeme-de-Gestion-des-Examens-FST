# 🎨 Résumé Visuel - Sessions Backend

## 📊 Architecture des Sessions

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │     SESSION      │         │     CRENEAU      │                 │
│  ├──────────────────┤         ├──────────────────┤                 │
│  │ id (PK)          │         │ id (PK)          │                 │
│  │ type_session     │         │ date             │                 │
│  │ annee_universi.. │         │ heure_debut      │                 │
│  │ date_debut       │ 1───────│ heure_fin        │ N               │
│  │ date_fin         │         │ libelle          │                 │
│  │ statut           │         └──────────────────┘                 │
│  └──────────────────┘                                              │
│         1 │                                                         │
│           │                                                         │
│        N  │                                                         │
│  ┌────────▼──────────────┐                                         │
│  │  PLANIFICATIONS       │                                         │
│  ├──────────────────────┤                                         │
│  │ id (PK)              │                                         │
│  │ session_id (FK)      │                                         │
│  │ section_id           │                                         │
│  │ matiere              │                                         │
│  │ date_examen          │                                         │
│  │ heure_debut          │                                         │
│  │ heure_fin            │                                         │
│  └──────────────────────┘                                         │
│         1 │                                                         │
│           │                                                         │
│        K  │                                                         │
│  ┌────────▼──────────────┐                                         │
│  │  SURVEILLANCE         │                                         │
│  ├──────────────────────┤                                         │
│  │ id (PK)              │                                         │
│  │ planification_id (FK)│                                         │
│  │ enseignant_id        │                                         │
│  │ date_affectation     │                                         │
│  └──────────────────────┘                                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🗓️ Calendrier 2025/2026

```
┌─────────────────────────────────────────────────────────────────┐
│ ANNÉE UNIVERSITAIRE 2025/2026                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ JAN 2026                                                         │
│ ├─ 07 (Mer) ─── S1 START                                        │
│ ├─ 08 (Jeu)                                                    │
│ ├─ 09 (Ven)                                                    │
│ ├─ 10 (Sam)    [Planification: Maths, BD, Algo]               │
│ ├─ 11 (Dim)    [Pas d'examen]                                  │
│ ├─ 12 (Lun)    [Surveillance: Prof1, Prof2]                   │
│ ├─ 13 (Mar)                                                    │
│ ├─ 14 (Mer)                                                    │
│ ├─ 15 (Jeu) ─── S1 END                                         │
│                                                                  │
│                                                                  │
│ MAI 2026                                                         │
│ ├─ 11 (Lun) ─── S2 START                                        │
│ ├─ 12 (Mar)                                                    │
│ ├─ 13 (Mer)    [Planification: ML, Stats, DB2]                │
│ ├─ 14 (Jeu)                                                    │
│ ├─ 15 (Ven)    [Surveillance: Prof3, Prof4]                   │
│ ├─ 16 (Sam)                                                    │
│ ├─ 17 (Dim)    [Pas d'examen]                                  │
│ ├─ 18 (Lun)                                                    │
│ ├─ 19 (Mar)                                                    │
│ ├─ 20 (Mer)                                                    │
│ ├─ 21 (Jeu)                                                    │
│ ├─ 22 (Ven)                                                    │
│ └─ 23 (Sam) ─── S2 END                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow: De la Session aux Examens

```
ÉTAPE 1: INITIALISATION
┌──────────────────────────────────────────────┐
│ Créer Session S1                             │
│ • type_session = "PRINCIPALE"                │
│ • annee_universitaire = "2025/2026"          │
│ • date_debut = 2026-01-07                    │
│ • date_fin = 2026-01-15                      │
│ • statut = "BROUILLON"                       │
└──────────────────────────────────────────────┘

ÉTAPE 2: CRÉNEAUX
┌──────────────────────────────────────────────┐
│ Créer Créneaux (24 slots)                    │
│ • 2026-01-07 08:30-10:30 (Mer Matin)         │
│ • 2026-01-07 11:00-13:00 (Mer Midi)          │
│ • 2026-01-07 14:00-16:00 (Mer Après-midi)   │
│ • ... (3 slots × 8 jours = 24 créneaux)     │
└──────────────────────────────────────────────┘

ÉTAPE 3: PLANIFICATIONS
┌──────────────────────────────────────────────┐
│ Générer Planifications (42 exams)            │
│ Pour chaque matière:                         │
│ • Chercher créneaux libres dans              │
│   [2026-01-07, 2026-01-15]                   │
│ • Assigner salle + groupe                    │
│ • Créer planification                        │
│ Résultat: 42 planifications générées         │
└──────────────────────────────────────────────┘

ÉTAPE 4: SURVEILLANCE
┌──────────────────────────────────────────────┐
│ Affecter Surveillants (2-4 par exam)         │
│ Pour chaque planification:                   │
│ • Récupérer date + heure d'examen            │
│ • Chercher enseignants disponibles           │
│ • Vérifier indisponibilités                  │
│ • Assigner surveillants                      │
│ Résultat: ~84 affectations (2×42)            │
└──────────────────────────────────────────────┘

ÉTAPE 5: PUBLICATION
┌──────────────────────────────────────────────┐
│ Valider et Publier                           │
│ • Statut session → "VALIDEE" → "PUBLIEE"     │
│ • Tous les exams ont leurs surveillants      │
│ • Les étudiants voient l'emploi du temps     │
└──────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

```
GET /referentiel/catalogue
├─ sessions: [
│   { id: 1, label: "Principale 2025/2026", date_debut: "2026-01-07", ... },
│   { id: 2, label: "Principale 2025/2026", date_debut: "2026-05-11", ... }
│  ]
├─ creneaux: [
│   { date: "2026-01-07", heure_debut: "08:30", heure_fin: "10:30" },
│   ...
│  ]
├─ sections: [...]
├─ matieres_by_section: {...}
└─ salles: [...]

POST /planifications
├─ Input: { session_id, section_id, date_examen, ... }
├─ Validation: date_examen ∈ [session.date_debut, session.date_fin]
└─ Output: { id, session_id, matiere, date_examen, ... }

POST /planifications/generate
├─ Input: { session_id, scope_section_ids, semestre, ... }
├─ Process: Génère automatiquement les planifications
└─ Output: { total: 42, created: 42, updated: 0 }

POST /surveillances/affecter-session
├─ Input: { session_id, section_nom, periode, ... }
├─ Process: Affecte auto les surveillants
└─ Output: { session, total_planifications, affectees, manquantes, ... }
```

---

## 🔍 Filtering Logic

```
┌─────────────────────────────────────────────────────────────────┐
│ Filtre: Créneaux d'une Session                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ALL CRENEAUX (DB)                                               │
│ ├─ 2026-01-06 08:30 ─────────────┐                              │
│ ├─ 2026-01-07 08:30 ─────────────┤                              │
│ ├─ 2026-01-08 08:30 ─────────────┤                              │
│ ├─ 2026-01-15 08:30 ─────────────┤ FILTERED                     │
│ ├─ 2026-01-16 08:30 ─────────────┤ (within session              │
│ ├─ 2026-05-10 08:30 ─────────────┤ [2026-01-07 to              │
│ └─ 2026-05-11 08:30 ─────────────┘ 2026-01-15])                │
│                                                                  │
│ CRENEAUX FOR SESSION S1 (24 slots)                              │
│ └─ 2026-01-07 to 2026-01-15                                    │
│    ├─ 3 slots per day                                          │
│    └─ 8 days × 3 = 24 creneaux                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Validation Chain

```
┌──────────────────────────┐
│ Create Planification     │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Get Session ID:1         │
│ Load: date_debut, ...    │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Validate:                │
│ date_debut <= date_exam  │──────┐
│       <= date_fin        │      │
└────────┬─────────────────┘      │
         │                        │
    YES  │                        NO
         │                        │
         ▼                        ▼
    ┌─────────┐          ┌──────────────┐
    │ CREATE  │          │ REJECT       │
    │ PLANIF  │          │ + Error Msg  │
    └─────────┘          └──────────────┘
```

---

## 📈 Data Volume (Example: S1)

```
┌────────────────────────────────────────────────┐
│ Session S1 (7-15 janvier 2026)                │
├────────────────────────────────────────────────┤
│                                                │
│ Days: 8 (excluding Sundays)                   │
│ Creneaux/day: 3 (08:30, 11:00, 14:00)        │
│ Total Creneaux: 24                            │
│                                                │
│ Sections: 10                                  │
│ Matieres/section: ~4                          │
│ Total Matieres: ~40                           │
│                                                │
│ Planifications/matiere: ~1                    │
│ Total Planifications: ~42                     │
│                                                │
│ Surveillants/planif: 2-4 (avg 2.5)           │
│ Total Affectations: ~105                      │
│                                                │
│ Salles disponibles: 20                        │
│ Salles utilisées: ~12                         │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 🎯 Key Fields Mapping

```
Session → date_debut
   ↓
   ├─→ Creneau: date ∈ [date_debut, date_fin]
   │
Session → date_fin
   ↓
   └─→ Planification: date_examen ∈ [date_debut, date_fin]
       ↓
       └─→ Surveillance: date_exam_implicite

Session → statut
   ↓
   ├─→ BROUILLON: Can edit/generate
   ├─→ VALIDEE: Can edit but careful
   └─→ PUBLIEE: Read-only (no changes)

Session → annee_universitaire (e.g., "2025/2026")
   ↓
   └─→ Matiere: semestre (S1, S2) for filtering
```

---

## 🚀 Quick Lookup Table

| Need | Query | File |
|------|-------|------|
| Get all sessions | SELECT * FROM session | catalogue_service.py |
| Get session dates | session.date_debut, session.date_fin | salle_session.py |
| Filter creneaux | WHERE creneau.date BETWEEN s.date_debut AND s.date_fin | catalogue_service.py |
| Validate date | IF date_exam ∈ [date_debut, date_fin] THEN OK | planifications.py |
| Count planifs | SELECT COUNT(*) FROM planifications WHERE session_id = ? | crud_planif.py |
| Affecter survs | WHERE session_id = ? ORDER BY date_examen | surv_auto.py |

---

## 🔗 Relationship Summary

```
┌────────┐
│Session │ ──1:N──→ │Planifications│ ──1:K──→ │Surveillance│
└────────┘          └──────────────┘          └─────────────┘
    ↓
  dates define
    ↓
┌────────┐
│Creneau │ (filtered by session dates)
└────────┘
```

---

## 💡 Pro Tips

1. **Always validate date_examen against session.date_debut/date_fin**
   ```python
   if not (session.date_debut <= date_examen <= session.date_fin):
       raise ValidationError("Invalid date for this session")
   ```

2. **Filter creneaux automatically in catalogue service**
   ```python
   creneaux_session = [c for c in all_creneaux 
                       if session.date_debut <= c.date <= session.date_fin]
   ```

3. **Check session.statut before generating**
   ```python
   if session.statut == \"PUBLIEE\":
       raise ConstraintError(\"Cannot modify published session\")
   ```

4. **Modifying session dates? Don't forget to revalidate planifications**
   ```python
   # After changing date_debut/date_fin:
   # 1. Check all existing planifications are still within range
   # 2. If not, move them or notify admin
   ```

---

## 📚 All Related Files

```
server/
├─ app/
│  ├─ models/
│  │  └─ salle_session.py (Session, Creneau ORM)
│  ├─ schemas/
│  │  ├─ session_schema.py (SessionOut)
│  │  └─ salle_session_schema.py (SessionBase, SessionCreate, SessionUpdate)
│  ├─ routers/
│  │  ├─ referentiel.py (GET /catalogue)
│  │  ├─ planifications.py (POST /planifications, POST /generate)
│  │  └─ surveillances.py (POST /affecter-session)
│  ├─ services/
│  │  ├─ catalogue_service.py (load_catalogue, _load_sessions, _load_creneaux)
│  │  └─ planif_service.py (_resolve_session_context)
│  ├─ algorithms/
│  │  ├─ planif_auto.py (generation logic)
│  │  └─ surv_auto.py (affectation logic)
│  ├─ crud/
│  │  └─ crud_planif.py (CRUD operations)
│  └─ seed/
│     └─ seed_data_v2.sql (S1 + S2 data)
├─ add_session_s2.py (Script to add S2)
└─ tests/
   └─ test_*.py
```

