"""Gradio draft interface .
Usage:
    python -m app.gradio_surveillance_draft

"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:root001727@localhost:5432/PFA"
engine       = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    return SessionLocal()


def close_db(db):
    try:
        db.close()
    except Exception:
        pass


def err(e: Exception) -> str:
    return f"❌ **Erreur** : `{type(e).__name__}` — {e}"


def _extract_id(label: str | None) -> int | None:
    if not label:
        return None
    try:
        return int(label.split("]")[0].replace("[", "").strip())
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# LOADERS
# ═════════════════════════════════════════════════════════════════════════════

def load_sessions() -> list[str]:
    db = get_db()
    try:
        from app.models.salle_session import Session as SessionModel
        rows = db.query(SessionModel).order_by(SessionModel.id.desc()).all()
        return [
            f"[{s.id}] {s.type_session} — {s.annee_universitaire} ({s.statut})"
            for s in rows
        ]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


def load_enseignants() -> list[str]:
    db = get_db()
    try:
        from app.models.enseignant import Enseignant
        rows = db.query(Enseignant).order_by(Enseignant.nom, Enseignant.prenom).all()
        return [
            f"[{e.id}] {e.prenom} {e.nom} — {e.grade or '—'} "
            f"({e.departement.code if e.departement else '—'})"
            for e in rows
        ]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


def load_planifications(session_id: int | None = None) -> list[str]:
    db = get_db()
    try:
        from app.models.planification import Planification
        q = db.query(Planification).filter(Planification.statut == "VALIDEE")
        if session_id:
            q = q.filter(Planification.session_id == session_id)
        rows = q.order_by(Planification.id).all()
        result = []
        for p in rows:
            sm  = p.section_matiere
            mat = sm.matiere if sm else None
            sec = sm.section if sm else None
            cr  = p.creneau
            label = (
                f"[{p.id}] {mat.code if mat else '?'} — "
                f"{p.type_epreuve} S{p.semestre} — "
                f"{sec.nom if sec else '?'} — "
                f"{cr.date if cr else '?'} {str(cr.heure_debut)[:5] if cr else ''}"
            )
            result.append(label)
        return result or ["(aucune planification VALIDEE)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


def load_surveillances(session_id: int | None = None) -> list[str]:
    db = get_db()
    try:
        from app.models.surveillance import Surveillance
        from app.models.planification import Planification
        q = (
            db.query(Surveillance)
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
        )
        if session_id:
            q = q.filter(Planification.session_id == session_id)
        rows = q.order_by(Surveillance.id).limit(300).all()
        result = []
        for s in rows:
            ens    = s.enseignant
            planif = s.planification
            sm     = planif.section_matiere if planif else None
            mat    = sm.matiere if sm else None
            label  = (
                f"[{s.id}] "
                f"{ens.prenom} {ens.nom} — " if ens else f"[{s.id}] ENS? — "
            )
            label += (
                f"{mat.code if mat else '?'} — "
                f"{planif.type_epreuve if planif else '?'} — "
                f"{s.statut_surveillance}"
            )
            result.append(label)
        return result or ["(aucune surveillance)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


def load_sections() -> list[str]:
    db = get_db()
    try:
        from app.models.departement_niveau_section import Section
        rows = db.query(Section).order_by(Section.nom).all()
        return [
            f"[{s.id}] {s.nom} "
            f"({s.niveau.libelle if s.niveau else '?'} — "
            f"{s.niveau.departement.code if s.niveau and s.niveau.departement else '?'})"
            for s in rows
        ] or ["(aucune section)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


def load_periodes() -> list[str]:
    db = get_db()
    try:
        from app.models.salle_session import Session as SessionModel
        from app.models.planification import Planification
        from sqlalchemy import distinct
        rows = db.query(
            distinct(SessionModel.annee_universitaire),
            Planification.semestre,
        ).join(
            Planification, Planification.session_id == SessionModel.id
        ).all()

        seen     = set()
        periodes = []
        for annee, sem in rows:
            key = f"{annee}-S{sem}"
            if key not in seen:
                seen.add(key)
                periodes.append(key)
        periodes.sort()
        return periodes or ["(aucune période)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


def load_types_epreuve() -> list[str]:
    db = get_db()
    try:
        from app.models.planification import Planification
        from sqlalchemy import distinct
        rows = db.query(distinct(Planification.type_epreuve)).all()
        return [r[0] for r in rows if r[0]] or ["EXAMEN_FINAL", "DS"]
    except Exception:
        return ["EXAMEN_FINAL", "DS"]
    finally:
        close_db(db)


def load_groupes(planif_id: int | None = None) -> list[str]:
    db = get_db()
    try:
        from app.models.planification import PlanifSalle
        if not planif_id:
            from app.models.departement_niveau_section import Groupe
            rows = db.query(Groupe).order_by(Groupe.id).all()
            return [
                f"[{g.id}] Groupe {g.numero} (effectif: {g.effectif})"
                for g in rows
            ] or ["(aucun groupe)"]
        rows = db.query(PlanifSalle).filter(
            PlanifSalle.planification_id == planif_id
        ).all()
        result = []
        for ps in rows:
            g = ps.groupe
            if g:
                result.append(f"[{g.id}] Groupe {g.numero} (effectif: {g.effectif})")
        return result or ["(aucun groupe pour cette planification)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


def load_annees_univ() -> list[str]:
    db = get_db()
    try:
        from app.models.salle_session import Session as SessionModel
        from sqlalchemy import distinct
        rows = db.query(distinct(SessionModel.annee_universitaire)).all()
        return sorted([r[0] for r in rows if r[0]], reverse=True) or ["2025/2026"]
    except Exception:
        return ["2025/2026"]
    finally:
        close_db(db)

def load_groupes_all() -> list[str]:
    db = get_db()
    try:
        from app.models.departement_niveau_section import Groupe
        rows = db.query(Groupe).order_by(Groupe.id).all()
        return [f"[{g.id}] Groupe {g.numero} (eff: {g.effectif})" for g in rows] or ["(aucun)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)

def load_salles() -> list[str]:
    db = get_db()
    try:
        from app.models.salle_session import Salle
        rows = db.query(Salle).order_by(Salle.code).all()
        return [f"[{s.id}] {s.code} — {s.designation or '—'}" for s in rows] or ["(aucune)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)

def load_departements() -> list[str]:
    db = get_db()
    try:
        from app.models.departement_niveau_section import Departement
        rows = db.query(Departement).order_by(Departement.nom).all()
        return [f"[{d.id}] {d.nom} ({d.code})" for d in rows] or ["(aucun)"]
    except Exception as e:
        return [f"[ERREUR] {e}"]
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# Chargement initial
# ═════════════════════════════════════════════════════════════════════════════

_SESSIONS       = load_sessions()
_ENSEIGNANTS    = load_enseignants()
_PLANIFICATIONS = load_planifications()
_SURVEILLANCES  = load_surveillances()
_SECTIONS       = load_sections()
_PERIODES       = load_periodes()
_TYPES_EPREUVE  = load_types_epreuve()
_GROUPES        = load_groupes()
_ANNEES_UNIV    = load_annees_univ()

_GROUPES_ALL    = load_groupes_all()
_SALLES         = load_salles()
_DEPARTEMENTS   = load_departements()


_S0   = _SESSIONS[0]       if _SESSIONS       else None
_E0   = _ENSEIGNANTS[0]    if _ENSEIGNANTS     else None
_P0   = _PLANIFICATIONS[0] if _PLANIFICATIONS  else None
_SU0  = _SURVEILLANCES[0]  if _SURVEILLANCES   else None
_SEC0 = _SECTIONS[0]       if _SECTIONS        else None
_PER0 = _PERIODES[0]       if _PERIODES        else None
_TE0  = _TYPES_EPREUVE[0]  if _TYPES_EPREUVE   else None
_G0   = _GROUPES[0]        if _GROUPES         else None
_AN0  = _ANNEES_UNIV[0]    if _ANNEES_UNIV     else None


# ═════════════════════════════════════════════════════════════════════════════
# Rafraîchissement
# ═════════════════════════════════════════════════════════════════════════════

def refresh_sessions():
    data = load_sessions()
    return gr.update(choices=data, value=data[0] if data else None)

def refresh_enseignants():
    data = load_enseignants()
    return gr.update(choices=data, value=data[0] if data else None)

def refresh_planifications_for_session(session_label: str):
    sid  = _extract_id(session_label)
    data = load_planifications(sid)
    return gr.update(choices=data, value=data[0] if data else None)

def refresh_surveillances_for_session(session_label: str):
    sid  = _extract_id(session_label)
    data = load_surveillances(sid)
    return gr.update(choices=data, value=data[0] if data else None)

def refresh_groupes_for_planif(planif_label: str):
    pid  = _extract_id(planif_label)
    data = load_groupes(pid)
    return gr.update(choices=data, value=data[0] if data else None)

def refresh_periodes():
    data = load_periodes()
    return gr.update(choices=data, value=data[0] if data else None)

def refresh_sections():
    data = load_sections()
    return gr.update(choices=data, value=data[0] if data else None)

def refresh_annees():
    data = load_annees_univ()
    return gr.update(choices=data, value=data[0] if data else None)


# ═════════════════════════════════════════════════════════════════════════════
# S1 — AFFECTATION AUTOMATIQUE
# ═════════════════════════════════════════════════════════════════════════════

def lancer_affectation_auto(
    session_label: str,
    section_label: str,
    periode_label: str,
    ep_label:      str,
) -> tuple[str, str]:
    """► POST /surveillances/affecter-session"""
    db  = get_db()
    sid = _extract_id(session_label)
    if not sid:
        return "❌ Veuillez sélectionner une session.", ""

    # ── Extraction section_nom depuis '[id] NOM (...)'
    section_nom = None
    if section_label and "[ERREUR]" not in section_label:
        try:
            section_nom = section_label.split("]")[1].strip().split("(")[0].strip()
        except Exception:
            section_nom = None

    # ── Extraction période
    periode = periode_label.strip() if periode_label and "[ERREUR]" not in periode_label else None

    # ── Extraction type épreuve
    type_epreuve = ep_label.strip() if ep_label and "[ERREUR]" not in ep_label else None

    # ── Validation — tous obligatoires
    manquants = []
    if not section_nom:
        manquants.append("Section")
    if not periode:
        manquants.append("Période")
    if not type_epreuve:
        manquants.append("Type d'épreuve")

    if manquants:
        return (
            f"❌ Champs obligatoires manquants : **{', '.join(manquants)}**\n\n"
            f"Veuillez sélectionner une valeur pour chacun avant de lancer l'affectation.",
            ""
        )

    try:
        from app.services.surv_service import SurvService

        service = SurvService(db)
        results, message = service.affecter_session_automatique(
            session_id=sid,
            section_nom=section_nom,
            periode=periode,
            type_epreuve=type_epreuve,
        )

        nb_ok  = sum(1 for r in results if r.statut == "AFFECTEE")
        nb_ko  = sum(1 for r in results if r.statut != "AFFECTEE")
        nb_tot = len(results)

        lignes = [
            "| Planif | Matière | Section | Type | Date | Statut | Affectés/Requis | Manquants |",
            "|:---:|---|---|---|---|:---:|:---:|:---:|",
        ]
        for r in results:
            icon = "✅" if r.statut == "AFFECTEE" else ("⚠️" if r.statut == "CONFLIT_PARTIEL" else "❌")
            lignes.append(
                f"| {r.planification_id} | `{r.matiere_code}` | {r.section_nom} "
                f"| {r.type_epreuve} | {r.creneau_date or '—'} "
                f"| {icon} {r.statut} "
                f"| {len(r.surveillants_affectes)}/{r.surveillants_requis} "
                f"| {r.manquants} |"
            )

        resume = (
            f"## ✅ Résultat — `POST /surveillances/affecter-session`\n\n"
            f"> **Session {sid}** | Section: `{section_nom}` | "
            f"Période: `{periode}` | Type: `{type_epreuve}`\n\n"
            f"_{message}_\n\n"
            f"**{nb_ok}/{nb_tot}** affectée(s) | **{nb_ko}** en conflit\n\n"
        ) + "\n".join(lignes)

        detail_lines = ["## Détail par groupe / salle\n"]
        for r in results:
            icon = "✅" if r.statut == "AFFECTEE" else ("⚠️" if r.statut == "CONFLIT_PARTIEL" else "❌")
            detail_lines.append(
                f"### {icon} Planif #{r.planification_id} — "
                f"{r.matiere_intitule or r.matiere_code} ({r.type_epreuve})\n"
                f"*{r.section_nom} | {r.creneau_date or '—'} {r.creneau_heure or ''}*\n"
            )
            for g in r.groupes:
                g_icon = "✅" if g.statut == "AFFECTEE" else "❌"
                detail_lines.append(
                    f"- {g_icon} **Groupe {g.groupe_numero or g.groupe_id or '—'}** "
                    f"| Salle `{g.salle_code or g.salle_id or '—'}` → "
                    f"{len(g.surveillants_affectes)}/{g.surveillants_requis} surveillant(s)"
                )
                for surv_orm in g.surveillants_affectes:
                    ens        = getattr(surv_orm, "enseignant", None)
                    nom        = f"{ens.prenom} {ens.nom}" if ens else f"ENS#{surv_orm.enseignant_id}"
                    grade      = ens.grade if ens else "—"
                    dept       = ens.departement.code if ens and ens.departement else "—"
                    charge_val = float(surv_orm.charge) if surv_orm.charge else 0.0
                    detail_lines.append(
                        f"  - 👤 **{nom}** ({grade}) [{dept}] "
                        f"— charge : **{charge_val:.2f}h**"
                        + (" ⚠️ *externe*" if surv_orm.est_externe else "")
                    )
                if g.manquants:
                    detail_lines.append(f"  - ⚠️ **{g.manquants} surveillant(s) manquant(s)**")
            if r.violations:
                detail_lines.append(f"\n> **{len(r.violations)} exclusion(s)** :")
                for v in r.violations[:10]:
                    raison = v.raison.value if hasattr(v.raison, "value") else str(v.raison)
                    detail_lines.append(
                        f">   - {v.nom} {v.prenom} → `{raison}`"
                        + (f" — _{v.details}_" if v.details else "")
                    )
            detail_lines.append("")

        non_aff = [r for r in results if r.statut == "CONFLIT" and len(r.surveillants_affectes) == 0]
        if non_aff:
            detail_lines.append(f"\n---\n## ❌ Planifications sans aucun surveillant ({len(non_aff)})\n")
            for r in non_aff:
                detail_lines.append(
                    f"- **Planif #{r.planification_id}** — `{r.matiere_code}` "
                    f"| {r.section_nom} | {r.type_epreuve} | {r.creneau_date or '—'}"
                )

        return resume, "\n".join(detail_lines)

    except Exception as e:
        return err(e), ""
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S2 — PROFIL COMPLET ENSEIGNANT
# ═════════════════════════════════════════════════════════════════════════════

def get_profil_enseignant(ens_label: str, annee_label: str, sem_label:   str = "(tous)", ep_label: str = "(tous)",) -> tuple[str, str]:
    db  = get_db()
    eid = _extract_id(ens_label)
    if not eid:
        return "❌ Veuillez sélectionner un enseignant.", ""
    try:
        from app.crud.crud_surv import get_surveillances_enrichies_for_enseignant
        annee = annee_label.strip() if annee_label and "(aucune" not in annee_label else None
        semestre     = int(sem_label) if sem_label not in ("(tous)", "", None) else None
        type_epreuve = ep_label if ep_label not in ("(tous)", "", None) else None
        data = get_surveillances_enrichies_for_enseignant(
            db, eid, annee,
            semestre=semestre,
            type_epreuve=type_epreuve,
        )

        if not data:
            return f"❌ Enseignant #{eid} non trouvé.", ""

        ens   = data["enseignant"]
        ch    = data["charge_horaire"]
        stats = data["statistiques"]
        survs = data["surveillances"]

        pct   = ch["taux_utilisation"]
        barre = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

        fiche = (
            f"## 👤 {ens['nom_complet']}\n\n"
            f"| Champ | Valeur |\n|---|---|\n"
            f"| Grade | {ens['grade'] or '—'} |\n"
            f"| Email | {ens['email'] or '—'} |\n"
            f"| Téléphone | {ens['telephone'] or '—'} |\n"
            f"| Département | {ens['departement']['nom'] or '—'} "
            f"(`{ens['departement']['code'] or '—'}`) |\n\n"
            f"### Charge horaire — {ch['annee_universitaire'] or 'N/A'}\n\n"
            f"```\n{barre} {pct:.1f}%\n```\n\n"
            f"| | Valeur |\n|---|---|\n"
            f"| Volume alloué | **{ch['volume_horaire']:.2f}h** |\n"
            f"| Volume consommé | **{ch['volume_consomme']:.2f}h** |\n"
            f"| Volume restant | **{ch['volume_restant']:.2f}h** |\n\n"
            f"### Statistiques\n\n"
            f"- Total surveillances : **{stats['total_surveillances']}**\n"
            f"- Confirmées : **{stats['nb_confirmees']}** | "
            f"Présences : **{stats['nb_presences']}** | "
            f"Externes : **{stats['nb_externes']}**\n"
        )

        if not survs:
            return fiche, "_Aucune surveillance enregistrée._"

        lines = [
                f"## Détail des surveillances ({len(survs)})\n",
                "| # | Date | Horaire | Matière | Type | Sem. | Groupe | Salle | Charge | Statut | Présence | Dept Exam |",
                "|:---:|---|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
            ]
        for i, item in enumerate(survs, 1):
            cr  = item["creneau"]
            mat = item["matiere"]
            grp = item["groupe"]
            sl  = item["salle"]
            sv  = item["surveillance"]
            pl  = item["planification"]
            de  = item["departement_examen"]   # ← ajoute cette ligne
            p   = "✅" if sv["presence"] else "—"
            st  = "✅ Confirmé" if sv["statut_surveillance"] == "CONFIRME" else "🟡 Affecté"
            lines.append(
                f"| {i} | {cr['date'] or '—'} "
                f"| {str(cr['heure_debut'] or '')[:5]}–{str(cr['heure_fin'] or '')[:5]} "
                f"| {mat['intitule'] or '—'} "
                f"| {pl['type_epreuve'] or '—'} "
                f"| S{pl['semestre'] or '—'} "
                f"| Gr.{grp['numero'] or '—'} "
                f"| {sl['code'] or '—'} "
                f"| {sv['charge']:.2f}h "
                f"| {st} | {p} "
                f"| {de['nom'] or '—'} |"   # ← ajoute ça
            )
        return fiche, "\n".join(lines)
    except Exception as e:
        return err(e), ""
    finally:
        close_db(db)

# ═════════════════════════════════════════════════════════════════════════════
# S3 — LISTE DES SURVEILLANCES D'UNE SESSION
# ═════════════════════════════════════════════════════════════════════════════
def get_session_surveillances(
    session_label:   str,
    ep_label:        str,
    statut_label:    str,
    semestre_label:  str,
    groupe_label:    str,
    salle_label:     str,
    dept_label:      str,
    section_label:   str = "(tous)",
    enseignant_label: str = "(tous)",
) -> str:
    db  = get_db()
    sid = _extract_id(session_label)
    if not sid:
        return "❌ Veuillez sélectionner une session."
    try:
        from app.models.surveillance import Surveillance
        from app.models.planification import Planification
        from app.models.salle_session import Session as SessionModel, Creneau
        from app.models.matiere import SectionMatiere

        sess = db.query(SessionModel).filter(SessionModel.id == sid).first()
        if not sess:
            return f"❌ Session #{sid} non trouvée."

        type_ep    = ep_label      if ep_label      not in ("(tous)", "", None) else None
        statut     = statut_label  if statut_label  not in ("(tous)", "", None) else None
        semestre   = semestre_label if semestre_label not in ("(tous)", "", None) else None
        groupe_id  = _extract_id(groupe_label)  if groupe_label  not in ("(tous)", "", None) else None
        salle_id   = _extract_id(salle_label)   if salle_label   not in ("(tous)", "", None) else None
        dept_id    = _extract_id(dept_label)    if dept_label    not in ("(tous)", "", None) else None

        q = (
            db.query(Surveillance)
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(Creneau, Planification.creneau_id == Creneau.id)
            .filter(Planification.session_id == sid)
        )
        if type_ep:   q = q.filter(Planification.type_epreuve == type_ep)
        if statut:    q = q.filter(Surveillance.statut_surveillance == statut)
        if semestre:  q = q.filter(Planification.semestre == int(semestre))
        if groupe_id: q = q.filter(Surveillance.groupe_id == groupe_id)
        if salle_id:  q = q.filter(Surveillance.salle_id == salle_id)
        if dept_id:   q = q.filter(Planification.departement_id == dept_id)
        section_id_val  = _extract_id(section_label)   if section_label   not in ("(tous)", "", None) else None
        enseignant_id_v = _extract_id(enseignant_label) if enseignant_label not in ("(tous)", "", None) else None
        if section_id_val:  q = q.join(SectionMatiere, Planification.section_matiere_id == SectionMatiere.id).filter(SectionMatiere.section_id == section_id_val)
        if enseignant_id_v: q = q.filter(Surveillance.enseignant_id == enseignant_id_v)
        q = q.order_by(Creneau.date.asc(), Creneau.heure_debut.asc())

        total = q.count()
        survs = q.limit(150).all()

        lines = [
            f"## 📋 Surveillances — Session #{sid} ({sess.annee_universitaire})\n",
            f"**{total}** résultat(s) | type={type_ep or 'tous'} | statut={statut or 'tous'} | sem={semestre or 'tous'}\n",
            "| ID | Enseignant | Grade | Date | Section | Matière | Type | Sem. | Grp | Salle | Statut | Prés. |",
            "|:---:|---|---|---|---|---|---|:---:|:---:|:---:|:---:|:---:|",
        ]
        for s in survs:
            ens   = s.enseignant
            pl    = s.planification
            cren  = pl.creneau         if pl else None
            sm    = pl.section_matiere if pl else None
            mat   = sm.matiere         if sm else None
            sec   = sm.section         if sm else None  # ← AJOUT
            grp   = s.groupe
            salle = s.salle
            p_icon  = "✅" if s.presence else "—"
            st_icon = "✅" if s.statut_surveillance == "CONFIRME" else "🟡"
            lines.append(
                f"| {s.id} "
                f"| {ens.prenom + ' ' + ens.nom if ens else '—'} "
                f"| {ens.grade if ens else '—'} "
                f"| {cren.date if cren else '—'} "
                f"| {sec.nom if sec else '—'} "  # ← AJOUT
                f"| {mat.code if mat else '—'} "
                f"| {pl.type_epreuve if pl else '—'} "
                f"| S{pl.semestre if pl else '—'} "
                f"| Gr.{grp.numero if grp else '—'} "
                f"| {salle.code if salle else '—'} "
                f"| {st_icon} {s.statut_surveillance} | {p_icon} |"
            )
        return "\n".join(lines)
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S5 — DÉTAIL COMPLET D'UNE SURVEILLANCE
# ═════════════════════════════════════════════════════════════════════════════

def get_detail_surveillance(surv_label: str) -> str:
    db  = get_db()
    sid = _extract_id(surv_label)
    if not sid:
        return "❌ Veuillez sélectionner une surveillance."
    try:
        from app.crud.crud_surv import get_surveillance, _enrich_surveillance
        s = get_surveillance(db, sid)
        if not s:
            return f"❌ Surveillance #{sid} non trouvée."

        d    = _enrich_surveillance(db, s)
        sv   = d["surveillance"]
        ens  = d["enseignant"]
        pl   = d["planification"]
        cr   = d["creneau"]
        mat  = d["matiere"]
        sec  = d["section"]
        niv  = d["niveau"]
        grp  = d["groupe"]
        sl   = d["salle"]
        de   = d["departement_examen"]
        sess = d["session"]

        pct   = (ens["volume_consomme"] / ens["volume_horaire"] * 100
                 if ens["volume_horaire"] and ens["volume_horaire"] > 0 else 0)
        barre = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

        return (
            f"## 🔍 Surveillance #{sid}\n\n"
            f"### Statut & Charge\n"
            f"- Statut : **{sv['statut_surveillance']}** | Mode : **{sv['mode_affectation']}**\n"
            f"- Charge : **{sv['charge']:.2f}h** | Présence : **{'✅ Oui' if sv['presence'] else '❌ Non'}**\n"
            + (f"- ⚠️ Externe : _{sv['motif_externe']}_\n" if sv['est_externe'] else "")
            + f"\n### 👤 Enseignant\n"
            f"- **{ens['nom_complet']}** ({ens['grade'] or '—'})\n"
            f"- Email : {ens['email'] or '—'} | Tél : {ens['telephone'] or '—'}\n"
            f"- Département : {ens['departement']['nom'] or '—'} (`{ens['departement']['code'] or '—'}`)\n"
            f"- Volume : {ens['volume_horaire']:.1f}h alloué | "
            f"{ens['volume_consomme']:.2f}h consommé | **{ens['volume_restant']:.2f}h restant**\n"
            f"  ```\n  {barre} {pct:.1f}%\n  ```\n\n"
            f"### 📚 Session & Examen\n"
            f"- Session : **{sess['type_session']}** {sess['annee_universitaire']} "
            f"({sess['date_debut']} → {sess['date_fin']}) — _{sess['statut']}_\n"
            f"- Département exam : {de['nom'] or '—'} (`{de['code'] or '—'}`)\n"
            f"- Matière : **{mat['intitule'] or '—'}** (`{mat['code'] or '—'}`)\n"
            f"- Type : **{pl['type_epreuve']}** | Semestre : **S{pl['semestre']}** | Durée : {pl['duree']} min\n"
            f"- Section : {sec['nom'] or '—'} | Niveau : {niv['libelle'] or '—'}\n\n"
            f"### 🕐 Créneau\n"
            f"- **{cr['date'] or '—'}** | "
            f"{str(cr['heure_debut'] or '')[:5]} → {str(cr['heure_fin'] or '')[:5]}"
            + (f" | _{cr['libelle']}_" if cr['libelle'] else "") + "\n\n"
            f"### 🏫 Affectation\n"
            f"- Groupe : **{grp['numero'] or '—'}** (effectif : {grp['effectif'] or '—'})\n"
            f"- Salle : **{sl['code'] or '—'}** — {sl['designation'] or '—'} "
            f"| Cap. {sl['capacite'] or '—'} | Bât. {sl['batiment'] or '—'}\n"
        )
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S6 — ENSEIGNANTS DISPONIBLES
# ═════════════════════════════════════════════════════════════════════════════

def get_disponibles_planif(planif_label: str) -> str:
    db  = get_db()
    pid = _extract_id(planif_label)
    if not pid:
        return "❌ Veuillez sélectionner une planification."
    try:
        from app.services.surv_service import SurvService
        result = SurvService(db).get_enseignants_disponibles_pour_planification(pid)
        if not result:
            return f"_Planification #{pid} non trouvée._"

        lines = [
            f"## 👥 Enseignants disponibles — Planification #{pid}\n",
            f"Date : **{result.date_planification}** | "
            f"**{result.total_disponibles}** disponible(s) | "
            f"⚠️ **{result.total_avec_avertissement}** avec avertissement\n",
        ]

        i = 1
        for dept in result.departements:
            lines.append(
                f"\n### 🏛️ {dept.departement_nom or '—'} "
                f"(`{dept.departement_code or '—'}`) — {dept.total} enseignant(s)\n"
            )
            lines.append("| # | Nom | Grade | Vol. alloué | Consommé | Restant | Survs | Avertissement |")
            lines.append("|:---:|---|---|---:|---:|---:|:---:|---|")
            for e in dept.enseignants:
                if e.a_avertissement:
                    warn = " / ".join([
                        f"⚠️ `{av.type_dispo}` {av.heure_debut[:5]}–{av.heure_fin[:5]}"
                        + (f" — {av.motif}" if av.motif else "")
                        for av in e.avertissements
                    ])
                else:
                    warn = "—"

                lines.append(
                    f"| {i} | {e.prenom} {e.nom} | {e.grade or '—'} "
                    f"| {e.volume_horaire:.1f}h | {e.volume_consomme:.1f}h "
                    f"| **{e.volume_restant:.1f}h** | {e.nb_surveillances} | {warn} |"
                )
                i += 1

        return "\n".join(lines)
    except Exception as e:
        return err(e)
    finally:
        close_db(db)

# ═════════════════════════════════════════════════════════════════════════════
# S7 — TOUS LES SURVEILLANTS
# ═════════════════════════════════════════════════════════════════════════════

def get_all_surveillants(session_label: str, sort_label: str, ordre_label: str) -> str:
    db  = get_db()
    sid = _extract_id(session_label)
    if not sid:
        return "❌ Veuillez sélectionner une session."
    try:
        from app.models.salle_session import Session as SessionModel
        from app.models.enseignant import Enseignant
        from app.services.surv_service import SurvService

        sess = db.query(SessionModel).filter(SessionModel.id == sid).first()
        if not sess:
            return f"❌ Session #{sid} non trouvée."

        service     = SurvService(db)
        enseignants = db.query(Enseignant).all()
        items       = []

        for ens in enseignants:
            vol  = service.get_volume_restant_enseignant(ens.id, sess.annee_universitaire)
            dept = ens.departement
            items.append({
                "id":      ens.id,
                "nom":     f"{ens.prenom} {ens.nom}",
                "grade":   ens.grade or "—",
                "dept":    dept.code if dept else "—",
                "vol_h":   vol["volume_horaire"],
                "vol_c":   vol["volume_consomme"],
                "vol_r":   vol["volume_restant"],
                "nb_surv": vol["nb_surveillances"],
            })

        field_map = {
            "Volume restant":    "vol_r",
            "Volume consommé":   "vol_c",
            "Nb. surveillances": "nb_surv",
            "Nom":               "nom",
        }
        key     = field_map.get(sort_label, "vol_r")
        reverse = (ordre_label == "Décroissant")
        items.sort(key=lambda x: x[key], reverse=reverse)

        lines = [
            f"## 📊 Tous les enseignants — Session #{sid} ({sess.annee_universitaire})\n",
            f"**{len(items)}** enseignant(s)\n",
            "| # | Nom | Grade | Dept | Alloué | Consommé | Taux | Restant | Survs |",
            "|:---:|---|---|:---:|---:|---:|---:|---:|:---:|",
        ]
        for i, it in enumerate(items, 1):
            taux = f"{it['vol_c']/it['vol_h']*100:.0f}%" if it["vol_h"] > 0 else "—"
            lines.append(
                f"| {i} | {it['nom']} | {it['grade']} | {it['dept']} "
                f"| {it['vol_h']:.0f}h | {it['vol_c']:.2f}h | {taux} "
                f"| **{it['vol_r']:.2f}h** | {it['nb_surv']} |"
            )
        return "\n".join(lines)
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S8 — CONFLITS
# ═════════════════════════════════════════════════════════════════════════════

def get_conflits_session(
    session_label:  str,
    semestre_label: str,
    ep_label:       str,
    section_label:  str,
) -> str:
    db  = get_db()
    sid = _extract_id(session_label)
    if not sid:
        return "❌ Veuillez sélectionner une session."
    try:
        from app.models.planification import Planification, PlanifSalle
        from app.models.departement_niveau_section import Section, Niveau, Groupe
        from app.models.salle_session import Salle
        from app.models.matiere import SectionMatiere

        semestre    = int(semestre_label) if semestre_label not in ("(tous)", "", None) else None
        type_ep     = ep_label      if ep_label      not in ("(tous)", "", None) else None
        section_nom = None
        if section_label and section_label not in ("(toutes)", "", None) and "[ERREUR]" not in section_label:
            try:
                section_nom = section_label.split("]")[1].strip().split("(")[0].strip()
            except Exception:
                section_nom = None

        q = db.query(Planification).filter(
            Planification.session_id == sid,
            Planification.statut     == "VALIDEE",
        )
        if semestre: q = q.filter(Planification.semestre == semestre)
        if type_ep:  q = q.filter(Planification.type_epreuve == type_ep)
        if section_nom:
            q = (
                q.join(SectionMatiere, Planification.section_matiere_id == SectionMatiere.id)
                 .join(Section, SectionMatiere.section_id == Section.id)
                 .filter(Section.nom == section_nom)
            )
        planifications = q.all()

        conflits = []
        for planif in planifications:
            sm        = planif.section_matiere
            mat       = sm.matiere  if sm  else None
            sec       = sm.section  if sm  else None
            dept_exam = planif.departement
            cren      = planif.creneau

            planif_salles = db.query(PlanifSalle).filter(
                PlanifSalle.planification_id == planif.id
            ).all()

            for ps in planif_salles:
                nb = sum(
                    1 for s in planif.surveillances
                    if s.statut_surveillance in ("AFFECTE", "CONFIRME")
                    and s.groupe_id == ps.groupe_id
                    and s.salle_id  == ps.salle_id
                )
                if nb < planif.nb_surveillants_requis:
                    grp   = db.query(Groupe).filter(Groupe.id == ps.groupe_id).first() if ps.groupe_id else None
                    salle = db.query(Salle).filter(Salle.id == ps.salle_id).first()    if ps.salle_id  else None

                    conflits.append({
                        "planif_id": planif.id,
                        "dept":      dept_exam.code      if dept_exam else "—",
                        "matiere":   mat.code            if mat       else "—",
                        "section":   sec.nom             if sec       else "—",
                        "type":      planif.type_epreuve,
                        "sem":       planif.semestre,
                        "date":      str(cren.date)      if cren      else "—",
                        "heure":     f"{str(cren.heure_debut)[:5]}–{str(cren.heure_fin)[:5]}" if cren else "—",
                        "groupe":    f"Gr.{grp.numero}"  if grp       else "—",
                        "salle":     salle.code          if salle     else "—",
                        "requis":    planif.nb_surveillants_requis,
                        "trouves":   nb,
                        "manquants": planif.nb_surveillants_requis - nb,
                    })

        if not conflits:
            return f"## ✅ Aucun conflit dans la session #{sid}"

        lines = [
            f"## ⚠️ Conflits — Session #{sid}\n",
            f"**{len(conflits)}** conflit(s) détecté(s) "
            f"| sem={semestre or 'tous'} | type={type_ep or 'tous'} | section={section_nom or 'toutes'}\n",
            "| Planif | Dept | Matière | Section | Type | Sem. | Date | Horaire | Groupe | Salle | Requis | Trouvés | Manquants |",
            "|:---:|:---:|---|---|---|:---:|---|---|:---:|:---:|:---:|:---:|:---:|",
        ]
        for c in conflits:
            lines.append(
                f"| {c['planif_id']} | {c['dept']} | `{c['matiere']}` "
                f"| {c['section']} | {c['type']} | S{c['sem']} "
                f"| {c['date']} | {c['heure']} "
                f"| {c['groupe']} | {c['salle']} "
                f"| {c['requis']} | {c['trouves']} | ❌ **{c['manquants']}** |"
            )
        return "\n".join(lines)
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S9 — RAPPORT SESSION
# ═════════════════════════════════════════════════════════════════════════════

def get_rapport_session(session_label: str) -> tuple[str, str]:
    db  = get_db()
    sid = _extract_id(session_label)
    if not sid:
        return "❌ Veuillez sélectionner une session.", ""
    try:
        from app.models.salle_session import Session as SessionModel
        from app.models.planification import Planification
        from app.models.surveillance import Surveillance
        from app.models.enseignant import ChargeHoraire

        sess = db.query(SessionModel).filter(SessionModel.id == sid).first()
        if not sess:
            return f"❌ Session #{sid} non trouvée.", ""

        planifs = db.query(Planification).filter(
            Planification.session_id == sid,
            Planification.statut     == "VALIDEE",
        ).all()

        all_survs = (
            db.query(Surveillance)
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .filter(Planification.session_id == sid)
            .all()
        )

        nb_ok = nb_partiel = nb_zero = 0
        for p in planifs:
            nb = sum(1 for s in p.surveillances if s.statut_surveillance in ("AFFECTE", "CONFIRME"))
            if nb >= p.nb_surveillants_requis:
                nb_ok += 1
            elif nb == 0:
                nb_zero += 1
            else:
                nb_partiel += 1

        resume = (
            f"## 📑 Rapport — Session #{sid} | {sess.annee_universitaire}\n\n"
            f"| Indicateur | Valeur |\n|---|---|\n"
            f"| Type | {sess.type_session} |\n"
            f"| Période | {sess.date_debut} → {sess.date_fin} |\n"
            f"| Statut | {sess.statut} |\n"
            f"| Planifications VALIDÉES | **{len(planifs)}** |\n"
            f"| ✅ Entièrement affectées | **{nb_ok}** |\n"
            f"| ⚠️ Partiellement affectées | **{nb_partiel}** |\n"
            f"| ❌ Non affectées | **{nb_zero}** |\n"
            f"| Total surveillances | **{len(all_survs)}** |\n"
            f"| Présences confirmées | **{sum(1 for s in all_survs if s.presence)}** |\n"
            f"| Enseignants externes | **{sum(1 for s in all_survs if s.est_externe)}** |\n"
        )

        ens_map: dict = {}
        for s in all_survs:
            eid = s.enseignant_id
            if eid not in ens_map:
                ch  = db.query(ChargeHoraire).filter(
                    ChargeHoraire.enseignant_id == eid,
                    ChargeHoraire.annee_univ    == sess.annee_universitaire,
                ).first()
                ens = s.enseignant
                ens_map[eid] = {
                    "nom":    f"{ens.prenom} {ens.nom}" if ens else "—",
                    "grade":  ens.grade                 if ens else "—",
                    "dept":   ens.departement.code      if ens and ens.departement else "—",
                    "charge": 0.0, "nb": 0, "pres": 0,
                    "vol_h":  float(ch.volume_horaire)  if ch else 0.0,
                }
            ens_map[eid]["charge"] += float(s.charge)
            ens_map[eid]["nb"]     += 1
            if s.presence:
                ens_map[eid]["pres"] += 1

        class_lines = [
            "\n## 🏆 Classement enseignants (charge cumulée)\n",
            "| # | Nom | Grade | Dept | Alloué | Charge session | Taux | Survs | Présences |",
            "|:---:|---|---|:---:|---:|---:|---:|:---:|:---:|",
        ]
        for i, c in enumerate(
            sorted(ens_map.values(), key=lambda x: x["charge"], reverse=True), 1
        ):
            taux = f"{c['charge']/c['vol_h']*100:.1f}%" if c["vol_h"] > 0 else "—"
            class_lines.append(
                f"| {i} | {c['nom']} | {c['grade']} | {c['dept']} "
                f"| {c['vol_h']:.0f}h | **{c['charge']:.2f}h** "
                f"| {taux} | {c['nb']} | {c['pres']} |"
            )

        return resume, "\n".join(class_lines)
    except Exception as e:
        return err(e), ""
    finally:
        close_db(db)

# ═════════════════════════════════════════════════════════════════════════════
# S11 — MODIFIER UNE SURVEILLANCE
# ═════════════════════════════════════════════════════════════════════════════

def modifier_surveillance(surv_label: str, presence: str, statut: str, charge: float) -> str:
    db  = get_db()
    sid = _extract_id(surv_label)
    if not sid:
        return "❌ Veuillez sélectionner une surveillance."
    try:
        from app.crud.crud_surv import get_surveillance, update_surveillance, _enrich_surveillance
        from app.schemas.surveillance_schema import SurveillanceUpdate, StatutSurveillance

        s = get_surveillance(db, sid)
        if not s:
            return f"❌ Surveillance #{sid} non trouvée."

        payload = SurveillanceUpdate(
            presence=(True if presence == "Présent" else False if presence == "Absent" else None),
            statut_surveillance=(
                StatutSurveillance.CONFIRME if statut == "CONFIRME"
                else StatutSurveillance.AFFECTE if statut == "AFFECTE"
                else None
            ),
            charge=(charge if charge > 0 else None),
        )
        updated = update_surveillance(db, s, payload)
        d  = _enrich_surveillance(db, updated)
        sv = d["surveillance"]
        ens = d["enseignant"]
        mat = d["matiere"]
        cr  = d["creneau"]

        return (
            f"## ✅ Surveillance #{sid} modifiée\n\n"
            f"- Enseignant : **{ens['nom_complet']}**\n"
            f"- Matière : **{mat['intitule'] or '—'}**\n"
            f"- Créneau : {cr['date'] or '—'} "
            f"{str(cr['heure_debut'] or '')[:5]}–{str(cr['heure_fin'] or '')[:5]}\n"
            f"- Statut : **{sv['statut_surveillance']}**\n"
            f"- Présence : **{'✅ Oui' if sv['presence'] else '❌ Non'}**\n"
            f"- Charge : **{sv['charge']:.2f}h**\n"
            f"- Mis à jour : _{sv['updated_at']}_\n"
        )
    except Exception as e:
        return err(e)
    finally:
        close_db(db)

# ═════════════════════════════════════════════════════════════════════════════
# S14 — REMPLACEMENT
# ═════════════════════════════════════════════════════════════════════════════

def remplacer_enseignant(surv_label: str, nouvel_ens_label: str, motif_label: str) -> str:
    db   = get_db()
    sid  = _extract_id(surv_label)
    neid = _extract_id(nouvel_ens_label)
    if not sid:
        return "❌ Veuillez sélectionner une surveillance."
    if not neid:
        return "❌ Veuillez sélectionner le nouvel enseignant."
    if not motif_label or motif_label in ("(aucun)", ""):
        return "❌ Veuillez sélectionner un motif."
    try:
        from app.services.surv_service import SurvService
        from app.crud.crud_surv import _enrich_surveillance, get_surveillance

        old, new = SurvService(db).replace_surveillance(sid, neid, motif_label)
        new_full = get_surveillance(db, new.id)
        d        = _enrich_surveillance(db, new_full) if new_full else {}
        ens      = d.get("enseignant", {})
        mat      = d.get("matiere", {})
        cr       = d.get("creneau", {})

        return (
            f"## ✅ Remplacement effectué\n\n"
            f"- Ancienne surveillance : **#{old.id}** (enseignant ID {old.enseignant_id})\n"
            f"- Nouvelle surveillance : **#{new.id}**\n"
            f"- Nouvel enseignant : **{ens.get('nom_complet', '—')}** ({ens.get('grade', '—')})\n"
            f"- Matière : **{mat.get('intitule', '—')}**\n"
            f"- Créneau : {cr.get('date', '—')} "
            f"{str(cr.get('heure_debut', '') or '')[:5]}–{str(cr.get('heure_fin', '') or '')[:5]}\n"
            f"- Motif : _{motif_label}_\n"
        )
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S15 — AFFECTATION MANUELLE
# ═════════════════════════════════════════════════════════════════════════════

def affectation_manuelle(session_label: str, planif_label: str, ens_labels: list, groupe_label: str) -> str:
    db  = get_db()
    sid = _extract_id(session_label)
    pid = _extract_id(planif_label)
    if not sid or not pid:
        return "❌ Veuillez sélectionner une session et une planification."
    if not ens_labels:
        return "❌ Veuillez sélectionner au moins un enseignant."
    try:
        from app.services.surv_service import SurvService
        from app.schemas.surveillance_schema import ManualAssignmentRequest

        ens_ids = [_extract_id(lab) for lab in ens_labels if _extract_id(lab)]
        grp_id  = _extract_id(groupe_label) if groupe_label and "(aucune" not in groupe_label else None

        req    = ManualAssignmentRequest(
            session_id=sid,
            planification_id=pid,
            enseignant_ids=ens_ids,
            groupe_id=grp_id,
        )
        result = SurvService(db).affecter_planification_manuellement(req)

        return (
            f"## ✅ Affectation manuelle — Planification #{pid}\n\n"
            f"- Session : **#{sid}**\n"
            f"- Enseignants sélectionnés : **{len(ens_ids)}**\n"
            f"- Enseignants affectés : **{result.get('surveillants_inseres', 0)}**\n"
            f"- Groupe : **{grp_id or '—'}**\n"
            f"- Statut : **{result.get('statut', '—')}**\n"
        )
    except ValueError as e:
        return f"❌ Conflit : {e}"
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S16 — SUPPRIMER UNE SURVEILLANCE
# ═════════════════════════════════════════════════════════════════════════════

def supprimer_surveillance(surv_label: str, confirmer: bool) -> str:
    if not confirmer:
        return "⚠️ Cochez la case de confirmation avant de supprimer."
    db  = get_db()
    sid = _extract_id(surv_label)
    if not sid:
        return "❌ Veuillez sélectionner une surveillance."
    try:
        from app.crud.crud_surv import delete_surveillance_by_id
        ok = delete_surveillance_by_id(db, sid)
        return (
            f"✅ Surveillance **#{sid}** supprimée avec succès."
            if ok else f"❌ Surveillance #{sid} non trouvée."
        )
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S17 — RESET SESSION
# ═════════════════════════════════════════════════════════════════════════════

def reset_session(session_label: str, confirmer: bool) -> str:
    if not confirmer:
        return "⚠️ Cochez la case de confirmation avant de réinitialiser."
    db  = get_db()
    sid = _extract_id(session_label)
    if not sid:
        return "❌ Veuillez sélectionner une session."
    try:
        from app.crud.crud_surv import delete_surveillances_for_session
        count = delete_surveillances_for_session(db, sid)
        return f"✅ **{count}** surveillance(s) supprimée(s) pour la session **#{sid}**."
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S18 — VOLUME HORAIRE
# ═════════════════════════════════════════════════════════════════════════════

def get_volume_enseignant(ens_label: str, annee_label: str) -> str:
    db  = get_db()
    eid = _extract_id(ens_label)
    if not eid:
        return "❌ Veuillez sélectionner un enseignant."
    try:
        from app.services.surv_service import SurvService
        annee = annee_label.strip()
        vol   = SurvService(db).get_volume_restant_enseignant(eid, annee)
        taux  = (vol["volume_consomme"] / vol["volume_horaire"] * 100
                 if vol["volume_horaire"] > 0 else 0)
        barre = "█" * int(taux / 5) + "░" * (20 - int(taux / 5))

        return (
            f"## 📈 Volume horaire — Enseignant #{eid} ({annee})\n\n"
            f"```\n{barre} {taux:.1f}%\n```\n\n"
            f"| Indicateur | Valeur |\n|---|---|\n"
            f"| Volume alloué | **{vol['volume_horaire']:.2f}h** |\n"
            f"| Volume consommé | **{vol['volume_consomme']:.2f}h** |\n"
            f"| Volume restant | **{vol['volume_restant']:.2f}h** |\n"
            f"| Surveillances | **{vol['nb_surveillances']}** |\n"
            f"| Taux d'utilisation | **{taux:.1f}%** |\n"
        )
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S19 — INDISPONIBILITÉS
# ═════════════════════════════════════════════════════════════════════════════

def get_disponibilites_enseignant(
    ens_label:    str,
    session_label: str,
    date_debut_manual: str = "",
    date_fin_manual:   str = "",
) -> str:
    db  = get_db()
    eid = _extract_id(ens_label)
    if not eid:
        return "❌ Veuillez sélectionner un enseignant."
    try:
        from app.models.disponibilite import DisponibiliteEnseignant
        from app.models.salle_session import Session as SessionModel
        from datetime import datetime as dt

        date_debut = date_fin = None

        # ── Priorité : dates manuelles ──
        if date_debut_manual and date_fin_manual:
            try:
                date_debut = dt.strptime(date_debut_manual.strip(), "%Y-%m-%d").date()
                date_fin   = dt.strptime(date_fin_manual.strip(),   "%Y-%m-%d").date()
            except ValueError:
                return "❌ Format de date invalide. Utilisez YYYY-MM-DD."
        else:
            # ── Fallback : dates depuis la session ──
            sid = _extract_id(session_label)
            if sid:
                sess = db.query(SessionModel).filter(SessionModel.id == sid).first()
                if sess:
                    date_debut = sess.date_debut
                    date_fin   = sess.date_fin

        q = db.query(DisponibiliteEnseignant).filter(
            DisponibiliteEnseignant.enseignant_id == eid
        )
        if date_debut:
            q = q.filter(DisponibiliteEnseignant.date >= date_debut)
        if date_fin:
            q = q.filter(DisponibiliteEnseignant.date <= date_fin)
        dispos = q.order_by(DisponibiliteEnseignant.date).all()

        periode_info = f"du {date_debut} au {date_fin}" if date_debut else "toute période"

        if not dispos:
            return f"_Aucune indisponibilité déclarée pour l'enseignant #{eid} ({periode_info})._"

        lines = [
            f"## 📅 Indisponibilités — Enseignant #{eid}\n",
            f"Période : **{periode_info}**\n",
            "| Date | Début | Fin | Type | Motif |",
            "|---|---|---|---|---|",
        ]
        for d in dispos:
            lines.append(
                f"| {d.date} | {str(d.heure_debut)[:5]} | {str(d.heure_fin)[:5]} "
                f"| `{d.type_dispo}` | {d.motif or '—'} |"
            )
        return "\n".join(lines)
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# S20 — STATISTIQUES GLOBALES
# ═════════════════════════════════════════════════════════════════════════════

def get_statistiques_globales(annee_label: str) -> str:
    db = get_db()
    try:
        from app.models.surveillance import Surveillance
        from app.models.planification import Planification
        from app.models.salle_session import Session as SessionModel
        from sqlalchemy import func

        annee = annee_label.strip()

        stats = (
            db.query(
                func.count(Surveillance.id).label("total"),
                func.coalesce(func.sum(Surveillance.charge), 0).label("heures"),
                func.count(func.distinct(Surveillance.enseignant_id)).label("ens"),
            )
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(SessionModel,  Planification.session_id      == SessionModel.id)
            .filter(SessionModel.annee_universitaire == annee)
            .first()
        )

        ext = (
            db.query(func.count(Surveillance.id))
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(SessionModel,  Planification.session_id      == SessionModel.id)
            .filter(SessionModel.annee_universitaire == annee, Surveillance.est_externe == True)
            .scalar() or 0
        )
        conf = (
            db.query(func.count(Surveillance.id))
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(SessionModel,  Planification.session_id      == SessionModel.id)
            .filter(SessionModel.annee_universitaire == annee, Surveillance.statut_surveillance == "CONFIRME")
            .scalar() or 0
        )

        total     = stats.total or 0
        taux_ext  = f"{ext/total*100:.1f}%" if total > 0 else "—"
        taux_conf = f"{conf/total*100:.1f}%" if total > 0 else "—"

        return (
            f"## 📊 Statistiques globales — {annee}\n\n"
            f"| Indicateur | Valeur |\n|---|---|\n"
            f"| Total surveillances | **{total}** |\n"
            f"| Total heures | **{float(stats.heures or 0):.2f}h** |\n"
            f"| Enseignants impliqués | **{stats.ens or 0}** |\n"
            f"| Enseignants externes | **{ext}** ({taux_ext}) |\n"
            f"| Confirmées | **{conf}** ({taux_conf}) |\n"
        )
    except Exception as e:
        return err(e)
    finally:
        close_db(db)


# ═════════════════════════════════════════════════════════════════════════════
# INTERFACE GRADIO
# ═════════════════════════════════════════════════════════════════════════════

THEME = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("IBM Plex Sans"), "sans-serif"],
    font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "monospace"],
)

CSS = """
.tab-nav button { font-weight: 600; font-size: 0.84rem; }
.section-header {
    background: linear-gradient(135deg, #312e81 0%, #4f46e5 60%, #7c3aed 100%);
    color: white; border-radius: 12px; padding: 18px 26px; margin-bottom: 14px;
}
.ep-badge {
    display:inline-block; background:#1e1b4b; color:#a5b4fc;
    font-family:monospace; padding:3px 10px; border-radius:5px;
    font-size:0.78rem; margin-bottom:8px;
}
footer { display: none !important; }
.refresh-btn { max-width: 48px !important; min-width: 48px !important; }
"""

_MOTIFS_REMPLACEMENT = [
    "(aucun)",
    "Indisponibilité médicale",
    "Mission officielle",
    "Congé exceptionnel",
    "Conflit d'horaire imprévu",
    "Demande personnelle",
    "Erreur d'affectation",
    "Autre raison",
]


def badge(text: str) -> str:
    return f'<span class="ep-badge">{text}</span>'


def build_interface():
    with gr.Blocks(title="Surveillance — Dashboard de Test v3", theme=THEME, css=CSS) as app:

        gr.HTML("""
        <div class="section-header">
          <h1 style="margin:0;font-size:1.45rem;">
            🎓 Module Surveillance — Dashboard de Test
          </h1>
          <p style="margin:6px 0 0;opacity:0.88;font-size:0.86rem;">
            Teste tous les endpoints <code>/surveillances</code> ·
            Toutes les valeurs sont sélectionnées depuis la base ·
            Aucune saisie clavier requise
          </p>
        </div>
        """)

        # ── TAB 1 — AFFECTATION AUTOMATIQUE ──────────────────────────────────
        with gr.Tab("🤖 Affectation Auto"):
            gr.HTML(badge("POST /surveillances/affecter-session"))
            gr.Markdown(
                "Lance l'algorithme v3 (6 contraintes). "
                "**Session**, **Section**, **Période** et **Type d'épreuve** sont tous **obligatoires** ⚠️"
            )
            with gr.Row():
                sess_auto = gr.Dropdown(label="Session *", choices=_SESSIONS, value=_S0)
                btn_ref_s1 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")

            with gr.Row():
                sec_auto = gr.Dropdown(
                    label="Section *",
                    choices=_SECTIONS,
                    value=_SEC0,
                )
                btn_ref_sec = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                per_auto = gr.Dropdown(
                    label="Période *",
                    choices=_PERIODES,
                    value=_PER0,
                )
                btn_ref_per = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                ep_auto = gr.Dropdown(
                    label="Type d'épreuve *",
                    choices=_TYPES_EPREUVE,
                    value=_TE0,
                )

            btn_auto = gr.Button("▶ Lancer l'affectation automatique", variant="primary")
            with gr.Row():
                out_auto_res = gr.Markdown(label="Résumé")
                out_auto_det = gr.Markdown(label="Détail par groupe")

            btn_auto.click(
                lancer_affectation_auto,
                [sess_auto, sec_auto, per_auto, ep_auto],
                [out_auto_res, out_auto_det],
            )
            btn_ref_s1.click(refresh_sessions, [], [sess_auto])
            btn_ref_sec.click(refresh_sections, [], [sec_auto])
            btn_ref_per.click(refresh_periodes, [], [per_auto])

        # ── TAB 2 — PROFIL ENSEIGNANT ─────────────────────────────────────────
        with gr.Tab("👤 Profil Enseignant"):
            gr.HTML(badge("GET /surveillances/enseignant/{id}/toutes-surveillances"))
            with gr.Row():
                ens_profil = gr.Dropdown(label="Enseignant *", choices=_ENSEIGNANTS, value=_E0)
                btn_ref_e2 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                ann_profil = gr.Dropdown(label="Année universitaire *", choices=_ANNEES_UNIV, value=_AN0)
                btn_ref_a2 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            with gr.Row():
                sem_profil = gr.Dropdown(
                    label="Semestre (optionnel)",
                    choices=["(tous)", "1", "2"],
                    value="(tous)",
                )
                ep_profil = gr.Dropdown(
                    label="Type d'épreuve (optionnel)",
                    choices=["(tous)"] + _TYPES_EPREUVE,
                    value="(tous)",
                )
            btn_profil = gr.Button("Afficher le profil complet", variant="primary")
            with gr.Row():
                out_profil_fiche  = gr.Markdown(label="Fiche & Charge")
                out_profil_detail = gr.Markdown(label="Détail surveillances")
            btn_profil.click(get_profil_enseignant, [ens_profil, ann_profil, sem_profil, ep_profil], [out_profil_fiche, out_profil_detail])
            btn_ref_e2.click(refresh_enseignants, [], [ens_profil])
            btn_ref_a2.click(refresh_annees, [], [ann_profil])


        # ── TAB 3 — SURVEILLANCES SESSION ────────────────────────────────────
        with gr.Tab("📋 Surveillances Session"):
            gr.HTML(badge("GET /surveillances/{session_id}"))
            with gr.Row():
                sess_list  = gr.Dropdown(label="Session *", choices=_SESSIONS, value=_S0)
                btn_ref_s3 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                ep_list    = gr.Dropdown(label="Type d'épreuve", choices=["(tous)"] + _TYPES_EPREUVE, value="(tous)")
                sem_list   = gr.Dropdown(label="Semestre", choices=["(tous)", "1", "2"], value="(tous)")
                stat_list  = gr.Dropdown(label="Statut", choices=["(tous)", "AFFECTE", "CONFIRME"], value="(tous)")
            with gr.Row():
                dept_list  = gr.Dropdown(label="Département", choices=["(tous)"] + _DEPARTEMENTS, value="(tous)")
                grp_list   = gr.Dropdown(label="Groupe", choices=["(tous)"] + _GROUPES_ALL, value="(tous)")
                salle_list = gr.Dropdown(label="Salle", choices=["(tous)"] + _SALLES, value="(tous)")
            with gr.Row():
                sec_list3  = gr.Dropdown(label="Section", choices=["(tous)"] + _SECTIONS, value="(tous)")
                btn_ref_sec3 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                ens_list3  = gr.Dropdown(label="Enseignant", choices=["(tous)"] + _ENSEIGNANTS, value="(tous)")
                btn_ref_ens3 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            btn_list = gr.Button("Rechercher", variant="primary")
            out_list = gr.Markdown()
            btn_list.click(
                get_session_surveillances,
                [sess_list, ep_list, stat_list, sem_list, grp_list, salle_list, dept_list, sec_list3, ens_list3],
                out_list,
            )
            btn_ref_sec3.click(refresh_sections, [], [sec_list3])
            btn_ref_ens3.click(refresh_enseignants, [], [ens_list3])
            btn_ref_s3.click(refresh_sessions, [], [sess_list])

        # ── TAB 4 — DÉTAIL SURVEILLANCE ──────────────────────────────────────
        with gr.Tab("🔍 Détail Surveillance"):
            gr.HTML(badge("GET /surveillances/{surveillance_id}/full-details"))
            with gr.Row():
                sess_det4  = gr.Dropdown(label="Session (pour filtrer)", choices=_SESSIONS, value=_S0)
                btn_ref_s4 = gr.Button("🔄 Charger", scale=1)
            surv_det4 = gr.Dropdown(label="Surveillance *", choices=_SURVEILLANCES, value=_SU0)
            btn_det4  = gr.Button("Afficher les détails complets", variant="primary")
            out_det4  = gr.Markdown()
            btn_det4.click(get_detail_surveillance, [surv_det4], out_det4)
            btn_ref_s4.click(refresh_surveillances_for_session, [sess_det4], [surv_det4])

        # ── TAB 5 — ENSEIGNANTS DISPONIBLES ──────────────────────────────────
        with gr.Tab("👥 Disponibles / Planif"):
            gr.HTML(badge("GET /surveillances/enseignants-disponibles/{planif_id}"))
            with gr.Row():
                sess_dispo = gr.Dropdown(label="Session (pour filtrer)", choices=_SESSIONS, value=_S0)
                btn_ref_s5 = gr.Button("🔄 Charger planifications", scale=1)
            planif_dispo = gr.Dropdown(label="Planification *", choices=_PLANIFICATIONS, value=_P0)
            btn_dispo    = gr.Button("Afficher les enseignants disponibles", variant="primary")
            out_dispo    = gr.Markdown()
            btn_dispo.click(get_disponibles_planif, [planif_dispo], out_dispo)
            btn_ref_s5.click(refresh_planifications_for_session, [sess_dispo], [planif_dispo])

        # ── TAB 6 — TOUS LES SURVEILLANTS ────────────────────────────────────
        with gr.Tab("📊 Tous Surveillants"):
            gr.HTML(badge("GET /surveillances/getallsurveillants"))
            with gr.Row():
                sess_all   = gr.Dropdown(label="Session *", choices=_SESSIONS, value=_S0)
                btn_ref_s6 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                sort_all   = gr.Dropdown(label="Trier par", choices=["Volume restant", "Volume consommé", "Nb. surveillances", "Nom"], value="Volume restant")
                ordre_all  = gr.Dropdown(label="Ordre", choices=["Décroissant", "Croissant"], value="Décroissant")
            btn_all = gr.Button("Charger", variant="primary")
            out_all = gr.Markdown()
            btn_all.click(get_all_surveillants, [sess_all, sort_all, ordre_all], out_all)
            btn_ref_s6.click(refresh_sessions, [], [sess_all])

        # ── TAB 7 — CONFLITS ─────────────────────────────────────────────────
        with gr.Tab("⚠️ Conflits"):
            gr.HTML(badge("GET /surveillances/session/{session_id}/conflits"))
            with gr.Row():
                sess_conf  = gr.Dropdown(label="Session *", choices=_SESSIONS, value=_S0)
                btn_ref_s7 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                sem_conf   = gr.Dropdown(label="Semestre", choices=["(tous)", "1", "2"], value="(tous)")
                ep_conf    = gr.Dropdown(label="Type d'épreuve", choices=["(tous)"] + _TYPES_EPREUVE, value="(tous)")
            with gr.Row():
                sec_conf   = gr.Dropdown(label="Section", choices=["(toutes)"] + _SECTIONS, value="(toutes)")
                btn_ref_sec_conf = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            btn_conf = gr.Button("Détecter les conflits", variant="primary")
            out_conf = gr.Markdown()
            btn_conf.click(
                get_conflits_session,
                [sess_conf, sem_conf, ep_conf, sec_conf],
                out_conf,
            )
            btn_ref_s7.click(refresh_sessions, [], [sess_conf])
            btn_ref_sec_conf.click(refresh_sections, [], [sec_conf])

        # ── TAB 8 — RAPPORT SESSION ───────────────────────────────────────────
        with gr.Tab("📑 Rapport Session"):
            gr.HTML(badge("GET /surveillances/session/{session_id}/rapport"))
            with gr.Row():
                sess_rapp  = gr.Dropdown(label="Session *", choices=_SESSIONS, value=_S0)
                btn_ref_s8 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            btn_rapp = gr.Button("Générer le rapport complet", variant="primary")
            with gr.Row():
                out_rapp_vue   = gr.Markdown(label="Vue d'ensemble")
                out_rapp_class = gr.Markdown(label="Classement enseignants")
            btn_rapp.click(get_rapport_session, [sess_rapp], [out_rapp_vue, out_rapp_class])
            btn_ref_s8.click(refresh_sessions, [], [sess_rapp])

        # ── TAB 9 — PRÉSENCES ────────────────────────────────────────────────

        # ── TAB 10 — MODIFIER / CONFIRMER / PRÉSENCE ─────────────────────────
        with gr.Tab("✏️ Modifier / Confirmer"):
            with gr.Row():
                sess_mod10  = gr.Dropdown(label="Session (filtrer)", choices=_SESSIONS, value=_S0)
                btn_ref_s10 = gr.Button("🔄 Charger", scale=1)
            surv_mod10 = gr.Dropdown(label="Surveillance *", choices=_SURVEILLANCES, value=_SU0)
            btn_ref_s10.click(refresh_surveillances_for_session, [sess_mod10], [surv_mod10])

            gr.Markdown("---")
            gr.HTML(badge("PATCH /surveillances/edit/{surveillance_id}"))
            with gr.Row():
                pres_mod10  = gr.Dropdown(label="Présence", choices=["(inchangé)", "Présent", "Absent"], value="(inchangé)")
                stat_mod10  = gr.Dropdown(label="Statut", choices=["(inchangé)", "AFFECTE", "CONFIRME"], value="(inchangé)")
                charg_mod10 = gr.Slider(label="Charge (h) — 0 = inchangé", minimum=0, maximum=4, step=0.5, value=0)
            btn_mod10 = gr.Button("Appliquer les modifications", variant="primary")
            out_mod10 = gr.Markdown()
            btn_mod10.click(modifier_surveillance, [surv_mod10, pres_mod10, stat_mod10, charg_mod10], out_mod10)

        # ── TAB 11 — REMPLACEMENT ────────────────────────────────────────────
        with gr.Tab("🔄 Remplacement"):
            gr.HTML(badge("POST /surveillances/{surveillance_id}/reassign"))
            with gr.Row():
                sess_remp11 = gr.Dropdown(label="Session (filtrer)", choices=_SESSIONS, value=_S0)
                btn_ref_s11 = gr.Button("🔄 Charger", scale=1)
            surv_remp11 = gr.Dropdown(label="Surveillance à remplacer *", choices=_SURVEILLANCES, value=_SU0)
            btn_ref_s11.click(refresh_surveillances_for_session, [sess_remp11], [surv_remp11])
            with gr.Row():
                nens_remp11 = gr.Dropdown(label="Nouvel enseignant *", choices=_ENSEIGNANTS, value=_E0)
                btn_ref_e11 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            motif_remp11 = gr.Dropdown(label="Motif du remplacement *", choices=_MOTIFS_REMPLACEMENT, value=_MOTIFS_REMPLACEMENT[1])
            btn_remp11   = gr.Button("Effectuer le remplacement", variant="secondary")
            out_remp11   = gr.Markdown()
            btn_remp11.click(remplacer_enseignant, [surv_remp11, nens_remp11, motif_remp11], out_remp11)
            btn_ref_e11.click(refresh_enseignants, [], [nens_remp11])

        # ── TAB 12 — AFFECTATION MANUELLE ────────────────────────────────────
        with gr.Tab("🔁 Affectation Manuelle"):
            gr.HTML(badge("POST /surveillances/manual-assignment"))
            with gr.Row():
                sess_man12  = gr.Dropdown(label="Session *", choices=_SESSIONS, value=_S0)
                btn_ref_s12 = gr.Button("🔄 Charger planifications", scale=1)
            planif_man12 = gr.Dropdown(label="Planification *", choices=_PLANIFICATIONS, value=_P0)
            with gr.Row():
                ens_man12   = gr.Dropdown(label="Enseignants (sélection multiple *)", choices=_ENSEIGNANTS, multiselect=True, value=[])
                btn_ref_e12 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            with gr.Row():
                grp_man12   = gr.Dropdown(label="Groupe (optionnel)", choices=["(aucun)"] + _GROUPES, value="(aucun)")
                btn_ref_g12 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            btn_man12 = gr.Button("Affecter manuellement", variant="primary")
            out_man12 = gr.Markdown()
            btn_man12.click(affectation_manuelle, [sess_man12, planif_man12, ens_man12, grp_man12], out_man12)
            btn_ref_s12.click(refresh_planifications_for_session, [sess_man12], [planif_man12])
            btn_ref_e12.click(refresh_enseignants, [], [ens_man12])
            btn_ref_g12.click(refresh_groupes_for_planif, [planif_man12], [grp_man12])

        # ── TAB 13 — VOLUME HORAIRE ───────────────────────────────────────────
        with gr.Tab("📈 Volume Enseignant"):
            gr.HTML(badge("Analytics — SurvService.get_volume_restant_enseignant"))
            with gr.Row():
                ens_vol13   = gr.Dropdown(label="Enseignant *", choices=_ENSEIGNANTS, value=_E0)
                btn_ref_e13 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                ann_vol13   = gr.Dropdown(label="Année universitaire *", choices=_ANNEES_UNIV, value=_AN0)
                btn_ref_a13 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            btn_vol13 = gr.Button("Calculer le volume", variant="primary")
            out_vol13 = gr.Markdown()
            btn_vol13.click(get_volume_enseignant, [ens_vol13, ann_vol13], out_vol13)
            btn_ref_e13.click(refresh_enseignants, [], [ens_vol13])
            btn_ref_a13.click(refresh_annees, [], [ann_vol13])

        # ── TAB 14 — INDISPONIBILITÉS ─────────────────────────────────────────
        # ── TAB 14 — INDISPONIBILITÉS ─────────────────────────────────────────
        with gr.Tab("📅 Indisponibilités"):
            gr.HTML(badge("GET /surveillances/enseignant/{id}/disponibilites"))
            gr.Markdown("La période est déduite automatiquement des dates de la session sélectionnée, ou entrez manuellement les dates.")
            with gr.Row():
                ens_dis14   = gr.Dropdown(label="Enseignant *", choices=_ENSEIGNANTS, value=_E0)
                btn_ref_e14 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
                sess_dis14  = gr.Dropdown(label="Session (pour déduire la période)", choices=["(toutes)"] + _SESSIONS, value="(toutes)")
                btn_ref_s14 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            with gr.Row():
                date_debut_dis14 = gr.Textbox(label="Date début (YYYY-MM-DD) — optionnel, prioritaire sur session", placeholder="2026-01-07")
                date_fin_dis14   = gr.Textbox(label="Date fin (YYYY-MM-DD) — optionnel, prioritaire sur session",   placeholder="2026-01-15")
            btn_dis14 = gr.Button("Consulter les indisponibilités", variant="primary")
            out_dis14 = gr.Markdown()
            btn_dis14.click(get_disponibilites_enseignant, [ens_dis14, sess_dis14, date_debut_dis14, date_fin_dis14], out_dis14)
            btn_ref_e14.click(refresh_enseignants, [], [ens_dis14])
            btn_ref_s14.click(refresh_sessions, [], [sess_dis14])

        # ── TAB 15 — STATISTIQUES ─────────────────────────────────────────────
        with gr.Tab("📊 Statistiques"):
            gr.HTML(badge("GET /surveillances/statistiques"))
            with gr.Row():
                ann_stat15  = gr.Dropdown(label="Année universitaire *", choices=_ANNEES_UNIV, value=_AN0)
                btn_ref_a15 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            btn_stat15 = gr.Button("Calculer les statistiques", variant="primary")
            out_stat15 = gr.Markdown()
            btn_stat15.click(get_statistiques_globales, [ann_stat15], out_stat15)
            btn_ref_a15.click(refresh_annees, [], [ann_stat15])

        # ── TAB 16 — SUPPRESSION ──────────────────────────────────────────────
        with gr.Tab("🗑️ Suppression"):
            gr.HTML(badge("DELETE /surveillances/{surveillance_id}"))
            with gr.Row():
                sess_del16  = gr.Dropdown(label="Session (filtrer)", choices=_SESSIONS, value=_S0)
                btn_ref_s16 = gr.Button("🔄 Charger", scale=1)
            surv_del16 = gr.Dropdown(label="Surveillance à supprimer *", choices=_SURVEILLANCES, value=_SU0)
            cfm_del16  = gr.Checkbox(label="⚠️ Je confirme la suppression (irréversible)", value=False)
            btn_del16  = gr.Button("Supprimer", variant="stop")
            out_del16  = gr.Markdown()
            btn_del16.click(supprimer_surveillance, [surv_del16, cfm_del16], out_del16)
            btn_ref_s16.click(refresh_surveillances_for_session, [sess_del16], [surv_del16])

        # ── TAB 17 — RESET SESSION ────────────────────────────────────────────
        with gr.Tab("🔥 Reset Session"):
            gr.HTML(badge("DELETE /surveillances/session/{session_id}/reset"))
            gr.Markdown("> ⛔ **Action destructrice et irréversible.** Supprime TOUTES les surveillances d'une session entière.")
            with gr.Row():
                sess_rst17  = gr.Dropdown(label="Session à réinitialiser *", choices=_SESSIONS, value=_S0)
                btn_ref_s17 = gr.Button("🔄", scale=0, elem_classes="refresh-btn")
            cfm_rst17 = gr.Checkbox(label="✅ Je confirme la suppression de TOUTES les surveillances de cette session", value=False)
            btn_rst17 = gr.Button("⚠️ RÉINITIALISER LA SESSION", variant="stop")
            out_rst17 = gr.Markdown()
            btn_rst17.click(reset_session, [sess_rst17, cfm_rst17], out_rst17)
            btn_ref_s17.click(refresh_sessions, [], [sess_rst17])

        gr.HTML("""
        <div style="text-align:center;padding:16px;color:#64748b;
                    font-size:0.78rem;margin-top:24px;border-top:1px solid #e2e8f0;">
            Module Surveillance · Système de Gestion des Examens · 2025/2026
        </div>
        """)

    return app


if __name__ == "__main__":
    interface = build_interface()
    interface.launch(
        server_name="localhost",
        server_port=7862,
        share=False,
        debug=True,
        show_error=True,
    )