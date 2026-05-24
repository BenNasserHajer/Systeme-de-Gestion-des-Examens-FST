"""
Script pour vérifier et créer le compte admin
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.enseignant import Enseignant

# Configuration du hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_and_create_admin():
    db: Session = SessionLocal()
    
    try:
        # Vérifier si la table compte_enseignant existe
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'compte_enseignant' not in tables:
            print("❌ La table compte_enseignant n'existe pas!")
            print("   Exécutez: psql -U postgres -d exam_surveillance -f add_auth_tables.sql")
            return
        
        # Importer le modèle
        from app.models.compte_enseignant import CompteEnseignant
        
        # Vérifier si le compte admin existe
        admin = db.query(CompteEnseignant).filter(
            CompteEnseignant.email == "admin@university.edu"
        ).first()
        
        if admin:
            print("✅ Compte admin existe déjà")
            print(f"   Email: {admin.email}")
            print(f"   Username: {admin.username}")
            print(f"   Active: {admin.is_active}")
            print(f"   Admin: {admin.is_admin}")
            
            # Vérifier le mot de passe
            test_password = "admin123"
            if pwd_context.verify(test_password, admin.hashed_password):
                print(f"✅ Mot de passe '{test_password}' est correct")
            else:
                print(f"❌ Mot de passe '{test_password}' est incorrect")
                print("   Réinitialisation du mot de passe...")
                admin.hashed_password = pwd_context.hash(test_password)
                db.commit()
                print(f"✅ Mot de passe réinitialisé à '{test_password}'")
        else:
            print("❌ Compte admin n'existe pas")
            print("   Création du compte admin...")
            
            # Vérifier qu'il y a au moins un enseignant
            enseignant = db.query(Enseignant).first()
            if not enseignant:
                print("❌ Aucun enseignant dans la base!")
                print("   Créez d'abord des enseignants")
                return
            
            # Créer le compte admin
            admin = CompteEnseignant(
                enseignant_id=enseignant.id,
                username="admin",
                email="admin@university.edu",
                hashed_password=pwd_context.hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            print("✅ Compte admin créé avec succès!")
            print(f"   Email: admin@university.edu")
            print(f"   Mot de passe: admin123")
            print(f"   Enseignant ID: {enseignant.id}")
        
        # Lister tous les comptes
        print("\n" + "="*60)
        print("TOUS LES COMPTES")
        print("="*60)
        
        comptes = db.query(CompteEnseignant).all()
        for compte in comptes:
            ens = compte.enseignant
            print(f"\n{compte.id}. {compte.email}")
            print(f"   Username: {compte.username}")
            print(f"   Enseignant: {ens.nom} {ens.prenom}")
            print(f"   Active: {compte.is_active}")
            print(f"   Admin: {compte.is_admin}")
        
        print(f"\nTotal: {len(comptes)} compte(s)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_create_admin()
