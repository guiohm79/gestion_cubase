from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLineEdit, QLabel, QSizePolicy, QScrollArea, QFrame
from PyQt5.QtCore import pyqtSignal, Qt
from services.tag_manager import TagManager

class TagBubble(QPushButton):
    """Bulle de tag cliquable (projet ou populaire)"""
    def __init__(self, tag, selected=False, parent=None, popular=False):
        super().__init__(tag, parent)
        self.tag = tag
        self.popular = popular
        self.setCheckable(True)
        self.setChecked(selected)
        self.update_style()
        self.clicked.connect(self.update_style)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if self.popular:
            self.setText(f'★ {tag}')

    def update_style(self):
        if self.popular:
            if self.isChecked():
                self.setStyleSheet("background-color: #ff9800; color: white; border-radius: 12px; padding: 4px 12px; margin: 2px; border: 2px solid #ff9800; font-weight: bold;")
            else:
                self.setStyleSheet("background-color: #ffe0b2; color: #ff9800; border-radius: 12px; padding: 4px 12px; margin: 2px; border: 2px dashed #ff9800;")
        else:
            if self.isChecked():
                self.setStyleSheet("background-color: #3399ff; color: white; border-radius: 12px; padding: 4px 12px; margin: 2px; border: 1px solid #007acc;")
            else:
                self.setStyleSheet("background-color: #e0e0e0; color: #222; border-radius: 12px; padding: 4px 12px; margin: 2px; border: 1px solid #bbb;")


class TagSelectorWidget(QWidget):
    tags_changed = pyqtSignal(list)
    tag_added = pyqtSignal(str)
    tag_removed = pyqtSignal(str)

    def __init__(self, all_tags=None, selected_tags=None, parent=None):
        super().__init__(parent)
        self.all_tags = all_tags if all_tags is not None else []
        self.selected_tags = set(selected_tags) if selected_tags is not None else set()
        self.bubbles = {}
        self.popular_bubbles = {}
        self.tag_manager = TagManager()
        self._setup_ui()
        self.refresh_bubbles()
        self.refresh_popular_tags()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Titre section tags projet
        main_layout.addWidget(QLabel("<b>Tags du projet :</b>"))

        # Scroll area for tag bubbles (tags du projet)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.bubble_container = QWidget()
        self.bubble_layout = QHBoxLayout(self.bubble_container)
        self.bubble_layout.setContentsMargins(0, 0, 0, 0)
        self.bubble_layout.setSpacing(2)
        self.bubble_container.setLayout(self.bubble_layout)
        self.scroll.setWidget(self.bubble_container)
        main_layout.addWidget(self.scroll)

        # Input for new tags
        input_layout = QHBoxLayout()
        self.txt_tag_input = QLineEdit()
        self.txt_tag_input.setPlaceholderText("Ajouter un tag et appuyer sur Entrée")
        self.txt_tag_input.returnPressed.connect(self._on_add_tag)
        input_layout.addWidget(self.txt_tag_input)
        main_layout.addLayout(input_layout)

        # Séparateur visuel
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Titre section tags populaires
        main_layout.addWidget(QLabel("<b>Tags les plus utilisés :</b>"))
        self.popular_frame = QFrame()
        self.popular_layout = QHBoxLayout(self.popular_frame)
        self.popular_layout.setContentsMargins(0, 0, 0, 0)
        self.popular_layout.setSpacing(2)
        main_layout.addWidget(self.popular_frame)
        self.popular_frame.setVisible(False)
        # Texte d'aide
        self.popular_hint = QLabel('<span style="color:#ff9800;font-size:10px;">Cliquez pour ajouter ce tag au projet</span>')
        main_layout.addWidget(self.popular_hint)
        self.popular_hint.setVisible(False)


    def refresh_bubbles(self):
        # Clear existing
        for i in reversed(range(self.bubble_layout.count())):
            widget = self.bubble_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.bubbles.clear()
        # Afficher uniquement les tags sélectionnés dans le projet
        for tag in self.selected_tags:
            bubble = TagBubble(tag, True)
            bubble.clicked.connect(lambda checked, t=tag: self._on_bubble_clicked(t, checked))
            self.bubble_layout.addWidget(bubble)
            self.bubbles[tag] = bubble
        self.bubble_layout.addStretch(1)

    def refresh_popular_tags(self):
        top_tags = self.tag_manager.get_top_tags(5)
        self.set_popular_tags(top_tags)

    def set_popular_tags(self, popular_tags):
        """
        Met à jour la section des tags populaires (top N).
        N'affiche que les tags non sélectionnés dans le projet.
        """
        # Effacer les bulles existantes
        for i in reversed(range(self.popular_layout.count())):
            widget = self.popular_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.popular_bubbles.clear()
        # Filtrer les tags déjà sélectionnés
        filtered_tags = [tag for tag in popular_tags if tag not in self.selected_tags]
        if filtered_tags:
            self.popular_frame.setVisible(True)
            self.popular_hint.setVisible(True)
        else:
            self.popular_frame.setVisible(False)
            self.popular_hint.setVisible(False)
        # Ajouter les bulles populaires (seulement non sélectionnées)
        for tag in filtered_tags:
            bubble = TagBubble(tag, False, popular=True)
            bubble.clicked.connect(lambda checked, t=tag: self._on_bubble_clicked(t, checked))
            self.popular_layout.addWidget(bubble)
            self.popular_bubbles[tag] = bubble

    def _on_bubble_clicked(self, tag, checked):
        if checked:
            self.selected_tags.add(tag)
            self.tag_added.emit(tag)
            self.tag_manager.add_or_increment_tag(tag)
        else:
            self.selected_tags.discard(tag)
            self.tag_removed.emit(tag)
        # Toujours synchroniser les deux sections
        self.refresh_bubbles()
        self.refresh_popular_tags()
        self.tags_changed.emit(list(self.selected_tags))

    def _on_add_tag(self):
        tag = self.txt_tag_input.text().strip()
        if tag and tag not in self.selected_tags:
            self.selected_tags.add(tag)
            self.all_tags.append(tag)
            self.tag_added.emit(tag)
            self.tag_manager.add_or_increment_tag(tag)
        elif tag and tag in self.all_tags:
            # Si déjà présent, simplement le sélectionner
            self.selected_tags.add(tag)
        # Toujours synchroniser les deux sections
        self.refresh_bubbles()
        self.refresh_popular_tags()
        self.tags_changed.emit(list(self.selected_tags))
        self.txt_tag_input.clear()

    def set_tags(self, all_tags, selected_tags=None):
        all_tags_set = set(all_tags)
        if selected_tags is not None:
            all_tags_set |= set(selected_tags)
        self.all_tags = list(all_tags_set)
        self.selected_tags = set(selected_tags) if selected_tags is not None else set()
        self.refresh_bubbles()

    def get_selected_tags(self):
        return list(self.selected_tags)
