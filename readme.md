# Tri Morceaux Cubase

Application de gestion de projets Cubase permettant de trier, comparer, sauvegarder et organiser vos projets.

## État du Projet

Le projet a été restructuré selon l'architecture proposée dans le cahier des charges. Les deux modes de fonctionnement (Tri et Espace de Travail) sont maintenant clairement séparés et utilisent des composants communs réutilisables.

### Améliorations Récentes

#### Avril 2025
- **Gestion avancée des VSTi (mode Workspace)** :
  - Ajout d'une interface de gestion des VSTi permettant d'éditer à la fois le nom et l'éditeur d'un VSTi dans une seule fenêtre de dialogue.
  - Le fichier `vsti_list.json` utilise désormais un format enrichi (liste d'objets `{name, editor}`), facilitant la gestion et l'affichage des éditeurs associés à chaque VSTi.
  - L'affichage des VSTi utilisés dans un projet se fait dans un tableau à deux colonnes (« Nom », « Éditeur ») triable par simple clic sur l'en-tête.
  - Correction des erreurs de compatibilité lors de la migration de l'ancien format (liste de chaînes) vers le nouveau format JSON (liste de dictionnaires).
  - Ajout d'un bouton "Sauvegarder" dans la gestion des VSTi pour enregistrer explicitement les modifications apportées à la liste.
  - Robustesse accrue lors du chargement/affichage des VSTi, gestion des cas où l'éditeur est inconnu ou absent dans la base.
- **Mode Tri : gestion des métadonnées 100% locale** : Les métadonnées (tags, notes, notation) sont désormais toujours lues et écrites dans le fichier local du projet. Le mode Tri n’utilise plus le fichier centralisé, ce qui garantit l’indépendance et la cohérence des informations pour chaque projet.
- **Correction automatique du champ `project_dir`** : Lors du scan en mode Tri, le chemin du dossier projet est systématiquement corrigé/déduit pour chaque projet, même si absent initialement. Cela supprime les avertissements et garantit le bon fonctionnement de la gestion locale des métadonnées.
- **Nettoyage des messages de debug** : Tous les prints et messages de debug ont été supprimés pour une console propre et professionnelle.
- **Affichage fiable des métadonnées** : L’éditeur de métadonnées affiche toujours le contenu réel du fichier local du projet sélectionné.


1. **Mode Tri (multi-sources)** :
   - Implémentation d'une structure de dossiers standard Cubase lors de la sauvegarde des projets
   - Création automatique des dossiers Audio, Auto Saves, Edits, Images et Presets
   - Sélection intelligente des fichiers avec mise en évidence des fichiers les plus récents
   - Synchronisation bidirectionnelle des options de filtrage (.bak et ._) avec l'arbre des fichiers
   - Affichage de la source des fichiers dans une colonne dédiée avec infobulles détaillées
   - Sauvegarde des métadonnées dans le dossier de destination avec fusion des informations existantes
   - Correction des inversions de colonnes dans le tableau des projets

2. **Mode Workspace (dossier unique)** :
   - Amélioration de la navigation avec une arborescence complète du système de fichiers
   - Possibilité de remonter jusqu'à la racine du PC dans l'arborescence gauche
   - Optimisation de l'affichage des colonnes dans les arborescences de fichiers
   - Correction des noms de colonnes pour qu'ils correspondent à leur contenu
   - Ajustement automatique de la largeur des colonnes pour une meilleure lisibilité
   - Mise en place d'une disposition horizontale plus intuitive pour les arborescences
   - Simplification de l'interface avec suppression des barres de navigation
   - Ajout de la fonctionnalité de glisser-déposer entre les arborescences
   - Possibilité de copier ou déplacer des fichiers par glisser-déposer
   - Sélection multiple de fichiers pour les opérations de glisser-déposer
   - **Gestion et affichage avancés des VSTi utilisés dans le projet : tableau triable à deux colonnes (Nom, Éditeur), édition centralisée, sauvegarde dans un format JSON enrichi.**

3. **Gestion des métadonnées** :
   - Amélioration de la sauvegarde des métadonnées en mode local et centralisé
   - Ajout d'une date de sauvegarde aux métadonnées
   - Correction des problèmes de synchronisation des métadonnées entre les modes
   - Réinitialisation correcte des métadonnées lors du changement de projet
   - Résolution des erreurs lors de l'enregistrement des métadonnées

4. **Interface utilisateur** :
   - Ajout d'une barre de progression globale lors du chargement d'un projet (mode Espace de Travail) : affichée sous le menu, avec le message "Chargement en cours...", visible pendant tout le chargement (scan, métadonnées, analyse VSTi)
   - L'analyse des VSTi s'effectue désormais en tâche de fond (thread dédié) pour garantir la fluidité de l'interface, même sur de gros projets
   - Affichage minimum garanti de la barre pour un meilleur feedback utilisateur, gestion robuste de l'arrêt des threads lors des changements rapides de projet
   - Amélioration de la navigation entre les modes Tri et Espace de Travail
   - Sauvegarde du dernier mode utilisé dans les paramètres
   - Préservation de la position et taille de la fenêtre lors du changement de mode
   - Simplification du comportement des cases à cocher (suppression de l'état intermédiaire)
   - Correction des problèmes de fenêtres qui s'ouvrent en double
   - Élimination des messages de confirmation redondants

### Problèmes Résolus

#### Avril 2025
- Suppression définitive des erreurs liées au champ `project_dir` manquant en mode Tri.
- Plus aucun risque de confusion ou d’écrasement entre métadonnées locales et centralisées.
- L’interface et la console sont désormais propres (aucun message de debug ou print parasite).
- Les métadonnées affichées et sauvegardées correspondent toujours au fichier local du projet.


1. **Gestion des métadonnées en mode local** : 
   - Ajout du champ `project_dir` dans le scanner pour stocker correctement le chemin du dossier de chaque projet
   - Amélioration de la gestion des erreurs dans le service de métadonnées
   - Meilleure résilience face aux chemins manquants ou invalides
   - Correction des erreurs lors de l'appel aux méthodes du service de métadonnées
   - Résolution des problèmes de sauvegarde des métadonnées dans le dossier de destination

2. **Interface utilisateur** :
   - Correction des inversions de colonnes dans les tableaux et arborescences
   - Amélioration de la navigation dans les arborescences de fichiers
   - Optimisation de l'affichage des colonnes et de leur largeur
   - Correction des noms de colonnes pour qu'ils correspondent à leur contenu
   - Mise en place d'une disposition horizontale plus intuitive pour les arborescences
   - Simplification de l'interface avec suppression des barres de navigation superflues
   - Implémentation du glisser-déposer pour faciliter la gestion des fichiers

3. **Gestion des threads** :
   - Ajout d'une méthode `closeEvent` pour gérer proprement la fermeture des fenêtres
   - Implémentation d'un mécanisme contrôlé d'arrêt des threads
   - Prévention des erreurs "QThread: Destroyed while thread is still running"
   - Amélioration de la stabilité générale de l'application
   
4. **Gestion des fichiers** :
   - Correction des problèmes de sauvegarde ("0 fichiers copiés")
   - Organisation intelligente des fichiers selon leur type
   - Détection automatique des fichiers de préréglages (.fxp, .fxb)
   - Affichage clair des sources de fichiers dans l'interface

### Problème en cours



### Améliorations Futures

1. **Interface utilisateur** :
   - Ajout de raccourcis clavier pour les actions fréquentes
   - Implémentation d'un thème personnalisable (au-delà du mode sombre)
   - Amélioration de la réactivité de l'interface lors du scan de grands dossiers
   - Ajout d'une barre de progression plus détaillée pour les opérations longues
   - Amélioration des fonctionnalités de glisser-déposer avec des options avancées
   - Ajout d'un menu contextuel pour les opérations de glisser-déposer

2. **Gestion des métadonnées** :
   - Implémentation de l'auto-complétion pour les tags
   - Ajout d'un système de tags prédéfinis
   - Possibilité de rechercher et filtrer par tags
   - Synchronisation des métadonnées entre différents ordinateurs

3. **Intégration avec Cubase** :
   - Amélioration de la détection automatique de l'installation de Cubase
   - Support des versions récentes de Cubase (12 et supérieur)
   - Lister les plugins et VSTi utilisés
   - Intégration plus poussée avec l'API de Cubase si disponible
   - Extraction des informations de tempo et tonalité des projets

4. **Gestion des erreurs** :
   - Implémentation d'un système de journalisation plus complet
   - Ajout d'un mécanisme de récupération après erreur
   - Amélioration des messages d'erreur pour l'utilisateur
   - Création d'un assistant de dépannage pour les problèmes courants

4. **Gestion des threads et stabilité** :
   - Résolution de l'erreur "QThread: Destroyed while thread is still running"
   - Implémentation d'un mécanisme d'arrêt contrôlé des threads
   - Nettoyage des threads après utilisation pour éviter les fuites de mémoire

5. **Interface utilisateur** :
   - Correction du problème des fenêtres de sélection qui s'ouvrent en double
   - Simplification du comportement des cases à cocher dans l'arbre des fichiers
   - Élimination des messages de confirmation redondants
   - Amélioration de la réactivité lors du changement de projet

### Structure Implémentée

```
.
├── main.py                      # Point d'entrée, parsing des arguments, lancement du mode approprié
├── config/                      # Configuration de l'application
│   ├── __init__.py
│   ├── settings.py              # Gestion des paramètres utilisateur
│   └── constants.py             # Constantes globales
│   └── vsti_list.json           # Liste enrichie des VSTi (nom, éditeur)
├── gui/                         # Interface utilisateur
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   └── base_window.py       # Classe de base pour les fenêtres principales
│   ├── components/              # Composants d'UI réutilisables
│   │   ├── __init__.py
│   │   ├── audio_player.py      # Lecteur audio unifié
│   │   ├── file_tree.py         # Arborescence de fichiers
│   │   ├── metadata_editor.py   # Éditeur de métadonnées (tags, notes)
│   │   └── project_table.py     # Table des projets
│   ├── sort_mode/               # Mode Tri (multi-sources)
│   │   ├── __init__.py
│   │   └── sort_window.py       # Fenêtre principale du mode tri
│   └── workspace_mode/          # Mode Espace de Travail
│       ├── __init__.py
│       └── workspace_window.py  # Fenêtre principale du mode workspace
├── models/                      # Modèles de données
│   ├── __init__.py
│   └── project_model.py         # Modèle pour l'affichage des projets
├── services/                    # Services métier
│   ├── __init__.py
│   ├── scanner.py               # Scanner de projets Cubase
│   ├── metadata_service.py      # Gestion des métadonnées
│   ├── audio_service.py         # Service audio unifié
│   ├── file_service.py          # Opérations sur les fichiers
│   └── cubase_service.py        # Interactions avec Cubase
│   └── vsti_manager.py          # Gestion des VSTi
└── styles/                      # Feuilles de style
    └── dark_theme.qss          
```

### Format du fichier vsti_list.json

Le fichier `config/vsti_list.json` contient la liste des VSTi connus et leur éditeur, utilisée pour l'affichage, l'édition et la détection automatique dans les projets. Il est au format JSON, chaque entrée étant un objet :

```json
[
  { "name": "HALion Sonic", "editor": "Steinberg" },
  { "name": "Serum", "editor": "Xfer Records" },
  ...
]
```

- **name** : nom exact du VSTi tel qu'il apparaît dans les projets Cubase
- **editor** : nom de l'éditeur/fabricant du VSTi

Ce format permet d'afficher dans l'application à la fois le nom et l'éditeur, de trier, filtrer et éditer facilement la base.

### Utilisation

L'application peut être lancée dans deux modes :

- **Mode Espace de Travail** (par défaut) : `python main.py`
- **Mode Tri** (multi-sources) : `python main.py --mode tri`

## Recommandations pour les Évolutions Futures

### 1. Améliorations Techniques

1. **Gestion des erreurs** :
   - Améliorer la détection et la récupération après erreur
   - Ajouter des messages d'erreur plus descriptifs
   - ✅ Améliorer la gestion des exceptions dans tous les services
   - Implémenter un système de journalisation (logging) centralisé

2. **Optimisation des performances** :
   - Optimiser le scan des dossiers volumineux avec un threading plus avancé
   - Implémenter un système de mise en cache des métadonnées

### 2. Améliorations Fonctionnelles

1. **Interface utilisateur** :
   - Ajouter des raccourcis clavier pour les actions fréquentes
   - Améliorer l'expérience utilisateur avec des animations et transitions
   - Implémenter un système de thèmes plus complet
   - Ajouter une fonction de recherche de projets par mots-clés ou tags
   - ✅ Simplifier le comportement des cases à cocher dans l'interface
   - ✅ Améliorer l'affichage des sources de fichiers
   - ✅ Implémenter le glisser-déposer entre les arborescences
   - ✅ Simplifier l'interface en supprimant les éléments superflus

2. **Gestion des métadonnées** :
   - Implémenter un système de tags hiérarchiques
   - Ajouter la possibilité d'importer/exporter les métadonnées
   - Synchronisation avec des services cloud
   - Améliorer l'interface d'édition des métadonnées avec auto-complétion des tags
   - ✅ Résoudre les problèmes de sauvegarde et de mise à jour des métadonnées

3. **Fonctionnalités avancées** :
   - Intégration plus poussée avec l'API de Cubase
   - Analyse audio avancée (détection de BPM, tonalité, etc.)
   - Gestion des versions et historique des modifications
   - Comparaison visuelle des différentes versions d'un projet
   - Sauvegarde automatique programmée des projets importants

### 3. Documentation

1. **Documentation utilisateur** :
   - Créer un guide utilisateur complet avec captures d'écran
   - Ajouter des tutoriels vidéo pour les fonctionnalités complexes

2. **Documentation technique** :
   - Documenter l'architecture et les choix de conception
   - Ajouter des diagrammes UML pour les composants principaux
   - Créer un guide de contribution pour les développeurs

## Cahier des Charges Initial

### 1. Introduction

L'application "Tri Morceaux Cubase" est un outil de gestion de projets Cubase avec deux fonctionnalités principales distinctes :

1. **Mode Tri (multi-sources)** : Pour trier, comparer et consolider des projets Cubase provenant de plusieurs sources
2. **Mode Espace de Travail (unique)** : Pour gérer et organiser un répertoire unique contenant des projets Cubase

Le code actuel nécessite une refonte pour clarifier la structure et séparer proprement ces deux modes.

### 2. Architecture proposée

```
.
├── main.py                      # Point d'entrée, parsing des arguments, lancement du mode approprié
├── config/                      # Configuration de l'application
│   ├── __init__.py
│   ├── settings.py              # Gestion des paramètres utilisateur
│   └── constants.py             # Constantes globales
├── gui/                         # Interface utilisateur
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   └── base_window.py       # Classe de base pour les fenêtres principales
│   ├── components/              # Composants d'UI réutilisables
│   │   ├── __init__.py
│   │   ├── audio_player.py      # Lecteur audio unifié
│   │   ├── file_tree.py         # Arborescence de fichiers
│   │   ├── metadata_editor.py   # Éditeur de métadonnées (tags, notes)
│   │   └── project_table.py     # Table des projets
│   ├── sort_mode/               # Mode Tri (multi-sources)
│   │   ├── __init__.py
│   │   └── sort_window.py       # Fenêtre principale du mode tri
│   └── workspace_mode/          # Mode Espace de Travail
│       ├── __init__.py
│       └── workspace_window.py  # Fenêtre principale du mode workspace
├── models/                      # Modèles de données
│   ├── __init__.py
│   └── project_model.py         # Modèle pour l'affichage des projets
├── services/                    # Services métier
│   ├── __init__.py
│   ├── scanner.py               # Scanner de projets Cubase
│   ├── metadata_service.py      # Gestion des métadonnées
│   ├── audio_service.py         # Service audio unifié
│   ├── file_service.py          # Opérations sur les fichiers
│   └── cubase_service.py        # Interactions avec Cubase
└── styles/                      # Feuilles de style
    └── dark_theme.qss          
```

### 3. Spécifications détaillées des modes

#### 3.1. Mode Tri (multi-sources)

**Objectif** : Permettre de consolider des projets dispersés dans plusieurs dossiers en triant et comparant leurs fichiers.

**Fonctionnalités** :
- Sélection de plusieurs dossiers sources
- Scan récursif des dossiers
- Regroupement des fichiers par projet
- Visualisation des projets avec leur contenu
- Comparaison des versions de fichiers (.cpr, .bak, .wav)
- Sélection des fichiers à conserver
- Copie structurée des fichiers sélectionnés vers un dossier de destination

**Interface utilisateur** :
1. Zone de sélection des dossiers sources
2. Tableau des projets trouvés
3. Détails du projet sélectionné (fichiers, taille, date)
4. Arborescence des fichiers du projet
5. Prévisualisation audio
6. Options de sauvegarde (dossier de destination, options)

#### 3.2. Mode Espace de Travail (unique)

**Objectif** : Gérer un répertoire de travail contenant des projets Cubase, avec organisation, tagging et gestion des fichiers.

**Fonctionnalités** :
- Sélection d'un dossier de travail unique
- Navigation dans l'arborescence des projets
- Gestion des métadonnées (tags, notes, notation)
- Gestion des fichiers (création, renommage, suppression)
- Prévisualisation audio
- Lancement des projets dans Cubase

**Interface utilisateur** :
1. Sélection du dossier de travail
2. Double arborescence :
   - Vue globale des projets (gauche)
   - Vue détaillée du projet sélectionné (droite)
3. Zone de métadonnées (tags, notes, étoiles)
4. Contrôles de manipulation de fichiers

### 4. Composants techniques communs

#### 4.1. Scanner de projets
- Détection et analyse des projets Cubase
- Identification des fichiers par type (.cpr, .bak, .wav)
- Extraction des métadonnées (date, taille)

#### 4.2. Gestionnaire de métadonnées
- Stockage et récupération des métadonnées (tags, notes, notation)
- Persistance locale (JSON dans chaque dossier projet)
- Prise en charge des deux modes (centralisé/local)

#### 4.3. Lecteur audio
- Prévisualisation des fichiers WAV
- Interface unifiée (contrôles de lecture)
- Implémentation unique et stable

#### 4.4. Modèle de données
- Représentation unifiée des projets
- Prise en charge des différentes vues (par projet, par dossier)
- Support du mode sombre/clair

### 5. Propositions d'amélioration

#### 5.1. Refactorisation prioritaire

1. **Séparation de main_window.py** :
   - Extraire les bases communes dans une classe abstraite BaseWindow
   - Créer SortWindow et WorkspaceWindow héritant de BaseWindow
   - Déplacer les fonctionnalités spécifiques dans les classes respectives

2. **Extraction des composants** :
   - Créer des classes dédiées pour les composants réutilisables
   - AudioPlayer unifié qui remplace les multiples implémentations
   - FileTreeWidget pour la gestion de l'arborescence
   - MetadataEditor pour les tags, notes, etc.

3. **Nettoyage du code** :
   - Suppression des duplications
   - Standardisation des noms de méthodes et variables
   - Documentation améliorée

#### 5.2. Améliorations fonctionnelles

1. **Mode Tri** :
   - Interface simplifiée et plus intuitive
   - Amélioration de la visualisation des différences entre fichiers
   - Prévisualisation des modifications avant sauvegarde

2. **Mode Espace de Travail** :
   - Gestion de métadonnées avancée (exportation/importation)
   - Intégration complète avec Cubase
   - Navigation améliorée dans les projets

3. **Commun** :
   - Système de recherche avancée
   - Historique des actions (undo/redo)
   - Exportation de rapports sur les projets

### 6. Plan d'implémentation

#### Phase 1: Restructuration du code
1. Établir la nouvelle structure de répertoires
2. Extraire les composants communs
3. Séparer les modes Tri et Espace de Travail

#### Phase 2: Stabilisation des fonctionnalités
1. Corriger les bugs dans le mode Tri
2. Finaliser le mode Espace de Travail
3. Unifier l'expérience utilisateur

#### Phase 3: Améliorations
1. Ajouter les nouvelles fonctionnalités
2. Optimiser les performances
3. Améliorer l'interface utilisateur

## Prérequis et Installation

### Prérequis
- Python 3.7 ou supérieur
- PyQt5
- pygame (pour la lecture audio)
- mutagen (pour l'analyse des fichiers audio)

### Installation

1. Clonez ou téléchargez ce dépôt
2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancement de l'application

Pour lancer l'application dans le mode Espace de Travail (par défaut) :
```bash
python main.py
```

Pour lancer l'application dans le mode Tri (multi-sources) :
```bash
python main.py --mode tri
```

### Mode Espace de Travail

Ce mode permet de gérer un répertoire unique contenant des projets Cubase :

1. Sélectionnez un dossier de travail via le bouton "Choisir dossier de travail..." dans la barre d'outils
2. Naviguez dans l'arborescence des projets à gauche
3. Visualisez les détails du projet sélectionné à droite
4. Gérez les métadonnées (tags, notes, notation) dans l'onglet "Tags & Notes"
5. Prévisualisez les fichiers audio en double-cliquant sur un fichier WAV

### Mode Tri (multi-sources)

Ce mode permet de consolider des projets dispersés dans plusieurs dossiers :

1. Ajoutez des dossiers à scanner via le bouton "Ajouter un dossier"
2. Lancez le scan avec le bouton "Scanner les dossiers"
3. Filtrez et triez les projets trouvés
4. Sélectionnez un projet pour voir ses détails et fichiers
5. Choisissez un dossier de destination
6. Sauvegardez le projet sélectionné avec les options souhaitées

Options disponibles:
- `--mode tri` : Lance directement en mode tri (multi-sources)
- `--mode workspace` : Lance directement en mode espace de travail (unique)
- `--workspace [chemin]` : Définit directement le dossier de travail

## Captures d'écran
### Mode Tri
1. Sélectionnez les dossiers sources contenant vos projets Cubase
2. Lancez l'analyse
3. Explorez les projets détectés
4. Sélectionnez les fichiers à conserver
5. Choisissez un dossier de destination
6. Sauvegardez le projet

### Mode Espace de Travail
1. Sélectionnez un dossier de travail contenant vos projets
2. Parcourez l'arborescence des projets
3. Gérez les métadonnées (tags, notes)
4. Manipulez les fichiers selon vos besoins
5. Lancez directement les projets dans Cubase

## 📷 Captures d'écran

*(À ajouter)*

## 📝 Conventions de code

- Utilisez PEP 8 pour le style de code Python
- Préfixez les attributs privés avec `_`
- Utilisez des noms explicites pour les méthodes et variables
- Ajoutez des docstrings pour toutes les classes et méthodes
- Organisez le code selon l'architecture proposée

## 📄 Licence

En cours...