"use client";

import { ConvocationCard } from "@/components/surveillance/ConvocationCard";
import { DisponibiliteForm } from "@/components/surveillance/DisponibiliteForm";

export default function ConvocationPage() {
  return (
    <section className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-900">Convocation Enseignant</h2>
      <ConvocationCard
        enseignant="Nom Enseignant"
        matiere="Big Data"
        salle="AMPHI INFO"
        date="2026-01-12 08:30"
      />
      <DisponibiliteForm
        onSubmit={(payload) => {
          console.log("Disponibilite envoyee:", payload);
        }}
      />
    </section>
  );
}
