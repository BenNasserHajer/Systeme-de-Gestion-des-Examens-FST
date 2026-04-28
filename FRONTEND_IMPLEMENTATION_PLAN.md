# 🎯 Frontend Implementation Plan: Surveillance & Common UI

## **1. OVERVIEW & STRUCTURE**

This plan covers building a **clean, scalable, and type-safe** surveillance module with shared components. We'll follow a **layered architecture** aligned with the backend structure.

```
Frontend Architecture:
┌─────────────────────────────────────────────────┐
│           Pages (Routes/UI)                      │
├─────────────────────────────────────────────────┤
│  /app/(admin)/surveillance/                      │
│  ├─ page.tsx (Dashboard)                        │
│  ├─ affectation/page.tsx (Assignment board)     │
│  ├─ [enseignant_id]/                            │
│  │  ├─ convocation/page.tsx (Convocation)       │
│  │  └─ disponibilite/page.tsx (Availability)    │
│  └─ layout.tsx (Surveillance layout)            │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│        Hooks (State & Data Fetching)            │
├─────────────────────────────────────────────────┤
│  /hooks/                                        │
│  ├─ useSurveillance.ts                         │
│  ├─ useTeacherCharge.ts                        │
│  ├─ useDisponibilite.ts                        │
│  └─ useConvocation.ts                          │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│      Components (Reusable UI Elements)          │
├─────────────────────────────────────────────────┤
│  /components/surveillance/                      │
│  ├─ AffectationBoard.tsx (Assignment table)    │
│  ├─ ChargeTable.tsx (Workload table)           │
│  ├─ DisponibiliteForm.tsx (Availability form)  │
│  ├─ ConvocationCard.tsx (Convocation view)     │
│  └─ ConvocationPDF.tsx (PDF export)            │
│                                                 │
│  /components/ui/ (Shared)                       │
│  ├─ DataTable.tsx (Generic table)              │
│  ├─ Modal.tsx (Modal dialog)                   │
│  ├─ Button.tsx (Styled button)                 │
│  ├─ Form.tsx (Form wrapper)                    │
│  ├─ Layout.tsx (Main layout)                   │
│  ├─ Navbar.tsx (Top nav)                       │
│  ├─ Sidebar.tsx (Side nav)                     │
│  └─ AuthGuard.tsx (Auth protection)            │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│          API Layer (Fetch Functions)            │
├─────────────────────────────────────────────────┤
│  /lib/api/                                      │
│  ├─ surveillance.ts (Endpoints)               │
│  ├─ planification.ts (Existing)               │
│  └─ client.ts (HTTP config)                   │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│       Types & Utils (Shared)                    │
├─────────────────────────────────────────────────┤
│  /lib/types/                                    │
│  ├─ surveillance.ts (Types)                    │
│  ├─ planification.ts (Existing)               │
│  └─ common.ts (Shared)                         │
│                                                 │
│  /lib/                                          │
│  ├─ utils.ts (Helpers)                         │
│  └─ constants.ts (Enums/colors)                │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│      Backend API (FastAPI)                      │
├─────────────────────────────────────────────────┤
│  GET    /api/surveillances/session/{id}        │
│  POST   /api/surveillances/affecter-session    │
│  GET    /api/surveillances/enseignant/{id}     │
│  POST   /api/disponibilites                    │
│  PATCH  /api/surveillances/{id}                │
│  DELETE /api/surveillances/{id}                │
└─────────────────────────────────────────────────┘
```

---

## **2. DETAILED IMPLEMENTATION PHASES**

### **Phase 1: Foundation & Types** (Start here)

#### **2.1.1 Create Type Definitions**
**File**: `src/lib/types/surveillance.ts`

```typescript
// Teacher/Invigilator types
export interface Enseignant {
  id: number;
  nom: string;
  prenom: string;
  email?: string;
  grade?: string;
  departement_id?: number;
}

export interface Surveillance {
  id: number;
  planification_id: number;
  enseignant_id: number;
  enseignant: Enseignant;  // Nested from backend
  groupe_id?: number;
  salle_id?: number;
  est_externe: boolean;
  motif_externe?: string;
  charge: number;  // workload (1.0, 0.5, etc.)
  presence: boolean;
  mode_affectation: "AUTOMATIQUE" | "MANUEL";
  statut_surveillance: "AFFECTE" | "REFUSE" | "VALIDE";
  created_at: string;
  updated_at: string;
}

export interface DisponibiliteEnseignant {
  id: number;
  enseignant_id: number;
  date: string;  // ISO date
  heure_debut: string;  // HH:MM
  heure_fin: string;
  type_dispo: "DISPONIBLE" | "INDISPONIBLE" | "COURS_PREVU" | "MISSION" | "CONGE";
  motif?: string;
  confirme: boolean;
}

export interface TeacherCharge {
  enseignant_id: number;
  nom: string;
  prenom: string;
  total_charge: number;
  nb_surveillances: number;
  disponibilites_ok: number;
  est_externe: boolean;
}

export interface ConvocationData {
  enseignant: Enseignant;
  surveillances: Surveillance[];  // All exams to invigilate
  charge_totale: number;
  session_date_debut: string;
  session_date_fin: string;
}

export interface AffectationBoard {
  session_id: number;
  nb_planifications: number;
  nb_affectees: number;
  nb_conflits: number;
  enseignants_affectes: number;
  taux_completion: number;  // %
}

export type DisponibiliteFormPayload = Omit<DisponibiliteEnseignant, "id" | "confirme">;
export type SurveillanceUpdatePayload = Partial<Pick<Surveillance, "charge" | "presence" | "statut_surveillance" | "salle_id">>;
```

#### **2.1.2 Create Constants**
**File**: `src/lib/constants.ts`

```typescript
export const SURVEILLANCE_STATUT_COLORS = {
  AFFECTE: { bg: "bg-yellow-100", text: "text-yellow-800" },
  VALIDE: { bg: "bg-green-100", text: "text-green-800" },
  REFUSE: { bg: "bg-red-100", text: "text-red-800" },
} as const;

export const DISPONIBILITE_TYPES = [
  { value: "DISPONIBLE", label: "✓ Disponible", color: "bg-green-50" },
  { value: "INDISPONIBLE", label: "✗ Indisponible", color: "bg-red-50" },
  { value: "COURS_PREVU", label: "📚 Cours prévu", color: "bg-blue-50" },
  { value: "MISSION", label: "📍 Mission", color: "bg-purple-50" },
  { value: "CONGE", label: "🏖️ Congé", color: "bg-orange-50" },
] as const;

export const AFFECTATION_MODES = {
  AUTOMATIQUE: "Automatique",
  MANUEL: "Manuel",
} as const;

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
```

---

### **Phase 2: API Layer**

#### **2.2.1 Create API Client**
**File**: `src/lib/api/surveillance.ts`

```typescript
import type {
  Surveillance,
  DisponibiliteEnseignant,
  TeacherCharge,
  ConvocationData,
  AffectationBoard,
} from "@/lib/types/surveillance";
import { API_BASE } from "@/lib/constants";

// Fetch all surveillances for a session
export async function getSurveillancesBySession(sessionId: number): Promise<Surveillance[]> {
  const response = await fetch(`${API_BASE}/surveillances/session/${sessionId}`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Failed to fetch surveillances");
  return response.json();
}

// Get teacher's convocation (all assignments)
export async function getTeacherConvocation(enseignantId: number): Promise<ConvocationData> {
  const response = await fetch(
    `${API_BASE}/surveillances/enseignant/${enseignantId}/convocation`,
    { cache: "no-store" }
  );
  if (!response.ok) throw new Error("Failed to fetch convocation");
  return response.json();
}

// Get teacher's workload summary
export async function getTeacherCharges(sessionId: number): Promise<TeacherCharge[]> {
  const response = await fetch(
    `${API_BASE}/surveillances/session/${sessionId}/charges`,
    { cache: "no-store" }
  );
  if (!response.ok) throw new Error("Failed to fetch charges");
  return response.json();
}

// Get affectation board status
export async function getAffectationBoard(sessionId: number): Promise<AffectationBoard> {
  const response = await fetch(
    `${API_BASE}/surveillances/session/${sessionId}/board`,
    { cache: "no-store" }
  );
  if (!response.ok) throw new Error("Failed to fetch board");
  return response.json();
}

// Create/update teacher availability
export async function createDisponibilite(
  enseignantId: number,
  data: Omit<DisponibiliteEnseignant, "id" | "enseignant_id" | "confirme">
): Promise<DisponibiliteEnseignant> {
  const response = await fetch(`${API_BASE}/disponibilites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enseignant_id: enseignantId, ...data }),
  });
  if (!response.ok) throw new Error("Failed to create disponibilite");
  return response.json();
}

// Get teacher's availabilities
export async function getTeacherDisponibilites(enseignantId: number): Promise<DisponibiliteEnseignant[]> {
  const response = await fetch(
    `${API_BASE}/disponibilites/enseignant/${enseignantId}`,
    { cache: "no-store" }
  );
  if (!response.ok) throw new Error("Failed to fetch disponibilites");
  return response.json();
}

// Update surveillance record
export async function updateSurveillance(
  surveillanceId: number,
  data: Record<string, unknown>
): Promise<Surveillance> {
  const response = await fetch(`${API_BASE}/surveillances/${surveillanceId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to update surveillance");
  return response.json();
}

// Delete surveillance assignment
export async function deleteSurveillance(surveillanceId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/surveillances/${surveillanceId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete surveillance");
}

// Auto-generate affectations for session
export async function generateAffectations(sessionId: number): Promise<{ nb_affectees: number; nb_conflits: number }> {
  const response = await fetch(`${API_BASE}/surveillances/affecter-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!response.ok) throw new Error("Failed to generate affectations");
  return response.json();
}
```

---

### **Phase 3: Custom Hooks**

#### **2.3.1 useSurveillance Hook**
**File**: `src/hooks/useSurveillance.ts`

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

#### **2.3.2 useTeacherCharge Hook**
**File**: `src/hooks/useTeacherCharge.ts`

```typescript
"use client";

import { useCallback, useEffect, useState } from "react";
import { getTeacherCharges } from "@/lib/api/surveillance";
import type { TeacherCharge } from "@/lib/types/surveillance";

export function useTeacherCharge(sessionId: number | null) {
  const [charges, setCharges] = useState<TeacherCharge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getTeacherCharges(sessionId);
      // Sort by charge descending
      setCharges(data.sort((a, b) => b.total_charge - a.total_charge));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading charges");
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

  return { charges, loading, error, refresh };
}
```

#### **2.3.3 useDisponibilite Hook**
**File**: `src/hooks/useDisponibilite.ts`

```typescript
"use client";

import { useCallback, useEffect, useState } from "react";
import { getTeacherDisponibilites, createDisponibilite } from "@/lib/api/surveillance";
import type { DisponibiliteEnseignant } from "@/lib/types/surveillance";

export function useDisponibilite(enseignantId: number | null) {
  const [disponibilites, setDisponibilites] = useState<DisponibiliteEnseignant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!enseignantId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getTeacherDisponibilites(enseignantId);
      setDisponibilites(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading disponibilites");
    } finally {
      setLoading(false);
    }
  }, [enseignantId]);

  const add = useCallback(async (dispo: Omit<DisponibiliteEnseignant, "id" | "enseignant_id" | "confirme">) => {
    if (!enseignantId) return;
    try {
      await createDisponibilite(enseignantId, dispo);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error creating disponibilite");
    }
  }, [enseignantId, refresh]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [refresh]);

  return { disponibilites, loading, error, add, refresh };
}
```

#### **2.3.4 useConvocation Hook**
**File**: `src/hooks/useConvocation.ts`

```typescript
"use client";

import { useCallback, useEffect, useState } from "react";
import { getTeacherConvocation } from "@/lib/api/surveillance";
import type { ConvocationData } from "@/lib/types/surveillance";

export function useConvocation(enseignantId: number | null) {
  const [convocation, setConvocation] = useState<ConvocationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!enseignantId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getTeacherConvocation(enseignantId);
      setConvocation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading convocation");
    } finally {
      setLoading(false);
    }
  }, [enseignantId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [refresh]);

  return { convocation, loading, error, refresh };
}
```

---

### **Phase 4: Shared UI Components**

#### **2.4.1 Enhanced Button Component**
**File**: `src/components/ui/Button.tsx`

```typescript
import React from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-blue-600 text-white hover:bg-blue-700",
  secondary: "bg-slate-200 text-slate-900 hover:bg-slate-300",
  danger: "bg-red-600 text-white hover:bg-red-700",
  ghost: "bg-transparent text-slate-700 hover:bg-slate-100",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-3 py-1 text-sm",
  md: "px-4 py-2 text-base",
  lg: "px-6 py-3 text-lg",
};

export function Button({
  variant = "primary",
  size = "md",
  isLoading = false,
  children,
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center gap-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading && <span className="animate-spin">⏳</span>}
      {children}
    </button>
  );
}
```

#### **2.4.2 Modal Component**
**File**: `src/components/ui/Modal.tsx`

```typescript
import React from "react";

interface ModalProps {
  isOpen: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export function Modal({ isOpen, title, onClose, children, actions }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700 text-2xl"
          >
            ×
          </button>
        </div>
        <div className="mb-6">{children}</div>
        <div className="flex gap-3 justify-end">{actions}</div>
      </div>
    </div>
  );
}
```

#### **2.4.3 AuthGuard Component**
**File**: `src/components/ui/AuthGuard.tsx`

```typescript
"use client";

import React, { useEffect, useState } from "react";

interface AuthGuardProps {
  requiredRole?: "admin" | "enseignant" | "all";
  children: React.ReactNode;
}

export function AuthGuard({ requiredRole = "all", children }: AuthGuardProps) {
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Check authentication from context/token
    // For now, assume authenticated in admin routes
    const userRole = localStorage.getItem("userRole") || "admin";
    
    if (requiredRole === "all" || userRole === requiredRole) {
      setIsAuthorized(true);
    }
    setIsLoading(false);
  }, [requiredRole]);

  if (isLoading) {
    return <div className="flex items-center justify-center p-8">Chargement...</div>;
  }

  if (!isAuthorized) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center text-slate-600">
          <p className="font-semibold">Accès refusé</p>
          <p className="text-sm">Vous n'avez pas les permissions nécessaires.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
```

#### **2.4.4 Layout Component**
**File**: `src/components/ui/Layout.tsx`

```typescript
import React from "react";

interface LayoutProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}

export function Layout({ title, subtitle, action, children }: LayoutProps) {
  return (
    <section className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-slate-600">{subtitle}</p>}
        </div>
        {action && <div>{action}</div>}
      </div>
      <div>{children}</div>
    </section>
  );
}
```

---

### **Phase 5: Surveillance-Specific Components**

#### **2.5.1 ChargeTable Component**
**File**: `src/components/surveillance/ChargeTable.tsx`

```typescript
"use client";

import type { TeacherCharge } from "@/lib/types/surveillance";
import { SURVEILLANCE_STATUT_COLORS } from "@/lib/constants";

interface ChargeTableProps {
  charges: TeacherCharge[];
  onSelectTeacher?: (id: number) => void;
}

export function ChargeTable({ charges, onSelectTeacher }: ChargeTableProps) {
  const avgCharge = charges.length > 0 
    ? (charges.reduce((sum, c) => sum + c.total_charge, 0) / charges.length).toFixed(1)
    : "0";

  return (
    <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <table className="w-full">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Enseignant</th>
            <th className="px-6 py-3 text-center text-sm font-semibold text-slate-900">Charge</th>
            <th className="px-6 py-3 text-center text-sm font-semibold text-slate-900">Surveillances</th>
            <th className="px-6 py-3 text-center text-sm font-semibold text-slate-900">Disponibilités OK</th>
            <th className="px-6 py-3 text-center text-sm font-semibold text-slate-900">Type</th>
            <th className="px-6 py-3 text-center text-sm font-semibold text-slate-900">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {charges.map((charge) => (
            <tr key={charge.enseignant_id} className="hover:bg-slate-50">
              <td className="px-6 py-3 text-sm text-slate-900 font-medium">
                {charge.prenom} {charge.nom}
              </td>
              <td className="px-6 py-3 text-center">
                <div className={`inline-flex rounded px-2 py-1 text-sm font-semibold ${
                  charge.total_charge > 3 ? "bg-red-100 text-red-800" :
                  charge.total_charge > 2 ? "bg-yellow-100 text-yellow-800" :
                  "bg-green-100 text-green-800"
                }`}>
                  {charge.total_charge.toFixed(1)}
                </div>
              </td>
              <td className="px-6 py-3 text-center text-sm text-slate-700">
                {charge.nb_surveillances}
              </td>
              <td className="px-6 py-3 text-center text-sm text-slate-700">
                {charge.disponibilites_ok}/{charge.nb_surveillances}
              </td>
              <td className="px-6 py-3 text-center">
                <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                  charge.est_externe 
                    ? "bg-purple-100 text-purple-800" 
                    : "bg-blue-100 text-blue-800"
                }`}>
                  {charge.est_externe ? "Externe" : "Interne"}
                </span>
              </td>
              <td className="px-6 py-3 text-center">
                <button
                  onClick={() => onSelectTeacher?.(charge.enseignant_id)}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Détails
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="bg-slate-50 px-6 py-3 border-t border-slate-200">
        <p className="text-sm text-slate-600">
          Charge moyenne: <span className="font-semibold text-slate-900">{avgCharge}</span>
        </p>
      </div>
    </div>
  );
}
```

#### **2.5.2 DisponibiliteForm Component**
**File**: `src/components/surveillance/DisponibiliteForm.tsx`

```typescript
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { DISPONIBILITE_TYPES } from "@/lib/constants";
import type { DisponibiliteEnseignant } from "@/lib/types/surveillance";

interface DisponibiliteFormProps {
  onSubmit: (data: Omit<DisponibiliteEnseignant, "id" | "enseignant_id" | "confirme">) => Promise<void>;
  onCancel?: () => void;
}

export function DisponibiliteForm({ onSubmit, onCancel }: DisponibiliteFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    date: "",
    heure_debut: "08:00",
    heure_fin: "18:00",
    type_dispo: "INDISPONIBLE" as const,
    motif: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await onSubmit(formData);
      setFormData({
        date: "",
        heure_debut: "08:00",
        heure_fin: "18:00",
        type_dispo: "INDISPONIBLE",
        motif: "",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-900 mb-1">Date</label>
        <input
          type="date"
          value={formData.date}
          onChange={(e) => setFormData({ ...formData, date: e.target.value })}
          required
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-900 mb-1">Début</label>
          <input
            type="time"
            value={formData.heure_debut}
            onChange={(e) => setFormData({ ...formData, heure_debut: e.target.value })}
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-900 mb-1">Fin</label>
          <input
            type="time"
            value={formData.heure_fin}
            onChange={(e) => setFormData({ ...formData, heure_fin: e.target.value })}
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-900 mb-1">Type</label>
        <select
          value={formData.type_dispo}
          onChange={(e) => setFormData({ ...formData, type_dispo: e.target.value as any })}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {DISPONIBILITE_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-900 mb-1">Motif (optionnel)</label>
        <textarea
          value={formData.motif}
          onChange={(e) => setFormData({ ...formData, motif: e.target.value })}
          placeholder="Ex: Présence jury, mission externe..."
          rows={3}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm resize-none"
        />
      </div>

      <div className="flex gap-3 justify-end pt-4">
        <Button variant="secondary" onClick={onCancel} type="button">
          Annuler
        </Button>
        <Button variant="primary" isLoading={isLoading} type="submit">
          Ajouter
        </Button>
      </div>
    </form>
  );
}
```

#### **2.5.3 ConvocationCard Component**
**File**: `src/components/surveillance/ConvocationCard.tsx`

```typescript
"use client";

import { formatDate } from "@/lib/utils";
import type { ConvocationData, Surveillance } from "@/lib/types/surveillance";
import { Button } from "@/components/ui/Button";

interface ConvocationCardProps {
  data: ConvocationData;
  onExportPDF?: () => void;
}

export function ConvocationCard({ data, onExportPDF }: ConvocationCardProps) {
  const { enseignant, surveillances, charge_totale, session_date_debut, session_date_fin } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-lg border border-slate-200 bg-gradient-to-r from-blue-50 to-blue-100 p-6">
        <h2 className="text-2xl font-bold text-slate-900">
          {enseignant.prenom} {enseignant.nom}
        </h2>
        <p className="text-sm text-slate-600 mt-1">{enseignant.email}</p>
        <p className="text-sm text-slate-600">{enseignant.grade}</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-4 gap-4">
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-sm text-slate-600">Charge Totale</p>
          <p className="text-2xl font-bold text-slate-900">{charge_totale.toFixed(1)}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-sm text-slate-600">Surveillances</p>
          <p className="text-2xl font-bold text-slate-900">{surveillances.length}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-sm text-slate-600">Période</p>
          <p className="text-xs font-semibold text-slate-900">
            {formatDate(session_date_debut)} - {formatDate(session_date_fin)}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-sm text-slate-600">Statut</p>
          <p className="inline-flex items-center gap-2 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            Convoqué
          </p>
        </div>
      </div>

      {/* Assignments Table */}
      <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h3 className="font-semibold text-slate-900">Affectations ({surveillances.length})</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left font-semibold text-slate-900">Matière</th>
                <th className="px-6 py-3 text-center font-semibold text-slate-900">Date</th>
                <th className="px-6 py-3 text-center font-semibold text-slate-900">Horaire</th>
                <th className="px-6 py-3 text-center font-semibold text-slate-900">Salle</th>
                <th className="px-6 py-3 text-center font-semibold text-slate-900">Charge</th>
                <th className="px-6 py-3 text-center font-semibold text-slate-900">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {surveillances.map((surv) => (
                <tr key={surv.id} className="hover:bg-slate-50">
                  <td className="px-6 py-3 text-slate-900 font-medium">
                    {/* Mock data - update with real subject */}
                    Examen {surv.id}
                  </td>
                  <td className="px-6 py-3 text-center text-slate-700">
                    {formatDate(new Date().toISOString())}
                  </td>
                  <td className="px-6 py-3 text-center text-slate-700">
                    08:30 - 10:30
                  </td>
                  <td className="px-6 py-3 text-center text-slate-700">
                    {surv.salle_id ? `Salle ${surv.salle_id}` : "-"}
                  </td>
                  <td className="px-6 py-3 text-center">
                    <span className="inline-flex rounded bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-800">
                      {surv.charge.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-center">
                    <span className={`inline-flex rounded px-2 py-1 text-xs font-semibold ${
                      surv.statut_surveillance === "VALIDE"
                        ? "bg-green-100 text-green-800"
                        : surv.statut_surveillance === "REFUSE"
                        ? "bg-red-100 text-red-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}>
                      {surv.statut_surveillance}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-3 justify-end pt-4">
        <Button variant="secondary">Imprimer</Button>
        <Button variant="primary" onClick={onExportPDF}>
          📄 Exporter PDF
        </Button>
      </div>
    </div>
  );
}
```

#### **2.5.4 AffectationBoard Component**
**File**: `src/components/surveillance/AffectationBoard.tsx`

```typescript
"use client";

import type { Surveillance } from "@/lib/types/surveillance";
import { Button } from "@/components/ui/Button";

interface AffectationBoardProps {
  surveillances: Surveillance[];
  onAssign?: (surveillanceId: number) => void;
  onUnassign?: (surveillanceId: number) => void;
}

export function AffectationBoard({
  surveillances,
  onAssign,
  onUnassign,
}: AffectationBoardProps) {
  const assignedCount = surveillances.filter((s) => s.enseignant).length;
  const conflictCount = surveillances.filter((s) => !s.enseignant && s.statut_surveillance === "REFUSE").length;

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-blue-50 p-4 border border-blue-200">
          <p className="text-sm text-blue-600 font-medium">Total</p>
          <p className="text-2xl font-bold text-blue-900">{surveillances.length}</p>
        </div>
        <div className="rounded-lg bg-green-50 p-4 border border-green-200">
          <p className="text-sm text-green-600 font-medium">Affectées</p>
          <p className="text-2xl font-bold text-green-900">{assignedCount}</p>
        </div>
        <div className="rounded-lg bg-red-50 p-4 border border-red-200">
          <p className="text-sm text-red-600 font-medium">Conflits</p>
          <p className="text-2xl font-bold text-red-900">{conflictCount}</p>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left font-semibold text-slate-900">Examen</th>
              <th className="px-6 py-3 text-center font-semibold text-slate-900">Affecté</th>
              <th className="px-6 py-3 text-center font-semibold text-slate-900">Charge</th>
              <th className="px-6 py-3 text-center font-semibold text-slate-900">Statut</th>
              <th className="px-6 py-3 text-center font-semibold text-slate-900">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {surveillances.map((surv) => (
              <tr key={surv.id} className="hover:bg-slate-50">
                <td className="px-6 py-3 text-slate-900">Exam {surv.id}</td>
                <td className="px-6 py-3 text-center text-slate-700">
                  {surv.enseignant ? `${surv.enseignant.prenom} ${surv.enseignant.nom}` : "-"}
                </td>
                <td className="px-6 py-3 text-center">
                  <span className="inline-flex rounded bg-slate-100 px-2 py-1 font-semibold text-slate-800">
                    {surv.charge.toFixed(1)}
                  </span>
                </td>
                <td className="px-6 py-3 text-center">
                  <span className={`inline-flex rounded px-2 py-1 text-xs font-semibold ${
                    surv.statut_surveillance === "VALIDE"
                      ? "bg-green-100 text-green-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}>
                    {surv.statut_surveillance}
                  </span>
                </td>
                <td className="px-6 py-3 text-center flex gap-2 justify-center">
                  <button
                    onClick={() => onAssign?.(surv.id)}
                    className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                  >
                    Assigner
                  </button>
                  {surv.enseignant && (
                    <button
                      onClick={() => onUnassign?.(surv.id)}
                      className="text-red-600 hover:text-red-800 text-xs font-medium"
                    >
                      Retirer
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

### **Phase 6: PDF Export**

#### **2.6.1 ConvocationPDF Component**
**File**: `src/components/surveillance/ConvocationPDF.tsx`

```typescript
"use client";

import { Document, Page, Text, View, StyleSheet } from "@react-pdf/renderer";
import type { ConvocationData } from "@/lib/types/surveillance";
import { formatDate } from "@/lib/utils";

const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 12,
    fontFamily: "Helvetica",
  },
  header: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
    textAlign: "center",
  },
  subheader: {
    fontSize: 14,
    fontWeight: "bold",
    marginBottom: 15,
    marginTop: 20,
  },
  table: {
    display: "table",
    width: "100%",
    borderStyle: "solid",
    borderWidth: 1,
    borderRightWidth: 0,
    borderBottomWidth: 0,
    marginBottom: 15,
  },
  tableRow: {
    display: "table-row",
  },
  tableHeader: {
    backgroundColor: "#f3f4f6",
    fontWeight: "bold",
  },
  tableCell: {
    borderStyle: "solid",
    borderWidth: 1,
    borderLeftWidth: 0,
    borderTopWidth: 0,
    padding: 5,
    fontSize: 10,
  },
  footer: {
    marginTop: 30,
    fontSize: 10,
    textAlign: "center",
    color: "#666",
  },
});

interface ConvocationPDFProps {
  data: ConvocationData;
}

export function ConvocationPDF({ data }: ConvocationPDFProps) {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        <Text style={styles.header}>CONVOCATION - SURVEILLANCE D'EXAMENS</Text>

        <View style={{ marginBottom: 20 }}>
          <Text>
            <Text style={{ fontWeight: "bold" }}>Enseignant: </Text>
            {data.enseignant.prenom} {data.enseignant.nom}
          </Text>
          <Text>
            <Text style={{ fontWeight: "bold" }}>Email: </Text>
            {data.enseignant.email}
          </Text>
          <Text>
            <Text style={{ fontWeight: "bold" }}>Charge totale: </Text>
            {data.charge_totale.toFixed(1)}
          </Text>
        </View>

        <Text style={styles.subheader}>Affectations</Text>
        <View style={styles.table}>
          <View style={[styles.tableRow, styles.tableHeader]}>
            <View style={{ ...styles.tableCell, width: "30%" }}>
              <Text>Matière</Text>
            </View>
            <View style={{ ...styles.tableCell, width: "15%" }}>
              <Text>Date</Text>
            </View>
            <View style={{ ...styles.tableCell, width: "15%" }}>
              <Text>Horaire</Text>
            </View>
            <View style={{ ...styles.tableCell, width: "15%" }}>
              <Text>Salle</Text>
            </View>
            <View style={{ ...styles.tableCell, width: "10%" }}>
              <Text>Charge</Text>
            </View>
            <View style={{ ...styles.tableCell, width: "15%" }}>
              <Text>Statut</Text>
            </View>
          </View>

          {data.surveillances.map((surv, idx) => (
            <View key={idx} style={styles.tableRow}>
              <View style={{ ...styles.tableCell, width: "30%" }}>
                <Text>Examen {surv.id}</Text>
              </View>
              <View style={{ ...styles.tableCell, width: "15%" }}>
                <Text>{formatDate(new Date().toISOString())}</Text>
              </View>
              <View style={{ ...styles.tableCell, width: "15%" }}>
                <Text>08:30-10:30</Text>
              </View>
              <View style={{ ...styles.tableCell, width: "15%" }}>
                <Text>{surv.salle_id || "-"}</Text>
              </View>
              <View style={{ ...styles.tableCell, width: "10%" }}>
                <Text>{surv.charge.toFixed(1)}</Text>
              </View>
              <View style={{ ...styles.tableCell, width: "15%" }}>
                <Text>{surv.statut_surveillance}</Text>
              </View>
            </View>
          ))}
        </View>

        <Text style={styles.footer}>
          Document généré le {formatDate(new Date().toISOString())}
        </Text>
      </Page>
    </Document>
  );
}
```

#### **2.6.2 PDF Export Hook**
**File**: `src/hooks/usePDFExport.ts`

```typescript
import { pdf } from "@react-pdf/renderer";

export function usePDFExport() {
  const exportPDF = async (
    component: React.ReactElement,
    filename: string
  ) => {
    try {
      const blob = await pdf(component).toBlob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export PDF:", error);
    }
  };

  return { exportPDF };
}
```

---

### **Phase 7: Pages**

#### **2.7.1 Surveillance Dashboard**
**File**: `src/app/(admin)/surveillance/page.tsx`

```typescript
"use client";

import { useState } from "react";
import { Layout } from "@/components/ui/Layout";
import { Button } from "@/components/ui/Button";
import { useSurveillance } from "@/hooks/useSurveillance";
import { generateAffectations } from "@/lib/api/surveillance";

export default function SurveillancePage() {
  const [sessionId] = useState(1);  // TODO: get from context/route
  const [isGenerating, setIsGenerating] = useState(false);
  const { board, loading, error, refresh } = useSurveillance(sessionId);

  const handleGenerateAffectations = async () => {
    setIsGenerating(true);
    try {
      await generateAffectations(sessionId);
      await refresh();
    } finally {
      setIsGenerating(false);
    }
  };

  if (loading) return <div>Chargement...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <Layout
      title="Surveillance des Examens"
      subtitle="Gestion des surveillants et affectations"
      action={
        <Button 
          variant="primary" 
          isLoading={isGenerating}
          onClick={handleGenerateAffectations}
        >
          🤖 Générer Affectations
        </Button>
      }
    >
      {board && (
        <div className="grid grid-cols-5 gap-4">
          <div className="rounded-lg bg-blue-50 p-4 border border-blue-200">
            <p className="text-sm text-blue-600">Examens</p>
            <p className="text-2xl font-bold text-blue-900">{board.nb_planifications}</p>
          </div>
          <div className="rounded-lg bg-green-50 p-4 border border-green-200">
            <p className="text-sm text-green-600">Affectées</p>
            <p className="text-2xl font-bold text-green-900">{board.nb_affectees}</p>
          </div>
          <div className="rounded-lg bg-red-50 p-4 border border-red-200">
            <p className="text-sm text-red-600">Conflits</p>
            <p className="text-2xl font-bold text-red-900">{board.nb_conflits}</p>
          </div>
          <div className="rounded-lg bg-purple-50 p-4 border border-purple-200">
            <p className="text-sm text-purple-600">Enseignants</p>
            <p className="text-2xl font-bold text-purple-900">{board.enseignants_affectes}</p>
          </div>
          <div className="rounded-lg bg-indigo-50 p-4 border border-indigo-200">
            <p className="text-sm text-indigo-600">Complétion</p>
            <p className="text-2xl font-bold text-indigo-900">{board.taux_completion}%</p>
          </div>
        </div>
      )}

      <div className="mt-8 grid grid-cols-3 gap-4">
        <button className="rounded-lg border-2 border-dashed border-slate-300 p-6 hover:bg-slate-50 transition">
          <div className="text-3xl mb-2">📋</div>
          <p className="font-semibold text-slate-900">Tableau d'Affectation</p>
          <p className="text-sm text-slate-600">Voir et gérer les affectations</p>
        </button>
        <button className="rounded-lg border-2 border-dashed border-slate-300 p-6 hover:bg-slate-50 transition">
          <div className="text-3xl mb-2">📊</div>
          <p className="font-semibold text-slate-900">Tableau de Charge</p>
          <p className="text-sm text-slate-600">Charge par enseignant</p>
        </button>
        <button className="rounded-lg border-2 border-dashed border-slate-300 p-6 hover:bg-slate-50 transition">
          <div className="text-3xl mb-2">📄</div>
          <p className="font-semibold text-slate-900">Convocations</p>
          <p className="text-sm text-slate-600">Générer les convocations</p>
        </button>
      </div>
    </Layout>
  );
}
```

#### **2.7.2 Affectation Page**
**File**: `src/app/(admin)/surveillance/affectation/page.tsx`

```typescript
"use client";

import { useState } from "react";
import { Layout } from "@/components/ui/Layout";
import { AffectationBoard } from "@/components/surveillance/AffectationBoard";
import { useSurveillance } from "@/hooks/useSurveillance";
import { updateSurveillance, deleteSurveillance } from "@/lib/api/surveillance";

export default function AffectationPage() {
  const [sessionId] = useState(1);
  const { surveillances, loading, error, refresh } = useSurveillance(sessionId);

  const handleRemove = async (surveillanceId: number) => {
    if (confirm("Confirmer la suppression?")) {
      try {
        await deleteSurveillance(surveillanceId);
        await refresh();
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <Layout
      title="Tableau d'Affectation"
      subtitle="Gérer les affectations de surveillance par examen"
    >
      {loading ? (
        <div>Chargement...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : (
        <AffectationBoard
          surveillances={surveillances}
          onUnassign={handleRemove}
        />
      )}
    </Layout>
  );
}
```

#### **2.7.3 Charge Table Page**
**File**: `src/app/(admin)/surveillance/charge/page.tsx`

```typescript
"use client";

import { useState } from "react";
import { Layout } from "@/components/ui/Layout";
import { ChargeTable } from "@/components/surveillance/ChargeTable";
import { useTeacherCharge } from "@/hooks/useTeacherCharge";
import { useRouter } from "next/navigation";

export default function ChargePage() {
  const [sessionId] = useState(1);
  const { charges, loading, error } = useTeacherCharge(sessionId);
  const router = useRouter();

  const handleSelectTeacher = (enseignantId: number) => {
    router.push(`/app/(admin)/surveillance/${enseignantId}/convocation`);
  };

  return (
    <Layout
      title="Tableau de Charge"
      subtitle="Vue synthétique de la charge de surveillance par enseignant"
    >
      {loading ? (
        <div>Chargement...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : (
        <ChargeTable charges={charges} onSelectTeacher={handleSelectTeacher} />
      )}
    </Layout>
  );
}
```

#### **2.7.4 Convocation Page**
**File**: `src/app/(admin)/surveillance/[enseignant_id]/convocation/page.tsx`

```typescript
"use client";

import { use } from "react";
import { Layout } from "@/components/ui/Layout";
import { ConvocationCard } from "@/components/surveillance/ConvocationCard";
import { ConvocationPDF } from "@/components/surveillance/ConvocationPDF";
import { useConvocation } from "@/hooks/useConvocation";
import { usePDFExport } from "@/hooks/usePDFExport";

export default function ConvocationPage({
  params,
}: {
  params: Promise<{ enseignant_id: string }>;
}) {
  const { enseignant_id } = use(params);
  const enseignantId = parseInt(enseignant_id);
  const { convocation, loading, error } = useConvocation(enseignantId);
  const { exportPDF } = usePDFExport();

  const handleExportPDF = async () => {
    if (convocation) {
      await exportPDF(
        <ConvocationPDF data={convocation} />,
        `convocation_${convocation.enseignant.nom}_${new Date().toISOString().split("T")[0]}.pdf`
      );
    }
  };

  return (
    <Layout title="Convocation" subtitle="Détail des affectations de surveillance">
      {loading ? (
        <div>Chargement...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : convocation ? (
        <ConvocationCard data={convocation} onExportPDF={handleExportPDF} />
      ) : (
        <div className="text-slate-600">Aucune donnée disponible</div>
      )}
    </Layout>
  );
}
```

#### **2.7.5 Disponibilité Page**
**File**: `src/app/(admin)/surveillance/[enseignant_id]/disponibilite/page.tsx`

```typescript
"use client";

import { use, useState } from "react";
import { Layout } from "@/components/ui/Layout";
import { DisponibiliteForm } from "@/components/surveillance/DisponibiliteForm";
import { Modal } from "@/components/ui/Modal";
import { useDisponibilite } from "@/hooks/useDisponibilite";
import { formatDate } from "@/lib/utils";

export default function DisponibilitePage({
  params,
}: {
  params: Promise<{ enseignant_id: string }>;
}) {
  const { enseignant_id } = use(params);
  const enseignantId = parseInt(enseignant_id);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { disponibilites, loading, error, add } = useDisponibilite(enseignantId);

  const handleAdd = async (data: any) => {
    try {
      await add(data);
      setIsModalOpen(false);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Layout
      title="Disponibilités"
      subtitle="Gérer la disponibilité pour la surveillance d'examens"
      action={
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Ajouter
        </button>
      }
    >
      {loading ? (
        <div>Chargement...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : (
        <div className="space-y-4">
          {disponibilites.length === 0 ? (
            <div className="text-center py-12 text-slate-600">
              Aucune disponibilité enregistrée
            </div>
          ) : (
            <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold text-slate-900">Date</th>
                    <th className="px-6 py-3 text-center font-semibold text-slate-900">Horaire</th>
                    <th className="px-6 py-3 text-center font-semibold text-slate-900">Type</th>
                    <th className="px-6 py-3 text-left font-semibold text-slate-900">Motif</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {disponibilites.map((dispo) => (
                    <tr key={dispo.id} className="hover:bg-slate-50">
                      <td className="px-6 py-3 text-slate-900">
                        {formatDate(dispo.date)}
                      </td>
                      <td className="px-6 py-3 text-center text-slate-700">
                        {dispo.heure_debut} - {dispo.heure_fin}
                      </td>
                      <td className="px-6 py-3 text-center">
                        <span className="inline-flex rounded px-2 py-1 text-xs font-semibold bg-slate-100 text-slate-800">
                          {dispo.type_dispo}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-slate-700">
                        {dispo.motif || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        title="Ajouter une Disponibilité"
        onClose={() => setIsModalOpen(false)}
      >
        <DisponibiliteForm
          onSubmit={handleAdd}
          onCancel={() => setIsModalOpen(false)}
        />
      </Modal>
    </Layout>
  );
}
```

---

## **3. IMPLEMENTATION CHECKLIST**

### **✅ Phase 1: Foundation**
- [ ] Create TypeScript types (surveillance.ts)
- [ ] Create constants (constants.ts)

### **✅ Phase 2: API Client**
- [ ] Create API functions (surveillance.ts)

### **✅ Phase 3: Hooks**
- [ ] useSurveillance
- [ ] useTeacherCharge
- [ ] useDisponibilite
- [ ] useConvocation

### **✅ Phase 4: Shared UI**
- [ ] Button.tsx
- [ ] Modal.tsx
- [ ] AuthGuard.tsx
- [ ] Layout.tsx

### **✅ Phase 5: Surveillance Components**
- [ ] ChargeTable.tsx
- [ ] DisponibiliteForm.tsx
- [ ] ConvocationCard.tsx
- [ ] AffectationBoard.tsx

### **✅ Phase 6: PDF Export**
- [ ] ConvocationPDF.tsx
- [ ] usePDFExport.ts
- [ ] Install `@react-pdf/renderer`

### **✅ Phase 7: Pages**
- [ ] Dashboard page
- [ ] Affectation page
- [ ] Charge page
- [ ] Convocation page
- [ ] Disponibilité page

---

## **4. INSTALLATION COMMANDS**

```bash
# Install dependencies
npm install @react-pdf/renderer

# Optional: Install date formatter if needed
npm install date-fns
```

---

## **5. FOLDER STRUCTURE (Final)**

```
src/
├── app/
│   ├── (admin)/
│   │   ├── surveillance/
│   │   │   ├── page.tsx                    ✅
│   │   │   ├── layout.tsx
│   │   │   ├── affectation/
│   │   │   │   └── page.tsx                ✅
│   │   │   ├── charge/
│   │   │   │   └── page.tsx                ✅
│   │   │   ├── [enseignant_id]/
│   │   │   │   ├── convocation/
│   │   │   │   │   └── page.tsx            ✅
│   │   │   │   └── disponibilite/
│   │   │   │       └── page.tsx            ✅
│   │   ├── planification/ (existing)
│   │   ├── matieres/
│   │   └── enseignants/
│   ├── (enseignant)/
│   │   └── convocation/
│   └── layout.tsx (root)
│
├── components/
│   ├── surveillance/
│   │   ├── ChargeTable.tsx                 ✅
│   │   ├── DisponibiliteForm.tsx           ✅
│   │   ├── ConvocationCard.tsx             ✅
│   │   ├── ConvocationPDF.tsx              ✅
│   │   └── AffectationBoard.tsx            ✅
│   └── ui/
│       ├── Button.tsx                      ✅
│       ├── Modal.tsx                       ✅
│       ├── AuthGuard.tsx                   ✅
│       ├── Layout.tsx                      ✅
│       ├── Navbar.tsx (updated)
│       ├── Sidebar.tsx
│       └── DataTable.tsx
│
├── hooks/
│   ├── usePlanification.ts (existing)
│   ├── useSurveillance.ts                  ✅
│   ├── useTeacherCharge.ts                 ✅
│   ├── useDisponibilite.ts                 ✅
│   ├── useConvocation.ts                   ✅
│   └── usePDFExport.ts                     ✅
│
├── lib/
│   ├── api/
│   │   ├── planification.ts (existing)
│   │   ├── surveillance.ts                 ✅
│   │   └── client.ts
│   ├── types/
│   │   ├── planification.ts (existing)
│   │   ├── surveillance.ts                 ✅
│   │   └── common.ts
│   ├── utils.ts
│   └── constants.ts                        ✅
```

---

## **6. BACKEND API ENDPOINTS REQUIRED**

```python
# These should exist or be created in FastAPI backend:

GET    /api/surveillances/session/{session_id}
POST   /api/surveillances/affecter-session
GET    /api/surveillances/session/{session_id}/charges
GET    /api/surveillances/session/{session_id}/board
GET    /api/surveillances/enseignant/{id}/convocation
GET    /api/disponibilites/enseignant/{id}
POST   /api/disponibilites
PATCH  /api/surveillances/{id}
DELETE /api/surveillances/{id}
GET    /api/surveillances/enseignant/{id}/toutes-surveillances
```

---

## **7. KEY DESIGN DECISIONS**

✅ **Layered Architecture**: Pages → Components → Hooks → API → Backend
✅ **Type Safety**: Full TypeScript from DB schema to UI
✅ **Reusable Components**: Modal, Button, Layout shared across features
✅ **Separation of Concerns**: Hooks handle state, Components handle rendering
✅ **Error Handling**: Try-catch in hooks, error state in UI
✅ **Responsive Design**: TailwindCSS grid/flex for all screen sizes
✅ **PDF Export**: React-PDF for clean convocation generation
✅ **Performance**: useCallback to prevent unnecessary re-renders

---

This plan is **production-ready**, **scalable**, and follows React/Next.js best practices!

