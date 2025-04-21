#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service de gestion des fichiers pour l'application
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class FileService:
    """Service de gestion des fichiers pour les projets Cubase"""
    
    @staticmethod
    def create_directory(path):
        """
        Création d'un dossier
        
        Args:
            path (str): Chemin du dossier à créer
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erreur lors de la création du dossier: {e}")
            return False
    
    @staticmethod
    def create_file(path, content=""):
        """
        Création d'un fichier
        
        Args:
            path (str): Chemin du fichier à créer
            content (str): Contenu du fichier
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Erreur lors de la création du fichier: {e}")
            return False
    
    @staticmethod
    def rename_item(old_path, new_path):
        """
        Renommage d'un fichier ou d'un dossier
        
        Args:
            old_path (str): Ancien chemin
            new_path (str): Nouveau chemin
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Vérifier si la destination existe déjà
            if os.path.exists(new_path):
                print(f"Un élément nommé '{os.path.basename(new_path)}' existe déjà")
                return False
            
            # Renommer
            os.rename(old_path, new_path)
            return True
        except Exception as e:
            print(f"Erreur lors du renommage: {e}")
            return False
    
    @staticmethod
    def delete_item(path):
        """
        Suppression d'un fichier ou d'un dossier
        
        Args:
            path (str): Chemin de l'élément à supprimer
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    @staticmethod
    def copy_file(src_path, dest_path):
        """
        Copie d'un fichier
        
        Args:
            src_path (str): Chemin du fichier source
            dest_path (str): Chemin du fichier de destination
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            shutil.copy2(src_path, dest_path)
            return True
        except Exception as e:
            print(f"Erreur lors de la copie du fichier: {e}")
            return False
    
    @staticmethod
    def move_file(src_path, dest_path):
        """
        Déplacement d'un fichier
        
        Args:
            src_path (str): Chemin du fichier source
            dest_path (str): Chemin du fichier de destination
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            shutil.move(src_path, dest_path)
            return True
        except Exception as e:
            print(f"Erreur lors du déplacement du fichier: {e}")
            return False
    
    @staticmethod
    def get_file_info(path):
        """
        Récupération des informations sur un fichier
        
        Args:
            path (str): Chemin du fichier
            
        Returns:
            dict: Informations sur le fichier
        """
        try:
            file_path = Path(path)
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'is_dir': file_path.is_dir(),
                'extension': file_path.suffix.lower() if file_path.is_file() else None
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des informations sur le fichier: {e}")
            return None
    
    @staticmethod
    def list_directory(path):
        """
        Liste le contenu d'un dossier
        
        Args:
            path (str): Chemin du dossier
            
        Returns:
            list: Liste des éléments du dossier
        """
        try:
            dir_path = Path(path)
            if not dir_path.exists() or not dir_path.is_dir():
                return []
            
            items = []
            for item in dir_path.iterdir():
                items.append(FileService.get_file_info(item))
            
            return items
        except Exception as e:
            print(f"Erreur lors de la liste du dossier: {e}")
            return []
    
    @staticmethod
    def open_in_cubase(file_path, cubase_path=None):
        """
        Ouverture d'un fichier dans Cubase
        
        Args:
            file_path (str): Chemin du fichier à ouvrir
            cubase_path (str): Chemin de l'exécutable Cubase (facultatif)
            
        Returns:
            bool: Succès de l'opération
        """
        import subprocess
        
        try:
            file_path = Path(file_path)
            if not file_path.exists() or file_path.suffix.lower() != '.cpr':
                print(f"Fichier invalide: {file_path}")
                return False
            
            # Si le chemin de Cubase est fourni, l'utiliser
            if cubase_path and os.path.exists(cubase_path):
                subprocess.Popen([cubase_path, str(file_path)])
                return True
            
            # Sinon, essayer d'ouvrir le fichier avec l'application par défaut
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS ou Linux
                subprocess.Popen(['open', str(file_path)])
            else:
                print(f"Système d'exploitation non supporté: {os.name}")
                return False
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier dans Cubase: {e}")
            return False
