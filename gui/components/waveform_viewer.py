import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QLinearGradient, QBrush
from scipy.io import wavfile

class ModernWaveformPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setMinimumWidth(400)
        
        # Variables pour les données audio
        self.waveform_data = None
        self.sample_rate = None
        self.duration = 0
        self.current_position = 0
        
        # Interface
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget personnalisé pour le rendu de la forme d'onde
        self.waveform_widget = WaveformWidget(self)
        layout.addWidget(self.waveform_widget)
        
        # Minuteur moderne sous la waveform
        timer_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.duration_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #FFA000; padding: 0 10px;")
        self.duration_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #f18300; padding: 0 10px;")
        timer_layout.addStretch()
        timer_layout.addWidget(self.current_time_label)
        # Séparateur visuel moderne
        sep = QLabel("/")
        sep.setStyleSheet("font-size: 50px; font-weight: bold; color: #555; padding: 0 10px;")
        timer_layout.addWidget(sep)
        timer_layout.addWidget(self.duration_label)
        timer_layout.addStretch()
        layout.addLayout(timer_layout)
        # Référence au player audio PyQt
        self.audio_player = None
        
    def link_audio_player(self, audio_player):
        """Connecte le player audio PyQt pour synchronisation"""
        self.audio_player = audio_player
        # Connexion des signaux de position/durée
        self.audio_player.player.positionChanged.connect(self.on_audio_position_changed)
        self.audio_player.player.durationChanged.connect(self.on_audio_duration_changed)

    def on_audio_position_changed(self, position_ms):
        if self.duration > 0:
            progress = position_ms / (self.duration * 1000)
            self.waveform_widget.set_progress(progress)
            self.current_time_label.setText(self.format_time(position_ms / 1000))

    def on_audio_duration_changed(self, duration_ms):
        self.duration = duration_ms / 1000
        self.duration_label.setText(self.format_time(self.duration))
        self.waveform_widget.set_duration(self.duration)

    def load_file(self, file_path):
        """Charge un fichier audio et prépare la visualisation"""
        try:
            # Charger les données audio
            sample_rate, data = wavfile.read(file_path)
            
            # Conversion mono si stéréo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # Normaliser les données
            if data.dtype != np.float32:
                data = data.astype(np.float32) / (2**15 if data.dtype == np.int16 else 2**31)
            
            # Sous-échantillonner pour l'affichage
            # Pour un affichage fluide, réduire à ~1000-2000 points
            n_points = min(1500, len(data))
            step = max(1, len(data) // n_points)
            waveform_data = data[::step]
            
            # Stocker les données
            self.waveform_data = waveform_data
            self.sample_rate = sample_rate
            self.duration = len(data) / sample_rate
            self.current_position = 0
            
            # Mettre à jour les labels
            self.duration_label.setText(self.format_time(self.duration))
            self.current_time_label.setText(self.format_time(0))
            
            # Mettre à jour le widget de forme d'onde
            self.waveform_widget.set_waveform_data(waveform_data)
            self.waveform_widget.set_duration(self.duration)
            
            return True
        except Exception as e:
            print(f"Erreur lors du chargement du fichier audio: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def play_pause(self):
        """Démarre ou met en pause la lecture"""
        if self.audio_player:
            self.audio_player.toggle_playback()
            return True
        return False
    
    def stop(self):
        """Arrête la lecture et réinitialise la position"""
        if self.audio_player:
            self.audio_player.stop_playback()
        self.current_time_label.setText(self.format_time(0))
        self.waveform_widget.set_progress(0)
        
    # update_position supprimé (plus de simulation, synchronisation réelle via signaux)
    
    def on_waveform_seek(self, percent):
        """Seek audio lors d'un clic sur la waveform"""
        if self.audio_player and self.duration > 0:
            new_position_ms = int(percent * self.duration * 1000)
            self.audio_player.set_position(new_position_ms)
    
    def format_time(self, seconds):
        """Formate le temps en minutes:secondes"""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes}:{seconds:02d}"


class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        
        # Données pour le rendu
        self.waveform_data = None
        self.progress = 0  # 0 à 1
        self.duration = 0  # Durée en secondes
        
        # Couleurs
        self.played_color = QColor(255, 120, 0)  # Orange pour la partie jouée
        self.remaining_color = QColor(241, 184, 140)  # Blanc pour la partie restante
        self.background_color = QColor(30, 30, 30, 0)  # Fond presque noir

    def set_duration(self, duration):
        self.duration = duration
        self.update()

    def format_time(self, seconds):
        seconds = int(seconds)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
        
    def set_waveform_data(self, data):
        """Définit les données de forme d'onde à afficher"""
        self.waveform_data = data
        self.update()

    def set_duration(self, duration):
        self.duration = duration
        self.update()

    def mousePressEvent(self, event):
        if self.waveform_data is None or not hasattr(self.parent(), 'on_waveform_seek'):
            return
        x = event.x()
        percent = x / self.width()
        self.parent().on_waveform_seek(percent)

        
    def set_progress(self, progress):
        """Définit la progression de la lecture (0-1)"""
        self.progress = max(0, min(1, progress))
        self.update()
        
    def paintEvent(self, event):
        """Dessine la forme d'onde"""
        if self.waveform_data is None:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fond
        painter.fillRect(self.rect(), self.background_color)
        
        # Dimensions
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Position de progression
        progress_x = int(width * self.progress)
        
        # Dessin de la forme d'onde
        if len(self.waveform_data) > 0:
            # Distance entre chaque point
            dx = width / len(self.waveform_data)
            
            # Amplitude maximale pour la mise à l'échelle
            max_amp = max(abs(self.waveform_data.min()), abs(self.waveform_data.max()))
            scale = (height * 0.8) / (max_amp * 2)
            
            # Dessin de chaque segment de la forme d'onde
            for i in range(len(self.waveform_data) - 1):
                x1 = i * dx
                x2 = (i + 1) * dx
                
                amp1 = self.waveform_data[i] * scale
                amp2 = self.waveform_data[i + 1] * scale
                
                y1 = center_y - amp1
                y2 = center_y - amp2
                
                # Choisir la couleur selon la position
                if x1 <= progress_x:
                    pen = QPen(self.played_color, 2)
                else:
                    pen = QPen(self.remaining_color, 2)
                
                painter.setPen(pen)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                
                # Dessiner aussi la partie inférieure de la forme d'onde
                y1_bottom = center_y + amp1
                y2_bottom = center_y + amp2
                painter.drawLine(int(x1), int(y1_bottom), int(x2), int(y2_bottom))
        
        # Dessiner les indicateurs de temps
        time_font = painter.font()
        time_font.setPointSize(8)
        painter.setFont(time_font)
        
        # Début (toujours orange)
        painter.setPen(self.played_color)
        painter.drawText(5, height - 5, "0:00")
        
        # Fin (toujours blanc)
        painter.setPen(self.remaining_color)
        painter.drawText(width - 40, height - 5, self.format_time(self.duration))