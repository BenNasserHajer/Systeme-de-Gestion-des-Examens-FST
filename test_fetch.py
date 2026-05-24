import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "server"))

from app.database import SessionLocal
from app.algorithms.surv_auto import AutomaticAffectationAlgorithm
from app.models.planification import Planification

db = SessionLocal()
algo = AutomaticAffectationAlgorithm(db)

# Find a valid session id
from app.models.salle_session import Session
session = db.query(Session).first()
if not session:
    print("No session found")
    sys.exit(0)

print(f"Testing session: {session.id} {session.annee_universitaire}")

# Test affecter_session
results, msg = algo.affecter_session(session.id, None, None, None)
print("Message:", msg)
for r in results:
    print(f"Planif {r.planification_id} statut: {r.statut} (requis: {r.surveillants_requis}, affectes: {len(r.surveillants_affectes)}, manquants: {r.manquants})")
