#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composant de lecteur audio unifié pour les fichiers WAV
"""

from PyQt5.QtCore import QUrl, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QSizePolicy, QStyle
)
from PyQt5.QtCore import Qt
from pathlib import Path

class AudioPlayer(QWidget):
    """Lecteur audio unifié pour les fichiers WAV"""
    
    # Signal émis lorsque la lecture est terminée
    playback_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialisation du lecteur audio
        
        Args:
            parent (QWidget): Widget parent
        """
        super(AudioPlayer, self).__init__(parent)
        
        # Création du lecteur média
        self.player = QMediaPlayer()
        self.player.stateChanged.connect(self.on_state_changed)
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        
        # Chemin du fichier audio actuel
        self.current_file = None
        
        # Configuration de l'interface
        self.setup_ui()
        
        # Timer pour mettre à jour la position
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(100)  # 100ms
        self.update_timer.timeout.connect(self.update_position)
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Label pour le nom du fichier
        self.lbl_filename = QLabel("Aucun fichier sélectionné")
        self.lbl_filename.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_filename)
        
        # Layout pour les contrôles
        controls_layout = QHBoxLayout()
        
        # Bouton de lecture/pause
        self.btn_play = QPushButton()
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play.clicked.connect(self.toggle_playback)
        self.btn_play.setEnabled(False)
        
        # Bouton d'arrêt
        self.btn_stop = QPushButton()
        self.btn_stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.btn_stop.clicked.connect(self.stop_playback)
        self.btn_stop.setEnabled(False)
        
        # Labels pour la position et la durée
        self.lbl_position = QLabel("00:00")
        self.lbl_duration = QLabel("00:00")
        
        # Ajout des widgets au layout des contrôles
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.lbl_position)
        controls_layout.addWidget(self.lbl_duration)
        
        # Ajout du layout des contrôles au layout principal
        layout.addLayout(controls_layout)
        
        # Configuration des tailles
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def load_file(self, file_path):
        """
        Chargement d'un fichier audio
        
        Args:
            file_path (str): Chemin du fichier audio
        
        Returns:
            bool: Succès du chargement
        """
        # Arrêt de la lecture en cours
        self.stop_playback()
        
        # Chargement du fichier
        path = Path(file_path)
        if not path.exists() or path.suffix.lower() != '.wav':
            self.lbl_filename.setText("Fichier invalide")
            self.current_file = None
            self.btn_play.setEnabled(False)
            self.btn_stop.setEnabled(False)
            return False
        
        # Mise à jour de l'interface
        self.lbl_filename.setText(path.name)
        self.current_file = str(path)
        
        # Chargement du média
        url = QUrl.fromLocalFile(str(path))
        media = QMediaContent(url)
        self.player.setMedia(media)
        
        # Activation des contrôles
        self.btn_play.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
        return True
    
    @pyqtSlot()
    def toggle_playback(self):
        """Démarrage ou pause de la lecture"""
        if not self.current_file:
            return
        
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.update_timer.stop()
        else:
            self.player.play()
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.btn_stop.setEnabled(True)
            self.update_timer.start()
    
    @pyqtSlot()
    def stop_playback(self):
        """Arrêt de la lecture"""
        self.player.stop()
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_stop.setEnabled(False)
        self.update_timer.stop()
    
    def on_state_changed(self, state):
        """
        Gestion des changements d'état du lecteur
        
        Args:
            state (int): Nouvel état du lecteur
        """
        if state == QMediaPlayer.StoppedState:
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.btn_stop.setEnabled(False)
            self.update_timer.stop()
            self.playback_finished.emit()
    
    def on_position_changed(self, position):
        """
        Mise à jour de la position dans l'interface
        
        Args:
            position (int): Nouvelle position en millisecondes
        """
        # Mise à jour du label de position
        minutes = position // 60000
        seconds = (position % 60000) // 1000
        self.lbl_position.setText(f"{minutes:02d}:{seconds:02d}")
    
    def on_duration_changed(self, duration):
        """
        Mise à jour de la durée dans l'interface
        
        Args:
            duration (int): Durée en millisecondes
        """
        # Mise à jour du label de durée
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        self.lbl_duration.setText(f"{minutes:02d}:{seconds:02d}")
    
    def set_position(self, position):
        """
        Définition de la position de lecture
        
        Args:
            position (int): Position en millisecondes
        """
        self.player.setPosition(position)
        # Plus de synchronisation avec slider
    
    def update_position(self):
        """Mise à jour de la position actuelle"""
        position = self.player.position()
        self.on_position_changed(position)
    
    def get_current_file(self):
        """
        Récupération du fichier audio actuel
        
        Returns:
            str: Chemin du fichier audio actuel ou None
        """
        return self.current_file
