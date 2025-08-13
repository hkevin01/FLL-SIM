"""
Internationalization Module

Handles language selection, translation, and localization for FLL-Sim users.
"""
from fll_sim.utils.logger import FLLLogger


class InternationalizationManager:
    def __init__(self):
        self.logger = FLLLogger("InternationalizationManager")
        self.language = "en"
        self.translations = {"en": {}}

    def set_language(self, lang_code):
        self.language = lang_code
        self.logger.info(f"Language set to {lang_code}")

    def add_translation(self, lang_code, key, value):
        self.translations.setdefault(lang_code, {})[key] = value
        self.logger.info(f"Added translation for {key} in {lang_code}")

    def translate(self, key):
        return self.translations.get(self.language, {}).get(key, key)
