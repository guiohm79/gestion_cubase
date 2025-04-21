#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion des paramètres utilisateur
"""

import os
import json
from pathlib import Path
from config.constants import DEFAULT_PREFS_DIR, DEFAULT_PREFS_FILE

class Settings:
    """Classe de gestion des paramètres utilisateur"""
    
    def __init__(self):
        """Initialisation des paramètres par défaut"""
        self.dark_mode = False
        self.remove_dotunderscore = False
        self.last_rename = ""
        self.last_notes = ""
        self.cubase_path = ""
        self.last_workspace = ""
        self.last_mode = "workspace"  # Mode par défaut (workspace ou tri)
        self.prefs_dir = Path(os.path.expanduser(DEFAULT_PREFS_DIR))
        self.prefs_file = self.prefs_dir / DEFAULT_PREFS_FILE
    
    def save(self):
        """Sauvegarde des paramètres utilisateur"""
        # Création du dossier de préférences s'il n'existe pas
        self.prefs_dir.mkdir(exist_ok=True)
        
        # Préparation des données à sauvegarder
        prefs = {
            'dark_mode': self.dark_mode,
            'remove_dotunderscore': self.remove_dotunderscore,
            'last_rename': self.last_rename,
            'last_notes': self.last_notes,
            'cubase_path': self.cubase_path,
            'last_workspace': self.last_workspace,
            'last_mode': self.last_mode
        }
        
        # Sauvegarde dans le fichier JSON
        with open(self.prefs_file, 'w') as f:
            json.dump(prefs, f)
    
    def load(self):
        """Chargement des paramètres utilisateur"""
        if not self.prefs_file.exists():
            return
        
        try:
            with open(self.prefs_file, 'r') as f:
                prefs = json.load(f)
            
            # Mise à jour des attributs
            self.dark_mode = prefs.get('dark_mode', False)
            self.remove_dotunderscore = prefs.get('remove_dotunderscore', False)
            self.last_rename = prefs.get('last_rename', "")
            self.last_notes = prefs.get('last_notes', "")
            self.cubase_path = prefs.get('cubase_path', "")
            self.last_workspace = prefs.get('last_workspace', "")
            self.last_mode = prefs.get('last_mode', "workspace")
        except Exception as e:
            print(f"Erreur lors du chargement des préférences: {e}")
    
    def get(self, key, default=None):
        """
        Récupération d'un paramètre par sa clé
        
        Args:
            key (str): Clé du paramètre
            default: Valeur par défaut si le paramètre n'existe pas
            
        Returns:
            Valeur du paramètre ou valeur par défaut
        """
        return getattr(self, key, default)
    
    def set(self, key, value):
        """
        Définition d'un paramètre
        
        Args:
            key (str): Clé du paramètre
            value: Valeur du paramètre
        """
        setattr(self, key, value)
        
# Instance globale des paramètres
settings = Settings()
