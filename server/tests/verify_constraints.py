#!/usr/bin/env python3
"""
Script de vérification de l'implémentation des 18 contraintes.
Vérifie que toutes les contraintes sont présentes et fonctionnelles.
"""

from datetime import date, time

from app.algorithms.contraintes import (
    ContrainteBatimentConsecutif,
    ContrainteCapaciteSalle,
    ContrainteCreneauSession,
    ContrainteDecoupageObligatoire,
    ContrainteDureeCreneau,
    ContrainteEquilibrageGroupes,
    ContrainteEspacementExamens,
    ContrainteMatiereEligible,
    ContraintePasDimanche,
    ContrainteRepartitionUniforme,
    ContrainteSalleOccupee,
    ContrainteSectionMatiereUnique,
    ContrainteSectionUnique,
    ContrainteSectionMatiereExists,
    ContrainteSessionEditable,
    build_default_engine,
)
from app.schemas.planification import (
    ModeAffectation,
    PlanifSalleAssign,
    PlanificationCreate,
    StatutSession,
    TypeEpreuve,
)


def create_valid_planif() -> PlanificationCreate:
    """Créer une planification valide pour les tests."""
    return PlanificationCreate(
        session_id=1,
        section_id=1,
        section_matiere_id=10,
        matiere="Test Matière",
        type_epreuve=TypeEpreuve.EXAMEN_FINAL,
        mode_affectation=ModeAffectation.AUTO,
        date_examen=date(2026, 6, 3),  # Mardi
        heure_debut=time(8, 30),
        heure_fin=time(10, 30),
        session_date_debut=date(2026, 6, 1),
        session_date_fin=date(2026, 6, 30),
        session_statut=StatutSession.BROUILLON,
        duree=120,
        coefficient=2.0,
        section_nb_etudiants=30,
        nb_groupes=1,
        nb_surveillants_requis=2,
        a_examen_final=True,
        a_ds=True,
        salles=[
            PlanifSalleAssign(
                salle_id="S22",
                salle_capacite=40,
                salle_batiment="A",
                groupe_id=1,
                groupe_effectif=30,
            )
        ],
    )


def test_contrainte(contrainte, nom, test_valide, test_invalide):
    """Tester une contrainte avec un cas valide et un cas invalide."""
    
    print(f"\n🔍 Test {nom}")
    print("-" * 60)
    
    # Test cas valide
    planif_valide, contexte_valide = test_valide()
    resultat_valide = contrainte.verifier(planif_valide, contexte_valide, None)
    
    if resultat_valide:
        print(f"  ✅ Cas valide : PASS")
    else:
        print(f"  ❌ Cas valide : FAIL (devrait être valide)")
        print(f"     Message : {contrainte.get_message()}")
        return False
    
    # Test cas invalide
    planif_invalide, contexte_invalide = test_invalide()
    resultat_invalide = contrainte.verifier(planif_invalide, contexte_invalide, None)
    
    if not resultat_invalide:
        print(f"  ✅ Cas invalide : PASS (violation détectée)")
        print(f"     Message : {contrainte.get_message()}")
    else:
        print(f"  ❌ Cas invalide : FAIL (devrait être invalide)")
        return False
    
    return True


def main():
    """Point d'entrée principal."""
    
    print("\n" + "=" * 80)
    print("🔬 VÉRIFICATION DE L'IMPLÉMENTATION DES 18 CONTRAINTES")
    print("=" * 80)
    
    resultats = {}
    
    # ========== CONTRAINTES DURES ==========
    
    print("\n" + "=" * 80)
    print("🔴 CONTRAINTES DURES (11)")
    print("=" * 80)
    
    # C1 : Salle occupée
    def test_c1_valide():
        planif = create_valid_planif()
        return planif, {"existing_planifs": []}
    
    def test_c1_invalide():
        planif = create_valid_planif()
        existing = create_valid_planif()
        existing.id = 999
        return planif, {"existing_planifs": [existing]}
    
    resultats["C1"] = test_contrainte(
        ContrainteSalleOccupee(priorite=1),
        "C1 - Salle unique par créneau",
        test_c1_valide,
        test_c1_invalide,
    )
    
    # C2 : Capacité salle
    def test_c2_valide():
        planif = create_valid_planif()
        return planif, {}
    
    def test_c2_invalide():
        planif = create_valid_planif()
        planif.salles[0].salle_capacite = 10  # Trop petit pour 30 étudiants
        return planif, {}
    
    resultats["C2"] = test_contrainte(
        ContrainteCapaciteSalle(priorite=1),
        "C2 - Capacité salle ≥ effectif",
        test_c2_valide,
        test_c2_invalide,
    )
    
    # C3/C18 : Créneau dans session
    def test_c3_valide():
        planif = create_valid_planif()
        return planif, {}
    
    def test_c3_invalide():
        planif = create_valid_planif()
        planif.date_examen = date(2026, 7, 1)  # Hors période
        return planif, {}
    
    resultats["C3/C18"] = test_contrainte(
        ContrainteCreneauSession(priorite=1),
        "C3/C18 - Créneau dans période session",
        test_c3_valide,
        test_c3_invalide,
    )
    
    # C4 : Pas dimanche
    def test_c4_valide():
        planif = create_valid_planif()
        planif.date_examen = date(2026, 6, 3)  # Mardi
        return planif, {}
    
    def test_c4_invalide():
        planif = create_valid_planif()
        planif.date_examen = date(2026, 6, 7)  # Dimanche
        return planif, {}
    
    resultats["C4"] = test_contrainte(
        ContraintePasDimanche(priorite=1),
        "C4 - Pas d'examen le dimanche",
        test_c4_valide,
        test_c4_invalide,
    )
    
    # C6/C12 : Section-matière unique
    def test_c6_valide():
        planif = create_valid_planif()
        return planif, {"existing_planifs": []}
    
    def test_c6_invalide():
        planif = create_valid_planif()
        existing = create_valid_planif()
        existing.id = 999
        return planif, {"existing_planifs": [existing]}
    
    resultats["C6/C12"] = test_contrainte(
        ContrainteSectionMatiereUnique(priorite=1),
        "C6/C12 - Unicité (section_matiere, session, type)",
        test_c6_valide,
        test_c6_invalide,
    )
    
    # C7/C14 : Section unique
    def test_c7_valide():
        planif = create_valid_planif()
        return planif, {"existing_planifs": []}
    
    def test_c7_invalide():
        planif = create_valid_planif()
        existing = create_valid_planif()
        existing.id = 999
        existing.section_matiere_id = 11  # Autre matière, même section
        return planif, {"existing_planifs": [existing]}
    
    resultats["C7/C14"] = test_contrainte(
        ContrainteSectionUnique(priorite=1),
        "C7/C14 - Pas de chevauchement section",
        test_c7_valide,
        test_c7_invalide,
    )
    
    # C8 : Découpage obligatoire
    def test_c8_valide():
        planif = create_valid_planif()
        planif.section_nb_etudiants = 80
        planif.salles = [
            PlanifSalleAssign(salle_id="S1", salle_capacite=40, groupe_id=1, groupe_effectif=40),
            PlanifSalleAssign(salle_id="S2", salle_capacite=40, groupe_id=2, groupe_effectif=40),
        ]
        return planif, {}
    
    def test_c8_invalide():
        planif = create_valid_planif()
        planif.section_nb_etudiants = 80
        planif.salles = [
            PlanifSalleAssign(salle_id="S1", salle_capacite=40, groupe_id=1, groupe_effectif=80),
        ]
        return planif, {}
    
    resultats["C8"] = test_contrainte(
        ContrainteDecoupageObligatoire(priorite=1),
        "C8 - Découpage obligatoire si nécessaire",
        test_c8_valide,
        test_c8_invalide,
    )
    
    # C11 : Matière éligible
    def test_c11_valide():
        planif = create_valid_planif()
        planif.type_epreuve = TypeEpreuve.EXAMEN_FINAL
        planif.a_examen_final = True
        return planif, {}
    
    def test_c11_invalide():
        planif = create_valid_planif()
        planif.type_epreuve = TypeEpreuve.EXAMEN_FINAL
        planif.a_examen_final = False
        return planif, {}
    
    resultats["C11"] = test_contrainte(
        ContrainteMatiereEligible(priorite=1),
        "C11 - Matière éligible pour type épreuve",
        test_c11_valide,
        test_c11_invalide,
    )
    
    # C15 : Durée créneau
    def test_c15_valide():
        planif = create_valid_planif()
        planif.duree = 120
        planif.heure_debut = time(8, 30)
        planif.heure_fin = time(10, 30)
        return planif, {}
    
    def test_c15_invalide():
        planif = create_valid_planif()
        planif.duree = 180
        planif.heure_debut = time(8, 30)
        planif.heure_fin = time(10, 30)  # Seulement 120 min
        return planif, {}
    
    resultats["C15"] = test_contrainte(
        ContrainteDureeCreneau(priorite=1),
        "C15 - Durée épreuve ≤ durée créneau",
        test_c15_valide,
        test_c15_invalide,
    )
    
    # C16 : section_matiere existe
    def test_c16_valide():
        planif = create_valid_planif()
        planif.section_matiere_id = 10
        return planif, {"known_section_matiere_ids": {10, 11, 12}}
    
    def test_c16_invalide():
        planif = create_valid_planif()
        planif.section_matiere_id = 999
        return planif, {"known_section_matiere_ids": {10, 11, 12}}
    
    resultats["C16"] = test_contrainte(
        ContrainteSectionMatiereExists(priorite=1),
        "C16 - section_matiere doit exister",
        test_c16_valide,
        test_c16_invalide,
    )
    
    # C17 : Session éditable
    def test_c17_valide():
        planif = create_valid_planif()
        planif.session_statut = StatutSession.BROUILLON
        return planif, {}
    
    def test_c17_invalide():
        planif = create_valid_planif()
        planif.session_statut = StatutSession.PUBLIEE
        return planif, {}
    
    resultats["C17"] = test_contrainte(
        ContrainteSessionEditable(priorite=1),
        "C17 - Session éditable (BROUILLON/VALIDEE)",
        test_c17_valide,
        test_c17_invalide,
    )
    
    # ========== CONTRAINTES SOUPLES ==========
    
    print("\n" + "=" * 80)
    print("🟡 CONTRAINTES SOUPLES (7)")
    print("=" * 80)
    
    # C5 : Bâtiment consécutif
    def test_c5_valide():
        planif = create_valid_planif()
        planif.salles[0].salle_batiment = "A"
        return planif, {"existing_planifs": []}
    
    def test_c5_invalide():
        planif = create_valid_planif()
        planif.salles[0].salle_batiment = "B"
        existing = create_valid_planif()
        existing.id = 999
        existing.section_matiere_id = 11
        existing.salles_affectees = [
            type('obj', (object,), {'salle_batiment': 'A'})()
        ]
        return planif, {"existing_planifs": [existing]}
    
    resultats["C5"] = test_contrainte(
        ContrainteBatimentConsecutif(priorite=2, dure=False),
        "C5 - Préférence même bâtiment (souple)",
        test_c5_valide,
        test_c5_invalide,
    )
    
    # C9 : Équilibrage groupes
    def test_c9_valide():
        planif = create_valid_planif()
        planif.salles = [
            PlanifSalleAssign(salle_id="S1", salle_capacite=20, groupe_id=1, groupe_effectif=15),
            PlanifSalleAssign(salle_id="S2", salle_capacite=20, groupe_id=2, groupe_effectif=15),
        ]
        return planif, {}
    
    def test_c9_invalide():
        planif = create_valid_planif()
        planif.salles = [
            PlanifSalleAssign(salle_id="S1", salle_capacite=20, groupe_id=1, groupe_effectif=20),
            PlanifSalleAssign(salle_id="S2", salle_capacite=20, groupe_id=2, groupe_effectif=10),
        ]
        return planif, {}
    
    resultats["C9"] = test_contrainte(
        ContrainteEquilibrageGroupes(priorite=2, dure=False),
        "C9 - Équilibrage groupes (écart ≤ 1) (souple)",
        test_c9_valide,
        test_c9_invalide,
    )
    
    # C10 : Espacement examens
    def test_c10_valide():
        planif = create_valid_planif()
        return planif, {"existing_planifs": []}
    
    def test_c10_invalide():
        planif = create_valid_planif()
        planif.heure_debut = time(11, 0)
        existing = create_valid_planif()
        existing.id = 999
        existing.section_matiere_id = 11
        existing.heure_debut = time(8, 30)
        return planif, {"existing_planifs": [existing]}
    
    resultats["C10"] = test_contrainte(
        ContrainteEspacementExamens(priorite=3, dure=False),
        "C10 - Espacement examens (souple)",
        test_c10_valide,
        test_c10_invalide,
    )
    
    # C13 : Répartition uniforme
    def test_c13_valide():
        planif = create_valid_planif()
        planif.date_examen = date(2026, 6, 15)  # Milieu de période
        return planif, {"existing_planifs": []}
    
    def test_c13_invalide():
        planif = create_valid_planif()
        planif.date_examen = date(2026, 6, 2)  # Début de période
        existing1 = create_valid_planif()
        existing1.id = 998
        existing1.section_matiere_id = 11
        existing1.date_examen = date(2026, 6, 1)
        existing2 = create_valid_planif()
        existing2.id = 999
        existing2.section_matiere_id = 12
        existing2.date_examen = date(2026, 6, 2)
        return planif, {"existing_planifs": [existing1, existing2]}
    
    resultats["C13"] = test_contrainte(
        ContrainteRepartitionUniforme(priorite=3, dure=False),
        "C13 - Répartition uniforme (souple)",
        test_c13_valide,
        test_c13_invalide,
    )
    
    # ========== RÉSUMÉ ==========
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    
    nb_total = len(resultats)
    nb_reussis = sum(1 for r in resultats.values() if r)
    nb_echoues = nb_total - nb_reussis
    
    print(f"\n✅ Tests réussis : {nb_reussis}/{nb_total}")
    print(f"❌ Tests échoués : {nb_echoues}/{nb_total}")
    
    if nb_echoues > 0:
        print("\n⚠️  Contraintes échouées :")
        for nom, resultat in resultats.items():
            if not resultat:
                print(f"  - {nom}")
    
    # Test du moteur complet
    print("\n" + "=" * 80)
    print("🔧 TEST DU MOTEUR COMPLET")
    print("=" * 80)
    
    engine = build_default_engine()
    print(f"\n✅ Moteur créé avec {len(engine.contraintes)} contraintes")
    
    planif_test = create_valid_planif()
    errors, warnings = engine.verifier_toutes(planif_test, {"existing_planifs": []}, None)
    
    print(f"\n📋 Test sur planification valide :")
    print(f"  - Erreurs : {len(errors)}")
    print(f"  - Warnings : {len(warnings)}")
    
    if errors:
        print("\n❌ Erreurs détectées (ne devrait pas y en avoir) :")
        for err in errors:
            print(f"  - {err}")
    else:
        print("\n✅ Aucune erreur détectée (OK)")
    
    # Conclusion
    print("\n" + "=" * 80)
    print("🎓 CONCLUSION")
    print("=" * 80)
    
    if nb_echoues == 0 and not errors:
        print("\n✅ Toutes les contraintes sont correctement implémentées !")
        print("✅ Le moteur de contraintes fonctionne parfaitement !")
        print("✅ Le système est prêt pour la production !")
    else:
        print("\n⚠️  Certaines contraintes nécessitent des corrections")
        print("💡 Vérifier les tests échoués ci-dessus")
    
    print("\n" + "=" * 80 + "\n")
    
    return nb_echoues == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
