"""Catalogue referentiel for exam planification — loads from database with static fallback."""

from __future__ import annotations

from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

TYPE_EPREUVE_OPTIONS = [
    {"value": "EXAMEN_FINAL", "label": "Examen Final"},
    {"value": "DS", "label": "DS"},
]

SEMESTRES = ["S1", "S2"]


def normalize_semestre_code(semestre: str) -> str:
    value = (semestre or "").strip().upper()
    if value.startswith("S"):
        return value
    return f"S{value}" if value else "S1"


def matiere_matches_semestre(matiere_semestre: str | None, selected_semestre: str) -> bool:
    """Match matiere annee_sem (e.g. 2025/2026-S1) against UI choice S1/S2."""
    if not matiere_semestre or not str(matiere_semestre).strip():
        return True
    code = normalize_semestre_code(selected_semestre)
    raw = str(matiere_semestre).strip().upper()
    return raw == code or raw.endswith(f"-{code}")

SESSIONS_FALLBACK = {
    "Session Normale Juin 2026": {
        "session_id": 1,
        "date_debut": "2026-06-01",
        "date_fin": "2026-06-30",
        "statut": "BROUILLON",
    },
}

SECTIONS_FALLBACK = {
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
        ],
    },
}

SAMPLE_CRENEAUX = [
    {"date_examen": "2026-06-02", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
    {"date_examen": "2026-06-02", "heure_debut": "10:00:00", "heure_fin": "12:00:00"},
    {"date_examen": "2026-06-03", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
    {"date_examen": "2026-06-04", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
    {"date_examen": "2026-06-05", "heure_debut": "08:00:00", "heure_fin": "10:00:00"},
]

SAMPLE_SALLES = [
    {"salle_id": "AMPHI-INFO", "capacite": 106, "batiment": "A"},
    {"salle_id": "Room 302", "capacite": 45, "batiment": "A"},
    {"salle_id": "INF-15", "capacite": 30, "batiment": "B"},
]


def _table_exists(db: Session, table_name: str) -> bool:
    bind = db.get_bind()
    if bind is None:
        return False
    return inspect(bind).has_table(table_name)


def _table_columns(db: Session, table_name: str) -> set[str]:
    bind = db.get_bind()
    if bind is None:
        return set()
    try:
        return {col["name"] for col in inspect(bind).get_columns(table_name)}
    except Exception:
        return set()


def _default_catalogue() -> dict[str, Any]:
    sections: list[dict[str, Any]] = []
    matieres_by_section: dict[str, list[dict[str, Any]]] = {}

    for label, section in SECTIONS_FALLBACK.items():
        sections.append(
            {
                "label": label,
                "section_id": section["section_id"],
                "effectif": section["effectif"],
                "niveau": section["niveau"],
            }
        )
        matieres_by_section[label] = list(section["matieres"])

    sections.sort(key=lambda x: x["label"])
    sessions = [{"label": label, **item} for label, item in sorted(SESSIONS_FALLBACK.items())]

    return {
        "source": "fallback-static",
        "message": "Catalogue statique (base de donnees indisponible ou vide).",
        "sessions": sessions,
        "sections": sections,
        "semestres": SEMESTRES,
        "types_epreuve": TYPE_EPREUVE_OPTIONS,
        "matieres_by_section": matieres_by_section,
        "salles": list(SAMPLE_SALLES),
        "creneaux": list(SAMPLE_CRENEAUX),
    }


def _load_sessions(db: Session) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    if _table_exists(db, "session"):
        rows = db.execute(
            text(
                """
                SELECT id, COALESCE(annee_universitaire, '') AS annee,
                       date_debut, date_fin, COALESCE(statut, 'BROUILLON') AS statut
                FROM session ORDER BY date_debut, id
                """
            )
        ).mappings().all()
        for row in rows:
            annee = row['annee']
            date_debut = row['date_debut']
            
            # Déterminer le semestre basé sur le mois de début
            # Janvier-Février = S1, Mai-Juin = S2
            if date_debut:
                month = date_debut.month if hasattr(date_debut, 'month') else int(str(date_debut).split('-')[1])
                if month >= 5:  # Mai ou après = S2
                    semestre_suffix = " S2"
                else:  # Janvier-Avril = S1
                    semestre_suffix = " S1"
            else:
                semestre_suffix = ""
            
            label = f"Principale {annee}{semestre_suffix}".strip() if annee else f"Session {row['id']}"
            sessions.append(
                {
                    "label": label,
                    "session_id": int(row["id"]),
                    "date_debut": str(row["date_debut"]),
                    "date_fin": str(row["date_fin"]),
                    "statut": str(row["statut"]).upper(),
                }
            )
    elif _table_exists(db, "sessions"):
        rows = db.execute(
            text(
                """
                SELECT id, date_debut, date_fin, COALESCE(statut, 'BROUILLON') AS statut
                FROM sessions ORDER BY date_debut, id
                """
            )
        ).mappings().all()
        for row in rows:
            sessions.append(
                {
                    "label": f"Session {row['id']} ({row['date_debut']} -> {row['date_fin']})",
                    "session_id": int(row["id"]),
                    "date_debut": str(row["date_debut"]),
                    "date_fin": str(row["date_fin"]),
                    "statut": str(row["statut"]).upper(),
                }
            )
    return sessions


def _load_sections_and_matieres(db: Session) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    sections: list[dict[str, Any]] = []
    matieres_by_section: dict[str, list[dict[str, Any]]] = {}

    if _table_exists(db, "section") and _table_exists(db, "section_matiere") and _table_exists(db, "matiere"):
        # Calculate effectif from groupe table if it exists, otherwise default to 0
        if _table_exists(db, "groupe"):
            section_rows = db.execute(
                text(
                    """
                    SELECT
                        s.id AS section_id,
                        COALESCE(s.nom, CONCAT('Section-', s.id)) AS section_label,
                        COALESCE(n.libelle, '') AS niveau,
                        COALESCE(SUM(g.nb_etudiants), 0) AS effectif
                    FROM section s
                    LEFT JOIN niveau n ON n.id = s.niveau_id
                    LEFT JOIN groupe g ON g.section_id = s.id
                    GROUP BY s.id, s.nom, n.libelle
                    ORDER BY section_label
                    """
                )
            ).mappings().all() if _table_exists(db, "niveau") else db.execute(
                text(
                    """
                    SELECT
                        s.id AS section_id,
                        COALESCE(s.nom, CONCAT('Section-', s.id)) AS section_label,
                        '' AS niveau,
                        COALESCE(SUM(g.nb_etudiants), 0) AS effectif
                    FROM section s
                    LEFT JOIN groupe g ON g.section_id = s.id
                    GROUP BY s.id, s.nom
                    ORDER BY section_label
                    """
                )
            ).mappings().all()
        else:
            section_rows = db.execute(
                text(
                    """
                    SELECT
                        s.id AS section_id,
                        COALESCE(s.nom, CONCAT('Section-', s.id)) AS section_label,
                        COALESCE(n.libelle, '') AS niveau,
                        0 AS effectif
                    FROM section s
                    LEFT JOIN niveau n ON n.id = s.niveau_id
                    ORDER BY section_label
                    """
                )
            ).mappings().all() if _table_exists(db, "niveau") else db.execute(
                text(
                    """
                    SELECT id AS section_id,
                           COALESCE(nom, CONCAT('Section-', id)) AS section_label,
                           '' AS niveau,
                           0 AS effectif
                    FROM section ORDER BY section_label
                    """
                )
            ).mappings().all()

        for row in section_rows:
            label = str(row["section_label"])
            sections.append(
                {
                    "label": label,
                    "section_id": int(row["section_id"]),
                    "effectif": int(row["effectif"]),
                    "niveau": str(row["niveau"]) or "—",
                }
            )
            matieres_by_section[label] = []

        mat_rows = db.execute(
            text(
                """
                SELECT
                    sm.id AS section_matiere_id,
                    sm.section_id,
                    m.intitule AS matiere,
                    COALESCE(sm.annee_sem, '') AS semestre,
                    COALESCE(m.coefficient, 1.0) AS coefficient,
                    COALESCE(sm.duree_examen, m.duree_examen, sm.duree_ds, m.duree_ds, 120) AS duree,
                    1 AS nb_surveillants_requis,
                    COALESCE(sm.a_examen_final, m.a_examen_final, true) AS a_examen_final,
                    COALESCE(sm.a_ds, m.a_ds, true) AS a_ds
                FROM section_matiere sm
                JOIN matiere m ON m.id = sm.matiere_id
                ORDER BY sm.section_id, sm.id
                """
            )
        ).mappings().all()

        label_by_id = {s["section_id"]: s["label"] for s in sections}
        for row in mat_rows:
            section_label = label_by_id.get(int(row["section_id"]))
            if not section_label:
                continue
            matieres_by_section.setdefault(section_label, []).append(
                {
                    "section_matiere_id": int(row["section_matiere_id"]),
                    "matiere": str(row["matiere"]),
                    "semestre": str(row["semestre"]) if row["semestre"] else "",
                    "coefficient": float(row["coefficient"]),
                    "duree": int(row["duree"]),
                    "nb_surveillants_requis": int(row["nb_surveillants_requis"]),
                    "a_examen_final": bool(row["a_examen_final"]),
                    "a_ds": bool(row["a_ds"]),
                }
            )

    elif _table_exists(db, "sections") and _table_exists(db, "section_matieres"):
        section_rows = db.execute(
            text(
                """
                SELECT id AS section_id,
                       COALESCE(nom, CONCAT('Section-', id)) AS section_label,
                       COALESCE(niveau, '') AS niveau,
                       COALESCE(nb_etudiants, 0) AS effectif
                FROM sections ORDER BY section_label
                """
            )
        ).mappings().all()
        for row in section_rows:
            label = str(row["section_label"])
            sections.append(
                {
                    "label": label,
                    "section_id": int(row["section_id"]),
                    "effectif": int(row["effectif"]),
                    "niveau": str(row["niveau"]) or "—",
                }
            )
            matieres_by_section[label] = []

        mat_rows = db.execute(
            text(
                """
                SELECT sm.id AS section_matiere_id, sm.section_id,
                       COALESCE(sm.matiere, CONCAT('Matiere-', sm.id)) AS matiere,
                       COALESCE(sm.coefficient, 1.0) AS coefficient,
                       COALESCE(sm.duree, 120) AS duree,
                       COALESCE(sm.nb_surveillants_requis, 1) AS nb_surveillants_requis,
                       COALESCE(sm.a_examen_final, true) AS a_examen_final,
                       COALESCE(sm.a_ds, true) AS a_ds
                FROM section_matieres sm ORDER BY sm.section_id, sm.id
                """
            )
        ).mappings().all()
        label_by_id = {s["section_id"]: s["label"] for s in sections}
        for row in mat_rows:
            section_label = label_by_id.get(int(row["section_id"]))
            if section_label:
                matieres_by_section.setdefault(section_label, []).append(
                    {
                        "section_matiere_id": int(row["section_matiere_id"]),
                        "matiere": str(row["matiere"]),
                        "coefficient": float(row["coefficient"]),
                        "duree": int(row["duree"]),
                        "nb_surveillants_requis": int(row["nb_surveillants_requis"]),
                        "a_examen_final": bool(row["a_examen_final"]),
                        "a_ds": bool(row["a_ds"]),
                    }
                )

    return sections, matieres_by_section


def list_salles_referentiel(db: Session) -> list[dict[str, Any]]:
    """Public accessor for room referential used by planification."""
    return _load_salles(db)


def _load_salles(db: Session) -> list[dict[str, Any]]:
    salles: list[dict[str, Any]] = []
    if _table_exists(db, "salle"):
        rows = db.execute(
            text(
                """
                SELECT COALESCE(code, CAST(id AS TEXT)) AS salle_id,
                       COALESCE(capacite, 0) AS capacite,
                       COALESCE(batiment, '') AS batiment
                FROM salle ORDER BY salle_id
                """
            )
        ).mappings().all()
        salles = [
            {"salle_id": str(r["salle_id"]), "capacite": int(r["capacite"]), "batiment": str(r["batiment"])}
            for r in rows
        ]
    elif _table_exists(db, "salles"):
        rows = db.execute(
            text(
                """
                SELECT COALESCE(code, CAST(id AS TEXT)) AS salle_id,
                       COALESCE(capacite, 0) AS capacite,
                       COALESCE(batiment, '') AS batiment
                FROM salles ORDER BY salle_id
                """
            )
        ).mappings().all()
        salles = [
            {"salle_id": str(r["salle_id"]), "capacite": int(r["capacite"]), "batiment": str(r["batiment"])}
            for r in rows
        ]
    elif _table_exists(db, "planif_salle"):
        cols = _table_columns(db, "planif_salle")
        cap = "COALESCE(MAX(salle_capacite), 0)" if "salle_capacite" in cols else "0"
        bat = "COALESCE(MAX(salle_batiment), '')" if "salle_batiment" in cols else "''"
        rows = db.execute(
            text(f"SELECT salle_id, {cap} AS capacite, {bat} AS batiment FROM planif_salle GROUP BY salle_id")
        ).mappings().all()
        salles = [
            {"salle_id": str(r["salle_id"]), "capacite": int(r["capacite"]), "batiment": str(r["batiment"])}
            for r in rows
        ]
    return salles


def _load_creneaux(db: Session) -> list[dict[str, Any]]:
    creneaux: list[dict[str, Any]] = []
    if _table_exists(db, "creneau"):
        rows = db.execute(
            text("SELECT date AS date_examen, heure_debut, heure_fin FROM creneau ORDER BY date, heure_debut")
        ).mappings().all()
        creneaux = [
            {
                "date_examen": str(r["date_examen"]),
                "heure_debut": str(r["heure_debut"]),
                "heure_fin": str(r["heure_fin"]),
            }
            for r in rows
        ]
    elif _table_exists(db, "creneaux"):
        rows = db.execute(
            text("SELECT date_examen, heure_debut, heure_fin FROM creneaux ORDER BY date_examen, heure_debut")
        ).mappings().all()
        creneaux = [
            {
                "date_examen": str(r["date_examen"]),
                "heure_debut": str(r["heure_debut"]),
                "heure_fin": str(r["heure_fin"]),
            }
            for r in rows
        ]
    return creneaux


def load_catalogue(db: Session | None = None) -> dict[str, Any]:
    catalogue = _default_catalogue()
    if db is None:
        return catalogue

    try:
        sessions = _load_sessions(db)
        sections, matieres_by_section = _load_sections_and_matieres(db)
        salles = _load_salles(db)
        creneaux = _load_creneaux(db)

        if sessions:
            catalogue["sessions"] = sessions
        if sections:
            catalogue["sections"] = sections
            catalogue["matieres_by_section"] = matieres_by_section
            catalogue["source"] = "database"
            catalogue["message"] = f"{len(sections)} section(s) chargee(s) depuis la base."
        catalogue["salles"] = salles if salles else list(SAMPLE_SALLES)
        if creneaux:
            catalogue["creneaux"] = creneaux
    except Exception as exc:
        catalogue["message"] = f"Erreur chargement BD: {exc}. Catalogue statique utilise."

    return catalogue


def get_section_by_id(catalogue: dict[str, Any], section_id: int) -> dict[str, Any] | None:
    for section in catalogue.get("sections", []):
        if section["section_id"] == section_id:
            return section
    return None


def build_generation_tasks_for_section(
    catalogue: dict[str, Any],
    section_id: int,
    type_epreuve: str,
    semestre: str = "S1",
) -> list[dict[str, Any]]:
    section = get_section_by_id(catalogue, section_id)
    if not section:
        raise ValueError(f"Section {section_id} introuvable.")

    matieres = catalogue.get("matieres_by_section", {}).get(section["label"], [])
    tasks: list[dict[str, Any]] = []
    
    semestre_normalized = normalize_semestre_code(semestre)

    for mat in matieres:
        # Filter by type d'épreuve
        if type_epreuve == "DS" and not mat.get("a_ds", False):
            continue
        if type_epreuve == "EXAMEN_FINAL" and not mat.get("a_examen_final", False):
            continue

        if not matiere_matches_semestre(mat.get("semestre"), semestre_normalized):
            continue
        
        tasks.append(
            {
                "section_id": section["section_id"],
                "section_matiere_id": mat["section_matiere_id"],
                "matiere": mat["matiere"],
                "semestre": semestre,
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
        raise ValueError(f"Aucune matiere eligible pour cette section, type d'epreuve et semestre {semestre}.")
    return tasks


def build_generation_request_by_section(
    catalogue: dict[str, Any],
    session_id: int,
    section_id: int,
    type_epreuve: str,
    semestre: str,
) -> dict[str, Any]:
    sessions_by_id = {s["session_id"]: s for s in catalogue.get("sessions", [])}
    session = sessions_by_id.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} introuvable.")

    tasks = build_generation_tasks_for_section(catalogue, section_id, type_epreuve, semestre)
    return {
        "session_id": session_id,
        "semestre": semestre,
        "session_date_debut": session["date_debut"],
        "session_date_fin": session["date_fin"],
        "session_statut": session["statut"],
        "mode": "AUTO",
        "scope_section_ids": [section_id],
        "tasks": tasks,
        "creneaux": catalogue.get("creneaux") or SAMPLE_CRENEAUX,
        "salles": catalogue.get("salles") or SAMPLE_SALLES,
    }
