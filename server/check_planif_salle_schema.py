from sqlalchemy import inspect, text
from app.database import engine

inspector = inspect(engine)
columns = inspector.get_columns('planif_salle')

print("Schéma de la table planif_salle:")
print("=" * 80)
for col in columns:
    nullable_str = "NULL" if col['nullable'] else "NOT NULL"
    print(f"{col['name']:30} {str(col['type']):20} {nullable_str}")

# Vérifier aussi les contraintes
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_name = 'planif_salle'
    """))
    
    print("\n📋 Contraintes:")
    for row in result:
        print(f"  - {row[0]}: {row[1]}")
