#!/usr/bin/env python3
"""
Script pour nettoyer les planifications d'une session.
Utile pour les tests répétés.
"""

import sys
from sqlalchemy import text
from app.database import SessionLocal, check_connection


def clean_session(session_id: int, confirm: bool = False) -> None:
    """Supprimer toutes les planifications d'une session."""
    
    db = SessionLocal()
    try:
        if not check_connection(db):
            print("❌ Erreur : Connexion à la base de données impossible")
            return
        
        # Compter les planifications existantes
        count_query = text("""
            SELECT COUNT(*) as count
            FROM planifications
            WHERE session_id = :session_id
        """)
        
        try:
            result = db.execute(count_query, {"session_id": session_id}).fetchone()
            count = result[0] if result else 0
        except Exception:
            # Essayer avec le schéma réel
            count_query = text("""
                SELECT COUNT(*) as count
                FROM planification_examen
                WHERE session_id = :session_id
            """)
            result = db.execute(count_query, {"session_id": session_id}).fetchone()
            count = result[0] if result else 0
        
        if count == 0:
            print(f"✅ Aucune planification trouvée pour la session {session_id}")
            return
        
        print(f"📊 Planifications trouvées : {count}")
        
        if not confirm:
            response = input(f"⚠️  Voulez-vous supprimer {count} planification(s) de la session {session_id} ? (oui/non) : ")
            if response.lower() not in ['oui', 'o', 'yes', 'y']:
                print("❌ Opération annulée")
                return
        
        # Supprimer les planifications
        try:
            # Essayer avec le schéma simplifié
            db.execute(
                text("DELETE FROM planifications WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            db.commit()
            print(f"✅ {count} planification(s) supprimée(s) avec succès (schéma simplifié)")
        except Exception:
            # Essayer avec le schéma réel
            db.rollback()
            db.execute(
                text("""
                    DELETE FROM planif_salle 
                    WHERE planification_id IN (
                        SELECT id FROM planification_examen WHERE session_id = :session_id
                    )
                """),
                {"session_id": session_id}
            )
            db.execute(
                text("DELETE FROM planification_examen WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            db.commit()
            print(f"✅ {count} planification(s) supprimée(s) avec succès (schéma réel)")
        
    except Exception as exc:
        db.rollback()
        print(f"❌ Erreur : {exc}")
    finally:
        db.close()


def list_sessions() -> None:
    """Lister toutes les sessions disponibles."""
    
    db = SessionLocal()
    try:
        if not check_connection(db):
            print("❌ Erreur : Connexion à la base de données impossible")
            return
        
        # Essayer avec le schéma simplifié
        try:
            query = text("""
                SELECT 
                    session_id,
                    session_date_debut,
                    session_date_fin,
                    COUNT(*) as nb_planifs
                FROM planifications
                GROUP BY session_id, session_date_debut, session_date_fin
                ORDER BY session_id
            """)
            results = db.execute(query).fetchall()
            
            if not results:
                print("📋 Aucune session avec planifications trouvée")
                return
            
            print("\n📋 Sessions avec planifications :")
            print("-" * 80)
            for row in results:
                print(f"Session {row[0]} : {row[1]} → {row[2]} ({row[3]} planifications)")
            print("-" * 80)
            
        except Exception:
            # Essayer avec le schéma réel
            query = text("""
                SELECT 
                    s.id,
                    s.date_debut,
                    s.date_fin,
                    COUNT(pe.id) as nb_planifs
                FROM session s
                LEFT JOIN planification_examen pe ON pe.session_id = s.id
                GROUP BY s.id, s.date_debut, s.date_fin
                ORDER BY s.id
            """)
            results = db.execute(query).fetchall()
            
            if not results:
                print("📋 Aucune session trouvée")
                return
            
            print("\n📋 Sessions disponibles :")
            print("-" * 80)
            for row in results:
                print(f"Session {row[0]} : {row[1]} → {row[2]} ({row[3]} planifications)")
            print("-" * 80)
        
    except Exception as exc:
        print(f"❌ Erreur : {exc}")
    finally:
        db.close()


def main():
    """Point d'entrée principal."""
    
    print("\n" + "=" * 80)
    print("🧹 NETTOYAGE DES PLANIFICATIONS")
    print("=" * 80 + "\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python clean_session.py list                    # Lister les sessions")
        print("  python clean_session.py <session_id>            # Nettoyer une session")
        print("  python clean_session.py <session_id> --confirm  # Sans confirmation")
        print("\nExemples:")
        print("  python clean_session.py list")
        print("  python clean_session.py 1")
        print("  python clean_session.py 1 --confirm")
        print()
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_sessions()
        return
    
    try:
        session_id = int(command)
    except ValueError:
        print(f"❌ Erreur : '{command}' n'est pas un ID de session valide")
        return
    
    confirm = "--confirm" in sys.argv or "-y" in sys.argv
    
    clean_session(session_id, confirm)
    
    print("\n" + "=" * 80)
    print("✨ Opération terminée")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
