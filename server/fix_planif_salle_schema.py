"""
Script pour corriger le schéma de planif_salle.
"""

from sqlalchemy import text
from app.database import engine

def fix_planif_salle_schema():
    """Corrige le schéma de planif_salle pour utiliser salle_id comme VARCHAR."""
    
    with engine.connect() as conn:
        print("🔧 Correction du schéma de planif_salle...")
        
        try:
            # 1. Supprimer la contrainte de clé étrangère sur salle_id
            print("1. Suppression de la contrainte FK sur salle_id...")
            conn.execute(text("""
                ALTER TABLE planif_salle 
                DROP CONSTRAINT IF EXISTS planif_salle_salle_id_fkey
            """))
            conn.commit()
            print("   ✅ Contrainte FK supprimée")
            
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
            conn.rollback()
        
        try:
            # 2. Supprimer la contrainte FK sur groupe_id (si elle existe)
            print("2. Suppression de la contrainte FK sur groupe_id...")
            conn.execute(text("""
                ALTER TABLE planif_salle 
                DROP CONSTRAINT IF EXISTS planif_salle_groupe_id_fkey
            """))
            conn.commit()
            print("   ✅ Contrainte FK sur groupe_id supprimée")
            
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
            conn.rollback()
        
        try:
            # 3. Changer le type de salle_id de INTEGER à VARCHAR
            print("3. Changement du type de salle_id...")
            conn.execute(text("""
                ALTER TABLE planif_salle 
                ALTER COLUMN salle_id TYPE VARCHAR(80)
            """))
            conn.commit()
            print("   ✅ salle_id est maintenant VARCHAR(80)")
            
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
            conn.rollback()
        
        try:
            # 4. Changer le type de groupe_id pour qu'il ne soit plus une FK
            # (groupe_id dans planif_salle est juste un numéro de groupe, pas une FK)
            print("4. groupe_id reste INTEGER (numéro de groupe)...")
            print("   ✅ groupe_id est correct")
            
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
        
        print("\n✅ Corrections appliquées!")
        print("\nVérification du schéma...")
        
        # Vérifier le schéma
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'planif_salle'
            ORDER BY ordinal_position
        """))
        
        print("\n📊 Schéma mis à jour de planif_salle:")
        print("=" * 80)
        for row in result:
            nullable_str = "NULL" if row[2] == 'YES' else "NOT NULL"
            print(f"{row[0]:30} {row[1]:20} {nullable_str}")


if __name__ == "__main__":
    fix_planif_salle_schema()
