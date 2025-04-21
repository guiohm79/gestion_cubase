#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe de base pour les fenêtres principales de l'application
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QToolBar, QAction, QStatusBar, QLabel, QSplitter,
    QApplication, QMessageBox, QTabWidget, QPushButton, 
    QTabBar, QStyle, QStyleOption
)
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QFont

from config.constants import UI_WINDOW_TITLE, UI_MIN_WIDTH, UI_MIN_HEIGHT
from config.settings import settings

class BaseWindow(QMainWindow):
    """Classe de base pour les fenêtres principales de l'application"""
    
    def __init__(self):
        """Initialisation de la fenêtre de base"""
        super().__init__()
        
        # Configuration de base de la fenêtre
        self.setWindowTitle(UI_WINDOW_TITLE)
        self.setMinimumSize(UI_MIN_WIDTH, UI_MIN_HEIGHT)
        
        # Chargement des préférences
        settings.load()
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Système d'onglets pour les modes
        self.setup_tabs()
        
        # Barre de statut
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")
        
        # Application du thème
        self.apply_theme()
    
    def setup_tabs(self):
        """Configuration du système d'onglets pour les modes"""
        # Création du conteneur principal
        self.tabs_container = QWidget()
        tabs_layout = QHBoxLayout(self.tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        
        # Création du widget d'onglets
        self.mode_tabs = QTabWidget()
        self.mode_tabs.setTabPosition(QTabWidget.North)
        self.mode_tabs.setTabsClosable(False)
        self.mode_tabs.setMovable(False)
        self.mode_tabs.setDocumentMode(True)  # Style plus moderne
        
        # Ajouter les onglets pour chaque mode
        from config.constants import MODE_TRI, MODE_WORKSPACE
        # Ajout du mode gestion
        MODE_GESTION = "gestion"
        
        # Déterminer le mode actuel
        current_mode = self.__class__.__name__
        active_index = 0
        
        # Créer les onglets pour chaque mode
        tri_tab = QWidget()
        workspace_tab = QWidget()
        gestion_tab = QWidget()
        
        # Ajouter les onglets au widget
        self.mode_tabs.addTab(tri_tab, "Tri")
        self.mode_tabs.addTab(workspace_tab, "Espace de Travail")
        self.mode_tabs.addTab(gestion_tab, "Gestion")
        
        # Définir l'onglet actif en fonction du mode actuel
        if "SortWindow" in current_mode:
            active_index = 0
        elif "WorkspaceWindow" in current_mode:
            active_index = 1
        elif "GestionWindow" in current_mode:
            active_index = 2
        
        self.mode_tabs.setCurrentIndex(active_index)
        
        # Connecter le changement d'onglet au changement de mode
        self.mode_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Ajouter le widget d'onglets au layout
        tabs_layout.addWidget(self.mode_tabs, 1)  # Stretch pour prendre la majorité de l'espace
        
        # Bouton de thème à droite
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("theme_button")  # Identifiant pour le style CSS
        self.theme_button.setFixedSize(32, 32)
        self.theme_button.setCheckable(True)
        self.theme_button.setChecked(settings.dark_mode)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.update_theme_button_icon()
        
        # Ajouter le bouton de thème au layout
        tabs_layout.addWidget(self.theme_button)
        
        # Ajouter le conteneur au layout principal
        self.main_layout.addWidget(self.tabs_container)
        
        # Ajouter un widget pour contenir le contenu spécifique à chaque mode
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.main_layout.addWidget(self.content_widget, 1)  # Stretch pour prendre tout l'espace restant
        
        # Les classes dérivées peuvent ajouter leurs propres actions
        self.setup_specific_toolbar()
    
    def on_tab_changed(self, index):
        """Gestion du changement d'onglet"""
        from config.constants import MODE_TRI, MODE_WORKSPACE
        MODE_GESTION = "gestion"
        
        # Déterminer le mode en fonction de l'index
        if index == 0:
            self.switch_mode(MODE_TRI)
        elif index == 1:
            self.switch_mode(MODE_WORKSPACE)
        elif index == 2:
            self.switch_mode(MODE_GESTION)
    
    def update_theme_button_icon(self):
        """Mettre à jour l'icône du bouton de thème en fonction du mode actuel"""
        if settings.dark_mode:
            icon_path = str(Path(__file__).parent.parent.parent / 'resources' / 'icons' / 'light_mode.svg')
            self.theme_button.setToolTip("Passer en mode clair")
        else:
            icon_path = str(Path(__file__).parent.parent.parent / 'resources' / 'icons' / 'dark_mode.svg')
            self.theme_button.setToolTip("Passer en mode sombre")
        
        if Path(icon_path).exists():
            self.theme_button.setIcon(QIcon(icon_path))
            self.theme_button.setIconSize(QSize(24, 24))
    
    def setup_specific_toolbar(self):
        """
        Méthode à surcharger dans les classes dérivées pour ajouter
        des actions spécifiques à l'interface
        """
        pass
    
    def toggle_theme(self):
        """Basculer entre le mode clair et le mode sombre"""
        settings.dark_mode = self.theme_button.isChecked()
        settings.save()
        
        self.update_theme_button_icon()
        self.apply_theme()
    
    def apply_theme(self):
        """Appliquer le thème actuel"""
        app = QApplication.instance()
        
        if settings.dark_mode:
            # Mode sombre
            style_path = Path(__file__).parent.parent.parent / 'styles' / 'dark_theme.qss'
        else:
            # Mode clair
            style_path = Path(__file__).parent.parent.parent / 'styles' / 'light_theme.qss'
        
        if style_path.exists():
            with open(style_path, 'r') as f:
                app.setStyleSheet(f.read())
            print(f"Thème {'sombre' if settings.dark_mode else 'clair'} activé")
        else:
            # Fallback si le fichier de style n'existe pas
            app.setStyleSheet("")
            print(f"Fichier de style {style_path} introuvable, utilisation du style par défaut")
        
        # Mise à jour de l'icône du bouton de thème
        self.update_theme_button_icon()
    
    def closeEvent(self, event):
        """Gestion de la fermeture de l'application"""
        # Sauvegarder les préférences
        settings.save()
        
        # Accepter l'événement de fermeture
        event.accept()
    
    def switch_mode(self, mode):
        """Basculer entre les modes Tri, Espace de Travail et Gestion"""
        try:
            print(f"Début du basculement vers le mode {mode}")
            
            # Sauvegarder le mode actuel dans les paramètres
            settings.last_mode = mode
            settings.save()
            
            # Informer l'utilisateur du changement de mode
            self.statusBar.showMessage(f"Basculement vers le mode {mode}...")
            
            # Créer une nouvelle fenêtre du mode approprié
            from gui.sort_mode.sort_window import SortWindow
            from gui.workspace_mode.workspace_window import WorkspaceWindow
            from gui.gestion_mode.gestion_window import GestionWindow
            
            print(f"Classes importées avec succès")
            
            # Obtenir la position et la taille actuelles de la fenêtre
            pos = self.pos()
            size = self.size()
            
            # Créer la nouvelle fenêtre selon le mode
            print(f"Création de la nouvelle fenêtre pour le mode {mode}")
            
            # Créer une instance de la nouvelle fenêtre sans la fermer immédiatement
            if mode == "tri":
                new_window = SortWindow()
                print("SortWindow créée avec succès")
            elif mode == "workspace":
                new_window = WorkspaceWindow()
                print("WorkspaceWindow créée avec succès")
            elif mode == "gestion":
                new_window = GestionWindow()
                print("GestionWindow créée avec succès")
            
            # Conserver une référence globale à la nouvelle fenêtre
            import main
            main.active_window = new_window
            print("Référence globale mise à jour")
            
            # Appliquer la position et la taille
            new_window.move(pos)
            new_window.resize(size)
            
            # Afficher la nouvelle fenêtre
            print("Affichage de la nouvelle fenêtre")
            new_window.show()
            
            # Attendre un peu avant de fermer l'ancienne fenêtre
            import time
            time.sleep(0.5)  # Attendre 500ms
            
            # Fermer la fenêtre actuelle
            print("Fermeture de l'ancienne fenêtre")
            self.close()
            
            print("Basculement terminé avec succès")
        except Exception as e:
            import traceback
            print(f"Erreur lors du basculement de mode: {e}")
            print(traceback.format_exc())
            self.show_error("Erreur", f"Impossible de basculer vers le mode {mode}:\n{str(e)}")
    
    def show_error(self, title, message):
        """Afficher un message d'erreur"""
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title, message):
        """Afficher un message d'avertissement"""
        QMessageBox.warning(self, title, message)
    
    def show_info(self, title, message):
        """Afficher un message d'information"""
        QMessageBox.information(self, title, message)
    
    def show_question(self, title, message):
        """Afficher une question avec boutons Oui/Non"""
        return QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) == QMessageBox.Yes
