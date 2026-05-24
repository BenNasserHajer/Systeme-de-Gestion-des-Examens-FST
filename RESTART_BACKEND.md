# 🔄 Redémarrage du Backend Requis

## ⚠️ Problème

Le backend doit être redémarré pour prendre en compte les modifications apportées aux fichiers :
- `app/algorithms/surv_auto.py`
- `app/models/planification.py`

## 🚀 Solution

### Étape 1 : Arrêter le serveur actuel
Dans le terminal où le backend tourne, appuyez sur `Ctrl+C`

### Étape 2 : Redémarrer le serveur
```bash
cd server
uvicorn app.main:app --reload
```

### Étape 3 : Vérifier que le serveur démarre correctement
Vous devriez voir :
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
[startup] database: connected
INFO:     Application startup complete.
```

### Étape 4 : Tester l'endpoint
```bash
curl http://localhost:8000/health
```

Devrait retourner :
```json
{"status":"ok","database":"connected","timestamp":"..."}
```

## 🔍 Si le serveur ne démarre pas

### Erreur possible : "Can't find any foreign key relationships"

Si vous voyez cette erreur au démarrage :
```
sqlalchemy.exc.NoForeignKeysError: Can't find any foreign key relationships between 'planif_salle' and 'groupe'.
```

**Solution :** Le modèle a besoin d'une migration de base de données. Deux options :

#### Option 1 : Ajouter la Foreign Key dans la base (Recommandé)
```sql
-- Se connecter à PostgreSQL
psql -U postgres -d exam_surveillance

-- Ajouter la foreign key
ALTER TABLE planif_salle 
ADD CONSTRAINT fk_planif_salle_groupe 
FOREIGN KEY (groupe_id) REFERENCES groupe(id) ON DELETE SET NULL;
```

#### Option 2 : Modifier le modèle pour ne pas utiliser la relation
Dans `server/app/models/planification.py`, remplacer :
```python
groupe: Mapped["Groupe"] = relationship("Groupe", lazy="selectin")
```

Par :
```python
# Relation commentée car pas de FK dans la DB
# groupe: Mapped["Groupe"] = relationship("Groupe", lazy="selectin")
```

Et dans `server/app/algorithms/surv_auto.py`, charger manuellement :
```python
# Au lieu de : grp = ligne.groupe
from app.models.departement_niveau_section import Groupe
grp = self.db.query(Groupe).filter(Groupe.id == ligne.groupe_id).first()
```

## ✅ Vérification Finale

Une fois le serveur redémarré, testez l'endpoint :
```bash
curl -X POST http://localhost:8000/api/surveillances/affecter-session \
  -H "Content-Type: application/json" \
  -d '{"session_id":1}'
```

Si ça fonctionne, vous devriez voir une réponse JSON avec les résultats de l'affectation.

## 📞 Besoin d'Aide ?

Si le problème persiste :
1. Vérifier les logs du serveur backend
2. Vérifier que PostgreSQL est bien démarré
3. Vérifier la connexion à la base de données
4. Consulter `SURVEILLANCE_READY.md` pour plus de détails
