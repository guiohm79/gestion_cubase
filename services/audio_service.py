#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service de gestion audio pour l'application
"""

import os
from pathlib import Path

class AudioService:
    """Service de gestion audio pour les fichiers WAV"""
    
    def __init__(self):
        """Initialisation du service audio"""
        self.current_file = None
        self.player = None
    
    def initialize_player(self, player):
        """
        Initialisation du lecteur audio
        
        Args:
            player: Instance du lecteur audio (AudioPlayer)
        """
        self.player = player
    
    def load_file(self, file_path):
        """
        Chargement d'un fichier audio
        
        Args:
            file_path (str): Chemin du fichier audio
            
        Returns:
            bool: Succès du chargement
        """
        if not self.player:
            print("Erreur: Lecteur audio non initialisé")
            return False
        
        path = Path(file_path)
        if not path.exists() or path.suffix.lower() != '.wav':
            print(f"Fichier audio invalide: {file_path}")
            return False
        
        self.current_file = str(path)
        return self.player.load_file(self.current_file)
    
    def play(self):
        """
        Démarrage de la lecture
        
        Returns:
            bool: Succès de l'opération
        """
        if not self.player or not self.current_file:
            return False
        
        self.player.toggle_playback()
        return True
    
    def stop(self):
        """
        Arrêt de la lecture
        
        Returns:
            bool: Succès de l'opération
        """
        if not self.player:
            return False
        
        self.player.stop_playback()
        return True
    
    def get_file_info(self, file_path):
        """
        Récupération des informations sur un fichier audio
        
        Args:
            file_path (str): Chemin du fichier audio
            
        Returns:
            dict: Informations sur le fichier audio
        """
        try:
            from mutagen.wave import WAVE
            
            path = Path(file_path)
            if not path.exists() or path.suffix.lower() != '.wav':
                return None
            
            audio = WAVE(file_path)
            
            # Récupération des informations
            info = {
                'path': file_path,
                'name': path.name,
                'size': path.stat().st_size,
                'size_mb': round(path.stat().st_size / (1024 * 1024), 2),
                'duration': audio.info.length,
                'duration_formatted': self._format_duration(audio.info.length),
                'sample_rate': audio.info.sample_rate,
                'channels': audio.info.channels,
                'bitrate': audio.info.bitrate
            }
            
            return info
        except Exception as e:
            print(f"Erreur lors de la récupération des informations sur le fichier audio: {e}")
            return None
    
    def _format_duration(self, seconds):
        """
        Formatage de la durée en minutes:secondes
        
        Args:
            seconds (float): Durée en secondes
            
        Returns:
            str: Durée formatée
        """
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
