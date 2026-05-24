"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";

import { affecterSession } from "@/lib/api/surveillance";
import type { AffecterSessionResponse } from "@/lib/types/surveillance";
import { AffectationBoard } from "@/components/surveillance/AffectationBoard";
import { Button } from "@/components/ui/Button";
import { Layout } from "@/components/ui/Layout";

export default function AffectationPage() {
  const searchParams = useSearchParams();
  const sessionParam = searchParams.get("sessionId") ?? searchParams.get("session_id");
  const sessionId = sessionParam ? Number(sessionParam) : null;
  const validSessionId = Number.isFinite(sessionId ?? NaN) ? sessionId : null;

  const [data, setData] = useState<AffecterSessionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    if (!validSessionId) {
      setError("Session ID manquant");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await affecterSession({ session_id: validSessionId });
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
      title="Affectation automatique"
      subtitle="Lancer l’algorithme de surveillance pour une session"
      actions={
        <Button onClick={handleRun} isLoading={loading}>
          Lancer l’affectation
        </Button>
      }
    >
      {!validSessionId && (
        <p className="text-sm text-amber-600">
          Ajoutez un paramètre sessionId dans l’URL pour lancer l’affectation.
        </p>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
      <AffectationBoard data={data} />
    </Layout>
  );
}
