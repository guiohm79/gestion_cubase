from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                            QTreeWidget, QTreeWidgetItem, QTableWidget, 
                            QTableWidgetItem, QPushButton, QSplitter, 
                            QHeaderView, QMessageBox, QFileDialog,
                            QToolBar, QAction, QDialog, QLineEdit, QFormLayout, QKeySequenceEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence

from lxml import etree as lxml_etree
import os

from gui.base.base_window import BaseWindow

class GestionWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.current_file = None
        self.xml_tree = None  # Pour conserver l'arbre XML complet
        self.xml_root = None
        self.current_category = None
        self.setup_ui()
        
        # Mise à jour du titre
        self.setWindowTitle("Tri Morceaux Cubase - Mode Gestion")

    def setup_specific_toolbar(self):
        """Configuration spécifique de l'interface"""
        # Créer une barre d'outils pour les actions spécifiques
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # Action pour ouvrir un fichier
        self.action_open = QAction("Ouvrir", self)
        self.action_open.triggered.connect(self.open_file)
        toolbar.addAction(self.action_open)
        
        # Action pour sauvegarder
        self.action_save = QAction("Enregistrer", self)
        self.action_save.triggered.connect(self.save_file)
        self.action_save.setEnabled(False)
        toolbar.addAction(self.action_save)
        
        # Ajouter la barre d'outils au layout de contenu
        self.content_layout.addWidget(toolbar)
    
    def setup_ui(self):
        # Titre en haut
        top_layout = QHBoxLayout()
        self.title_label = QLabel("Éditeur de raccourcis Cubase")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        
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
        # Double-clic pour éditer un raccourci
        self.command_table.itemDoubleClicked.connect(self.edit_shortcut)
        
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
        
        # Assemblage final dans le layout de contenu
        self.content_layout.addLayout(top_layout)
        self.content_layout.addWidget(self.splitter, 1)  # Stretch pour prendre tout l'espace disponible
        self.content_layout.addLayout(bottom_layout)
    
    def open_file(self):
        """Ouvre un fichier XML de raccourcis Cubase"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un fichier de raccourcis", "", "Fichiers XML (*.xml)")
        
        if not file_path:
            return
            
        try:
            # Utiliser lxml qui est plus tolérant aux erreurs
            parser = lxml_etree.XMLParser(recover=True)
            self.xml_tree = lxml_etree.parse(file_path, parser)
            self.xml_root = self.xml_tree.getroot()
            self.current_file = file_path
            
            self.load_categories()
            
            # Activer les boutons
            self.action_save.setEnabled(True)
            
            # Mettre à jour le titre
            self.title_label.setText(f"Éditeur de raccourcis - {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")
    
    def load_categories(self):
        """Charge les catégories depuis le XML"""
        # Vider la liste actuelle
        self.category_tree.clear()
        
        if self.xml_root is None:
            return
        
        try:    
            # Trouver l'élément qui contient les catégories avec lxml
            preset_elem = self.xml_root.xpath("./member[@name='Preset']")
            if not preset_elem:
                QMessageBox.warning(self, "Erreur", "Structure XML non reconnue: élément 'Preset' introuvable")
                return
                
            categories_elem = preset_elem[0].xpath("./list[@name='Categories']")
            if not categories_elem:
                QMessageBox.warning(self, "Erreur", "Structure XML non reconnue: élément 'Categories' introuvable")
                return
                
            # Ajouter chaque catégorie au TreeWidget
            for category_item in categories_elem[0].xpath("./item"):
                category_name_elem = category_item.xpath("./string[@name='Name']")
                if not category_name_elem:
                    continue
                    
                category_name = category_name_elem[0].get("value")
                
                # Créer l'élément dans la liste
                tree_item = QTreeWidgetItem([category_name])
                self.category_tree.addTopLevelItem(tree_item)
                
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des catégories: {str(e)}")
    
    def on_category_selected(self, item):
        """Gère la sélection d'une catégorie"""
        self.current_category = item.text(0)
        self.load_commands()
        # Activer le bouton d'ajout quand une catégorie est sélectionnée
        self.add_shortcut_btn.setEnabled(True)
    
    def load_commands(self):
        """Charge les commandes de la catégorie sélectionnée"""
        # Vider le tableau
        self.command_table.setRowCount(0)
        
        if self.xml_root is None or self.current_category is None:
            return
        
        try:
            # Chercher la catégorie avec XPath (plus robuste)
            xpath_query = f".//item[string[@name='Name'][@value='{self.current_category}']]"
            category_items = self.xml_root.xpath(xpath_query)
            
            if not category_items:
                return
                
            category_item = category_items[0]
            
            # Trouver les commandes
            commands_elem = category_item.xpath("./list[@name='Commands']")
            if not commands_elem:
                return
                
            # Parcourir toutes les commandes
            for command_item in commands_elem[0].xpath("./item"):
                command_name_elem = command_item.xpath("./string[@name='Name']")
                if not command_name_elem:
                    continue
                
                command_name = command_name_elem[0].get("value")
                shortcut_text = ""
                
                # Chercher les raccourcis
                key_elem = command_item.xpath("./string[@name='Key']")
                if key_elem:
                    shortcut_text = key_elem[0].get("value")
                else:
                    # Essayer de trouver une liste de touches
                    key_list = command_item.xpath("./list[@name='Key']/item")
                    if key_list:
                        shortcuts = [key.get("value") for key in key_list if key.get("value")]
                        shortcut_text = ", ".join(shortcuts)
                
                # Ajouter à la table
                row = self.command_table.rowCount()
                self.command_table.insertRow(row)
                self.command_table.setItem(row, 0, QTableWidgetItem(command_name))
                self.command_table.setItem(row, 1, QTableWidgetItem(shortcut_text))
                
            # Activer le bouton de suppression si des commandes sont affichées
            self.remove_shortcut_btn.setEnabled(self.command_table.rowCount() > 0)
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des commandes: {str(e)}")
    
    def edit_shortcut(self, item):
        """Édite un raccourci existant via double-clic"""
        # Ne réagir que si on double-clique sur la colonne des raccourcis
        if item.column() != 1:
            return
            
        row = item.row()
        command_name = self.command_table.item(row, 0).text()
        current_shortcut = item.text()
        
        # Petite boîte de dialogue pour éditer le raccourci
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Modifier le raccourci pour {command_name}")
        layout = QFormLayout(dialog)
        
        # On utilise QKeySequenceEdit au lieu de QLineEdit
        shortcut_edit = QKeySequenceEdit()
        
        # On convertit le raccourci Cubase en QKeySequence
        if current_shortcut:
            # Format Cubase: "Ctrl+R" -> format Qt: "Ctrl+R"
            # C'est assez similaire mais il peut y avoir des différences
            # qu'on pourrait gérer avec une fonction de conversion plus complexe
            shortcut_edit.setKeySequence(QKeySequence(current_shortcut))
        
        layout.addRow("Appuie sur les touches du nouveau raccourci:", shortcut_edit)
        layout.addRow(QLabel("(ESC pour effacer)"))
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Annuler")
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)
        
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer la séquence de touches et la convertir en texte
            key_sequence = shortcut_edit.keySequence()
            new_shortcut = key_sequence.toString()
            
            if new_shortcut != current_shortcut:
                # Mettre à jour l'affichage
                item.setText(new_shortcut)
                # Mettre à jour le XML
                self.update_shortcut_in_xml(command_name, current_shortcut, new_shortcut)

    def save_file(self):
        """Sauvegarde les modifications dans le fichier XML à la mode bucheron"""
        if self.current_file and self.xml_tree is not None:
            try:
                # Proposer d'enregistrer sous un nouveau nom
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Enregistrer le fichier de raccourcis", self.current_file,
                    "Fichiers XML (*.xml)")
                
                if not file_path:
                    return
                
                # Débugage : Afficher l'arbre XML en console (en commentaire)
                # print("Contenu de l'arbre XML avant sauvegarde:", lxml_etree.tostring(self.xml_root, pretty_print=True, encoding='unicode'))
                
                # Créer un nouvel objet ElementTree pour la sauvegarde
                # (parfois ça règle les problèmes bizarres)
                tree_to_save = lxml_etree.ElementTree(self.xml_root)
                
                # Sauvegarde BRUTALE avec mode direct
                with open(file_path, 'wb') as f:
                    # L'en-tête XML manuellement pour être sûr
                    f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
                    # Sortie directe en UTF-8
                    f.write(lxml_etree.tostring(self.xml_root, pretty_print=True, xml_declaration=False, encoding='utf-8'))
                
                # Vérifier que le fichier existe et a une taille > 0
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    # Mettre à jour le nom du fichier courant si nécessaire
                    if file_path != self.current_file:
                        self.current_file = file_path
                        self.title_label.setText(f"Éditeur de raccourcis - {os.path.basename(file_path)}")
                    
                    QMessageBox.information(self, "Succès", f"Fichier sauvegardé : {file_path} ({os.path.getsize(file_path)} octets)")
                else:
                    QMessageBox.warning(self, "Problème", "Le fichier a été créé mais semble vide. Vérifie les permissions.")
                
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible d'enregistrer le fichier: {str(e)}")
                # Afficher l'erreur en console pour debug
                print(f"ERREUR SAUVEGARDE: {str(e)}")

    def update_shortcut_in_xml(self, command_name, old_shortcut, new_shortcut):
        """Met à jour un raccourci dans le fichier XML"""
        try:
            # Chercher la commande dans la catégorie actuelle
            xpath_query = f".//item[string[@name='Name'][@value='{self.current_category}']]"
            category_items = self.xml_root.xpath(xpath_query)
            
            if not category_items:
                return
                
            category_item = category_items[0]
            
            # Trouver la commande
            cmd_xpath = f"./list[@name='Commands']/item[string[@name='Name'][@value='{command_name}']]"
            command_items = category_item.xpath(cmd_xpath)
            
            if not command_items:
                return
                
            command_item = command_items[0]
            
            # Mettre à jour le raccourci
            key_elem = command_item.xpath("./string[@name='Key']")
            key_list = command_item.xpath("./list[@name='Key']")
            if key_elem:
                # C'est un raccourci simple
                key_elem[0].set("value", new_shortcut)
            elif key_list:
                # Parcourir les items pour trouver celui qui correspond à l'ancien raccourci
                for key_item in key_list[0].xpath("./item"):
                    if key_item.get("value") == old_shortcut:
                        key_item.set("value", new_shortcut)
                        break
            else:
                # Aucun raccourci existant : créer la balise
                lxml_etree.SubElement(command_item, "string", name="Key", value=new_shortcut, wide="true")
            # Le fichier est maintenant modifié, activer la sauvegarde
            self.action_save.setEnabled(True)
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la mise à jour du raccourci: {str(e)}")
    
    def add_shortcut(self):
        """Ajoute un nouveau raccourci à la commande sélectionnée"""
        # Vérifier qu'une commande est sélectionnée
        current_row = self.command_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une commande d'abord")
            return
            
        command_name = self.command_table.item(current_row, 0).text()
        
        # Petite boîte de dialogue pour ajouter un raccourci
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ajouter un raccourci pour {command_name}")
        layout = QFormLayout(dialog)
        
        # On utilise QKeySequenceEdit pour capturer les touches directement
        shortcut_edit = QKeySequenceEdit()
        layout.addRow("Appuie sur les touches du raccourci:", shortcut_edit)
        layout.addRow(QLabel("(ESC pour effacer)"))
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Annuler")
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)
        
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer la séquence de touches et la convertir en texte
            key_sequence = shortcut_edit.keySequence()
            new_shortcut = key_sequence.toString()
            
            if new_shortcut:
                # Ajouter le raccourci au XML
                if self.add_shortcut_to_xml(command_name, new_shortcut):
                    # Recharger la liste des commandes pour mettre à jour l'affichage
                    self.load_commands()
    
    def add_shortcut_to_xml(self, command_name, new_shortcut):
        """Ajoute un raccourci dans le fichier XML"""
        try:
            # Chercher la commande dans la catégorie actuelle
            xpath_query = f".//item[string[@name='Name'][@value='{self.current_category}']]"
            category_items = self.xml_root.xpath(xpath_query)
            
            if not category_items:
                return False
                
            category_item = category_items[0]
            
            # Trouver la commande
            cmd_xpath = f"./list[@name='Commands']/item[string[@name='Name'][@value='{command_name}']]"
            command_items = category_item.xpath(cmd_xpath)
            
            if not command_items:
                return False
                
            command_item = command_items[0]
            
            # Vérifier si le raccourci existe déjà pour cette commande
            key_elem = command_item.xpath("./string[@name='Key']")
            if key_elem and key_elem[0].get("value") == new_shortcut:
                QMessageBox.warning(self, "Doublon", f"Ce raccourci existe déjà pour cette commande.")
                return False
            key_list = command_item.xpath("./list[@name='Key']")
            if key_list:
                for key_item in key_list[0].xpath("./item"):
                    if key_item.get("value") == new_shortcut:
                        QMessageBox.warning(self, "Doublon", f"Ce raccourci existe déjà pour cette commande.")
                        return False
            
            # Ajout du raccourci
            if key_elem:
                # Il y a déjà un raccourci simple, le convertir en liste
                old_shortcut = key_elem[0].get("value")
                # Supprimer l'ancien élément string
                parent = key_elem[0].getparent()
                parent.remove(key_elem[0])
                # Créer un nouvel élément list
                key_list_elem = lxml_etree.SubElement(command_item, "list", name="Key", type="string")
                # Ajouter l'ancien raccourci comme premier item
                lxml_etree.SubElement(key_list_elem, "item", value=old_shortcut)
                # Ajouter le nouveau raccourci comme deuxième item
                lxml_etree.SubElement(key_list_elem, "item", value=new_shortcut)
            elif key_list:
                # Ajouter à la liste existante
                lxml_etree.SubElement(key_list[0], "item", value=new_shortcut)
            else:
                # Pas de raccourci du tout, créer un simple
                lxml_etree.SubElement(command_item, "string", name="Key", value=new_shortcut)
            # Le fichier est maintenant modifié, activer la sauvegarde
            self.action_save.setEnabled(True)
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'ajout du raccourci: {str(e)}")
            return False
    
    def remove_shortcut(self):
        """Supprime le raccourci sélectionné"""
        # Vérifier qu'une commande est sélectionnée
        current_row = self.command_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une commande d'abord")
            return
            
        command_name = self.command_table.item(current_row, 0).text()
        current_shortcut = self.command_table.item(current_row, 1).text()
        
        if not current_shortcut:
            QMessageBox.information(self, "Info", "Cette commande n'a pas de raccourci")
            return
            
        # Confirmer la suppression
        reply = QMessageBox.question(self, "Confirmation", 
                                    f"Voulez-vous vraiment supprimer le raccourci pour {command_name} ?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                    
        if reply == QMessageBox.Yes:
            # Supprimer le raccourci du XML
            if self.remove_shortcut_from_xml(command_name):
                # Recharger la liste des commandes pour mettre à jour l'affichage
                self.load_commands()
    
    def remove_shortcut_from_xml(self, command_name):
        """Supprime un raccourci du fichier XML"""
        try:
            # Chercher la commande dans la catégorie actuelle
            xpath_query = f".//item[string[@name='Name'][@value='{self.current_category}']]"
            category_items = self.xml_root.xpath(xpath_query)
            
            if not category_items:
                return False
                
            category_item = category_items[0]
            
            # Trouver la commande
            cmd_xpath = f"./list[@name='Commands']/item[string[@name='Name'][@value='{command_name}']]"
            command_items = category_item.xpath(cmd_xpath)
            
            if not command_items:
                return False
                
            command_item = command_items[0]
            
            # Supprimer tous les raccourcis
            key_elem = command_item.xpath("./string[@name='Key']")
            if key_elem:
                parent = key_elem[0].getparent()
                parent.remove(key_elem[0])
            
            key_list = command_item.xpath("./list[@name='Key']")
            if key_list:
                parent = key_list[0].getparent()
                parent.remove(key_list[0])
            
            # Le fichier est maintenant modifié, activer la sauvegarde
            self.action_save.setEnabled(True)
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la suppression du raccourci: {str(e)}")
            return False