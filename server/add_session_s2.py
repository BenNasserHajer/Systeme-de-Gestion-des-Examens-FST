"""
Script pour ajouter la session S2 avec période d'examens du 11 au 23 mai 2026.
"""

from datetime import date, time
from sqlalchemy.orm import Session

# Import de tous les modèles pour éviter les erreurs de relations
from app.database import SessionLocal
from app.models.salle_session import Session as SessionModel, Creneau
from app.models.enseignant import Enseignant
from app.models.compte_enseignant import CompteEnseignant
from app.models.planification import Planification
from app.models.surveillance import Surveillance

def add_session_s2():
    """Ajoute la session S2 et ses créneaux."""
    db: Session = SessionLocal()
    
    try:
        # Vérifier si la session S2 existe déjà
        existing = db.query(SessionModel).filter(
            SessionModel.annee_universitaire == "2025/2026",
            SessionModel.date_debut == date(2026, 5, 11)
        ).first()
        
        if existing:
            print(f"✓ Session S2 existe déjà (ID: {existing.id})")
            session_s2 = existing
        else:
            # Créer la session S2
            session_s2 = SessionModel(
                type_session="PRINCIPALE",
                annee_universitaire="2025/2026",
                date_debut=date(2026, 5, 11),
                date_fin=date(2026, 5, 23),
                statut="BROUILLON"
            )
            db.add(session_s2)
            db.commit()
            db.refresh(session_s2)
            print(f"✓ Session S2 créée (ID: {session_s2.id})")
        
        # Créneaux pour S2 (11 mai au 23 mai 2026)
        creneaux_s2 = [
            # Semaine 1: 11-16 mai
            # Lundi 11 mai
            (date(2026, 5, 11), time(8, 0), time(10, 0), "Lun 11/05 Matin"),
            (date(2026, 5, 11), time(10, 30), time(12, 30), "Lun 11/05 Midi"),
            (date(2026, 5, 11), time(14, 0), time(16, 0), "Lun 11/05 Après-midi"),
            # Mardi 12 mai
            (date(2026, 5, 12), time(8, 0), time(10, 0), "Mar 12/05 Matin"),
            (date(2026, 5, 12), time(10, 30), time(12, 30), "Mar 12/05 Midi"),
            (date(2026, 5, 12), time(14, 0), time(16, 0), "Mar 12/05 Après-midi"),
            # Mercredi 13 mai
            (date(2026, 5, 13), time(8, 0), time(10, 0), "Mer 13/05 Matin"),
            (date(2026, 5, 13), time(10, 30), time(12, 30), "Mer 13/05 Midi"),
            (date(2026, 5, 13), time(14, 0), time(16, 0), "Mer 13/05 Après-midi"),
            # Jeudi 14 mai
            (date(2026, 5, 14), time(8, 0), time(10, 0), "Jeu 14/05 Matin"),
            (date(2026, 5, 14), time(10, 30), time(12, 30), "Jeu 14/05 Midi"),
            (date(2026, 5, 14), time(14, 0), time(16, 0), "Jeu 14/05 Après-midi"),
            # Vendredi 15 mai
            (date(2026, 5, 15), time(8, 0), time(10, 0), "Ven 15/05 Matin"),
            (date(2026, 5, 15), time(10, 30), time(12, 30), "Ven 15/05 Midi"),
            (date(2026, 5, 15), time(14, 0), time(16, 0), "Ven 15/05 Après-midi"),
            # Samedi 16 mai
            (date(2026, 5, 16), time(8, 0), time(10, 0), "Sam 16/05 Matin"),
            (date(2026, 5, 16), time(10, 30), time(12, 30), "Sam 16/05 Midi"),
            
            # Semaine 2: 18-23 mai (pas de dimanche 17)
            # Lundi 18 mai
            (date(2026, 5, 18), time(8, 0), time(10, 0), "Lun 18/05 Matin"),
            (date(2026, 5, 18), time(10, 30), time(12, 30), "Lun 18/05 Midi"),
            (date(2026, 5, 18), time(14, 0), time(16, 0), "Lun 18/05 Après-midi"),
            # Mardi 19 mai
            (date(2026, 5, 19), time(8, 0), time(10, 0), "Mar 19/05 Matin"),
            (date(2026, 5, 19), time(10, 30), time(12, 30), "Mar 19/05 Midi"),
            (date(2026, 5, 19), time(14, 0), time(16, 0), "Mar 19/05 Après-midi"),
            # Mercredi 20 mai
            (date(2026, 5, 20), time(8, 0), time(10, 0), "Mer 20/05 Matin"),
            (date(2026, 5, 20), time(10, 30), time(12, 30), "Mer 20/05 Midi"),
            (date(2026, 5, 20), time(14, 0), time(16, 0), "Mer 20/05 Après-midi"),
            # Jeudi 21 mai
            (date(2026, 5, 21), time(8, 0), time(10, 0), "Jeu 21/05 Matin"),
            (date(2026, 5, 21), time(10, 30), time(12, 30), "Jeu 21/05 Midi"),
            (date(2026, 5, 21), time(14, 0), time(16, 0), "Jeu 21/05 Après-midi"),
            # Vendredi 22 mai
            (date(2026, 5, 22), time(8, 0), time(10, 0), "Ven 22/05 Matin"),
            (date(2026, 5, 22), time(10, 30), time(12, 30), "Ven 22/05 Midi"),
            (date(2026, 5, 22), time(14, 0), time(16, 0), "Ven 22/05 Après-midi"),
            # Samedi 23 mai
            (date(2026, 5, 23), time(8, 0), time(10, 0), "Sam 23/05 Matin"),
            (date(2026, 5, 23), time(10, 30), time(12, 30), "Sam 23/05 Midi"),
        ]
        
        created_count = 0
        existing_count = 0
        
        for creneau_date, heure_debut, heure_fin, libelle in creneaux_s2:
            # Vérifier si le créneau existe déjà
            existing_creneau = db.query(Creneau).filter(
                Creneau.date == creneau_date,
                Creneau.heure_debut == heure_debut
            ).first()
            
            if not existing_creneau:
                creneau = Creneau(
                    date=creneau_date,
                    heure_debut=heure_debut,
                    heure_fin=heure_fin,
                    libelle=libelle
                )
                db.add(creneau)
                created_count += 1
            else:
                existing_count += 1
        
        db.commit()
        
        print(f"✓ Créneaux S2: {created_count} créés, {existing_count} existants")
        print(f"\n📅 Session S2 configurée:")
        print(f"   Période: 11 mai 2026 → 23 mai 2026")
        print(f"   Créneaux: {created_count + existing_count} créneaux disponibles")
        print(f"   Statut: BROUILLON")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Ajout de la session S2 (11-23 mai 2026)...\n")
    add_session_s2()
    print("\n✅ Terminé!")
