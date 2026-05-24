"""
Test de planification d'examens avec des données réelles de la base de données.
"""

from datetime import date, time
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.algorithms.contraintes import build_default_engine
from app.algorithms.planif_auto import generer
from app.crud.crud_planif import create_planification, get_emploi_du_temps
from app.models.planification import Planification
from app.models.salle_session import Salle, Session, Creneau
from app.models.matiere import SectionMatiere
from app.schemas.planification import (
    GenerationRequest,
    GenerationCreneau,
    GenerationSalle,
    GenerationTask,
    StatutSession,
    TypeEpreuve,
    ModeAffectation,
)


def print_separator(title: str = ""):
    """Affiche un séparateur visuel."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    else:
        print(f"{'=' * 80}\n")


def get_database_stats(db: Session):
    """Récupère les statistiques de la base de données."""
    print_separator("📊 STATISTIQUES DE LA BASE DE DONNÉES")
    
    sessions = db.query(Session).all()
    salles = db.query(Salle).all()
    creneaux = db.query(Creneau).all()
    section_matieres = db.query(SectionMatiere).all()
    planifs_existantes = db.query(Planification).all()
    
    print(f"Sessions d'examen : {len(sessions)}")
    print(f"Salles disponibles : {len(salles)}")
    print(f"Créneaux définis : {len(creneaux)}")
    print(f"Section-Matières : {len(section_matieres)}")
    print(f"Planifications existantes : {len(planifs_existantes)}")
    
    if sessions:
        print("\n📅 Sessions disponibles :")
        for s in sessions:
            print(f"  - ID {s.id}: {s.type_session} {s.annee_universitaire}")
            print(f"    Période: {s.date_debut} → {s.date_fin}")
            print(f"    Statut: {s.statut}")
    
    return sessions, salles, creneaux, section_matieres


def display_salles(salles: list[Salle], limit: int = 10):
    """Affiche les salles disponibles."""
    print_separator("🏫 SALLES DISPONIBLES")
    
    # Grouper par bâtiment
    salles_par_batiment = {}
    for salle in salles:
        bat = salle.batiment or "Sans bâtiment"
        if bat not in salles_par_batiment:
            salles_par_batiment[bat] = []
        salles_par_batiment[bat].append(salle)
    
    for batiment, salles_bat in sorted(salles_par_batiment.items()):
        print(f"\n📍 Bâtiment {batiment} ({len(salles_bat)} salles):")
        for salle in sorted(salles_bat, key=lambda s: s.capacite, reverse=True)[:limit]:
            print(f"  - {salle.code}: capacité {salle.capacite}")
    
    capacite_totale = sum(s.capacite for s in salles)
    capacite_moyenne = capacite_totale / len(salles) if salles else 0
    print(f"\n📈 Capacité totale: {capacite_totale} places")
    print(f"📊 Capacité moyenne: {capacite_moyenne:.1f} places/salle")


def display_creneaux(creneaux: list[Creneau], session: Session, limit: int = 10):
    """Affiche les créneaux disponibles pour une session."""
    print_separator("⏰ CRÉNEAUX DISPONIBLES")
    
    # Filtrer les créneaux dans la période de la session
    creneaux_session = [
        c for c in creneaux 
        if session.date_debut <= c.date <= session.date_fin
    ]
    
    # Grouper par date
    creneaux_par_date = {}
    for creneau in creneaux_session:
        if creneau.date not in creneaux_par_date:
            creneaux_par_date[creneau.date] = []
        creneaux_par_date[creneau.date].append(creneau)
    
    print(f"Créneaux dans la période {session.date_debut} → {session.date_fin}:")
    print(f"Total: {len(creneaux_session)} créneaux sur {len(creneaux_par_date)} jours\n")
    
    for jour, creneaux_jour in sorted(creneaux_par_date.items())[:limit]:
        jour_semaine = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"][jour.weekday()]
        print(f"📅 {jour_semaine} {jour}:")
        for creneau in sorted(creneaux_jour, key=lambda c: c.heure_debut):
            duree = (creneau.heure_fin.hour * 60 + creneau.heure_fin.minute) - \
                    (creneau.heure_debut.hour * 60 + creneau.heure_debut.minute)
            print(f"  - {creneau.heure_debut.strftime('%H:%M')} → "
                  f"{creneau.heure_fin.strftime('%H:%M')} ({duree} min)")


def display_section_matieres(section_matieres: list[SectionMatiere], limit: int = 10):
    """Affiche les matières à planifier."""
    print_separator("📚 MATIÈRES À PLANIFIER")
    
    # Filtrer celles qui ont des examens
    avec_examen = [sm for sm in section_matieres if sm.a_examen_final]
    
    print(f"Total: {len(section_matieres)} section-matières")
    print(f"Avec examen final: {len(avec_examen)}\n")
    
    print(f"Échantillon (premières {limit}) :")
    for sm in avec_examen[:limit]:
        section = sm.section
        matiere = sm.matiere
        
        # Calculer le nombre total d'étudiants à partir des groupes
        nb_etudiants = sum(g.nb_etudiants for g in section.groupes) if section.groupes else 0
        
        print(f"\n  📖 {matiere.intitule} ({matiere.code})")
        print(f"     Section: {section.nom}")
        print(f"     Étudiants: {nb_etudiants} ({len(section.groupes)} groupes)")
        print(f"     Durée examen: {sm.duree_examen} min")
        print(f"     Coefficient: {matiere.coefficient}")
        print(f"     Année/Semestre: {sm.annee_sem}")


def test_generation_simple(db: Session, session: Session, salles: list[Salle], 
                          creneaux: list[Creneau], section_matieres: list[SectionMatiere]):
    """Test de génération avec un petit échantillon de matières."""
    print_separator("🧪 TEST DE GÉNÉRATION (ÉCHANTILLON)")
    
    # Sélectionner quelques matières pour le test
    matieres_test = [sm for sm in section_matieres if sm.a_examen_final][:5]
    
    if not matieres_test:
        print("❌ Aucune matière avec examen final trouvée!")
        return
    
    print(f"Matières sélectionnées pour le test: {len(matieres_test)}")
    for sm in matieres_test:
        nb_etudiants = sum(g.nb_etudiants for g in sm.section.groupes) if sm.section.groupes else 0
        print(f"  - {sm.matiere.intitule} (Section: {sm.section.nom}, "
              f"{nb_etudiants} étudiants)")
    
    # Préparer les créneaux pour la génération
    creneaux_session = [
        c for c in creneaux 
        if session.date_debut <= c.date <= session.date_fin
    ][:10]  # Limiter à 10 créneaux pour le test
    
    generation_creneaux = [
        GenerationCreneau(
            date_examen=c.date,
            heure_debut=c.heure_debut,
            heure_fin=c.heure_fin
        )
        for c in creneaux_session
    ]
    
    # Préparer les salles
    generation_salles = [
        GenerationSalle(
            salle_id=s.code,
            capacite=s.capacite,
            batiment=s.batiment
        )
        for s in salles
    ]
    
    # Préparer les tâches
    generation_tasks = []
    for sm in matieres_test:
        # Calculer le nombre total d'étudiants
        nb_etudiants = sum(g.nb_etudiants for g in sm.section.groupes) if sm.section.groupes else 0
        
        # Si aucun étudiant, skip cette matière
        if nb_etudiants == 0:
            continue
        
        # Extraire le semestre de annee_sem (ex: "2025/2026-S1" -> "S1")
        semestre = "S1"
        if sm.annee_sem and "-S" in sm.annee_sem:
            semestre = sm.annee_sem.split("-")[1]
        
        generation_tasks.append(
            GenerationTask(
                section_id=sm.section_id,
                section_matiere_id=sm.id,
                matiere_id=sm.matiere_id,
                matiere=sm.matiere.intitule,
                semestre=semestre,
                section_departement_id=sm.section.niveau.departement_id if sm.section.niveau else None,
                type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                duree=sm.duree_examen or 120,
                section_nb_etudiants=nb_etudiants,
                coefficient=float(sm.matiere.coefficient),
                nb_surveillants_requis=2,
                a_examen_final=sm.a_examen_final,
                a_ds=sm.a_ds,
            )
        )
    
    # Créer la requête de génération
    request = GenerationRequest(
        session_id=session.id,
        session_date_debut=session.date_debut,
        session_date_fin=session.date_fin,
        session_statut=StatutSession(session.statut),
        annee_universitaire=session.annee_universitaire,
        semestre="S1",
        mode=ModeAffectation.AUTO,
        tasks=generation_tasks,
        creneaux=generation_creneaux,
        salles=generation_salles,
    )
    
    print(f"\n🔧 Configuration de la génération:")
    print(f"  - Session: {session.type_session} {session.annee_universitaire}")
    print(f"  - Période: {session.date_debut} → {session.date_fin}")
    print(f"  - Matières: {len(generation_tasks)}")
    print(f"  - Créneaux: {len(generation_creneaux)}")
    print(f"  - Salles: {len(generation_salles)}")
    
    # Récupérer les planifications existantes
    existing_planifs = db.query(Planification).filter(
        Planification.session_id == session.id
    ).all()
    
    print(f"\n⚙️ Lancement de la génération...")
    
    # Générer
    engine = build_default_engine()
    creates, result = generer(
        request=request,
        engine=engine,
        existing_planifs=existing_planifs,
        db=db,
        known_section_matiere_ids={sm.id for sm in section_matieres}
    )
    
    # Afficher les résultats
    print_separator("📊 RÉSULTATS DE LA GÉNÉRATION")
    
    print(f"✅ Planifications créées: {result.nb_crees}")
    print(f"⚠️  Conflits détectés: {result.nb_conflits}")
    
    if result.conflits:
        print(f"\n❌ Détails des conflits:")
        for conflit in result.conflits:
            print(f"  - {conflit}")
    
    if creates:
        print(f"\n📝 Planifications générées:")
        for i, planif in enumerate(creates, 1):
            print(f"\n  {i}. {planif.matiere}")
            print(f"     📅 Date: {planif.date_examen}")
            print(f"     ⏰ Horaire: {planif.heure_debut.strftime('%H:%M')} → "
                  f"{planif.heure_fin.strftime('%H:%M')}")
            print(f"     ⏱️  Durée: {planif.duree} min")
            print(f"     👥 Étudiants: {planif.section_nb_etudiants}")
            print(f"     🏫 Groupes: {planif.nb_groupes}")
            print(f"     📍 Salles:")
            for salle in planif.salles:
                print(f"        • {salle.salle_id} (capacité: {salle.salle_capacite}, "
                      f"groupe {salle.groupe_id}: {salle.groupe_effectif} étudiants)")
    
    return creates, result


def save_to_database(db: Session, creates: list):
    """Sauvegarde les planifications dans la base de données."""
    print_separator("💾 SAUVEGARDE DANS LA BASE DE DONNÉES")
    
    if not creates:
        print("Aucune planification à sauvegarder.")
        return []
    
    saved = []
    errors = []
    
    for i, planif_create in enumerate(creates, 1):
        try:
            print(f"Sauvegarde {i}/{len(creates)}: {planif_create.matiere}...", end=" ")
            planif = create_planification(db, planif_create)
            saved.append(planif)
            print("✅")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            errors.append((planif_create.matiere, str(e)))
    
    print(f"\n📊 Résumé:")
    print(f"  ✅ Sauvegardées: {len(saved)}")
    print(f"  ❌ Erreurs: {len(errors)}")
    
    if errors:
        print(f"\n❌ Détails des erreurs:")
        for matiere, error in errors:
            print(f"  - {matiere}: {error}")
    
    return saved


def display_emploi_du_temps(db: Session, session_id: int):
    """Affiche l'emploi du temps généré."""
    print_separator("📅 EMPLOI DU TEMPS GÉNÉRÉ")
    
    emploi = get_emploi_du_temps(db, session_id=session_id)
    
    if not emploi:
        print("Aucune planification trouvée pour cette session.")
        return
    
    print(f"Total: {len(emploi)} examens planifiés\n")
    
    # Grouper par date
    par_date = {}
    for planif in emploi:
        if planif.date_examen not in par_date:
            par_date[planif.date_examen] = []
        par_date[planif.date_examen].append(planif)
    
    for jour, planifs_jour in sorted(par_date.items()):
        jour_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][jour.weekday()]
        print(f"\n📅 {jour_semaine} {jour}")
        print(f"{'─' * 80}")
        
        for planif in sorted(planifs_jour, key=lambda p: p.heure_debut):
            print(f"\n  ⏰ {planif.heure_debut.strftime('%H:%M')} - "
                  f"{planif.heure_fin.strftime('%H:%M')}")
            print(f"  📖 {planif.matiere}")
            print(f"  👥 {planif.section_nb_etudiants} étudiants en {planif.nb_groupes} groupe(s)")
            
            salles_str = ", ".join([s.salle_id for s in planif.salles_affectees])
            print(f"  🏫 Salles: {salles_str}")


def main():
    """Fonction principale de test."""
    print_separator("🚀 TEST DE PLANIFICATION D'EXAMENS AVEC DONNÉES RÉELLES")
    
    db = SessionLocal()
    
    try:
        # 1. Récupérer les statistiques
        sessions, salles, creneaux, section_matieres = get_database_stats(db)
        
        if not sessions:
            print("\n❌ Aucune session trouvée dans la base de données!")
            print("Veuillez d'abord créer une session d'examen.")
            return
        
        # Utiliser la première session
        session = sessions[0]
        
        # 2. Afficher les ressources disponibles
        display_salles(salles)
        display_creneaux(creneaux, session)
        display_section_matieres(section_matieres)
        
        # 3. Demander confirmation
        print_separator("⚠️  CONFIRMATION")
        print(f"Vous allez tester la génération pour la session:")
        print(f"  - {session.type_session} {session.annee_universitaire}")
        print(f"  - Période: {session.date_debut} → {session.date_fin}")
        print(f"  - Statut: {session.statut}")
        print(f"\nCe test va générer des planifications pour 5 matières (échantillon).")
        
        response = input("\nContinuer? (o/n): ").strip().lower()
        if response != 'o':
            print("Test annulé.")
            return
        
        # 4. Générer les planifications
        creates, result = test_generation_simple(
            db, session, salles, creneaux, section_matieres
        )
        
        if not creates:
            print("\n❌ Aucune planification générée.")
            return
        
        # 5. Demander si on sauvegarde
        print_separator("💾 SAUVEGARDE")
        response = input(f"Voulez-vous sauvegarder ces {len(creates)} planifications? (o/n): ").strip().lower()
        
        if response == 'o':
            saved = save_to_database(db, creates)
            
            if saved:
                # 6. Afficher l'emploi du temps
                display_emploi_du_temps(db, session.id)
                
                print_separator("✅ TEST TERMINÉ AVEC SUCCÈS")
                print(f"✅ {len(saved)} planifications sauvegardées dans la base de données")
                print(f"📊 Vous pouvez maintenant consulter l'emploi du temps via l'API ou le frontend")
        else:
            print("\nPlanifications non sauvegardées (test uniquement).")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
