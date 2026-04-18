"""Business logic for surveillance load computation."""

from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.surveillance import Surveillance


class ChargeService:
    """Compute surveillance load by teacher."""

    def __init__(self, db: Session):
        self.db = db

    def compute_by_teacher(self) -> dict[str, float]:
        rows = self.db.query(Surveillance).all()
        loads: dict[str, float] = defaultdict(float)
        for row in rows:
            loads[row.enseignant] += row.charge
        return dict(loads)
