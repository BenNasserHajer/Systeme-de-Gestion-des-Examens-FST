"""
Test automatique de planification avec sauvegarde automatique.
"""

from test_real_data import *

def main_auto():
    """Version automatique sans demande de confirmation."""
    print_separator("🚀 TEST AUTOMATIQUE DE PLANIFICATION")
    
    db = SessionLocal()
    
    try:
        # 1. Récupérer les statistiques
        sessions, salles, creneaux, section_matieres = get_database_stats(db)
        
        if not sessions:
            print("\n❌ Aucune session trouvée!")
            return
        
        session = sessions[0]
        
        # 2. Générer les planifications
        creates, result = test_generation_simple(
            db, session, salles, creneaux, section_matieres
        )
        
        if not creates:
            print("\n❌ Aucune planification générée.")
            return
        
        # 3. Sauvegarder automatiquement
        saved = save_to_database(db, creates)
        
        if saved:
            # 4. Afficher l'emploi du temps
            display_emploi_du_temps(db, session.id)
            
            print_separator("✅ TEST TERMINÉ AVEC SUCCÈS")
            print(f"✅ {len(saved)} planifications sauvegardées")
            print(f"📊 Session: {session.type_session} {session.annee_universitaire}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main_auto()
