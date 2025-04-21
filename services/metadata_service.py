#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service de gestion des métadonnées des projets (tags, notes, notation)
"""

import os
import json
from pathlib import Path
from datetime import datetime

from config.constants import DEFAULT_METADATA_FILE

class MetadataService:
    """
    Service de gestion des métadonnées pour les projets Cubase.
    Supporte deux modes :
    - mode centralisé (pour le mode tri multi-sources)
    - mode local (metadata.json dans chaque dossier de projet, pour le mode workspace)
    """
    def __init__(self, mode='local'):
        """
        Initialisation du service de métadonnées
        
        Args:
            mode (str): 'centralized' ou 'local' (défaut)
        """
        self.mode = mode  # 'centralized' ou 'local'
        self.metadata_dir = Path.home() / '.trie_morceaux' / 'metadata'
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.metadata_dir / 'projects_metadata.json'
        self.metadata = self._load_metadata() if self.mode == 'centralized' else None
        self.local_filename = DEFAULT_METADATA_FILE
    
    def _get_local_metadata_path(self, project_dir):
        """
        Retourne le chemin du fichier metadata.json local pour un projet
        
        Args:
            project_dir (str): Chemin du dossier du projet
            
        Returns:
            Path: Chemin du fichier de métadonnées
        """
        return Path(project_dir) / self.local_filename
    
    def _load_local_metadata(self, project_dir):
        """
        Charge les métadonnées locales d'un projet (metadata.json)
        
        Args:
            project_dir (str): Chemin du dossier du projet
            
        Returns:
            dict: Métadonnées du projet
        """
        meta_path = self._get_local_metadata_path(project_dir)
        if meta_path.exists():
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des métadonnées locales: {e}")
                return {}
        else:
            return {}
    
    def _save_local_metadata(self, project_dir, metadata):
        """
        Sauvegarde les métadonnées locales d'un projet (metadata.json)
        
        Args:
            project_dir (str): Chemin du dossier du projet
            metadata (dict): Métadonnées à sauvegarder
            
        Returns:
            bool: Succès de l'opération
        """
        meta_path = self._get_local_metadata_path(project_dir)
        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des métadonnées locales: {e}")
            return False
    
    def _load_metadata(self):
        """
        Chargement des métadonnées depuis le fichier centralisé
        
        Returns:
            dict: Métadonnées de tous les projets
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des métadonnées: {e}")
                return {}
        else:
            return {}
    
    def _save_metadata(self):
        """
        Sauvegarde des métadonnées dans le fichier centralisé
        
        Returns:
            bool: Succès de l'opération
        """
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des métadonnées: {e}")
            return False
    
    def get_project_metadata(self, project_name, project_dir=None):
        """
        Récupération des métadonnées d'un projet
        
        Args:
            project_name (str): Nom du projet
            project_dir (str): Chemin du dossier projet (requis en mode local)
            
        Returns:
            dict: Métadonnées du projet
        """
        if self.mode == 'centralized':
            if project_name not in self.metadata:
                self.metadata[project_name] = {
                    'tags': [],
                    'rating': 0,
                    'notes': '',
                    'last_modified': datetime.now().isoformat()
                }
                self._save_metadata()
            return self.metadata[project_name]
        else:
            # En mode local, on a besoin du chemin du dossier
            if not project_dir:
                print(f"ATTENTION: project_dir est requis en mode local pour le projet {project_name}")
                # Retourner des métadonnées vides plutôt que de lever une exception
                return {
                    "name": project_name,
                    "styles": [],
                    "bpm": 0,
                    "rating": 0,
                    "tags": [],
                    "versions": [],
                    "notes": "",
                    "last_modified": datetime.now().isoformat()
                }
            
            # Vérifier que le chemin existe
            if not os.path.exists(project_dir):
                print(f"ATTENTION: Le dossier {project_dir} n'existe pas pour le projet {project_name}")
                return {
                    "name": project_name,
                    "styles": [],
                    "bpm": 0,
                    "rating": 0,
                    "tags": [],
                    "versions": [],
                    "notes": "",
                    "last_modified": datetime.now().isoformat()
                }
            
            metadata = self._load_local_metadata(project_dir)
            if not metadata:
                metadata = {
                    "name": project_name,
                    "styles": [],
                    "bpm": 0,
                    "rating": 0,
                    "tags": [],
                    "versions": [],
                    "notes": "",
                    "last_modified": datetime.now().isoformat()
                }
                self._save_local_metadata(project_dir, metadata)
            return metadata
    
    def set_project_metadata(self, project_name, metadata, project_dir=None):
        """
        Sauvegarde des métadonnées d'un projet (tous les champs)
        
        Args:
            project_name (str): Nom du projet
            metadata (dict): Métadonnées à sauvegarder
            project_dir (str): Chemin du dossier projet (requis en mode local)
            
        Returns:
            bool: Succès de l'opération
        """
        # Mise à jour de la date de modification
        metadata['last_modified'] = datetime.now().isoformat()
        
        if self.mode == 'centralized':
            self.metadata[project_name] = metadata
            return self._save_metadata()
        else:
            if not project_dir:
                print(f"ERREUR: project_dir est requis en mode local pour sauvegarder les métadonnées de {project_name}")
                return False
            
            # Vérifier que le chemin existe
            if not os.path.exists(project_dir):
                print(f"ERREUR: Le dossier {project_dir} n'existe pas pour sauvegarder les métadonnées de {project_name}")
                return False
                
            return self._save_local_metadata(project_dir, metadata)
    
    def set_project_tags(self, project_name, tags, project_dir=None):
        """
        Définition des tags d'un projet
        
        Args:
            project_name (str): Nom du projet
            tags (list): Liste des tags
            project_dir (str): Chemin du dossier projet (requis en mode local)
            
        Returns:
            bool: Succès de l'opération
        """
        if self.mode == 'centralized':
            if project_name not in self.metadata:
                self.metadata[project_name] = {
                    'tags': [],
                    'rating': 0,
                    'notes': '',
                    'last_modified': datetime.now().isoformat()
                }
            self.metadata[project_name]['tags'] = tags
            self.metadata[project_name]['last_modified'] = datetime.now().isoformat()
            return self._save_metadata()
        else:
            if not project_dir:
                raise ValueError("project_dir est requis en mode local")
            metadata = self.get_project_metadata(project_name, project_dir)
            metadata['tags'] = tags
            metadata['last_modified'] = datetime.now().isoformat()
            return self._save_local_metadata(project_dir, metadata)
    
    def set_project_rating(self, project_name, rating, project_dir=None):
        """
        Définition de la note en étoiles d'un projet
        
        Args:
            project_name (str): Nom du projet
            rating (int): Note de 0 à 5 étoiles
            project_dir (str): Chemin du dossier projet (requis en mode local)
            
        Returns:
            bool: Succès de l'opération
        """
        if not isinstance(rating, int) or rating < 0 or rating > 5:
            print(f"Note invalide: {rating}. Doit être un entier entre 0 et 5.")
            return False
        
        if self.mode == 'centralized':
            if project_name not in self.metadata:
                self.metadata[project_name] = {
                    'tags': [],
                    'rating': 0,
                    'notes': '',
                    'last_modified': datetime.now().isoformat()
                }
            self.metadata[project_name]['rating'] = rating
            self.metadata[project_name]['last_modified'] = datetime.now().isoformat()
            return self._save_metadata()
        else:
            if not project_dir:
                raise ValueError("project_dir est requis en mode local")
            metadata = self.get_project_metadata(project_name, project_dir)
            metadata['rating'] = rating
            metadata['last_modified'] = datetime.now().isoformat()
            return self._save_local_metadata(project_dir, metadata)
    
    def set_project_notes(self, project_name, notes, project_dir=None):
        """
        Définition des notes d'un projet
        
        Args:
            project_name (str): Nom du projet
            notes (str): Notes du projet
            project_dir (str): Chemin du dossier projet (requis en mode local)
            
        Returns:
            bool: Succès de l'opération
        """
        if self.mode == 'centralized':
            if project_name not in self.metadata:
                self.metadata[project_name] = {
                    'tags': [],
                    'rating': 0,
                    'notes': '',
                    'last_modified': datetime.now().isoformat()
                }
            self.metadata[project_name]['notes'] = notes
            self.metadata[project_name]['last_modified'] = datetime.now().isoformat()
            return self._save_metadata()
        else:
            if not project_dir:
                raise ValueError("project_dir est requis en mode local")
            metadata = self.get_project_metadata(project_name, project_dir)
            metadata['notes'] = notes
            metadata['last_modified'] = datetime.now().isoformat()
            return self._save_local_metadata(project_dir, metadata)
    
    def get_all_tags(self):
        """
        Récupération de tous les tags utilisés dans les projets
        """
        all_tags = set()
        if self.mode == 'centralized':
            for project_name, metadata in self.metadata.items():
                all_tags.update(metadata.get('tags', []))
        else:
            # En mode local, on ne peut pas facilement récupérer tous les tags
            # sans parcourir tous les dossiers de projets
            # Cette fonctionnalité pourrait être implémentée ultérieurement
            pass
        return sorted(list(all_tags))

    def get_tag_usage_stats(self):
        """
        Retourne un dictionnaire {tag: nombre_d_utilisations} pour tous les tags utilisés dans tous les projets.
        """
        tag_counts = {}
        if self.mode == 'centralized':
            for metadata in self.metadata.values():
                for tag in metadata.get('tags', []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        else:
            # Optionnel : parcourir tous les dossiers de projets pour compter les tags en mode local
            pass
        return tag_counts
    
    def add_tag_to_project(self, project_name, tag, project_dir=None):
        """
        Ajout d'un tag à un projet
        
        Args:
            project_name (str): Nom du projet
            tag (str): Tag à ajouter
            project_dir (str): Chemin du dossier projet (requis en mode local)
            
        Returns:
            bool: Succès de l'opération
        """
        if self.mode == 'centralized':
            metadata = self.get_project_metadata(project_name)
            if tag not in metadata['tags']:
                metadata['tags'].append(tag)
                metadata['last_modified'] = datetime.now().isoformat()
                return self._save_metadata()
            return True
        else:
            if not project_dir:
                raise ValueError("project_dir est requis en mode local")
            metadata = self.get_project_metadata(project_name, project_dir)
            if tag not in metadata['tags']:
                metadata['tags'].append(tag)
                metadata['last_modified'] = datetime.now().isoformat()
                return self._save_local_metadata(project_dir, metadata)
            return True
    
    def remove_tag_from_project(self, project_name, tag, project_dir=None):
        """
        Suppression d'un tag d'un projet
        
        Args:
            project_name (str): Nom du projet
            tag (str): Tag à supprimer
            project_dir (str): Chemin du dossier projet (requis en mode local)
            
        Returns:
            bool: Succès de l'opération
        """
        if self.mode == 'centralized':
            metadata = self.get_project_metadata(project_name)
            if tag in metadata['tags']:
                metadata['tags'].remove(tag)
                metadata['last_modified'] = datetime.now().isoformat()
                return self._save_metadata()
            return True
        else:
            if not project_dir:
                raise ValueError("project_dir est requis en mode local")
            metadata = self.get_project_metadata(project_name, project_dir)
            if tag in metadata['tags']:
                metadata['tags'].remove(tag)
                metadata['last_modified'] = datetime.now().isoformat()
                return self._save_local_metadata(project_dir, metadata)
            return True
