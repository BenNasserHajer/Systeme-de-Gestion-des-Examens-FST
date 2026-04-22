# # """Surveillance endpoints - API routes for surveillance management."""

# # from typing import Optional
# # from fastapi import APIRouter, Depends, HTTPException, Query
# # from fastapi.responses import FileResponse, StreamingResponse
# # from sqlalchemy.orm import Session
# # import csv
# # from io import StringIO, BytesIO
# # from datetime import datetime

# # from app.database import get_db
# # from app.services.surv_service import SurvService
# # from app.schemas.surveillance_schema import (
# #     SurveillanceCreate,
# #     SurveillanceUpdate,
# #     SurveillanceOut,
# #     ManualAssignmentRequest,
# #     ManualAssignmentBatchRequest,
# #     ManualAssignmentResponse,
# #     ManualAssignmentBatchResponse,
# #     RemplacementRequest,
# #     RemplacementResponse,
# #     EnseignantsDisponiblesResponse,
# #     EnseignantDisponible,
# # )

# # router = APIRouter(prefix="/surveillances", tags=["surveillances"])


# # # ============================================================================
# # # AUTOMATIC AFFECTATION ENDPOINTS
# # # ============================================================================


# # @router.post("/affecter-session")
# # def affecter_session_automatique(
# #     payload: dict = None,
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     POST /surveillances/affecter-session
# #     Lancer l'affectation automatique pour toutes les planifications VALIDEE.
# #     """
# #     if not payload or "session_id" not in payload:
# #         raise HTTPException(status_code=400, detail="session_id requis")

# #     session_id = payload["session_id"]
# #     service = SurvService(db)

# #     try:
# #         results, message = service.affecter_session_automatique(session_id)

# #         # Compter les affectées et conflits
# #         affectees = sum(1 for r in results if r.statut == "AFFECTEE")
# #         conflits = sum(1 for r in results if r.statut == "CONFLIT")

# #         return {
# #             "session_id": session_id,
# #             "total_planifications": len(results),
# #             "affectees_automatiquement": affectees,
# #             "en_conflit": conflits,
# #             "message": message,
# #             "resultats": [
# #                 {
# #                     "planification_id": r.planification_id,
# #                     "statut": r.statut,
# #                     "surveillants_requis": r.surveillants_requis,
# #                     "surveillants_affectes": len(r.surveillants_affectes),
# #                     "manquants": r.manquants,
# #                     "raisons_exclusion": [
# #                         {
# #                             "enseignant_id": v.enseignant_id,
# #                             "nom": v.nom,
# #                             "prenom": v.prenom,
# #                             "raison": v.raison.value,
# #                         }
# #                         for v in r.violations
# #                     ] if r.violations else [],
# #                 }
# #                 for r in results
# #             ],
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # # ============================================================================
# # # MANUAL AFFECTATION ENDPOINTS
# # # ============================================================================


# # @router.post("/manual-assignment")
# # def manual_assignment_single(
# #     request: ManualAssignmentRequest,
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     POST /surveillances/manual-assignment
# #     Affectation manuelle d'une planification en conflit.
# #     """
# #     service = SurvService(db)

# #     try:
# #         result = service.affecter_planification_manuellement(request)
# #         return {
# #             "planification_id": result["planification_id"],
# #             "statut": result["statut"],
# #             "surveillants_inseres": result["surveillants_inseres"],
# #         }
# #     except ValueError as e:
# #         raise HTTPException(status_code=409, detail=str(e))
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # @router.post("/manual-assignment-batch")
# # def manual_assignment_batch(
# #     request: ManualAssignmentBatchRequest,
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     POST /surveillances/manual-assignment-batch
# #     Affectation manuelle totale d'une session.
# #     """
# #     service = SurvService(db)

# #     try:
# #         result = service.affecter_session_manuellement(request)
# #         return {
# #             "session_id": result["session_id"],
# #             "statut": result["statut"],
# #             "total_surveillances_inserees": result["total_surveillances_inserees"],
# #         }
# #     except ValueError as e:
# #         raise HTTPException(status_code=409, detail=str(e))
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # # ============================================================================
# # # CONSULTATION ENDPOINTS
# # # ============================================================================


# # @router.get("/{session_id}")
# # def get_session_surveillances(
# #     session_id: int,
# #     skip: int = Query(0, ge=0),
# #     limit: int = Query(50, ge=1, le=100),
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     GET /surveillances/{session_id}
# #     Récupérer toutes les surveillances d'une session.
# #     """
# #     service = SurvService(db)
# #     surveillances = service.get_all_surveillances(
# #         session_id=session_id,
# #         skip=skip,
# #         limit=limit,
# #     )

# #     return {
# #         "total": len(surveillances),
# #         "data": [
# #             {
# #                 "id": s.id,
# #                 "planification_id": s.planification_id,
# #                 "enseignant_id": s.enseignant_id,
# #                 "charge": float(s.charge),
# #                 "est_externe": s.est_externe,
# #                 "motif_externe": s.motif_externe,
# #                 "mode_affectation": s.mode_affectation,
# #                 "statut_surveillance": s.statut_surveillance,
# #             }
# #             for s in surveillances
# #         ],
# #     }


# # @router.get("/getallsurveillants")
# # def get_all_surveillants(
# #     session_id: int = Query(..., description="ID de la session"),
# #     page: int = Query(1, ge=1),
# #     limit: int = Query(20, ge=1, le=100),
# #     sort: str = Query("volume_restant"),
# #     order: str = Query("desc", regex="^(asc|desc)$"),
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     GET /surveillances/getallsurveillants
# #     Récupérer tous les enseignants disponibles pour affectation.
# #     """
# #     from app.models.session import Session as SessionModel
    
# #     session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
# #     if not session:
# #         raise HTTPException(status_code=404, detail="Session non trouvée")

# #     service = SurvService(db)

# #     # Récupérer tous les enseignants
# #     from app.models.enseignant import Enseignant
# #     enseignants = db.query(Enseignant).all()

# #     disponibles = []
# #     for ens in enseignants:
# #         volume_info = service.get_volume_restant_enseignant(
# #             ens.id,
# #             session.annee_universitaire,
# #         )

# #         disponibles.append({
# #             "enseignant_id": ens.id,
# #             "nom": ens.nom,
# #             "prenom": ens.prenom,
# #             "grade": ens.grade,
# #             "departement": {
# #                 "id": ens.departement_id,
# #                 "nom": ens.departement.nom if ens.departement else "Unknown",
# #                 "code": ens.departement.code if ens.departement else "UNK",
# #             },
# #             "volume_horaire": volume_info["volume_horaire"],
# #             "volume_consomme": volume_info["volume_consomme"],
# #             "volume_restant": volume_info["volume_restant"],
# #             "nb_surveillances": volume_info["nb_surveillances"],
# #         })

# #     # Trier
# #     reverse = order == "desc"
# #     disponibles.sort(key=lambda x: x.get(sort, 0), reverse=reverse)

# #     # Paginer
# #     start = (page - 1) * limit
# #     end = start + limit
# #     paginated = disponibles[start:end]

# #     return {
# #         "data": paginated,
# #         "pagination": {
# #             "page": page,
# #             "limit": limit,
# #             "total": len(disponibles),
# #             "pages": (len(disponibles) + limit - 1) // limit,
# #         },
# #     }


# # @router.get("/disponibles/{planif_id}")
# # def get_enseignants_disponibles(
# #     planif_id: int,
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     GET /surveillances/disponibles/{planif_id}
# #     Récupérer les enseignants disponibles pour une planification (résolution conflit).
# #     Applique uniquement les contraintes 1 et 4.
# #     """
# #     service = SurvService(db)
# #     disponibles = service.get_enseignants_disponibles_pour_planification(planif_id)

# #     return {
# #         "planification_id": planif_id,
# #         "total": len(disponibles),
# #         "data": [
# #             {
# #                 "enseignant_id": d.enseignant_id,
# #                 "nom": d.nom,
# #                 "prenom": d.prenom,
# #                 "grade": d.grade,
# #                 "departement": d.departement,
# #                 "volume_horaire": d.volume_horaire,
# #                 "volume_consomme": d.volume_consomme,
# #                 "volume_restant": d.volume_restant,
# #                 "nb_surveillances": d.nb_surveillances,
# #             }
# #             for d in disponibles
# #         ],
# #     }


# # # ============================================================================
# # # DETAIL ENDPOINTS
# # # ============================================================================


# # @router.get("/{surveillance_id}/detail")
# # def get_surveillance_detail(
# #     surveillance_id: int,
# #     db: Session = Depends(get_db),
# # ):
# #     """GET /surveillances/{surveillance_id}/detail"""
# #     service = SurvService(db)
# #     surveillance = service.get_surveillance_by_id(surveillance_id)

# #     if not surveillance:
# #         raise HTTPException(status_code=404, detail="Surveillance non trouvée")

# #     return {
# #         "id": surveillance.id,
# #         "planification_id": surveillance.planification_id,
# #         "enseignant_id": surveillance.enseignant_id,
# #         "charge": float(surveillance.charge),
# #         "presence": surveillance.presence,
# #         "mode_affectation": surveillance.mode_affectation,
# #         "statut_surveillance": surveillance.statut_surveillance,
# #         "est_externe": surveillance.est_externe,
# #         "motif_externe": surveillance.motif_externe,
# #         "created_at": surveillance.created_at.isoformat(),
# #         "updated_at": surveillance.updated_at.isoformat(),
# #     }


# # # ============================================================================
# # # MODIFICATION ENDPOINTS
# # # ============================================================================


# # @router.patch("/{surveillance_id}")
# # def update_surveillance(
# #     surveillance_id: int,
# #     payload: SurveillanceUpdate,
# #     db: Session = Depends(get_db),
# # ):
# #     """PATCH /surveillances/{surveillance_id}"""
# #     service = SurvService(db)

# #     result = service.update_surveillance(surveillance_id, payload)
# #     if not result:
# #         raise HTTPException(status_code=404, detail="Surveillance non trouvée")

# #     return {
# #         "id": result.id,
# #         "planification_id": result.planification_id,
# #         "enseignant_id": result.enseignant_id,
# #         "charge": float(result.charge),
# #         "statut_surveillance": result.statut_surveillance,
# #         "motif_externe": result.motif_externe,
# #         "updated_at": result.updated_at.isoformat(),
# #     }


# # @router.post("/{surveillance_id}/remplacer")
# # def replace_surveillance(
# #     surveillance_id: int,
# #     request: RemplacementRequest,
# #     db: Session = Depends(get_db),
# # ):
# #     """POST /surveillances/{surveillance_id}/remplacer"""
# #     service = SurvService(db)

# #     try:
# #         old, new = service.replace_surveillance(
# #             surveillance_id,
# #             request.nouvel_enseignant_id,
# #             request.motif,
# #         )

# #         return {
# #             "ancienne_surveillance_id": old.id,
# #             "nouvelle_surveillance_id": new.id,
# #             "motif": request.motif,
# #         }
# #     except ValueError as e:
# #         raise HTTPException(status_code=404, detail=str(e))
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # # ============================================================================
# # # DELETION ENDPOINTS
# # # ============================================================================


# # @router.delete("/{surveillance_id}")
# # def delete_surveillance(
# #     surveillance_id: int,
# #     db: Session = Depends(get_db),
# # ):
# #     """DELETE /surveillances/{surveillance_id}"""
# #     service = SurvService(db)

# #     if not service.delete_surveillance(surveillance_id):
# #         raise HTTPException(status_code=404, detail="Surveillance non trouvée")

# #     return {"message": "Surveillance supprimée avec succès"}


# # # ============================================================================
# # # RAPPORT & EXPORT ENDPOINTS
# # # ============================================================================


# # @router.get("/session/{session_id}/rapport")
# # def get_rapport_session(
# #     session_id: int,
# #     departement_id: Optional[int] = None,
# #     db: Session = Depends(get_db),
# # ):
# #     """GET /surveillances/session/{session_id}/rapport"""
# #     from app.models.session import Session as SessionModel

# #     session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
# #     if not session:
# #         raise HTTPException(status_code=404, detail="Session non trouvée")

# #     service = SurvService(db)
# #     surveillances = service.get_all_surveillances(session_id=session_id, limit=10000)

# #     return {
# #         "session_id": session_id,
# #         "session_info": {
# #             "type": session.type_session,
# #             "annee_univ": session.annee_universitaire,
# #             "date_debut": session.date_debut.isoformat(),
# #             "date_fin": session.date_fin.isoformat(),
# #         },
# #         "total_surveillances": len(surveillances),
# #         "total_externes": sum(1 for s in surveillances if s.est_externe),
# #         "taux_externe": (sum(1 for s in surveillances if s.est_externe) / len(surveillances) * 100) if surveillances else 0,
# #         "date_generation": datetime.now().isoformat(),
# #     }


# # @router.get("/session/{session_id}/export")
# # def export_session(
# #     session_id: int,
# #     format: str = Query("csv", regex="^(csv|xlsx)$"),
# #     db: Session = Depends(get_db),
# # ):
# #     """GET /surveillances/session/{session_id}/export"""
# #     service = SurvService(db)
# #     surveillances = service.get_all_surveillances(session_id=session_id, limit=10000)

# #     if format == "csv":
# #         output = StringIO()
# #         writer = csv.DictWriter(
# #             output,
# #             fieldnames=[
# #                 "ID",
# #                 "Planification",
# #                 "Enseignant",
# #                 "Charge",
# #                 "Mode",
# #                 "Statut",
# #                 "Externe",
# #                 "Motif",
# #             ],
# #         )
# #         writer.writeheader()

# #         for s in surveillances:
# #             writer.writerow({
# #                 "ID": s.id,
# #                 "Planification": s.planification_id,
# #                 "Enseignant": s.enseignant_id,
# #                 "Charge": f"{s.charge:.2f}",
# #                 "Mode": s.mode_affectation,
# #                 "Statut": s.statut_surveillance,
# #                 "Externe": "Oui" if s.est_externe else "Non",
# #                 "Motif": s.motif_externe or "",
# #             })

# #         return StreamingResponse(
# #             iter([output.getvalue()]),
# #             media_type="text/csv",
# #             headers={"Content-Disposition": "attachment; filename=surveillances.csv"},
# #         )
# #     else:
# #         # XLSX format (simplified)
# #         return HTTPException(status_code=501, detail="Format XLSX non implémenté")


# # @router.get("/statistiques")
# # def get_statistiques(
# #     annee_univ: str = Query(..., description="Année universitaire"),
# #     db: Session = Depends(get_db),
# # ):
# #     """GET /surveillances/statistiques"""
# #     from app.models.surveillance import Surveillance
# #     from app.models.planification import Planification
# #     from app.models.session import Session as SessionModel
# #     from sqlalchemy import func

# #     stats = db.query(
# #         func.count(Surveillance.id).label("total_surveillances"),
# #         func.sum(Surveillance.charge).label("total_heures"),
# #         func.count(func.distinct(Surveillance.enseignant_id)).label("unique_enseignants"),
# #         func.sum(func.cast(Surveillance.est_externe, db.Integer)).label("count_externes"),
# #     ).join(Planification).join(SessionModel).filter(
# #         SessionModel.annee_universitaire == annee_univ,
# #     ).first()

# #     total = stats.total_surveillances or 0
# #     externes = stats.count_externes or 0

# #     return {
# #         "annee_universitaire": annee_univ,
# #         "total_surveillances": total,
# #         "total_heures": float(stats.total_heures or 0),
# #         "unique_enseignants": stats.unique_enseignants or 0,
# #         "count_externes": externes,
# #         "taux_externe": (externes / total * 100) if total > 0 else 0,
# #     }


# # # ============================================================================
# # # HELPER ENDPOINTS
# # # ============================================================================


# # @router.get("/enseignant/{enseignant_id}/disponibilites")
# # def get_enseignant_disponibilites(
# #     enseignant_id: int,
# #     date_debut: str,
# #     date_fin: str,
# #     db: Session = Depends(get_db),
# # ):
# #     """GET /surveillances/enseignant/{enseignant_id}/disponibilites"""
# #     from app.models.disponibilite_enseignant import DisponibiliteEnseignant
# #     from datetime import datetime as dt

# #     try:
# #         start_date = dt.strptime(date_debut, "%Y-%m-%d").date()
# #         end_date = dt.strptime(date_fin, "%Y-%m-%d").date()
# #     except ValueError:
# #         raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")

# #     disponibilites = db.query(DisponibiliteEnseignant).filter(
# #         DisponibiliteEnseignant.enseignant_id == enseignant_id,
# #         DisponibiliteEnseignant.date >= start_date,
# #         DisponibiliteEnseignant.date <= end_date,
# #     ).all()

# #     return {
# #         "enseignant_id": enseignant_id,
# #         "date_debut": date_debut,
# #         "date_fin": date_fin,
# #         "disponibilites": [
# #             {
# #                 "date": d.date.isoformat(),
# #                 "heure_debut": str(d.heure_debut),
# #                 "heure_fin": str(d.heure_fin),
# #                 "type": d.type_dispo,
# #                 "motif": d.motif,
# #             }
# #             for d in disponibilites
# #         ],
# #     }


# """Surveillance endpoints - API routes for surveillance management."""

# from typing import Optional
# from fastapi import APIRouter, Depends, HTTPException, Query
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# import csv
# from io import StringIO
# from datetime import datetime

# from app.database import get_db
# from app.services.surv_service import SurvService
# from app.schemas.surveillance_schema import (
#     SurveillanceUpdate,
#     ManualAssignmentRequest,
#     ManualAssignmentBatchRequest,
#     RemplacementRequest,
# )

# # router = APIRouter(prefix="/surveillances", tags=["surveillances"])

# router = APIRouter(prefix="/surveillances", tags=["Surveillance"])



# # ============================================================================
# # AUTOMATIC AFFECTATION ENDPOINTS
# # ============================================================================


# @router.post("/affecter-session")
# def affecter_session_automatique(
#     payload: dict = None,
#     db: Session = Depends(get_db),
# ):
#     """
#     POST /surveillances/affecter-session
#     Lancer l'affectation automatique pour toutes les planifications VALIDEE.
#     """
#     if not payload or "session_id" not in payload:
#         raise HTTPException(status_code=400, detail="session_id requis")

#     session_id = payload["session_id"]
#     service = SurvService(db)

#     try:
#         results, message = service.affecter_session_automatique(session_id)

#         affectees = sum(1 for r in results if r.statut == "AFFECTEE")
#         conflits = sum(1 for r in results if r.statut == "CONFLIT")

#         return {
#             "session_id": session_id,
#             "total_planifications": len(results),
#             "affectees_automatiquement": affectees,
#             "en_conflit": conflits,
#             "message": message,
#             "resultats": [
#                 {
#                     "planification_id": r.planification_id,
#                     "statut": r.statut,
#                     "surveillants_requis": r.surveillants_requis,
#                     "surveillants_affectes": len(r.surveillants_affectes),
#                     "manquants": r.manquants,
#                     "raisons_exclusion": [
#                         {
#                             "enseignant_id": v.enseignant_id,
#                             "nom": v.nom,
#                             "prenom": v.prenom,
#                             "raison": v.raison.value,
#                         }
#                         for v in r.violations
#                     ] if r.violations else [],
#                 }
#                 for r in results
#             ],
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# # ============================================================================
# # MANUAL AFFECTATION ENDPOINTS
# # ============================================================================


# @router.post("/manual-assignment")
# def manual_assignment_single(
#     request: ManualAssignmentRequest,
#     db: Session = Depends(get_db),
# ):
#     """
#     POST /surveillances/manual-assignment
#     Affectation manuelle d'une planification en conflit.
#     """
#     service = SurvService(db)

#     try:
#         result = service.affecter_planification_manuellement(request)
#         return {
#             "planification_id": result["planification_id"],
#             "statut": result["statut"],
#             "surveillants_inseres": result["surveillants_inseres"],
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=409, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/manual-assignment-batch")
# def manual_assignment_batch(
#     request: ManualAssignmentBatchRequest,
#     db: Session = Depends(get_db),
# ):
#     """
#     POST /surveillances/manual-assignment-batch
#     Affectation manuelle totale d'une session.
#     """
#     service = SurvService(db)

#     try:
#         result = service.affecter_session_manuellement(request)
#         return {
#             "session_id": result["session_id"],
#             "statut": result["statut"],
#             "total_surveillances_inserees": result["total_surveillances_inserees"],
#             "planifications_non_affectees": result.get("planifications_non_affectees", []),
#             "message": result.get("message", ""),
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=409, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# # ============================================================================
# # CONSULTATION ENDPOINTS
# # ============================================================================


# @router.get("/{session_id}")
# def get_session_surveillances(
#     session_id: int,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(50, ge=1, le=100),
#     db: Session = Depends(get_db),
# ):
#     """
#     GET /surveillances/{session_id}
#     Récupérer toutes les surveillances d'une session.
#     """
#     service = SurvService(db)
#     surveillances = service.get_all_surveillances(
#         session_id=session_id,
#         skip=skip,
#         limit=limit,
#     )

#     return {
#         "total": len(surveillances),
#         "data": [
#             {
#                 "id": s.id,
#                 "planification_id": s.planification_id,
#                 "enseignant_id": s.enseignant_id,
#                 "charge": float(s.charge),
#                 "est_externe": s.est_externe,
#                 "motif_externe": s.motif_externe,
#                 "mode_affectation": s.mode_affectation,
#                 "statut_surveillance": s.statut_surveillance,
#             }
#             for s in surveillances
#         ],
#     }


# @router.get("/getallsurveillants")
# def get_all_surveillants(
#     session_id: int = Query(..., description="ID de la session"),
#     page: int = Query(1, ge=1),
#     limit: int = Query(20, ge=1, le=100),
#     sort: str = Query("volume_restant"),
#     order: str = Query("desc", regex="^(asc|desc)$"),
#     db: Session = Depends(get_db),
# ):
#     """
#     GET /surveillances/getallsurveillants
#     Récupérer tous les enseignants disponibles pour affectation.
#     """
#     from app.models.salle_session import Session as SessionModel
    
#     session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Session non trouvée")

#     service = SurvService(db)

#     from app.models.enseignant import Enseignant
#     enseignants = db.query(Enseignant).all()

#     disponibles = []
#     for ens in enseignants:
#         volume_info = service.get_volume_restant_enseignant(
#             ens.id,
#             session.annee_universitaire,
#         )

#         disponibles.append({
#             "enseignant_id": ens.id,
#             "nom": ens.nom,
#             "prenom": ens.prenom,
#             "grade": ens.grade,
#             "departement": {
#                 "id": ens.departement_id,
#                 "nom": ens.departement.nom if ens.departement else "Unknown",
#                 "code": ens.departement.code if ens.departement else "UNK",
#             },
#             "volume_horaire": volume_info["volume_horaire"],
#             "volume_consomme": volume_info["volume_consomme"],
#             "volume_restant": volume_info["volume_restant"],
#             "nb_surveillances": volume_info["nb_surveillances"],
#         })

#     reverse = order == "desc"
#     disponibles.sort(key=lambda x: x.get(sort, 0), reverse=reverse)

#     start = (page - 1) * limit
#     end = start + limit
#     paginated = disponibles[start:end]

#     return {
#         "data": paginated,
#         "pagination": {
#             "page": page,
#             "limit": limit,
#             "total": len(disponibles),
#             "pages": (len(disponibles) + limit - 1) // limit,
#         },
#     }


# @router.get("/disponibles/{planif_id}")
# def get_enseignants_disponibles(
#     planif_id: int,
#     db: Session = Depends(get_db),
# ):
#     """
#     GET /surveillances/disponibles/{planif_id}
#     Récupérer les enseignants disponibles pour une planification (résolution conflit).
#     Applique uniquement les contraintes 1 et 4.
#     """
#     service = SurvService(db)
#     disponibles = service.get_enseignants_disponibles_pour_planification(planif_id)

#     return {
#         "planification_id": planif_id,
#         "total": len(disponibles),
#         "data": [
#             {
#                 "enseignant_id": d.enseignant_id,
#                 "nom": d.nom,
#                 "prenom": d.prenom,
#                 "grade": d.grade,
#                 "departement": d.departement,
#                 "volume_horaire": d.volume_horaire,
#                 "volume_consomme": d.volume_consomme,
#                 "volume_restant": d.volume_restant,
#                 "nb_surveillances": d.nb_surveillances,
#             }
#             for d in disponibles
#         ],
#     }


# # ============================================================================
# # DETAIL ENDPOINTS
# # ============================================================================


# @router.get("/{surveillance_id}/detail")
# def get_surveillance_detail(
#     surveillance_id: int,
#     db: Session = Depends(get_db),
# ):
#     """GET /surveillances/{surveillance_id}/detail"""
#     service = SurvService(db)
#     surveillance = service.get_surveillance_by_id(surveillance_id)

#     if not surveillance:
#         raise HTTPException(status_code=404, detail="Surveillance non trouvée")

#     return {
#         "id": surveillance.id,
#         "planification_id": surveillance.planification_id,
#         "enseignant_id": surveillance.enseignant_id,
#         "charge": float(surveillance.charge),
#         "presence": surveillance.presence,
#         "mode_affectation": surveillance.mode_affectation,
#         "statut_surveillance": surveillance.statut_surveillance,
#         "est_externe": surveillance.est_externe,
#         "motif_externe": surveillance.motif_externe,
#         "created_at": surveillance.created_at.isoformat(),
#         "updated_at": surveillance.updated_at.isoformat(),
#     }


# # ============================================================================
# # MODIFICATION ENDPOINTS
# # ============================================================================


# @router.patch("/{surveillance_id}")
# def update_surveillance(
#     surveillance_id: int,
#     payload: SurveillanceUpdate,
#     db: Session = Depends(get_db),
# ):
#     """PATCH /surveillances/{surveillance_id}"""
#     service = SurvService(db)

#     result = service.update_surveillance(surveillance_id, payload)
#     if not result:
#         raise HTTPException(status_code=404, detail="Surveillance non trouvée")

#     return {
#         "id": result.id,
#         "planification_id": result.planification_id,
#         "enseignant_id": result.enseignant_id,
#         "charge": float(result.charge),
#         "statut_surveillance": result.statut_surveillance,
#         "motif_externe": result.motif_externe,
#         "updated_at": result.updated_at.isoformat(),
#     }


# @router.post("/{surveillance_id}/remplacer")
# def replace_surveillance(
#     surveillance_id: int,
#     request: RemplacementRequest,
#     db: Session = Depends(get_db),
# ):
#     """POST /surveillances/{surveillance_id}/remplacer"""
#     service = SurvService(db)

#     try:
#         old, new = service.replace_surveillance(
#             surveillance_id,
#             request.nouvel_enseignant_id,
#             request.motif,
#         )

#         return {
#             "ancienne_surveillance_id": old.id,
#             "nouvelle_surveillance_id": new.id,
#             "motif": request.motif,
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# # ============================================================================
# # DELETION ENDPOINTS
# # ============================================================================


# @router.delete("/{surveillance_id}")
# def delete_surveillance(
#     surveillance_id: int,
#     db: Session = Depends(get_db),
# ):
#     """DELETE /surveillances/{surveillance_id}"""
#     service = SurvService(db)

#     if not service.delete_surveillance(surveillance_id):
#         raise HTTPException(status_code=404, detail="Surveillance non trouvée")

#     return {"message": "Surveillance supprimée avec succès"}


# # ============================================================================
# # RAPPORT & EXPORT ENDPOINTS
# # ============================================================================


# @router.get("/session/{session_id}/rapport")
# def get_rapport_session(
#     session_id: int,
#     departement_id: Optional[int] = None,
#     db: Session = Depends(get_db),
# ):
#     """
#     GET /surveillances/session/{session_id}/rapport
#     Générer un rapport complet d'affectation pour une session.
#     """
#     from app.models.salle_session import Session as SessionModel
#     from app.models.planification_examen import PlanificationExamen
#     from app.models.surveillance import Surveillance
#     from app.models.enseignant import Enseignant, ChargeHoraire
#     from app.models.salle_session import Creneau
#     from app.models.section_matiere import SectionMatiere
#     from app.models.matiere import Matiere
#     from app.models.departement_niveau_section import Section
#     from sqlalchemy import func

#     session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Session non trouvée")

#     # Récupérer les planifications avec filtrage par département
#     query = db.query(PlanificationExamen).filter(
#         PlanificationExamen.session_id == session_id,
#         PlanificationExamen.statut_planif == "VALIDEE",
#     )
    
#     # ✅ Appliquer le filtre departement_id
#     if departement_id:
#         query = query.filter(PlanificationExamen.departement_id == departement_id)
    
#     planifications = query.all()

#     # Récupérer toutes les surveillances de la session
#     surv_query = db.query(Surveillance).join(PlanificationExamen).filter(
#         PlanificationExamen.session_id == session_id,
#         PlanificationExamen.statut_planif == "VALIDEE",
#     )
#     if departement_id:
#         surv_query = surv_query.filter(PlanificationExamen.departement_id == departement_id)
#     surveillances = surv_query.all()

#     # ============================================================
#     # 1. Détail des planifications
#     # ============================================================
#     planifications_detail = []
#     planifications_en_conflit = []
    
#     for planif in planifications:
#         survs = [s for s in surveillances if s.planification_id == planif.id]
        
#         section_matiere = db.query(SectionMatiere).filter(
#             SectionMatiere.id == planif.section_matiere_id
#         ).first()
#         matiere = db.query(Matiere).filter(Matiere.id == section_matiere.matiere_id).first() if section_matiere else None
#         creneau = db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
#         section = db.query(Section).filter(Section.id == section_matiere.section_id).first() if section_matiere else None
        
#         planif_data = {
#             "planification_id": planif.id,
#             "matiere_code": matiere.code if matiere else "N/A",
#             "matiere_intitule": matiere.intitule if matiere else "N/A",
#             "section_nom": section.nom if section else "N/A",
#             "type_epreuve": planif.type_epreuve,
#             "duree": planif.duree,
#             "creneau": {
#                 "date": creneau.date.isoformat() if creneau else None,
#                 "heure_debut": str(creneau.heure_debut) if creneau else None,
#                 "heure_fin": str(creneau.heure_fin) if creneau else None,
#             },
#             "nb_surveillants_requis": planif.nb_surveillants_requis,
#             "surveillants": [
#                 {
#                     "enseignant_id": s.enseignant_id,
#                     "nom": s.enseignant.nom,
#                     "prenom": s.enseignant.prenom,
#                     "grade": s.enseignant.grade,
#                     "charge_imputee": float(s.charge),
#                     "mode_affectation": s.mode_affectation,
#                     "est_externe": s.est_externe,
#                     "motif_externe": s.motif_externe,
#                 }
#                 for s in survs
#             ],
#         }
        
#         planifications_detail.append(planif_data)
        
#         # ✅ Vérifier si c'est un conflit
#         if len(survs) < planif.nb_surveillants_requis:
#             planifications_en_conflit.append({
#                 **planif_data,
#                 "surveillants_trouves": len(survs),
#                 "manquants": planif.nb_surveillants_requis - len(survs),
#             })

#     # ============================================================
#     # 2. Classement des enseignants par charge cumulée
#     # ============================================================
#     enseignant_charges = {}
#     for surv in surveillances:
#         ens_id = surv.enseignant_id
#         if ens_id not in enseignant_charges:
#             charge_horaire = db.query(ChargeHoraire).filter(
#                 ChargeHoraire.enseignant_id == ens_id,
#                 ChargeHoraire.annee_univ == session.annee_universitaire,
#             ).first()
#             enseignant_charges[ens_id] = {
#                 "enseignant_id": ens_id,
#                 "nom": surv.enseignant.nom,
#                 "prenom": surv.enseignant.prenom,
#                 "grade": surv.enseignant.grade,
#                 "charge_totale": 0.0,
#                 "nb_surveillances": 0,
#                 "volume_horaire": charge_horaire.volume_horaire if charge_horaire else 0.0,
#             }
#         enseignant_charges[ens_id]["charge_totale"] += float(surv.charge)
#         enseignant_charges[ens_id]["nb_surveillances"] += 1

#     classement = []
#     for data in enseignant_charges.values():
#         taux_utilisation = (data["charge_totale"] / data["volume_horaire"] * 100) if data["volume_horaire"] > 0 else 0
#         classement.append({
#             "enseignant_id": data["enseignant_id"],
#             "nom": data["nom"],
#             "prenom": data["prenom"],
#             "grade": data["grade"],
#             "charge_totale": round(data["charge_totale"], 2),
#             "nb_surveillances": data["nb_surveillances"],
#             "taux_utilisation": round(taux_utilisation, 2),
#         })
    
#     classement.sort(key=lambda x: x["charge_totale"], reverse=True)

#     # ============================================================
#     # 3. Statistiques
#     # ============================================================
#     total_planifs = len(planifications)
#     total_completes = sum(1 for p in planifications_detail if len(p["surveillants"]) >= p["nb_surveillants_requis"])
#     total_partielles = sum(1 for p in planifications_detail if 0 < len(p["surveillants"]) < p["nb_surveillants_requis"])
#     total_non_affectees = sum(1 for p in planifications_detail if len(p["surveillants"]) == 0)

#     return {
#         "session": {
#             "id": session.id,
#             "type_session": session.type_session,
#             "annee_univ": session.annee_universitaire,
#             "date_debut": session.date_debut.isoformat(),
#             "date_fin": session.date_fin.isoformat(),
#             "statut": session.statut,
#         },
#         "statistiques": {
#             "total_planifications": total_planifs,
#             "completes": total_completes,
#             "partielles": total_partielles,
#             "non_affectees": total_non_affectees,
#         },
#         "planifications": planifications_detail,
#         "en_conflit": planifications_en_conflit,
#         "classement_enseignants": classement,
#         "date_generation": datetime.now().isoformat(),
#     }


# @router.get("/session/{session_id}/export")
# def export_session(
#     session_id: int,
#     format: str = Query("csv", regex="^(csv|xlsx)$"),
#     db: Session = Depends(get_db),
# ):
#     """GET /surveillances/session/{session_id}/export"""
#     service = SurvService(db)
#     surveillances = service.get_all_surveillances(session_id=session_id, limit=10000)

#     if format == "csv":
#         output = StringIO()
#         writer = csv.DictWriter(
#             output,
#             fieldnames=["ID", "Planification", "Enseignant", "Charge", "Mode", "Statut", "Externe", "Motif"],
#         )
#         writer.writeheader()

#         for s in surveillances:
#             writer.writerow({
#                 "ID": s.id,
#                 "Planification": s.planification_id,
#                 "Enseignant": s.enseignant_id,
#                 "Charge": f"{s.charge:.2f}",
#                 "Mode": s.mode_affectation,
#                 "Statut": s.statut_surveillance,
#                 "Externe": "Oui" if s.est_externe else "Non",
#                 "Motif": s.motif_externe or "",
#             })

#         return StreamingResponse(
#             iter([output.getvalue()]),
#             media_type="text/csv",
#             headers={"Content-Disposition": "attachment; filename=surveillances.csv"},
#         )
#     else:
#         raise HTTPException(status_code=501, detail="Format XLSX non implémenté")


# @router.get("/statistiques")
# def get_statistiques(
#     annee_univ: str = Query(..., description="Année universitaire"),
#     db: Session = Depends(get_db),
# ):
#     """GET /surveillances/statistiques"""
#     from app.models.surveillance import Surveillance
#     from app.models.planification_examen import PlanificationExamen
#     from app.models.salle_session import Session as SessionModel
#     from sqlalchemy import func

#     stats = db.query(
#         func.count(Surveillance.id).label("total_surveillances"),
#         func.sum(Surveillance.charge).label("total_heures"),
#         func.count(func.distinct(Surveillance.enseignant_id)).label("unique_enseignants"),
#         func.sum(func.cast(Surveillance.est_externe, db.Integer)).label("count_externes"),
#     ).join(PlanificationExamen).join(SessionModel).filter(
#         SessionModel.annee_universitaire == annee_univ,
#     ).first()

#     # ✅ Calcul du nombre total de surveillances REQUISES
#     total_requis = db.query(func.sum(PlanificationExamen.nb_surveillants_requis)).join(
#         SessionModel
#     ).filter(
#         SessionModel.annee_universitaire == annee_univ,
#         PlanificationExamen.statut_planif == "VALIDEE",
#     ).scalar() or 0

#     total = stats.total_surveillances or 0
#     externes = stats.count_externes or 0
    
#     # ✅ Calcul du taux de remplissage
#     taux_remplissage = (total / total_requis * 100) if total_requis > 0 else 0

#     return {
#         "annee_universitaire": annee_univ,
#         "total_surveillances": total,
#         "total_heures": float(stats.total_heures or 0),
#         "unique_enseignants": stats.unique_enseignants or 0,
#         "count_externes": externes,
#         "taux_externe": (externes / total * 100) if total > 0 else 0,
#         "taux_remplissage": round(taux_remplissage, 2),
#     }


# @router.get("/session/{session_id}/conflits")
# def get_session_conflits(
#     session_id: int,
#     db: Session = Depends(get_db),
# ):
#     """
#     GET /surveillances/session/{session_id}/conflits
#     Retourne la liste des planifications en conflit non résolues pour une session.
#     """
#     from app.models.planification_examen import PlanificationExamen
#     from app.models.surveillance import Surveillance
#     from app.models.salle_session import Creneau

#     planifications = db.query(PlanificationExamen).filter(
#         PlanificationExamen.session_id == session_id,
#         PlanificationExamen.statut_planif == "VALIDEE",
#     ).all()

#     conflits = []
#     for planif in planifications:
#         nb_affectees = db.query(Surveillance).filter(
#             Surveillance.planification_id == planif.id,
#             Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
#         ).count()

#         if nb_affectees < planif.nb_surveillants_requis:
#             creneau = db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
            
#             conflits.append({
#                 "planification_id": planif.id,
#                 "type_epreuve": planif.type_epreuve,
#                 "creneau": {
#                     "date": creneau.date.isoformat() if creneau else None,
#                     "heure_debut": str(creneau.heure_debut) if creneau else None,
#                     "heure_fin": str(creneau.heure_fin) if creneau else None,
#                 },
#                 "surveillants_requis": planif.nb_surveillants_requis,
#                 "surveillants_trouves": nb_affectees,
#                 "manquants": planif.nb_surveillants_requis - nb_affectees,
#                 "statut_resolution": "NON_RESOLU",
#             })

#     return {
#         "session_id": session_id,
#         "total_conflits": len(conflits),
#         "conflits": conflits,
#     }


# # ============================================================================
# # HELPER ENDPOINTS
# # ============================================================================


# @router.get("/enseignant/{enseignant_id}/disponibilites")
# def get_enseignant_disponibilites(
#     enseignant_id: int,
#     date_debut: str,
#     date_fin: str,
#     db: Session = Depends(get_db),
# ):
#     """GET /surveillances/enseignant/{enseignant_id}/disponibilites"""
#     from app.models.disponibilite import DisponibiliteEnseignant
#     from datetime import datetime as dt

#     try:
#         start_date = dt.strptime(date_debut, "%Y-%m-%d").date()
#         end_date = dt.strptime(date_fin, "%Y-%m-%d").date()
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")

#     disponibilites = db.query(DisponibiliteEnseignant).filter(
#         DisponibiliteEnseignant.enseignant_id == enseignant_id,
#         DisponibiliteEnseignant.date >= start_date,
#         DisponibiliteEnseignant.date <= end_date,
#     ).all()

#     return {
#         "enseignant_id": enseignant_id,
#         "date_debut": date_debut,
#         "date_fin": date_fin,
#         "disponibilites": [
#             {
#                 "date": d.date.isoformat(),
#                 "heure_debut": str(d.heure_debut),
#                 "heure_fin": str(d.heure_fin),
#                 "type": d.type_dispo,
#                 "motif": d.motif,
#             }
#             for d in disponibilites
#         ],
#     }

"""Surveillance endpoints - API routes for surveillance management."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
from io import StringIO
from datetime import datetime

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
    GetAllSurveillantsResponse,
    GetAllSurveillantsItem,
    GetDisponibilitesResponse,
    DisponibiliteItem,
    StatistiquesResponse,
)

router = APIRouter(prefix="/surveillances", tags=["Surveillance"])


# ============================================================================
# AUTOMATIC AFFECTATION ENDPOINTS
# ============================================================================


@router.post("/affecter-session", response_model=AffecterSessionResponse)
def affecter_session_automatique(
    payload: AffecterSessionRequest,
    db: Session = Depends(get_db),
):
    """
    POST /surveillances/affecter-session
    Lancer l'affectation automatique pour toutes les planifications VALIDEE.
    """
    session_id = payload.session_id
    service = SurvService(db)

    try:
        results, message = service.affecter_session_automatique(session_id)

        affectees = sum(1 for r in results if r.statut == "AFFECTEE")
        conflits = sum(1 for r in results if r.statut == "CONFLIT")

        resultats = []
        for r in results:
            resultats.append(
                AffecterSessionResult(
                    planification_id=r.planification_id,
                    statut=r.statut,
                    surveillants_requis=r.surveillants_requis,
                    surveillants_affectes=len(r.surveillants_affectes),
                    manquants=r.manquants,
                    raisons_exclusion=[
                        {
                            "enseignant_id": v.enseignant_id,
                            "nom": v.nom,
                            "prenom": v.prenom,
                            "raison": v.raison.value,
                        }
                        for v in r.violations
                    ] if r.violations else [],
                )
            )

        return AffecterSessionResponse(
            session_id=session_id,
            total_planifications=len(results),
            affectees_automatiquement=affectees,
            en_conflit=conflits,
            message=message,
            resultats=resultats,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# MANUAL AFFECTATION ENDPOINTS
# ============================================================================


@router.post("/manual-assignment")
def manual_assignment_single(
    request: ManualAssignmentRequest,
    db: Session = Depends(get_db),
):
    """
    POST /surveillances/manual-assignment
    Affectation manuelle d'une planification en conflit.
    """
    service = SurvService(db)

    try:
        result = service.affecter_planification_manuellement(request)
        return {
            "planification_id": result["planification_id"],
            "statut": result["statut"],
            "surveillants_inseres": result["surveillants_inseres"],
        }
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/manual-assignment-batch")
def manual_assignment_batch(
    request: ManualAssignmentBatchRequest,
    db: Session = Depends(get_db),
):
    """
    POST /surveillances/manual-assignment-batch
    Affectation manuelle totale d'une session.
    """
    service = SurvService(db)

    try:
        result = service.affecter_session_manuellement(request)
        return {
            "session_id": result["session_id"],
            "statut": result["statut"],
            "total_surveillances_inserees": result["total_surveillances_inserees"],
            "planifications_non_affectees": result.get("planifications_non_affectees", []),
            "message": result.get("message", ""),
        }
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# CONSULTATION ENDPOINTS
# ============================================================================


@router.get("/{session_id}")
def get_session_surveillances(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    GET /surveillances/{session_id}
    Récupérer toutes les surveillances d'une session.
    """
    service = SurvService(db)
    surveillances = service.get_all_surveillances(
        session_id=session_id,
        skip=skip,
        limit=limit,
    )

    return {
        "total": len(surveillances),
        "data": [
            {
                "id": s.id,
                "planification_id": s.planification_id,
                "enseignant_id": s.enseignant_id,
                "charge": float(s.charge),
                "est_externe": s.est_externe,
                "motif_externe": s.motif_externe,
                "mode_affectation": s.mode_affectation,
                "statut_surveillance": s.statut_surveillance,
            }
            for s in surveillances
        ],
    }


@router.get("/getallsurveillants", response_model=GetAllSurveillantsResponse)
def get_all_surveillants(
    session_id: int = Query(..., description="ID de la session"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("volume_restant"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """
    GET /surveillances/getallsurveillants
    Récupérer tous les enseignants disponibles pour affectation.
    """
    from app.models.salle_session import Session as SessionModel
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    service = SurvService(db)

    from app.models.enseignant import Enseignant
    enseignants = db.query(Enseignant).all()

    disponibles = []
    for ens in enseignants:
        volume_info = service.get_volume_restant_enseignant(
            ens.id,
            session.annee_universitaire,
        )

        disponibles.append(
            GetAllSurveillantsItem(
                enseignant_id=ens.id,
                nom=ens.nom,
                prenom=ens.prenom,
                grade=ens.grade,
                departement={
                    "id": ens.departement_id,
                    "nom": ens.departement.nom if ens.departement else "Unknown",
                    "code": ens.departement.code if ens.departement else "UNK",
                },
                volume_horaire=volume_info["volume_horaire"],
                volume_consomme=volume_info["volume_consomme"],
                volume_restant=volume_info["volume_restant"],
                nb_surveillances=volume_info["nb_surveillances"],
            )
        )

    reverse = order == "desc"
    disponibles.sort(key=lambda x: getattr(x, sort, 0), reverse=reverse)

    start = (page - 1) * limit
    end = start + limit
    paginated = disponibles[start:end]

    return GetAllSurveillantsResponse(
        data=paginated,
        pagination={
            "page": page,
            "limit": limit,
            "total": len(disponibles),
            "pages": (len(disponibles) + limit - 1) // limit,
        },
    )


@router.get("/disponibles/{planif_id}")
def get_enseignants_disponibles(
    planif_id: int,
    db: Session = Depends(get_db),
):
    """
    GET /surveillances/disponibles/{planif_id}
    Récupérer les enseignants disponibles pour une planification (résolution conflit).
    Applique uniquement les contraintes 1 et 4.
    """
    service = SurvService(db)
    disponibles = service.get_enseignants_disponibles_pour_planification(planif_id)

    return {
        "planification_id": planif_id,
        "total": len(disponibles),
        "data": [
            {
                "enseignant_id": d.enseignant_id,
                "nom": d.nom,
                "prenom": d.prenom,
                "grade": d.grade,
                "departement": d.departement,
                "volume_horaire": d.volume_horaire,
                "volume_consomme": d.volume_consomme,
                "volume_restant": d.volume_restant,
                "nb_surveillances": d.nb_surveillances,
            }
            for d in disponibles
        ],
    }


# ============================================================================
# DETAIL ENDPOINTS
# ============================================================================


@router.get("/{surveillance_id}/detail")
def get_surveillance_detail(
    surveillance_id: int,
    db: Session = Depends(get_db),
):
    """GET /surveillances/{surveillance_id}/detail"""
    service = SurvService(db)
    surveillance = service.get_surveillance_by_id(surveillance_id)

    if not surveillance:
        raise HTTPException(status_code=404, detail="Surveillance non trouvée")

    return {
        "id": surveillance.id,
        "planification_id": surveillance.planification_id,
        "enseignant_id": surveillance.enseignant_id,
        "charge": float(surveillance.charge),
        "presence": surveillance.presence,
        "mode_affectation": surveillance.mode_affectation,
        "statut_surveillance": surveillance.statut_surveillance,
        "est_externe": surveillance.est_externe,
        "motif_externe": surveillance.motif_externe,
        "created_at": surveillance.created_at.isoformat(),
        "updated_at": surveillance.updated_at.isoformat(),
    }


# ============================================================================
# MODIFICATION ENDPOINTS
# ============================================================================


@router.patch("/{surveillance_id}")
def update_surveillance(
    surveillance_id: int,
    payload: SurveillanceUpdate,
    db: Session = Depends(get_db),
):
    """PATCH /surveillances/{surveillance_id}"""
    service = SurvService(db)

    result = service.update_surveillance(surveillance_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Surveillance non trouvée")

    return {
        "id": result.id,
        "planification_id": result.planification_id,
        "enseignant_id": result.enseignant_id,
        "charge": float(result.charge),
        "statut_surveillance": result.statut_surveillance,
        "motif_externe": result.motif_externe,
        "updated_at": result.updated_at.isoformat(),
    }


@router.post("/{surveillance_id}/remplacer")
def replace_surveillance(
    surveillance_id: int,
    request: RemplacementRequest,
    db: Session = Depends(get_db),
):
    """POST /surveillances/{surveillance_id}/remplacer"""
    service = SurvService(db)

    try:
        old, new = service.replace_surveillance(
            surveillance_id,
            request.nouvel_enseignant_id,
            request.motif,
        )

        return {
            "ancienne_surveillance_id": old.id,
            "nouvelle_surveillance_id": new.id,
            "motif": request.motif,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# DELETION ENDPOINTS
# ============================================================================


@router.delete("/{surveillance_id}")
def delete_surveillance(
    surveillance_id: int,
    db: Session = Depends(get_db),
):
    """DELETE /surveillances/{surveillance_id}"""
    service = SurvService(db)

    if not service.delete_surveillance(surveillance_id):
        raise HTTPException(status_code=404, detail="Surveillance non trouvée")

    return {"message": "Surveillance supprimée avec succès"}


# ============================================================================
# RAPPORT & EXPORT ENDPOINTS
# ============================================================================


@router.get("/session/{session_id}/rapport")
def get_rapport_session(
    session_id: int,
    departement_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    GET /surveillances/session/{session_id}/rapport
    Générer un rapport complet d'affectation pour une session.
    """
    from app.models.salle_session import Session as SessionModel
    from app.models.planification_examen import PlanificationExamen
    from app.models.surveillance import Surveillance
    from app.models.enseignant import Enseignant, ChargeHoraire
    from app.models.salle_session import Creneau
    from app.models.section_matiere import SectionMatiere
    from app.models.matiere import Matiere
    from app.models.departement_niveau_section import Section

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    # Récupérer les planifications avec filtrage par département
    query = db.query(PlanificationExamen).filter(
        PlanificationExamen.session_id == session_id,
        PlanificationExamen.statut_planif == "VALIDEE",
    )
    
    if departement_id:
        query = query.filter(PlanificationExamen.departement_id == departement_id)
    
    planifications = query.all()

    # Récupérer toutes les surveillances de la session
    surv_query = db.query(Surveillance).join(PlanificationExamen).filter(
        PlanificationExamen.session_id == session_id,
        PlanificationExamen.statut_planif == "VALIDEE",
    )
    if departement_id:
        surv_query = surv_query.filter(PlanificationExamen.departement_id == departement_id)
    surveillances = surv_query.all()

    # ============================================================
    # 1. Détail des planifications
    # ============================================================
    planifications_detail = []
    planifications_en_conflit = []
    
    for planif in planifications:
        survs = [s for s in surveillances if s.planification_id == planif.id]
        
        section_matiere = db.query(SectionMatiere).filter(
            SectionMatiere.id == planif.section_matiere_id
        ).first()
        matiere = db.query(Matiere).filter(Matiere.id == section_matiere.matiere_id).first() if section_matiere else None
        creneau = db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
        section = db.query(Section).filter(Section.id == section_matiere.section_id).first() if section_matiere else None
        
        planif_data = {
            "planification_id": planif.id,
            "matiere_code": matiere.code if matiere else "N/A",
            "matiere_intitule": matiere.intitule if matiere else "N/A",
            "section_nom": section.nom if section else "N/A",
            "type_epreuve": planif.type_epreuve,
            "duree": planif.duree,
            "creneau": {
                "date": creneau.date.isoformat() if creneau else None,
                "heure_debut": str(creneau.heure_debut) if creneau else None,
                "heure_fin": str(creneau.heure_fin) if creneau else None,
            },
            "nb_surveillants_requis": planif.nb_surveillants_requis,
            "surveillants": [
                {
                    "enseignant_id": s.enseignant_id,
                    "nom": s.enseignant.nom,
                    "prenom": s.enseignant.prenom,
                    "grade": s.enseignant.grade,
                    "charge_imputee": float(s.charge),
                    "mode_affectation": s.mode_affectation,
                    "est_externe": s.est_externe,
                    "motif_externe": s.motif_externe,
                }
                for s in survs
            ],
        }
        
        planifications_detail.append(planif_data)
        
        if len(survs) < planif.nb_surveillants_requis:
            planifications_en_conflit.append({
                **planif_data,
                "surveillants_trouves": len(survs),
                "manquants": planif.nb_surveillants_requis - len(survs),
            })

    # ============================================================
    # 2. Classement des enseignants par charge cumulée
    # ============================================================
    enseignant_charges = {}
    for surv in surveillances:
        ens_id = surv.enseignant_id
        if ens_id not in enseignant_charges:
            charge_horaire = db.query(ChargeHoraire).filter(
                ChargeHoraire.enseignant_id == ens_id,
                ChargeHoraire.annee_univ == session.annee_universitaire,
            ).first()
            enseignant_charges[ens_id] = {
                "enseignant_id": ens_id,
                "nom": surv.enseignant.nom,
                "prenom": surv.enseignant.prenom,
                "grade": surv.enseignant.grade,
                "charge_totale": 0.0,
                "nb_surveillances": 0,
                "volume_horaire": charge_horaire.volume_horaire if charge_horaire else 0.0,
            }
        enseignant_charges[ens_id]["charge_totale"] += float(surv.charge)
        enseignant_charges[ens_id]["nb_surveillances"] += 1

    classement = []
    for data in enseignant_charges.values():
        taux_utilisation = (data["charge_totale"] / data["volume_horaire"] * 100) if data["volume_horaire"] > 0 else 0
        classement.append({
            "enseignant_id": data["enseignant_id"],
            "nom": data["nom"],
            "prenom": data["prenom"],
            "grade": data["grade"],
            "charge_totale": round(data["charge_totale"], 2),
            "nb_surveillances": data["nb_surveillances"],
            "taux_utilisation": round(taux_utilisation, 2),
        })
    
    classement.sort(key=lambda x: x["charge_totale"], reverse=True)

    # ============================================================
    # 3. Statistiques
    # ============================================================
    total_planifs = len(planifications)
    total_completes = sum(1 for p in planifications_detail if len(p["surveillants"]) >= p["nb_surveillants_requis"])
    total_partielles = sum(1 for p in planifications_detail if 0 < len(p["surveillants"]) < p["nb_surveillants_requis"])
    total_non_affectees = sum(1 for p in planifications_detail if len(p["surveillants"]) == 0)

    return {
        "session": {
            "id": session.id,
            "type_session": session.type_session,
            "annee_univ": session.annee_universitaire,
            "date_debut": session.date_debut.isoformat(),
            "date_fin": session.date_fin.isoformat(),
            "statut": session.statut,
        },
        "statistiques": {
            "total_planifications": total_planifs,
            "completes": total_completes,
            "partielles": total_partielles,
            "non_affectees": total_non_affectees,
        },
        "planifications": planifications_detail,
        "en_conflit": planifications_en_conflit,
        "classement_enseignants": classement,
        "date_generation": datetime.now().isoformat(),
    }


@router.get("/session/{session_id}/export")
def export_session(
    session_id: int,
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: Session = Depends(get_db),
):
    """GET /surveillances/session/{session_id}/export"""
    service = SurvService(db)
    surveillances = service.get_all_surveillances(session_id=session_id, limit=10000)

    if format == "csv":
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["ID", "Planification", "Enseignant", "Charge", "Mode", "Statut", "Externe", "Motif"],
        )
        writer.writeheader()

        for s in surveillances:
            writer.writerow({
                "ID": s.id,
                "Planification": s.planification_id,
                "Enseignant": s.enseignant_id,
                "Charge": f"{s.charge:.2f}",
                "Mode": s.mode_affectation,
                "Statut": s.statut_surveillance,
                "Externe": "Oui" if s.est_externe else "Non",
                "Motif": s.motif_externe or "",
            })

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=surveillances.csv"},
        )
    else:
        raise HTTPException(status_code=501, detail="Format XLSX non implémenté")


@router.get("/statistiques", response_model=StatistiquesResponse)
def get_statistiques(
    annee_univ: str = Query(..., description="Année universitaire"),
    db: Session = Depends(get_db),
):
    """GET /surveillances/statistiques"""
    from app.models.surveillance import Surveillance
    from app.models.planification_examen import PlanificationExamen
    from app.models.salle_session import Session as SessionModel
    from sqlalchemy import func

    stats = db.query(
        func.count(Surveillance.id).label("total_surveillances"),
        func.sum(Surveillance.charge).label("total_heures"),
        func.count(func.distinct(Surveillance.enseignant_id)).label("unique_enseignants"),
        func.sum(func.cast(Surveillance.est_externe, db.Integer)).label("count_externes"),
    ).join(PlanificationExamen).join(SessionModel).filter(
        SessionModel.annee_universitaire == annee_univ,
    ).first()

    total_requis = db.query(func.sum(PlanificationExamen.nb_surveillants_requis)).join(
        SessionModel
    ).filter(
        SessionModel.annee_universitaire == annee_univ,
        PlanificationExamen.statut_planif == "VALIDEE",
    ).scalar() or 0

    total = stats.total_surveillances or 0
    externes = stats.count_externes or 0
    taux_remplissage = (total / total_requis * 100) if total_requis > 0 else 0

    return StatistiquesResponse(
        annee_universitaire=annee_univ,
        total_surveillances=total,
        total_heures=float(stats.total_heures or 0),
        unique_enseignants=stats.unique_enseignants or 0,
        count_externes=externes,
        taux_externe=(externes / total * 100) if total > 0 else 0,
        taux_remplissage=round(taux_remplissage, 2),
    )


@router.get("/session/{session_id}/conflits")
def get_session_conflits(
    session_id: int,
    db: Session = Depends(get_db),
):
    """
    GET /surveillances/session/{session_id}/conflits
    Retourne la liste des planifications en conflit non résolues pour une session.
    """
    from app.models.planification_examen import PlanificationExamen
    from app.models.surveillance import Surveillance
    from app.models.salle_session import Creneau

    planifications = db.query(PlanificationExamen).filter(
        PlanificationExamen.session_id == session_id,
        PlanificationExamen.statut_planif == "VALIDEE",
    ).all()

    conflits = []
    for planif in planifications:
        nb_affectees = db.query(Surveillance).filter(
            Surveillance.planification_id == planif.id,
            Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
        ).count()

        if nb_affectees < planif.nb_surveillants_requis:
            creneau = db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
            
            conflits.append({
                "planification_id": planif.id,
                "type_epreuve": planif.type_epreuve,
                "creneau": {
                    "date": creneau.date.isoformat() if creneau else None,
                    "heure_debut": str(creneau.heure_debut) if creneau else None,
                    "heure_fin": str(creneau.heure_fin) if creneau else None,
                },
                "surveillants_requis": planif.nb_surveillants_requis,
                "surveillants_trouves": nb_affectees,
                "manquants": planif.nb_surveillants_requis - nb_affectees,
                "statut_resolution": "NON_RESOLU",
            })

    return {
        "session_id": session_id,
        "total_conflits": len(conflits),
        "conflits": conflits,
    }


# ============================================================================
# HELPER ENDPOINTS
# ============================================================================


@router.get("/enseignant/{enseignant_id}/disponibilites", response_model=GetDisponibilitesResponse)
def get_enseignant_disponibilites(
    enseignant_id: int,
    date_debut: str = Query(..., description="Date de début (YYYY-MM-DD)"),
    date_fin: str = Query(..., description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """GET /surveillances/enseignant/{enseignant_id}/disponibilites"""
    from app.models.disponibilite import DisponibiliteEnseignant
    from datetime import datetime as dt

    try:
        start_date = dt.strptime(date_debut, "%Y-%m-%d").date()
        end_date = dt.strptime(date_fin, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")

    disponibilites = db.query(DisponibiliteEnseignant).filter(
        DisponibiliteEnseignant.enseignant_id == enseignant_id,
        DisponibiliteEnseignant.date >= start_date,
        DisponibiliteEnseignant.date <= end_date,
    ).all()

    disponibilites_list = []
    for d in disponibilites:
        disponibilites_list.append(
            DisponibiliteItem(
                date=d.date.isoformat(),
                heure_debut=str(d.heure_debut),
                heure_fin=str(d.heure_fin),
                type=d.type_dispo,
                motif=d.motif,
            )
        )

    return GetDisponibilitesResponse(
        enseignant_id=enseignant_id,
        date_debut=date_debut,
        date_fin=date_fin,
        disponibilites=disponibilites_list,
    )