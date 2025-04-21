import os
import json
from pathlib import Path

TAGS_FILE = Path(__file__).parent.parent / 'config' / 'tags.json'

class TagManager:
    """Gestionnaire global des tags persistants (tags.json)"""
    def __init__(self, tags_file=TAGS_FILE):
        self.tags_file = Path(tags_file)
        self.tags = self._load_tags()

    def _load_tags(self):
        if self.tags_file.exists():
            try:
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        else:
            return {}

    def _save_tags(self):
        self.tags_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump(self.tags, f, ensure_ascii=False, indent=2)

    def add_or_increment_tag(self, tag):
        tag = tag.strip()
        if not tag:
            return
        if tag in self.tags:
            self.tags[tag] += 1
        else:
            self.tags[tag] = 1
        self._save_tags()

    def get_top_tags(self, n=5):
        # Retourne les n tags les plus utilisés (par ordre décroissant)
        return [tag for tag, _ in sorted(self.tags.items(), key=lambda item: item[1], reverse=True)[:n]]

    def get_all_tags(self):
        # Retourne tous les tags connus (ordre alpha)
        return sorted(self.tags.keys())

    def remove_tag(self, tag):
        if tag in self.tags:
            del self.tags[tag]
            self._save_tags()

    def reset(self):
        self.tags = {}
        self._save_tags()
