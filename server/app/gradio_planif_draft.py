"""Gradio draft interface to test exam planning without writing to database.

Usage:
    python -m app.gradio_planif_draft

Notes:
- This tool calls the planning algorithm directly.
- It does NOT persist generated planifications into the DB.
"""

from __future__ import annotations

import json
from datetime import date
from types import SimpleNamespace
from typing import Any

import gradio as gr
from sqlalchemy import inspect, text

from app.algorithms.contraintes import build_default_engine
from app.algorithms.planif_auto import generer
from app.crud.crud_planif import create_planification, list_existing_for_session
from app.database import SessionLocal, check_connection
from app.schemas.planification import GenerationRequest


SESSIONS = {
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

SECTIONS = {
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

TYPE_EP_CHOICES = {
    "DS": "DS",
    "Examen Final": "EXAMEN_FINAL",
}

DEFAULT_NIVEAUX = sorted({value["niveau"] for value in SECTIONS.values()})

SAMPLE_CRENEAUX = [
    {
        "date_examen": "2026-06-02",
        "heure_debut": "08:30:00",
        "heure_fin": "10:30:00",
    },
    {
        "date_examen": "2026-06-02",
        "heure_debut": "11:00:00",
        "heure_fin": "13:00:00",
    },
    {
        "date_examen": "2026-06-03",
        "heure_debut": "08:30:00",
        "heure_fin": "10:30:00",
    },
]

SAMPLE_SALLES = [
    {"salle_id": "S20A", "capacite": 20, "batiment": "A"},
    {"salle_id": "S20B", "capacite": 20, "batiment": "A"},
    {"salle_id": "S30", "capacite": 30, "batiment": "B"},
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

    sessions = []
    for label, item in sorted(SESSIONS.items()):
        sessions.append(
            {
                "label": label,
                "session_id": item["session_id"],
                "date_debut": item["date_debut"],
                "date_fin": item["date_fin"],
                "statut": item["statut"],
            }
        )

    return {
        "source": "fallback-static",
        "connected": False,
        "message": "Catalogue local statique charge (connexion BD indisponible ou donnees vides).",
        "sessions": sessions,
        "niveaux": sorted(sections_by_niveau.keys()),
        "sections_by_niveau": sections_by_niveau,
        "matieres_by_section": matieres_by_section,
        "salles": list(SAMPLE_SALLES),
        "creneaux": list(SAMPLE_CRENEAUX),
    }


def _derive_niveau_from_label_or_id(section_label: str, section_id: int) -> str:
    upper = section_label.upper()
    if "L1" in upper:
        return "L1"
    if "L2" in upper:
        return "L2"
    if "L3" in upper:
        return "L3"
    if "M1" in upper:
        return "M1"
    if "M2" in upper:
        return "M2"
    if section_id >= 200:
        return "M1/M2"
    return "L1/L2/L3"


def _table_exists(session, table_name: str) -> bool:
    bind = session.get_bind()
    if bind is None:
        return False
    return inspect(bind).has_table(table_name)


def _table_columns(session, table_name: str) -> set[str]:
    bind = session.get_bind()
    if bind is None:
        return set()
    try:
        return {col["name"] for col in inspect(bind).get_columns(table_name)}
    except Exception:
        return set()


def _load_existing_for_generation(db, session_id: int) -> list[Any]:
    """Return existing planifications in a shape compatible with the generation wrapper."""
    has_planifs = _table_exists(db, "planifications")
    if has_planifs:
        try:
            return list_existing_for_session(db, session_id)
        except Exception:
            return []

    if not _table_exists(db, "planification_examen"):
        return []
    if not _table_exists(db, "creneau"):
        return []

    rows = db.execute(
        text(
            """
            SELECT
                pe.id AS planif_id,
                pe.section_matiere_id,
                sm.section_id,
                c.date AS date_examen,
                c.heure_debut AS heure_debut
            FROM planification_examen pe
            JOIN creneau c ON c.id = pe.creneau_id
            LEFT JOIN section_matiere sm ON sm.id = pe.section_matiere_id
            WHERE pe.session_id = :session_id
            """
        ),
        {"session_id": session_id},
    ).mappings().all()

    if not rows:
        return []

    salle_codes_by_planif: dict[int, list[str]] = {}
    if _table_exists(db, "planif_salle") and _table_exists(db, "salle"):
        salle_rows = db.execute(
            text(
                """
                SELECT ps.planification_id, s.code AS salle_code
                FROM planif_salle ps
                JOIN salle s ON s.id = ps.salle_id
                """
            )
        ).mappings().all()
        for r in salle_rows:
            salle_codes_by_planif.setdefault(int(r["planification_id"]), []).append(str(r["salle_code"]))

    existing: list[Any] = []
    for row in rows:
        salles = [SimpleNamespace(salle_id=code) for code in salle_codes_by_planif.get(int(row["planif_id"]), [])]
        existing.append(
            SimpleNamespace(
                section_id=int(row["section_id"]) if row["section_id"] is not None else -1,
                section_matiere_id=int(row["section_matiere_id"]),
                date_examen=row["date_examen"],
                heure_debut=row["heure_debut"],
                salles_affectees=salles,
            )
        )
    return existing


def _save_generated_to_real_schema(db, creates: list[Any]) -> tuple[int, list[str]]:
    """Persist generated planifications in the real schema (planification_examen)."""
    errors: list[str] = []
    saved = 0
    mode_map = {
        "AUTO": "AUTOMATIQUE",
        "MANUEL": "MANUELLE",
    }

    if not _table_exists(db, "planification_examen"):
        return 0, ["Table planification_examen introuvable."]
    if not _table_exists(db, "creneau"):
        return 0, ["Table creneau introuvable."]

    creneau_rows = db.execute(
        text("SELECT id, date, heure_debut, heure_fin FROM creneau")
    ).mappings().all()
    creneau_map = {
        (row["date"], row["heure_debut"], row["heure_fin"]): int(row["id"])
        for row in creneau_rows
    }

    salle_code_to_id: dict[str, int] = {}
    if _table_exists(db, "salle"):
        salle_rows = db.execute(text("SELECT id, code FROM salle")).mappings().all()
        salle_code_to_id = {str(r["code"]): int(r["id"]) for r in salle_rows}

    for payload in creates:
        creneau_key = (payload.date_examen, payload.heure_debut, payload.heure_fin)
        creneau_id = creneau_map.get(creneau_key)
        if creneau_id is None:
            errors.append(
                f"{payload.matiere}: creneau introuvable pour {payload.date_examen} {payload.heure_debut}-{payload.heure_fin}."
            )
            continue

        try:
            mode_value = mode_map.get(payload.mode_affectation.value, payload.mode_affectation.value)
            new_planif_id = db.execute(
                text(
                    """
                    INSERT INTO planification_examen (
                        session_id,
                        section_matiere_id,
                        creneau_id,
                        type_epreuve,
                        duree,
                        mode_affectation,
                        statut,
                        nb_groupes,
                        nb_surveillants_requis
                    )
                    VALUES (
                        :session_id,
                        :section_matiere_id,
                        :creneau_id,
                        :type_epreuve,
                        :duree,
                        :mode_affectation,
                        :statut,
                        :nb_groupes,
                        :nb_surveillants_requis
                    )
                    RETURNING id
                    """
                ),
                {
                    "session_id": int(payload.session_id),
                    "section_matiere_id": int(payload.section_matiere_id),
                    "creneau_id": int(creneau_id),
                    "type_epreuve": payload.type_epreuve.value,
                    "duree": int(payload.duree),
                    "mode_affectation": mode_value,
                    "statut": payload.statut.value,
                    "nb_groupes": int(payload.nb_groupes),
                    "nb_surveillants_requis": int(payload.nb_surveillants_requis),
                },
            ).scalar_one()

            if _table_exists(db, "planif_salle") and salle_code_to_id:
                for salle in payload.salles:
                    salle_id = salle_code_to_id.get(str(salle.salle_id))
                    if salle_id is None:
                        errors.append(f"{payload.matiere}: salle introuvable ({salle.salle_id})")
                        continue
                    db.execute(
                        text(
                            """
                            INSERT INTO planif_salle (planification_id, salle_id, groupe_id)
                            VALUES (:planification_id, :salle_id, :groupe_id)
                            """
                        ),
                        {
                            "planification_id": int(new_planif_id),
                            "salle_id": int(salle_id),
                            "groupe_id": int(salle.groupe_id),
                        },
                    )

            db.commit()
            saved += 1
        except Exception as exc:
            db.rollback()
            errors.append(f"{payload.matiere}: {exc}")

    return saved, errors


def _load_catalogue_from_db() -> dict[str, Any]:
    fallback = _default_catalogue()
    db = SessionLocal()
    try:
        if not check_connection(db):
            fallback["message"] = "Connexion BD echec. Catalogue statique utilise."
            return fallback

        sessions: list[dict[str, Any]] = []
        sections_by_niveau: dict[str, list[dict[str, Any]]] = {}
        matieres_by_section: dict[str, list[dict[str, Any]]] = {}

        has_planifs = _table_exists(db, "planifications")
        has_planif_salle = _table_exists(db, "planif_salle")
        has_sessions_table = _table_exists(db, "sessions")
        has_sections_table = _table_exists(db, "sections")
        has_section_matieres_table = _table_exists(db, "section_matieres")
        has_real_session = _table_exists(db, "session")
        has_real_niveau = _table_exists(db, "niveau")
        has_real_section = _table_exists(db, "section")
        has_real_section_matiere = _table_exists(db, "section_matiere")
        has_real_matiere = _table_exists(db, "matiere")
        has_real_salle = _table_exists(db, "salle")
        has_real_creneau = _table_exists(db, "creneau")
        planif_salle_cols = _table_columns(db, "planif_salle") if has_planif_salle else set()

        if has_real_session:
            rows = db.execute(
                text(
                    """
                    SELECT id, date_debut, date_fin, COALESCE(statut, 'BROUILLON') AS statut
                    FROM session
                    ORDER BY date_debut, id
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
                        "statut": str(row["statut"]),
                    }
                )
        elif has_sessions_table:
            rows = db.execute(
                text(
                    """
                    SELECT id, date_debut, date_fin, COALESCE(statut, 'BROUILLON') AS statut
                    FROM sessions
                    ORDER BY date_debut, id
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
                        "statut": str(row["statut"]),
                    }
                )
        elif has_planifs:
            rows = db.execute(
                text(
                    """
                    SELECT DISTINCT
                        session_id,
                        session_date_debut AS date_debut,
                        session_date_fin AS date_fin,
                        session_statut AS statut
                    FROM planifications
                    ORDER BY session_id
                    """
                )
            ).mappings().all()
            for row in rows:
                sessions.append(
                    {
                        "label": f"Session {row['session_id']} ({row['date_debut']} -> {row['date_fin']})",
                        "session_id": int(row["session_id"]),
                        "date_debut": str(row["date_debut"]),
                        "date_fin": str(row["date_fin"]),
                        "statut": str(row["statut"]),
                    }
                )

        if has_real_section and has_real_niveau and has_real_section_matiere and has_real_matiere:
            section_rows = db.execute(
                text(
                    """
                    SELECT
                        s.id AS section_id,
                        COALESCE(s.nom, CONCAT('Section-', s.id)) AS section_label,
                        COALESCE(n.libelle, 'Non renseigne') AS niveau,
                        COALESCE(s.nb_etudiants, 0) AS effectif
                    FROM section s
                    LEFT JOIN niveau n ON n.id = s.niveau_id
                    ORDER BY niveau, section_label
                    """
                )
            ).mappings().all()

            for row in section_rows:
                niveau = str(row["niveau"])
                label = str(row["section_label"])
                sections_by_niveau.setdefault(niveau, []).append(
                    {
                        "label": label,
                        "section_id": int(row["section_id"]),
                        "effectif": int(row["effectif"]),
                        "niveau": niveau,
                    }
                )
                matieres_by_section[label] = []

            mat_rows = db.execute(
                text(
                    """
                    SELECT
                        sm.id AS section_matiere_id,
                        sm.section_id AS section_id,
                        m.intitule AS matiere,
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

            section_label_by_id = {
                int(item["section_id"]): item["label"]
                for sections in sections_by_niveau.values()
                for item in sections
            }

            for row in mat_rows:
                section_label = section_label_by_id.get(int(row["section_id"]))
                if not section_label:
                    continue
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

        elif has_sections_table and has_section_matieres_table:
            section_rows = db.execute(
                text(
                    """
                    SELECT
                        s.id AS section_id,
                        COALESCE(s.nom, CONCAT('Section-', s.id)) AS section_label,
                        COALESCE(s.niveau, 'Non renseigne') AS niveau,
                        COALESCE(s.nb_etudiants, 0) AS effectif
                    FROM sections s
                    ORDER BY niveau, section_label
                    """
                )
            ).mappings().all()

            for row in section_rows:
                niveau = str(row["niveau"])
                label = str(row["section_label"])
                sections_by_niveau.setdefault(niveau, []).append(
                    {
                        "label": label,
                        "section_id": int(row["section_id"]),
                        "effectif": int(row["effectif"]),
                        "niveau": niveau,
                    }
                )
                matieres_by_section[label] = []

            mat_rows = db.execute(
                text(
                    """
                    SELECT
                        sm.id AS section_matiere_id,
                        sm.section_id AS section_id,
                        COALESCE(sm.matiere, CONCAT('Matiere-', sm.id)) AS matiere,
                        COALESCE(sm.coefficient, 1.0) AS coefficient,
                        COALESCE(sm.duree, 120) AS duree,
                        COALESCE(sm.nb_surveillants_requis, 1) AS nb_surveillants_requis,
                        COALESCE(sm.a_examen_final, true) AS a_examen_final,
                        COALESCE(sm.a_ds, true) AS a_ds
                    FROM section_matieres sm
                    ORDER BY sm.section_id, sm.id
                    """
                )
            ).mappings().all()

            section_label_by_id = {
                int(item["section_id"]): item["label"]
                for sections in sections_by_niveau.values()
                for item in sections
            }

            for row in mat_rows:
                section_label = section_label_by_id.get(int(row["section_id"]))
                if not section_label:
                    continue
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

        elif has_planifs:
            section_rows = db.execute(
                text(
                    """
                    SELECT
                        section_id,
                        COALESCE(MAX(section_nb_etudiants), 0) AS effectif
                    FROM planifications
                    GROUP BY section_id
                    ORDER BY section_id
                    """
                )
            ).mappings().all()

            for row in section_rows:
                section_id = int(row["section_id"])
                label = f"Section-{section_id}"
                niveau = _derive_niveau_from_label_or_id(label, section_id)
                sections_by_niveau.setdefault(niveau, []).append(
                    {
                        "label": label,
                        "section_id": section_id,
                        "effectif": int(row["effectif"]),
                        "niveau": niveau,
                    }
                )
                matieres_by_section[label] = []

            mat_rows = db.execute(
                text(
                    """
                    SELECT
                        section_id,
                        section_matiere_id,
                        matiere,
                        COALESCE(MAX(coefficient), 1.0) AS coefficient,
                        COALESCE(MAX(duree), 120) AS duree,
                        COALESCE(MAX(nb_surveillants_requis), 1) AS nb_surveillants_requis,
                        SUM(CASE WHEN type_epreuve = 'EXAMEN_FINAL' THEN 1 ELSE 0 END) AS has_exam,
                        SUM(CASE WHEN type_epreuve = 'DS' THEN 1 ELSE 0 END) AS has_ds
                    FROM planifications
                    GROUP BY section_id, section_matiere_id, matiere
                    ORDER BY section_id, section_matiere_id
                    """
                )
            ).mappings().all()

            for row in mat_rows:
                section_label = f"Section-{int(row['section_id'])}"
                matieres_by_section.setdefault(section_label, []).append(
                    {
                        "section_matiere_id": int(row["section_matiere_id"]),
                        "matiere": str(row["matiere"]),
                        "coefficient": float(row["coefficient"]),
                        "duree": int(row["duree"]),
                        "nb_surveillants_requis": int(row["nb_surveillants_requis"]),
                        "a_examen_final": int(row["has_exam"]) > 0,
                        "a_ds": int(row["has_ds"]) > 0,
                    }
                )

        salles: list[dict[str, Any]] = []
        if has_real_salle:
            rows = db.execute(
                text(
                    """
                    SELECT
                        COALESCE(code, CAST(id AS TEXT)) AS salle_id,
                        COALESCE(capacite, 0) AS capacite,
                        COALESCE(batiment, '') AS batiment
                    FROM salle
                    ORDER BY salle_id
                    """
                )
            ).mappings().all()
            for row in rows:
                salles.append(
                    {
                        "salle_id": str(row["salle_id"]),
                        "capacite": int(row["capacite"]),
                        "batiment": str(row["batiment"]),
                    }
                )
        elif _table_exists(db, "salles"):
            rows = db.execute(
                text(
                    """
                    SELECT
                        COALESCE(code, CAST(id AS TEXT)) AS salle_id,
                        COALESCE(capacite, 0) AS capacite,
                        COALESCE(batiment, '') AS batiment
                    FROM salles
                    ORDER BY salle_id
                    """
                )
            ).mappings().all()
            for row in rows:
                salles.append(
                    {
                        "salle_id": str(row["salle_id"]),
                        "capacite": int(row["capacite"]),
                        "batiment": str(row["batiment"]),
                    }
                )
        elif has_planif_salle:
            capacite_expr = "COALESCE(MAX(salle_capacite), 0)" if "salle_capacite" in planif_salle_cols else "0"
            batiment_expr = "COALESCE(MAX(salle_batiment), '')" if "salle_batiment" in planif_salle_cols else "''"
            rows = db.execute(
                text(
                    f"""
                    SELECT
                        salle_id,
                        {capacite_expr} AS capacite,
                        {batiment_expr} AS batiment
                    FROM planif_salle
                    GROUP BY salle_id
                    ORDER BY salle_id
                    """
                )
            ).mappings().all()
            for row in rows:
                salles.append(
                    {
                        "salle_id": str(row["salle_id"]),
                        "capacite": int(row["capacite"]),
                        "batiment": str(row["batiment"]),
                    }
                )

        creneaux: list[dict[str, Any]] = []
        if has_real_creneau:
            rows = db.execute(
                text(
                    """
                    SELECT date AS date_examen, heure_debut, heure_fin
                    FROM creneau
                    ORDER BY date, heure_debut
                    """
                )
            ).mappings().all()
            for row in rows:
                creneaux.append(
                    {
                        "date_examen": str(row["date_examen"]),
                        "heure_debut": str(row["heure_debut"]),
                        "heure_fin": str(row["heure_fin"]),
                    }
                )
        elif _table_exists(db, "creneaux"):
            rows = db.execute(
                text(
                    """
                    SELECT date_examen, heure_debut, heure_fin
                    FROM creneaux
                    ORDER BY date_examen, heure_debut
                    """
                )
            ).mappings().all()
            for row in rows:
                creneaux.append(
                    {
                        "date_examen": str(row["date_examen"]),
                        "heure_debut": str(row["heure_debut"]),
                        "heure_fin": str(row["heure_fin"]),
                    }
                )
        elif has_planifs:
            rows = db.execute(
                text(
                    """
                    SELECT DISTINCT date_examen, heure_debut, heure_fin
                    FROM planifications
                    ORDER BY date_examen, heure_debut
                    """
                )
            ).mappings().all()
            for row in rows:
                creneaux.append(
                    {
                        "date_examen": str(row["date_examen"]),
                        "heure_debut": str(row["heure_debut"]),
                        "heure_fin": str(row["heure_fin"]),
                    }
                )

        if not sessions:
            sessions = fallback["sessions"]
        if not sections_by_niveau:
            sections_by_niveau = fallback["sections_by_niveau"]
            matieres_by_section = fallback["matieres_by_section"]
        if not salles:
            salles = fallback["salles"]
        if not creneaux:
            creneaux = fallback["creneaux"]

        is_partial = (
            sessions == fallback["sessions"]
            or sections_by_niveau == fallback["sections_by_niveau"]
            or salles == fallback["salles"]
            or creneaux == fallback["creneaux"]
        )

        niveaux = sorted(sections_by_niveau.keys())
        for niveau in sections_by_niveau:
            sections_by_niveau[niveau] = sorted(sections_by_niveau[niveau], key=lambda x: x["label"])

        return {
            "source": "database-partial" if is_partial else "database",
            "connected": True,
            "message": (
                "Connexion BD OK. Catalogue charge depuis la base."
                if not is_partial
                else "Connexion BD OK. Catalogue partiellement charge depuis la base (composants manquants completes par fallback)."
            ),
            "sessions": sessions,
            "niveaux": niveaux,
            "sections_by_niveau": sections_by_niveau,
            "matieres_by_section": matieres_by_section,
            "salles": salles,
            "creneaux": creneaux,
        }
    except Exception as exc:
        fallback["message"] = f"Erreur chargement BD: {exc}. Fallback local applique."
        return fallback
    finally:
        db.close()


def _parse_json_array(raw: str, field_name: str) -> list[dict[str, Any]]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name}: JSON invalide ({exc})") from exc

    if not isinstance(value, list):
        raise ValueError(f"{field_name}: un tableau JSON est attendu.")

    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{field_name}[{i}]: objet JSON attendu.")

    return value


def _sections_for_niveau(catalogue: dict[str, Any], niveau: str) -> list[str]:
    items = catalogue.get("sections_by_niveau", {}).get(niveau, [])
    return [item["label"] for item in items]


def _build_tasks_for_admin(
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
    if type_epreuve_label not in TYPE_EP_CHOICES:
        raise ValueError("Type d'epreuve invalide.")

    type_epreuve = TYPE_EP_CHOICES[type_epreuve_label]
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
        raise ValueError(
            "Aucune matiere eligible pour cette section et ce type d'epreuve."
        )

    return tasks


def _db_status_message() -> str:
    db = SessionLocal()
    try:
        ok = check_connection(db)
        if ok:
            return "Connexion BD: OK"
        return "Connexion BD: echec"
    except Exception as exc:
        return f"Connexion BD: erreur ({exc})"
    finally:
        db.close()


def _section_details_markdown(catalogue: dict[str, Any], section_label: str) -> str:
    section_by_label = {
        item["label"]: item
        for sections in catalogue.get("sections_by_niveau", {}).values()
        for item in sections
    }
    section = section_by_label.get(section_label)
    matieres = catalogue.get("matieres_by_section", {}).get(section_label, [])

    if not section:
        return "### Section\n- Section introuvable"

    lines = [
        "### Section selectionnee",
        f"- Libelle: **{section['label']}**",
        f"- Niveau: **{section['niveau']}**",
        f"- Effectif: **{section['effectif']}**",
        f"- Matieres disponibles: **{len(matieres)}**",
    ]
    for mat in matieres:
        ep = []
        if mat.get("a_examen_final", False):
            ep.append("Examen Final")
        if mat.get("a_ds", False):
            ep.append("DS")
        ep_txt = "/".join(ep) if ep else "Aucune"
        lines.append(
            f"- {mat['matiere']} (coef {mat['coefficient']}, duree {mat['duree']} min, types {ep_txt})"
        )
    return "\n".join(lines)


def _refresh_catalogue_and_ui() -> tuple[dict[str, Any], str, gr.Dropdown, gr.Dropdown, str, str, str, dict[str, Any], str]:
    catalogue = _load_catalogue_from_db()
    niveaux = catalogue.get("niveaux") or DEFAULT_NIVEAUX
    niveau_value = niveaux[0] if niveaux else None

    sections = _sections_for_niveau(catalogue, niveau_value) if niveau_value else []
    section_value = sections[0] if sections else None

    sessions = catalogue.get("sessions", [])
    session_labels = [s["label"] for s in sessions]
    session_value = session_labels[0] if session_labels else None

    creneaux = catalogue.get("creneaux") or SAMPLE_CRENEAUX
    salles = catalogue.get("salles") or SAMPLE_SALLES

    status_md = (
        "### Etat BD\n"
        f"- {_db_status_message()}\n"
        f"- Source catalogue: **{catalogue.get('source', 'unknown')}**\n"
        f"- Detail: {catalogue.get('message', '')}"
    )
    details_md = _section_details_markdown(catalogue, section_value) if section_value else "### Section\n- Aucune"

    return (
        catalogue,
        status_md,
        gr.update(choices=session_labels, value=session_value),
        gr.update(choices=niveaux, value=niveau_value),
        json.dumps(creneaux, indent=2, ensure_ascii=True),
        json.dumps(salles, indent=2, ensure_ascii=True),
        details_md,
        {
            "sessions": sessions,
            "niveaux": niveaux,
            "sections_by_niveau": catalogue.get("sections_by_niveau", {}),
            "salles": salles,
            "creneaux": creneaux,
        },
        catalogue.get("message", ""),
    )


def _on_niveau_change(catalogue: dict[str, Any], niveau: str):
    sections = _sections_for_niveau(catalogue, niveau)
    if not sections:
        return gr.update(choices=[], value=None), "### Section\n- Aucune section pour ce niveau"
    section_value = sections[0]
    return gr.update(choices=sections, value=section_value), _section_details_markdown(catalogue, section_value)


def _on_section_change(catalogue: dict[str, Any], section_label: str):
    return _section_details_markdown(catalogue, section_label)


def _update_button_text(save_to_db: bool) -> gr.Button:
    """Mettre à jour le texte du bouton selon le mode."""
    if save_to_db:
        return gr.update(value="💾 Generer et SAUVEGARDER en base de données", variant="secondary")
    return gr.update(value="🚀 Generer en mode SIMULATION (pas de sauvegarde)", variant="primary")


def _run_draft_generation(
    catalogue: dict[str, Any],
    session_label: str,
    niveau_label: str,
    section_label: str,
    type_epreuve_label: str,
    creneaux_json: str,
    salles_json: str,
    enregistrer_db: bool,
) -> tuple[str, dict[str, Any], str]:
    """Execute generation in dry-run mode (no DB writes)."""
    try:
        sessions_by_label = {s["label"]: s for s in catalogue.get("sessions", [])}
        if session_label not in sessions_by_label:
            raise ValueError("Session inconnue.")

        session = sessions_by_label[session_label]

        section_info = None
        for sections in catalogue.get("sections_by_niveau", {}).values():
            for section in sections:
                if section["label"] == section_label:
                    section_info = section
                    break
            if section_info:
                break

        if not section_info:
            raise ValueError("Section inconnue.")
        if section_info["niveau"] != niveau_label:
            raise ValueError("La section selectionnee ne correspond pas au niveau choisi.")

        tasks = _build_tasks_for_admin(catalogue, section_label, type_epreuve_label)
        creneaux = _parse_json_array(creneaux_json, "creneaux")
        salles = _parse_json_array(salles_json, "salles")

        existing_planifs = []
        db = None
        db_status_msg = "Connexion BD non testee"
        try:
            db = SessionLocal()
            if check_connection(db):
                existing_planifs = _load_existing_for_generation(db, int(session["session_id"]))
                db_status_msg = "Connexion BD OK"
            else:
                db_status_msg = "Connexion BD echec"
        except Exception as exc:
            db_status_msg = f"Connexion BD erreur: {exc}"
        finally:
            if db:
                db.close()

        request = GenerationRequest(
            session_id=int(session["session_id"]),
            session_date_debut=date.fromisoformat(session["date_debut"]),
            session_date_fin=date.fromisoformat(session["date_fin"]),
            session_statut=session["statut"],
            mode="AUTO",
            tasks=tasks,
            creneaux=creneaux,
            salles=salles,
        )

        creates, result = generer(
            request=request,
            engine=build_default_engine(),
            existing_planifs=existing_planifs,
            db=None,
            known_section_matiere_ids={t["section_matiere_id"] for t in tasks if "section_matiere_id" in t},
        )

        nb_saved = 0
        save_errors: list[str] = []
        if enregistrer_db:
            save_db = SessionLocal()
            try:
                if not check_connection(save_db):
                    save_errors.append("Connexion BD indisponible: sauvegarde annulee.")
                else:
                    if _table_exists(save_db, "planifications"):
                        for payload in creates:
                            try:
                                create_planification(save_db, payload)
                                nb_saved += 1
                            except Exception as exc:
                                save_errors.append(f"{payload.matiere}: {exc}")
                    else:
                        saved, errs = _save_generated_to_real_schema(save_db, creates)
                        nb_saved += saved
                        save_errors.extend(errs)
            finally:
                save_db.close()

        created_payload = [item.model_dump(mode="json") for item in creates]
        summary = (
            "### Resultat de simulation\n"
            f"- Session: **{session_label}**\n"
            f"- Niveau: **{niveau_label}**\n"
            f"- Section: **{section_label}**\n"
            f"- Type epreuve: **{type_epreuve_label}**\n"
            f"- Planifications generees: **{result.nb_crees}**\n"
            f"- Conflits detectes: **{result.nb_conflits}**\n"
            f"- {db_status_msg}\n"
            f"- Sauvegarde BD demandee: **{'Oui' if enregistrer_db else 'Non'}**\n"
            f"- Planifications sauvegardees: **{nb_saved}**"
        )

        conflits_md = (
            "\n".join(f"- {msg}" for msg in result.conflits)
            if result.conflits
            else "- Aucun conflit detecte"
        )

        if save_errors:
            conflits_md = conflits_md + "\n" + "\n".join(f"- Erreur sauvegarde: {msg}" for msg in save_errors)

        return summary, {
            "planifications": created_payload,
            "rapport": result.model_dump(mode="json"),
            "sauvegarde": {
                "requested": enregistrer_db,
                "saved": nb_saved,
                "errors": save_errors,
            },
        }, conflits_md

    except Exception as exc:
        return (
            "### Erreur de simulation",
            {"error": str(exc)},
            f"- {exc}",
        )


def create_app() -> gr.Blocks:
    """Build the Gradio UI for draft-only planification tests."""
    with gr.Blocks(title="Draft Planification Examens") as demo:
        catalogue_state = gr.State(_default_catalogue())

        gr.Markdown(
            "# 🎨 Draft Planification Examens\n"
            "Interface de test (Gradio) pour la generation automatique.\n\n"
            "⚠️ **MODE PAR DÉFAUT : SIMULATION (pas de sauvegarde en BD)**\n"
            "✅ Cochez la case ci-dessous pour sauvegarder en base de données.\n\n"
            "L'admin choisit des valeurs lisibles: **niveau, section, session, type d'epreuve**."
        )

        status_md = gr.Markdown("### Etat BD\n- Verification en attente")
        with gr.Row():
            refresh_btn = gr.Button("🔄 Charger donnees reelles (BD)")
            save_to_db = gr.Checkbox(
                label="💾 Sauvegarder en base apres generation (DÉCOCHÉ = mode simulation)", 
                value=False,
                info="Décoché par défaut pour éviter les doublons"
            )
        catalogue_json = gr.JSON(label="Catalogue charge (sessions/niveaux/sections/salles/creneaux)")
        refresh_info = gr.Markdown()

        with gr.Row():
            session_label = gr.Dropdown(
                choices=[],
                value=None,
                label="Session",
            )
            niveau_label = gr.Dropdown(
                choices=[],
                value=None,
                label="Niveau",
            )
            section_label = gr.Dropdown(
                choices=[],
                value=None,
                label="Section",
            )
            type_epreuve_label = gr.Dropdown(
                choices=sorted(TYPE_EP_CHOICES.keys()),
                value="Examen Final",
                label="Type epreuve",
            )

        section_md = gr.Markdown("### Section\n- Aucune")

        niveau_label.change(
            fn=_on_niveau_change,
            inputs=[catalogue_state, niveau_label],
            outputs=[section_label, section_md],
        )
        section_label.change(
            fn=_on_section_change,
            inputs=[catalogue_state, section_label],
            outputs=[section_md],
        )
        
        save_to_db.change(
            fn=_update_button_text,
            inputs=[save_to_db],
            outputs=[btn],
        )

        creneaux_json = gr.Code(
            value=json.dumps(SAMPLE_CRENEAUX, indent=2, ensure_ascii=True),
            language="json",
            label="creneaux (JSON)",
        )
        salles_json = gr.Code(
            value=json.dumps(SAMPLE_SALLES, indent=2, ensure_ascii=True),
            language="json",
            label="salles (JSON)",
        )

        btn = gr.Button("🚀 Generer en mode SIMULATION (pas de sauvegarde)", variant="primary", size="lg")

        summary = gr.Markdown(label="Resume")
        out_json = gr.JSON(label="Planifications generees (non persistees)")
        conflits = gr.Markdown(label="Conflits")

        btn.click(
            fn=_run_draft_generation,
            inputs=[
                catalogue_state,
                session_label,
                niveau_label,
                section_label,
                type_epreuve_label,
                creneaux_json,
                salles_json,
                save_to_db,
            ],
            outputs=[summary, out_json, conflits],
        )

        refresh_btn.click(
            fn=_refresh_catalogue_and_ui,
            inputs=[],
            outputs=[
                catalogue_state,
                status_md,
                session_label,
                niveau_label,
                creneaux_json,
                salles_json,
                section_md,
                catalogue_json,
                refresh_info,
            ],
        )

        demo.load(
            fn=_refresh_catalogue_and_ui,
            inputs=[],
            outputs=[
                catalogue_state,
                status_md,
                session_label,
                niveau_label,
                creneaux_json,
                salles_json,
                section_md,
                catalogue_json,
                refresh_info,
            ],
        )

    return demo


demo = create_app()


if __name__ == "__main__":
    demo.launch()
