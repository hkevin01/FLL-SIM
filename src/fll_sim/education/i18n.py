"""
Internationalization (i18n) Module

Provides multi-language support for FLL-Sim GUI and documentation.
Designed for extensibility and educator localization tools.
"""

from typing import Dict, List
import json

class I18nManager:
    """Manages translations and language settings."""
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language: str = 'en'

    def add_translation(self, key: str, text: str, lang: str) -> None:
        if key not in self.translations:
            self.translations[key] = {}
        self.translations[key][lang] = text

    def set_language(self, lang: str) -> None:
        self.current_language = lang

    def translate(self, key: str) -> str:
        return self.translations.get(key, {}).get(self.current_language, key)

    def load_translations_from_file(self, file_path: str, lang: str) -> None:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for key, text in data.items():
            self.add_translation(key, text, lang)

    def available_languages(self) -> List[str]:
        langs = set()
        for key in self.translations:
            langs.update(self.translations[key].keys())
        return list(langs)

    def get_translation_dict(self, lang: str) -> Dict[str, str]:
        return {key: self.translations[key][lang] for key in self.translations if lang in self.translations[key]}
