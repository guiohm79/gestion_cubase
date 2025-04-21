from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTreeWidget, QTreeWidgetItem, QTableWidget, 
                            QTableWidgetItem, QPushButton, QSplitter, 
                            QHeaderView, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET
import os

class GestionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.xml_root = None
        self.current_category = None
        self.setup_ui()

    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Titre et boutons en haut
        top_layout = QHBoxLayout()
        self.title_label = QLabel("Éditeur de raccourcis Cubase")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.open_button = QPushButton("Ouvrir")
        self.open_button.clicked.connect(self.open_file)
        
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setEnabled(False)
        
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.open_button)
        top_layout.addWidget(self.save_button)
        
        # Splitter pour diviser l'écran
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panneau de gauche : liste des catégories
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabels(["Catégories"])
        self.category_tree.itemClicked.connect(self.on_category_selected)
        
        # Panneau de droite : tableau des commandes
        self.command_table = QTableWidget()
        self.command_table.setColumnCount(2)
        self.command_table.setHorizontalHeaderLabels(["Commande", "Raccourci"])
        self.command_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.command_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        # Ajout des widgets au splitter
        self.splitter.addWidget(self.category_tree)
        self.splitter.addWidget(self.command_table)
        self.splitter.setSizes([200, 600])  # Tailles initiales
        
        # Boutons d'action en bas
        bottom_layout = QHBoxLayout()
        
        self.add_shortcut_btn = QPushButton("Ajouter raccourci")
        self.add_shortcut_btn.clicked.connect(self.add_shortcut)
        self.add_shortcut_btn.setEnabled(False)
        
        self.remove_shortcut_btn = QPushButton("Supprimer raccourci")
        self.remove_shortcut_btn.clicked.connect(self.remove_shortcut)
        self.remove_shortcut_btn.setEnabled(False)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.add_shortcut_btn)
        bottom_layout.addWidget(self.remove_shortcut_btn)
        
        # Assemblage final
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.splitter)
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un fichier de raccourcis", "", "Fichiers XML (*.xml)")
        
        if file_path:
            try:
                self.current_file = file_path
                tree = ET.parse(file_path)
                self.xml_root = tree.getroot()
                self.load_categories()
                self.save_button.setEnabled(True)
                self.add_shortcut_btn.setEnabled(True)
                self.title_label.setText(f"Éditeur de raccourcis - {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")
    
    def load_categories(self):
        # Vider la liste actuelle
        self.category_tree.clear()
        
        if self.xml_root is None:
            return
            
        # Trouver l'élément qui contient les catégories
        preset_elem = self.xml_root.find("./member[@name='Preset']")
        if preset_elem is None:
            return
            
        categories_elem = preset_elem.find("./list[@name='Categories']")
        if categories_elem is None:
            return
            
        # Ajouter chaque catégorie au TreeWidget
        for category_item in categories_elem.findall("./item"):
            category_name_elem = category_item.find("./string[@name='Name']")
            if category_name_elem is None:
                continue
                
            category_name = category_name_elem.get("value")
            
            # Créer l'élément dans la liste
            tree_item = QTreeWidgetItem([category_name])
            self.category_tree.addTopLevelItem(tree_item)
    
    def on_category_selected(self, item):
        self.current_category = item.text(0)
        self.load_commands()
    
    def load_commands(self):
        # Vider le tableau
        self.command_table.setRowCount(0)
        
        if self.xml_root is None or self.current_category is None:
            return
        
        # Chercher la catégorie dans le XML
        preset_elem = self.xml_root.find("./member[@name='Preset']")
        categories_elem = preset_elem.find("./list[@name='Categories']")
        
        for category_item in categories_elem.findall("./item"):
            category_name_elem = category_item.find("./string[@name='Name']")
            if category_name_elem is None or category_name_elem.get("value") != self.current_category:
                continue
            
            # Trouver les commandes
            commands_elem = category_item.find("./list[@name='Commands']")
            if commands_elem is None:
                break
            
            # Parcourir toutes les commandes
            for command_item in commands_elem.findall("./item"):
                command_name_elem = command_item.find("./string[@name='Name']")
                if command_name_elem is None:
                    continue
                
                command_name = command_name_elem.get("value")
                shortcut_text = ""
                
                # Chercher les raccourcis
                key_elem = command_item.find("./string[@name='Key']")
                if key_elem is not None:
                    shortcut_text = key_elem.get("value")
                else:
                    # Essayer de trouver une liste de touches
                    key_list = command_item.find("./list[@name='Key']")
                    if key_list is not None:
                        shortcuts = []
                        for key_item in key_list.findall("./item"):
                            shortcuts.append(key_item.get("value"))
                        shortcut_text = ", ".join(shortcuts)
                
                # Ajouter à la table
                row = self.command_table.rowCount()
                self.command_table.insertRow(row)
                self.command_table.setItem(row, 0, QTableWidgetItem(command_name))
                self.command_table.setItem(row, 1, QTableWidgetItem(shortcut_text))
            
            break
    
    def add_shortcut(self):
        # À implémenter: ouvrir une boîte de dialogue pour ajouter un raccourci
        QMessageBox.information(self, "Info", "Fonctionnalité à venir: Ajouter un raccourci")
    
    def remove_shortcut(self):
        # À implémenter: supprimer le raccourci sélectionné
        QMessageBox.information(self, "Info", "Fonctionnalité à venir: Supprimer un raccourci")
    
    def save_file(self):
        if self.current_file and self.xml_root is not None:
            try:
                tree = ET.ElementTree(self.xml_root)
                tree.write(self.current_file, encoding="utf-8", xml_declaration=True)
                QMessageBox.information(self, "Succès", "Fichier enregistré avec succès!")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible d'enregistrer le fichier: {str(e)}")
