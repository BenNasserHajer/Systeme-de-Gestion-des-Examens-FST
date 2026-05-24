"""
Script interactif pour gérer les comptes enseignants
Permet de voir, créer, modifier et supprimer des comptes
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models.enseignant import Enseignant
from app.models.compte_enseignant import CompteEnseignant


def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def voir_tous_enseignants(db: Session):
    """Affiche tous les enseignants avec leur statut de compte"""
    print_header("TOUS LES ENSEIGNANTS")
    
    query = text("""
        SELECT 
            e.id,
            e.nom,
            e.prenom,
            e.grade,
            e.email,
            d.nom as departement,
            CASE WHEN ce.id IS NOT NULL THEN 'OUI' ELSE 'NON' END as a_compte,
            ce.email as email_compte,
            ce.actif
        FROM enseignant e
        LEFT JOIN departement d ON e.departement_id = d.id
        LEFT JOIN compte_enseignant ce ON e.id = ce.enseignant_id
        ORDER BY e.nom, e.prenom
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    if not rows:
        print("❌ Aucun enseignant trouvé dans la base de données")
        return
    
    print(f"\n{'ID':<5} {'Nom':<20} {'Prénom':<20} {'Grade':<15} {'Département':<20} {'Compte':<8} {'Actif':<6}")
    print("-" * 120)
    
    for row in rows:
        actif = "✓" if row.actif else "✗" if row.a_compte == "OUI" else "-"
        print(f"{row.id:<5} {row.nom:<20} {row.prenom:<20} {row.grade or '-':<15} {row.departement or '-':<20} {row.a_compte:<8} {actif:<6}")
    
    print(f"\nTotal: {len(rows)} enseignant(s)")


def voir_enseignants_sans_compte(db: Session):
    """Affiche les enseignants qui n'ont pas encore de compte"""
    print_header("ENSEIGNANTS SANS COMPTE")
    
    query = text("""
        SELECT 
            e.id,
            e.nom,
            e.prenom,
            e.grade,
            e.email,
            d.nom as departement
        FROM enseignant e
        LEFT JOIN compte_enseignant ce ON e.id = ce.enseignant_id
        LEFT JOIN departement d ON e.departement_id = d.id
        WHERE ce.id IS NULL
        ORDER BY e.nom, e.prenom
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    if not rows:
        print("✅ Tous les enseignants ont déjà un compte!")
        return []
    
    print(f"\n{'ID':<5} {'Nom':<20} {'Prénom':<20} {'Grade':<15} {'Email':<30} {'Département':<20}")
    print("-" * 120)
    
    for row in rows:
        print(f"{row.id:<5} {row.nom:<20} {row.prenom:<20} {row.grade or '-':<15} {row.email or '-':<30} {row.departement or '-':<20}")
    
    print(f"\nTotal: {len(rows)} enseignant(s) sans compte")
    return rows


def voir_comptes_existants(db: Session):
    """Affiche tous les comptes enseignants existants"""
    print_header("COMPTES ENSEIGNANTS EXISTANTS")
    
    query = text("""
        SELECT 
            ce.id,
            e.nom,
            e.prenom,
            ce.email,
            ce.type_compte,
            ce.actif,
            ce.created_at
        FROM compte_enseignant ce
        INNER JOIN enseignant e ON ce.enseignant_id = e.id
        ORDER BY ce.created_at DESC
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    if not rows:
        print("❌ Aucun compte enseignant trouvé")
        return
    
    print(f"\n{'ID':<5} {'Nom':<20} {'Prénom':<20} {'Email':<35} {'Type':<12} {'Actif':<6} {'Créé le':<20}")
    print("-" * 130)
    
    for row in rows:
        actif = "✓" if row.actif else "✗"
        created = row.created_at.strftime("%Y-%m-%d %H:%M") if row.created_at else "-"
        print(f"{row.id:<5} {row.nom:<20} {row.prenom:<20} {row.email:<35} {row.type_compte:<12} {actif:<6} {created:<20}")
    
    print(f"\nTotal: {len(rows)} compte(s)")


def creer_compte_pour_enseignant(db: Session, enseignant_id: int, email: str, mot_de_passe: str):
    """Crée un compte pour un enseignant spécifique"""
    try:
        # Vérifier que l'enseignant existe
        enseignant = db.query(Enseignant).filter(Enseignant.id == enseignant_id).first()
        if not enseignant:
            print(f"❌ Enseignant avec ID {enseignant_id} introuvable")
            return False
        
        # Vérifier qu'il n'a pas déjà un compte
        compte_existant = db.query(CompteEnseignant).filter(
            CompteEnseignant.enseignant_id == enseignant_id
        ).first()
        if compte_existant:
            print(f"❌ L'enseignant {enseignant.prenom} {enseignant.nom} a déjà un compte")
            return False
        
        # Créer le compte
        nouveau_compte = CompteEnseignant(
            enseignant_id=enseignant_id,
            email=email,
            mot_de_passe=mot_de_passe,  # ⚠️ En clair! Utiliser bcrypt en production
            type_compte="ENSEIGNANT",
            actif=True
        )
        
        db.add(nouveau_compte)
        db.commit()
        
        print(f"✅ Compte créé avec succès pour {enseignant.prenom} {enseignant.nom}")
        print(f"   Email: {email}")
        print(f"   Mot de passe: {mot_de_passe}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la création du compte: {e}")
        return False


def creer_comptes_automatiquement(db: Session):
    """Crée automatiquement des comptes pour tous les enseignants sans compte"""
    print_header("CRÉATION AUTOMATIQUE DES COMPTES")
    
    enseignants_sans_compte = voir_enseignants_sans_compte(db)
    
    if not enseignants_sans_compte:
        return
    
    print("\n⚠️  Cette action va créer des comptes pour tous les enseignants ci-dessus")
    print("   Format email: prenom.nom@fst.utm.tn")
    print("   Mot de passe par défaut: password123")
    
    reponse = input("\nContinuer? (oui/non): ").strip().lower()
    if reponse not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return
    
    comptes_crees = 0
    erreurs = 0
    
    for ens in enseignants_sans_compte:
        # Générer l'email
        prenom = ens.prenom.lower().replace(' ', '.')
        nom = ens.nom.lower().replace(' ', '.')
        email = f"{prenom}.{nom}@fst.utm.tn"
        
        # Créer le compte
        if creer_compte_pour_enseignant(db, ens.id, email, "password123"):
            comptes_crees += 1
        else:
            erreurs += 1
    
    print(f"\n✅ {comptes_crees} compte(s) créé(s)")
    if erreurs > 0:
        print(f"❌ {erreurs} erreur(s)")


def modifier_mot_de_passe(db: Session, email: str, nouveau_mdp: str):
    """Modifie le mot de passe d'un compte"""
    try:
        compte = db.query(CompteEnseignant).filter(CompteEnseignant.email == email).first()
        if not compte:
            print(f"❌ Compte avec email {email} introuvable")
            return False
        
        compte.mot_de_passe = nouveau_mdp
        db.commit()
        
        print(f"✅ Mot de passe modifié pour {email}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur: {e}")
        return False


def activer_desactiver_compte(db: Session, email: str, actif: bool):
    """Active ou désactive un compte"""
    try:
        compte = db.query(CompteEnseignant).filter(CompteEnseignant.email == email).first()
        if not compte:
            print(f"❌ Compte avec email {email} introuvable")
            return False
        
        compte.actif = actif
        db.commit()
        
        statut = "activé" if actif else "désactivé"
        print(f"✅ Compte {statut} pour {email}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur: {e}")
        return False


def menu_principal():
    """Affiche le menu principal"""
    print_header("GESTION DES COMPTES ENSEIGNANTS")
    print("\n1. Voir tous les enseignants")
    print("2. Voir les enseignants sans compte")
    print("3. Voir les comptes existants")
    print("4. Créer un compte pour un enseignant")
    print("5. Créer des comptes automatiquement pour tous")
    print("6. Modifier un mot de passe")
    print("7. Activer/Désactiver un compte")
    print("8. Quitter")
    print("\n" + "="*70)


def main():
    """Fonction principale"""
    db = SessionLocal()
    
    try:
        while True:
            menu_principal()
            choix = input("\nVotre choix: ").strip()
            
            if choix == "1":
                voir_tous_enseignants(db)
                
            elif choix == "2":
                voir_enseignants_sans_compte(db)
                
            elif choix == "3":
                voir_comptes_existants(db)
                
            elif choix == "4":
                print_header("CRÉER UN COMPTE")
                voir_enseignants_sans_compte(db)
                
                try:
                    ens_id = int(input("\nID de l'enseignant: ").strip())
                    email = input("Email: ").strip()
                    mdp = input("Mot de passe: ").strip()
                    
                    if email and mdp:
                        creer_compte_pour_enseignant(db, ens_id, email, mdp)
                    else:
                        print("❌ Email et mot de passe requis")
                except ValueError:
                    print("❌ ID invalide")
                
            elif choix == "5":
                creer_comptes_automatiquement(db)
                
            elif choix == "6":
                print_header("MODIFIER MOT DE PASSE")
                voir_comptes_existants(db)
                
                email = input("\nEmail du compte: ").strip()
                nouveau_mdp = input("Nouveau mot de passe: ").strip()
                
                if email and nouveau_mdp:
                    modifier_mot_de_passe(db, email, nouveau_mdp)
                else:
                    print("❌ Email et mot de passe requis")
                
            elif choix == "7":
                print_header("ACTIVER/DÉSACTIVER COMPTE")
                voir_comptes_existants(db)
                
                email = input("\nEmail du compte: ").strip()
                action = input("Action (activer/desactiver): ").strip().lower()
                
                if email and action in ['activer', 'desactiver']:
                    activer_desactiver_compte(db, email, action == 'activer')
                else:
                    print("❌ Email et action requis")
                
            elif choix == "8":
                print("\n👋 Au revoir!")
                break
                
            else:
                print("❌ Choix invalide")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🔐 GESTION DES COMPTES ENSEIGNANTS")
    print("="*70)
    print("\n⚠️  IMPORTANT:")
    print("   - Les mots de passe sont stockés en CLAIR (pas sécurisé!)")
    print("   - En production, utilisez bcrypt pour hasher les mots de passe")
    print("   - Mot de passe par défaut: password123")
    print("\n" + "="*70)
    
    input("\nAppuyez sur Entrée pour continuer...")
    
    main()
