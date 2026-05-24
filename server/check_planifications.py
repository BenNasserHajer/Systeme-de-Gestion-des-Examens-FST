"""Vérifier les planifications dans la base de données"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.planification import Planification
from app.models.salle_session import Session as SessionModel

def check_planifications():
    db: Session = SessionLocal()
    try:
        # Vérifier les sessions
        print("=" * 60)
        print("SESSIONS DISPONIBLES")
        print("=" * 60)
        sessions = db.query(SessionModel).all()
        for s in sessions:
            print(f"Session #{s.id}: {s.type_session} {s.annee_universitaire}")
            print(f"  Dates: {s.date_debut} → {s.date_fin}")
            print(f"  Statut: {s.statut}")
            print()
        
        # Vérifier les planifications
        print("=" * 60)
        print("PLANIFICATIONS PAR SESSION ET STATUT")
        print("=" * 60)
        
        for session in sessions:
            planifs = db.query(Planification).filter(
                Planification.session_id == session.id
            ).all()
            
            print(f"\nSession #{session.id} ({session.type_session} {session.annee_universitaire}):")
            print(f"  Total planifications: {len(planifs)}")
            
            if planifs:
                # Grouper par statut
                statuts = {}
                for p in planifs:
                    statuts[p.statut] = statuts.get(p.statut, 0) + 1
                
                for statut, count in statuts.items():
                    print(f"    - {statut}: {count}")
                
                # Afficher quelques exemples
                print(f"\n  Exemples (5 premiers):")
                for i, p in enumerate(planifs[:5], 1):
                    print(f"    {i}. Planif #{p.id}: {p.matiere} - Statut: {p.statut}")
                    print(f"       Date: {p.date_examen} {p.heure_debut}-{p.heure_fin}")
                    print(f"       Section: {p.section_id}, Nb étudiants: {p.section_nb_etudiants}")
                    print(f"       Nb surveillants requis: {p.nb_surveillants_requis}")
            else:
                print("  Aucune planification")
        
        # Vérifier les enseignants
        print("\n" + "=" * 60)
        print("ENSEIGNANTS DISPONIBLES")
        print("=" * 60)
        from app.models.enseignant import Enseignant
        enseignants = db.query(Enseignant).all()
        print(f"Total enseignants: {len(enseignants)}")
        
        if enseignants:
            print("\nExemples (5 premiers):")
            for i, e in enumerate(enseignants[:5], 1):
                dept = e.departement
                print(f"  {i}. {e.nom} {e.prenom} ({e.grade})")
                print(f"     Département: {dept.nom if dept else 'N/A'}")
                # Volume horaire peut avoir différents noms selon le modèle
                volume = getattr(e, 'volume_horaire_surveillance', None) or getattr(e, 'volume_horaire', None)
                if volume:
                    print(f"     Volume horaire: {volume}h")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_planifications()
