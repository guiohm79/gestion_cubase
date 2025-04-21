import json
import os
import re

VSTI_LIST_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'vsti_list.json')
VSTI_LIST_PATH = os.path.abspath(VSTI_LIST_PATH)

def load_vsti_list():
    if not os.path.exists(VSTI_LIST_PATH):
        return []
    with open(VSTI_LIST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_vsti_list(vsti_list):
    with open(VSTI_LIST_PATH, 'w', encoding='utf-8') as f:
        json.dump(vsti_list, f, ensure_ascii=False, indent=2)

def add_vsti(name):
    vsti_list = load_vsti_list()
    if name not in vsti_list:
        vsti_list.append(name)
        save_vsti_list(vsti_list)

def remove_vsti(name):
    vsti_list = load_vsti_list()
    if name in vsti_list:
        vsti_list.remove(name)
        save_vsti_list(vsti_list)


def update_vsti(old_name, new_name):
    vsti_list = load_vsti_list()
    if old_name in vsti_list:
        idx = vsti_list.index(old_name)
        vsti_list[idx] = new_name
        save_vsti_list(vsti_list)


def get_vsti_editor(vsti_name):
    vsti_list = load_vsti_list()
    vsti_name_stripped = vsti_name.strip()
    if vsti_list and isinstance(vsti_list[0], dict) and 'editor' in vsti_list[0] and 'name' in vsti_list[0]:
        # 1. Correspondance exacte
        for vst in vsti_list:
            if vsti_name_stripped.lower() == vst['name'].lower():
                return vst.get('editor', 'Inconnu')
        
        # 2. Regex : nom + (fin OU espaces + chiffres + fin)
        for vst in vsti_list:
            vst_name = vst['name'].strip()
            pattern = r'^' + re.escape(vst_name) + r'(?:\s*\d*)$'
            if re.match(pattern, vsti_name_stripped, re.IGNORECASE):
                return vst.get('editor', 'Inconnu')
        
        # 3. Version sans espaces
        vsti_name_clean = vsti_name_stripped.lower().replace(' ', '')
        for vst in vsti_list:
            vst_name_clean = vst['name'].lower().replace(' ', '')
            pattern = r'^' + re.escape(vst_name_clean) + r'(?:\d*)$'
            if re.match(pattern, vsti_name_clean):
                return vst.get('editor', 'Inconnu')
            
        # 4. Vérifier si le VSTi est contenu dans le nom (pour les variantes avec suffixes)
        for vst in vsti_list:
            if vst['name'].lower() in vsti_name_stripped.lower():
                return vst.get('editor', 'Inconnu')
            
        return 'Inconnu'
    else:
        return 'Inconnu'

def get_vsti_by_editor(vsti_names):
    print("Appel de get_vsti_by_editor avec :", vsti_names)
    """
    Retourne une liste de VSTi utilisés triée/groupée par éditeur.
    Args:
        vsti_names (list): liste des noms de VST utilisés (issus de trouve_vsti par exemple)
    Returns:
        list de tuples (editor, [vsti1, vsti2, ...]) triée par nom d'éditeur
    """
    editor_to_vsti = {}
    for vst in vsti_names:
        editor = get_vsti_editor(vst)
        editor_to_vsti.setdefault(editor, []).append(vst)
    # Tri
    result = []
    for editor in sorted(editor_to_vsti):
        result.append((editor, sorted(editor_to_vsti[editor])))
    return result
