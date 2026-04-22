# """
# Gradio draft for testing surveillance algorithm interactively.

# Run with:
#     python -m gradio app/gradio_surveillance_draft.py

# Or programmatically:
#     import gradio as gr
#     from app.gradio_surveillance_draft import create_interface
#     interface = create_interface()
#     interface.launch()
# """

# import gradio as gr
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# # Database connection
# DATABASE_URL = "postgresql://user:password@localhost/exam_planning_db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def get_db():
#     """Get database session."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # ============================================================================
# # TEST FUNCTIONS
# # ============================================================================


# def test_affectation_automatique(session_id: int):
#     """Test automatic affectation for a session."""
#     db = SessionLocal()
#     try:
#         from app.services.surv_service import SurvService
        
#         service = SurvService(db)
#         results, message = service.affecter_session_automatique(session_id)
        
#         # Compter les résultats
#         affectees = sum(1 for r in results if r.statut == "AFFECTEE")
#         conflits = sum(1 for r in results if r.statut == "CONFLIT")
        
#         output = f"""
# ## Résultat Affectation Automatique
# - Session ID: {session_id}
# - Total planifications: {len(results)}
# - Affectées: {affectees} ✓
# - En conflit: {conflits} ✗

# ### Message
# {message}

# ### Détail par Planification
# """
        
#         for r in results:
#             if r.statut == "AFFECTEE":
#                 output += f"\n✓ **Planif {r.planification_id}**: AFFECTÉE ({len(r.surveillants_affectes)} surveillants)"
#             else:
#                 output += f"\n✗ **Planif {r.planification_id}**: CONFLIT ({r.manquants} manquants)"
#                 if r.violations:
#                     output += f"\n   Raisons d'exclusion:"
#                     for v in r.violations:
#                         output += f"\n   - {v.nom} {v.prenom}: {v.raison.value}"
        
#         return output
#     except Exception as e:
#         return f"❌ Erreur: {str(e)}"
#     finally:
#         db.close()


# def test_enseignants_disponibles(planif_id: int):
#     """Test getting available enseignants for a planification."""
#     db = SessionLocal()
#     try:
#         from app.services.surv_service import SurvService
        
#         service = SurvService(db)
#         disponibles = service.get_enseignants_disponibles_pour_planification(planif_id)
        
#         output = f"""
# ## Enseignants Disponibles pour Planif {planif_id}
# Total: {len(disponibles)}

# ### Liste (triée par volume restant)
# """
        
#         for d in disponibles:
#             dept = d.departement.get("code", "?")
#             output += f"""
# - **{d.prenom} {d.nom}** ({d.grade})
#   - Département: {dept}
#   - Volume restant: {d.volume_restant:.2f}h / {d.volume_horaire:.2f}h
#   - Surveillances: {d.nb_surveillances}
# """
        
#         return output
#     except Exception as e:
#         return f"❌ Erreur: {str(e)}"
#     finally:
#         db.close()


# def test_volume_enseignant(enseignant_id: int, annee_univ: str):
#     """Test volume information for an enseignant."""
#     db = SessionLocal()
#     try:
#         from app.services.surv_service import SurvService
        
#         service = SurvService(db)
#         volume_info = service.get_volume_restant_enseignant(enseignant_id, annee_univ)
        
#         output = f"""
# ## Volume Enseignant {enseignant_id}
# Année: {annee_univ}

# ### Détails
# - Volume horaire: **{volume_info['volume_horaire']:.2f}h**
# - Volume consommé: **{volume_info['volume_consomme']:.2f}h**
# - Volume restant: **{volume_info['volume_restant']:.2f}h**
# - Nombre de surveillances: **{volume_info['nb_surveillances']}**

# ### Taux d'utilisation
# {(volume_info['volume_consomme'] / volume_info['volume_horaire'] * 100) if volume_info['volume_horaire'] > 0 else 0:.1f}%
# """
        
#         return output
#     except Exception as e:
#         return f"❌ Erreur: {str(e)}"
#     finally:
#         db.close()


# def test_statistiques_session(session_id: int):
#     """Test getting statistics for a session."""
#     db = SessionLocal()
#     try:
#         from app.services.surv_service import SurvService
#         from app.models.session import Session as SessionModel
        
#         session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
#         if not session:
#             return f"❌ Session {session_id} non trouvée"
        
#         service = SurvService(db)
#         surveillances = service.get_all_surveillances(session_id=session_id, limit=10000)
        
#         affectees_auto = sum(1 for s in surveillances if s.mode_affectation == "AUTOMATIQUE")
#         affectees_manuelles = sum(1 for s in surveillances if s.mode_affectation == "MANUELLE")
#         externes = sum(1 for s in surveillances if s.est_externe)
#         total_charge = sum(float(s.charge) for s in surveillances)
        
#         output = f"""
# ## Statistiques Session {session_id}
# Année: {session.annee_universitaire}

# ### Affectations
# - Automatiques: **{affectees_auto}**
# - Manuelles: **{affectees_manuelles}**
# - Total: **{len(surveillances)}**

# ### Externes
# - Enseignants externes: **{externes}**
# - Taux: **{(externes / len(surveillances) * 100) if surveillances else 0:.1f}%**

# ### Charge
# - Total heures: **{total_charge:.2f}h**
# - Moyenne par surveillance: **{(total_charge / len(surveillances)) if surveillances else 0:.2f}h**
# """
        
#         return output
#     except Exception as e:
#         return f"❌ Erreur: {str(e)}"
#     finally:
#         db.close()


# def test_remplacement(surveillance_id: int, nouvel_enseignant_id: int, motif: str):
#     """Test replacing an enseignant on a surveillance."""
#     db = SessionLocal()
#     try:
#         from app.services.surv_service import SurvService
        
#         service = SurvService(db)
#         old, new = service.replace_surveillance(
#             surveillance_id,
#             nouvel_enseignant_id,
#             motif,
#         )
        
#         output = f"""
# ## Remplacement Effectué
# - Ancienne surveillance: {old.id}
# - Nouvelle surveillance: {new.id}
# - Motif: {motif}

# ### Ancien Enseignant
# - ID: {old.enseignant_id}
# - Charge: {old.charge}h

# ### Nouvel Enseignant
# - ID: {new.enseignant_id}
# - Charge: {new.charge}h
# """
        
#         return output
#     except Exception as e:
#         return f"❌ Erreur: {str(e)}"
#     finally:
#         db.close()


# # ============================================================================
# # GRADIO INTERFACE
# # ============================================================================


# def create_interface():
#     """Create Gradio interface for surveillance testing."""
    
#     with gr.Blocks(title="Surveillance Testing") as interface:
#         gr.Markdown("# 🎓 Surveillance Affectation Testing")
#         gr.Markdown("""
#         Interface de test pour le module Surveillance du système de gestion des examens.
        
#         Testez les différentes fonctionnalités:
#         - Affectation automatique
#         - Enseignants disponibles
#         - Volumes horaires
#         - Statistiques
#         - Remplacement
#         """)
        
#         # ====================================================================
#         # TAB 1: Automatic Affectation
#         # ====================================================================
        
#         with gr.Tab("Affectation Automatique"):
#             gr.Markdown("## Test d'Affectation Automatique")
            
#             session_id_input = gr.Number(
#                 label="Session ID",
#                 value=1,
#                 precision=0,
#             )
#             test_auto_btn = gr.Button("Lancer Affectation Automatique", variant="primary")
#             auto_output = gr.Markdown()
            
#             test_auto_btn.click(
#                 fn=test_affectation_automatique,
#                 inputs=session_id_input,
#                 outputs=auto_output,
#             )
        
#         # ====================================================================
#         # TAB 2: Available Enseignants
#         # ====================================================================
        
#         with gr.Tab("Enseignants Disponibles"):
#             gr.Markdown("## Enseignants Disponibles pour Planification")
            
#             planif_id_input = gr.Number(
#                 label="Planification ID",
#                 value=1,
#                 precision=0,
#             )
#             test_disp_btn = gr.Button("Récupérer Disponibles")
#             disp_output = gr.Markdown()
            
#             test_disp_btn.click(
#                 fn=test_enseignants_disponibles,
#                 inputs=planif_id_input,
#                 outputs=disp_output,
#             )
        
#         # ====================================================================
#         # TAB 3: Volume Info
#         # ====================================================================
        
#         with gr.Tab("Volume Enseignant"):
#             gr.Markdown("## Information Volume Horaire")
            
#             with gr.Row():
#                 ens_id_input = gr.Number(
#                     label="Enseignant ID",
#                     value=1,
#                     precision=0,
#                 )
#                 annee_input = gr.Textbox(
#                     label="Année Universitaire",
#                     value="2025/2026",
#                 )
            
#             test_vol_btn = gr.Button("Récupérer Volume")
#             vol_output = gr.Markdown()
            
#             test_vol_btn.click(
#                 fn=test_volume_enseignant,
#                 inputs=[ens_id_input, annee_input],
#                 outputs=vol_output,
#             )
        
#         # ====================================================================
#         # TAB 4: Session Statistics
#         # ====================================================================
        
#         with gr.Tab("Statistiques Session"):
#             gr.Markdown("## Statistiques d'une Session")
            
#             session_stat_input = gr.Number(
#                 label="Session ID",
#                 value=1,
#                 precision=0,
#             )
#             test_stat_btn = gr.Button("Récupérer Statistiques")
#             stat_output = gr.Markdown()
            
#             test_stat_btn.click(
#                 fn=test_statistiques_session,
#                 inputs=session_stat_input,
#                 outputs=stat_output,
#             )
        
#         # ====================================================================
#         # TAB 5: Replacement
#         # ====================================================================
        
#         with gr.Tab("Remplacement"):
#             gr.Markdown("## Remplacer un Enseignant sur Surveillance")
            
#             with gr.Row():
#                 surv_id_input = gr.Number(
#                     label="Surveillance ID",
#                     value=1,
#                     precision=0,
#                 )
#                 new_ens_input = gr.Number(
#                     label="Nouvel Enseignant ID",
#                     value=2,
#                     precision=0,
#                 )
            
#             motif_input = gr.Textbox(
#                 label="Motif du Remplacement",
#                 value="Enseignant indisponible",
#             )
            
#             test_repl_btn = gr.Button("Effectuer Remplacement")
#             repl_output = gr.Markdown()
            
#             test_repl_btn.click(
#                 fn=test_remplacement,
#                 inputs=[surv_id_input, new_ens_input, motif_input],
#                 outputs=repl_output,
#             )
        
#         # ====================================================================
#         # INFO
#         # ====================================================================
        
#         with gr.Tab("À Propos"):
#             gr.Markdown("""
#             # À Propos du Module Surveillance
            
#             ## Architecture
            
#             - **Models**: ORM Surveillance avec champs `est_externe` et `motif_externe`
#             - **Schemas**: Pydantic pour validation API
#             - **CRUD**: Opérations base de données
#             - **Services**: Logique métier
#             - **Algorithms**: Algorithme d'affectation automatique
#             - **Routers**: Endpoints FastAPI
            
#             ## 5 Contraintes
            
#             1. **Disponibilité Temporelle** (HARD): Enseignant doit être libre le créneau
#             2. **Conflit Matière** (SOFT/Auto, Ignorée/Manuel): Ne pas surveiller sa matière
#             3. **Volume Horaire** (HARD/Auto, Ignorée/Manuel): Respecter volume annuel ±0.05%
#             4. **Non-Simultanéité** (HARD): Un seul examen par créneau par enseignant
#             5. **Département** (HARD/Auto, Ignorée/Manuel): Même département en auto
            
#             ## Modes d'Affectation
            
#             - **Automatique**: Algorithme applique les 5 contraintes (sauf Conflit matière en dernier recours)
#             - **Manuel Total**: Responsable affecte manuellement (Contraintes 1 et 4 uniquement)
#             - **Manuel Partiel**: Résoudre un conflit après automatique
            
#             ## Volume Horaire
            
#             Calculé **uniquement** sur l'année universitaire de la session:
            
#             ```
#             volume_restant = volume_horaire - SUM(charge AFFECTE/CONFIRME
#                                             WHERE annee_universitaire = session.annee)
#             ```
            
#             ## Traçabilité Externe
            
#             - `est_externe = TRUE` → Enseignant d'un autre département
#             - `motif_externe` → Raison du recours (ex: "Manque de personnel")
            
#             ## Notes d'Implémentation
            
#             - Suppression physique (pas de soft delete)
#             - Persistance immédiate en automatique
#             - Non-blocage: Un conflit n'arrête pas la suite
#             - Transaction par planification en auto
#             - Transaction globale en manuel batch
#             """)
    
#     return interface


# if __name__ == "__main__":
#     interface = create_interface()
#     interface.launch(
#         server_name="0.0.0.0",
#         server_port=7862,
#         share=False,
#         debug=True,
#     )


import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Gradio draft for testing surveillance algorithm interactively.

Run with:
    python -m gradio app/gradio_surveillance_draft.py
"""

import gradio as gr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import json

# Database connection
DATABASE_URL="postgresql://postgres:root001727@localhost:5432/PFA"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# API base URL (ajustez selon votre configuration)
API_BASE_URL = "http://localhost:8000"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_affectation_automatique(session_id: int):
    """Test automatic affectation for a session."""
    db = SessionLocal()
    try:
        from app.services.surv_service import SurvService
        
        service = SurvService(db)
        results, message = service.affecter_session_automatique(session_id)
        
        affectees = sum(1 for r in results if r.statut == "AFFECTEE")
        conflits = sum(1 for r in results if r.statut == "CONFLIT")
        
        output = f"""
## Résultat Affectation Automatique
- Session ID: {session_id}
- Total planifications: {len(results)}
- Affectées: {affectees} ✓
- En conflit: {conflits} ✗

### Message
{message}

### Détail par Planification
"""
        
        for r in results:
            if r.statut == "AFFECTEE":
                output += f"\n✓ **Planif {r.planification_id}**: AFFECTÉE ({len(r.surveillants_affectes)} surveillants)"
            else:
                output += f"\n✗ **Planif {r.planification_id}**: CONFLIT ({r.manquants} manquants)"
                if r.violations:
                    output += f"\n   Raisons d'exclusion:"
                    for v in r.violations:
                        output += f"\n   - {v.nom} {v.prenom}: {v.raison.value}"
        
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


def test_enseignants_disponibles(planif_id: int):
    """Test getting available enseignants for a planification."""
    db = SessionLocal()
    try:
        from app.services.surv_service import SurvService
        
        service = SurvService(db)
        disponibles = service.get_enseignants_disponibles_pour_planification(planif_id)
        
        output = f"""
## Enseignants Disponibles pour Planif {planif_id}
Total: {len(disponibles)}

### Liste (triée par volume restant)
"""
        
        for d in disponibles:
            dept = d.departement.get("code", "?")
            output += f"""
- **{d.prenom} {d.nom}** ({d.grade})
  - Département: {dept}
  - Volume restant: {d.volume_restant:.2f}h / {d.volume_horaire:.2f}h
  - Surveillances: {d.nb_surveillances}
"""
        
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


def test_volume_enseignant(enseignant_id: int, annee_univ: str):
    """Test volume information for an enseignant."""
    db = SessionLocal()
    try:
        from app.services.surv_service import SurvService
        
        service = SurvService(db)
        volume_info = service.get_volume_restant_enseignant(enseignant_id, annee_univ)
        
        output = f"""
## Volume Enseignant {enseignant_id}
Année: {annee_univ}

### Détails
- Volume horaire: **{volume_info['volume_horaire']:.2f}h**
- Volume consommé: **{volume_info['volume_consomme']:.2f}h**
- Volume restant: **{volume_info['volume_restant']:.2f}h**
- Nombre de surveillances: **{volume_info['nb_surveillances']}**

### Taux d'utilisation
{(volume_info['volume_consomme'] / volume_info['volume_horaire'] * 100) if volume_info['volume_horaire'] > 0 else 0:.1f}%
"""
        
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


def test_statistiques_session(session_id: int):
    """Test getting statistics for a session."""
    db = SessionLocal()
    try:
        from app.services.surv_service import SurvService
        from app.models.salle_session import Session as SessionModel
        
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return f"❌ Session {session_id} non trouvée"
        
        service = SurvService(db)
        surveillances = service.get_all_surveillances(session_id=session_id, limit=10000)
        
        affectees_auto = sum(1 for s in surveillances if s.mode_affectation == "AUTOMATIQUE")
        affectees_manuelles = sum(1 for s in surveillances if s.mode_affectation == "MANUELLE")
        externes = sum(1 for s in surveillances if s.est_externe)
        total_charge = sum(float(s.charge) for s in surveillances)
        
        output = f"""
## Statistiques Session {session_id}
Année: {session.annee_universitaire}

### Affectations
- Automatiques: **{affectees_auto}**
- Manuelles: **{affectees_manuelles}**
- Total: **{len(surveillances)}**

### Externes
- Enseignants externes: **{externes}**
- Taux: **{(externes / len(surveillances) * 100) if surveillances else 0:.1f}%**

### Charge
- Total heures: **{total_charge:.2f}h**
- Moyenne par surveillance: **{(total_charge / len(surveillances)) if surveillances else 0:.2f}h**
"""
        
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


def test_remplacement(surveillance_id: int, nouvel_enseignant_id: int, motif: str):
    """Test replacing an enseignant on a surveillance."""
    db = SessionLocal()
    try:
        from app.services.surv_service import SurvService
        
        service = SurvService(db)
        old, new = service.replace_surveillance(
            surveillance_id,
            nouvel_enseignant_id,
            motif,
        )
        
        output = f"""
## Remplacement Effectué
- Ancienne surveillance: {old.id}
- Nouvelle surveillance: {new.id}
- Motif: {motif}

### Ancien Enseignant
- ID: {old.enseignant_id}
- Charge: {old.charge}h

### Nouvel Enseignant
- ID: {new.enseignant_id}
- Charge: {new.charge}h
"""
        
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


# ============================================================================
# NOUVEAUX TESTS
# ============================================================================

def test_conflits_session(session_id: int):
    """Test GET /surveillances/session/{session_id}/conflits"""
    db = SessionLocal()
    try:
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
                    "surveillants_requis": planif.nb_surveillants_requis,
                    "surveillants_trouves": nb_affectees,
                    "manquants": planif.nb_surveillants_requis - nb_affectees,
                    "creneau": f"{creneau.date} {creneau.heure_debut}" if creneau else "N/A",
                })
        
        if not conflits:
            return f"✅ Session {session_id} : Aucun conflit détecté !"
        
        output = f"""
## Conflits Session {session_id}
Total: {len(conflits)} conflit(s)

### Liste des conflits
"""
        for c in conflits:
            output += f"""
- **Planif {c['planification_id']}** ({c['creneau']})
  - Requis: {c['surveillants_requis']}
  - Trouvés: {c['surveillants_trouves']}
  - Manquants: {c['manquants']}
"""
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


def test_rapport_session(session_id: int, departement_id: int = None):
    """Test GET /surveillances/session/{session_id}/rapport"""
    db = SessionLocal()
    try:
        from app.services.surv_service import SurvService
        
        service = SurvService(db)
        
        # Appeler le service pour obtenir le rapport (simulé)
        from app.models.salle_session import Session as SessionModel
        from app.models.planification_examen import PlanificationExamen
        from app.models.surveillance import Surveillance
        
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return f"❌ Session {session_id} non trouvée"
        
        query = db.query(PlanificationExamen).filter(
            PlanificationExamen.session_id == session_id,
            PlanificationExamen.statut_planif == "VALIDEE",
        )
        if departement_id:
            query = query.filter(PlanificationExamen.departement_id == departement_id)
        planifications = query.all()
        
        surveillances = db.query(Surveillance).join(PlanificationExamen).filter(
            PlanificationExamen.session_id == session_id,
        )
        if departement_id:
            surveillances = surveillances.filter(PlanificationExamen.departement_id == departement_id)
        surveillances = surveillances.all()
        
        output = f"""
## Rapport Session {session_id}
Année: {session.annee_universitaire}
Département filtre: {departement_id if departement_id else "Tous"}

### Statistiques
- Total planifications: {len(planifications)}
- Total surveillances: {len(surveillances)}
- Externes: {sum(1 for s in surveillances if s.est_externe)}

### Planifications
"""
        for p in planifications:
            survs = [s for s in surveillances if s.planification_id == p.id]
            output += f"\n- **Planif {p.id}**: {len(survs)}/{p.nb_surveillants_requis} surveillants"
            if len(survs) < p.nb_surveillants_requis:
                output += f" ⚠️ CONFLIT ({p.nb_surveillants_requis - len(survs)} manquants)"
        
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


def test_statistiques_globales(annee_univ: str):
    """Test GET /surveillances/statistiques"""
    db = SessionLocal()
    try:
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
        
        output = f"""
## Statistiques Globales {annee_univ}

### Volume
- Total surveillances: **{total}**
- Total heures: **{float(stats.total_heures or 0):.2f}h**
- Enseignants uniques: **{stats.unique_enseignants or 0}**

### Taux
- Taux remplissage: **{taux_remplissage:.2f}%**
- Taux externe: **{(externes / total * 100) if total > 0 else 0:.2f}%**
- Externes: **{externes}**

### Requis
- Places requises: **{total_requis}**
"""
        return output
    except Exception as e:
        return f"❌ Erreur: {str(e)}"
    finally:
        db.close()


def test_affectation_manuelle(session_id: int, planification_id: int, enseignant_ids: str, motifs: str):
    """Test POST /surveillances/manual-assignment"""
    try:
        ids = [int(x.strip()) for x in enseignant_ids.split(",")]
        
        payload = {
            "session_id": session_id,
            "planification_id": planification_id,
            "enseignant_ids": ids,
            "motifs_externes": {}
        }
        
        # Traiter les motifs
        if motifs:
            for i, ens_id in enumerate(ids):
                payload["motifs_externes"][ens_id] = motifs if "," not in motifs else motifs.split(",")[i] if i < len(motifs.split(",")) else None
        
        response = requests.post(
            f"{API_BASE_URL}/surveillances/manual-assignment",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return f"""
## ✅ Affectation manuelle réussie !
- Planification: {data['planification_id']}
- Statut: {data['statut']}
- Surveillants insérés: {data['surveillants_inseres']}
"""
        else:
            return f"❌ Erreur {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_interface():
    """Create Gradio interface for surveillance testing."""
    
    with gr.Blocks(title="Surveillance Testing", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🎓 Surveillance Affectation Testing")
        gr.Markdown("""
        Interface de test pour le module Surveillance du système de gestion des examens.
        
        Testez les différentes fonctionnalités:
        - Affectation automatique
        - Enseignants disponibles
        - Volumes horaires
        - Statistiques
        - Remplacement
        - **Conflits** (NOUVEAU)
        - **Rapport complet** (NOUVEAU)
        - **Statistiques globales** (NOUVEAU)
        - **Affectation manuelle** (NOUVEAU)
        """)
        
        # ====================================================================
        # TAB 1: Automatic Affectation
        # ====================================================================
        
        with gr.Tab("Affectation Automatique"):
            gr.Markdown("## Test d'Affectation Automatique")
            session_id_input = gr.Number(label="Session ID", value=1, precision=0)
            test_auto_btn = gr.Button("Lancer Affectation Automatique", variant="primary")
            auto_output = gr.Markdown()
            test_auto_btn.click(fn=test_affectation_automatique, inputs=session_id_input, outputs=auto_output)
        
        # ====================================================================
        # TAB 2: Available Enseignants
        # ====================================================================
        
        with gr.Tab("Enseignants Disponibles"):
            gr.Markdown("## Enseignants Disponibles pour Planification")
            planif_id_input = gr.Number(label="Planification ID", value=1, precision=0)
            test_disp_btn = gr.Button("Récupérer Disponibles")
            disp_output = gr.Markdown()
            test_disp_btn.click(fn=test_enseignants_disponibles, inputs=planif_id_input, outputs=disp_output)
        
        # ====================================================================
        # TAB 3: Volume Info
        # ====================================================================
        
        with gr.Tab("Volume Enseignant"):
            gr.Markdown("## Information Volume Horaire")
            with gr.Row():
                ens_id_input = gr.Number(label="Enseignant ID", value=1, precision=0)
                annee_input = gr.Textbox(label="Année Universitaire", value="2025/2026")
            test_vol_btn = gr.Button("Récupérer Volume")
            vol_output = gr.Markdown()
            test_vol_btn.click(fn=test_volume_enseignant, inputs=[ens_id_input, annee_input], outputs=vol_output)
        
        # ====================================================================
        # TAB 4: Session Statistics
        # ====================================================================
        
        with gr.Tab("Statistiques Session"):
            gr.Markdown("## Statistiques d'une Session")
            session_stat_input = gr.Number(label="Session ID", value=1, precision=0)
            test_stat_btn = gr.Button("Récupérer Statistiques")
            stat_output = gr.Markdown()
            test_stat_btn.click(fn=test_statistiques_session, inputs=session_stat_input, outputs=stat_output)
        
        # ====================================================================
        # TAB 5: Replacement
        # ====================================================================
        
        with gr.Tab("Remplacement"):
            gr.Markdown("## Remplacer un Enseignant sur Surveillance")
            with gr.Row():
                surv_id_input = gr.Number(label="Surveillance ID", value=1, precision=0)
                new_ens_input = gr.Number(label="Nouvel Enseignant ID", value=2, precision=0)
            motif_input = gr.Textbox(label="Motif du Remplacement", value="Enseignant indisponible")
            test_repl_btn = gr.Button("Effectuer Remplacement")
            repl_output = gr.Markdown()
            test_repl_btn.click(fn=test_remplacement, inputs=[surv_id_input, new_ens_input, motif_input], outputs=repl_output)
        
        # ====================================================================
        # TAB 6: Conflits (NOUVEAU)
        # ====================================================================
        
        with gr.Tab("Conflits Session"):
            gr.Markdown("## Lister les Planifications en Conflit")
            conflit_session_input = gr.Number(label="Session ID", value=1, precision=0)
            test_conflit_btn = gr.Button("Lister Conflits", variant="secondary")
            conflit_output = gr.Markdown()
            test_conflit_btn.click(fn=test_conflits_session, inputs=conflit_session_input, outputs=conflit_output)
        
        # ====================================================================
        # TAB 7: Rapport Session (NOUVEAU)
        # ====================================================================
        
        with gr.Tab("Rapport Session"):
            gr.Markdown("## Rapport Complet d'une Session")
            with gr.Row():
                rapport_session_input = gr.Number(label="Session ID", value=1, precision=0)
                dept_filter_input = gr.Number(label="Département ID (optionnel)", value=None, precision=0)
            test_rapport_btn = gr.Button("Générer Rapport", variant="secondary")
            rapport_output = gr.Markdown()
            test_rapport_btn.click(fn=test_rapport_session, inputs=[rapport_session_input, dept_filter_input], outputs=rapport_output)
        
        # ====================================================================
        # TAB 8: Statistiques Globales (NOUVEAU)
        # ====================================================================
        
        with gr.Tab("Statistiques Globales"):
            gr.Markdown("## Statistiques Globales par Année Universitaire")
            annee_globale_input = gr.Textbox(label="Année Universitaire", value="2025/2026")
            test_globale_btn = gr.Button("Calculer Statistiques", variant="secondary")
            globale_output = gr.Markdown()
            test_globale_btn.click(fn=test_statistiques_globales, inputs=annee_globale_input, outputs=globale_output)
        
        # ====================================================================
        # TAB 9: Affectation Manuelle (NOUVEAU)
        # ====================================================================
        
        with gr.Tab("Affectation Manuelle"):
            gr.Markdown("## Affectation Manuelle (Résolution de Conflit)")
            with gr.Row():
                manuelle_session_input = gr.Number(label="Session ID", value=1, precision=0)
                manuelle_planif_input = gr.Number(label="Planification ID", value=1, precision=0)
            with gr.Row():
                manuelle_ens_input = gr.Textbox(label="IDs des enseignants (séparés par virgules)", value="55,23")
                manuelle_motif_input = gr.Textbox(label="Motif externe (optionnel)", value="Manque de personnel")
            test_manuelle_btn = gr.Button("Valider Affectation Manuelle", variant="primary")
            manuelle_output = gr.Markdown()
            test_manuelle_btn.click(
                fn=test_affectation_manuelle,
                inputs=[manuelle_session_input, manuelle_planif_input, manuelle_ens_input, manuelle_motif_input],
                outputs=manuelle_output
            )
        
        # ====================================================================
        # INFO
        # ====================================================================
        
        with gr.Tab("À Propos"):
            gr.Markdown("""
            # À Propos du Module Surveillance
            
            ## Architecture
            
            - **Models**: ORM Surveillance avec champs `est_externe` et `motif_externe`
            - **Schemas**: Pydantic pour validation API
            - **CRUD**: Opérations base de données
            - **Services**: Logique métier
            - **Algorithms**: Algorithme d'affectation automatique
            - **Routers**: Endpoints FastAPI
            
            ## 5 Contraintes
            
            1. **Disponibilité Temporelle** (HARD): Enseignant doit être libre le créneau
            2. **Conflit Matière** (SOFT/Auto, Ignorée/Manuel): Ne pas surveiller sa matière
            3. **Volume Horaire** (HARD/Auto, Ignorée/Manuel): Respecter volume annuel ±0.05%
            4. **Non-Simultanéité** (HARD): Un seul examen par créneau par enseignant
            5. **Département** (HARD/Auto, Ignorée/Manuel): Même département en auto
            
            ## Endpoints Disponibles
            
            | Méthode | Endpoint | Description |
            |---------|----------|-------------|
            | POST | `/surveillances/affecter-session` | Affectation automatique |
            | POST | `/surveillances/manual-assignment` | Affectation manuelle (1 planif) |
            | POST | `/surveillances/manual-assignment-batch` | Affectation manuelle (batch) |
            | GET | `/surveillances/{session_id}` | Surveillances d'une session |
            | GET | `/surveillances/getallsurveillants` | Tous les enseignants |
            | GET | `/surveillances/disponibles/{planif_id}` | Enseignants disponibles |
            | GET | `/surveillances/session/{session_id}/rapport` | Rapport complet |
            | GET | `/surveillances/session/{session_id}/conflits` | Conflits non résolus |
            | GET | `/surveillances/statistiques` | Statistiques globales |
            | PATCH | `/surveillances/{surveillance_id}` | Modifier surveillance |
            | DELETE | `/surveillances/{surveillance_id}` | Supprimer surveillance |
            | POST | `/surveillances/{surveillance_id}/remplacer` | Remplacer enseignant |
            
            ## Notes d'Implémentation
            
            - Suppression physique (pas de soft delete)
            - Persistance immédiate en automatique
            - Non-blocage: Un conflit n'arrête pas la suite
            - Transaction par planification en auto
            - Transaction globale en manuel batch
            """)
    
    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=True,
    )