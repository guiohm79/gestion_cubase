#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application de tri et gestion des projets Cubase
"""

import sys
import argparse
from PyQt5.QtWidgets import QApplication

from gui.sort_mode.sort_window import SortWindow
from gui.workspace_mode.workspace_window import WorkspaceWindow
from gui.gestion_mode.gestion_window import GestionWindow
from config.constants import MODE_TRI, MODE_WORKSPACE, UI_WINDOW_TITLE

# Ajout du mode gestion
MODE_GESTION = "gestion"
from config.settings import settings

# Référence globale à la fenêtre active pour éviter qu'elle ne soit collectée par le garbage collector
active_window = None

def parse_arguments():
    """Analyse des arguments de la ligne de commande"""
    parser = argparse.ArgumentParser(description="Application de gestion de projets Cubase")
    parser.add_argument(
        "--mode", 
        choices=[MODE_TRI, MODE_WORKSPACE, MODE_GESTION], 
        default=None,
        help="Mode de fonctionnement de l'application (tri ou workspace)"
    )
    return parser.parse_args()

def main():
    """Point d'entrée de l'application"""
    # Analyse des arguments
    args = parse_arguments()
    
    # Création de l'application
    app = QApplication(sys.argv)
    app.setApplicationName(UI_WINDOW_TITLE)
    
    # Chargement des préférences
    settings.load()
    
    # Déterminer le mode à utiliser (priorité aux arguments de ligne de commande)
    mode = args.mode if args.mode else settings.last_mode
    
    # Sauvegarder le mode actuel
    settings.last_mode = mode
    settings.save()
    
    # Création de la fenêtre selon le mode
    if mode == MODE_TRI:
        window = SortWindow()
    elif mode == MODE_WORKSPACE:
        window = WorkspaceWindow()
    elif mode == MODE_GESTION:
        window = GestionWindow()
    else:
        window = SortWindow()  # fallback
    
    # Conserver une référence globale à la fenêtre active
    global active_window
    active_window = window
    
    # Affichage de la fenêtre
    window.show()
    
    # Exécution de l'application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
