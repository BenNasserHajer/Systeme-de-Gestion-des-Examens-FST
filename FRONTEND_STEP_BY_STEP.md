# 🛠️ STEP-BY-STEP FILE CREATION GUIDE

## **Phase 1: Types & Constants (30 mins)**

### Step 1.1: Create Types File
**File**: `src/lib/types/surveillance.ts`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 1 for full code]

**What to include**:
- ✅ Enseignant interface
- ✅ Surveillance interface  
- ✅ DisponibiliteEnseignant interface
- ✅ TeacherCharge interface
- ✅ ConvocationData interface
- ✅ Type aliases (FormPayload types)

**Verification**:
```bash
npx tsc --noEmit  # Should have no errors for this file
```

---

### Step 1.2: Create Constants File
**File**: `src/lib/constants.ts`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 1 for full code]

**What to include**:
- ✅ Color mappings for statuses
- ✅ Disponibilité type options
- ✅ Affectation modes
- ✅ API base URL

**Test locally**:
```typescript
import { SURVEILLANCE_STATUT_COLORS } from "@/lib/constants";
console.log(SURVEILLANCE_STATUT_COLORS.AFFECTE);  // Should log colors
```

---

## **Phase 2: API Client (30 mins)**

### Step 2.1: Create API Client File
**File**: `src/lib/api/surveillance.ts`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 2 for full code]

**What to include** (10 functions):
- ✅ getSurveillancesBySession()
- ✅ getTeacherConvocation()
- ✅ getTeacherCharges()
- ✅ getAffectationBoard()
- ✅ createDisponibilite()
- ✅ getTeacherDisponibilites()
- ✅ updateSurveillance()
- ✅ deleteSurveillance()
- ✅ generateAffectations()
- Plus helper utilities

**Test functions**:
```bash
# Backend must be running
curl http://localhost:8000/api/surveillances/session/1
# Should return: []
```

---

## **Phase 3: Custom Hooks (1 hour)**

### Step 3.1: useSurveillance Hook
**File**: `src/hooks/useSurveillance.ts`

**Template**:
```typescript
"use client";
import { useCallback, useEffect, useState } from "react";
import { getSurveillancesBySession, getAffectationBoard } from "@/lib/api/surveillance";
import type { Surveillance, AffectationBoard } from "@/lib/types/surveillance";

export function useSurveillance(sessionId: number | null) {
  const [surveillances, setSurveillances] = useState<Surveillance[]>([]);
  const [board, setBoard] = useState<AffectationBoard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const [data, boardData] = await Promise.all([
        getSurveillancesBySession(sessionId),
        getAffectationBoard(sessionId),
      ]);
      setSurveillances(data);
      setBoard(boardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading surveillances");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [refresh]);

  return { surveillances, board, loading, error, refresh };
}
```

**Test**:
```typescript
// In a component
const { surveillances, loading } = useSurveillance(1);
console.log(surveillances);  // Should log array
```

### Step 3.2-3.4: Create Other Hooks
**Files**:
- `src/hooks/useTeacherCharge.ts` - Similar pattern
- `src/hooks/useDisponibilite.ts` - With `add()` method
- `src/hooks/useConvocation.ts` - Simple fetch

**Copy pattern from 3.1 and adapt for each**

---

## **Phase 4: Shared UI Components (1.5 hours)**

### Step 4.1: Button Component
**File**: `src/components/ui/Button.tsx`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 4 for full code]

**Features**:
- ✅ 4 variants (primary, secondary, danger, ghost)
- ✅ 3 sizes (sm, md, lg)
- ✅ isLoading state
- ✅ Proper TypeScript

**Test**:
```typescript
<Button variant="primary" size="md">Click me</Button>
<Button isLoading={true}>Loading...</Button>
<Button variant="danger">Delete</Button>
```

---

### Step 4.2: Modal Component
**File**: `src/components/ui/Modal.tsx`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 4 for full code]

**Features**:
- ✅ Overlay with backdrop
- ✅ Close button (×)
- ✅ Title, content, actions
- ✅ Controlled by isOpen prop

**Test**:
```typescript
const [open, setOpen] = useState(false);
<Modal isOpen={open} title="Test" onClose={() => setOpen(false)}>
  Content
  <actions>
    <Button onClick={() => setOpen(false)}>Close</Button>
  </actions>
</Modal>
```

---

### Step 4.3: AuthGuard Component
**File**: `src/components/ui/AuthGuard.tsx`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 4 for full code]

**Features**:
- ✅ Check authentication
- ✅ Check role-based access
- ✅ Show loading state
- ✅ Show access denied message

**Test**:
```typescript
<AuthGuard requiredRole="admin">
  Admin only content
</AuthGuard>
```

---

### Step 4.4: Layout Component
**File**: `src/components/ui/Layout.tsx`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 4 for full code]

**Features**:
- ✅ Title + subtitle
- ✅ Action button slot
- ✅ Consistent spacing
- ✅ Common pattern for all pages

**Test**:
```typescript
<Layout 
  title="My Page" 
  subtitle="Description"
  action={<Button>Action</Button>}
>
  Page content
</Layout>
```

---

## **Phase 5: Surveillance Components (2 hours)**

### Step 5.1: ChargeTable Component
**File**: `src/components/surveillance/ChargeTable.tsx`

**Key points**:
- ✅ Display TeacherCharge array
- ✅ Color coding for charge levels
- ✅ Average charge calculation
- ✅ Click handler for selection

**Test data**:
```typescript
const mockCharges: TeacherCharge[] = [
  {
    enseignant_id: 1,
    nom: "Dupont",
    prenom: "Jean",
    total_charge: 2.5,
    nb_surveillances: 3,
    disponibilites_ok: 2,
    est_externe: false,
  },
];
<ChargeTable charges={mockCharges} />
```

---

### Step 5.2: DisponibiliteForm Component
**File**: `src/components/surveillance/DisponibiliteForm.tsx`

**Key points**:
- ✅ Date picker
- ✅ Time range pickers
- ✅ Type dropdown
- ✅ Optional motif textarea
- ✅ Form validation
- ✅ Submit button with loading state

**Form fields**:
```
date (required)
heure_debut (required, time)
heure_fin (required, time)
type_dispo (select from DISPONIBILITE_TYPES)
motif (optional textarea)
```

---

### Step 5.3: ConvocationCard Component
**File**: `src/components/surveillance/ConvocationCard.tsx`

**Key sections**:
- ✅ Header with teacher info
- ✅ 4-column summary (charge, count, period, status)
- ✅ Assignments table
- ✅ Export PDF button

**Mock data for testing**:
```typescript
const mockConvocation: ConvocationData = {
  enseignant: { id: 1, nom: "Dupont", prenom: "Jean", email: "j.dupont@univ.tn" },
  surveillances: [
    { id: 1, charge: 1.0, statut_surveillance: "AFFECTE", salle_id: 1, ... }
  ],
  charge_totale: 2.5,
  session_date_debut: "2026-01-07",
  session_date_fin: "2026-02-14"
};
```

---

### Step 5.4: AffectationBoard Component
**File**: `src/components/surveillance/AffectationBoard.tsx`

**Key sections**:
- ✅ Stats grid (Total, Affectées, Conflits)
- ✅ Surveillances table
- ✅ Assign/Unassign buttons

**Table columns**:
```
Examen | Affecté | Charge | Statut | Actions
```

---

## **Phase 6: PDF Export (1 hour)**

### Step 6.1: Install Dependency
```bash
npm install @react-pdf/renderer

# Also add types if needed
npm install --save-dev @types/react-pdf-renderer
```

### Step 6.2: ConvocationPDF Component
**File**: `src/components/surveillance/ConvocationPDF.tsx`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 6 for full code]

**Structure**:
- ✅ Document wrapper
- ✅ Page setup (A4)
- ✅ Header section
- ✅ Styled table for assignments
- ✅ Footer with date

**Test**:
```typescript
import { PDFDownloadLink } from "@react-pdf/renderer";

<PDFDownloadLink 
  document={<ConvocationPDF data={data} />} 
  fileName="convocation.pdf"
>
  {({ loading }) => (loading ? "Generating..." : "Download PDF")}
</PDFDownloadLink>
```

### Step 6.3: usePDFExport Hook
**File**: `src/hooks/usePDFExport.ts`

[See FRONTEND_IMPLEMENTATION_PLAN.md Phase 6 for full code]

**Usage**:
```typescript
const { exportPDF } = usePDFExport();
await exportPDF(
  <ConvocationPDF data={data} />,
  `convocation_${name}.pdf`
);
```

---

## **Phase 7: Pages (2 hours)**

### Step 7.1: Surveillance Dashboard
**File**: `src/app/(admin)/surveillance/page.tsx`

**Structure**:
```tsx
export default function SurveillancePage() {
  // 1. State
  const [sessionId] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // 2. Data
  const { board, loading, error, refresh } = useSurveillance(sessionId);
  
  // 3. Handlers
  const handleGenerateAffectations = async () => { ... }
  
  // 4. UI
  return <Layout>...</Layout>
}
```

**Key elements**:
- ✅ 5-column stats grid
- ✅ 3 action buttons (Affectation, Charge, Convocations)
- ✅ Generate button with loading state

### Step 7.2: Affectation Page
**File**: `src/app/(admin)/surveillance/affectation/page.tsx`

**Structure**:
- ✅ useSurveillance hook
- ✅ AffectationBoard component
- ✅ handleRemove callback

### Step 7.3: Charge Page
**File**: `src/app/(admin)/surveillance/charge/page.tsx`

**Structure**:
- ✅ useTeacherCharge hook
- ✅ ChargeTable component
- ✅ Navigation to convocation on select

### Step 7.4: Convocation Page
**File**: `src/app/(admin)/surveillance/[enseignant_id]/convocation/page.tsx`

**Structure**:
- ✅ Dynamic route with enseignant_id
- ✅ useConvocation hook
- ✅ ConvocationCard component
- ✅ handleExportPDF callback

**Important**: Use `use(params)` hook for async params in Next.js 15+:
```typescript
const { enseignant_id } = use(params);
const enseignantId = parseInt(enseignant_id);
```

### Step 7.5: Disponibilité Page
**File**: `src/app/(admin)/surveillance/[enseignant_id]/disponibilite/page.tsx`

**Structure**:
- ✅ Dynamic route with enseignant_id
- ✅ useDisponibilite hook
- ✅ Modal for form
- ✅ DisponibiliteForm component
- ✅ Disponibilité list table

**Table columns**:
```
Date | Horaire | Type | Motif
```

---

## **File Creation Checklist**

### Phase 1 ✅
- [ ] `src/lib/types/surveillance.ts` - 100 lines
- [ ] `src/lib/constants.ts` - 30 lines

### Phase 2 ✅
- [ ] `src/lib/api/surveillance.ts` - 150 lines

### Phase 3 ✅
- [ ] `src/hooks/useSurveillance.ts` - 50 lines
- [ ] `src/hooks/useTeacherCharge.ts` - 45 lines
- [ ] `src/hooks/useDisponibilite.ts` - 60 lines
- [ ] `src/hooks/useConvocation.ts` - 45 lines

### Phase 4 ✅
- [ ] `src/components/ui/Button.tsx` - 45 lines
- [ ] `src/components/ui/Modal.tsx` - 40 lines
- [ ] `src/components/ui/AuthGuard.tsx` - 35 lines
- [ ] `src/components/ui/Layout.tsx` - 25 lines

### Phase 5 ✅
- [ ] `src/components/surveillance/ChargeTable.tsx` - 100 lines
- [ ] `src/components/surveillance/DisponibiliteForm.tsx` - 120 lines
- [ ] `src/components/surveillance/ConvocationCard.tsx` - 150 lines
- [ ] `src/components/surveillance/AffectationBoard.tsx` - 100 lines

### Phase 6 ✅
- [ ] `src/components/surveillance/ConvocationPDF.tsx` - 80 lines
- [ ] `src/hooks/usePDFExport.ts` - 25 lines

### Phase 7 ✅
- [ ] `src/app/(admin)/surveillance/page.tsx` - 100 lines
- [ ] `src/app/(admin)/surveillance/affectation/page.tsx` - 50 lines
- [ ] `src/app/(admin)/surveillance/charge/page.tsx` - 50 lines
- [ ] `src/app/(admin)/surveillance/[enseignant_id]/convocation/page.tsx` - 60 lines
- [ ] `src/app/(admin)/surveillance/[enseignant_id]/disponibilite/page.tsx` - 80 lines

**Total: ~1500 lines of code**

---

## **Quick Build & Test**

```bash
# 1. Build check
npm run build
# ✅ Should succeed (0 errors)

# 2. Type check
npx tsc --noEmit
# ✅ Should show 0 errors

# 3. Lint check
npm run lint
# ✅ Should show 0 errors

# 4. Start dev server
npm run dev
# ✅ http://localhost:3000

# 5. Navigate to pages
# - http://localhost:3000/app/(admin)/surveillance
# - http://localhost:3000/app/(admin)/surveillance/affectation
# - etc.

# 6. Test with browser devtools
# - Check Network tab for API calls
# - Check Console for errors
# - Test form submissions
```

---

## **Debugging Tips**

### If types don't match:

```typescript
// Check exact shape
type TestType = Surveillance;
// Hover over TestType to see full structure in VS Code
```

### If API calls fail:

```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS
# Frontend should allow backend origin in .env:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### If components don't render:

```typescript
// Add debug logging
console.log("Rendering component with props:", props);

// Check hook dependencies
// Open DevTools → React tab → Profiler
```

### If forms don't submit:

```typescript
// Check form validation
console.log("Form data:", formData);
console.log("Errors:", errors);

// Test API directly
fetch("http://localhost:8000/api/disponibilites", {
  method: "POST",
  body: JSON.stringify({ ... })
})
```

---

## **Common Mistakes to Avoid**

❌ **Don't forget `"use client"`** at top of page components

```typescript
// Wrong
export default function Page() { ... }

// Right
"use client";
export default function Page() { ... }
```

❌ **Don't forget to handle loading/error states**

```typescript
// Wrong
return <Component data={data} />

// Right
if (loading) return <Loading />;
if (error) return <Error message={error} />;
return <Component data={data} />;
```

❌ **Don't forget to clean up async operations**

```typescript
// Wrong
useEffect(() => {
  fetchData();
}, []);

// Right
useEffect(() => {
  const timer = setTimeout(() => {
    void fetchData();
  }, 0);
  return () => clearTimeout(timer);
}, []);
```

---

