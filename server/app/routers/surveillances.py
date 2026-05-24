"""
routers/surveillances.py
Surveillance endpoints — version enrichie.

Tous les endpoints retournent les informations complètes via les relations
bidirectionnelles SQLAlchemy (pas uniquement des IDs).

Endpoints existants conservés et enrichis :
  POST   /surveillances/affecter-session
  POST   /surveillances/manual-assignment
  POST   /surveillances/manual-assignment-batch 
  GET    /surveillances/enseignant/{id}/toutes-surveillances 
  ? GET    /surveillances/{session_id}    != /surveillances/getallsurveillants                   
  GET    /surveillances/{surveillance_id}/full-details
  GET    /surveillances/getallsurveillants  
   GET    /surveillances/enseignants-disponibles/{planif_id}
  PATCH  /surveillances/edit/{surveillance_id}  
  POST   /surveillances/{surveillance_id}/reassign   
  DELETE /surveillances/{surveillance_id}  
  DELETE /surveillances/session/{session_id}/reset   
  GET    /surveillances/session/{session_id}/rapport  
  GET    /surveillances/session/{session_id}/conflits  
  GET    /surveillances/statistiques   
  GET    /surveillances/enseignant/{id}/disponibilites 
"""

from typing import Optional
import csv
from io import StringIO
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.surv_service import SurvService
from app.schemas.surveillance_schema import (
    SurveillanceUpdate,
    ManualAssignmentRequest,
    ManualAssignmentBatchRequest,
    RemplacementRequest,
    AffecterSessionRequest,
    AffecterSessionResponse,
    AffecterSessionResult,
    GroupeResultOut,
    EnseignantAffecteOut,
    DepartementOut,
    NiveauOut,
    SectionOut,
    GroupeOut,
    SalleOut,
    MatiereOut,
    CreneauOut,
    SessionOut,
    RaisonExclusionOut,
    GetAllSurveillantsResponse,
    GetAllSurveillantsItem,
    GetDisponibilitesResponse,
    DisponibiliteItem,
    StatistiquesResponse,
)
from app.schemas.disponibilite_schema import (
    DisponibiliteEnseignantCreate,
    DisponibiliteEnseignantOut,
)

router = APIRouter(prefix="/surveillances", tags=["Surveillance"])


def _build_result(r, db: Session, session_orm) -> AffecterSessionResult:
    """
    Transforme un PlanificationAffectationResult (algo) en AffecterSessionResult
    avec TOUS les sous-objets enrichis depuis la base.
    """
    from app.models.planification import Planification
    from app.models.surveillance import Surveillance as SurveillanceModel

    planif = db.query(Planification).filter(
        Planification.id == r.planification_id
    ).first()

    sm  = planif.section_matiere if planif else None
    mat = sm.matiere             if sm     else None
    sec = sm.section             if sm     else None
    niv = sec.niveau             if sec    else None
    dep = niv.departement        if niv    else None
    cren = planif.creneau        if planif else None
    
    # Charger le département de l'examen si section_departement_id existe
    dept_exam = None
    if planif and planif.section_departement_id:
        from app.models.departement_niveau_section import Departement
        dept_exam = db.query(Departement).filter(
            Departement.id == planif.section_departement_id
        ).first()
    
    sess = planif.session        if planif else None

    matiere_out = MatiereOut(
        id=mat.id, code=mat.code, intitule=mat.intitule,
        coefficient=float(mat.coefficient) if mat and mat.coefficient else None,
        credit=mat.credit,
        duree_examen=mat.duree_examen, duree_ds=mat.duree_ds,
    ) if mat else None

    niveau_out = NiveauOut(
        id=niv.id, libelle=niv.libelle, type_formation=niv.type_formation,
    ) if niv else None

    section_out = SectionOut(
        id=sec.id, nom=sec.nom, niveau=niveau_out,
    ) if sec else None

    dept_exam_out = DepartementOut(
        id=dept_exam.id, nom=dept_exam.nom, code=dept_exam.code,
    ) if dept_exam else None

    creneau_out = CreneauOut(
        id=cren.id,
        date=str(cren.date),
        heure_debut=str(cren.heure_debut),
        heure_fin=str(cren.heure_fin),
        libelle=cren.libelle,
    ) if cren else None

    session_out = SessionOut(
        id=sess.id,
        type_session=sess.type_session,
        annee_universitaire=sess.annee_universitaire,
        date_debut=str(sess.date_debut),
        date_fin=str(sess.date_fin),
        statut=sess.statut,
    ) if sess else None

    groupes_out = []
    for g in r.groupes:
        from app.models.departement_niveau_section import Groupe
        grp_orm   = db.query(Groupe).filter(Groupe.id == g.groupe_id).first()  if g.groupe_id else None
        from app.models.salle_session import Salle
        salle_orm = db.query(Salle).filter(Salle.code == g.salle_id).first()   if g.salle_id  else None

        groupe_out = GroupeOut(
            id=grp_orm.id, numero=grp_orm.numero,
            effectif=grp_orm.effectif, nb_etudiants=grp_orm.nb_etudiants,
            annee=grp_orm.annee,
        ) if grp_orm else None

        salle_out = SalleOut(
            id=salle_orm.id, code=salle_orm.code,
            designation=salle_orm.designation,
            capacite=salle_orm.capacite, batiment=salle_orm.batiment,
        ) if salle_orm else None

        surveillants_out = []
        for surv_obj in g.surveillants_affectes:
            surv_db = db.query(SurveillanceModel).filter(
                SurveillanceModel.id == surv_obj.id
            ).first()
            
            if surv_db:
                ens      = surv_db.enseignant
                dept_ens = ens.departement if ens else None
                grp_surv = surv_db.groupe
                salle_surv = surv_db.salle
                s_id = surv_db.id
                ens_id = ens.id if ens else surv_db.enseignant_id
                charge = surv_db.charge
                mode_aff = surv_db.mode_affectation
                statut = surv_db.statut_surveillance
                pres = surv_db.presence
                est_ext = surv_db.est_externe
                motif_ext = surv_db.motif_externe
            else:
                # Dry run fallback
                ens = getattr(surv_obj, "enseignant", None)
                dept_ens = ens.departement if ens else getattr(surv_obj, "_fake_departement", None)
                grp_surv = getattr(surv_obj, "groupe", None)
                salle_surv = getattr(surv_obj, "salle", None)
                s_id = surv_obj.id
                ens_id = surv_obj.enseignant_id
                charge = surv_obj.charge
                mode_aff = surv_obj.mode_affectation
                statut = surv_obj.statut_surveillance
                pres = surv_obj.presence
                est_ext = surv_obj.est_externe
                motif_ext = surv_obj.motif_externe

            if not ens and not surv_db and not hasattr(surv_obj, "_fake_nom"):
                continue

            surveillants_out.append(EnseignantAffecteOut(
                surveillance_id=s_id,
                enseignant_id=ens_id,
                nom=ens.nom                   if ens else getattr(surv_obj, "_fake_nom", ""),
                prenom=ens.prenom             if ens else getattr(surv_obj, "_fake_prenom", ""),
                grade=ens.grade               if ens else getattr(surv_obj, "_fake_grade", None),
                email=ens.email               if ens else None,
                telephone=ens.telephone       if ens else None,
                departement=DepartementOut(
                    id=dept_ens.id if dept_ens else None,
                    nom=dept_ens.nom if dept_ens else getattr(surv_obj, "_fake_dept_nom", None),
                    code=dept_ens.code if dept_ens else getattr(surv_obj, "_fake_dept_code", None),
                ) if dept_ens or hasattr(surv_obj, "_fake_dept_nom") else None,
                groupe=GroupeOut(
                    id=grp_surv.id,
                    numero=grp_surv.numero,
                    effectif=grp_surv.effectif,
                    nb_etudiants=grp_surv.nb_etudiants,
                    annee=grp_surv.annee,
                ) if grp_surv else None,
                salle=SalleOut(
                    id=salle_surv.id,
                    code=salle_surv.code,
                    designation=salle_surv.designation,
                    capacite=salle_surv.capacite,
                    batiment=salle_surv.batiment,
                ) if salle_surv else None,
                charge=float(charge),
                mode_affectation=mode_aff,
                statut_surveillance=statut,
                presence=pres,
                est_externe=est_ext,
                motif_externe=motif_ext,
            ))

        groupes_out.append(GroupeResultOut(
            groupe=groupe_out,
            salle=salle_out,
            statut=g.statut,
            surveillants_affectes=surveillants_out,
            surveillants_requis=g.surveillants_requis,
            manquants=g.manquants,
        ))

    return AffecterSessionResult(
        planification_id=r.planification_id,
        type_epreuve=planif.type_epreuve       if planif else "",
        semestre=planif.semestre               if planif else None,
        duree=planif.duree                     if planif else None,
        statut_planif=planif.statut            if planif else "",
        nb_surveillants_requis=planif.nb_surveillants_requis if planif else 0,
        matiere=matiere_out,
        section=section_out,
        departement_examen=dept_exam_out,
        creneau=creneau_out,
        session=session_out,
        statut=r.statut,
        surveillants_requis=r.surveillants_requis,
        surveillants_affectes=len(r.surveillants_affectes),
        manquants=r.manquants,
        groupes=groupes_out,
        raisons_exclusion=[
            RaisonExclusionOut(
                enseignant_id=v.enseignant_id,
                nom=v.nom, prenom=v.prenom,
                raison=v.raison.value,
                details=v.details,
            )
            for v in r.violations
        ],
    )


# ══════════════════════════════════════════════════════════════════════════════
# AFFECTATION AUTOMATIQUE
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/affecter-session", response_model=AffecterSessionResponse)
def affecter_session_automatique(
    payload: AffecterSessionRequest,
    db: Session = Depends(get_db),
):
    """
    Lance l'algorithme d'affectation automatique des surveillants pour une session.

    BODY (JSON) :
      - session_id   (int, obligatoire) : ID de la session d'examens
      - section_nom  (str, optionnel)   : Filtrer par nom de section ex: "IGL3"
      - periode      (str, optionnel)   : Filtrer par période ex: "2025/2026-S1"
      - type_epreuve (str, optionnel)   : Filtrer par type ex: "EXAMEN_FINAL" ou "DS"

    RÉPONSE :
      - session                   : infos complètes de la session
      - total_planifications      : nombre total de planifications traitées
      - affectees_automatiquement : nombre de planifications entièrement affectées
      - en_conflit                : nombre de planifications avec manque de surveillants
      - message                   : message récapitulatif de l'algorithme
      - resultats                 : liste des planifications affectées (même partiellement)
          • matiere, section, departement_examen, creneau, session
          • groupes : liste des groupes avec leurs surveillants affectés
              - enseignant (nom, prénom, grade, email, département)
              - groupe, salle, charge, mode, statut, présence, est_externe
          • raisons_exclusion : pourquoi certains enseignants ont été écartés
      - non_affectees             : planifications sans aucun surveillant (0 affecté)

    CONTRAINTES appliquées par l'algorithme :
      C1 - Volume horaire restant suffisant
      C2 - Disponibilité déclarée (pas d'indisponibilité sur le créneau)
      C3 - Pas de conflit de matière (enseignant ne surveille pas sa propre matière)
      C4 - Non-simultanéité (pas déjà affecté au même créneau)
      C5 - Appartenance au département de l'examen (priorité internes)
      C6 - Équité de charge (prioriser ceux avec le plus de volume restant)
    """
    from app.models.salle_session import Session as SessionModel

    service = SurvService(db)
    try:
        results, message = service.affecter_session_automatique(
            session_id=payload.session_id,
            section_nom=payload.section_nom,
            periode=payload.periode,
            type_epreuve=payload.type_epreuve,
            dry_run=not payload.save,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    session_orm = db.query(SessionModel).filter(
        SessionModel.id == payload.session_id
    ).first()

    session_out = SessionOut(
        id=session_orm.id,
        type_session=session_orm.type_session,
        annee_universitaire=session_orm.annee_universitaire,
        date_debut=str(session_orm.date_debut),
        date_fin=str(session_orm.date_fin),
        statut=session_orm.statut,
    ) if session_orm else None

    resultats     = []
    non_affectees = []

    for r in results:
        result_out = _build_result(r, db, session_orm)
        if r.statut == "CONFLIT" and len(r.surveillants_affectes) == 0:
            non_affectees.append(result_out)
        else:
            resultats.append(result_out)

    affectees = sum(1 for r in results if r.statut == "AFFECTEE")
    conflits  = sum(1 for r in results if r.statut in ("CONFLIT", "CONFLIT_PARTIEL"))

    return AffecterSessionResponse(
        session_id=payload.session_id,
        session=session_out,
        total_planifications=len(results),
        affectees_automatiquement=affectees,
        en_conflit=conflits,
        message=message,
        resultats=resultats,
        non_affectees=non_affectees,
    )


# ══════════════════════════════════════════════════════════════════════════════
# AFFECTATION MANUELLE — planif unique
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/manual-assignment")
def manual_assignment_single(
    request: ManualAssignmentRequest,
    db: Session = Depends(get_db),
):
    """
    Affecte manuellement un ou plusieurs enseignants à une planification précise.

    BODY (JSON) :
      - session_id       (int)       : ID de la session
      - planification_id (int)       : ID de la planification cible
      - groupe_id        (int)       : ID du groupe concerné
      - salle_id         (int)       : ID de la salle concernée
      - enseignant_ids   (list[int]) : liste des IDs des enseignants à affecter
      - motifs_externes  (dict)      : optionnel — {enseignant_id: "motif"} pour les externes

    RÉPONSE :
      - planification_id      : ID de la planification
      - statut                : "CONFLIT_RESOLU" si complet, "INCOMPLET" sinon
      - surveillants_requis   : nombre de surveillants attendus
      - surveillants_inseres  : nombre effectivement insérés
      - manquants             : différence (0 si complet)
      - surveillances         : détail complet de chaque surveillance créée
          • enseignant (nom, grade, département, volume horaire)
          • planification, session, créneau, matière, section
          • groupe, salle, charge, mode, statut

    CONTRAINTE appliquée :
      - C4 uniquement : non-simultanéité — si l'enseignant est déjà affecté
        au même créneau, il est rejeté avec raison "DEJA_AFFECTE"
      - Si un rejet survient, TOUTES les affectations de la requête sont annulées (rollback)

    ERREURS :
      - 409 : validation échouée (enseignant déjà affecté en simultané)
      - 400 : erreur inattendue
    """
    service = SurvService(db)
    try:
        return service.affecter_planification_manuellement(request)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# AFFECTATION MANUELLE — batch session
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/manual-assignment-batch")
def manual_assignment_batch(
    request: ManualAssignmentBatchRequest,
    db: Session = Depends(get_db),
):
    """
    Affecte manuellement des enseignants à plusieurs planifications en une seule requête.

    BODY (JSON) :
      - session_id      (int)  : ID de la session
      - affectations    (list) : liste d'objets contenant :
          • planification_id (int)       : ID de la planification
          • groupe_id        (int)       : ID du groupe
          • salle_id         (int)       : ID de la salle
          • enseignant_ids   (list[int]) : IDs des enseignants à affecter
      - motifs_externes (dict) : optionnel — {enseignant_id: "motif"} pour les externes

    RÉPONSE (succès) :
      - session_id                   : ID de la session
      - statut                       : "SUCCES"
      - total_surveillances_inserees : nombre total de surveillances créées
      - surveillances                : détail complet de chaque surveillance créée

    RÉPONSE (avertissement) :
      - statut                        : "AVERTISSEMENT"
      - message                       : explication
      - planifications_non_affectees  : liste des planif_ids incomplètes

    CONTRAINTE appliquée :
      - C4 uniquement : non-simultanéité par enseignant
      - Si incomplet (moins d'enseignants que requis), retourne AVERTISSEMENT sans insérer

    ERREURS :
      - 409 : conflit de simultanéité détecté
      - 400 : erreur inattendue
    """
    service = SurvService(db)
    try:
        return service.affecter_session_manuellement(request)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# PROFIL COMPLET D'UN ENSEIGNANT
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/enseignant/{enseignant_id}/toutes-surveillances")
def get_all_surveillances_enseignant(
    enseignant_id:       int,
    annee_universitaire: Optional[str] = Query(None, description="Ex: 2025/2026"),
    semestre:            Optional[int] = Query(None, description="1 ou 2"),
    type_epreuve:        Optional[str] = Query(None, description="DS ou EXAMEN_FINAL"),
    db: Session = Depends(get_db),
):
    """
    Retourne le profil complet d'un enseignant avec toutes ses surveillances.

    PATH :
      - enseignant_id (int) : ID de l'enseignant

    QUERY PARAMS (tous optionnels) :
      - annee_universitaire : filtrer par année ex: "2025/2026"
      - semestre            : filtrer par semestre (1 ou 2)
      - type_epreuve        : filtrer par type ("DS" ou "EXAMEN_FINAL")

    RÉPONSE :
      - enseignant :
          • id, nom, prenom, nom_complet, grade, email, téléphone
          • departement (id, nom, code)
      - charge_horaire :
          • annee_universitaire
          • volume_horaire   : heures allouées
          • volume_consomme  : heures déjà utilisées en surveillance
          • volume_restant   : heures encore disponibles
          • taux_utilisation : pourcentage consommé
      - statistiques :
          • total_surveillances, charge_totale
          • nb_confirmees, nb_presences, nb_externes
          • taux_utilisation
      - surveillances : liste détaillée de chaque surveillance avec :
          • session, planification, créneau, matière, section, niveau
          • groupe, salle, département examen
          • statut, mode, charge, présence, est_externe

    ERREURS :
      - 404 : enseignant non trouvé
    """
    from app.crud.crud_surv import get_surveillances_enrichies_for_enseignant
    data = get_surveillances_enrichies_for_enseignant(
        db, enseignant_id, annee_universitaire,
        semestre=semestre,
        type_epreuve=type_epreuve,
    )
    if not data:
        raise HTTPException(status_code=404, detail=f"Enseignant {enseignant_id} non trouvé")
    return data


# ══════════════════════════════════════════════════════════════════════════════
# LISTE TOUS LES ENSEIGNANTS AVEC VOLUME (route statique avant /{session_id})
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/getallsurveillants", response_model=GetAllSurveillantsResponse)
def get_all_surveillants(
    session_id: int = Query(...),
    page:  int = Query(1,  ge=1),
    limit: int = Query(100, ge=1, le=500),
    sort:  str = Query("volume_restant"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """Liste tous les enseignants avec volume annuel et charge surveillance (annee session)."""
    from app.models.salle_session import Session as SessionModel
    from app.models.enseignant import Enseignant

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    service = SurvService(db)
    enseignants = db.query(Enseignant).all()
    items = []

    annee_univ = session.annee_universitaire
    session_label = f"{session.type_session} {annee_univ}".strip()

    for ens in enseignants:
        vol = service.get_volume_restant_enseignant(ens.id, annee_univ)
        dept = ens.departement
        items.append(
            GetAllSurveillantsItem(
                enseignant_id=ens.id,
                nom=ens.nom,
                prenom=ens.prenom,
                grade=ens.grade,
                departement={
                    "id": dept.id if dept else None,
                    "nom": dept.nom if dept else "Unknown",
                    "code": dept.code if dept else "UNK",
                },
                volume_horaire=vol["volume_horaire"],
                volume_consomme=vol["volume_consomme"],
                volume_restant=vol["volume_restant"],
                volume_annuel=vol["volume_annuel"],
                charge_surveillance=vol["charge_surveillance"],
                taux_utilisation=vol["taux_utilisation"],
                nb_surveillances=vol["nb_surveillances"],
            )
        )

    allowed_sort = {
        "volume_restant",
        "volume_consomme",
        "volume_horaire",
        "volume_annuel",
        "charge_surveillance",
        "taux_utilisation",
        "nb_surveillances",
    }
    sort_key = sort if sort in allowed_sort else "charge_surveillance"
    items.sort(key=lambda x: getattr(x, sort_key, 0) or 0, reverse=(order == "desc"))
    start = (page - 1) * limit
    paginated = items[start : start + limit]

    return GetAllSurveillantsResponse(
        session_id=session_id,
        annee_universitaire=annee_univ,
        session_label=session_label,
        data=paginated,
        pagination={
            "page": page,
            "limit": limit,
            "total": len(items),
            "pages": (len(items) + limit - 1) // limit,
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES SURVEILLANCES D'UNE SESSION
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/{session_id}")
def get_session_surveillances(
    session_id:     int,
    departement_id: Optional[int] = Query(None),
    groupe_id:      Optional[int] = Query(None),
    salle_id:       Optional[int] = Query(None),
    type_epreuve:   Optional[str] = Query(None),
    statut:         Optional[str] = Query(None),
    section_id:     Optional[int] = Query(None),
    enseignant_id:  Optional[int] = Query(None),
    semestre:       Optional[int] = Query(None),
    skip:  int = Query(0,  ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Retourne la liste paginée et filtrée de toutes les surveillances d'une session.

    PATH :
      - session_id (int) : ID de la session

    QUERY PARAMS (tous optionnels sauf session_id) :
      - departement_id : filtrer par département de l'examen
      - groupe_id      : filtrer par groupe
      - salle_id       : filtrer par salle
      - type_epreuve   : "DS" ou "EXAMEN_FINAL"
      - statut         : "AFFECTE" ou "CONFIRME"
      - section_id     : filtrer par section
      - enseignant_id  : filtrer par enseignant
      - semestre       : 1 ou 2
      - skip           : pagination — offset (défaut 0)
      - limit          : pagination — taille de page (défaut 50, max 200)

    RÉPONSE :
      - session : infos de la session (id, type, annee, dates, statut)
      - total   : nombre total de résultats (avant pagination)
      - skip    : offset appliqué
      - limit   : limite appliquée
      - data    : liste de surveillances enrichies, chacune contenant :
          • surveillance (id, statut, mode, charge, présence, est_externe)
          • enseignant (nom, grade, département, volume horaire)
          • planification (type, semestre, durée, nb_requis)
          • session, créneau, matière, section, niveau
          • groupe, salle, département examen

    ERREURS :
      - 404 : session non trouvée
    """
    from app.models.surveillance import Surveillance
    from app.models.planification import Planification
    from app.models.salle_session import Session as SessionModel, Creneau
    from app.crud.crud_surv import _enrich_surveillance
    from app.models.matiere import SectionMatiere

    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail=f"Session {session_id} non trouvée")

    q = (
        db.query(Surveillance)
        .select_from(Surveillance)
        .join(Planification, Surveillance.planification_id == Planification.id)
        .join(Creneau, Planification.creneau_id == Creneau.id)
        .filter(Planification.session_id == session_id)
    )
    if departement_id: q = q.filter(Planification.departement_id == departement_id)
    if type_epreuve:   q = q.filter(Planification.type_epreuve == type_epreuve)
    if statut:         q = q.filter(Surveillance.statut_surveillance == statut)
    if groupe_id:      q = q.filter(Surveillance.groupe_id == groupe_id)
    if salle_id:       q = q.filter(Surveillance.salle_id == salle_id)
    if semestre:       q = q.filter(Planification.semestre == semestre)
    if section_id:
        q = (
            q.join(SectionMatiere, Planification.section_matiere_id == SectionMatiere.id)
            .filter(SectionMatiere.section_id == section_id)
        )
    if enseignant_id: q = q.filter(Surveillance.enseignant_id == enseignant_id)
    q = q.order_by(Creneau.date.asc(), Creneau.heure_debut.asc())

    total = q.count()
    survs = q.offset(skip).limit(limit).all()
    data  = [_enrich_surveillance(db, s, session_obj.annee_universitaire) for s in survs]

    return {
        "session": {
            "id": session_obj.id, "type_session": session_obj.type_session,
            "annee_universitaire": session_obj.annee_universitaire,
            "date_debut": str(session_obj.date_debut),
            "date_fin":   str(session_obj.date_fin),
            "statut":     session_obj.statut,
        },
        "total": total, "skip": skip, "limit": limit, "data": data,
    }


# ══════════════════════════════════════════════════════════════════════════════
# DÉTAIL D'UNE SURVEILLANCE
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/{surveillance_id}/full-details")
def get_surveillance_detail(surveillance_id: int, db: Session = Depends(get_db)):
    """
    Retourne le détail complet d'une surveillance par son ID.

    PATH :
      - surveillance_id (int) : ID de la surveillance

    RÉPONSE :
      - surveillance : id, statut, mode, charge, présence, est_externe,
                       motif_externe, created_at, updated_at
      - enseignant   : nom, prénom, grade, email, téléphone, département,
                       volume_horaire, volume_consomme, volume_restant
      - planification : id, type_epreuve, semestre, durée, statut, nb_requis
      - session      : id, type, annee, dates, statut
      - creneau      : id, date, heure_debut, heure_fin, libelle
      - matiere      : id, code, intitule, coefficient, credit, durées
      - section      : id, nom, nb_etudiants, niveau (libelle, type_formation)
      - niveau       : id, libelle, type_formation
      - groupe       : id, numero, effectif, nb_etudiants, annee
      - salle        : id, code, designation, capacite, batiment
      - departement_examen : id, nom, code

    ERREURS :
      - 404 : surveillance non trouvée
    """
    from app.crud.crud_surv import get_surveillance, _enrich_surveillance
    s = get_surveillance(db, surveillance_id)
    if not s:
        raise HTTPException(status_code=404, detail="Surveillance non trouvée")
    return _enrich_surveillance(db, s)


# ══════════════════════════════════════════════════════════════════════════════
# ENSEIGNANTS DISPONIBLES POUR UNE PLANIFICATION
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/enseignants-disponibles/{planif_id}")
def get_enseignants_disponibles(planif_id: int, db: Session = Depends(get_db)):
    """
    Retourne la liste des enseignants éligibles pour surveiller une planification,
    groupés par département, avec avertissements si indisponibilité déclarée le jour J.

    PATH :
      - planif_id (int) : ID de la planification cible

    LOGIQUE :
      - Contrainte stricte  → non-simultanéité (C4) : si l'enseignant est déjà
        affecté à une autre surveillance au même créneau (même date + même heure début),
        il est EXCLU de la liste.
      - Contrainte souple   → indisponibilité le même JOUR (sans regarder l'heure) :
        si l'enseignant a une entrée dans disponibilite_enseignant pour la même date
        que la planification, il est retourné AVEC un avertissement et le détail
        complet de son indisponibilité (type, heures, motif).

    RÉPONSE :
      - planification_id         : ID de la planification
      - date_planification       : date du créneau de la planification
      - total_disponibles        : nombre total d'enseignants retournés
      - total_avec_avertissement : nombre d'enseignants avec au moins un avertissement
      - departements             : liste groupée par département, chaque département :
          • departement_id, departement_nom, departement_code
          • total : nombre d'enseignants dans ce département
          • enseignants : liste triée par volume_restant décroissant, chacun avec :
              · enseignant_id, nom, prenom, grade, email, telephone
              · volume_horaire, volume_consomme, volume_restant, nb_surveillances
              · a_avertissement (bool)
              · avertissements : liste des indisponibilités du jour avec :
                  - date, heure_debut, heure_fin, type_dispo, motif

    ERREURS :
      - 404 : planification non trouvée
    """
    service = SurvService(db)
    result  = service.get_enseignants_disponibles_pour_planification(planif_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Planification {planif_id} non trouvée")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# MODIFIER UNE SURVEILLANCE
# ══════════════════════════════════════════════════════════════════════════════

@router.patch("/edit/{surveillance_id}")
def update_surveillance_endpoint(surveillance_id: int, payload: SurveillanceUpdate, db: Session = Depends(get_db)):
    """
    Modifie partiellement une surveillance existante.
    Seuls les champs fournis dans le body sont mis à jour (PATCH sémantique).

    PATH :
      - surveillance_id (int) : ID de la surveillance à modifier

    BODY (JSON, tous les champs sont optionnels) :
      - presence            (bool)   : marquer la présence ou l'absence de l'enseignant
      - statut_surveillance (str)    : "AFFECTE" ou "CONFIRME"
      - charge              (float)  : nombre d'heures imputées (ex: 1.5)
      - motif_externe       (str)    : motif si l'enseignant est externe au département

    RÉPONSE :
      Surveillance enrichie complète (même structure que /full-details) :
      - surveillance, enseignant, planification, session, créneau,
        matière, section, niveau, groupe, salle, département examen

    NOTES :
      - Ce endpoint remplace /confirmer/{id} : envoyer {"statut_surveillance": "CONFIRME"}
      - Ce endpoint remplace /marquer-presence/{id} : envoyer {"presence": true/false}
      - updated_at est automatiquement mis à jour

    ERREURS :
      - 404 : surveillance non trouvée
    """
    service = SurvService(db)
    result  = service.update_surveillance(surveillance_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Surveillance non trouvée")
    from app.crud.crud_surv import _enrich_surveillance
    return _enrich_surveillance(db, result)


# ══════════════════════════════════════════════════════════════════════════════
# REMPLACEMENT D'UN ENSEIGNANT
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/{surveillance_id}/reassign")
def replace_surveillance_endpoint(surveillance_id: int, request: RemplacementRequest, db: Session = Depends(get_db)):
    """
    Remplace l'enseignant d'une surveillance par un autre.
    L'ancienne surveillance est supprimée et une nouvelle est créée.

    PATH :
      - surveillance_id (int) : ID de la surveillance à remplacer

    BODY (JSON) :
      - nouvel_enseignant_id (int) : ID du nouvel enseignant
      - motif               (str, optionnel) : raison du remplacement
                            ex: "Indisponibilité médicale", "Mission officielle"

    RÉPONSE :
      - ancienne_surveillance_id : ID de la surveillance supprimée
      - ancien_enseignant_id     : ID de l'ancien enseignant
      - motif                    : motif fourni
      - nouvelle_surveillance    : détail complet de la nouvelle surveillance créée
          (même structure que /full-details)

    NOTES :
      - Le motif est préfixé "Remplacement: " dans le champ motif_externe
      - La nouvelle surveillance hérite du groupe, salle, charge et mode
        de l'ancienne
      - L'opération est atomique : suppression + création dans la même transaction

    ERREURS :
      - 404 : surveillance non trouvée ou nouvel enseignant inexistant
      - 400 : erreur inattendue
    """
    service = SurvService(db)
    try:
        old, new = service.replace_surveillance(surveillance_id, request.nouvel_enseignant_id, request.motif)
        from app.crud.crud_surv import _enrich_surveillance, get_surveillance
        new_full = get_surveillance(db, new.id)
        return {
            "ancienne_surveillance_id": old.id,
            "ancien_enseignant_id":     old.enseignant_id,
            "motif":                    request.motif,
            "nouvelle_surveillance":    _enrich_surveillance(db, new_full) if new_full else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# SUPPRIMER UNE SURVEILLANCE
# ══════════════════════════════════════════════════════════════════════════════

@router.delete("/{surveillance_id}")
def delete_surveillance_endpoint(surveillance_id: int, db: Session = Depends(get_db)):
    """
    Supprime une surveillance par son ID.

    PATH :
      - surveillance_id (int) : ID de la surveillance à supprimer

    RÉPONSE :
      - message : confirmation textuelle
      - id      : ID de la surveillance supprimée

    NOTES :
      - La suppression est irréversible
      - La charge de cet enseignant sera automatiquement recalculée
        lors des prochains appels aux endpoints de volume

    ERREURS :
      - 404 : surveillance non trouvée
    """
    service = SurvService(db)
    if not service.delete_surveillance(surveillance_id):
        raise HTTPException(status_code=404, detail="Surveillance non trouvée")
    return {"message": "Surveillance supprimée avec succès", "id": surveillance_id}


# ══════════════════════════════════════════════════════════════════════════════
# RÉINITIALISER UNE SESSION
# ══════════════════════════════════════════════════════════════════════════════

@router.delete("/session/{session_id}/reset")
def reset_session_surveillances(session_id: int, db: Session = Depends(get_db)):
    """
    Supprime TOUTES les surveillances d'une session entière.
    Action destructrice et irréversible — à utiliser avant une réaffectation complète.

    PATH :
      - session_id (int) : ID de la session à réinitialiser

    RÉPONSE :
      - session_id               : ID de la session concernée
      - surveillances_supprimees : nombre de surveillances supprimées
      - message                  : confirmation textuelle

    NOTES :
      - Supprime en cascade toutes les surveillances liées à toutes les
        planifications de la session
      - Les planifications elles-mêmes ne sont PAS supprimées
      - Après reset, la session est prête pour une nouvelle affectation automatique
        via /affecter-session
    """
    from app.crud.crud_surv import delete_surveillances_for_session
    count = delete_surveillances_for_session(db, session_id)
    return {"session_id": session_id, "surveillances_supprimees": count, "message": f"{count} surveillance(s) supprimée(s)"}


# ══════════════════════════════════════════════════════════════════════════════
# RAPPORT COMPLET D'UNE SESSION
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/session/{session_id}/rapport")
def get_rapport_session(session_id: int, departement_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """
    Génère un rapport complet d'une session d'examens.

    PATH :
      - session_id (int) : ID de la session

    QUERY PARAMS (optionnel) :
      - departement_id : filtrer le rapport par département

    RÉPONSE :
      - session : infos de la session (id, type, annee, dates, statut)
      - statistiques :
          • total_planifications : nombre de planifications VALIDEES
          • completes            : planifications avec tous les surveillants
          • partielles           : planifications avec certains surveillants seulement
          • non_affectees        : planifications sans aucun surveillant
          • total_surveillances  : total de surveillances créées
          • total_presences      : nombre de présences confirmées
          • total_externes       : nombre d'enseignants externes
      - planifications : liste détaillée de chaque planification avec :
          • matière, section, département, créneau
          • nb_surveillants_requis, nb_surveillants_trouves, complet
          • surveillants : liste avec enseignant, groupe, salle, charge,
                           mode, statut, présence, est_externe
      - en_conflit : sous-liste des planifications incomplètes avec "manquants"
      - classement_enseignants : enseignants triés par charge décroissante avec :
          • nom, grade, département
          • charge_totale, nb_surveillances, nb_presences
          • volume_horaire, taux_utilisation
      - date_generation : horodatage de génération du rapport

    ERREURS :
      - 404 : session non trouvée
    """
    from app.models.salle_session import Session as SessionModel, Creneau
    from app.models.planification import Planification
    from app.models.surveillance import Surveillance
    from app.models.enseignant import ChargeHoraire
    from datetime import datetime

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    q = db.query(Planification).filter(Planification.session_id == session_id, Planification.statut == "VALIDEE")
    if departement_id:
        q = q.filter(Planification.departement_id == departement_id)
    planifications = q.all()

    planif_detail = []
    en_conflit    = []

    for planif in planifications:
        survs     = planif.surveillances
        cren      = planif.creneau
        sm        = planif.section_matiere
        mat       = sm.matiere  if sm  else None
        sec       = sm.section  if sm  else None
        dept_exam = planif.departement

        surveillants_detail = []
        for s in survs:
            if s.statut_surveillance not in ("AFFECTE", "CONFIRME"):
                continue
            grp   = s.groupe
            salle = s.salle
            ens   = s.enseignant
            surveillants_detail.append({
                "surveillance_id": s.id,
                "enseignant": {
                    "id": ens.id if ens else None,
                    "nom_complet": f"{ens.prenom} {ens.nom}" if ens else None,
                    "grade": ens.grade if ens else None,
                    "email": ens.email if ens else None,
                    "departement": {"id": ens.departement.id if ens and ens.departement else None, "nom": ens.departement.nom if ens and ens.departement else None, "code": ens.departement.code if ens and ens.departement else None},
                },
                "groupe":  {"id": grp.id if grp else None, "numero": grp.numero if grp else None, "effectif": grp.effectif if grp else None},
                "salle":   {"id": salle.id if salle else None, "code": salle.code if salle else None, "designation": salle.designation if salle else None, "batiment": salle.batiment if salle else None, "capacite": salle.capacite if salle else None},
                "charge_imputee": float(s.charge), "mode_affectation": s.mode_affectation,
                "statut": s.statut_surveillance, "presence": s.presence,
                "est_externe": s.est_externe, "motif_externe": s.motif_externe,
            })

        nb_trouves = len(surveillants_detail)
        data = {
            "planification_id": planif.id, "type_epreuve": planif.type_epreuve, "semestre": planif.semestre, "duree": planif.duree,
            "departement_examen": {"id": dept_exam.id if dept_exam else None, "nom": dept_exam.nom if dept_exam else None, "code": dept_exam.code if dept_exam else None},
            "matiere": {"id": mat.id if mat else None, "code": mat.code if mat else None, "intitule": mat.intitule if mat else None},
            "section": {"id": sec.id if sec else None, "nom": sec.nom if sec else None},
            "creneau": {"date": cren.date.isoformat() if cren else None, "heure_debut": str(cren.heure_debut) if cren else None, "heure_fin": str(cren.heure_fin) if cren else None, "libelle": cren.libelle if cren else None},
            "nb_surveillants_requis": planif.nb_surveillants_requis, "nb_surveillants_trouves": nb_trouves,
            "complet": nb_trouves >= planif.nb_surveillants_requis, "surveillants": surveillants_detail,
        }
        planif_detail.append(data)
        if nb_trouves < planif.nb_surveillants_requis:
            en_conflit.append({**data, "manquants": planif.nb_surveillants_requis - nb_trouves})

    all_survs = db.query(Surveillance).select_from(Surveillance).join(Planification, Surveillance.planification_id == Planification.id).filter(Planification.session_id == session_id).all()
    ens_charges: dict = {}
    for s in all_survs:
        eid = s.enseignant_id
        if eid not in ens_charges:
            ch  = db.query(ChargeHoraire).filter(ChargeHoraire.enseignant_id == eid, ChargeHoraire.annee_univ == session.annee_universitaire).first()
            ens = s.enseignant
            ens_charges[eid] = {"enseignant_id": eid, "nom_complet": f"{ens.prenom} {ens.nom}" if ens else "—", "grade": ens.grade if ens else "—", "departement": {"id": ens.departement.id if ens and ens.departement else None, "nom": ens.departement.nom if ens and ens.departement else None, "code": ens.departement.code if ens and ens.departement else None}, "charge_totale": 0.0, "nb_surveillances": 0, "nb_presences": 0, "volume_horaire": float(ch.volume_horaire) if ch else 0.0}
        ens_charges[eid]["charge_totale"]    += float(s.charge)
        ens_charges[eid]["nb_surveillances"] += 1
        if s.presence: ens_charges[eid]["nb_presences"] += 1

    classement = sorted([{**d, "taux_utilisation": round(d["charge_totale"] / d["volume_horaire"] * 100 if d["volume_horaire"] > 0 else 0, 2)} for d in ens_charges.values()], key=lambda x: x["charge_totale"], reverse=True)
    total_ok      = sum(1 for p in planif_detail if p["complet"])
    total_partiel = sum(1 for p in planif_detail if 0 < p["nb_surveillants_trouves"] < p["nb_surveillants_requis"])
    total_zero    = sum(1 for p in planif_detail if p["nb_surveillants_trouves"] == 0)

    return {"session": {"id": session.id, "type_session": session.type_session, "annee_univ": session.annee_universitaire, "date_debut": session.date_debut.isoformat(), "date_fin": session.date_fin.isoformat(), "statut": session.statut}, "statistiques": {"total_planifications": len(planifications), "completes": total_ok, "partielles": total_partiel, "non_affectees": total_zero, "total_surveillances": len(all_survs), "total_presences": sum(1 for s in all_survs if s.presence), "total_externes": sum(1 for s in all_survs if s.est_externe)}, "planifications": planif_detail, "en_conflit": en_conflit, "classement_enseignants": classement, "date_generation": datetime.now().isoformat()}


# ══════════════════════════════════════════════════════════════════════════════
# CONFLITS D'UNE SESSION
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/session/{session_id}/conflits")
def get_session_conflits(
    session_id:   int,
    semestre:     Optional[int] = Query(None),
    type_epreuve: Optional[str] = Query(None),
    section_nom:  Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Détecte et retourne les conflits de surveillance d'une session.
    Un conflit = un groupe/salle avec moins de surveillants que requis.

    PATH :
      - session_id (int) : ID de la session

    QUERY PARAMS (tous optionnels) :
      - semestre     : filtrer par semestre (1 ou 2)
      - type_epreuve : "DS" ou "EXAMEN_FINAL"
      - section_nom  : filtrer par nom de section ex: "IGL3"

    RÉPONSE :
      - session_id     : ID de la session
      - total_conflits : nombre de conflits détectés
      - conflits       : liste de conflits, chacun contenant :
          • planification_id, type_epreuve, semestre
          • departement_examen (id, nom, code)
          • matiere (id, code, intitule)
          • section (id, nom)
          • creneau (date, heure_debut, heure_fin, libelle)
          • groupe (id, numero, effectif)
          • salle (id, code, designation, batiment, capacite)
          • surveillants_requis  : nombre attendu
          • surveillants_trouves : nombre actuellement affecté
          • manquants            : différence (toujours > 0 dans cette liste)
          • statut_resolution    : toujours "NON_RESOLU" (prévu pour futur usage)

    NOTES :
      - Seules les planifications avec statut "VALIDEE" sont analysées
      - Le comptage se fait par couple (groupe_id, salle_id) spécifique
        pour être précis en cas de plusieurs groupes par planification
    """
    from app.models.planification import Planification, PlanifSalle
    from app.models.departement_niveau_section import Section, Niveau, Groupe
    from app.models.salle_session import Salle
    from app.models.matiere import SectionMatiere

    q = db.query(Planification).filter(
        Planification.session_id == session_id,
        Planification.statut     == "VALIDEE",
    )
    if semestre:     q = q.filter(Planification.semestre == semestre)
    if type_epreuve: q = q.filter(Planification.type_epreuve == type_epreuve)
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
                salle = db.query(Salle).filter(Salle.code == ps.salle_id).first()  if ps.salle_id  else None

                conflits.append({
                    "planification_id":   planif.id,
                    "type_epreuve":       planif.type_epreuve,
                    "semestre":           planif.semestre,
                    "departement_examen": {
                        "id":   dept_exam.id   if dept_exam else None,
                        "nom":  dept_exam.nom  if dept_exam else None,
                        "code": dept_exam.code if dept_exam else None,
                    },
                    "matiere": {
                        "id":      mat.id      if mat else None,
                        "code":    mat.code    if mat else None,
                        "intitule": mat.intitule if mat else None,
                    },
                    "section": {
                        "id":  sec.id  if sec else None,
                        "nom": sec.nom if sec else None,
                    },
                    "creneau": {
                        "date":        cren.date.isoformat()  if cren else None,
                        "heure_debut": str(cren.heure_debut)  if cren else None,
                        "heure_fin":   str(cren.heure_fin)    if cren else None,
                        "libelle":     cren.libelle           if cren else None,
                    },
                    "groupe": {
                        "id":      grp.id      if grp else None,
                        "numero":  grp.numero  if grp else None,
                        "effectif": grp.effectif if grp else None,
                    },
                    "salle": {
                        "id":          salle.id          if salle else None,
                        "code":        salle.code        if salle else None,
                        "designation": salle.designation if salle else None,
                        "batiment":    salle.batiment    if salle else None,
                        "capacite":    salle.capacite    if salle else None,
                    },
                    "surveillants_requis":  planif.nb_surveillants_requis,
                    "surveillants_trouves": nb,
                    "manquants":            planif.nb_surveillants_requis - nb,
                    "statut_resolution":    "NON_RESOLU",
                })

    return {
        "session_id":     session_id,
        "total_conflits": len(conflits),
        "conflits":       conflits,
    }


# ══════════════════════════════════════════════════════════════════════════════
# STATISTIQUES GLOBALES
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/statistiques", response_model=StatistiquesResponse)
def get_statistiques(annee_univ: str = Query(...), db: Session = Depends(get_db)):
    """
    Retourne les statistiques globales de surveillance pour une année universitaire.

    QUERY PARAMS :
      - annee_univ (str, obligatoire) : année universitaire ex: "2025/2026"

    RÉPONSE :
      - annee_universitaire : année concernée
      - total_surveillances : nombre total de surveillances créées
      - total_heures        : somme des charges (heures) imputées
      - unique_enseignants  : nombre d'enseignants distincts impliqués
      - count_externes      : nombre de surveillances par enseignants externes
      - taux_externe        : pourcentage de surveillances externes
      - taux_remplissage    : pourcentage de postes pourvus vs postes requis
                              (total_surveillances / total_requis * 100)

    NOTES :
      - Couvre toutes les sessions de l'année universitaire spécifiée
      - taux_remplissage = 100% signifie que toutes les planifications
        ont le nombre exact de surveillants requis
    """
    from app.models.surveillance import Surveillance
    from app.models.planification import Planification
    from app.models.salle_session import Session as SessionModel
    from sqlalchemy import func
    stats = db.query(func.count(Surveillance.id).label("total_surveillances"), func.sum(Surveillance.charge).label("total_heures"), func.count(func.distinct(Surveillance.enseignant_id)).label("unique_enseignants")).select_from(Surveillance).join(Planification, Surveillance.planification_id == Planification.id).join(SessionModel, Planification.session_id == SessionModel.id).filter(SessionModel.annee_universitaire == annee_univ).first()
    count_externes = db.query(func.count(Surveillance.id)).select_from(Surveillance).join(Planification, Surveillance.planification_id == Planification.id).join(SessionModel, Planification.session_id == SessionModel.id).filter(SessionModel.annee_universitaire == annee_univ, Surveillance.est_externe == True).scalar() or 0
    total_requis = db.query(func.sum(Planification.nb_surveillants_requis)).select_from(Planification).join(SessionModel, Planification.session_id == SessionModel.id).filter(SessionModel.annee_universitaire == annee_univ, Planification.statut == "VALIDEE").scalar() or 0
    total = stats.total_surveillances or 0
    return StatistiquesResponse(annee_universitaire=annee_univ, total_surveillances=total, total_heures=float(stats.total_heures or 0), unique_enseignants=stats.unique_enseignants or 0, count_externes=count_externes, taux_externe=(count_externes / total * 100) if total > 0 else 0, taux_remplissage=round((total / total_requis * 100) if total_requis > 0 else 0, 2))


# ══════════════════════════════════════════════════════════════════════════════
# INDISPONIBILITÉS D'UN ENSEIGNANT
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/enseignant/{enseignant_id}/disponibilites", response_model=GetDisponibilitesResponse)
def get_enseignant_disponibilites(enseignant_id: int, date_debut: str = Query(...), date_fin: str = Query(...), db: Session = Depends(get_db)):
    """
    Retourne les indisponibilités déclarées d'un enseignant sur une période donnée.

    PATH :
      - enseignant_id (int) : ID de l'enseignant

    QUERY PARAMS (obligatoires) :
      - date_debut (str) : date de début au format "YYYY-MM-DD" ex: "2026-01-07"
      - date_fin   (str) : date de fin   au format "YYYY-MM-DD" ex: "2026-01-15"

    RÉPONSE :
      - enseignant_id  : ID de l'enseignant
      - date_debut     : date de début de la période
      - date_fin       : date de fin de la période
      - disponibilites : liste des indisponibilités déclarées, chacune avec :
          • date        : date de l'indisponibilité
          • heure_debut : heure de début (format "HH:MM:SS")
          • heure_fin   : heure de fin   (format "HH:MM:SS")
          • type        : type parmi DISPONIBLE, INDISPONIBLE, COURS_PREVU,
                          MISSION, CONGE
          • motif       : description libre (peut être null)

    NOTES :
      - Retourne une liste vide si aucune indisponibilité n'est déclarée
      - Les dates sont inclusives (date_debut <= date <= date_fin)
      - Utile pour le frontend pour afficher le calendrier d'un enseignant
        avant de l'affecter manuellement

    ERREURS :
      - 400 : format de date invalide (doit être YYYY-MM-DD)
    """
    from app.models.disponibilite import DisponibiliteEnseignant
    from datetime import datetime as dt
    try:
        start = dt.strptime(date_debut, "%Y-%m-%d").date()
        end   = dt.strptime(date_fin,   "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")
    dispos = db.query(DisponibiliteEnseignant).filter(DisponibiliteEnseignant.enseignant_id == enseignant_id, DisponibiliteEnseignant.date >= start, DisponibiliteEnseignant.date <= end).all()
    return GetDisponibilitesResponse(enseignant_id=enseignant_id, date_debut=date_debut, date_fin=date_fin, disponibilites=[DisponibiliteItem(date=d.date.isoformat(), heure_debut=str(d.heure_debut), heure_fin=str(d.heure_fin), type=d.type_dispo, motif=d.motif) for d in dispos])


# ══════════════════════════════════════════════════════════════════════════════
# CRÉER UNE DISPONIBILITÉ
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/disponibilites", response_model=DisponibiliteEnseignantOut)
def create_disponibilite(payload: DisponibiliteEnseignantCreate, db: Session = Depends(get_db)):
    """
    Crée une indisponibilité (ou disponibilité) pour un enseignant.

    BODY :
      - enseignant_id (int)
      - date (date)
      - heure_debut (time)
      - heure_fin (time)
      - type_dispo (str)
      - motif (str, optionnel)
      - confirme (bool, default True)
    """
    from app.models.enseignant import Enseignant
    from app.models.disponibilite import DisponibiliteEnseignant

    enseignant = db.query(Enseignant).filter(Enseignant.id == payload.enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")

    record = DisponibiliteEnseignant(
        enseignant_id=payload.enseignant_id,
        date=payload.date,
        heure_debut=payload.heure_debut,
        heure_fin=payload.heure_fin,
        type_dispo=payload.type_dispo,
        motif=payload.motif,
        confirme=payload.confirme,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record