#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle de données pour l'affichage des projets
"""

from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor, QBrush

from config.constants import PROJECT_COLUMNS

class ProjectTableModel(QAbstractTableModel):
    """Modèle de données pour l'affichage des projets dans un tableau"""
    dark_mode = False  # Mode sombre activé ou non
    
    def __init__(self, parent=None):
        """Initialisation du modèle"""
        super().__init__(parent)
        
        # Données
        self._data = []
        
        # En-têtes et colonnes du tableau
        self._headers = PROJECT_COLUMNS
        # Ordre des colonnes corrigé pour correspondre aux en-têtes
        # PROJECT_COLUMNS = ["Nom du projet", "Date de modification", "Taille", "Fichiers CPR", "Fichiers BAK", "Fichiers WAV", "Source"]
        self._columns = [
            'project_name',      # Nom du projet
            'latest_cpr_date',   # Date de modification
            'total_size_mb',     # Taille
            'cpr_count',         # Fichiers CPR
            'bak_count',         # Fichiers BAK
            'wav_count',         # Fichiers WAV
            'source'             # Source
        ]
        
        # Couleurs pour différencier les sources
        self._source_to_color = {}
        self._color_index = 0
        self._colors = [
            QColor(200, 230, 200),  # Vert pâle
            QColor(200, 200, 230),  # Bleu pâle
            QColor(230, 200, 200),  # Rouge pâle
            QColor(230, 230, 200),  # Jaune pâle
            QColor(200, 230, 230),  # Cyan pâle
            QColor(230, 200, 230),  # Magenta pâle
            QColor(220, 220, 220),  # Gris pâle
            QColor(230, 215, 200),  # Orange pâle
            QColor(215, 200, 230),  # Violet pâle
            QColor(200, 230, 215)   # Turquoise pâle
        ]
        
        # Mode d'affichage (par projet ou par dossier)
        self._view_mode = "project"  # "project" ou "folder"
    
    def rowCount(self, parent=QModelIndex()):
        """Nombre de lignes dans le modèle"""
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        """Nombre de colonnes dans le modèle"""
        return len(self._headers)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """En-têtes du tableau"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return QVariant()
    
    def data(self, index, role=Qt.DisplayRole):
        """Données à afficher dans le tableau"""
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        col = index.column()
        
        if row >= len(self._data) or self._columns[col] not in self._data[row]:
            return QVariant()
        
        if role == Qt.DisplayRole:
            value = self._data[row][self._columns[col]]
            
            # Formatage des dates
            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y %H:%M")
            
            # Formatage des chemins de fichiers (afficher seulement le nom)
            if isinstance(value, str) and '\\' in value:
                return value.split('\\')[-1]
            
            # Formatage des notes en étoiles
            if self._columns[col] == "rating":
                rating = int(value) if isinstance(value, (int, float)) else 0
                return "★" * rating + "☆" * (5 - rating)
            
            return str(value)
        
        # Coloration des lignes en fonction de la source
        elif role == Qt.BackgroundRole:
            # Alternance de gris foncé en mode sombre
            if getattr(self, "dark_mode", False):
                if row % 2 == 0:
                    return QBrush(QColor("#232629"))
                else:
                    return QBrush(QColor("#2d2f31"))
            # Sinon, coloration par source (mode clair)
            source = self._data[row].get('source', '')
            # Si c'est une source multiple, pas de coloration spécifique
            if source == "Plusieurs sources":
                return QVariant()
            # Sinon, attribuer une couleur à la source si ce n'est pas déjà fait
            if source not in self._source_to_color and source:
                self._source_to_color[source] = self._colors[self._color_index % len(self._colors)]
                self._color_index += 1
            # Retourner la couleur associée à la source
            if source in self._source_to_color:
                return QBrush(self._source_to_color[source])
        
        return QVariant()
    
    def update_data(self, data, view_mode=None):
        """
        Mise à jour des données du modèle
        
        Args:
            data (list): Nouvelles données
            view_mode (str): Mode d'affichage ("project" ou "folder")
        """
        # Mise à jour du mode de visualisation si spécifié
        if view_mode is not None:
            self._view_mode = view_mode
        
        # Début de la mise à jour
        self.beginResetModel()
        
        # Mise à jour des données
        self._data = data if data is not None else []
        
        # Réinitialiser les couleurs des sources
        self._source_to_color = {}
        
        # Ajout des notes depuis le service de métadonnées
        from services.metadata_service import MetadataService
        metadata_service = MetadataService()
        
        for project in self._data:
            project_name = project['project_name']
            try:
                metadata = metadata_service.get_project_metadata(project_name)
                project['rating'] = metadata.get('rating', 0)
            except Exception as e:
                print(f"Erreur lors de la récupération des métadonnées pour {project_name}: {e}")
                project['rating'] = 0
        
        # Marquer les projets les plus récents dans chaque dossier
        if self._view_mode == "folder" and self._data:
            # Grouper par dossier et trouver le plus récent dans chaque groupe
            folders = {}
            for project in self._data:
                folder = Path(project.get('source', '')).name
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(project)
            
            # Marquer le plus récent dans chaque dossier
            for folder, projects in folders.items():
                if projects:
                    # Trouver le projet le plus récent dans ce dossier
                    latest = max(projects, key=lambda x: x.get('latest_cpr_date', datetime.min) 
                                if x.get('latest_cpr_date') else datetime.min)
                    latest['is_latest'] = True
        
        self.endResetModel()
    
    def get_project(self, row):
        """
        Récupération du projet à une ligne donnée
        
        Args:
            row (int): Indice de la ligne
            
        Returns:
            dict: Données du projet
        """
        if 0 <= row < len(self._data):
            return self._data[row]
        return None
        
    def get_project_at_row(self, row):
        """
        Récupération du nom du projet à une ligne donnée
        
        Args:
            row (int): Indice de la ligne
            
        Returns:
            str: Nom du projet
        """
        if 0 <= row < len(self._data):
            return self._data[row]['project_name']
        return None
        
    def get_source_color(self, source):
        """
        Récupération de la couleur associée à une source
        
        Args:
            source (str): Chemin de la source
            
        Returns:
            QColor: Couleur associée à la source
        """
        if source in self._source_to_color:
            return self._source_to_color[source]
        return None
    
    def set_view_mode(self, mode):
        """
        Définition du mode d'affichage
        
        Args:
            mode (str): Mode d'affichage ("project" ou "folder")
        """
        if mode in ["project", "folder"] and mode != self._view_mode:
            self._view_mode = mode
            return True
        return False
