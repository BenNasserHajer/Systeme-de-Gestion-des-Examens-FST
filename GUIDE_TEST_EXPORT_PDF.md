# Guide de Test : Export PDF Planification

## 🎯 Objectif
Tester la nouvelle fonctionnalité d'export PDF de la planification des examens dans l'interface administrateur.

---

## 📋 Prérequis

1. **Serveur backend** : Doit être démarré
   ```bash
   cd server
   uvicorn main:app --reload
   ```

2. **Frontend** : Doit être démarré
   ```bash
   cd frontend
   npm run dev
   ```

3. **Compte administrateur** : Vous devez avoir un compte admin pour accéder à la page de planification

---

## 🧪 Scénario de Test

### Étape 1 : Connexion
1. Ouvrez votre navigateur et allez sur `http://localhost:3000/login`
2. Connectez-vous avec un compte administrateur
3. Vous devriez être redirigé vers la page d'accueil admin

### Étape 2 : Navigation vers Planification
1. Dans la barre de navigation supérieure, cliquez sur **"Planification"**
2. Vérifiez que :
   - ✅ La navbar est présente avec les logos UTM et FST
   - ✅ Il n'y a pas de sidebar latérale
   - ✅ Le lien "Planification" est actif (couleur indigo avec bordure)

### Étape 3 : Génération d'une Planification
1. Remplissez le formulaire de génération :
   - Sélectionnez une **Session**
   - Sélectionnez une **Section**
   - Sélectionnez un **Semestre** (S1 ou S2)
   - Sélectionnez un **Type d'épreuve** (EXAMEN_FINAL ou DS)

2. Cliquez sur **"Générer automatiquement"**

3. Attendez que la génération se termine
   - Des examens devraient apparaître dans le calendrier
   - Un message de succès devrait s'afficher

### Étape 4 : Export PDF
1. Dans l'en-tête de la page, vous devriez voir deux boutons :
   - **"Exporter en PDF"** (à gauche)
   - **"Valider (X)"** (à droite, où X est le nombre d'examens en brouillon)

2. Cliquez sur **"Exporter en PDF"**

3. Vérifiez que :
   - ✅ Le bouton affiche "Chargement..." pendant quelques secondes
   - ✅ Un fichier PDF est téléchargé automatiquement
   - ✅ Le nom du fichier suit le format : `planification-{session}-{section}-{semestre}.pdf`

### Étape 5 : Vérification du PDF
1. Ouvrez le fichier PDF téléchargé

2. Vérifiez le contenu :
   - ✅ **En-tête** :
     - Titre : "Emploi du Temps des Examens"
     - Sous-titre : "Université de Tunis El Manar · Faculté des Sciences de Tunis"
   
   - ✅ **Section d'informations** :
     - Session (type et année universitaire)
     - Section (label et effectif)
     - Semestre
     - Nombre d'examens
   
   - ✅ **Tableau des examens** :
     - Colonnes : Date | Horaire | Matière | Salles | Groupes
     - Les examens sont triés par date puis par heure
     - Les lignes alternent entre blanc et gris clair
     - Toutes les données sont présentes et lisibles
   
   - ✅ **Footer** :
     - Date et heure de génération du document

3. Vérifiez le format :
   - ✅ Le document est en format paysage (landscape)
   - ✅ Le tableau est bien visible et ne déborde pas
   - ✅ Les polices sont lisibles

---

## 🔍 Tests Supplémentaires

### Test 1 : Bouton désactivé sans examens
1. Allez sur la page de planification sans générer d'examens
2. Vérifiez que le bouton "Exporter en PDF" est **désactivé** (grisé)

### Test 2 : Bouton désactivé sans session
1. Si possible, réinitialisez la page
2. Vérifiez que le bouton est désactivé tant qu'aucune session n'est sélectionnée

### Test 3 : Export avec plusieurs examens
1. Générez une planification avec au moins 5-10 examens
2. Exportez en PDF
3. Vérifiez que tous les examens sont présents dans le PDF
4. Vérifiez que le tri par date/heure est correct

### Test 4 : Export avec différentes configurations
1. Testez avec différentes sessions
2. Testez avec différentes sections
3. Testez avec S1 et S2
4. Vérifiez que les informations dans le PDF sont correctes à chaque fois

---

## ❌ Gestion des Erreurs

### Si le bouton ne s'affiche pas
- Vérifiez que vous êtes bien sur la page `/planification`
- Vérifiez la console du navigateur pour des erreurs JavaScript
- Rafraîchissez la page (F5)

### Si le PDF ne se télécharge pas
- Vérifiez la console du navigateur pour des erreurs
- Vérifiez que votre navigateur autorise les téléchargements
- Essayez avec un autre navigateur

### Si le PDF est vide ou incomplet
- Vérifiez que des examens sont bien générés dans le calendrier
- Vérifiez la console pour des erreurs de transformation de données
- Essayez de régénérer la planification

### Si le PDF a des données incorrectes
- Vérifiez les données dans le calendrier (sont-elles correctes ?)
- Comparez avec les données affichées dans l'interface
- Signalez les incohérences

---

## 📊 Checklist de Test

- [ ] Connexion en tant qu'admin réussie
- [ ] Navigation vers Planification
- [ ] Navbar visible avec logos UTM/FST
- [ ] Pas de sidebar latérale
- [ ] Génération d'une planification réussie
- [ ] Bouton "Exporter en PDF" visible
- [ ] Bouton désactivé sans examens
- [ ] Clic sur "Exporter en PDF" fonctionne
- [ ] Indicateur de chargement visible
- [ ] Fichier PDF téléchargé
- [ ] Nom du fichier correct
- [ ] PDF s'ouvre correctement
- [ ] En-tête du PDF correct
- [ ] Informations de session/section correctes
- [ ] Tableau des examens complet
- [ ] Tri des examens correct
- [ ] Format paysage
- [ ] Footer avec horodatage
- [ ] Test avec plusieurs examens
- [ ] Test avec différentes configurations

---

## 🐛 Rapport de Bugs

Si vous rencontrez des problèmes, notez :
1. **Étape où le problème survient**
2. **Message d'erreur** (si affiché)
3. **Console du navigateur** (F12 > Console)
4. **Configuration testée** (session, section, semestre)
5. **Navigateur utilisé** (Chrome, Firefox, Edge, etc.)

---

## ✅ Résultat Attendu

À la fin des tests, vous devriez avoir :
- ✅ Une interface admin moderne sans sidebar
- ✅ Un bouton d'export PDF fonctionnel
- ✅ Des fichiers PDF professionnels et lisibles
- ✅ Toutes les données correctement exportées
- ✅ Une expérience utilisateur fluide

Bon test ! 🚀
