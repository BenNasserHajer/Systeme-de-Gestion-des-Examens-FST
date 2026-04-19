# Organisation Soutenance PFA

## Structure Dossiers

### Backend

```text
server/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── models/
│   │   ├── planification.py
│   │   ├── surveillance.py
│   │   └── base.py
│   ├── schemas/
│   │   ├── planification.py
│   │   ├── surveillance.py
│   │   └── commun.py
│   ├── routers/
│   │   ├── planifications.py
│   │   ├── surveillances.py
│   │   └── referentiel.py
│   ├── services/
│   │   ├── planif_service.py
│   │   ├── surv_service.py
│   │   └── charge_service.py
│   ├── algorithms/
│   │   ├── planif_auto.py
│   │   ├── contraintes.py
│   │   └── surv_auto.py
│   └── crud/
│       ├── crud_planif.py
│       └── crud_surv.py
├── alembic/versions/
│   ├── 001_planif.py
│   └── 002_surv.py
├── tests/
│   ├── test_planif.py
│   └── test_surv.py
└── requirements.txt
```

### Frontend (Next.js latest)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── (admin)/
│   │   │   ├── planification/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/edit/page.tsx
│   │   │   ├── surveillance/page.tsx
│   │   │   ├── salles/page.tsx
│   │   │   ├── matieres/page.tsx
│   │   │   └── enseignants/page.tsx
│   │   └── (enseignant)/
│   │       └── convocation/page.tsx
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── DataTable.tsx
│   │   ├── planification/
│   │   │   ├── EmploiDuTemps.tsx
│   │   │   ├── PlanifCard.tsx
│   │   │   └── GroupeTable.tsx
│   │   └── surveillance/
│   │       ├── ChargeTable.tsx
│   │       ├── ConvocationCard.tsx
│   │       └── DisponibiliteForm.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── planification.ts
│   │   │   └── surveillance.ts
│   │   ├── types/
│   │   │   ├── planification.ts
│   │   │   └── surveillance.ts
│   │   └── utils.ts
│   └── hooks/
│       ├── usePlanification.ts
│       └── useSurveillance.ts
├── .env.local
└── package.json
```

## Repartition Exacte

- P1 - Back Planif: models/planification.py, schemas/planification.py, routers/planifications.py, services/planif_service.py, algorithms/planif_auto.py, algorithms/contraintes.py, crud/crud_planif.py, alembic/versions/001_planif.py, tests/test_planif.py.
- P2 - Back Surv: models/surveillance.py, schemas/surveillance.py, routers/surveillances.py, services/surv_service.py, services/charge_service.py, algorithms/surv_auto.py, crud/crud_surv.py, alembic/versions/002_surv.py, tests/test_surv.py.
- P3 - Front Planif: pages planification/salles/matieres, components/planification/*, lib/api/planification.ts, lib/types/planification.ts, hooks/usePlanification.ts.
- P4 - Front Surv: layout/global UI final, page surveillance, page enseignants, espace enseignant convocation, components/surveillance/*, lib/api/surveillance.ts, lib/types/surveillance.ts, hooks/useSurveillance.ts.
- Partage (tous): conventions git, design system commun, composants UI (`components/ui/*`), revue de code croisee.

## Conventions Soutenance

- Regle absolue: aucune logique metier dans les composants React.
- Regle absolue: aucune logique metier dans les routers FastAPI.
- Backend: la logique metier est uniquement dans `app/services/`.
- Frontend: la logique metier et les appels API sont portes par `src/hooks/` et `src/lib/api/`.
- Routers/API routes: validation entree/sortie, appel service, retour HTTP uniquement.
- Composants React: affichage pur, callbacks, etat UI local uniquement.
- Nommage: `snake_case.py` cote backend, `PascalCase.tsx` pour les composants.
- Tests: minimum un test d endpoint par module (`planif` et `surv`) + tests hooks cote front.

## Planning 4 Semaines

- Semaine 1: socle architecture, modeles/schemas, migration 001, pages planification de base, composants UI partages.
- Semaine 2: services + CRUD planification, endpoint auto planif, hooks front planification, integration page admin planification.
- Semaine 3: modeles/schemas surveillance, migration 002, services charge/surveillance, pages surveillance + enseignants.
- Semaine 4: espace enseignant convocation, tests et corrections, nettoyage code, repetition soutenance (demo + justification architecture).
