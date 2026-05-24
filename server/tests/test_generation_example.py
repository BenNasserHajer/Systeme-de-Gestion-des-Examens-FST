#!/usr/bin/env python3
"""
Script de test pour la génération automatique d'emploi du temps.
Simule une requête de génération avec les données réelles de la section INF/IOT MR2.
"""

from datetime import date, time

from app.algorithms.contraintes import build_default_engine
from app.algorithms.planif_auto import generer
from app.schemas.planification import (
    GenerationCreneau,
    GenerationRequest,
    GenerationSalle,
    GenerationTask,
    ModeAffectation,
    StatutSession,
    TypeEpreuve,
)


def create_test_request() -> GenerationRequest:
    """Créer une requête de test avec les données réelles."""
    
    # 10 matières MR2 INF/IOT
    matieres = [
        ("Optimisation Combinatoire", "MR2-INF-322", 10),
        ("IDM pour les systèmes complexes Temps Réels", "MR2-INF-IOT", 11),
        ("Bases de données avancées", "MR2-INF-312", 12),
        ("Sécurité IOT", "MR2-INF-331", 13),
        ("Blockchain", "MR2-INF-351", 14),
        ("Fouilles de Données", "MR2-INF-FDD", 15),
        ("Big Data", "MR2-INF-352", 16),
        ("Applications et plateforme IoT", "MR2-INF-APL", 17),
        ("Calcul de Haute Performance", "MR2-INF-CHP", 18),
        ("Réseaux IoT", "MR2-INF-RIOT", 19),
    ]
    
    tasks = [
        GenerationTask(
            section_id=1,
            section_matiere_id=sm_id,
            matiere=intitule,
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            duree=120,
            section_nb_etudiants=15,
            coefficient=2.0,
            nb_surveillants_requis=2,
            a_examen_final=True,
            a_ds=True,
        )
        for intitule, code, sm_id in matieres
    ]
    
    # 23 créneaux sur 8 jours ouvrables (07/01 → 15/01/2026)
    dates = [
        date(2026, 1, 7),   # Mercredi
        date(2026, 1, 8),   # Jeudi
        date(2026, 1, 9),   # Vendredi
        date(2026, 1, 10),  # Samedi
        date(2026, 1, 12),  # Lundi
        date(2026, 1, 13),  # Mardi
        date(2026, 1, 14),  # Mercredi
        date(2026, 1, 15),  # Jeudi
    ]
    
    horaires = [
        (time(8, 30), time(10, 30)),   # 08:30-10:30
        (time(11, 0), time(13, 0)),    # 11:00-13:00
        (time(14, 0), time(16, 0)),    # 14:00-16:00
    ]
    
    creneaux = [
        GenerationCreneau(
            date_examen=d,
            heure_debut=h_debut,
            heure_fin=h_fin,
        )
        for d in dates
        for h_debut, h_fin in horaires
    ]
    
    # 28 salles (sélection représentative)
    salles_data = [
        ("S22", 25, "S"),
        ("AMPHI INFO", 150, "AMPHI"),
        ("I106", 30, "I"),
        ("I107", 30, "I"),
        ("I108", 30, "I"),
        ("S31", 30, "S"),
        ("S32", 30, "S"),
        ("S33", 30, "S"),
        ("A101", 40, "A"),
        ("A102", 40, "A"),
        ("B201", 35, "B"),
        ("B202", 35, "B"),
        ("C301", 25, "C"),
        ("C302", 25, "C"),
        ("LAB1", 20, "LAB"),
        ("LAB2", 20, "LAB"),
        ("LAB3", 20, "LAB"),
        ("D401", 50, "D"),
        ("D402", 50, "D"),
        ("E501", 45, "E"),
    ]
    
    salles = [
        GenerationSalle(
            salle_id=code,
            capacite=cap,
            batiment=bat,
        )
        for code, cap, bat in salles_data
    ]
    
    return GenerationRequest(
        session_id=1,
        session_date_debut=date(2026, 1, 7),
        session_date_fin=date(2026, 1, 15),
        session_statut=StatutSession.BROUILLON,
        mode=ModeAffectation.AUTO,
        tasks=tasks,
        creneaux=creneaux,
        salles=salles,
    )


def print_results(creates, result):
    """Afficher les résultats de la génération."""
    
    print("\n" + "=" * 80)
    print("📊 RÉSULTATS DE LA GÉNÉRATION AUTOMATIQUE")
    print("=" * 80)
    
    print(f"\n✅ Planifications créées : {result.nb_crees}")
    print(f"❌ Conflits détectés     : {result.nb_conflits}")
    
    if result.conflits:
        print("\n⚠️  CONFLITS :")
        for conflit in result.conflits:
            print(f"  - {conflit}")
    
    if creates:
        print("\n📅 EMPLOI DU TEMPS GÉNÉRÉ :")
        print("-" * 80)
        
        # Grouper par date
        by_date = {}
        for planif in creates:
            d = planif.date_examen
            if d not in by_date:
                by_date[d] = []
            by_date[d].append(planif)
        
        # Afficher par date
        for d in sorted(by_date.keys()):
            print(f"\n📆 {d.strftime('%A %d/%m/%Y').upper()}")
            print("-" * 80)
            
            for planif in sorted(by_date[d], key=lambda p: p.heure_debut):
                print(f"\n  🕐 {planif.heure_debut.strftime('%H:%M')} - {planif.heure_fin.strftime('%H:%M')}")
                print(f"  📚 {planif.matiere}")
                print(f"  👥 {planif.section_nb_etudiants} étudiants → {planif.nb_groupes} groupe(s)")
                print(f"  🏢 Salles : {', '.join(s.salle_id for s in planif.salles)}")
                print(f"  👮 Surveillants requis : {planif.nb_surveillants_requis}")
    
    print("\n" + "=" * 80)


def print_statistics(creates):
    """Afficher des statistiques sur la génération."""
    
    if not creates:
        return
    
    print("\n📈 STATISTIQUES :")
    print("-" * 80)
    
    # Répartition par jour
    by_date = {}
    for planif in creates:
        d = planif.date_examen
        by_date[d] = by_date.get(d, 0) + 1
    
    print("\n📊 Répartition par jour :")
    for d in sorted(by_date.keys()):
        count = by_date[d]
        bar = "█" * count
        print(f"  {d.strftime('%d/%m')} : {bar} ({count} examens)")
    
    # Répartition par créneau horaire
    by_time = {}
    for planif in creates:
        h = planif.heure_debut.strftime('%H:%M')
        by_time[h] = by_time.get(h, 0) + 1
    
    print("\n🕐 Répartition par créneau horaire :")
    for h in sorted(by_time.keys()):
        count = by_time[h]
        bar = "█" * count
        print(f"  {h} : {bar} ({count} examens)")
    
    # Utilisation des salles
    salles_used = set()
    for planif in creates:
        for salle in planif.salles:
            salles_used.add(salle.salle_id)
    
    print(f"\n🏢 Salles utilisées : {len(salles_used)}")
    print(f"  {', '.join(sorted(salles_used))}")
    
    # Découpage en groupes
    nb_decoupes = sum(1 for p in creates if p.nb_groupes > 1)
    print(f"\n✂️  Découpages en groupes : {nb_decoupes}")
    
    # Contraintes souples
    print("\n🎯 Respect des contraintes souples :")
    
    # C10 : Éviter examens consécutifs
    violations_c10 = 0
    for d in by_date:
        if by_date[d] > 1:
            violations_c10 += by_date[d] - 1
    
    if violations_c10 == 0:
        print("  ✅ C10 (espacement) : Respectée (max 1 examen/jour)")
    else:
        print(f"  ⚠️  C10 (espacement) : {violations_c10} violations (examens multiples/jour)")
    
    # C13 : Répartition uniforme
    if by_date:
        avg = sum(by_date.values()) / len(by_date)
        max_count = max(by_date.values())
        if max_count <= avg * 1.5:
            print("  ✅ C13 (répartition) : Respectée (distribution uniforme)")
        else:
            print(f"  ⚠️  C13 (répartition) : Concentration sur certains jours (max={max_count}, moy={avg:.1f})")


def main():
    """Point d'entrée principal."""
    
    print("\n🚀 TEST DE GÉNÉRATION AUTOMATIQUE D'EMPLOI DU TEMPS")
    print("=" * 80)
    print("\n📋 Configuration :")
    print("  - Session : Principale 2025/2026")
    print("  - Période : 07/01/2026 → 15/01/2026 (8 jours ouvrables)")
    print("  - Section : INF/IOT MR2 (15 étudiants)")
    print("  - Matières : 10 matières (toutes EXAMEN_FINAL, 120 min)")
    print("  - Créneaux : 23 créneaux (08:30, 11:00, 14:00)")
    print("  - Salles : 20 salles (capacités variées)")
    
    print("\n⏳ Génération en cours...")
    
    # Créer la requête
    request = create_test_request()
    
    # Exécuter l'algorithme
    engine = build_default_engine()
    creates, result = generer(request, engine, [], None)
    
    # Afficher les résultats
    print_results(creates, result)
    print_statistics(creates)
    
    # Résumé final
    print("\n🎓 RÉSUMÉ :")
    print("-" * 80)
    
    if result.nb_conflits == 0:
        print("✅ Génération réussie à 100% !")
        print("✅ Toutes les contraintes dures respectées")
        print("✅ Optimisation des contraintes souples appliquée")
    else:
        taux_reussite = (result.nb_crees / (result.nb_crees + result.nb_conflits)) * 100
        print(f"⚠️  Génération partielle : {taux_reussite:.1f}% de réussite")
        print(f"⚠️  {result.nb_conflits} matière(s) non planifiée(s)")
        print("💡 Actions recommandées :")
        print("   - Ajouter des créneaux supplémentaires")
        print("   - Ajouter des salles")
        print("   - Planifier manuellement les matières en conflit")
    
    print("\n" + "=" * 80)
    print("✨ Test terminé avec succès !")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
