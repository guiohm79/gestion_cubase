#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constantes globales pour l'application
"""

# Modes d'application
MODE_TRI = "tri"
MODE_WORKSPACE = "workspace"

# Types de fichiers
FILE_TYPE_CPR = "cpr"
FILE_TYPE_BAK = "bak"
FILE_TYPE_WAV = "wav"
FILE_TYPE_OTHER = "other"

# Chemins par défaut
DEFAULT_PREFS_DIR = "~/.trie_morceaux"
DEFAULT_PREFS_FILE = "preferences.json"
DEFAULT_METADATA_FILE = "metadata.json"
DEFAULT_NOTES_FILE = "notes.txt"

# Configuration de l'interface
UI_WINDOW_TITLE = "Tri Morceaux Cubase"
UI_MIN_WIDTH = 1000
UI_MIN_HEIGHT = 700

# Colonnes du tableau des projets
PROJECT_COLUMNS = [
    "Nom du projet",
    "Date de modification",
    "Taille",
    "Fichiers CPR",
    "Fichiers BAK",
    "Fichiers WAV",
    "Source"
]

# Colonnes de l'arborescence des fichiers
# Ordre des colonnes dans QFileSystemModel : Nom, Taille, Type, Date de modification
FILE_TREE_COLUMNS = [
    "Nom",
    "Taille",
    "Type",
    "Date de modification"
]
