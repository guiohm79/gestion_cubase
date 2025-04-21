#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composant de table des projets pour l'application
"""

from PyQt5.QtWidgets import (
    QTableView, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QSortFilterProxyModel

from models.project_model import ProjectTableModel

class ProjectTable(QTableView):
    """Composant de table des projets basé sur QTableView"""
    
    # Signaux personnalisés
    project_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialisation de la table des projets
        
        Args:
            parent (QWidget): Widget parent
        """
        super(ProjectTable, self).__init__(parent)
        
        # Modèle de données
        self.project_model = ProjectTableModel()
        
        # Modèle de proxy pour le tri et le filtrage
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.project_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        # Configuration de la vue
        self.setModel(self.proxy_model)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSortingEnabled(True)
        
        # Connexion des signaux
        self.clicked.connect(self._on_project_clicked)
        self.doubleClicked.connect(self._on_project_double_clicked)
    
    def update_data(self, projects, view_mode=None):
        """
        Mise à jour des données de la table
        
        Args:
            projects (list): Liste des projets à afficher
            view_mode (str, optional): Mode d'affichage ("project" ou "folder"). Defaults to None.
        """
        self.project_model.update_data(projects, view_mode)
    
    def set_filter(self, text):
        """
        Définition du filtre de recherche
        
        Args:
            text (str): Texte de recherche
        """
        self.proxy_model.setFilterFixedString(text)
    
    def set_sort_column(self, column, order=Qt.AscendingOrder):
        """
        Définition de la colonne de tri
        
        Args:
            column (int): Index de la colonne
            order (Qt.SortOrder): Ordre de tri
        """
        self.sortByColumn(column, order)
    
    def get_selected_project(self):
        """
        Récupération du projet sélectionné
        
        Returns:
            dict: Projet sélectionné ou None
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return None
        
        # Récupération de l'index de la ligne dans le modèle de proxy
        proxy_row = indexes[0].row()
        
        # Conversion de l'index du modèle de proxy vers le modèle source
        source_row = self.proxy_model.mapToSource(self.proxy_model.index(proxy_row, 0)).row()
        
        # Récupération du projet dans le modèle source
        return self.project_model.get_project(source_row)
    
    def _on_project_clicked(self, index):
        """
        Gestion du clic sur un projet
        
        Args:
            index (QModelIndex): Index du projet cliqué
        """
        project = self.get_selected_project()
        if project:
            self.project_selected.emit(project)
    
    def _on_project_double_clicked(self, index):
        """
        Gestion du double-clic sur un projet
        
        Args:
            index (QModelIndex): Index du projet double-cliqué
        """
        # Même comportement que le clic simple pour l'instant
        self._on_project_clicked(index)
    
    def set_dark_mode(self, enabled):
        """
        Définition du mode sombre
        
        Args:
            enabled (bool): Activation du mode sombre
        """
        self.project_model.dark_mode = enabled
        self.project_model.layoutChanged.emit()
