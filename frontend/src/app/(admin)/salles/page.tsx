"use client";

import { useEffect, useState } from "react";

const API = "http://localhost:8000/api/salles";

type Salle = {
  id: number;
  nom: string;
  capacite: number | null;
};

export default function SallesPage() {
  const [salles, setSalles] = useState<Salle[]>([]);
  const [nom, setNom] = useState("");
  const [capacite, setCapacite] = useState("");
  const [editId, setEditId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ✅ FETCH CLEAN
  const fetchSalles = async () => {
    try {
      const res = await fetch(API);
      if (!res.ok) throw new Error("Erreur API");

      const data = await res.json();
      setSalles(Array.isArray(data) ? data : []);
    } catch (err) {
      setError("Impossible de charger les salles");
      console.error(err);
    }
  };

  useEffect(() => {
    fetchSalles();
  }, []);

  // RESET FORM
  const reset = () => {
    setNom("");
    setCapacite("");
    setEditId(null);
    setError("");
  };

  // CREATE / UPDATE
  const submit = async () => {
    if (!nom.trim()) {
      setError("Le nom est requis");
      return;
    }

    setLoading(true);
    setError("");

    const body = {
      nom,
      capacite: capacite ? Number(capacite) : null,
    };

    try {
      const url =
        editId !== null ? `${API}/${editId}` : API;

      const method = editId !== null ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Erreur serveur");
      }

      reset();
      fetchSalles();
    } catch (err: any) {
      setError(err.message || "Erreur lors de la sauvegarde");
    } finally {
      setLoading(false);
    }
  };

  // EDIT
  const startEdit = (s: Salle) => {
    setEditId(s.id);
    setNom(s.nom);
    setCapacite(s.capacite?.toString() || "");
  };

  // DELETE
  const deleteSalle = async (id: number) => {
    if (!confirm("Supprimer cette salle ?")) return;

    try {
      const res = await fetch(`${API}/${id}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Erreur suppression");

      fetchSalles();
    } catch (err) {
      console.error(err);
      setError("Erreur lors de la suppression");
    }
  };

  return (
    <div className="p-6 space-y-6">

      <h1 className="text-xl font-bold">Gestion des Salles</h1>

      {/* FORM */}
      <div className="p-4 border rounded space-y-3">
        {error && <p className="text-red-500 text-sm">{error}</p>}

        <input
          className="border p-2 w-full"
          placeholder="Nom salle"
          value={nom}
          onChange={(e) => setNom(e.target.value)}
        />

        <input
          className="border p-2 w-full"
          placeholder="Capacité"
          type="number"
          value={capacite}
          onChange={(e) => setCapacite(e.target.value)}
        />

        <div className="flex gap-2">
          <button
            onClick={submit}
            disabled={loading}
            className="bg-black text-white px-4 py-2"
          >
            {editId ? "Modifier" : "Ajouter"}
          </button>

          {editId && (
            <button
              onClick={reset}
              className="border px-4 py-2"
            >
              Annuler
            </button>
          )}
        </div>
      </div>

      {/* LIST */}
      <div className="border rounded p-4">
        <table className="w-full">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nom</th>
              <th>Capacité</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {salles.map((s) => (
              <tr key={s.id} className="border-t">
                <td>{s.id}</td>
                <td>{s.nom}</td>
                <td>{s.capacite ?? "-"}</td>
                <td className="flex gap-2">
                  <button onClick={() => startEdit(s)}>
                    Edit
                  </button>
                  <button onClick={() => deleteSalle(s.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}