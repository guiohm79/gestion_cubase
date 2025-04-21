from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                            QTreeWidget, QTreeWidgetItem, QTableWidget, 
                            QTableWidgetItem, QPushButton, QSplitter, 
                            QHeaderView, QMessageBox, QFileDialog,
                            QToolBar, QAction, QDialog, QLineEdit, QFormLayout, QKeySequenceEdit,
                            QListWidget, QListWidgetItem, QMenu, QComboBox, QApplication, QWidget,
                            QInputDialog)
from PyQt5.QtCore import Qt, QSize, QMimeData
from PyQt5.QtGui import QKeySequence, QDrag
import os
import sys
import glob
import platform
from pathlib import Path

from lxml import etree as lxml_etree

from gui.base.base_window import BaseWindow


def get_cubase_key_commands_paths():
    """Détecte les chemins possibles pour les fichiers de raccourcis Cubase sur différents systèmes"""
    paths = []
    system = platform.system()
    
    if system == "Windows":
        # Chemin sur Windows
        user_home = os.path.expanduser("~")
        base_path = os.path.join(user_home, "AppData", "Roaming", "Steinberg")
        
        # Rechercher tous les dossiers Cubase
        cubase_dirs = glob.glob(os.path.join(base_path, "Cubase *_64"))
        
        for cubase_dir in cubase_dirs:
            key_commands_path = os.path.join(cubase_dir, "Presets", "KeyCommands")
            if os.path.exists(key_commands_path):
                paths.append(key_commands_path)
    
    elif system == "Darwin":  # macOS
        # Chemin sur Mac
        user_home = os.path.expanduser("~")
        library_path = os.path.join(user_home, "Library", "Preferences")
        
        # Rechercher tous les dossiers Cubase
        cubase_dirs = glob.glob(os.path.join(library_path, "Cubase *"))
        
        for cubase_dir in cubase_dirs:
            key_commands_path = os.path.join(cubase_dir, "Presets", "KeyCommands")
            if os.path.exists(key_commands_path):
                paths.append(key_commands_path)
    
    # Ajouter un dossier par défaut si aucun n'a été trouvé
    if not paths:
        # Utiliser le dossier Documents comme fallback
        user_docs = os.path.join(os.path.expanduser("~"), "Documents")
        paths.append(user_docs)
    
    return paths

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
        
        # Action pour importer depuis Cubase
        self.action_import_cubase = QAction("Importer depuis Cubase", self)
        self.action_import_cubase.triggered.connect(self.import_from_cubase)
        toolbar.addAction(self.action_import_cubase)
        
        # Action pour sauvegarder
        self.action_save = QAction("Enregistrer", self)
        self.action_save.triggered.connect(self.save_file)
        self.action_save.setEnabled(False)
        toolbar.addAction(self.action_save)
        
        # Action pour exporter vers Cubase
        self.action_export_cubase = QAction("Exporter vers Cubase", self)
        self.action_export_cubase.triggered.connect(self.export_to_cubase)
        self.action_export_cubase.setEnabled(False)
        toolbar.addAction(self.action_export_cubase)
        
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
        # Double-clic pour éditer un raccourci ou une macro
        self.command_table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Menu contextuel pour les commandes
        self.command_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.command_table.customContextMenuRequested.connect(self.show_command_context_menu)
        
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
            
        self.load_xml_file(file_path)
    
    def load_xml_file(self, file_path):
        """Charge un fichier XML de raccourcis Cubase"""
        try:
            # Utiliser lxml qui est plus tolérant aux erreurs
            parser = lxml_etree.XMLParser(recover=True)
            self.xml_tree = lxml_etree.parse(file_path, parser)
            self.xml_root = self.xml_tree.getroot()
            self.current_file = file_path
            
            self.load_categories()
            
            # Activer les boutons
            self.action_save.setEnabled(True)
            self.action_export_cubase.setEnabled(True)
            
            # Mettre à jour le titre
            self.title_label.setText(f"Éditeur de raccourcis - {os.path.basename(file_path)}")
            
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")
            return False
            
    def import_from_cubase(self):
        """Importe un fichier de raccourcis depuis les dossiers de Cubase"""
        # Récupérer les chemins possibles
        cubase_paths = get_cubase_key_commands_paths()
        
        if not cubase_paths:
            QMessageBox.warning(self, "Erreur", "Aucun dossier de raccourcis Cubase n'a été trouvé sur votre système.")
            return
        
        # Si un seul chemin est disponible, l'utiliser directement
        if len(cubase_paths) == 1:
            path = cubase_paths[0]
            # Lister les fichiers XML dans ce dossier
            xml_files = [f for f in os.listdir(path) if f.endswith(".xml")]
            
            if not xml_files:
                QMessageBox.warning(self, "Erreur", f"Aucun fichier XML trouvé dans {path}")
                return
                
            # Si un seul fichier XML, l'utiliser directement
            if len(xml_files) == 1:
                file_path = os.path.join(path, xml_files[0])
                self.load_xml_file(file_path)
                return
                
            # Sinon, demander à l'utilisateur de choisir
            file_name, ok = QInputDialog.getItem(
                self, "Choisir un fichier", "Sélectionnez un fichier de raccourcis:",
                xml_files, 0, False)
                
            if ok and file_name:
                file_path = os.path.join(path, file_name)
                self.load_xml_file(file_path)
        else:
            # Plusieurs chemins disponibles, demander à l'utilisateur de choisir
            path, ok = QInputDialog.getItem(
                self, "Choisir un dossier", "Sélectionnez un dossier de raccourcis Cubase:",
                cubase_paths, 0, False)
                
            if ok and path:
                # Lister les fichiers XML dans ce dossier
                xml_files = [f for f in os.listdir(path) if f.endswith(".xml")]
                
                if not xml_files:
                    QMessageBox.warning(self, "Erreur", f"Aucun fichier XML trouvé dans {path}")
                    return
                    
                # Si un seul fichier XML, l'utiliser directement
                if len(xml_files) == 1:
                    file_path = os.path.join(path, xml_files[0])
                    self.load_xml_file(file_path)
                    return
                    
                # Sinon, demander à l'utilisateur de choisir
                file_name, ok = QInputDialog.getItem(
                    self, "Choisir un fichier", "Sélectionnez un fichier de raccourcis:",
                    xml_files, 0, False)
                    
                if ok and file_name:
                    file_path = os.path.join(path, file_name)
                    self.load_xml_file(file_path)
    
    def export_to_cubase(self):
        """Exporte le fichier de raccourcis vers les dossiers de Cubase"""
        if not self.current_file or not self.xml_tree:
            QMessageBox.warning(self, "Erreur", "Aucun fichier n'est actuellement ouvert.")
            return
            
        # Récupérer les chemins possibles
        cubase_paths = get_cubase_key_commands_paths()
        
        if not cubase_paths:
            QMessageBox.warning(self, "Erreur", "Aucun dossier de raccourcis Cubase n'a été trouvé sur votre système.")
            return
        
        # Si un seul chemin est disponible, l'utiliser directement
        if len(cubase_paths) == 1:
            target_dir = cubase_paths[0]
        else:
            # Plusieurs chemins disponibles, demander à l'utilisateur de choisir
            target_dir, ok = QInputDialog.getItem(
                self, "Choisir un dossier", "Sélectionnez un dossier de destination:",
                cubase_paths, 0, False)
                
            if not ok or not target_dir:
                return
        
        # Demander le nom du fichier
        current_name = os.path.basename(self.current_file)
        file_name, ok = QInputDialog.getText(
            self, "Nom du fichier", "Entrez un nom pour le fichier:",
            text=current_name)
            
        if not ok or not file_name:
            return
            
        # Assurer que le fichier a l'extension .xml
        if not file_name.lower().endswith(".xml"):
            file_name += ".xml"
            
        # Chemin complet du fichier de destination
        target_path = os.path.join(target_dir, file_name)
        
        # Confirmer si le fichier existe déjà
        if os.path.exists(target_path):
            reply = QMessageBox.question(
                self, "Confirmer le remplacement",
                f"Le fichier {file_name} existe déjà. Voulez-vous le remplacer ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
            if reply != QMessageBox.Yes:
                return
        
        try:
            # Créer le dossier de destination s'il n'existe pas
            os.makedirs(target_dir, exist_ok=True)
            
            # Sauvegarde BRUTALE avec mode direct
            with open(target_path, 'wb') as f:
                # L'en-tête XML manuellement pour être sûr
                f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
                # Sortie directe en UTF-8
                f.write(lxml_etree.tostring(self.xml_root, pretty_print=True, xml_declaration=False, encoding='utf-8'))
            
            QMessageBox.information(
                self, "Succès",
                f"Fichier exporté avec succès vers {target_path}")
                
        except Exception as e:
            QMessageBox.warning(
                self, "Erreur",
                f"Impossible d'exporter le fichier: {str(e)}")
    
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
    
    def on_item_double_clicked(self, item):
        """Événement déclenché lors d'un double-clic sur un élément de la table"""
        row = item.row()
        command_name = self.command_table.item(row, 0).text()
        
        # Si on double-clique sur la colonne des commandes (0) et qu'on est dans la catégorie Macro
        if item.column() == 0 and self.current_category == "Macro":
            # C'est une macro, ouvrir l'éditeur de macro
            self.edit_macro(command_name)
        # Si on double-clique sur la colonne des raccourcis (1)
        elif item.column() == 1:
            # Éditer le raccourci
            self.edit_shortcut(command_name, item.text())
    
    def show_command_context_menu(self, position):
        """Événement déclenché lors d'un clic droit sur la table des commandes"""
        # Récupérer l'item sélectionné
        current_row = self.command_table.currentRow()
        
        # Créer le menu contextuel
        menu = QMenu()
        
        # Actions différentes selon la catégorie
        if self.current_category == "Macro":
            # Options spécifiques aux macros
            create_macro_action = menu.addAction("Créer une nouvelle macro")
            
            # Options disponibles seulement si une macro est sélectionnée
            if current_row >= 0:
                command_name = self.command_table.item(current_row, 0).text()
                current_shortcut = self.command_table.item(current_row, 1).text()
                
                edit_macro_action = menu.addAction("Modifier la macro")
                edit_shortcut_action = menu.addAction("Modifier le raccourci")
                delete_macro_action = menu.addAction("Supprimer la macro")
                
                # Exécuter le menu et récupérer l'action sélectionnée
                action = menu.exec_(self.command_table.mapToGlobal(position))
                
                if action == create_macro_action:
                    self.create_new_macro()
                elif action == edit_macro_action:
                    self.edit_macro(command_name)
                elif action == edit_shortcut_action:
                    self.edit_shortcut(command_name, current_shortcut)
                elif action == delete_macro_action:
                    self.delete_macro(command_name)
            else:
                # Seulement l'option de création si aucune macro n'est sélectionnée
                action = menu.exec_(self.command_table.mapToGlobal(position))
                
                if action == create_macro_action:
                    self.create_new_macro()
        else:
            # Pour les autres catégories, juste l'option d'éditer le raccourci
            if current_row >= 0:
                command_name = self.command_table.item(current_row, 0).text()
                current_shortcut = self.command_table.item(current_row, 1).text()
                
                edit_shortcut_action = menu.addAction("Modifier le raccourci")
                
                # Exécuter le menu et récupérer l'action sélectionnée
                action = menu.exec_(self.command_table.mapToGlobal(position))
                
                if action == edit_shortcut_action:
                    self.edit_shortcut(command_name, current_shortcut)
    
    def edit_shortcut(self, command_name, current_shortcut):
        """Édite un raccourci existant"""
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
                # Mettre à jour l'affichage dans la table
                current_row = self.command_table.currentRow()
                if current_row >= 0:
                    self.command_table.item(current_row, 1).setText(new_shortcut)
                
                # Mettre à jour le XML
                self.update_shortcut_in_xml(command_name, current_shortcut, new_shortcut)
                
    def create_new_macro(self):
        """Événement déclenché pour créer une nouvelle macro"""
        try:
            # Demander le nom de la nouvelle macro
            macro_name, ok = QInputDialog.getText(
                self, "Nouvelle macro", "Nom de la nouvelle macro:")
                
            if not ok or not macro_name:
                return
                
            # Vérifier si une macro avec ce nom existe déjà
            if self.macro_exists(macro_name):
                QMessageBox.warning(self, "Erreur", f"Une macro nommée '{macro_name}' existe déjà")
                return
                
            # Créer une nouvelle macro vide
            commands = []
            
            # Ouvrir l'éditeur de macro
            dialog = MacroEditorDialog(self, macro_name, commands, self.xml_root)
            
            if dialog.exec_() == QDialog.Accepted:
                # Récupérer les commandes de la macro
                new_commands = dialog.get_macro_commands()
                
                # Ajouter la macro dans le XML
                self.add_macro_to_xml(macro_name, new_commands)
                
                # Recharger la liste des commandes pour mettre à jour l'affichage
                self.load_commands()
                
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la création de la macro: {str(e)}")
    
    def delete_macro(self, macro_name):
        """Événement déclenché pour supprimer une macro"""
        try:
            # Confirmer la suppression
            reply = QMessageBox.question(
                self, "Confirmer la suppression",
                f"Voulez-vous vraiment supprimer la macro '{macro_name}' ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
            if reply != QMessageBox.Yes:
                return
                
            # Supprimer la macro du XML
            self.remove_macro_from_xml(macro_name)
            
            # Recharger la liste des commandes pour mettre à jour l'affichage
            self.load_commands()
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la suppression de la macro: {str(e)}")
    
    def macro_exists(self, macro_name):
        """Événement déclenché pour vérifier si une macro existe"""
        try:
            # Chercher la macro dans le XML
            xpath_query = f".//item[string[@name='Name'][@value='Macro']]"
            macro_category = self.xml_root.xpath(xpath_query)
            
            if not macro_category:
                return False
            
            # Trouver la macro spécifique
            macro_xpath = f"./list[@name='Commands']/item[string[@name='Name'][@value='{macro_name}']]"
            macro_items = macro_category[0].xpath(macro_xpath)
            
            return len(macro_items) > 0
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la vérification de la macro: {str(e)}")
            return False
    
    def edit_macro(self, macro_name):
        """Édite une macro existante"""
        try:
            # Chercher la macro dans le XML
            xpath_query = f".//item[string[@name='Name'][@value='Macro']]"
            macro_category = self.xml_root.xpath(xpath_query)
            
            if not macro_category:
                QMessageBox.warning(self, "Erreur", "Catégorie Macro introuvable dans le XML")
                return
            
            # Trouver la macro spécifique
            macro_xpath = f"./list[@name='Commands']/item[string[@name='Name'][@value='{macro_name}']]"
            macro_items = macro_category[0].xpath(macro_xpath)
            
            if not macro_items:
                QMessageBox.warning(self, "Erreur", f"Macro '{macro_name}' introuvable")
                return
            
            macro_item = macro_items[0]
            
            # Chercher la définition complète de la macro
            macro_def_xpath = f".//item[string[@name='Name'][@value='{macro_name}']][list[@name='Commands']]"
            macro_def_items = self.xml_root.xpath(macro_def_xpath)
            
            if not macro_def_items:
                # Créer une nouvelle définition de macro si elle n'existe pas
                commands = []
            else:
                macro_def = macro_def_items[0]
                
                # Extraire les commandes de la macro
                commands = []
                for cmd_item in macro_def.xpath("./list[@name='Commands']/item"):
                    category_elem = cmd_item.xpath("./string[@name='Category']")
                    name_elem = cmd_item.xpath("./string[@name='Name']")
                    
                    if category_elem and name_elem:
                        category = category_elem[0].get("value")
                        name = name_elem[0].get("value")
                        commands.append({"category": category, "name": name})
            
            # Ouvrir l'éditeur de macro
            dialog = MacroEditorDialog(self, macro_name, commands, self.xml_root)
            
            if dialog.exec_() == QDialog.Accepted:
                # Récupérer les commandes modifiées
                new_commands = dialog.get_macro_commands()
                
                # Mettre à jour la macro dans le XML
                self.update_macro_in_xml(macro_name, new_commands)
                
                # Recharger la liste des commandes pour mettre à jour l'affichage
                self.load_commands()
                
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'édition de la macro: {str(e)}")

    def add_macro_to_xml(self, macro_name, commands):
        """Ajoute une nouvelle macro dans le fichier XML"""
        try:
            # 1. Ajouter la macro à la liste des macros
            # Chercher la catégorie Macro
            xpath_query = f".//item[string[@name='Name'][@value='Macro']]"
            macro_category = self.xml_root.xpath(xpath_query)
            
            if not macro_category:
                # Si la catégorie Macro n'existe pas, la créer
                preset_elem = self.xml_root.xpath("./member[@name='Preset']")[0]
                categories_elem = preset_elem.xpath("./list[@name='Categories']")[0]
                
                # Créer l'élément catégorie Macro
                macro_category_elem = lxml_etree.SubElement(categories_elem, "item")
                lxml_etree.SubElement(macro_category_elem, "string", name="Name", value="Macro")
                
                # Créer la liste des commandes
                commands_list = lxml_etree.SubElement(macro_category_elem, "list", name="Commands", type="list")
                
                # Ajouter la nouvelle macro à la liste
                macro_item = lxml_etree.SubElement(commands_list, "item")
                lxml_etree.SubElement(macro_item, "string", name="Name", value=macro_name)
            else:
                # Ajouter la macro à la catégorie existante
                macro_category_elem = macro_category[0]
                commands_list = macro_category_elem.xpath("./list[@name='Commands']")[0]
                
                # Ajouter la nouvelle macro à la liste
                macro_item = lxml_etree.SubElement(commands_list, "item")
                lxml_etree.SubElement(macro_item, "string", name="Name", value=macro_name)
            
            # 2. Créer la définition de la macro
            preset_elem = self.xml_root.xpath("./member[@name='Preset']")[0]
            
            # Créer l'élément item pour la macro
            macro_elem = lxml_etree.SubElement(preset_elem, "item")
            lxml_etree.SubElement(macro_elem, "string", name="Name", value=macro_name)
            
            # Créer la liste des commandes
            commands_list = lxml_etree.SubElement(macro_elem, "list", name="Commands", type="list")
            
            # Ajouter chaque commande
            for cmd in commands:
                cmd_item = lxml_etree.SubElement(commands_list, "item")
                lxml_etree.SubElement(cmd_item, "string", name="Category", value=cmd["category"])
                lxml_etree.SubElement(cmd_item, "string", name="Name", value=cmd["name"])
            
            # Le fichier est maintenant modifié, activer la sauvegarde
            self.action_save.setEnabled(True)
            
            QMessageBox.information(self, "Succès", f"Macro '{macro_name}' créée avec succès")
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la création de la macro: {str(e)}")
            return False
    
    def remove_macro_from_xml(self, macro_name):
        """Supprime une macro du fichier XML"""
        try:
            # 1. Supprimer la macro de la liste des macros
            xpath_query = f".//item[string[@name='Name'][@value='Macro']]"
            macro_category = self.xml_root.xpath(xpath_query)
            
            if not macro_category:
                return False
            
            # Trouver la macro spécifique dans la liste
            macro_xpath = f"./list[@name='Commands']/item[string[@name='Name'][@value='{macro_name}']]"
            macro_items = macro_category[0].xpath(macro_xpath)
            
            if not macro_items:
                return False
            
            # Supprimer la macro de la liste
            macro_item = macro_items[0]
            parent = macro_item.getparent()
            parent.remove(macro_item)
            
            # 2. Supprimer la définition de la macro
            macro_def_xpath = f".//item[string[@name='Name'][@value='{macro_name}']][list[@name='Commands']]"
            macro_def_items = self.xml_root.xpath(macro_def_xpath)
            
            if macro_def_items:
                # Supprimer la définition
                macro_def = macro_def_items[0]
                parent = macro_def.getparent()
                parent.remove(macro_def)
            
            # Le fichier est maintenant modifié, activer la sauvegarde
            self.action_save.setEnabled(True)
            
            QMessageBox.information(self, "Succès", f"Macro '{macro_name}' supprimée avec succès")
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la suppression de la macro: {str(e)}")
            return False
    
    def update_macro_in_xml(self, macro_name, commands):
        """Met à jour une macro dans le fichier XML"""
        try:
            # Chercher la définition de la macro
            macro_def_xpath = f".//item[string[@name='Name'][@value='{macro_name}']][list[@name='Commands']]"
            macro_def_items = self.xml_root.xpath(macro_def_xpath)
            
            if macro_def_items:
                # Supprimer l'ancienne définition
                macro_def = macro_def_items[0]
                parent = macro_def.getparent()
                parent.remove(macro_def)
            
            # Créer une nouvelle définition de macro
            preset_elem = self.xml_root.xpath("./member[@name='Preset']")[0]
            
            # Créer l'élément item pour la macro
            macro_elem = lxml_etree.SubElement(preset_elem, "item")
            lxml_etree.SubElement(macro_elem, "string", name="Name", value=macro_name)
            
            # Créer la liste des commandes
            commands_list = lxml_etree.SubElement(macro_elem, "list", name="Commands", type="list")
            
            # Ajouter chaque commande
            for cmd in commands:
                cmd_item = lxml_etree.SubElement(commands_list, "item")
                lxml_etree.SubElement(cmd_item, "string", name="Category", value=cmd["category"])
                lxml_etree.SubElement(cmd_item, "string", name="Name", value=cmd["name"])
            
            # Le fichier est maintenant modifié, activer la sauvegarde
            self.action_save.setEnabled(True)
            
            QMessageBox.information(self, "Succès", f"Macro '{macro_name}' mise à jour avec succès")
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la mise à jour de la macro: {str(e)}")
            return False

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
            # Vérifier d'abord si le nouveau raccourci existe déjà dans tout le fichier XML
            shortcut_exists, category, cmd = self.is_shortcut_already_used(new_shortcut, exclude_command=command_name)
            if shortcut_exists:
                QMessageBox.warning(self, "Doublon", f"Ce raccourci est déjà utilisé par la commande '{cmd}' dans la catégorie '{category}'")
                return
                
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
    
    def is_shortcut_already_used(self, new_shortcut, exclude_command=None):
        """Vérifie si un raccourci est déjà utilisé dans tout le fichier XML
        
        Args:
            new_shortcut (str): Le raccourci à vérifier
            exclude_command (str, optional): Nom de la commande à exclure de la vérification
            
        Returns:
            tuple: (bool, str, str) - (Existe déjà, Catégorie, Commande)
        """
        if self.xml_root is None or not new_shortcut:
            return False, "", ""
            
        # Parcourir toutes les catégories
        for category_item in self.xml_root.xpath(".//item[string[@name='Name']]"):
            category_name = category_item.xpath("./string[@name='Name']/@value")
            if not category_name:
                continue
                
            category_name = category_name[0]
            
            # Parcourir toutes les commandes de cette catégorie
            for command_item in category_item.xpath("./list[@name='Commands']/item"):
                command_name = command_item.xpath("./string[@name='Name']/@value")
                if not command_name:
                    continue
                    
                command_name = command_name[0]
                
                # Si on a spécifié une commande à exclure, on la saute
                if exclude_command and command_name == exclude_command and category_name == self.current_category:
                    continue
                
                # Vérifier raccourci simple
                key_elem = command_item.xpath("./string[@name='Key']")
                if len(key_elem) > 0 and key_elem[0].get("value") == new_shortcut:
                    return True, category_name, command_name
                
                # Vérifier liste de raccourcis
                key_list = command_item.xpath("./list[@name='Key']/item")
                for key_item in key_list:
                    if key_item.get("value") == new_shortcut:
                        return True, category_name, command_name
        
        return False, "", ""

    def add_shortcut_to_xml(self, command_name, new_shortcut):
        """Ajoute un raccourci dans le fichier XML"""
        try:
            # Vérifier d'abord si le raccourci existe déjà dans tout le fichier XML
            shortcut_exists, category, cmd = self.is_shortcut_already_used(new_shortcut, exclude_command=command_name)
            if shortcut_exists:
                QMessageBox.warning(self, "Doublon", f"Ce raccourci est déjà utilisé par la commande '{cmd}' dans la catégorie '{category}'")
                return False

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
            
            # Vérifier si le raccourci existe déjà pour cette commande (simple ou liste)
            key_elem = command_item.xpath("./string[@name='Key']")
            key_list = command_item.xpath("./list[@name='Key']")
            
            # Ajout du raccourci
            if key_elem:
                # Il y a déjà un raccourci simple, le convertir en liste
                old_shortcut = key_elem[0].get("value")
                parent = key_elem[0].getparent()
                parent.remove(key_elem[0])
                key_list_elem = lxml_etree.SubElement(command_item, "list", name="Key", type="string")
                # Ajouter l'ancien raccourci comme premier item
                lxml_etree.SubElement(key_list_elem, "item", value=old_shortcut)
                # Ajouter le nouveau raccourci
                lxml_etree.SubElement(key_list_elem, "item", value=new_shortcut)
            elif key_list:
                # Ajouter à la liste existante
                lxml_etree.SubElement(key_list[0], "item", value=new_shortcut)
            else:
                # Aucun raccourci existant, créer un raccourci simple
                lxml_etree.SubElement(command_item, "string", name="Key", value=new_shortcut, wide="true")
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

class MacroEditorDialog(QDialog):
    """Dialogue d'édition des macros avec drag and drop"""
    def __init__(self, parent=None, macro_name="", commands=None, xml_root=None):
        super().__init__(parent)
        self.macro_name = macro_name
        self.commands = commands or []
        self.xml_root = xml_root
        self.available_commands = {}
        self.setup_ui()
        self.load_available_commands()
        self.load_macro_commands()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle(f"Éditeur de macro: {self.macro_name}")
        self.resize(800, 600)
        
        main_layout = QVBoxLayout(self)
        
        # Titre et description
        title_label = QLabel(f"Édition de la macro: {self.macro_name}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        description_label = QLabel("Glissez-déposez les commandes entre les listes pour modifier la macro.")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)
        
        # Splitter horizontal pour diviser l'écran
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau de gauche: commandes disponibles
        left_panel = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        
        category_label = QLabel("Catégories:")
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.filter_available_commands)
        
        available_label = QLabel("Commandes disponibles:")
        self.available_list = QListWidget()
        self.available_list.setDragEnabled(True)
        
        left_panel.addWidget(category_label)
        left_panel.addWidget(self.category_combo)
        left_panel.addWidget(available_label)
        left_panel.addWidget(self.available_list)
        
        # Panneau de droite: commandes de la macro
        right_panel = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        macro_label = QLabel("Commandes de la macro:")
        self.macro_list = QListWidget()
        self.macro_list.setDragEnabled(True)
        self.macro_list.setAcceptDrops(True)
        self.macro_list.setDropIndicatorShown(True)
        self.macro_list.setDefaultDropAction(Qt.MoveAction)
        
        # Boutons pour gérer les commandes de la macro
        buttons_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Supprimer")
        self.remove_btn.clicked.connect(self.remove_selected_command)
        self.move_up_btn = QPushButton("Monter")
        self.move_up_btn.clicked.connect(self.move_command_up)
        self.move_down_btn = QPushButton("Descendre")
        self.move_down_btn.clicked.connect(self.move_command_down)
        
        buttons_layout.addWidget(self.remove_btn)
        buttons_layout.addWidget(self.move_up_btn)
        buttons_layout.addWidget(self.move_down_btn)
        
        right_panel.addWidget(macro_label)
        right_panel.addWidget(self.macro_list)
        right_panel.addLayout(buttons_layout)
        
        # Ajouter les widgets au splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter, 1)
        
        # Boutons OK/Annuler
        dialog_buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        
        dialog_buttons.addStretch()
        dialog_buttons.addWidget(self.ok_button)
        dialog_buttons.addWidget(self.cancel_button)
        
        main_layout.addLayout(dialog_buttons)
        
        # Configurer le drag & drop
        self.available_list.setDragDropMode(QListWidget.DragOnly)
        self.macro_list.setDragDropMode(QListWidget.DragDrop)
        
        # Menu contextuel pour la liste des commandes de la macro
        self.macro_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.macro_list.customContextMenuRequested.connect(self.show_macro_context_menu)
    
    def load_available_commands(self):
        """Charge toutes les commandes disponibles depuis le XML"""
        if self.xml_root is None:
            return
            
        try:
            # Trouver toutes les catégories
            categories = set()
            
            # Parcourir toutes les catégories
            for category_item in self.xml_root.xpath(".//item[string[@name='Name']]"):
                category_name = category_item.xpath("./string[@name='Name']/@value")
                if not category_name:
                    continue
                    
                category_name = category_name[0]
                
                # Ignorer la catégorie Macro
                if category_name == "Macro":
                    continue
                    
                categories.add(category_name)
                
                # Parcourir toutes les commandes de cette catégorie
                commands = []
                for command_item in category_item.xpath("./list[@name='Commands']/item"):
                    command_name = command_item.xpath("./string[@name='Name']/@value")
                    if not command_name:
                        continue
                        
                    command_name = command_name[0]
                    commands.append(command_name)
                
                # Stocker les commandes par catégorie
                self.available_commands[category_name] = commands
            
            # Remplir le combobox des catégories
            self.category_combo.addItem("Toutes les catégories")
            for category in sorted(categories):
                self.category_combo.addItem(category)
                
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des commandes disponibles: {str(e)}")
    
    def filter_available_commands(self, category):
        """Filtre les commandes disponibles par catégorie"""
        self.available_list.clear()
        
        if category == "Toutes les catégories":
            # Afficher toutes les commandes
            for cat, commands in sorted(self.available_commands.items()):
                for cmd in sorted(commands):
                    item = QListWidgetItem(f"{cat}: {cmd}")
                    item.setData(Qt.UserRole, {"category": cat, "name": cmd})
                    self.available_list.addItem(item)
        else:
            # Afficher seulement les commandes de la catégorie sélectionnée
            if category in self.available_commands:
                for cmd in sorted(self.available_commands[category]):
                    item = QListWidgetItem(f"{category}: {cmd}")
                    item.setData(Qt.UserRole, {"category": category, "name": cmd})
                    self.available_list.addItem(item)
    
    def load_macro_commands(self):
        """Charge les commandes de la macro"""
        self.macro_list.clear()
        
        for cmd in self.commands:
            category = cmd.get("category", "")
            command = cmd.get("name", "")
            item = QListWidgetItem(f"{category}: {command}")
            item.setData(Qt.UserRole, {"category": category, "name": command})
            self.macro_list.addItem(item)
    
    def remove_selected_command(self):
        """Supprime la commande sélectionnée de la macro"""
        current_row = self.macro_list.currentRow()
        if current_row >= 0:
            self.macro_list.takeItem(current_row)
    
    def move_command_up(self):
        """Déplace la commande sélectionnée vers le haut"""
        current_row = self.macro_list.currentRow()
        if current_row > 0:
            item = self.macro_list.takeItem(current_row)
            self.macro_list.insertItem(current_row - 1, item)
            self.macro_list.setCurrentRow(current_row - 1)
    
    def move_command_down(self):
        """Déplace la commande sélectionnée vers le bas"""
        current_row = self.macro_list.currentRow()
        if current_row < self.macro_list.count() - 1:
            item = self.macro_list.takeItem(current_row)
            self.macro_list.insertItem(current_row + 1, item)
            self.macro_list.setCurrentRow(current_row + 1)
    
    def show_macro_context_menu(self, position):
        """Affiche un menu contextuel pour la liste des commandes de la macro"""
        menu = QMenu()
        
        remove_action = menu.addAction("Supprimer")
        move_up_action = menu.addAction("Monter")
        move_down_action = menu.addAction("Descendre")
        
        # Désactiver les actions si aucun élément n'est sélectionné
        current_row = self.macro_list.currentRow()
        if current_row < 0:
            remove_action.setEnabled(False)
            move_up_action.setEnabled(False)
            move_down_action.setEnabled(False)
        else:
            move_up_action.setEnabled(current_row > 0)
            move_down_action.setEnabled(current_row < self.macro_list.count() - 1)
        
        action = menu.exec_(self.macro_list.mapToGlobal(position))
        
        if action == remove_action:
            self.remove_selected_command()
        elif action == move_up_action:
            self.move_command_up()
        elif action == move_down_action:
            self.move_command_down()
    
    def get_macro_commands(self):
        """Récupère les commandes de la macro"""
        commands = []
        for i in range(self.macro_list.count()):
            item = self.macro_list.item(i)
            data = item.data(Qt.UserRole)
            if isinstance(data, dict) and "category" in data and "command" in data:
                # Assurer la compatibilité avec la structure attendue
                commands.append({"category": data["category"], "name": data["command"]})
            elif isinstance(data, dict) and "category" in data and "name" in data:
                # Déjà dans le bon format
                commands.append(data)
        return commands