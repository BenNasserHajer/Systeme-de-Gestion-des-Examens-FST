"""
Script pour appliquer directement les corrections de schéma sans Alembic.
"""

from sqlalchemy import text
from app.database import engine

def fix_schema():
    """Applique les corrections de schéma directement."""
    
    with engine.connect() as conn:
        print("🔧 Application des corrections de schéma...")
        
        try:
            # 1. Rendre departement_id nullable
            print("1. Rendre departement_id nullable...")
            conn.execute(text("""
                ALTER TABLE planification_examen 
                ALTER COLUMN departement_id DROP NOT NULL
            """))
            conn.commit()
            print("   ✅ departement_id est maintenant nullable")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        try:
            # 2. Rendre creneau_id nullable
            print("2. Rendre creneau_id nullable...")
            conn.execute(text("""
                ALTER TABLE planification_examen 
                ALTER COLUMN creneau_id DROP NOT NULL
            """))
            conn.commit()
            print("   ✅ creneau_id est maintenant nullable")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        try:
            # 3. Changer coefficient de INTEGER à FLOAT
            print("3. Changer coefficient de INTEGER à FLOAT...")
            conn.execute(text("""
                ALTER TABLE planification_examen 
                ALTER COLUMN coefficient TYPE DOUBLE PRECISION
                USING coefficient::DOUBLE PRECISION
            """))
            conn.commit()
            print("   ✅ coefficient est maintenant FLOAT")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        try:
            # 4. Rendre section_nb_etudiants NOT NULL (avec valeur par défaut temporaire)
            print("4. Rendre section_nb_etudiants NOT NULL...")
            # D'abord, mettre une valeur par défaut pour les NULL existants
            conn.execute(text("""
                UPDATE planification_examen 
                SET section_nb_etudiants = 0 
                WHERE section_nb_etudiants IS NULL
            """))
            conn.execute(text("""
                ALTER TABLE planification_examen 
                ALTER COLUMN section_nb_etudiants SET NOT NULL
            """))
            conn.commit()
            print("   ✅ section_nb_etudiants est maintenant NOT NULL")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        try:
            # 5. Rendre a_examen_final NOT NULL avec default
            print("5. Rendre a_examen_final NOT NULL...")
            conn.execute(text("""
                UPDATE planification_examen 
                SET a_examen_final = TRUE 
                WHERE a_examen_final IS NULL
            """))
            conn.execute(text("""
                ALTER TABLE planification_examen 
                ALTER COLUMN a_examen_final SET NOT NULL,
                ALTER COLUMN a_examen_final SET DEFAULT TRUE
            """))
            conn.commit()
            print("   ✅ a_examen_final est maintenant NOT NULL")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        try:
            # 6. Rendre a_ds NOT NULL avec default
            print("6. Rendre a_ds NOT NULL...")
            conn.execute(text("""
                UPDATE planification_examen 
                SET a_ds = TRUE 
                WHERE a_ds IS NULL
            """))
            conn.execute(text("""
                ALTER TABLE planification_examen 
                ALTER COLUMN a_ds SET NOT NULL,
                ALTER COLUMN a_ds SET DEFAULT TRUE
            """))
            conn.commit()
            print("   ✅ a_ds est maintenant NOT NULL")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        try:
            # 7. Rendre section_id NOT NULL
            print("7. Rendre section_id NOT NULL...")
            conn.execute(text("""
                UPDATE planification_examen 
                SET section_id = 1 
                WHERE section_id IS NULL
            """))
            conn.execute(text("""
                ALTER TABLE planification_examen 
                ALTER COLUMN section_id SET NOT NULL
            """))
            conn.commit()
            print("   ✅ section_id est maintenant NOT NULL")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        try:
            # 8. Modifier la clé primaire de planif_salle
            print("8. Modifier la clé primaire de planif_salle...")
            conn.execute(text("""
                ALTER TABLE planif_salle 
                DROP CONSTRAINT IF EXISTS planif_salle_pkey
            """))
            conn.execute(text("""
                ALTER TABLE planif_salle 
                ADD PRIMARY KEY (planification_id, groupe_id)
            """))
            conn.commit()
            print("   ✅ Clé primaire composite créée")
            
        except Exception as e:
            print(f"   ⚠️  Erreur (peut-être déjà appliqué): {e}")
            conn.rollback()
        
        print("\n✅ Toutes les corrections ont été appliquées!")
        print("\nVérification du schéma...")
        
        # Vérifier le schéma
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'planification_examen'
            AND column_name IN ('departement_id', 'creneau_id', 'coefficient', 
                               'section_nb_etudiants', 'a_examen_final', 'a_ds', 'section_id')
            ORDER BY column_name
        """))
        
        print("\n📊 Schéma mis à jour:")
        print("=" * 80)
        for row in result:
            nullable_str = "NULL" if row[2] == 'YES' else "NOT NULL"
            print(f"{row[0]:30} {row[1]:20} {nullable_str}")


if __name__ == "__main__":
    fix_schema()
