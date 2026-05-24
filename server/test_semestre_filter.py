"""Test du filtrage par semestre."""

from app.database import SessionLocal
from app.services.catalogue_service import load_catalogue, build_generation_tasks_for_section

def test_semestre_filter():
    db = SessionLocal()
    try:
        # Load catalogue
        catalogue = load_catalogue(db)
        
        print("=" * 60)
        print("TEST FILTRAGE PAR SEMESTRE")
        print("=" * 60)
        
        # Get first section
        if not catalogue["sections"]:
            print("❌ Aucune section trouvée")
            return
        
        section = catalogue["sections"][0]
        section_id = section["section_id"]
        section_label = section["label"]
        
        print(f"\nSection: {section_label} (ID: {section_id})")
        
        # Show all matières with their semester
        matieres = catalogue["matieres_by_section"].get(section_label, [])
        print(f"\nTotal matières: {len(matieres)}")
        
        s1_count = 0
        s2_count = 0
        no_sem_count = 0
        
        for mat in matieres:
            sem = mat.get("semestre", "")
            if "1" in sem:
                s1_count += 1
            elif "2" in sem:
                s2_count += 1
            else:
                no_sem_count += 1
            print(f"  - {mat['matiere'][:40]:40} | Semestre: {sem or 'N/A'}")
        
        print(f"\nRépartition:")
        print(f"  S1: {s1_count} matières")
        print(f"  S2: {s2_count} matières")
        print(f"  Sans semestre: {no_sem_count} matières")
        
        # Test generation for S1
        print("\n" + "=" * 60)
        print("GÉNÉRATION POUR S1")
        print("=" * 60)
        try:
            tasks_s1 = build_generation_tasks_for_section(
                catalogue, section_id, "EXAMEN_FINAL", "S1"
            )
            print(f"✅ {len(tasks_s1)} matières générées pour S1:")
            for task in tasks_s1[:5]:  # Show first 5
                print(f"  - {task['matiere']}")
            if len(tasks_s1) > 5:
                print(f"  ... et {len(tasks_s1) - 5} autres")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test generation for S2
        print("\n" + "=" * 60)
        print("GÉNÉRATION POUR S2")
        print("=" * 60)
        try:
            tasks_s2 = build_generation_tasks_for_section(
                catalogue, section_id, "EXAMEN_FINAL", "S2"
            )
            print(f"✅ {len(tasks_s2)} matières générées pour S2:")
            for task in tasks_s2[:5]:  # Show first 5
                print(f"  - {task['matiere']}")
            if len(tasks_s2) > 5:
                print(f"  ... et {len(tasks_s2) - 5} autres")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("\n" + "=" * 60)
        print("✅ TEST TERMINÉ")
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    test_semestre_filter()
