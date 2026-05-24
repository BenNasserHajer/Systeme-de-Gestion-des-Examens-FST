"""Test catalogue loading."""

from app.database import SessionLocal
from app.services.catalogue_service import load_catalogue

def main():
    db = SessionLocal()
    try:
        cat = load_catalogue(db)
        print("=" * 60)
        print("CATALOGUE TEST")
        print("=" * 60)
        print(f"Source: {cat['source']}")
        print(f"Message: {cat['message']}")
        print(f"Sessions: {len(cat['sessions'])}")
        print(f"Sections: {len(cat['sections'])}")
        print(f"Salles: {len(cat['salles'])}")
        print(f"Creneaux: {len(cat['creneaux'])}")
        
        if cat['sections']:
            print("\nFirst 3 sections:")
            for section in cat['sections'][:3]:
                print(f"  - {section['label']}: {section['effectif']} students (niveau: {section['niveau']})")
                matieres = cat['matieres_by_section'].get(section['label'], [])
                print(f"    {len(matieres)} matières")
        
        print("\n✅ Catalogue loaded successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
