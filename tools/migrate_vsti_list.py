import json
import os

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'vsti_list.json'))
DST = SRC  # On écrase le fichier original après sauvegarde
BACKUP = SRC + '.bak'

def migrate():
    with open(SRC, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Si déjà au bon format, ne rien faire
    if data and isinstance(data[0], dict) and 'name' in data[0]:
        print('Déjà au format enrichi, rien à faire.')
        return
    # Créer la sauvegarde
    with open(BACKUP, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Migration
    enriched = [{"name": name} for name in data]
    with open(DST, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    print(f'Migration terminée. Ancien fichier sauvegardé sous {BACKUP}')

if __name__ == '__main__':
    migrate()
