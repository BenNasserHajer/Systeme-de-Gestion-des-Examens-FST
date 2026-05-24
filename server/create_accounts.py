"""
Script pour créer des comptes enseignants avec mots de passe hashés.
Usage: python create_accounts.py
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.enseignant import Enseignant
from app.models.compte_enseignant import CompteEnseignant

# Configuration du hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    return pwd_context.hash(password)


def create_account(
    db: Session,
    enseignant_id: int,
    username: str,
    email: str,
    password: str,
    is_admin: bool = False
) -> CompteEnseignant:
    """Crée un compte enseignant."""
    
    # Vérifier si l'enseignant existe
    enseignant = db.query(Enseignant).filter(Enseignant.id == enseignant_id).first()
    if not enseignant:
        raise ValueError(f"Enseignant avec ID {enseignant_id} n'existe pas")
    
    # Vérifier si le compte existe déjà
    existing = db.query(CompteEnseignant).filter(
        (CompteEnseignant.username == username) |
        (CompteEnseignant.email == email) |
        (CompteEnseignant.enseignant_id == enseignant_id)
    ).first()
    
    if existing:
        raise ValueError(f"Un compte existe déjà pour cet enseignant/username/email")
    
    # Créer le compte
    hashed_password = hash_password(password)
    compte = CompteEnseignant(
        enseignant_id=enseignant_id,
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=is_admin
    )
    
    db.add(compte)
    db.commit()
    db.refresh(compte)
    
    return compte


def create_accounts_for_all_enseignants(db: Session, default_password: str = "password123"):
    """Crée des comptes pour tous les enseignants qui n'en ont pas."""
    
    enseignants = db.query(Enseignant).all()
    created = 0
    skipped = 0
    
    for ens in enseignants:
        # Vérifier si un compte existe déjà
        existing = db.query(CompteEnseignant).filter(
            CompteEnseignant.enseignant_id == ens.id
        ).first()
        
        if existing:
            print(f"⏭️  Compte existe déjà pour {ens.nom} {ens.prenom}")
            skipped += 1
            continue
        
        # Générer username et email
        username = f"{ens.nom.lower()}.{ens.prenom.lower()}".replace(" ", "")
        email = f"{username}@university.edu"
        
        try:
            compte = create_account(
                db=db,
                enseignant_id=ens.id,
                username=username,
                email=email,
                password=default_password,
                is_admin=False
            )
            print(f"✅ Compte créé: {username} (ID: {compte.id})")
            created += 1
        except Exception as e:
            print(f"❌ Erreur pour {ens.nom} {ens.prenom}: {e}")
    
    return created, skipped


def create_admin_account(db: Session, enseignant_id: int = 1):
    """Crée un compte administrateur."""
    
    try:
        compte = create_account(
            db=db,
            enseignant_id=enseignant_id,
            username="admin",
            email="admin@university.edu",
            password="admin123",
            is_admin=True
        )
        print(f"✅ Compte admin créé: admin (ID: {compte.id})")
        return compte
    except ValueError as e:
        print(f"⚠️  {e}")
        return None


def list_accounts(db: Session):
    """Liste tous les comptes."""
    
    comptes = db.query(CompteEnseignant).all()
    
    print("\n" + "=" * 80)
    print("LISTE DES COMPTES")
    print("=" * 80)
    
    for compte in comptes:
        enseignant = compte.enseignant
        status = "🟢 Actif" if compte.is_active else "🔴 Inactif"
        admin = "👑 Admin" if compte.is_admin else "👤 User"
        
        print(f"\n{compte.id}. {compte.username}")
        print(f"   Email: {compte.email}")
        print(f"   Enseignant: {enseignant.nom} {enseignant.prenom}")
        print(f"   Status: {status} | {admin}")
        print(f"   Créé: {compte.created_at}")
        if compte.last_login:
            print(f"   Dernière connexion: {compte.last_login}")
    
    print("\n" + "=" * 80)
    print(f"Total: {len(comptes)} comptes")
    print("=" * 80)


def reset_password(db: Session, username: str, new_password: str):
    """Réinitialise le mot de passe d'un compte."""
    
    compte = db.query(CompteEnseignant).filter(
        CompteEnseignant.username == username
    ).first()
    
    if not compte:
        print(f"❌ Compte '{username}' non trouvé")
        return False
    
    compte.hashed_password = hash_password(new_password)
    db.commit()
    
    print(f"✅ Mot de passe réinitialisé pour {username}")
    return True


def main():
    """Menu principal."""
    
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("GESTION DES COMPTES ENSEIGNANTS")
        print("=" * 80)
        print("\n1. Créer des comptes pour tous les enseignants")
        print("2. Créer un compte admin")
        print("3. Créer un compte spécifique")
        print("4. Lister tous les comptes")
        print("5. Réinitialiser un mot de passe")
        print("6. Quitter")
        print()
        
        choice = input("Votre choix (1-6): ").strip()
        
        if choice == "1":
            print("\n📝 Création des comptes pour tous les enseignants...")
            password = input("Mot de passe par défaut (défaut: password123): ").strip()
            if not password:
                password = "password123"
            
            created, skipped = create_accounts_for_all_enseignants(db, password)
            print(f"\n✅ {created} comptes créés, {skipped} ignorés")
            print(f"🔑 Mot de passe par défaut: {password}")
        
        elif choice == "2":
            print("\n👑 Création du compte admin...")
            ens_id = input("ID de l'enseignant (défaut: 1): ").strip()
            ens_id = int(ens_id) if ens_id else 1
            
            create_admin_account(db, ens_id)
            print("🔑 Username: admin")
            print("🔑 Password: admin123")
        
        elif choice == "3":
            print("\n📝 Création d'un compte spécifique...")
            ens_id = int(input("ID de l'enseignant: "))
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password = input("Mot de passe: ").strip()
            is_admin = input("Admin? (o/N): ").strip().lower() == "o"
            
            compte = create_account(db, ens_id, username, email, password, is_admin)
            print(f"✅ Compte créé: {compte.username} (ID: {compte.id})")
        
        elif choice == "4":
            list_accounts(db)
        
        elif choice == "5":
            print("\n🔑 Réinitialisation de mot de passe...")
            username = input("Username: ").strip()
            new_password = input("Nouveau mot de passe: ").strip()
            
            reset_password(db, username, new_password)
        
        elif choice == "6":
            print("\n👋 Au revoir!")
            return
        
        else:
            print("\n❌ Choix invalide")
    
    except KeyboardInterrupt:
        print("\n\n👋 Annulé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
