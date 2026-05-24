"""
Script de diagnostic pour comprendre pourquoi toutes les planifications sont en conflit.
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.planification import Planification
from app.models.enseignant import Enseignant, ChargeHoraire
from app.models.departement_niveau_section import Departement


def diagnose():
    db: Session = SessionLocal()
    
    print("=" * 80)
    print("DIAGNOSTIC DES CONFLITS D'AFFECTATION")
    print("=" * 80)
    
    # 1. Vérifier les planifications VALIDEE
    planifs = db.query(Planification).filter(
        Planification.session_id == 1,
        Planification.statut == "VALIDEE"
    ).all()
    
    print(f"\n📋 Planifications VALIDEE dans session 1: {len(planifs)}")
    
    if not planifs:
        print("❌ Aucune planification VALIDEE trouvée!")
        return
    
    # 2. Analyser chaque planification
    for i, planif in enumerate(planifs, 1):
        print(f"\n{'─' * 80}")
        print(f"Planification #{i} (ID: {planif.id})")
        print(f"{'─' * 80}")
        
        # Info de base
        sm = planif.section_matiere
        mat = sm.matiere if sm else None
        sec = sm.section if sm else None
        
        print(f"  Matière: {mat.code if mat else 'N/A'} - {mat.intitule if mat else 'N/A'}")
        print(f"  Section: {sec.nom if sec else 'N/A'}")
        print(f"  Type: {planif.type_epreuve}")
        print(f"  Durée: {planif.duree}h")
        print(f"  Surveillants requis: {planif.nb_surveillants_requis}")
        
        # Département de l'examen
        dept_exam_id = planif.section_departement_id
        print(f"\n  🏢 Département examen ID: {dept_exam_id}")
        
        if dept_exam_id:
            dept_exam = db.query(Departement).filter(Departement.id == dept_exam_id).first()
            if dept_exam:
                print(f"     ✅ Département: {dept_exam.nom} ({dept_exam.code})")
            else:
                print(f"     ❌ Département ID {dept_exam_id} n'existe pas!")
        else:
            print(f"     ❌ section_departement_id est NULL!")
        
        # Créneau
        cren = planif.creneau
        if cren:
            print(f"\n  📅 Créneau: {cren.date} {cren.heure_debut}-{cren.heure_fin}")
        
        # Groupes et salles
        planif_salles = planif.salles_affectees
        print(f"\n  🏫 Groupes/Salles: {len(planif_salles)}")
        for ps in planif_salles:
            print(f"     - Groupe {ps.groupe_id}, Salle {ps.salle_id}")
    
    # 3. Analyser les enseignants disponibles
    print(f"\n{'=' * 80}")
    print("ANALYSE DES ENSEIGNANTS")
    print("=" * 80)
    
    enseignants = db.query(Enseignant).all()
    print(f"\n👥 Total enseignants: {len(enseignants)}")
    
    # Grouper par département
    dept_counts = {}
    for ens in enseignants:
        dept = ens.departement
        dept_name = dept.nom if dept else "Sans département"
        dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
    
    print("\n📊 Répartition par département:")
    for dept_name, count in sorted(dept_counts.items()):
        print(f"   {dept_name}: {count} enseignants")
    
    # 4. Analyser les charges horaires
    print(f"\n{'=' * 80}")
    print("ANALYSE DES CHARGES HORAIRES")
    print("=" * 80)
    
    charges = db.query(ChargeHoraire).filter(
        ChargeHoraire.annee_univ == "2025/2026"
    ).all()
    
    print(f"\n⏱️  Charges horaires pour 2025/2026: {len(charges)}")
    
    if charges:
        total_volume = sum(c.volume_horaire for c in charges if c.volume_horaire)
        avg_volume = total_volume / len(charges) if charges else 0
        print(f"   Volume total: {total_volume}h")
        print(f"   Volume moyen: {avg_volume:.1f}h par enseignant")
        
        # Enseignants avec volume > 0
        with_volume = [c for c in charges if c.volume_horaire and c.volume_horaire > 0]
        print(f"   Enseignants avec volume > 0: {len(with_volume)}")
    else:
        print("   ❌ Aucune charge horaire définie pour 2025/2026!")
    
    # 5. Recommandations
    print(f"\n{'=' * 80}")
    print("🔍 DIAGNOSTIC ET RECOMMANDATIONS")
    print("=" * 80)
    
    issues = []
    
    # Vérifier section_departement_id NULL
    null_dept = sum(1 for p in planifs if not p.section_departement_id)
    if null_dept > 0:
        issues.append(f"❌ {null_dept} planification(s) avec section_departement_id NULL")
        print(f"\n1. {issues[-1]}")
        print("   Solution:")
        print("   UPDATE planification_examen")
        print("   SET section_departement_id = 1")
        print("   WHERE session_id = 1 AND statut = 'VALIDEE';")
    
    # Vérifier charges horaires
    if not charges:
        issues.append("❌ Aucune charge horaire définie pour 2025/2026")
        print(f"\n2. {issues[-1]}")
        print("   Solution: Créer des charges horaires pour les enseignants")
    elif len(with_volume) < len(enseignants) / 2:
        issues.append(f"⚠️  Seulement {len(with_volume)}/{len(enseignants)} enseignants ont un volume horaire")
        print(f"\n3. {issues[-1]}")
        print("   Solution: Définir volume_horaire pour plus d'enseignants")
    
    # Vérifier disponibilités
    from app.models.disponibilite import DisponibiliteEnseignant
    dispos = db.query(DisponibiliteEnseignant).all()
    print(f"\n4. 📅 Disponibilités déclarées: {len(dispos)}")
    if len(dispos) == 0:
        print("   ℹ️  Aucune indisponibilité déclarée (OK - tous disponibles par défaut)")
    
    # Résumé
    print(f"\n{'=' * 80}")
    if issues:
        print(f"⚠️  {len(issues)} problème(s) détecté(s)")
        print("\nPriorité: Fixer section_departement_id NULL")
    else:
        print("✅ Configuration semble correcte")
        print("   Les conflits peuvent être dus à:")
        print("   - Contraintes de non-simultanéité")
        print("   - Contraintes de matière (enseignant ne surveille pas sa matière)")
        print("   - Volume horaire insuffisant")
    
    db.close()


if __name__ == "__main__":
    diagnose()
