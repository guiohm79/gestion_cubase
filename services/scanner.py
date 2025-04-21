#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service de scan et d'analyse des projets Cubase
"""

import os
from pathlib import Path
from datetime import datetime
import shutil
from collections import defaultdict

class CubaseScanner:
    """Service pour scanner et analyser les projets Cubase"""
    
    def __init__(self):
        """Initialisation du scanner"""
        self.projects = defaultdict(lambda: {
            'cpr_files': [],
            'bak_files': [],
            'wav_files': [],
            'other_files': [],
            'directories': [],
            'source': '',
            'project_dir': ''  # Ajout du chemin complet du dossier du projet
        })
        self.df_projects = []
    
    def scan_directory(self, root_dir):
        """
        Parcours récursif d'un dossier pour trouver les projets Cubase
        
        Args:
            root_dir (str): Chemin du dossier racine à scanner
        
        Returns:
            dict: Dictionnaire des projets trouvés
        """
        root_path = Path(root_dir)
        
        if not root_path.exists():
            print(f"Le dossier {root_path} n'existe pas!")
            return self.projects
        
        # Parcours récursif du dossier
        file_count = 0
        for path in root_path.rglob('*'):
            if path.is_file():
                file_count += 1
                # Récupération de l'extension et du nom du dossier parent
                ext = path.suffix.lower()
                parent_dir = path.parent.name
                project_dir = path.parent
                
                # Détermination du nom du projet (nom du dossier parent)
                project_name = project_dir.name
                
                # Initialisation du chemin du dossier du projet s'il n'existe pas encore
                if 'project_dir' not in self.projects[project_name] or not self.projects[project_name]['project_dir']:
                    self.projects[project_name]['project_dir'] = str(project_dir)
                
                # Si le projet n'a pas encore de source, on l'initialise
                if 'source' not in self.projects[project_name]:
                    self.projects[project_name]['source'] = str(root_path)
                # Si le projet existe déjà mais vient d'une autre source, on le marque comme multi-source
                elif self.projects[project_name]['source'] != str(root_path):
                    self.projects[project_name]['source'] = "Plusieurs sources"
                
                # Ajout du fichier à la catégorie correspondante
                if ext == '.cpr':
                    self.projects[project_name]['cpr_files'].append({
                        'path': str(path),
                        'size': path.stat().st_size,
                        'modified': datetime.fromtimestamp(path.stat().st_mtime),
                        'created': datetime.fromtimestamp(path.stat().st_ctime),
                        'source': str(root_path)
                    })
                elif ext == '.bak':
                    self.projects[project_name]['bak_files'].append({
                        'path': str(path),
                        'size': path.stat().st_size,
                        'modified': datetime.fromtimestamp(path.stat().st_mtime),
                        'created': datetime.fromtimestamp(path.stat().st_ctime),
                        'source': str(root_path)
                    })
                elif ext == '.wav':
                    self.projects[project_name]['wav_files'].append({
                        'path': str(path),
                        'size': path.stat().st_size,
                        'modified': datetime.fromtimestamp(path.stat().st_mtime),
                        'created': datetime.fromtimestamp(path.stat().st_ctime),
                        'source': str(root_path)
                    })
                else:
                    self.projects[project_name]['other_files'].append({
                        'path': str(path),
                        'size': path.stat().st_size,
                        'modified': datetime.fromtimestamp(path.stat().st_mtime),
                        'created': datetime.fromtimestamp(path.stat().st_ctime),
                        'source': str(root_path)
                    })
            elif path.is_dir() and path.name not in ['.', '..']:
                project_name = path.parent.name
                self.projects[project_name]['directories'].append({
                    'path': str(path),
                    'name': path.name,
                    'source': str(root_path)
                })
        
        # Conversion en DataFrame pour faciliter l'analyse
        self._create_dataframe()
        
        return self.projects
    
    def scan_multiple_directories(self, dir_list):
        """
        Scan de plusieurs dossiers racines
        
        Args:
            dir_list (list): Liste des chemins des dossiers à scanner
            
        Returns:
            dict: Dictionnaire des projets trouvés
        """
        for directory in dir_list:
            self.scan_directory(directory)
        
        return self.projects
    
    def _create_dataframe(self):
        """
        Création d'une liste de dictionnaires à partir des projets trouvés
        """
        data = []
        
        for project_name, project_data in self.projects.items():
            # Trouver le fichier CPR le plus récent
            latest_cpr = None
            if project_data['cpr_files']:
                latest_cpr = max(project_data['cpr_files'], 
                                key=lambda x: x['modified'])
            
            # Calculer les statistiques
            total_size = sum(f['size'] for files in [
                project_data['cpr_files'], 
                project_data['bak_files'],
                project_data['wav_files'],
                project_data['other_files']
            ] for f in files)
            
            # Correction : si project_dir est vide, on le déduit du chemin du dernier fichier trouvé
            project_dir = project_data.get('project_dir', '')
            if not project_dir:
                # Cherche le chemin du dossier du dernier fichier CPR/Bak/Wav/Other trouvé
                for key in ['cpr_files', 'bak_files', 'wav_files', 'other_files']:
                    if project_data[key]:
                        project_dir = str(Path(project_data[key][-1]['path']).parent)
                        break
            data.append({
                'project_name': project_name,
                'source': project_data.get('source', ''),
                'project_dir': project_dir,
                'latest_cpr': latest_cpr['path'] if latest_cpr else None,
                'latest_cpr_date': latest_cpr['modified'] if latest_cpr else None,
                'cpr_count': len(project_data['cpr_files']),
                'bak_count': len(project_data['bak_files']),
                'wav_count': len(project_data['wav_files']),
                'other_count': len(project_data['other_files']),
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            })
        
        self.df_projects = data
        return self.df_projects
    
    def get_project_details(self, project_name):
        """
        Récupération des détails d'un projet spécifique
        
        Args:
            project_name (str): Nom du projet
            
        Returns:
            dict: Détails du projet
        """
        return self.projects.get(project_name, None)
    
    def copy_project(self, project_name, destination, keep_bak=False, remove_dotunderscore=False, new_project_name="", project_notes=""):
        """
        Copie d'un projet vers un dossier de destination selon la structure Cubase
        
        Args:
            project_name (str): Nom du projet
            destination (str): Chemin du dossier de destination
            keep_bak (bool): Conserver les fichiers .bak
            remove_dotunderscore (bool): Supprimer les fichiers commençant par ._
            new_project_name (str): Nouveau nom pour le répertoire du projet (facultatif)
            project_notes (str): Notes à ajouter au projet dans un fichier notes.txt (facultatif)
            
        Returns:
            bool: Succès de l'opération
        """
        project = self.projects.get(project_name)
        if not project:
            return False
        
        # Détermination du nom du dossier de destination
        dest_project_name = new_project_name if new_project_name else project_name
        dest_project_dir = Path(destination) / dest_project_name
        
        # Création du dossier de destination
        try:
            dest_project_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Erreur lors de la création du dossier de destination: {e}")
            return False
        
        # Copie des fichiers CPR
        for file_info in project['cpr_files']:
            src_path = Path(file_info['path'])
            dest_path = dest_project_dir / src_path.name
            
            try:
                shutil.copy2(src_path, dest_path)
                print(f"Copié: {src_path} -> {dest_path}")
            except Exception as e:
                print(f"Erreur lors de la copie du fichier CPR: {e}")
        
        # Copie des fichiers BAK si demandé
        if keep_bak:
            for file_info in project['bak_files']:
                src_path = Path(file_info['path'])
                dest_path = dest_project_dir / src_path.name
                
                try:
                    shutil.copy2(src_path, dest_path)
                    print(f"Copié: {src_path} -> {dest_path}")
                except Exception as e:
                    print(f"Erreur lors de la copie du fichier BAK: {e}")
        
        # Copie des fichiers WAV
        for file_info in project['wav_files']:
            src_path = Path(file_info['path'])
            
            # Vérification si le fichier doit être ignoré
            if remove_dotunderscore and src_path.name.startswith('._'):
                print(f"Ignoré (._): {src_path}")
                continue
            
            dest_path = dest_project_dir / src_path.name
            
            try:
                shutil.copy2(src_path, dest_path)
                print(f"Copié: {src_path} -> {dest_path}")
            except Exception as e:
                print(f"Erreur lors de la copie du fichier WAV: {e}")
        
        # Copie des autres fichiers
        for file_info in project['other_files']:
            src_path = Path(file_info['path'])
            
            # Vérification si le fichier doit être ignoré
            if remove_dotunderscore and src_path.name.startswith('._'):
                print(f"Ignoré (._): {src_path}")
                continue
            
            dest_path = dest_project_dir / src_path.name
            
            try:
                shutil.copy2(src_path, dest_path)
                print(f"Copié: {src_path} -> {dest_path}")
            except Exception as e:
                print(f"Erreur lors de la copie du fichier: {e}")
        
        # Création du fichier de notes si des notes sont fournies
        if project_notes:
            notes_path = dest_project_dir / "notes.txt"
            try:
                with open(notes_path, 'w', encoding='utf-8') as f:
                    f.write(project_notes)
                print(f"Notes sauvegardées dans: {notes_path}")
            except Exception as e:
                print(f"Erreur lors de la création du fichier de notes: {e}")
        
        return True
    
    def clear(self):
        """
        Réinitialisation du scanner
        """
        self.projects = defaultdict(lambda: {
            'cpr_files': [],
            'bak_files': [],
            'wav_files': [],
            'other_files': [],
            'directories': [],
            'source': ''
        })
        self.df_projects = []
