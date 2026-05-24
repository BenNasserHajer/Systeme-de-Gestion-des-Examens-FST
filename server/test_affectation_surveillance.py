"""Test de l'affectation automatique des surveillants"""

import sys
import io
# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.surv_service import SurvService

def test_affectation():
    db: Session = SessionLocal()
    try:
        service = SurvService(db)
        
        # Test avec session_id = 1
        print("=" * 60)
        print("TEST AFFECTATION AUTOMATIQUE")
        print("=" * 60)
        print("Session ID: 1")
        print("Section: Toutes")
        print("Période: Toutes")
        print("Type épreuve: Tous")
        print()
        
        try:
            results, message = service.affecter_session_automatique(
                session_id=1,
                section_nom=None,  # Toutes les sections
                periode=None,      # Toutes les périodes
                type_epreuve=None  # Tous les types
            )
            
            print("✓ Succès!")
            print(f"\nMessage: {message}")
            print(f"\nNombre de planifications traitées: {len(results)}")
            
            affectees = sum(1 for r in results if r.statut == "AFFECTEE")
            conflits = sum(1 for r in results if r.statut in ("CONFLIT", "CONFLIT_PARTIEL"))
            
            print(f"  - Affectées complètement: {affectees}")
            print(f"  - En conflit: {conflits}")
            
            if results:
                print("\n" + "=" * 60)
                print("DÉTAIL DES RÉSULTATS")
                print("=" * 60)
                for i, r in enumerate(results, 1):
                    statut_icon = "✓" if r.statut == "AFFECTEE" else "⚠" if r.statut == "CONFLIT_PARTIEL" else "✗"
                    print(f"\n{i}. {statut_icon} Planif #{r.planification_id}: {r.statut}")
                    print(f"   Surveillants: {r.surveillants_affectes}/{r.surveillants_requis}")
                    if r.manquants > 0:
                        print(f"   Manquants: {r.manquants}")
                    
                    # Afficher les groupes
                    for j, groupe in enumerate(r.groupes, 1):
                        print(f"   Groupe {j}: {len(groupe.surveillants_affectes)} surveillants affectés")
                        for surv in groupe.surveillants_affectes:
                            print(f"     - {surv.nom} {surv.prenom}")
                    
                    # Afficher les raisons d'exclusion
                    if r.violations:
                        print(f"   Raisons d'exclusion:")
                        for v in r.violations[:3]:  # Limiter à 3
                            print(f"     - {v.nom} {v.prenom}: {v.raison}")
            else:
                print("\n⚠ Aucune planification traitée")
            
        except Exception as e:
            print(f"\n✗ Erreur: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    test_affectation()
