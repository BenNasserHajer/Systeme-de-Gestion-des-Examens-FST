cd server
source venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload


# POUR AJOUTER TABLE

1 Creer le modele dans app/models/nom_table.py

2 Importer dans app/models/__init__.py :
    from app.models.nom_table import NomTable

3 Generer la migration :
    alembic revision --autogenerate -m "create_nom_table"

4 Appliquer la migration :
    alembic upgrade head

5 Commiter :
    git add app/models/ alembic/versions/
    git commit -m "feat: add nom_table"
    git push

# COMMANDES ESSENTIELLES

alembic upgrade head                              # Appliquer les migrations
alembic revision --autogenerate -m "message"      # Creer une migration
alembic current                                  # Voir version actuelle
alembic downgrade -1                             # Annuler derniere migration
