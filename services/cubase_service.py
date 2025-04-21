#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service d'interaction avec Cubase
"""

import os
import subprocess
from pathlib import Path

class CubaseService:
    """Service d'interaction avec Cubase"""
    
    def __init__(self, cubase_path=None):
        """
        Initialisation du service Cubase
        
        Args:
            cubase_path (str): Chemin de l'exécutable Cubase (facultatif)
        """
        self.cubase_path = cubase_path
    
    def set_cubase_path(self, path):
        """
        Définition du chemin de l'exécutable Cubase
        
        Args:
            path (str): Chemin de l'exécutable Cubase
            
        Returns:
            bool: Succès de l'opération
        """
        if not path or not os.path.exists(path):
            return False
        
        self.cubase_path = path
        return True
    
    def open_project(self, project_path):
        """
        Ouverture d'un projet Cubase
        
        Args:
            project_path (str): Chemin du fichier projet (.cpr)
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            path = Path(project_path)
            if not path.exists() or path.suffix.lower() != '.cpr':
                print(f"Fichier projet invalide: {project_path}")
                return False
            
            # Si le chemin de Cubase est défini, l'utiliser
            if self.cubase_path and os.path.exists(self.cubase_path):
                subprocess.Popen([self.cubase_path, str(path)])
                return True
            
            # Sinon, essayer d'ouvrir le fichier avec l'application par défaut
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS ou Linux
                subprocess.Popen(['open', str(path)])
            else:
                print(f"Système d'exploitation non supporté: {os.name}")
                return False
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'ouverture du projet dans Cubase: {e}")
            return False
    
    def find_cubase_executable(self):
        """
        Recherche automatique de l'exécutable Cubase
        
        Returns:
            str: Chemin de l'exécutable Cubase ou None
        """
        # Chemins possibles pour Cubase sur Windows
        windows_paths = [
            os.path.expandvars(r'%ProgramFiles%\Steinberg\Cubase*'),
            os.path.expandvars(r'%ProgramFiles(x86)%\Steinberg\Cubase*')
        ]
        
        # Chemins possibles pour Cubase sur macOS
        mac_paths = [
            '/Applications/Cubase*.app',
            '/Applications/Steinberg/Cubase*.app'
        ]
        
        # Recherche selon le système d'exploitation
        import glob
        
        if os.name == 'nt':  # Windows
            for pattern in windows_paths:
                matches = glob.glob(pattern)
                for match in matches:
                    exe_path = os.path.join(match, 'Cubase.exe')
                    if os.path.exists(exe_path):
                        return exe_path
        elif os.name == 'posix':  # macOS ou Linux
            for pattern in mac_paths:
                matches = glob.glob(pattern)
                for match in matches:
                    return match
        
        return None
