# 📊 VISUAL PLANNING & ARCHITECTURE DIAGRAMS

## **1. Complete Component Hierarchy**

```
App (Root Layout)
├── Navbar
│   └── Title + User Menu
└── Div (flex layout)
    ├── Sidebar
    │   ├── Navigation Links
    │   │   ├─ Planification
    │   │   ├─ Surveillance
    │   │   │   ├─ Dashboard
    │   │   │   ├─ Affectation
    │   │   │   ├─ Charge
    │   │   │   ├─ Convocations
    │   │   │   └─ Disponibilités
    │   │   ├─ Matieres (P4)
    │   │   └─ Enseignants (P4)
    │   └── Logout
    │
    └── Main Content
        ├─ Surveillance Routes
        │  ├─ /surveillance (Dashboard)
        │  │  └─ Layout
        │  │     ├─ Title + Action Button
        │  │     ├─ Stats Grid (5 cards)
        │  │     └─ Quick Action Cards
        │  │
        │  ├─ /surveillance/affectation (Affectation Board)
        │  │  └─ Layout
        │  │     ├─ Title
        │  │     ├─ AffectationBoard
        │  │     │  ├─ Stats Grid (3 cards)
        │  │     │  └─ Surveillances Table
        │  │     │     └─ Each Row:
        │  │     │        ├─ Exam Name
        │  │     │        ├─ Assigned Teacher
        │  │     │        ├─ Charge Badge
        │  │     │        ├─ Status Badge
        │  │     │        └─ Action Buttons
        │  │     │
        │  ├─ /surveillance/charge (Charge Table)
        │  │  └─ Layout
        │  │     ├─ Title
        │  │     ├─ ChargeTable
        │  │     │  ├─ Header Row
        │  │     │  ├─ Data Rows (sorted by charge)
        │  │     │  │  ├─ Teacher Name
        │  │     │  │  ├─ Total Charge (color coded)
        │  │     │  │  ├─ Count
        │  │     │  │  ├─ Availabilities OK
        │  │     │  │  ├─ Type Badge
        │  │     │  │  └─ Details Button
        │  │     │  └─ Average Charge Footer
        │  │     │
        │  ├─ /surveillance/[id]/convocation
        │  │  └─ Layout
        │  │     ├─ Title
        │  │     ├─ ConvocationCard
        │  │     │  ├─ Header (Teacher Info)
        │  │     │  ├─ Summary Grid (4 cards)
        │  │     │  │  ├─ Total Charge
        │  │     │  │  ├─ Count
        │  │     │  │  ├─ Period
        │  │     │  │  └─ Status
        │  │     │  ├─ Assignments Table
        │  │     │  │  └─ Rows with:
        │  │     │  │     ├─ Subject
        │  │     │  │     ├─ Date
        │  │     │  │     ├─ Time
        │  │     │  │     ├─ Room
        │  │     │  │     ├─ Charge
        │  │     │  │     └─ Status
        │  │     │  └─ Action Buttons
        │  │     │     ├─ Print
        │  │     │     └─ Export PDF
        │  │     │        └─ (hidden) ConvocationPDF
        │  │     │
        │  └─ /surveillance/[id]/disponibilite
        │     └─ Layout
        │        ├─ Title
        │        ├─ Add Button (opens Modal)
        │        ├─ Modal (isOpen)
        │        │  ├─ Title
        │        │  ├─ DisponibiliteForm
        │        │  │  ├─ Date Input
        │        │  │  ├─ Time Range (start/end)
        │        │  │  ├─ Type Select
        │        │  │  ├─ Motif TextArea
        │        │  │  └─ Buttons (Cancel, Submit)
        │        │  └─ Overlay (closes modal)
        │        │
        │        └─ Disponibilites Table (if any)
        │           └─ Rows with:
        │              ├─ Date
        │              ├─ Time Range
        │              ├─ Type Badge
        │              └─ Motif
```

---

## **2. Data Flow Diagram**

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERACTION                       │
│  Admin clicks "View Charge Table for Session 1"          │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│              NEXT.JS PAGE COMPONENT                      │
│  ChargePage()                                            │
│  ├─ sessionId = 1 (from state/route)                     │
│  ├─ useTeacherCharge(1) hook called                      │
│  └─ Renders: <Layout> + <ChargeTable>                    │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│            CUSTOM HOOK (State Management)                │
│  useTeacherCharge(sessionId)                             │
│  ├─ [charges, setCharges] = useState([])                 │
│  ├─ [loading, setLoading] = useState(true)               │
│  ├─ [error, setError] = useState(null)                   │
│  │                                                       │
│  ├─ const refresh = useCallback(async () => {            │
│  │   setLoading(true)                                    │
│  │   try {                                               │
│  │     // ← Call API here                                │
│  │     const data = await getTeacherCharges(1)           │
│  │     setCharges(data.sort(...))                        │
│  │   } catch (err) {                                     │
│  │     setError(err.message)                             │
│  │   } finally {                                         │
│  │     setLoading(false)                                 │
│  │   }                                                   │
│  │ }, [])                                                │
│  │                                                       │
│  └─ useEffect(() => { refresh() }, [])                   │
│     Returns: {charges, loading, error, refresh}          │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│           API CLIENT FUNCTION                            │
│  getTeacherCharges(sessionId)                            │
│  ├─ const response = fetch(                              │
│  │   `${API_BASE}/surveillances/session/1/charges`       │
│  │ )                                                     │
│  │                                                       │
│  └─ return response.json()  // TeacherCharge[]           │
│     Returns: [                                           │
│       {                                                  │
│         enseignant_id: 5,                                │
│         nom: "Dupont",                                   │
│         prenom: "Jean",                                  │
│         total_charge: 2.5,                               │
│         nb_surveillances: 3,                             │
│         disponibilites_ok: 2,                            │
│         est_externe: false                               │
│       },                                                 │
│       ...                                                │
│     ]                                                    │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│              HTTP REQUEST                                │
│  GET /api/surveillances/session/1/charges                │
│  Headers:                                                │
│  ├─ Content-Type: application/json                       │
│  └─ Cache-Control: no-store                              │
│                                                          │
│  Response 200 OK:                                        │
│  [                                                       │
│    {                                                     │
│      "enseignant_id": 5,                                 │
│      "nom": "Dupont",                                    │
│      ...more fields                                      │
│    }                                                     │
│  ]                                                       │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│          FASTAPI BACKEND (app/routers)                   │
│  GET /api/surveillances/session/{id}/charges             │
│  │                                                       │
│  ├─ Service: SurvService.get_charges(session_id)         │
│  │  ├─ Query: SELECT * FROM surveillance WHERE ...       │
│  │  ├─ Group by enseignant_id                            │
│  │  ├─ Calculate: SUM(charge), COUNT(*), etc.            │
│  │  └─ Return: List[TeacherCharge] DTO                   │
│  │                                                       │
│  └─ Response: JSON payload                               │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│          POSTGRESQL DATABASE                             │
│  SELECT                                                  │
│    e.id as enseignant_id,                                │
│    e.nom,                                                │
│    e.prenom,                                             │
│    SUM(s.charge) as total_charge,                        │
│    COUNT(s.id) as nb_surveillances,                      │
│    COUNT(CASE WHEN d.type_dispo='DISPONIBLE'             │
│                THEN 1 END) as disponibilites_ok          │
│  FROM surveillance s                                     │
│  JOIN enseignant e ON s.enseignant_id = e.id             │
│  LEFT JOIN disponibilite_enseignant d                    │
│    ON e.id = d.enseignant_id                             │
│  WHERE s.planification_id IN                             │
│    (SELECT id FROM planification WHERE session_id=1)     │
│  GROUP BY e.id                                           │
│  ORDER BY total_charge DESC                              │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│          DATA FLOWS BACK UP                              │
│  Response → Hook → State Update → Component Re-renders   │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│          PRESENTATIONAL COMPONENT                        │
│  <ChargeTable charges={charges} />                       │
│  ├─ Loops through charges array                          │
│  ├─ Renders: <table>                                     │
│  │  └─ <tbody>                                           │
│  │     └─ {charges.map(charge => (                       │
│  │        <tr key={charge.enseignant_id}>                │
│  │          <td>{charge.prenom} {charge.nom}</td>        │
│  │          <td>{charge.total_charge}</td>               │
│  │          <td>{charge.nb_surveillances}</td>           │
│  │          <td>{charge.disponibilites_ok}</td>          │
│  │          <td>                                         │
│  │            <button                                    │
│  │              onClick={() =>                           │
│  │                onSelectTeacher(charge.enseignant_id)  │
│  │              }                                        │
│  │            >Détails</button>                          │
│  │          </td>                                        │
│  │        </tr>                                          │
│  │      ))}                                              │
│  │  </tbody>                                             │
│  │  └─ Footer with average                               │
│  └─ User sees table rendered on screen                   │
└──────────────────────┬──────────────────────────────────┘

                       ↓

┌─────────────────────────────────────────────────────────┐
│              USER SEES RESULT                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Tableau de Charge                                   │  │
│  ├────────────────────────────────────────────────────┤  │
│  │ Enseignant  │ Charge │ Surveillances │ Dispo │ ...  │  │
│  ├─────────────┼────────┼───────────────┼───────┼────│  │
│  │ Jean Dupont │ 2.5    │ 3             │ 2/3   │... │  │
│  │ Marie Aurel │ 1.8    │ 2             │ 2/2   │... │  │
│  │ Pierre Dubb │ 3.2    │ 4             │ 3/4   │... │  │
│  ├────────────────────────────────────────────────────┤  │
│  │ Charge moyenne: 2.5                                 │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  User clicks "Détails" for Jean Dupont                  │
│  → Navigation to /surveillance/5/convocation             │
│  → Process repeats for ConvocationPage                   │
└──────────────────────────────────────────────────────────┘
```

---

## **3. File Dependency Graph**

```
UTILITIES & CONFIG
├─ utils.ts
└─ constants.ts

TYPES
└─ types/surveillance.ts

API CLIENT
├─ api/surveillance.ts (depends on: types, constants)
└─ lib/api/client.ts

HOOKS (State Management)
├─ hooks/useSurveillance.ts (depends on: api)
├─ hooks/useTeacherCharge.ts (depends on: api)
├─ hooks/useDisponibilite.ts (depends on: api)
├─ hooks/useConvocation.ts (depends on: api)
└─ hooks/usePDFExport.ts

UI COMPONENTS (Shared)
├─ ui/Button.tsx
├─ ui/Modal.tsx
├─ ui/AuthGuard.tsx
├─ ui/Layout.tsx
├─ ui/Navbar.tsx
└─ ui/Sidebar.tsx

SURVEILLANCE COMPONENTS
├─ surveillance/ChargeTable.tsx (depends on: types, constants, Button)
├─ surveillance/DisponibiliteForm.tsx (depends on: Button, constants)
├─ surveillance/ConvocationCard.tsx (depends on: types, utils, Button)
├─ surveillance/ConvocationPDF.tsx (depends on: types, utils)
├─ surveillance/AffectationBoard.tsx (depends on: types, Button)
└─ surveillance/Modal + Form combinations

PAGES
├─ app/(admin)/surveillance/page.tsx
│  └─ depends on: useSurveillance, Layout, Button
├─ app/(admin)/surveillance/affectation/page.tsx
│  └─ depends on: useSurveillance, AffectationBoard
├─ app/(admin)/surveillance/charge/page.tsx
│  └─ depends on: useTeacherCharge, ChargeTable, useRouter
├─ app/(admin)/surveillance/[id]/convocation/page.tsx
│  └─ depends on: useConvocation, ConvocationCard, usePDFExport
└─ app/(admin)/surveillance/[id]/disponibilite/page.tsx
   └─ depends on: useDisponibilite, DisponibiliteForm, Modal

ROOT LAYOUT
└─ app/layout.tsx (depends on: Navbar, Sidebar)
```

---

## **4. State Management Flow**

```
Page Component
    ↓
[sessionId, enseignantId] from route/state
    ↓
    ├─ useHook(id) called
    │  ↓
    │  Create state variables:
    │  ├─ [data, setData] = useState([])
    │  ├─ [loading, setLoading] = useState(true)
    │  ├─ [error, setError] = useState(null)
    │
    │  Define refresh callback:
    │  ├─ setLoading(true)
    │  ├─ try {
    │  │   const result = await fetchFunction(id)
    │  │   setData(result)
    │  │ } catch (err) {
    │  │   setError(err)
    │  │ }
    │  ├─ finally {
    │  │   setLoading(false)
    │  │ }
    │
    │  Auto-fetch on mount:
    │  ├─ useEffect(() => {
    │  │   void refresh()
    │  │ }, [refresh])
    │
    │  Return { data, loading, error, refresh }
    │
    ├─ Destructure hook return
    │  const { data, loading, error, refresh } = useHook(id)
    │
    ├─ Show loading state if loading
    │
    ├─ Show error state if error
    │
    └─ Show component with data when ready
       └─ <Component data={data} onAction={handler} />
          ↓
          Event triggered (click, submit, etc.)
          ↓
          Handler calls function:
          ├─ updateData() / deleteData() / etc.
          ├─ Then: refresh()  ← State updates
          └─ UI re-renders automatically
```

---

## **5. Form Submission Flow**

```
User fills form fields
    ↓
[formData state updates]
    ↓
User clicks "Submit"
    ↓
handleSubmit(e) handler triggered
    ├─ e.preventDefault()
    ├─ setIsLoading(true)
    ├─ try {
    │  ├─ await onSubmit(formData)  ← API call
    │  │  ├─ fetch POST /api/endpoint
    │  │  ├─ backend processes
    │  │  ├─ database INSERT
    │  │  └─ response returns
    │  │
    │  ├─ Reset form fields
    │  ├─ Close modal (if applicable)
    │  └─ refresh() ← Update parent state
    │     ├─ Calls hook refresh()
    │     ├─ Fetches fresh data
    │     └─ Parent component re-renders
    │
    │ } catch (err) {
    │  └─ setError(err.message)
    │
    │ } finally {
    │  └─ setIsLoading(false)
    │     └─ Button state returns to normal
    │
    └─ User sees success message
       └─ New item appears in list
```

---

## **6. Navigation Flow**

```
Sidebar Navigation
│
├─ /app/(admin)/surveillance
│  └─ Dashboard with stats
│     └─ Links to other pages
│
├─ /app/(admin)/surveillance/affectation
│  └─ Affectation Board
│     └─ Link to teacher details
│
├─ /app/(admin)/surveillance/charge
│  └─ Charge Table
│     └─ Click "Détails" → /surveillance/[id]/convocation
│
├─ /app/(admin)/surveillance/[id]/convocation
│  └─ Teacher's convocation detail
│     └─ Export PDF or go back
│
└─ /app/(admin)/surveillance/[id]/disponibilite
   └─ Teacher's availability form
      └─ Add dates and time slots
```

---

## **7. URL Patterns**

```
Route Pattern                          Component                  Data Source
──────────────────────────────────────────────────────────────────────────────

/app/(admin)/surveillance
└─ Dashboard                           page.tsx                   useSurveillance(1)
└─ Shows: stats grid + action buttons

/app/(admin)/surveillance/affectation
└─ Affectation board                   page.tsx                   useSurveillance(1)
└─ Shows: assignments table + stats

/app/(admin)/surveillance/charge
└─ Charge table                        page.tsx                   useTeacherCharge(1)
└─ Shows: teacher charges sorted

/app/(admin)/surveillance/[enseignant_id]/convocation
└─ Individual convocation              page.tsx                   useConvocation(id)
└─ Shows: teacher detail + assignments

/app/(admin)/surveillance/[enseignant_id]/disponibilite
└─ Availability management             page.tsx                   useDisponibilite(id)
└─ Shows: form + existing availabilities
```

---

## **8. Error Handling Flowchart**

```
User action triggers async operation
    ↓
┌─────────────────────────────┐
│ setLoading(true)            │ ← Show spinner
├─────────────────────────────┤
│ try {                        │
│   await fetchData()          │
│   setData(result)            │
│ }                            │
├─────────────────────────────┤
│ catch (error) {              │ ← Network error, parse error, etc.
│   setError(error.message)    │
│ }                            │
├─────────────────────────────┤
│ finally {                    │
│   setLoading(false)          │ ← Hide spinner
│ }                            │
└─────────────────────────────┘
    ↓
Conditional rendering in component:

if (loading) return <LoadingSpinner />
  ↓ Show: ⏳

if (error) return <ErrorBox message={error} />
  ↓ Show: ⚠️ Error: {message}
  ↓ Show: Retry button

if (data) return <Content data={data} />
  ↓ Show: Actual content
```

---

## **9. Testing Scenario Example**

### **Scenario: Add Disponibilité**

```
┌─────────────────────────────────────────────────────┐
│ User navigates to /surveillance/5/disponibilite     │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ DisponibilityPage component mounts                   │
│ useDisponibilite(5) hook calls                       │
│ → getTeacherDisponibilites(5)                        │
│ → GET /api/disponibilites/enseignant/5              │
│ → Returns: []  (no existing ones)                    │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Page renders with empty table                        │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ User clicks "+ Ajouter" button                       │
│ setIsModalOpen(true)                                 │
│ Modal appears with DisponibiliteForm                │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ User fills form:                                     │
│ date: "2026-01-15"                                   │
│ heure_debut: "14:00"                                 │
│ heure_fin: "18:00"                                   │
│ type_dispo: "MISSION"                                │
│ motif: "Jury FSSM"                                   │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ User clicks "Ajouter"                                │
│ handleAdd(formData) called                           │
│ setIsLoading(true)  ← button shows spinner          │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ API call: POST /api/disponibilites                   │
│ {                                                    │
│   "enseignant_id": 5,                                │
│   "date": "2026-01-15",                              │
│   "heure_debut": "14:00",                            │
│   "heure_fin": "18:00",                              │
│   "type_dispo": "MISSION",                           │
│   "motif": "Jury FSSM"                               │
│ }                                                    │
│                                                      │
│ Backend inserts record                               │
│ Returns: {id: 42, ...same data...}                   │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Back in hook: handleAdd() completes                  │
│ await refresh()                                      │
│ → Calls getTeacherDisponibilites(5) again           │
│ → GET /api/disponibilites/enseignant/5              │
│ → Returns: [{id: 42, date: "2026-01-15", ...}]      │
│ → setDisponibilites([{id: 42, ...}])                │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ setIsLoading(false)  ← button returns to normal     │
│ setIsModalOpen(false) ← modal closes                 │
│ Component re-renders with new data                  │
└────────────────────┬────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ✅ User sees:                                       │
│ - Modal closed                                       │
│ - Table now shows 1 row                              │
│ - Row contains: 2026-01-15, 14:00-18:00,             │
│   MISSION, "Jury FSSM"                               │
└─────────────────────────────────────────────────────┘
```

---

## **10. Performance Optimization Points**

```
Optimization                  Location                Implementation
─────────────────────────────────────────────────────────────────────

Prevent rerenders on         Hook (useCallback)       Dependencies properly tracked
parent changes

Lazy load components         Page (dynamic import)    If needed: lazy(() => import(...))

Debounce API calls           Hook                     useCallback with dependencies

Cache API responses          Hook (useState)          Manual cache or React Query

Optimize table rendering     Component (useMemo)      Memoize expensive calculations

Image optimization           UI Components            Use Next.js Image component

CSS optimization             TailwindCSS config       Purge unused styles

Bundle optimization          next.config.ts           Code splitting for routes

Database query optimization  Backend (ORM)            Eager loading, indexes, pagination
```

---

