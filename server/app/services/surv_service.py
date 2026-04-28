"""
services/surv_service.py
"""

from typing import Optional
from sqlalchemy.orm import Session as SQLSession

from app.algorithms.surv_auto import AutomaticAffectationAlgorithm
from app.crud.crud_surv import (
    create_surveillance,
    create_surveillances_batch,
    delete_surveillance,
    delete_surveillance_by_id,
    get_surveillance,
    get_surveillances_for_enseignant,
    get_surveillances_for_planification,
    list_surveillances,
    replace_surveillance,
    update_surveillance,
    get_enseignant_charge_for_year,
    count_surveillances_for_enseignant,
)
from app.models.surveillance import Surveillance
from app.models.planification import Planification
from app.models.enseignant import Enseignant, ChargeHoraire
from app.models.disponibilite import DisponibiliteEnseignant
from app.models.salle_session import Session, Creneau
from app.schemas.surveillance_schema import (
    SurveillanceCreate,
    SurveillanceUpdate,
    ManualAssignmentRequest,
    ManualAssignmentBatchRequest,
    EnseignantDisponible,
)


class SurvService:

    def __init__(self, db: SQLSession):
        self.db        = db
        self.algorithm = AutomaticAffectationAlgorithm(db)

    # ── Listing ──────────────────────────────────────────────────────────────

    def get_all_surveillances(
        self,
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
    ):
        return list_surveillances(
            self.db,
            planification_id=planification_id,
            enseignant_id=enseignant_id,
            session_id=session_id,
            groupe_id=groupe_id,
            salle_id=salle_id,
            est_externe=est_externe,
            statut=statut,
            skip=skip,
            limit=limit,
        )

    def get_surveillance_by_id(self, surveillance_id: int):
        return get_surveillance(self.db, surveillance_id)

    def get_surveillances_for_planification(self, planification_id: int):
        return get_surveillances_for_planification(self.db, planification_id)

    def get_surveillances_for_enseignant(
        self, enseignant_id: int, annee_universitaire: str | None = None
    ):
        return get_surveillances_for_enseignant(
            self.db, enseignant_id, annee_universitaire
        )

    # ── CRUD basique ─────────────────────────────────────────────────────────

    def create_surveillance(self, payload: SurveillanceCreate):
        return create_surveillance(self.db, payload)

    def update_surveillance(self, surveillance_id: int, payload: SurveillanceUpdate):
        s = get_surveillance(self.db, surveillance_id)
        return update_surveillance(self.db, s, payload) if s else None

    def delete_surveillance(self, surveillance_id: int) -> bool:
        return delete_surveillance_by_id(self.db, surveillance_id)

    def replace_surveillance(
        self, surveillance_id: int, new_enseignant_id: int, motif: str
    ):
        old = get_surveillance(self.db, surveillance_id)
        if not old:
            raise ValueError("Surveillance non trouvée")
        return replace_surveillance(self.db, old, new_enseignant_id, motif)

    # ── Affectation automatique ───────────────────────────────────────────────

    def affecter_session_automatique(
        self,
        session_id:   int,
        section_nom:  Optional[str] = None,
        periode:      Optional[str] = None,
        type_epreuve: Optional[str] = None,
    ):
        """
        Lance l'algorithme v3 avec filtres optionnels.

        Args:
            session_id:   ID de la session (obligatoire)
            section_nom:  Ex: "IGL3" ou "INF/IOT"
            periode:      Ex: "2025/2026-S1" ou "2025/2026-S2"
            type_epreuve: "DS" ou "EXAMEN_FINAL"
        """
        return self.algorithm.affecter_session(
            session_id=session_id,
            section_nom=section_nom,
            periode=periode,
            type_epreuve=type_epreuve,
        )

    # ── Affectation manuelle — planif unique ──────────────────────────────────

    def affecter_planification_manuellement(self, request: ManualAssignmentRequest):
        from app.crud.crud_surv import _enrich_surveillance

        planif = self.db.query(Planification).filter(
            Planification.id         == request.planification_id,
            Planification.session_id == request.session_id,
        ).first()
        if not planif:
            raise ValueError(
                f"Planification {request.planification_id} non trouvée "
                f"dans la session {request.session_id}"
            )

        crees   = []
        erreurs = []

        for ens_id in request.enseignant_ids:
            # ── Seule contrainte active : C4 non-simultanéité ──
            if self._check_simultaneite(ens_id, planif):
                erreurs.append({"enseignant_id": ens_id, "raison": "DEJA_AFFECTE"})
                continue

            ens         = self.db.query(Enseignant).filter(Enseignant.id == ens_id).first()
            est_externe = ens.departement_id != planif.departement_id
            motif       = request.motifs_externes.get(ens_id) if est_externe else None

            payload = SurveillanceCreate(
                planification_id=request.planification_id,
                enseignant_id=ens_id,
                groupe_id=request.groupe_id,
                salle_id=request.salle_id,
                charge=float(planif.duree / 60),
                mode_affectation="MANUELLE",
                est_externe=est_externe,
                motif_externe=motif,
            )
            crees.append(create_surveillance(self.db, payload))

        if erreurs:
            for s in crees:
                delete_surveillance(self.db, s)
            raise ValueError(f"Validation échouée: {erreurs}")

        # ── Récupérer annee_univ depuis la session ──
        sess       = planif.session
        annee_univ = sess.annee_universitaire if sess else None

        # ── Enrichir chaque surveillance créée ──
        surveillances_detail = [
            _enrich_surveillance(self.db, s, annee_univ)
            for s in crees
        ]

        # ── Vérifier si le nombre de surveillants est suffisant ──
        nb_inseres  = len(crees)
        nb_requis   = planif.nb_surveillants_requis
        manquants   = nb_requis - nb_inseres

        if manquants > 0:
            statut = "INCOMPLET"
        else:
            statut = "CONFLIT_RESOLU"

        return {
            "planification_id":     request.planification_id,
            "statut":               statut,
            "surveillants_requis":  nb_requis,
            "surveillants_inseres": nb_inseres,
            "manquants":            manquants,
            "surveillances":        surveillances_detail,
        }

    # ── Affectation manuelle — batch ─────────────────────────────────────────

    def affecter_session_manuellement(self, request: ManualAssignmentBatchRequest):
        from app.crud.crud_surv import _enrich_surveillance

        session = self.db.query(Session).filter(
            Session.id == request.session_id
        ).first()
        if not session:
            raise ValueError(f"Session {request.session_id} non trouvée")

        crees      = []
        erreurs    = []
        incomplets = []

        for item in request.affectations:
            planif = self.db.query(Planification).filter(
                Planification.id         == item.planification_id,
                Planification.session_id == request.session_id,
            ).first()
            if not planif:
                incomplets.append(item.planification_id)
                erreurs.append({"planification_id": item.planification_id, "erreur": "Non trouvée"})
                continue

            if len(item.enseignant_ids) < planif.nb_surveillants_requis:
                incomplets.append(item.planification_id)

            for ens_id in item.enseignant_ids:
                # ── Seule contrainte active : C4 non-simultanéité ──
                if self._check_simultaneite(ens_id, planif):
                    erreurs.append({
                        "planification_id": item.planification_id,
                        "enseignant_id":    ens_id,
                        "raison":           "DEJA_AFFECTE",
                    })
                    continue

                ens         = self.db.query(Enseignant).filter(Enseignant.id == ens_id).first()
                est_externe = ens.departement_id != planif.departement_id
                motif       = request.motifs_externes.get(ens_id) if est_externe else None

                crees.append(SurveillanceCreate(
                    planification_id=item.planification_id,
                    enseignant_id=ens_id,
                    groupe_id=item.groupe_id,
                    salle_id=item.salle_id,
                    charge=float(planif.duree / 60),
                    mode_affectation="MANUELLE",
                    est_externe=est_externe,
                    motif_externe=motif,
                ))

        if incomplets:
            return {
                "session_id": request.session_id,
                "statut":     "AVERTISSEMENT",
                "message":    "Certaines planifications sont incomplètes",
                "planifications_non_affectees": incomplets,
            }
        if erreurs:
            raise ValueError(f"Validation échouée: {erreurs}")

        surveillances_inserees = create_surveillances_batch(self.db, crees)

        # ── Enrichir chaque surveillance créée ──
        annee_univ = session.annee_universitaire
        surveillances_detail = [
            _enrich_surveillance(self.db, s, annee_univ)
            for s in surveillances_inserees
        ]

        return {
            "session_id":                   request.session_id,
            "statut":                       "SUCCES",
            "total_surveillances_inserees": len(surveillances_inserees),
            "surveillances":                surveillances_detail,
        }

    # ── Helpers contraintes ──────────────────────────────────────────────────

    def _check_disponibilite(self, enseignant_id: int, planif: Planification) -> bool:
        creneau = planif.creneau
        if not creneau:
            creneau = self.db.query(Creneau).filter(
                Creneau.id == planif.creneau_id
            ).first()
        if not creneau:
            return False

        indispos = self.db.query(DisponibiliteEnseignant).filter(
            DisponibiliteEnseignant.enseignant_id == enseignant_id,
            DisponibiliteEnseignant.date          == creneau.date,
            DisponibiliteEnseignant.type_dispo.in_(
                ["INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]
            ),
        ).all()

        for i in indispos:
            if i.heure_debut < creneau.heure_fin and i.heure_fin > creneau.heure_debut:
                return False
        return True

    def _check_simultaneite(self, enseignant_id: int, planif: Planification) -> bool:
        creneau = planif.creneau
        if not creneau:
            creneau = self.db.query(Creneau).filter(
                Creneau.id == planif.creneau_id
            ).first()
        if not creneau:
            return False

        return bool(
            self.db.query(Surveillance)
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(Creneau,       Planification.creneau_id      == Creneau.id)
            .filter(
                Surveillance.enseignant_id == enseignant_id,
                Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
                Creneau.date        == creneau.date,
                Creneau.heure_debut == creneau.heure_debut,
                Surveillance.planification_id != planif.id,
            )
            .first()
        )

    # ── Analytics ────────────────────────────────────────────────────────────

    def get_volume_restant_enseignant(
        self, enseignant_id: int, annee_universitaire: str
    ) -> dict:
        charge = self.db.query(ChargeHoraire).filter(
            ChargeHoraire.enseignant_id == enseignant_id,
            ChargeHoraire.annee_univ    == annee_universitaire,
        ).first()
        volume_horaire  = float(charge.volume_horaire) if charge else 0.0
        volume_consomme = get_enseignant_charge_for_year(
            self.db, enseignant_id, annee_universitaire
        )
        nb = count_surveillances_for_enseignant(
            self.db, enseignant_id, annee_universitaire
        )
        return {
            "enseignant_id":    enseignant_id,
            "volume_horaire":   volume_horaire,
            "volume_consomme":  volume_consomme,
            "volume_restant":   round(volume_horaire - volume_consomme, 2),
            "nb_surveillances": nb,
        }

    def get_enseignants_disponibles_pour_planification(
    self, planif_id: int
    ) -> dict:
        from app.models.disponibilite import DisponibiliteEnseignant
        from app.schemas.surveillance_schema import (
            EnseignantDisponibleV2,
            AvertissementIndisponibilite,
            DepartementDisponiblesOut,
            EnseignantsDisponiblesResponse,
        )

        planif = self.db.query(Planification).filter(
            Planification.id == planif_id
        ).first()
        if not planif:
            return {}

        session    = planif.session
        annee_univ = session.annee_universitaire if session else ""
        creneau    = planif.creneau
        if not creneau:
            creneau = self.db.query(Creneau).filter(
                Creneau.id == planif.creneau_id
            ).first()

        date_planif = creneau.date if creneau else None

        enseignants = self.db.query(Enseignant).all()

        # ── Grouper par département
        dept_map: dict[int | None, list[EnseignantDisponibleV2]] = {}

        for ens in enseignants:
            # ── Contrainte stricte : non-simultanéité
            if self._check_simultaneite(ens.id, planif):
                continue

            # ── Contrainte souple : indisponibilité le même jour
            avertissements = []
            if date_planif:
                indispos = self.db.query(DisponibiliteEnseignant).filter(
                    DisponibiliteEnseignant.enseignant_id == ens.id,
                    DisponibiliteEnseignant.date          == date_planif,
                ).all()
                for i in indispos:
                    avertissements.append(AvertissementIndisponibilite(
                        date=str(i.date),
                        heure_debut=str(i.heure_debut),
                        heure_fin=str(i.heure_fin),
                        type_dispo=i.type_dispo,
                        motif=i.motif,
                    ))

            vol  = self.get_volume_restant_enseignant(ens.id, annee_univ)
            dept = ens.departement
            dept_id = dept.id if dept else None

            ens_out = EnseignantDisponibleV2(
                enseignant_id=ens.id,
                nom=ens.nom,
                prenom=ens.prenom,
                grade=ens.grade,
                email=ens.email,
                telephone=ens.telephone,
                volume_horaire=vol["volume_horaire"],
                volume_consomme=vol["volume_consomme"],
                volume_restant=vol["volume_restant"],
                nb_surveillances=vol["nb_surveillances"],
                a_avertissement=len(avertissements) > 0,
                avertissements=avertissements,
            )

            if dept_id not in dept_map:
                dept_map[dept_id] = {
                    "info": dept,
                    "enseignants": [],
                }
            dept_map[dept_id]["enseignants"].append(ens_out)

        # ── Construire la réponse par département
        departements = []
        total_disponibles = 0
        total_avec_avertissement = 0

        for dept_id, data in dept_map.items():
            dept     = data["info"]
            ens_list = sorted(
                data["enseignants"],
                key=lambda x: x.volume_restant,
                reverse=True,
            )
            departements.append(DepartementDisponiblesOut(
                departement_id=dept.id     if dept else None,
                departement_nom=dept.nom   if dept else None,
                departement_code=dept.code if dept else None,
                enseignants=ens_list,
                total=len(ens_list),
            ))
            total_disponibles        += len(ens_list)
            total_avec_avertissement += sum(1 for e in ens_list if e.a_avertissement)

        # ── Trier les départements par nom
        departements.sort(key=lambda x: x.departement_nom or "")

        return EnseignantsDisponiblesResponse(
            planification_id=planif_id,
            date_planification=str(date_planif) if date_planif else "",
            total_disponibles=total_disponibles,
            total_avec_avertissement=total_avec_avertissement,
            departements=departements,
        )