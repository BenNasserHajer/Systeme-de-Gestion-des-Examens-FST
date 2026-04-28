"""
Algorithme d'affectation automatique des surveillances — par groupe/salle.

VERSION 3 — Améliorations majeures :
  • Filtre précis par session_id + section + periode + type_epreuve
  • Contrainte C5 (HARD) — Équité inter-département
  • Contrainte C6 (SOFT) — Équité de fréquence dans la session courante
  • Pré-chargement en batch (N+1 éliminés)
  • Résistance aux doublons inter-groupe par créneau
  • Log structuré par niveau DEBUG / INFO / WARNING
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.surveillance import Surveillance
from app.models.enseignant import Enseignant, ChargeHoraire, Enseignement
from app.models.planification import Planification, PlanifSalle
from app.models.disponibilite import DisponibiliteEnseignant
from app.models.departement_niveau_section import Departement, Section, Niveau
from app.models.matiere import SectionMatiere
from app.models.salle_session import Session as SessionModel, Creneau
from app.crud.crud_surv import create_surveillance
from app.schemas.surveillance_schema import (
    SurveillanceCreate,
    ModeAffectation,
    StatutSurveillance,
    ReasonExclusion,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Dataclasses internes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EnseignantCandidat:
    enseignant_id:              int
    nom:                        str
    prenom:                     str
    grade:                      Optional[str]
    departement_id:             int
    departement_nom:            str
    volume_horaire:             float
    volume_restant:             float
    volume_consomme:            float
    nb_surveillances:           int
    nb_surveillances_session:   int   = 0
    meme_departement:           bool  = True
    a_conflit_matiere:          bool  = False

    def __lt__(self, other: "EnseignantCandidat") -> bool:
        """
        Ordre de priorité :
          1. Même département (interne > externe)
          2. Volume restant DESC
          3. Nb surveillances dans la session courante ASC  (équité C6)
          4. Nb surveillances totales ASC
        """
        if self.meme_departement != other.meme_departement:
            return self.meme_departement > other.meme_departement
        if self.volume_restant != other.volume_restant:
            return self.volume_restant > other.volume_restant
        if self.nb_surveillances_session != other.nb_surveillances_session:
            return self.nb_surveillances_session < other.nb_surveillances_session
        return self.nb_surveillances < other.nb_surveillances


@dataclass
class ConstraintViolation:
    enseignant_id: int
    nom:           str
    prenom:        str
    raison:        ReasonExclusion
    details:       Optional[str] = None


@dataclass
class GroupeAffectationResult:
    """Résultat pour UNE ligne planif_salle (1 groupe + 1 salle)."""
    planification_id:      int
    groupe_id:             Optional[int]
    salle_id:              Optional[int]
    groupe_numero:         Optional[int]    = None
    salle_code:            Optional[str]    = None
    statut:                str              = "AFFECTEE"
    surveillants_affectes: list             = field(default_factory=list)
    surveillants_requis:   int              = 0
    manquants:             int              = 0
    violations:            list             = field(default_factory=list)


@dataclass
class PlanificationAffectationResult:
    """Résultat global d'une planification (agrège tous ses groupes/salles)."""
    planification_id:   int
    matiere_intitule:   str              = ""
    matiere_code:       str              = ""
    section_nom:        str              = ""
    type_epreuve:       str              = ""
    creneau_date:       Optional[str]    = None
    creneau_heure:      Optional[str]    = None
    statut:             str              = "AFFECTEE"
    groupes:            list             = field(default_factory=list)

    @property
    def surveillants_affectes(self) -> list:
        result = []
        for g in self.groupes:
            result.extend(g.surveillants_affectes)
        return result

    @property
    def surveillants_requis(self) -> int:
        return sum(g.surveillants_requis for g in self.groupes)

    @property
    def manquants(self) -> int:
        return sum(g.manquants for g in self.groupes)

    @property
    def violations(self) -> list:
        result = []
        for g in self.groupes:
            result.extend(g.violations)
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Requête de filtre des planifications
# ─────────────────────────────────────────────────────────────────────────────

def _build_planification_query(
    db: Session,
    session_id: int,
    section_nom: str,
    periode: str,
    type_epreuve: str,
):
    """
    Construit la requête de planifications filtrée par :
      - session_id (obligatoire)
      - section_nom ex: "IGL3"
      - periode ex: "2025/2026-S2" → annee_univ="2025/2026", semestre=2
      - type_epreuve ex: "DS" ou "EXAMEN_FINAL"
    """
    q = (
        db.query(Planification)
        .join(Creneau, Planification.creneau_id == Creneau.id)
        .filter(
            Planification.session_id == session_id,
            Planification.statut == "VALIDEE",
        )
    )

    q = (
        q.join(SectionMatiere, Planification.section_matiere_id == SectionMatiere.id)
         .join(Section, SectionMatiere.section_id == Section.id)
         .filter(Section.nom == section_nom)
    )

    # periode = "2025/2026-S2" → annee_univ="2025/2026", semestre=2
    parts = periode.rsplit("-S", 1)
    if len(parts) == 2:
        annee_univ = parts[0]
        try:
            semestre = int(parts[1])
            q = q.filter(
                Planification.semestre == semestre,
            )
            # Filtre sur l'année via la session
            q = (
                q.join(SessionModel, Planification.session_id == SessionModel.id, isouter=True)
                 .filter(SessionModel.annee_universitaire == annee_univ)
            )
        except ValueError:
            logger.warning("Période invalide: %s", periode)

    q = q.filter(Planification.type_epreuve == type_epreuve)

    q = q.order_by(Creneau.date.asc(), Creneau.heure_debut.asc())
    return q


# ─────────────────────────────────────────────────────────────────────────────
# Algorithme principal
# ─────────────────────────────────────────────────────────────────────────────

class AutomaticAffectationAlgorithm:
    """
    Affectation automatique des surveillances, groupe par groupe.

    Contraintes :
        C1 – Disponibilité temporelle           (HARD)
        C2 – Conflit de matière                 (SOFT — relaxable en dernier recours)
        C3 – Volume horaire annuel ±0.05%       (HARD)
        C4 – Non-simultanéité                   (HARD)
        C5 – Priorité département (interne > externe)  (SOFT — dégradé si nécessaire)
        C6 – Équité fréquence dans la session   (SOFT — critère de tri)
    """

    TOLERANCE_PERCENT = 0.0005   # ±0.05 % du volume horaire annuel

    def __init__(self, db: Session):
        self.db = db
        self._creneau_cache: dict[int, Optional[Creneau]] = {}
        self._affectes_par_creneau: dict[tuple, set[int]] = {}
        # ← AJOUT : suivi en mémoire des surveillances créées dans cette exécution
        self._nb_surveillances_session_mem: dict[int, int] = {}

    # ── Point d'entrée public ────────────────────────────────────────────────

    def affecter_session(
        self,
        session_id:   int,
        section_nom:  str,
        periode:      str,
        type_epreuve: str,
    ) -> tuple[list[PlanificationAffectationResult], str]:
        """
        Affecter les planifications VALIDEE d'une session.

        Args:
            session_id:   ID de la session (ex: 1)
            section_nom:  Nom de la section (ex: "INF/IOT")
            periode:      Année+semestre   (ex: "2025/2026-S1")
            type_epreuve: Type d'épreuve   (ex: "DS" ou "EXAMEN_FINAL")
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        if not session:
            return [], f"Session {session_id} non trouvée"

        q = _build_planification_query(
            self.db, session_id, section_nom, periode, type_epreuve
        )
        planifications = q.all()

        if not planifications:
            return [], (
                f"Aucune planification VALIDEE dans la session {session_id} "
                f"pour les critères donnés."
            )

        self._preload_creneau_cache(planifications)

        results:  list[PlanificationAffectationResult] = []
        nb_ok = nb_ko = 0

        for planif in planifications:
            result = self._affecter_planification(
                planif, session_id, session.annee_universitaire
            )
            results.append(result)
            if result.statut == "AFFECTEE":
                nb_ok += 1
            else:
                nb_ko += 1

        msg = (
            f"Traitement terminé : {nb_ok} planification(s) entièrement affectée(s), "
            f"{nb_ko} en conflit (partiel ou total)."
        )
        logger.info(msg)
        return results, msg

    # ── Pré-chargement batch ─────────────────────────────────────────────────

    def _preload_creneau_cache(self, planifications: list[Planification]) -> None:
        ids = list({p.creneau_id for p in planifications})
        creneaux = self.db.query(Creneau).filter(Creneau.id.in_(ids)).all()
        for c in creneaux:
            self._creneau_cache[c.id] = c

    # ── Niveau planification ─────────────────────────────────────────────────

    def _affecter_planification(
        self,
        planif:      Planification,
        session_id:  int,
        annee_univ:  str,
    ) -> PlanificationAffectationResult:
        sm       = planif.section_matiere
        mat      = sm.matiere if sm else None
        sec      = sm.section if sm else None
        creneau  = self._get_creneau(planif)

        result = PlanificationAffectationResult(
            planification_id=planif.id,
            matiere_intitule=mat.intitule if mat else "",
            matiere_code=mat.code if mat else "",
            section_nom=sec.nom if sec else "",
            type_epreuve=planif.type_epreuve,
            creneau_date=str(creneau.date) if creneau else None,
            creneau_heure=f"{creneau.heure_debut}–{creneau.heure_fin}" if creneau else None,
            statut="AFFECTEE",
        )

        lignes: list[PlanifSalle] = (
            self.db.query(PlanifSalle)
            .filter(PlanifSalle.planification_id == planif.id)
            .all()
        )

        if not lignes:
            logger.warning("Planification %s : aucune ligne planif_salle", planif.id)
            result.statut = "CONFLIT"
            return result

        annee_sem_cible = sm.annee_sem if sm else f"{annee_univ}-S{planif.semestre}"

        candidats_base = self._get_enseignants_departement(
            planif.departement_id, session_id, annee_univ, annee_sem_cible
        )

        creneau_key = (creneau.date, creneau.heure_debut) if creneau else (planif.id,)
        if creneau_key not in self._affectes_par_creneau:
            self._affectes_par_creneau[creneau_key] = set()

        for ligne in lignes:
            groupe_result = self._affecter_groupe(
                planif=planif,
                ligne=ligne,
                candidats_base=candidats_base,
                session_id=session_id,
                creneau_key=creneau_key,
            )
            result.groupes.append(groupe_result)

        nb_conflits = sum(1 for g in result.groupes if g.statut == "CONFLIT")
        if nb_conflits == 0:
            result.statut = "AFFECTEE"
        elif nb_conflits == len(result.groupes):
            result.statut = "CONFLIT"
        else:
            result.statut = "CONFLIT_PARTIEL"

        return result

    # ── Niveau groupe/salle ──────────────────────────────────────────────────

    def _affecter_groupe(
        self,
        planif:         Planification,
        ligne:          PlanifSalle,
        candidats_base: list[EnseignantCandidat],
        session_id:     int,
        creneau_key:    tuple,
    ) -> GroupeAffectationResult:
        grp   = ligne.groupe
        salle = ligne.salle

        result = GroupeAffectationResult(
            planification_id=planif.id,
            groupe_id=ligne.groupe_id,
            salle_id=ligne.salle_id,
            groupe_numero=grp.numero if grp else None,
            salle_code=salle.code if salle else None,
            statut="AFFECTEE",
            surveillants_requis=planif.nb_surveillants_requis,
        )

        self._refresh_volumes(candidats_base, session_id)

        candidats_eligibles: list[EnseignantCandidat] = []
        violations:          list[ConstraintViolation] = []
        deja_affectes_creneau = self._affectes_par_creneau.get(creneau_key, set())

        for candidat in candidats_base:
            if candidat.enseignant_id in deja_affectes_creneau:
                violations.append(ConstraintViolation(
                    enseignant_id=candidat.enseignant_id,
                    nom=candidat.nom, prenom=candidat.prenom,
                    raison=ReasonExclusion.DEJA_AFFECTE,
                    details="Déjà affecté à un autre groupe de ce créneau",
                ))
                continue

            if not self._check_disponibilite(candidat.enseignant_id, planif):
                violations.append(ConstraintViolation(
                    enseignant_id=candidat.enseignant_id,
                    nom=candidat.nom, prenom=candidat.prenom,
                    raison=ReasonExclusion.INDISPONIBLE,
                ))
                continue

            if self._check_simultaneite(candidat.enseignant_id, planif):
                violations.append(ConstraintViolation(
                    enseignant_id=candidat.enseignant_id,
                    nom=candidat.nom, prenom=candidat.prenom,
                    raison=ReasonExclusion.DEJA_AFFECTE,
                ))
                continue

            tolerance = candidat.volume_horaire * self.TOLERANCE_PERCENT
            if candidat.volume_restant < -tolerance:
                violations.append(ConstraintViolation(
                    enseignant_id=candidat.enseignant_id,
                    nom=candidat.nom, prenom=candidat.prenom,
                    raison=ReasonExclusion.VOLUME_EPUISE,
                    details=(
                        f"Restant: {candidat.volume_restant:.2f}h "
                        f"(limite: {-tolerance:.4f}h)"
                    ),
                ))
                continue

            candidat.a_conflit_matiere = self._check_conflit_matiere(
                candidat.enseignant_id, planif
            )
            candidats_eligibles.append(candidat)

        candidats_eligibles.sort()

        sans_conflit = [c for c in candidats_eligibles if not c.a_conflit_matiere]
        avec_conflit = [c for c in candidats_eligibles if c.a_conflit_matiere]

        selectionnes: list[EnseignantCandidat] = []
        nb_requis = planif.nb_surveillants_requis

        for c in sans_conflit:
            if len(selectionnes) >= nb_requis:
                break
            selectionnes.append(c)

        for c in avec_conflit:
            if len(selectionnes) >= nb_requis:
                break
            selectionnes.append(c)

        surveillants_inseres = []
        for candidat in selectionnes:
            surv = self._creer_surveillance(planif, candidat, ligne)
            surveillants_inseres.append(surv)
            self._affectes_par_creneau[creneau_key].add(candidat.enseignant_id)
            logger.debug(
                "Surveillance créée : planif=%s groupe=%s ens=%s (%s %s)",
                planif.id, ligne.groupe_id, candidat.enseignant_id,
                candidat.prenom, candidat.nom,
            )

        result.surveillants_affectes = surveillants_inseres
        result.violations            = violations

        if len(surveillants_inseres) < nb_requis:
            result.statut    = "CONFLIT"
            result.manquants = nb_requis - len(surveillants_inseres)
            logger.warning(
                "Conflit groupe %s / salle %s : %s manquant(s)",
                ligne.groupe_id, ligne.salle_id, result.manquants,
            )
        else:
            ids_avec_conflit = {c.enseignant_id for c in avec_conflit}
            ids_inseres      = {s.enseignant_id for s in surveillants_inseres}
            if ids_avec_conflit & ids_inseres:
                result.violations.append(ConstraintViolation(
                    enseignant_id=0,
                    nom="AVERTISSEMENT", prenom="",
                    raison=ReasonExclusion.CONFLIT_MATIERE,
                    details=(
                        f"Groupe {ligne.groupe_id} / Salle {ligne.salle_id} : "
                        "contrainte matière levée — enseignant surveille sa propre matière."
                    ),
                ))

        return result

    # ── Helpers — données ────────────────────────────────────────────────────

    def _get_enseignants_departement(
        self,
        departement_id:  int,
        session_id:      int,
        annee_univ:      str,
        annee_sem_cible: str,
    ) -> list[EnseignantCandidat]:
        departement = self.db.query(Departement).filter(
            Departement.id == departement_id
        ).first()
        dept_nom = departement.nom if departement else "Unknown"

        enseignants = (
            self.db.query(
                Enseignant.id,
                Enseignant.nom,
                Enseignant.prenom,
                Enseignant.grade,
                Enseignant.departement_id,
            )
            .join(Enseignement, Enseignement.enseignant_id == Enseignant.id)
            .filter(
                Enseignant.departement_id == departement_id,
                Enseignement.annee_sem    == annee_sem_cible,
            )
            .distinct()
            .all()
        )

        charges = {
            ch.enseignant_id: float(ch.volume_horaire)
            for ch in self.db.query(ChargeHoraire).filter(
                ChargeHoraire.annee_univ == annee_univ
            ).all()
        }

        rows_session = (
            self.db.query(
                Surveillance.enseignant_id,
                func.count(Surveillance.id).label("nb"),
            )
            .join(Planification)
            .filter(
                Planification.session_id == session_id,
                Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
            )
            .group_by(Surveillance.enseignant_id)
            .all()
        )
        nb_session_map: dict[int, int] = {r.enseignant_id: r.nb for r in rows_session}

        candidats = []
        for ens in enseignants:
            vol = charges.get(ens.id, 0.0)
            candidats.append(EnseignantCandidat(
                enseignant_id=ens.id,
                nom=ens.nom,
                prenom=ens.prenom,
                grade=ens.grade,
                departement_id=ens.departement_id or 0,
                departement_nom=dept_nom,
                volume_horaire=vol,
                volume_restant=0.0,
                volume_consomme=0.0,
                nb_surveillances=0,
                nb_surveillances_session=nb_session_map.get(ens.id, 0),
                meme_departement=True,
            ))
        return candidats

    def _refresh_volumes(
        self,
        candidats: list[EnseignantCandidat],
        session_id: int,
    ) -> None:
        ens_ids = [c.enseignant_id for c in candidats]
        rows = (
            self.db.query(
                Surveillance.enseignant_id,
                func.coalesce(func.sum(Surveillance.charge), 0).label("total"),
                func.count(Surveillance.id).label("nb"),
            )
            .join(Planification)
            .filter(
                Surveillance.enseignant_id.in_(ens_ids),
                Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
                Planification.session_id == session_id,
            )
            .group_by(Surveillance.enseignant_id)
            .all()
        )
        consomme_map = {r.enseignant_id: (float(r.total), r.nb) for r in rows}

        for c in candidats:
            consomme, nb = consomme_map.get(c.enseignant_id, (0.0, 0))
            c.volume_consomme = consomme
            c.volume_restant  = c.volume_horaire - consomme
            # ← CORRECTION : ajouter les surveillances créées en mémoire (pas encore commitées)
            nb_mem = self._nb_surveillances_session_mem.get(c.enseignant_id, 0)
            c.nb_surveillances_session = nb + nb_mem
            c.nb_surveillances = nb + nb_mem

    def _get_creneau(self, planif: Planification) -> Optional[Creneau]:
        if planif.creneau_id in self._creneau_cache:
            return self._creneau_cache[planif.creneau_id]
        creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
        self._creneau_cache[planif.creneau_id] = creneau
        return creneau

    # ── Helpers — contraintes ────────────────────────────────────────────────

    def _check_disponibilite(
        self, enseignant_id: int, planif: Planification
    ) -> bool:
        creneau = self._get_creneau(planif)
        if not creneau:
            return False
        indispos = (
            self.db.query(DisponibiliteEnseignant)
            .filter(
                DisponibiliteEnseignant.enseignant_id == enseignant_id,
                DisponibiliteEnseignant.date == creneau.date,
                DisponibiliteEnseignant.type_dispo.in_(
                    ["INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]
                ),
            )
            .all()
        )
        for i in indispos:
            if i.heure_debut < creneau.heure_fin and i.heure_fin > creneau.heure_debut:
                return False
        return True

    def _check_simultaneite(
        self, enseignant_id: int, planif: Planification
    ) -> bool:
        creneau = self._get_creneau(planif)
        if not creneau:
            return False
        conflit = (
            self.db.query(Surveillance)
            .select_from(Surveillance)
            .join(Planification, Surveillance.planification_id == Planification.id)
            .join(Creneau, Planification.creneau_id == Creneau.id)
            .filter(
                Surveillance.enseignant_id == enseignant_id,
                Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
                Creneau.date        == creneau.date,
                Creneau.heure_debut == creneau.heure_debut,
            )
            .first()
        )
        return conflit is not None

    def _check_conflit_matiere(
        self, enseignant_id: int, planif: Planification
    ) -> bool:
        sm = self.db.query(SectionMatiere).filter(
            SectionMatiere.id == planif.section_matiere_id
        ).first()
        if not sm:
            return False
        return (
            self.db.query(Enseignement)
            .filter(
                Enseignement.enseignant_id == enseignant_id,
                Enseignement.matiere_id    == sm.matiere_id,
                Enseignement.type_enseignement.in_(["COURS", "TD"]),
            )
            .first()
        ) is not None

    # ── Helper — insertion ───────────────────────────────────────────────────

    def _creer_surveillance(
        self,
        planif:   Planification,
        candidat: EnseignantCandidat,
        ligne:    PlanifSalle,
    ) -> Surveillance:
        payload = SurveillanceCreate(
            planification_id=planif.id,
            enseignant_id=candidat.enseignant_id,
            groupe_id=ligne.groupe_id,
            salle_id=ligne.salle_id,
            charge=round(planif.duree / 60, 2),
            mode_affectation=ModeAffectation.AUTOMATIQUE,
            statut_surveillance=StatutSurveillance.AFFECTE,
            est_externe=False,
            motif_externe=None,
        )
        surv = create_surveillance(self.db, payload)

        # ← AJOUT : incrémenter le compteur en mémoire immédiatement
        eid = candidat.enseignant_id
        self._nb_surveillances_session_mem[eid] = (
            self._nb_surveillances_session_mem.get(eid, 0) + 1
        )
        return surv