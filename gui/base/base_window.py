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
    QApplication, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

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
        
        # Barre d'outils
        self.setup_toolbar()
        
        # Barre de statut
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")
        
        # Application du thème
        self.apply_theme()
    
    def setup_toolbar(self):
        """Configuration de la barre d'outils commune"""
        self.toolbar = QToolBar("Barre d'outils principale")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Action pour basculer le thème (mode sombre)
        self.action_toggle_theme = QAction("Mode sombre", self)
        self.action_toggle_theme.setCheckable(True)
        self.action_toggle_theme.setChecked(settings.dark_mode)
        self.action_toggle_theme.toggled.connect(self.toggle_theme)
        self.toolbar.addAction(self.action_toggle_theme)
        
        # Action pour basculer entre les modes
        self.toolbar.addSeparator()
        from config.constants import MODE_TRI, MODE_WORKSPACE
        # Ajout du mode gestion
        MODE_GESTION = "gestion"
        current_mode = self.__class__.__name__
        
        # Créer les actions pour chaque mode
        if "SortWindow" in current_mode:
            self.action_switch_workspace = QAction("Passer en mode Espace de Travail", self)
            self.action_switch_workspace.setToolTip("Basculer vers le mode Espace de Travail")
            self.action_switch_workspace.triggered.connect(lambda: self.switch_mode(MODE_WORKSPACE))
            self.toolbar.addAction(self.action_switch_workspace)
            
            self.action_switch_gestion = QAction("Passer en mode Gestion", self)
            self.action_switch_gestion.setToolTip("Basculer vers le mode Gestion")
            self.action_switch_gestion.triggered.connect(lambda: self.switch_mode(MODE_GESTION))
            self.toolbar.addAction(self.action_switch_gestion)
        elif "WorkspaceWindow" in current_mode:
            self.action_switch_tri = QAction("Passer en mode Tri", self)
            self.action_switch_tri.setToolTip("Basculer vers le mode Tri (multi-sources)")
            self.action_switch_tri.triggered.connect(lambda: self.switch_mode(MODE_TRI))
            self.toolbar.addAction(self.action_switch_tri)
            
            self.action_switch_gestion = QAction("Passer en mode Gestion", self)
            self.action_switch_gestion.setToolTip("Basculer vers le mode Gestion")
            self.action_switch_gestion.triggered.connect(lambda: self.switch_mode(MODE_GESTION))
            self.toolbar.addAction(self.action_switch_gestion)
        elif "GestionWindow" in current_mode:
            self.action_switch_tri = QAction("Passer en mode Tri", self)
            self.action_switch_tri.setToolTip("Basculer vers le mode Tri (multi-sources)")
            self.action_switch_tri.triggered.connect(lambda: self.switch_mode(MODE_TRI))
            self.toolbar.addAction(self.action_switch_tri)
            
            self.action_switch_workspace = QAction("Passer en mode Espace de Travail", self)
            self.action_switch_workspace.setToolTip("Basculer vers le mode Espace de Travail")
            self.action_switch_workspace.triggered.connect(lambda: self.switch_mode(MODE_WORKSPACE))
            self.toolbar.addAction(self.action_switch_workspace)
        
        # Les classes dérivées peuvent ajouter leurs propres actions
        self.setup_specific_toolbar()
        
        self.toolbar.addSeparator()
    
    def setup_specific_toolbar(self):
        """
        Méthode à surcharger dans les classes dérivées pour ajouter
        des actions spécifiques à la barre d'outils
        """
        pass
    
    def toggle_theme(self):
        """Basculer entre le mode clair et le mode sombre"""
        settings.dark_mode = self.action_toggle_theme.isChecked()
        settings.save()
        
        self.apply_theme()
    
    def apply_theme(self):
        """Appliquer le thème actuel"""
        app = QApplication.instance()
        
        if settings.dark_mode:
            # Mode sombre
            style_path = Path(__file__).parent.parent.parent / 'styles' / 'dark_theme.qss'
            if style_path.exists():
                with open(style_path, 'r') as f:
                    app.setStyleSheet(f.read())
                self.action_toggle_theme.setText("Mode clair")
                print("Mode sombre activé")
        else:
            # Mode clair
            app.setStyleSheet("")
            self.action_toggle_theme.setText("Mode sombre")
            print("Mode clair activé")
    
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
            self.show_error("Erreur", f"Impossible de basculer vers le mode {self.next_mode}:\n{str(e)}")
    
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
