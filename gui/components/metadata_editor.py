#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composant d'édition des métadonnées pour l'application
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QCompleter, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from .tag_selector_widget import TagSelectorWidget

class TagButton(QPushButton):
    """Bouton de tag avec signal de suppression"""
    
    remove_requested = pyqtSignal(str)
    
    def __init__(self, tag_text, parent=None):
        """
        Initialisation du bouton de tag
        
        Args:
            tag_text (str): Texte du tag
            parent (QWidget): Widget parent
        """
        super(TagButton, self).__init__(tag_text, parent)
        self.tag_text = tag_text
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 5px 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.clicked.connect(self._on_clicked)
    
    def _on_clicked(self):
        """Gestion du clic sur le bouton"""
        self.remove_requested.emit(self.tag_text)

class MetadataEditor(QWidget):
    """Composant d'édition des métadonnées (tags, notes, notation)"""
    
    # Signaux
    metadata_changed = pyqtSignal(dict)
    tag_added = pyqtSignal(str)
    tag_removed = pyqtSignal(str)
    rating_changed = pyqtSignal(int)
    notes_changed = pyqtSignal(str)
    save_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialisation de l'éditeur de métadonnées
        """
        super(MetadataEditor, self).__init__(parent)
        self.current_tags = []
        self.current_rating = 0
        self.all_tags = []
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Section des tags
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)
        
        # Nouveau widget de sélection de tags
        self.tag_selector = TagSelectorWidget(self.all_tags, self.current_tags)
        self.tag_selector.tags_changed.connect(self._on_tags_changed)
        self.tag_selector.tag_added.connect(self._on_tag_added)
        self.tag_selector.tag_removed.connect(self._on_tag_removed)
        tags_layout.addWidget(self.tag_selector)
        
        # Section de notation à étoiles
        rating_group = QGroupBox("Note du projet")
        rating_layout = QHBoxLayout(rating_group)
        
        self.lbl_rating = QLabel("Attribuer une note:")
        rating_layout.addWidget(self.lbl_rating)
        
        # Création des boutons d'étoiles
        self.rating_buttons = []
        for i in range(6):  # 0 à 5 étoiles
            btn = QPushButton(str(i) + " ★" if i > 0 else "0")
            btn.setProperty("rating", i)
            btn.clicked.connect(self.set_rating)
            self.rating_buttons.append(btn)
            rating_layout.addWidget(btn)
        
        # Section des notes
        notes_group = QGroupBox("Notes du projet")
        notes_layout = QVBoxLayout(notes_group)
        
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Ajoutez ici des notes sur le projet")
        self.txt_notes.setMinimumHeight(100)
        self.txt_notes.textChanged.connect(self._on_notes_changed)
        
        notes_layout.addWidget(self.txt_notes)
        
        # Bouton de sauvegarde
        self.btn_save = QPushButton("Sauvegarder les métadonnées")
        self.btn_save.clicked.connect(self._on_save_clicked)
        
        # Ajout des sections au layout principal
        main_layout.addWidget(tags_group)
        main_layout.addWidget(rating_group)
        main_layout.addWidget(notes_group)
        main_layout.addWidget(self.btn_save)
    
    def set_all_tags(self, tags):
        """
        Définition de la liste complète des tags pour l'auto-complétion
        """
        self.all_tags = tags
        self.tag_selector.set_tags(self.all_tags, self.current_tags)
    
    def set_metadata(self, metadata):
        """
        Définition des métadonnées à éditer
        """
        # Mise à jour des tags
        self.current_tags = metadata.get('tags', [])
        # Fusionner les tags du projet avec la liste globale (sans doublons)
        all_tags_set = set(self.all_tags) | set(self.current_tags)
        self.all_tags = list(all_tags_set)
        self.tag_selector.set_tags(self.all_tags, self.current_tags)
        
        # Mise à jour de la note
        self.current_rating = metadata.get('rating', 0)
        self.update_rating_buttons()
        
        # Mise à jour des notes
        self.txt_notes.setText(metadata.get('notes', ''))
    
    def get_metadata(self):
        """
        Récupération des métadonnées éditées
        """
        return {
            'tags': self.tag_selector.get_selected_tags(),
            'rating': self.current_rating,
            'notes': self.txt_notes.toPlainText()
        }
    
    # Ancienne méthode add_tag supprimée (remplacée par la gestion du TagSelectorWidget)

    
    # Ancienne méthode remove_tag supprimée (remplacée par la gestion du TagSelectorWidget)

    
    # Ancienne méthode update_tags_display supprimée (remplacée par la gestion du TagSelectorWidget)
    
    def set_rating(self):
        """Définition de la note du projet"""
        # Récupération du bouton qui a émis le signal
        sender = self.sender()
        if not sender:
            return
        
        # Récupération de la note
        rating = sender.property("rating")
        if rating is None:
            return
        
        # Mise à jour de la note
        self.current_rating = rating
        self.update_rating_buttons()
        
        # Émettre le signal
        self.rating_changed.emit(rating)
        self.metadata_changed.emit(self.get_metadata())

    def _on_tags_changed(self, tags):
        self.current_tags = tags
        self.metadata_changed.emit(self.get_metadata())

    def _on_tag_added(self, tag):
        self.tag_added.emit(tag)
        self.metadata_changed.emit(self.get_metadata())

    def _on_tag_removed(self, tag):
        self.tag_removed.emit(tag)
        self.metadata_changed.emit(self.get_metadata())
    
    def update_rating_buttons(self):
        """Mise à jour de l'apparence des boutons de notation"""
        for i, btn in enumerate(self.rating_buttons):
            if i <= self.current_rating:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("")
    
    def _on_notes_changed(self):
        """Gestion du changement des notes"""
        self.notes_changed.emit(self.txt_notes.toPlainText())
        self.metadata_changed.emit(self.get_metadata())
    
    def _on_save_clicked(self):
        """Gestion du clic sur le bouton de sauvegarde"""
        self.save_requested.emit()
