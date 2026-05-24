"""
crud/crud_surv.py
"""
from datetime import datetime
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models.surveillance import Surveillance
from app.models.enseignant import Enseignant, ChargeHoraire
from app.models.planification import Planification, PlanifSalle
from app.models.salle_session import Session as SessionModel, Creneau, Salle
from app.models.matiere import SectionMatiere, Matiere
from app.models.departement_niveau_section import Section, Niveau, Departement, Groupe
from app.schemas.surveillance_schema import SurveillanceCreate, SurveillanceUpdate


# ─────────────────────────────────────────────────────────────────────────────
# Helper — query de base avec eager loading
# ─────────────────────────────────────────────────────────────────────────────

def _base(db: Session):
    return (
        db.query(Surveillance)
        .options(
            selectinload(Surveillance.enseignant),
            selectinload(Surveillance.planification),
            selectinload(Surveillance.groupe),
            selectinload(Surveillance.salle),
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# Enrichissement complet d'une surveillance
# ─────────────────────────────────────────────────────────────────────────────

def _enrich_surveillance(db: Session, s: Surveillance, annee_univ: str | None = None) -> dict:
    # — Planification & dépendances —
    planif    = s.planification
    creneau   = planif.creneau        if planif else None
    sm        = planif.section_matiere if planif else None
    mat       = sm.matiere            if sm     else None
    sec       = sm.section            if sm     else None
    niv       = sec.niveau            if sec    else None
    # Planification doesn't have a direct departement relationship
    dept_exam = None

    # — Session (pour annee_univ si non fourni) —
    sess_obj = planif.session if planif else None

    # — Groupe & Salle —
    grp   = s.groupe
    salle = s.salle

    # — Enseignant & son département —
    ens      = s.enseignant
    dept_ens = ens.departement if ens else None

    # — Charge horaire —
    annee_key = annee_univ or (sess_obj.annee_universitaire if sess_obj else None)
    ch = None
    if ens and annee_key:
        ch = db.query(ChargeHoraire).filter(
            ChargeHoraire.enseignant_id == ens.id,
            ChargeHoraire.annee_univ    == annee_key,
        ).first()

    # — Volume consommé —
    charge_consommee = 0.0
    if ens and annee_key:
        charge_consommee = (
            db.query(func.coalesce(func.sum(Surveillance.charge), 0))
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(SessionModel,  Planification.session_id      == SessionModel.id)
            .filter(
                Surveillance.enseignant_id == ens.id,
                Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
                SessionModel.annee_universitaire == annee_key,
            )
            .scalar() or 0.0
        )

    vol_horaire = float(ch.volume_horaire) if ch else 0.0

    return {
        "surveillance": {
            "id":                  s.id,
            "statut_surveillance": s.statut_surveillance,
            "mode_affectation":    s.mode_affectation,
            "charge":              float(s.charge),
            "presence":            s.presence,
            "est_externe":         s.est_externe,
            "motif_externe":       s.motif_externe,
            "created_at":          s.created_at.isoformat() if s.created_at else None,
            "updated_at":          s.updated_at.isoformat() if s.updated_at else None,
        },
        "enseignant": {
            "id":              ens.id                              if ens else None,
            "nom":             ens.nom                             if ens else None,
            "prenom":          ens.prenom                         if ens else None,
            "nom_complet":     f"{ens.prenom} {ens.nom}"          if ens else None,
            "grade":           ens.grade                          if ens else None,
            "email":           ens.email                          if ens else None,
            "telephone":       ens.telephone                      if ens else None,
            "volume_horaire":  vol_horaire,
            "volume_consomme": float(charge_consommee),
            "volume_restant":  round(vol_horaire - float(charge_consommee), 2),
            "departement": {
                "id":   dept_ens.id   if dept_ens else None,
                "nom":  dept_ens.nom  if dept_ens else None,
                "code": dept_ens.code if dept_ens else None,
            },
        },
        "planification": {
            "id":                     planif.id                     if planif else None,
            "type_epreuve":           planif.type_epreuve           if planif else None,
            "duree":                  planif.duree                  if planif else None,
            "semestre":               planif.semestre               if planif else None,
            "statut":                 planif.statut                 if planif else None,
            "nb_groupes":             planif.nb_groupes             if planif else None,
            "nb_surveillants_requis": planif.nb_surveillants_requis if planif else None,
            "mode_affectation":       planif.mode_affectation       if planif else None,
        },
        "session": {
            "id":                  sess_obj.id                  if sess_obj else None,
            "type_session":        sess_obj.type_session         if sess_obj else None,
            "annee_universitaire": sess_obj.annee_universitaire  if sess_obj else None,
            "date_debut":          str(sess_obj.date_debut)      if sess_obj else None,
            "date_fin":            str(sess_obj.date_fin)        if sess_obj else None,
            "statut":              sess_obj.statut               if sess_obj else None,
        },
        "departement_examen": {
            "id":   dept_exam.id   if dept_exam else None,
            "nom":  dept_exam.nom  if dept_exam else None,
            "code": dept_exam.code if dept_exam else None,
        },
        "creneau": {
            "id":          creneau.id               if creneau else None,
            "date":        str(creneau.date)         if creneau else None,
            "heure_debut": str(creneau.heure_debut)  if creneau else None,
            "heure_fin":   str(creneau.heure_fin)    if creneau else None,
            "libelle":     creneau.libelle           if creneau else None,
        },
        "matiere": {
            "id":           mat.id                  if mat else None,
            "code":         mat.code                if mat else None,
            "intitule":     mat.intitule             if mat else None,
            "coefficient":  float(mat.coefficient)  if mat and mat.coefficient else None,
            "credit":       mat.credit              if mat else None,
            "duree_examen": mat.duree_examen        if mat else None,
            "duree_ds":     mat.duree_ds            if mat else None,
        },
        "section": {
            "id":           sec.id           if sec else None,
            "nom":          sec.nom          if sec else None,
            "nb_etudiants": sec.nb_etudiants if sec else None,
            "niveau": {
                "id":             niv.id             if niv else None,
                "libelle":        niv.libelle        if niv else None,
                "type_formation": niv.type_formation if niv else None,
            },
        },
        "niveau": {
            "id":             niv.id             if niv else None,
            "libelle":        niv.libelle        if niv else None,
            "type_formation": niv.type_formation if niv else None,
        },
        "groupe": {
            "id":           grp.id           if grp else None,
            "numero":       grp.numero       if grp else None,
            "effectif":     grp.effectif     if grp else None,
            "nb_etudiants": grp.nb_etudiants if grp else None,
            "annee":        grp.annee        if grp else None,
        },
        "salle": {
            "id":          salle.id          if salle else None,
            "code":        salle.code        if salle else None,
            "designation": salle.designation if salle else None,
            "capacite":    salle.capacite    if salle else None,
            "batiment":    salle.batiment    if salle else None,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────────────────

def list_surveillances(
    db:               Session,
    *,
    planification_id: int | None  = None,
    enseignant_id:    int | None  = None,
    session_id:       int | None  = None,
    groupe_id:        int | None  = None,
    salle_id:         int | None  = None,
    est_externe:      bool | None = None,
    statut:           str | None  = None,
    skip:  int = 0,
    limit: int = 50,
) -> list[Surveillance]:
    if session_id is not None:
        q = (
            db.query(Surveillance)
            .options(
                selectinload(Surveillance.enseignant),
                selectinload(Surveillance.planification),
                selectinload(Surveillance.groupe),
                selectinload(Surveillance.salle),
            )
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .filter(Planification.session_id == session_id)
        )
        if planification_id is not None:
            q = q.filter(Surveillance.planification_id == planification_id)
        if enseignant_id is not None:
            q = q.filter(Surveillance.enseignant_id == enseignant_id)
        if groupe_id is not None:
            q = q.filter(Surveillance.groupe_id == groupe_id)
        if salle_id is not None:
            q = q.filter(Surveillance.salle_id == salle_id)
        if est_externe is not None:
            q = q.filter(Surveillance.est_externe == est_externe)
        if statut is not None:
            q = q.filter(Surveillance.statut_surveillance == statut)
        return q.offset(skip).limit(limit).all()

    q = _base(db)
    if planification_id is not None:
        q = q.filter(Surveillance.planification_id == planification_id)
    if enseignant_id is not None:
        q = q.filter(Surveillance.enseignant_id == enseignant_id)
    if groupe_id is not None:
        q = q.filter(Surveillance.groupe_id == groupe_id)
    if salle_id is not None:
        q = q.filter(Surveillance.salle_id == salle_id)
    if est_externe is not None:
        q = q.filter(Surveillance.est_externe == est_externe)
    if statut is not None:
        q = q.filter(Surveillance.statut_surveillance == statut)
    return q.offset(skip).limit(limit).all()


def get_surveillance(db: Session, surveillance_id: int) -> Surveillance | None:
    return _base(db).filter(Surveillance.id == surveillance_id).first()


def get_surveillances_for_planification(
    db: Session, planification_id: int
) -> list[Surveillance]:
    return _base(db).filter(
        Surveillance.planification_id == planification_id
    ).all()


def get_surveillances_for_groupe(
    db: Session, planification_id: int, groupe_id: int
) -> list[Surveillance]:
    return _base(db).filter(
        Surveillance.planification_id == planification_id,
        Surveillance.groupe_id        == groupe_id,
    ).all()


# ─────────────────────────────────────────────────────────────────────────────
# ← MODIFIÉ : ajout semestre + type_epreuve
# ─────────────────────────────────────────────────────────────────────────────

def get_surveillances_for_enseignant(
    db:                  Session,
    enseignant_id:       int,
    annee_universitaire: str | None = None,
    semestre:            int | None = None,   # ← AJOUTÉ
    type_epreuve:        str | None = None,   # ← AJOUTÉ
) -> list[Surveillance]:
    if annee_universitaire or semestre is not None or type_epreuve:
        q = (
            db.query(Surveillance)
            .options(
                selectinload(Surveillance.enseignant),
                selectinload(Surveillance.planification),
                selectinload(Surveillance.groupe),
                selectinload(Surveillance.salle),
            )
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .filter(Surveillance.enseignant_id == enseignant_id)
        )
        if annee_universitaire:
            q = (
                q.join(SessionModel, Planification.session_id == SessionModel.id)
                 .filter(SessionModel.annee_universitaire == annee_universitaire)
            )
        if semestre is not None:
            q = q.filter(Planification.semestre == semestre)
        if type_epreuve:
            q = q.filter(Planification.type_epreuve == type_epreuve)
        return q.all()

    return _base(db).filter(Surveillance.enseignant_id == enseignant_id).all()


# ─────────────────────────────────────────────────────────────────────────────
# ← MODIFIÉ : ajout semestre + type_epreuve
# ─────────────────────────────────────────────────────────────────────────────

def get_surveillances_enrichies_for_enseignant(
    db:                  Session,
    enseignant_id:       int,
    annee_universitaire: str | None = None,
    semestre:            int | None = None,   # ← AJOUTÉ
    type_epreuve:        str | None = None,   # ← AJOUTÉ
) -> dict:
    ens = db.query(Enseignant).filter(Enseignant.id == enseignant_id).first()
    if not ens:
        return {}

    dept = ens.departement

    # ← MODIFIÉ : passer les nouveaux filtres
    surveillances = get_surveillances_for_enseignant(
        db, enseignant_id, annee_universitaire,
        semestre=semestre,
        type_epreuve=type_epreuve,
    )

    # Déduire l'annee_key depuis la première surveillance si non fournie
    annee_key = annee_universitaire
    if not annee_key and surveillances:
        first_planif = surveillances[0].planification
        if first_planif and first_planif.session:
            annee_key = first_planif.session.annee_universitaire

    ch = None
    if annee_key:
        ch = db.query(ChargeHoraire).filter(
            ChargeHoraire.enseignant_id == enseignant_id,
            ChargeHoraire.annee_univ    == annee_key,
        ).first()

    charge_totale    = sum(float(s.charge) for s in surveillances)
    nb_confirmees    = sum(1 for s in surveillances if s.statut_surveillance == "CONFIRME")
    nb_presences     = sum(1 for s in surveillances if s.presence)
    nb_externes      = sum(1 for s in surveillances if s.est_externe)
    volume_horaire   = float(ch.volume_horaire) if ch else 0.0
    taux_utilisation = round(charge_totale / volume_horaire * 100, 2) if volume_horaire > 0 else 0.0

    surveillances_detail = []
    for s in surveillances:
        planif    = s.planification
        sess_obj  = planif.session         if planif else None
        cren      = planif.creneau         if planif else None
        sm        = planif.section_matiere if planif else None
        mat       = sm.matiere             if sm     else None
        sec       = sm.section             if sm     else None
        niv       = sec.niveau             if sec    else None
        dept_exam = None
        grp       = s.groupe
        salle     = s.salle

        surveillances_detail.append({
            "surveillance": {
                "id":                  s.id,
                "statut_surveillance": s.statut_surveillance,
                "mode_affectation":    s.mode_affectation,
                "charge":              float(s.charge),
                "presence":            s.presence,
                "est_externe":         s.est_externe,
                "motif_externe":       s.motif_externe,
                "created_at":          s.created_at.isoformat() if s.created_at else None,
                "updated_at":          s.updated_at.isoformat() if s.updated_at else None,
            },
            "session": {
                "id":                  sess_obj.id                  if sess_obj else None,
                "type_session":        sess_obj.type_session         if sess_obj else None,
                "annee_universitaire": sess_obj.annee_universitaire  if sess_obj else None,
                "date_debut":          str(sess_obj.date_debut)      if sess_obj else None,
                "date_fin":            str(sess_obj.date_fin)        if sess_obj else None,
                "statut":              sess_obj.statut               if sess_obj else None,
            },
            "planification": {
                "id":                     planif.id                     if planif else None,
                "type_epreuve":           planif.type_epreuve           if planif else None,
                "semestre":               planif.semestre               if planif else None,
                "duree":                  planif.duree                  if planif else None,
                "nb_surveillants_requis": planif.nb_surveillants_requis if planif else None,
                "statut":                 planif.statut                 if planif else None,
            },
            "departement_examen": {
                "id":   dept_exam.id   if dept_exam else None,
                "nom":  dept_exam.nom  if dept_exam else None,
                "code": dept_exam.code if dept_exam else None,
            },
            "creneau": {
                "id":          cren.id              if cren else None,
                "date":        str(cren.date)        if cren else None,
                "heure_debut": str(cren.heure_debut) if cren else None,
                "heure_fin":   str(cren.heure_fin)   if cren else None,
                "libelle":     cren.libelle          if cren else None,
            },
            "matiere": {
                "id":       mat.id       if mat else None,
                "code":     mat.code     if mat else None,
                "intitule": mat.intitule if mat else None,
            },
            "section": {
                "id":  sec.id  if sec else None,
                "nom": sec.nom if sec else None,
            },
            "niveau": {
                "id":             niv.id             if niv else None,
                "libelle":        niv.libelle        if niv else None,
                "type_formation": niv.type_formation if niv else None,
            },
            "groupe": {
                "id":           grp.id           if grp else None,
                "numero":       grp.numero       if grp else None,
                "effectif":     grp.effectif     if grp else None,
                "nb_etudiants": grp.nb_etudiants if grp else None,
                "annee":        grp.annee        if grp else None,
            },
            "salle": {
                "id":          salle.id          if salle else None,
                "code":        salle.code        if salle else None,
                "designation": salle.designation if salle else None,
                "capacite":    salle.capacite    if salle else None,
                "batiment":    salle.batiment    if salle else None,
            },
        })

    return {
        "enseignant": {
            "id":          ens.id,
            "nom":         ens.nom,
            "prenom":      ens.prenom,
            "nom_complet": f"{ens.prenom} {ens.nom}",
            "grade":       ens.grade,
            "email":       ens.email,
            "telephone":   ens.telephone,
            "departement": {
                "id":   dept.id   if dept else None,
                "nom":  dept.nom  if dept else None,
                "code": dept.code if dept else None,
            },
        },
        "charge_horaire": {
            "annee_universitaire": annee_key,
            "volume_horaire":      volume_horaire,
            "volume_consomme":     round(charge_totale, 2),
            "volume_restant":      round(volume_horaire - charge_totale, 2),
            "taux_utilisation":    taux_utilisation,
        },
        "statistiques": {
            "total_surveillances": len(surveillances),
            "charge_totale":       round(charge_totale, 2),
            "nb_confirmees":       nb_confirmees,
            "nb_presences":        nb_presences,
            "nb_externes":         nb_externes,
            "taux_utilisation":    taux_utilisation,
        },
        "surveillances": surveillances_detail,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────────────────────

def create_surveillance(db: Session, payload: SurveillanceCreate) -> Surveillance:
    item = Surveillance(
        planification_id=payload.planification_id,
        enseignant_id=payload.enseignant_id,
        groupe_id=payload.groupe_id,
        salle_id=payload.salle_id,
        charge=payload.charge,
        mode_affectation=(
            payload.mode_affectation.value
            if hasattr(payload.mode_affectation, "value")
            else payload.mode_affectation
        ),
        statut_surveillance=(
            payload.statut_surveillance.value
            if hasattr(payload.statut_surveillance, "value")
            else payload.statut_surveillance
        ),
        est_externe=payload.est_externe,
        motif_externe=payload.motif_externe,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return get_surveillance(db, item.id) or item


def create_surveillances_batch(
    db: Session, payloads: list[SurveillanceCreate]
) -> list[Surveillance]:
    items = [
        Surveillance(
            planification_id=p.planification_id,
            enseignant_id=p.enseignant_id,
            groupe_id=p.groupe_id,
            salle_id=p.salle_id,
            charge=p.charge,
            mode_affectation=(
                p.mode_affectation.value
                if hasattr(p.mode_affectation, "value")
                else p.mode_affectation
            ),
            statut_surveillance=(
                p.statut_surveillance.value
                if hasattr(p.statut_surveillance, "value")
                else p.statut_surveillance
            ),
            est_externe=p.est_externe,
            motif_externe=p.motif_externe,
        )
        for p in payloads
    ]
    db.add_all(items)
    db.commit()
    result = []
    for item in items:
        db.refresh(item)
        result.append(get_surveillance(db, item.id) or item)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────────────────────

def update_surveillance(
    db: Session, surveillance: Surveillance, payload: SurveillanceUpdate
) -> Surveillance:
    if payload.presence is not None:
        surveillance.presence = payload.presence
    if payload.statut_surveillance is not None:
        surveillance.statut_surveillance = (
            payload.statut_surveillance.value
            if hasattr(payload.statut_surveillance, "value")
            else payload.statut_surveillance
        )
    if payload.charge is not None:
        surveillance.charge = payload.charge
    if payload.motif_externe is not None:
        surveillance.motif_externe = payload.motif_externe
    surveillance.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(surveillance)
    return get_surveillance(db, surveillance.id) or surveillance


# ─────────────────────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────────────────────

def delete_surveillance(db: Session, surveillance: Surveillance) -> None:
    db.delete(surveillance)
    db.commit()


def delete_surveillance_by_id(db: Session, surveillance_id: int) -> bool:
    s = get_surveillance(db, surveillance_id)
    if s:
        delete_surveillance(db, s)
        return True
    return False


def delete_surveillances_for_planification(db: Session, planification_id: int) -> int:
    count = (
        db.query(Surveillance)
        .filter(Surveillance.planification_id == planification_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return count


def delete_surveillances_for_session(db: Session, session_id: int) -> int:
    # Récupérer d'abord les IDs des planifications de la session
    planif_ids = [
        p.id for p in db.query(Planification.id)
        .filter(Planification.session_id == session_id)
        .all()
    ]
    if not planif_ids:
        return 0
    count = (
        db.query(Surveillance)
        .filter(Surveillance.planification_id.in_(planif_ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return count


# ─────────────────────────────────────────────────────────────────────────────
# REPLACEMENT
# ─────────────────────────────────────────────────────────────────────────────

def replace_surveillance(
    db:                Session,
    old:               Surveillance,
    new_enseignant_id: int,
    motif:             str,
) -> tuple[Surveillance, Surveillance]:
    new_payload = SurveillanceCreate(
        planification_id=old.planification_id,
        enseignant_id=new_enseignant_id,
        groupe_id=old.groupe_id,
        salle_id=old.salle_id,
        charge=float(old.charge),
        mode_affectation=old.mode_affectation,
        statut_surveillance=old.statut_surveillance,
        est_externe=old.est_externe,
        motif_externe=f"Remplacement: {motif}" if motif else old.motif_externe,
    )
    old_id         = old.id
    old_enseignant = old.enseignant_id

    new = create_surveillance(db, new_payload)
    delete_surveillance(db, old)

    class _OldInfo:
        def __init__(self, _id, _ens_id):
            self.id            = _id
            self.enseignant_id = _ens_id

    return _OldInfo(old_id, old_enseignant), new


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

def get_enseignant_charge_for_year(
    db: Session, enseignant_id: int, annee_universitaire: str
) -> float:
    result = (
        db.query(func.coalesce(func.sum(Surveillance.charge), 0))
        .select_from(Surveillance)
        .join(Planification, Surveillance.planification_id == Planification.id)
        .join(SessionModel,  Planification.session_id      == SessionModel.id)
        .filter(
            Surveillance.enseignant_id           == enseignant_id,
            Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
            SessionModel.annee_universitaire     == annee_universitaire,
        )
        .scalar()
    )
    return float(result or 0)


def count_surveillances_for_enseignant(
    db: Session, enseignant_id: int, annee_universitaire: str | None = None
) -> int:
    if annee_universitaire:
        return (
            db.query(func.count(Surveillance.id))
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(SessionModel,  Planification.session_id      == SessionModel.id)
            .filter(
                Surveillance.enseignant_id           == enseignant_id,
                Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
                SessionModel.annee_universitaire     == annee_universitaire,
            )
            .scalar() or 0
        )
    return (
        db.query(func.count(Surveillance.id))
        .filter(
            Surveillance.enseignant_id           == enseignant_id,
            Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
        )
        .scalar() or 0
    )