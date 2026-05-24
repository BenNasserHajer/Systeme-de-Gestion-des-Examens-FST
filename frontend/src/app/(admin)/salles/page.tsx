"use client";

import { useEffect, useState } from "react";
import { getSalles, createSalle, updateSalle, deleteSalle, type Salle, type SalleCreate, type SalleUpdate } from "@/lib/api/salle";

export default function SallesPage() {
  const [salles, setSalles] = useState<Salle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSalle, setEditingSalle] = useState<Salle | null>(null);
  const [formData, setFormData] = useState<SalleCreate>({
    code: "",
    designation: "",
    capacite: 30,
    batiment: "",
  });

  const loadSalles = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSalles();
      setSalles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors du chargement des salles");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSalles();
  }, []);

  const handleOpenModal = (salle?: Salle) => {
    if (salle) {
      setEditingSalle(salle);
      setFormData({
        code: salle.code,
        designation: salle.designation || "",
        capacite: salle.capacite,
        batiment: salle.batiment || "",
      });
    } else {
      setEditingSalle(null);
      setFormData({
        code: "",
        designation: "",
        capacite: 30,
        batiment: "",
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingSalle(null);
    setFormData({
      code: "",
      designation: "",
      capacite: 30,
      batiment: "",
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingSalle) {
        await updateSalle(editingSalle.id, formData as SalleUpdate);
      } else {
        await createSalle(formData);
      }
      await loadSalles();
      handleCloseModal();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erreur lors de l'enregistrement");
    }
  };

  const handleDelete = async (salle: Salle) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer la salle "${salle.code}" ?`)) {
      return;
    }
    try {
      await deleteSalle(salle.id);
      await loadSalles();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erreur lors de la suppression");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-slate-600">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Gestion des Salles</h1>
          <p className="text-sm text-slate-600 mt-1">
            {salles.length} salle{salles.length !== 1 ? "s" : ""} enregistrée{salles.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Nouvelle Salle
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Code
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Désignation
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Capacité
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                Bâtiment
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-slate-700 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {salles.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                  Aucune salle enregistrée. Cliquez sur "Nouvelle Salle" pour commencer.
                </td>
              </tr>
            ) : (
              salles.map((salle) => (
                <tr key={salle.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-medium text-slate-900">{salle.code}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-slate-700">{salle.designation || "—"}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {salle.capacite} places
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-slate-700">{salle.batiment || "—"}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleOpenModal(salle)}
                      className="text-blue-600 hover:text-blue-900 transition-colors"
                    >
                      Modifier
                    </button>
                    <button
                      onClick={() => handleDelete(salle)}
                      className="text-red-600 hover:text-red-900 transition-colors"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-slate-200">
              <h2 className="text-xl font-semibold text-slate-900">
                {editingSalle ? "Modifier la Salle" : "Nouvelle Salle"}
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label htmlFor="code" className="block text-sm font-medium text-slate-700 mb-1">
                  Code <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="code"
                  required
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: A101"
                />
              </div>

              <div>
                <label htmlFor="designation" className="block text-sm font-medium text-slate-700 mb-1">
                  Désignation
                </label>
                <input
                  type="text"
                  id="designation"
                  value={formData.designation || ""}
                  onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Salle de cours A"
                />
              </div>

              <div>
                <label htmlFor="capacite" className="block text-sm font-medium text-slate-700 mb-1">
                  Capacité <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="capacite"
                  required
                  min="1"
                  value={formData.capacite}
                  onChange={(e) => setFormData({ ...formData, capacite: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label htmlFor="batiment" className="block text-sm font-medium text-slate-700 mb-1">
                  Bâtiment
                </label>
                <input
                  type="text"
                  id="batiment"
                  value={formData.batiment || ""}
                  onChange={(e) => setFormData({ ...formData, batiment: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Bâtiment A"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editingSalle ? "Enregistrer" : "Créer"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
