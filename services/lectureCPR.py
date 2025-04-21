import re
import os
from services.vsti_manager import load_vsti_list

def trouve_vsti(fichier, progress_callback=None):
    print(f"Analyse de : {os.path.basename(fichier)}")
    
    with open(fichier, "rb") as f:
        data = f.read()
    
    # Charger la liste des VSTi dynamiquement
    vsti_connus = load_vsti_list()
    
    trouvés = set()  # On utilise un set pour éviter les doublons
    
    total = len(vsti_connus) * 2  # Boucles numérotés + sans numéro
    progress = 0
    # Cherchons les VSTi numérotés (comme "Serum 01", "Kick 2 01", etc.)
    for idx, vsti in enumerate(vsti_connus):
        # Vérifier si on doit arrêter l'analyse
        if progress_callback and progress_callback(int(progress * 100 / total)) is False:
            print("Analyse interrompue par l'utilisateur")
            return trouvés
            
        if isinstance(vsti, dict):
            vsti_name = vsti.get("name", "")
        else:
            vsti_name = vsti
        if not vsti_name:
            continue
        pattern = re.compile(f"{vsti_name}\s+\d{{2}}".encode('utf-8'))
        matches = pattern.findall(data)
        for match in matches:
            trouvés.add(match.decode('utf-8', errors='ignore'))
        progress += 1
        
    # Cherchons aussi les instances sans numéro
    for idx, vsti in enumerate(vsti_connus):
        # Vérifier si on doit arrêter l'analyse
        if progress_callback and progress_callback(int(progress * 100 / total)) is False:
            print("Analyse interrompue par l'utilisateur")
            return trouvés
            
        if isinstance(vsti, dict):
            vsti_name = vsti.get("name", "")
        else:
            vsti_name = vsti
        if not vsti_name:
            continue
        # On évite les faux positifs en vérifiant que ce n'est pas au milieu d'un mot
        pattern = re.compile(rb'(?<!\w)' + vsti_name.encode('utf-8') + rb'(?!\w)')
        matches = pattern.findall(data)
        if matches:
            if not any(vsti_name in déjà_trouvé for déjà_trouvé in trouvés):
                trouvés.add(vsti_name)
        progress += 1
        
    # Cherchons aussi les entrées de type "Plugin Nam..."
    plugin_pattern = re.compile(rb'Plugin\s+Nam[^\n\r]{2,40}')
    plugin_matches = plugin_pattern.findall(data)
    
    for match in plugin_matches:
        # Vérifier si on doit arrêter l'analyse
        if progress_callback and progress_callback(100) is False:
            print("Analyse interrompue par l'utilisateur")
            return trouvés
            
        texte = match.decode('utf-8', errors='ignore')
        # On extrait le nom du plugin si on le trouve
        for vsti in vsti_connus:
            if isinstance(vsti, dict):
                vsti_name = vsti.get("name", "")
            else:
                vsti_name = vsti
            if vsti_name and vsti_name in texte and vsti_name not in trouvés and not any(vsti_name in déjà_trouvé for déjà_trouvé in trouvés):
                trouvés.add(vsti_name)
    
    print("\nListe des plugins :")
    for vsti in sorted(trouvés):
        print(f"→ {vsti}")
    
    return trouvés

if __name__ == "__main__":
    trouve_vsti("monprojet.cpr")