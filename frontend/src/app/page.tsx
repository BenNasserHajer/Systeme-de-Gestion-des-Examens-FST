"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, mot_de_passe: motDePasse }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Email ou mot de passe incorrect");
        return;
      }
      const data = await res.json();
      const type = data.user?.type;
      if (type === "ADMIN") router.push("/planification");
      else if (type === "ENSEIGNANT") router.push("/indisponibilite");
      else setError("Type de compte non reconnu");
    } catch {
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fst-wrap">
      <div className="fst-col">

        {/* Icon badge */}
        <div className="fst-badge" aria-hidden="true">
          🎓
        </div>

        {/* Glass card */}
        <div className="fst-card">
          <p className="fst-title">Faculté des Sciences de Tunis</p>
          <p className="fst-subtitle">Connexion</p>
          <div className="fst-gold-line" />

          <form onSubmit={handleSubmit}>

            {/* Email */}
            <div className="fst-field">
              <div className="fst-icon">✉</div>
              <input
                className="fst-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Adresse électronique"
                autoComplete="email"
              />
            </div>

            {/* Password */}
            <div className="fst-field">
              <div className="fst-icon">🔒</div>
              <input
                className="fst-input"
                type={showPassword ? "text" : "password"}
                value={motDePasse}
                onChange={(e) => setMotDePasse(e.target.value)}
                required
                placeholder="Mot de passe"
                autoComplete="current-password"
              />
              <button
                type="button"
                className="fst-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label="Afficher/masquer le mot de passe"
              >
                {showPassword ? "🙈" : "👁"}
              </button>
            </div>

            {/* Error */}
            {error && (
              <div className="fst-error">{error}</div>
            )}



            {/* Submit */}
            <div className="fst-btn-wrap">
              <button
                type="submit"
                className="fst-btn"
                disabled={loading}
              >
                {loading ? "Authentification…" : "Connexion"}
              </button>
            </div>

          </form>
        </div>

        {/* Decorative dots */}
        <div className="fst-dots">
          <div className="fst-dot fst-dot--active" />
          <div className="fst-dot" />
          <div className="fst-dot" />
        </div>

      </div>
    </div>
  );
}