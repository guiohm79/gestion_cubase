#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fenêtre principale du mode Tri (multi-sources)
"""

import os
import shutil
from pathlib import Path
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog,
    QGroupBox, QCheckBox, QMessageBox, QProgressBar,
    QSplitter, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QComboBox, QAction, QLineEdit, QMenu, QTextEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

from gui.base.base_window import BaseWindow
from gui.components.audio_player import AudioPlayer
from gui.components.file_tree import FileTree
from gui.components.metadata_editor import MetadataEditor
from gui.components.project_table import ProjectTable

from services.scanner import CubaseScanner
from services.metadata_service import MetadataService
from services.file_service import FileService
from services.audio_service import AudioService
from services.cubase_service import CubaseService

from config.constants import FILE_TREE_COLUMNS
from config.settings import settings

class ScanThread(QThread):
    """Thread pour le scan des dossiers"""
    scan_progress = pyqtSignal(int)
    scan_complete = pyqtSignal(dict)
    
    def __init__(self, directories):
        """
        Initialisation du thread
        
        Args:
            directories (list): Liste des dossiers à scanner
        """
        super().__init__()
        self.directories = directories
        self.scanner = CubaseScanner()
        self.running = True
    
    def run(self):
        """Exécution du thread"""
        print(f"Démarrage du scan de {len(self.directories)} dossiers")
        total_dirs = len(self.directories)
        for i, directory in enumerate(self.directories):
            if not self.running:
                break
            print(f"Scan du dossier: {directory}")
            self.scanner.scan_directory(directory)
            self.scan_progress.emit(int((i + 1) / total_dirs * 100))
        
        if self.running:
            # Préparer les données pour le modèle
            self.scanner._create_dataframe()
            
            print(f"Scan terminé, {len(self.scanner.projects)} projets trouvés")
            self.scan_complete.emit(self.scanner.projects)
    
    def stop(self):
        """Arrêt du thread"""
        self.running = False

class SortWindow(BaseWindow):
    """Fenêtre principale du mode Tri (multi-sources)"""
    
    def __init__(self):
        super().__init__()
        
        # Initialisation des services
        self.scanner = CubaseScanner()
        self.metadata_service = MetadataService(mode='local')
        self.file_service = FileService()
        self.audio_service = AudioService()
        self.cubase_service = CubaseService()
        
        # Dossier de destination
        self.destination_directory = None
        self.selected_directories = []
        
        # Thread de scan
        self.scan_thread = None
        
        # Configuration de l'interface utilisateur
        self.setup_ui()
        
        # Mise à jour du titre
        self.setWindowTitle("Tri Morceaux Cubase - Mode Tri (multi-sources)")
        
        # Mise à jour du titre
        self.setWindowTitle("Tri Morceaux Cubase - Mode Tri (multi-sources)")
    
    def closeEvent(self, event):
        """Gestion de la fermeture de la fenêtre
        
        Args:
            event (QCloseEvent): Événement de fermeture
        """
        print("closeEvent appelé - Début de la fermeture de la fenêtre")
        
        # Arrêt du thread de scan s'il est en cours d'exécution
        if hasattr(self, 'scan_thread') and self.scan_thread is not None:
            print(f"Thread de scan existant: {self.scan_thread}, en cours d'exécution: {self.scan_thread.isRunning()}")
            if self.scan_thread.isRunning():
                print("Arrêt du thread de scan...")
                self.scan_thread.stop()
                self.scan_thread.wait(2000)  # Attendre 2 secondes maximum
                print("Thread de scan arrêté")
        else:
            print("Aucun thread de scan à arrêter")
        
        # S'assurer que tous les threads sont arrêtés avant de fermer
        print("Attente de la fin de tous les threads...")
        QThread.msleep(500)  # Pause pour laisser le temps aux threads de se terminer
        
        # Accepter l'événement de fermeture
        print("closeEvent terminé - Fermeture de la fenêtre acceptée")
        event.accept()
    
    def setup_specific_toolbar(self):
        """Configuration spécifique de la barre d'outils"""
        # Action pour sauvegarder
        action_save = QAction("Sauvegarder", self)
        action_save.triggered.connect(self.save_selected_project)
        self.toolbar.addAction(action_save)
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Widget central déjà créé dans BaseWindow
        
        # Groupe pour la sélection des dossiers
        dir_group = QGroupBox("Sélection des dossiers")
        dir_layout = QVBoxLayout(dir_group)
        
        # Boutons pour ajouter/supprimer des dossiers
        btn_layout = QHBoxLayout()
        self.btn_add_dir = QPushButton("Ajouter un dossier")
        self.btn_add_dir.clicked.connect(self.add_directory)
        self.btn_clear_dirs = QPushButton("Effacer la liste")
        self.btn_clear_dirs.clicked.connect(self.clear_directories)
        btn_layout.addWidget(self.btn_add_dir)
        btn_layout.addWidget(self.btn_clear_dirs)
        
        # Liste des dossiers sélectionnés
        self.dir_list = QTreeWidget()
        self.dir_list.setHeaderLabels(["Dossiers sélectionnés"])
        self.dir_list.setColumnCount(1)
        
        # Bouton de scan
        self.btn_scan = QPushButton("Scanner les dossiers")
        self.btn_scan.clicked.connect(self.scan_directories)
        self.btn_scan.setEnabled(False)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Ajout des widgets au groupe
        dir_layout.addLayout(btn_layout)
        dir_layout.addWidget(self.dir_list)
        dir_layout.addWidget(self.btn_scan)
        dir_layout.addWidget(self.progress_bar)
        
        # Groupe pour les résultats
        results_group = QGroupBox("Résultats")
        results_layout = QVBoxLayout(results_group)
        
        # Contrôles de filtrage et tri
        filter_layout = QHBoxLayout()
        
        # Filtre par nom
        self.lbl_filter = QLabel("Filtrer par nom:")
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Entrez un nom de projet...")
        self.txt_filter.textChanged.connect(self.filter_projects)
        
        # Tri par colonne
        self.lbl_sort = QLabel("Trier par:")
        self.cmb_sort = QComboBox()
        self.cmb_sort.addItems(["Nom du projet", "Date de modification", "Taille"])
        self.cmb_sort.currentIndexChanged.connect(self.sort_projects)
        
        # Ordre de tri
        self.chk_sort_desc = QCheckBox("Ordre décroissant")
        self.chk_sort_desc.stateChanged.connect(self.sort_projects)
        
        filter_layout.addWidget(self.lbl_filter)
        filter_layout.addWidget(self.txt_filter, 2)
        filter_layout.addWidget(self.lbl_sort)
        filter_layout.addWidget(self.cmb_sort, 1)
        filter_layout.addWidget(self.chk_sort_desc)
        
        # Table des projets
        self.project_table = ProjectTable()
        
        # Ajout des contrôles de filtrage et tri au layout
        results_layout.addLayout(filter_layout)
        results_layout.addWidget(self.project_table)
        
        # Détails du projet sélectionné
        details_group = QGroupBox("Détails du projet")
        details_layout = QVBoxLayout(details_group)
        
        # Onglets pour les différentes vues
        self.details_tabs = QTabWidget()
        
        # Onglet des fichiers
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        
        # Arbre des fichiers du projet
        self.file_tree = QTreeWidget()
        # Définir les en-têtes de colonnes pour correspondre à l'ordre des données
        self.file_tree.setHeaderLabels(["Nom", "Taille", "Date de modification", "Source"])
        self.file_tree.setColumnCount(4)
        self.file_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        # Ajuster la largeur des colonnes pour une meilleure lisibilité
        self.file_tree.header().setStretchLastSection(False)
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_tree.header().resizeSection(1, 100)  # Taille
        self.file_tree.header().resizeSection(2, 150)  # Date
        self.file_tree.header().resizeSection(3, 150)  # Source
        
        # Lecteur audio pour les fichiers WAV
        self.audio_player = AudioPlayer()
        self.audio_player.setVisible(False)  # Masqué par défaut
        
        # Initialisation du service audio
        if hasattr(self, 'audio_service'):
            self.audio_service.initialize_player(self.audio_player)
        
        files_layout.addWidget(self.file_tree)
        files_layout.addWidget(self.audio_player)
        
        # Onglet des métadonnées
        metadata_tab = QWidget()
        metadata_layout = QVBoxLayout(metadata_tab)
        
        # Éditeur de métadonnées
        self.metadata_editor = MetadataEditor()
        self.metadata_editor.save_requested.connect(self.save_project_metadata)
        
        metadata_layout.addWidget(self.metadata_editor)
        
        # Ajout des onglets
        self.details_tabs.addTab(files_tab, "Fichiers")
        self.details_tabs.addTab(metadata_tab, "Tags & Notes")
        
        details_layout.addWidget(self.details_tabs)
        
        # Options de sauvegarde
        save_group = QGroupBox("Options de sauvegarde")
        save_layout = QVBoxLayout(save_group)
        
        # Sélection du dossier de destination
        dest_layout = QHBoxLayout()
        self.btn_dest_dir = QPushButton("Dossier de destination")
        self.btn_dest_dir.clicked.connect(self.select_destination)
        self.lbl_dest_dir = QLabel("Aucun dossier sélectionné")
        dest_layout.addWidget(self.btn_dest_dir)
        dest_layout.addWidget(self.lbl_dest_dir, 1)
        
        # Options de sauvegarde
        self.chk_keep_bak = QCheckBox("Conserver les fichiers .bak")
        self.chk_remove_dotunderscore = QCheckBox("Supprimer les fichiers commençant par ._")
        self.chk_remove_dotunderscore.setChecked(settings.remove_dotunderscore)
        
        # Option pour renommer le répertoire du projet
        rename_layout = QHBoxLayout()
        self.lbl_rename = QLabel("Renommer le projet:")
        self.txt_rename = QLineEdit()
        self.txt_rename.setPlaceholderText("Laissez vide pour conserver le nom original")
        self.txt_rename.setText(settings.last_rename)
        rename_layout.addWidget(self.lbl_rename)
        rename_layout.addWidget(self.txt_rename, 1)
        
        # Champ pour les notes du projet
        notes_group = QGroupBox("Notes du projet")
        notes_layout = QVBoxLayout(notes_group)
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Ajoutez ici des notes sur le projet (sera sauvegardé dans un fichier notes.txt)")
        self.txt_notes.setMinimumHeight(80)
        self.txt_notes.setText(settings.last_notes)
        notes_layout.addWidget(self.txt_notes)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        # Bouton de sauvegarde
        self.btn_save = QPushButton("Sauvegarder le projet sélectionné")
        self.btn_save.clicked.connect(self.save_selected_project)
        self.btn_save.setEnabled(False)
        
        # Bouton pour lancer le projet dans Cubase
        self.btn_open_in_cubase = QPushButton("Ouvrir dans Cubase")
        self.btn_open_in_cubase.clicked.connect(self.open_in_cubase)
        self.btn_open_in_cubase.setEnabled(False)
        
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_open_in_cubase)
        
        save_layout.addLayout(dest_layout)
        save_layout.addLayout(rename_layout)
        save_layout.addWidget(notes_group)
        save_layout.addWidget(self.chk_keep_bak)
        save_layout.addWidget(self.chk_remove_dotunderscore)
        save_layout.addLayout(buttons_layout)
        
        # Splitter pour les détails et les options de sauvegarde
        details_splitter = QSplitter(Qt.Vertical)
        details_splitter.addWidget(details_group)
        details_splitter.addWidget(save_group)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(results_group)
        main_splitter.addWidget(details_splitter)
        main_splitter.setSizes([400, 600])
        
        # Ajout des groupes au layout principal
        self.main_layout.addWidget(dir_group)
        self.main_layout.addWidget(main_splitter, 3)
        
        # Connexion des signaux
        self.connect_signals()
    
    def connect_signals(self):
        """Connexion des signaux aux slots"""
        # Boutons
        self.btn_scan.clicked.connect(self.scan_directories)
        self.btn_dest_dir.clicked.connect(self.select_destination)
        # La connexion du bouton save est déjà faite dans setup_ui
        # self.btn_save.clicked.connect(self.save_selected_project)
        self.btn_open_in_cubase.clicked.connect(lambda: self.open_in_cubase())
        self.btn_add_dir.clicked.connect(self.add_directory)
        self.btn_clear_dirs.clicked.connect(self.clear_directories)
        
        # Table des projets
        self.project_table.project_selected.connect(self.on_project_selected)
        
        # Arbre des fichiers
        self.file_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Options
        self.chk_remove_dotunderscore.stateChanged.connect(self.on_remove_dotunderscore_changed)
        self.chk_keep_bak.stateChanged.connect(self.on_keep_bak_changed)
    
    def on_project_selected(self, project):
        """Gestion de la sélection d'un projet
        
        Args:
            project (dict): Projet sélectionné
        """
        if not project:
            return
        # Recherche la version corrigée dans self.all_projects_data
        if hasattr(self, 'all_projects_data') and isinstance(self.all_projects_data, list):
            project_name = project.get('project_name', '')
            for p in self.all_projects_data:
                if p.get('project_name', '') == project_name:
                    project = p
                    break
        # Mise à jour du projet sélectionné
        self.selected_project = project
        
        # Extraction du nom du projet
        project_name = project.get('project_name', '')
        
        
        # Réinitialisation des métadonnées avant de les mettre à jour
        if hasattr(self, 'metadata_editor'):
            # Utiliser set_metadata avec des valeurs vides pour réinitialiser
            self.metadata_editor.set_metadata({
                'tags': [],
                'notes': '',
                'rating': 0
            })
        
        # Mise à jour de l'arbre des fichiers
        if project_name:
            self.update_file_tree(project_name)
        else:
            print("ERREUR: Impossible de récupérer le nom du projet")
        
        # Mise à jour des métadonnées
        if hasattr(self, 'metadata_editor'):
            self.update_metadata(project)
        else:
            print("ATTENTION: Aucun éditeur de métadonnées disponible")
        
        # Activation des boutons
        self.btn_save.setEnabled(True)
        self.btn_open_in_cubase.setEnabled(True)
    
    def add_directory(self):
        """Ajout d'un dossier à scanner"""
        # Déconnecter temporairement le signal pour éviter les appels multiples
        self.btn_add_dir.clicked.disconnect()
        
        # Ouvrir la boîte de dialogue
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier à scanner", str(Path.home()))
        if directory and directory not in self.selected_directories:
            self.selected_directories.append(directory)
            item = QTreeWidgetItem([directory])
            self.dir_list.addTopLevelItem(item)
            self.btn_scan.setEnabled(True)
        
        # Reconnecter le signal
        self.btn_add_dir.clicked.connect(self.add_directory)
    
    def clear_directories(self):
        """Effacement de la liste des dossiers"""
        self.selected_directories = []
        self.dir_list.clear()
        self.btn_scan.setEnabled(False)
    
    def scan_directories(self):
        """Lancement du scan des dossiers"""
        if not self.selected_directories:
            QMessageBox.warning(self, "Erreur", "Aucun dossier sélectionné!")
            return
        
        print("Début du scan des dossiers")
        
        # Arrêt du thread précédent s'il existe et est en cours d'exécution
        if hasattr(self, 'scan_thread') and self.scan_thread is not None and self.scan_thread.isRunning():
            print("Arrêt du thread de scan précédent...")
            self.scan_thread.stop()
            self.scan_thread.wait(2000)  # Attendre 2 secondes maximum
            print("Thread de scan précédent arrêté")
        
        # Affichage de la barre de progression
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Création et lancement du thread de scan
        print("Création d'un nouveau thread de scan")
        self.scan_thread = ScanThread(self.selected_directories)
        self.scan_thread.scan_progress.connect(self.update_scan_progress)
        self.scan_thread.scan_complete.connect(self.on_scan_complete)
        self.scan_thread.start()
        print(f"Thread de scan démarré: {self.scan_thread}, en cours d'exécution: {self.scan_thread.isRunning()}")
    
    def update_scan_progress(self, value):
        """
        Mise à jour de la barre de progression
        
        Args:
            value (int): Valeur de progression (0-100)
        """
        self.progress_bar.setValue(value)
    
    def update_metadata(self, project):
        """Mise à jour de l'éditeur de métadonnées avec les métadonnées du projet"""
        
        if not hasattr(self, 'metadata_editor'):
            return
        project_name = project.get('project_name', '')
        project_dir = project.get('project_dir', None)
        try:
            metadata = self.metadata_service.get_project_metadata(project_name, project_dir)
            if metadata:
                notes = metadata.get('notes', '')
                if notes is None:
                    notes = ''
                else:
                    notes = str(notes)
                self.metadata_editor.set_metadata({
                    'tags': metadata.get('tags', []),
                    'notes': notes,
                    'rating': metadata.get('rating', 0)
                })
            else:
                # Réinitialisation de l'éditeur si aucune métadonnée n'est trouvée
                self.metadata_editor.set_metadata({'tags': [], 'notes': '', 'rating': 0})
            # Stockage du nom du projet pour la sauvegarde
            self.metadata_editor.current_project = project_name
        except Exception as e:
            print(f"ERREUR lors de la récupération des métadonnées: {str(e)}")
    
    def save_project_metadata(self):
        """
        Sauvegarde des métadonnées du projet sélectionné
        """
        if not hasattr(self, 'metadata_editor') or not hasattr(self, 'selected_project'):
            print("ERREUR: Impossible de sauvegarder les métadonnées - éditeur ou projet non disponible")
            return
            
        # Récupération du nom du projet
        project_name = self.selected_project.get('project_name', '')
        if not project_name:
            print("ERREUR: Impossible de sauvegarder les métadonnées - nom du projet non disponible")
            return
            
        try:
            # Récupération des métadonnées depuis l'éditeur
            tags = self.metadata_editor.get_tags()
            notes = self.metadata_editor.get_notes()
            rating = self.metadata_editor.get_rating()
            
            # Création du dictionnaire de métadonnées
            metadata = {
                'tags': tags,
                'notes': notes,
                'rating': rating,
                'last_saved': datetime.now().isoformat()
            }
            
            # Sauvegarde des métadonnées
            self.metadata_service.save_metadata(project_name, metadata)
            
            # Message de confirmation
            self.statusBar.showMessage(f"Métadonnées sauvegardées pour le projet {project_name}")
            
        except Exception as e:
            print(f"ERREUR lors de la sauvegarde des métadonnées: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la sauvegarde des métadonnées:\n{str(e)}")
    
    def on_scan_complete(self, projects):
        """
        Traitement des résultats du scan
        
        Args:
            projects (dict): Dictionnaire des projets trouvés
        """
        print("Scan terminé, traitement des résultats...")
        
        # Masquage de la barre de progression
        self.progress_bar.setVisible(False)
        
        # Mettre à jour le scanner principal avec les projets trouvés
        self.scanner.projects = projects
        
        # Préparer les données pour le modèle
        self.scanner._create_dataframe()
        
        # Récupérer les données pour le modèle
        self.all_projects_data = self.scanner.df_projects
        
        print(f"Nombre de projets à afficher: {len(self.all_projects_data)}")
        
        # Mise à jour de la table des projets
        self.project_table.update_data(self.all_projects_data)
        # Connexion du signal pour sélectionner le projet depuis la table
        self.project_table.project_selected.connect(self.on_project_selected)
        
        # Message de statut
        self.statusBar.showMessage(f"{len(self.all_projects_data)} projets trouvés")
        
        # Nettoyage du thread de scan
        if self.scan_thread:
            print("Nettoyage du thread de scan après complétion")
            # Déconnecter les signaux pour éviter les fuites mémoire
            try:
                self.scan_thread.scan_progress.disconnect()
                self.scan_thread.scan_complete.disconnect()
            except TypeError:
                # Ignorer les erreurs si les signaux sont déjà déconnectés
                pass
            
            # Attendre que le thread se termine complètement
            if self.scan_thread.isRunning():
                self.scan_thread.stop()
                self.scan_thread.wait(1000)  # Attendre 1 seconde maximum
            
            print("Thread de scan nettoyé")
    
    def filter_projects(self):
        """Filtrage des projets par nom"""
        filter_text = self.txt_filter.text().strip()
        self.project_table.set_filter(filter_text)
    
    def sort_projects(self):
        """Tri des projets selon les critères sélectionnés"""
        column_index = self.cmb_sort.currentIndex()
        descending = self.chk_sort_desc.isChecked()
        order = Qt.DescendingOrder if descending else Qt.AscendingOrder
        
        # Correspondance entre l'index du combobox et la colonne du modèle
        column_mapping = {
            0: 0,  # Nom du projet
            1: 2,  # Date de modification
            2: 6   # Taille
        }
        
        if column_index in column_mapping:
            self.project_table.set_sort_column(column_mapping[column_index], order)
    
    def show_project_details(self, project):
        """
        Affichage des détails d'un projet
        
        Args:
            project (dict): Projet sélectionné
        """
        if not project:
            return
        
        # Récupération des détails du projet
        project_name = project.get('project_name')
        project_dir = project.get('project_dir', '')
        
        # Récupération des métadonnées du projet
        try:
            # Passer le chemin du dossier du projet pour permettre l'accès aux métadonnées locales
            metadata = self.metadata_service.get_project_metadata(project_name, project_dir)
            self.metadata_editor.set_metadata(metadata)
            print(f"Métadonnées chargées pour {project_name} depuis {project_dir}")
        except Exception as e:
            print(f"Erreur lors de la récupération des métadonnées: {e}")
            self.metadata_editor.set_metadata({'tags': [], 'rating': 0, 'notes': ''})
        
        # Mise à jour de l'arbre des fichiers
        self.update_file_tree(project_name)
        
        # Activation des boutons
        self.btn_save.setEnabled(True)
        self.btn_open_in_cubase.setEnabled(True)
        
        # Message de statut
        self.statusBar.showMessage(f"Projet sélectionné: {project_name}")
    
    def update_file_tree(self, project_name):
        """
        Mise à jour de l'arbre des fichiers pour un projet
        
        Args:
            project_name (str): Nom du projet
        """
        # Effacement de l'arbre
        self.file_tree.clear()
        
        # Récupération des détails du projet
        project_details = self.scanner.get_project_details(project_name)
        if not project_details:
            return
        
        # Trouver le fichier CPR le plus récent
        latest_cpr = None
        if project_details['cpr_files']:
            latest_cpr = max(project_details['cpr_files'], key=lambda x: x['modified'])
        
        # Création des éléments pour les fichiers CPR
        cpr_parent = QTreeWidgetItem(self.file_tree, ["Fichiers CPR"])
        for file_info in project_details['cpr_files']:
            path = Path(file_info['path'])
            # Indiquer si c'est le fichier le plus récent
            is_latest = latest_cpr and file_info['path'] == latest_cpr['path']
            display_name = f"{path.name} {'(PLUS RÉCENT)' if is_latest else ''}"
            
            # Ajouter la source du fichier
            source = file_info.get('source', '')
            if source:
                source_name = Path(source).name
            else:
                source_name = "Source inconnue"
            
            # Extraire le nom de la source pour l'affichage
            source_display = Path(source).name if source else "Source inconnue"
            
            item = QTreeWidgetItem(cpr_parent, [
                display_name,
                f"{file_info['size'] / (1024 * 1024):.2f} MB",
                file_info['modified'].strftime("%d/%m/%Y %H:%M"),
                source_display
            ])
            # Ajouter la source complète comme tooltip
            item.setToolTip(0, f"Source: {source}")
            item.setToolTip(3, f"Chemin complet: {source}")
            
            item.setData(0, Qt.UserRole, file_info['path'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # Cocher par défaut le fichier le plus récent, décocher les autres
            item.setCheckState(0, Qt.Checked if is_latest else Qt.Unchecked)
        
        # Trouver le fichier BAK le plus récent
        latest_bak = None
        if project_details['bak_files']:
            latest_bak = max(project_details['bak_files'], key=lambda x: x['modified'])
        
        # Création des éléments pour les fichiers BAK
        bak_parent = QTreeWidgetItem(self.file_tree, ["Fichiers BAK"])
        for file_info in project_details['bak_files']:
            path = Path(file_info['path'])
            # Indiquer si c'est le fichier le plus récent
            is_latest = latest_bak and file_info['path'] == latest_bak['path']
            display_name = f"{path.name} {'(PLUS RÉCENT)' if is_latest else ''}"
            
            # Ajouter la source du fichier
            source = file_info.get('source', '')
            if source:
                source_name = Path(source).name
            else:
                source_name = "Source inconnue"
            
            # Extraire le nom de la source pour l'affichage
            source_display = Path(source).name if source else "Source inconnue"
            
            item = QTreeWidgetItem(bak_parent, [
                display_name,
                f"{file_info['size'] / (1024 * 1024):.2f} MB",
                file_info['modified'].strftime("%d/%m/%Y %H:%M"),
                source_display
            ])
            # Ajouter la source complète comme tooltip
            item.setToolTip(0, f"Source: {source}")
            item.setToolTip(3, f"Chemin complet: {source}")
            
            item.setData(0, Qt.UserRole, file_info['path'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # Cocher par défaut le fichier le plus récent si l'option est activée, décocher les autres
            should_check = self.chk_keep_bak.isChecked() and is_latest
            item.setCheckState(0, Qt.Checked if should_check else Qt.Unchecked)
        
        # Création des éléments pour les fichiers WAV
        wav_parent = QTreeWidgetItem(self.file_tree, ["Fichiers WAV"])
        for file_info in project_details['wav_files']:
            path = Path(file_info['path'])
            # Vérifier si c'est un fichier ._ et si l'option de suppression est activée
            is_dotunderscore = path.name.startswith('._')
            
            # Ajouter la source du fichier
            source = file_info.get('source', '')
            if source:
                source_name = Path(source).name
            else:
                source_name = "Source inconnue"
            
            # Extraire le nom de la source pour l'affichage
            source_display = Path(source).name if source else "Source inconnue"
            
            item = QTreeWidgetItem(wav_parent, [
                path.name,
                f"{file_info['size'] / (1024 * 1024):.2f} MB",
                file_info['modified'].strftime("%d/%m/%Y %H:%M"),
                source_display
            ])
            # Ajouter la source complète comme tooltip
            item.setToolTip(0, f"Source: {source}")
            item.setToolTip(3, f"Chemin complet: {source}")
            
            item.setData(0, Qt.UserRole, file_info['path'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # Par défaut, les fichiers WAV sont sélectionnés sauf s'ils commencent par ._ et que l'option est activée
            should_check = not (is_dotunderscore and self.chk_remove_dotunderscore.isChecked())
            item.setCheckState(0, Qt.Checked if should_check else Qt.Unchecked)
        
        # Création des éléments pour les autres fichiers
        other_parent = QTreeWidgetItem(self.file_tree, ["Autres fichiers"])
        for file_info in project_details['other_files']:
            path = Path(file_info['path'])
            # Vérifier si c'est un fichier ._ et si l'option de suppression est activée
            is_dotunderscore = path.name.startswith('._')
            
            # Ajouter la source du fichier
            source = file_info.get('source', '')
            if source:
                source_name = Path(source).name
            else:
                source_name = "Source inconnue"
            
            # Extraire le nom de la source pour l'affichage
            source_display = Path(source).name if source else "Source inconnue"
            
            item = QTreeWidgetItem(other_parent, [
                path.name,
                f"{file_info['size'] / (1024 * 1024):.2f} MB",
                file_info['modified'].strftime("%d/%m/%Y %H:%M"),
                source_display
            ])
            # Ajouter la source complète comme tooltip
            item.setToolTip(0, f"Source: {source}")
            item.setToolTip(3, f"Chemin complet: {source}")
            
            item.setData(0, Qt.UserRole, file_info['path'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # Par défaut, les autres fichiers sont sélectionnés sauf s'ils commencent par ._ et que l'option est activée
            should_check = not (is_dotunderscore and self.chk_remove_dotunderscore.isChecked())
            item.setCheckState(0, Qt.Checked if should_check else Qt.Unchecked)
        
        # Ajouter des cases à cocher pour les éléments parents
        cpr_parent.setFlags(cpr_parent.flags() | Qt.ItemIsUserCheckable)
        cpr_parent.setCheckState(0, Qt.Checked)
        
        bak_parent.setFlags(bak_parent.flags() | Qt.ItemIsUserCheckable)
        bak_parent.setCheckState(0, Qt.Checked if self.chk_keep_bak.isChecked() else Qt.Unchecked)
        
        # Appliquer l'état de la case à cocher des BAK à tous les enfants
        for i in range(bak_parent.childCount()):
            bak_parent.child(i).setCheckState(0, bak_parent.checkState(0))
        
        wav_parent.setFlags(wav_parent.flags() | Qt.ItemIsUserCheckable)
        wav_parent.setCheckState(0, Qt.Checked)
        
        other_parent.setFlags(other_parent.flags() | Qt.ItemIsUserCheckable)
        other_parent.setCheckState(0, Qt.Checked)
        
        # Connecter le signal de changement d'état des cases à cocher
        self.file_tree.itemChanged.connect(self.on_file_tree_item_changed)
        
        # Expansion des éléments parents
        self.file_tree.expandAll()
    
    def on_item_double_clicked(self, item, column):
        """
        Gestion du double-clic sur un élément de l'arbre des fichiers
        
        Args:
            item (QTreeWidgetItem): Élément cliqué
            column (int): Colonne cliquée
        """
        # Récupération du chemin du fichier
        file_path = item.data(0, Qt.UserRole)
        if not file_path:
            return
        
        # Vérification du type de fichier
        path = Path(file_path)
        if path.suffix.lower() == '.wav':
            # Lecture du fichier WAV
            self.audio_service.load_file(file_path)
            self.audio_player.setVisible(True)
            self.audio_service.play()
        elif path.suffix.lower() == '.cpr':
            # Ouverture du fichier CPR dans Cubase
            self.open_in_cubase(file_path)
    
    def select_destination(self):
        """Sélection du dossier de destination"""
        # Déconnecter temporairement le signal pour éviter les appels multiples
        self.btn_dest_dir.clicked.disconnect()
        
        # Ouvrir la boîte de dialogue
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier de destination", str(Path.home()))
        if directory:
            self.destination_directory = directory
            self.lbl_dest_dir.setText(directory)
        
        # Reconnecter le signal
        self.btn_dest_dir.clicked.connect(self.select_destination)
    
    def get_selected_files(self):
        """
        Récupère la liste des fichiers sélectionnés dans l'arbre des fichiers
        
        Returns:
            dict: Dictionnaire contenant les listes de fichiers sélectionnés par catégorie
        """
        selected_files = {
            'cpr_files': [],
            'bak_files': [],
            'wav_files': [],
            'other_files': []
        }
        
        # Parcourir les catégories (parents)
        for category_idx in range(self.file_tree.topLevelItemCount()):
            category = self.file_tree.topLevelItem(category_idx)
            category_name = category.text(0).lower()
            
            # Déterminer la clé du dictionnaire selon la catégorie
            if 'cpr' in category_name:
                key = 'cpr_files'
            elif 'bak' in category_name:
                key = 'bak_files'
            elif 'wav' in category_name:
                key = 'wav_files'
            else:
                key = 'other_files'
            
            print(f"Catégorie: {category_name}, Clé: {key}, Nombre d'enfants: {category.childCount()}")
            
            # Parcourir les fichiers de la catégorie
            for file_idx in range(category.childCount()):
                file_item = category.child(file_idx)
                file_name = file_item.text(0)
                check_state = file_item.checkState(0)
                file_path = file_item.data(0, Qt.UserRole)
                
                # Afficher des informations de débogage
                print(f"  Fichier: {file_name}, État: {check_state}, Chemin: {file_path}")
                
                # Si le fichier est sélectionné (coché)
                if check_state == Qt.Checked:
                    if file_path:
                        selected_files[key].append(file_path)
                        print(f"    -> Ajouté à la liste {key}")
        
        # Afficher le nombre de fichiers sélectionnés par catégorie
        for key, files in selected_files.items():
            print(f"Nombre de fichiers {key}: {len(files)}")
        
        return selected_files
    
    def save_selected_project(self):
        """Sauvegarde du projet sélectionné avec les fichiers sélectionnés"""
        # Vérification de la sélection
        project = self.project_table.get_selected_project()
        if not project:
            QMessageBox.warning(self, "Erreur", "Aucun projet sélectionné!")
            return
        
        # Vérification du dossier de destination
        if not self.destination_directory:
            QMessageBox.warning(self, "Erreur", "Aucun dossier de destination sélectionné!")
            return
        
        # Récupération des options
        project_name = project.get('project_name')
        new_project_name = self.txt_rename.text().strip()
        project_notes = self.txt_notes.toPlainText()
        
        # Récupération des fichiers sélectionnés
        selected_files = self.get_selected_files()
        
        # Sauvegarde des préférences
        settings.remove_dotunderscore = self.chk_remove_dotunderscore.isChecked()
        settings.last_rename = new_project_name
        settings.last_notes = project_notes
        settings.save()
        
        # Détermination du nom du dossier de destination
        dest_project_name = new_project_name if new_project_name else project_name
        dest_project_dir = Path(self.destination_directory) / dest_project_name
        
        try:
            # Vérifier si des fichiers sont sélectionnés
            total_files = sum(len(files) for files in selected_files.values())
            if total_files == 0:
                QMessageBox.warning(self, "Attention", "Aucun fichier sélectionné pour la sauvegarde!")
                return
            
            # Création du dossier de destination principal
            dest_project_dir.mkdir(parents=True, exist_ok=True)
            print(f"Dossier de destination créé: {dest_project_dir}")
            
            # Création des sous-dossiers standards Cubase
            audio_dir = dest_project_dir / "Audio"
            auto_saves_dir = dest_project_dir / "Auto Saves"
            edits_dir = dest_project_dir / "Edits"
            images_dir = dest_project_dir / "Images"
            presets_dir = dest_project_dir / "Presets"
            
            # Créer les sous-dossiers
            audio_dir.mkdir(exist_ok=True)
            auto_saves_dir.mkdir(exist_ok=True)
            edits_dir.mkdir(exist_ok=True)
            images_dir.mkdir(exist_ok=True)
            presets_dir.mkdir(exist_ok=True)
            
            # Copie des fichiers sélectionnés
            files_copied = 0
            
            # Fonction pour copier les fichiers d'une catégorie vers un dossier spécifique
            def copy_files(file_paths, category_name, target_dir=None):
                nonlocal files_copied
                for file_path in file_paths:
                    src_path = Path(file_path)
                    
                    # Déterminer le dossier de destination en fonction du type de fichier
                    if target_dir:
                        dest_path = target_dir / src_path.name
                    else:
                        dest_path = dest_project_dir / src_path.name
                    
                    try:
                        # Vérifier si le fichier source existe
                        if not os.path.exists(src_path):
                            print(f"ERREUR: Le fichier source n'existe pas: {src_path}")
                            continue
                        
                        # Copier le fichier
                        shutil.copy2(src_path, dest_path)
                        files_copied += 1
                        print(f"Copié: {src_path} -> {dest_path}")
                    except Exception as e:
                        print(f"Erreur lors de la copie du fichier {category_name}: {e}")
            
            # Fonction pour détecter les fichiers de preset (.fxp, .fxb) dans les autres fichiers
            def extract_preset_files(other_files):
                preset_files = []
                remaining_files = []
                
                for file_path in other_files:
                    path = Path(file_path)
                    if path.suffix.lower() in [".fxp", ".fxb"]:
                        preset_files.append(file_path)
                    else:
                        remaining_files.append(file_path)
                        
                return preset_files, remaining_files
            
            # Extraire les fichiers de preset des autres fichiers
            preset_files, other_files_filtered = extract_preset_files(selected_files['other_files'])
            
            # Copie des fichiers par catégorie dans les dossiers appropriés
            print(f"Début de la copie de {total_files} fichiers vers {dest_project_dir}")
            
            # Fichiers CPR dans le dossier principal
            copy_files(selected_files['cpr_files'], "CPR")
            
            # Fichiers BAK dans le dossier Auto Saves
            copy_files(selected_files['bak_files'], "BAK", auto_saves_dir)
            
            # Fichiers WAV dans le dossier Audio
            copy_files(selected_files['wav_files'], "WAV", audio_dir)
            
            # Fichiers de preset dans le dossier Presets
            copy_files(preset_files, "Preset", presets_dir)
            
            # Autres fichiers dans le dossier principal
            copy_files(other_files_filtered, "Autre")
            
            # Création du fichier de notes si des notes sont fournies
            if project_notes:
                notes_path = dest_project_dir / "notes.txt"
                try:
                    with open(notes_path, 'w', encoding='utf-8') as f:
                        f.write(project_notes)
                    print(f"Notes sauvegardées dans: {notes_path}")
                except Exception as e:
                    print(f"Erreur lors de la création du fichier de notes: {e}")
            
            # Sauvegarde des métadonnées dans le dossier de destination
            try:
                # Récupérer les métadonnées du projet
                metadata = self.metadata_editor.get_metadata()
                
                # Récupérer les métadonnées existantes du service
                existing_metadata = self.metadata_service.get_project_metadata(project_name)
                if existing_metadata:
                    # Fusionner les métadonnées existantes avec celles de l'éditeur
                    # pour s'assurer que toutes les informations sont préservées
                    for key, value in existing_metadata.items():
                        if key not in metadata or not metadata[key]:
                            metadata[key] = value
                
                # Ajouter la date de sauvegarde aux métadonnées
                metadata['saved_date'] = datetime.datetime.now().isoformat()
                metadata['name'] = dest_project_name
                
                # Sauvegarder les métadonnées dans le dossier de destination
                metadata_path = dest_project_dir / "metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                print(f"Métadonnées sauvegardées dans: {metadata_path}")
                
                # Enregistrer également les métadonnées dans le service pour les synchroniser
                # Utiliser le nom du projet d'origine pour éviter les incohérences
                self.metadata_service.set_project_metadata(project_name, metadata, str(dest_project_dir))
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des métadonnées dans le dossier de destination: {e}")
            
            # Message de succès
            QMessageBox.information(self, "Succès", f"Projet '{project_name}' sauvegardé avec succès!\n{files_copied} fichiers copiés.")
            self.statusBar.showMessage(f"Projet '{project_name}' sauvegardé dans {self.destination_directory} ({files_copied} fichiers)")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde du projet '{project_name}': {str(e)}")
    
    def save_project_metadata(self):
        """Sauvegarde des métadonnées du projet sélectionné"""
        # Vérification de la sélection
        project = self.project_table.get_selected_project()
        if not project:
            QMessageBox.warning(self, "Erreur", "Aucun projet sélectionné!")
            return
        
        # Récupération des métadonnées
        project_name = project.get('project_name')
        metadata = self.metadata_editor.get_metadata()
        
        # Sauvegarde des métadonnées
        try:
            # Récupérer le dossier du projet
            project_dir = None
            project_details = self.scanner.get_project_details(project_name)
            if project_details and project_details.get('cpr_files'):
                # Utiliser le dossier du premier fichier CPR trouvé
                first_cpr = project_details['cpr_files'][0]
                project_dir = str(Path(first_cpr['path']).parent)
                print(f"Dossier du projet détecté: {project_dir}")
            
            # Sauvegarder les métadonnées
            if self.metadata_service.mode == 'local' and not project_dir:
                QMessageBox.warning(self, "Attention", f"Impossible de déterminer le dossier du projet '{project_name}' pour sauvegarder les métadonnées en mode local.")
                return
            
            success = self.metadata_service.set_project_metadata(project_name, metadata, project_dir)
            if success:
                # Afficher uniquement un message dans la barre d'état, pas de boîte de dialogue
                self.statusBar.showMessage(f"Métadonnées du projet '{project_name}' sauvegardées")
                
                # Mettre à jour l'affichage du projet en passant le projet actuel
                self.on_project_selected(project)
            else:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde des métadonnées du projet '{project_name}'")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde des métadonnées: {e}")
    
    def open_in_cubase(self, file_path=None):
        """
        Ouverture d'un fichier dans Cubase
        
        Args:
            file_path (str): Chemin du fichier à ouvrir (facultatif)
        """
        # Si aucun chemin n'est fourni, utiliser le fichier CPR du projet sélectionné
        if not file_path:
            project = self.project_table.get_selected_project()
            if not project or not project.get('latest_cpr'):
                QMessageBox.warning(self, "Erreur", "Aucun fichier CPR disponible!")
                return
            
            file_path = project.get('latest_cpr')
        
        # Ouverture du fichier dans Cubase
        success = self.cubase_service.open_project(file_path)
        if not success:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ouverture du fichier dans Cubase")
    
    def on_remove_dotunderscore_changed(self, state):
        """
        Gestion du changement de l'option de suppression des fichiers ._
        
        Args:
            state (int): État de la case à cocher
        """
        settings.remove_dotunderscore = (state == Qt.Checked)
        settings.save()
        
        # Mettre à jour l'arbre des fichiers pour refléter le changement
        project = self.project_table.get_selected_project()
        if project:
            self.update_file_tree(project.get('project_name'))
    
    def on_keep_bak_changed(self, state):
        """
        Gestion du changement de l'option de conservation des fichiers .bak
        
        Args:
            state (int): État de la case à cocher
        """
        settings.keep_bak = (state == Qt.Checked)
        settings.save()
        
        # Déconnecter temporairement le signal pour éviter les boucles infinies
        if hasattr(self, 'file_tree') and self.file_tree:
            try:
                self.file_tree.itemChanged.disconnect(self.on_file_tree_item_changed)
            except TypeError:
                # Le signal n'est peut-être pas connecté
                pass
            
            # Mettre à jour l'état des fichiers BAK dans l'arbre
            for i in range(self.file_tree.topLevelItemCount()):
                parent = self.file_tree.topLevelItem(i)
                if parent.text(0).lower() == "fichiers bak":
                    parent.setCheckState(0, Qt.Checked if state == Qt.Checked else Qt.Unchecked)
                    
                    # Appliquer à tous les enfants
                    for j in range(parent.childCount()):
                        parent.child(j).setCheckState(0, parent.checkState(0))
                    break
            
            # Reconnecter le signal
            try:
                self.file_tree.itemChanged.connect(self.on_file_tree_item_changed)
            except TypeError:
                pass
    
    def on_file_tree_item_changed(self, item, column):
        """
        Gestion du changement d'état d'une case à cocher dans l'arbre des fichiers
        
        Args:
            item (QTreeWidgetItem): Élément modifié
            column (int): Colonne modifiée
        """
        if column != 0:  # Les cases à cocher sont dans la première colonne
            return
        
        # Déconnecter temporairement le signal pour éviter les boucles infinies
        self.file_tree.itemChanged.disconnect(self.on_file_tree_item_changed)
        
        # Si c'est un élément parent (catégorie)
        if item.childCount() > 0:
            # Appliquer l'état de la case à cocher à tous les enfants
            check_state = item.checkState(0)
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, check_state)
                
            # Si c'est le parent des fichiers BAK, mettre à jour la case à cocher globale
            if item.text(0).lower() == "fichiers bak":
                self.chk_keep_bak.setChecked(check_state == Qt.Checked)
        else:
            # Si c'est un fichier, vérifier si tous les fichiers de la même catégorie sont cochés/décochés
            parent = item.parent()
            if parent:
                all_checked = True
                all_unchecked = True
                
                for i in range(parent.childCount()):
                    child_state = parent.child(i).checkState(0)
                    if child_state != Qt.Checked:
                        all_checked = False
                    if child_state != Qt.Unchecked:
                        all_unchecked = False
                
                # Mettre à jour l'état de la case à cocher du parent
                # Si au moins un enfant est coché, le parent est coché
                if all_unchecked:
                    parent.setCheckState(0, Qt.Unchecked)
                else:
                    parent.setCheckState(0, Qt.Checked)
                    
                # Si c'est un fichier BAK, vérifier s'il faut mettre à jour la case à cocher globale
                if parent.text(0).lower() == "fichiers bak":
                    self.chk_keep_bak.setChecked(not all_unchecked)
        
        # Reconnecter le signal
        self.file_tree.itemChanged.connect(self.on_file_tree_item_changed)
