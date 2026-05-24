from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)
columns = inspector.get_columns('planification_examen')

print("Schéma de la table planification_examen:")
print("=" * 80)
for col in columns:
    nullable_str = "NULL" if col['nullable'] else "NOT NULL"
    print(f"{col['name']:30} {str(col['type']):20} {nullable_str}")
