"""Catalogue referentiel for exam planification (sections, sessions, salles, creneaux)."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

SESSIONS: dict[str, dict[str, Any]] = {
    "Session Normale Juin 2026": {
        "session_id": 1,
        "date_debut": "2026-06-01",
        "date_fin": "2026-06-30",
        "statut": "BROUILLON",
    },
    "Session Rattrapage Juillet 2026": {
        "session_id": 2,
        "date_debut": "2026-07-01",
        "date_fin": "2026-07-20",
        "statut": "BROUILLON",
    },
}

SECTIONS: dict[str, dict[str, Any]] = {
    "INFO-L3-A": {
        "niveau": "L3",
        "section_id": 101,
        "effectif": 35,
        "matieres": [
            {
                "section_matiere_id": 1001,
                "matiere": "Algorithmique Avancee",
                "coefficient": 2.0,
                "duree": 120,
                "nb_surveillants_requis": 2,
                "a_examen_final": True,
                "a_ds": True,
            },
            {
                "section_matiere_id": 1002,
                "matiere": "Base de Donnees",
                "coefficient": 1.5,
                "duree": 120,
                "nb_surveillants_requis": 1,
                "a_examen_final": True,
                "a_ds": True,
            },
            {
                "section_matiere_id": 1005,
                "matiere": "Physique 101",
                "coefficient": 1.5,
                "duree": 150,
                "nb_surveillants_requis": 2,
                "a_examen_final": True,
                "a_ds": True,
            },
        ],
    },
    "INFO-L3-B": {
        "niveau": "L3",
        "section_id": 102,
        "effectif": 28,
        "matieres": [
            {
                "section_matiere_id": 1003,
                "matiere": "Systemes Distribues",
                "coefficient": 2.0,
                "duree": 120,
                "nb_surveillants_requis": 2,
                "a_examen_final": True,
                "a_ds": True,
            },
            {
                "section_matiere_id": 1004,
                "matiere": "Securite Informatique",
                "coefficient": 1.5,
                "duree": 120,
                "nb_surveillants_requis": 1,
                "a_examen_final": True,
                "a_ds": True,
            },
        ],
    },
    "INFO-M1": {
        "niveau": "M1",
        "section_id": 201,
        "effectif": 24,
        "matieres": [
            {
                "section_matiere_id": 2001,
                "matiere": "Machine Learning",
                "coefficient": 2.0,
                "duree": 120,
                "nb_surveillants_requis": 2,
                "a_examen_final": True,
                "a_ds": True,
            },
            {
                "section_matiere_id": 2002,
                "matiere": "Cloud Computing",
                "coefficient": 1.0,
                "duree": 90,
                "nb_surveillants_requis": 1,
                "a_examen_final": True,
                "a_ds": False,
            },
        ],
    },
}

TYPE_EPREUVE_LABELS = {
    "DS": "DS",
    "Examen Final": "EXAMEN_FINAL",
}

SAMPLE_CRENEAUX = [
    {"date_examen": "2026-06-02", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
    {"date_examen": "2026-06-02", "heure_debut": "10:00:00", "heure_fin": "12:00:00"},
    {"date_examen": "2026-06-02", "heure_debut": "13:00:00", "heure_fin": "15:00:00"},
    {"date_examen": "2026-06-03", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
    {"date_examen": "2026-06-03", "heure_debut": "10:00:00", "heure_fin": "12:00:00"},
    {"date_examen": "2026-06-04", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
    {"date_examen": "2026-06-04", "heure_debut": "10:00:00", "heure_fin": "12:00:00"},
    {"date_examen": "2026-06-05", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
]

SAMPLE_SALLES = [
    {"salle_id": "Room 302", "capacite": 45, "batiment": "A"},
    {"salle_id": "S20A", "capacite": 20, "batiment": "A"},
    {"salle_id": "S20B", "capacite": 20, "batiment": "A"},
    {"salle_id": "S30", "capacite": 30, "batiment": "B"},
    {"salle_id": "AMPHI INFO", "capacite": 80, "batiment": "C"},
]


def _default_catalogue() -> dict[str, Any]:
    sections_by_niveau: dict[str, list[dict[str, Any]]] = {}
    matieres_by_section: dict[str, list[dict[str, Any]]] = {}

    for section_label, section in SECTIONS.items():
        niveau = section["niveau"]
        sections_by_niveau.setdefault(niveau, []).append(
            {
                "label": section_label,
                "section_id": section["section_id"],
                "effectif": section["effectif"],
                "niveau": niveau,
            }
        )
        matieres_by_section[section_label] = list(section["matieres"])

    for niveau in sections_by_niveau:
        sections_by_niveau[niveau] = sorted(sections_by_niveau[niveau], key=lambda x: x["label"])

    sessions = [
        {"label": label, **item}
        for label, item in sorted(SESSIONS.items())
    ]

    return {
        "source": "fallback-static",
        "sessions": sessions,
        "niveaux": sorted(sections_by_niveau.keys()),
        "sections_by_niveau": sections_by_niveau,
        "matieres_by_section": matieres_by_section,
        "salles": list(SAMPLE_SALLES),
        "creneaux": list(SAMPLE_CRENEAUX),
        "types_epreuve": list(TYPE_EPREUVE_LABELS.keys()),
    }


def load_catalogue(db: Session | None = None) -> dict[str, Any]:
    catalogue = _default_catalogue()
    if db is None:
        return catalogue

    try:
        bind = db.get_bind()
        if bind is None or not inspect(bind).has_table("session"):
            return catalogue

        rows = db.execute(
            text("SELECT id, annee_universitaire, date_debut, date_fin, statut FROM session ORDER BY id")
        ).mappings().all()
        if rows:
            catalogue["sessions"] = [
                {
                    "label": f"Session {row['id']} ({row['annee_universitaire']})",
                    "session_id": row["id"],
                    "date_debut": str(row["date_debut"]),
                    "date_fin": str(row["date_fin"]),
                    "statut": str(row["statut"]).upper(),
                }
                for row in rows
            ]
            catalogue["source"] = "database"
    except Exception:
        pass

    return catalogue


def build_generation_tasks(
    catalogue: dict[str, Any],
    section_label: str,
    type_epreuve_label: str,
) -> list[dict[str, Any]]:
    section_by_label = {
        item["label"]: item
        for sections in catalogue.get("sections_by_niveau", {}).values()
        for item in sections
    }
    section = section_by_label.get(section_label)
    if not section:
        raise ValueError("Section inconnue.")
    if type_epreuve_label not in TYPE_EPREUVE_LABELS:
        raise ValueError("Type d'epreuve invalide.")

    type_epreuve = TYPE_EPREUVE_LABELS[type_epreuve_label]
    matieres = catalogue.get("matieres_by_section", {}).get(section_label, [])

    tasks: list[dict[str, Any]] = []
    for mat in matieres:
        if type_epreuve == "DS" and not mat.get("a_ds", False):
            continue
        if type_epreuve == "EXAMEN_FINAL" and not mat.get("a_examen_final", False):
            continue
        tasks.append(
            {
                "section_id": section["section_id"],
                "section_matiere_id": mat["section_matiere_id"],
                "matiere": mat["matiere"],
                "type_epreuve": type_epreuve,
                "duree": mat["duree"],
                "section_nb_etudiants": section["effectif"],
                "coefficient": mat["coefficient"],
                "nb_surveillants_requis": mat["nb_surveillants_requis"],
                "a_examen_final": mat.get("a_examen_final", True),
                "a_ds": mat.get("a_ds", True),
            }
        )

    if not tasks:
        raise ValueError("Aucune matiere eligible pour cette section et ce type d'epreuve.")
    return tasks


def build_generation_request(
    catalogue: dict[str, Any],
    session_id: int,
    section_label: str,
    type_epreuve_label: str,
    niveau: str,
) -> dict[str, Any]:
    sessions_by_id = {s["session_id"]: s for s in catalogue.get("sessions", [])}
    session = sessions_by_id.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} introuvable.")

    section_by_label = {
        item["label"]: item
        for sections in catalogue.get("sections_by_niveau", {}).values()
        for item in sections
    }
    section = section_by_label.get(section_label)
    if not section:
        raise ValueError("Section inconnue.")
    if section["niveau"] != niveau:
        raise ValueError("La section ne correspond pas au niveau selectionne.")

    tasks = build_generation_tasks(catalogue, section_label, type_epreuve_label)
    return {
        "session_id": session_id,
        "session_date_debut": session["date_debut"],
        "session_date_fin": session["date_fin"],
        "session_statut": session["statut"],
        "mode": "AUTO",
        "scope_section_ids": [section["section_id"]],
        "tasks": tasks,
        "creneaux": catalogue.get("creneaux") or SAMPLE_CRENEAUX,
        "salles": catalogue.get("salles") or SAMPLE_SALLES,
    }
