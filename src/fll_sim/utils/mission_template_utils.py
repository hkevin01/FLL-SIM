"""
Mission Template Utility Module

Provides helper functions for creating, loading, and validating mission templates in FLL-Sim.
"""
import json

from fll_sim.utils.errors import FLLSimError
from fll_sim.utils.logger import FLLLogger


class MissionTemplateUtils:
    """Utility functions for mission template management."""
    def __init__(self):
        self.logger = FLLLogger('MissionTemplateUtils')

    def create_template(self, name, description, objectives):
        try:
            template = {
                'name': name,
                'description': description,
                'objectives': objectives
            }
            self.logger.info(f"Mission template created: {name}")
            return template
        except Exception as e:
            self.logger.error(f"Create template error: {e}")
            raise FLLSimError(f"Create template error: {e}") from e

    def save_template(self, template, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            self.logger.info(f"Mission template saved to {path}")
        except Exception as e:
            self.logger.error(f"Save template error: {e}")
            raise FLLSimError(f"Save template error: {e}") from e

    def load_template(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            self.logger.info(f"Mission template loaded from {path}")
            return template
        except Exception as e:
            self.logger.error(f"Load template error: {e}")
            raise FLLSimError(f"Load template error: {e}") from e

class TemplateManager:
    """Manages mission and robot templates for FLL-Sim ecosystem."""
    def __init__(self):
        self.templates = {}
    def add_template(self, name: str, template: dict) -> None:
        self.templates[name] = template
    def get_template(self, name: str) -> dict:
        return self.templates.get(name, {})
    def list_templates(self) -> list:
        return list(self.templates.keys())
    def list_templates(self) -> list:
        return list(self.templates.keys())
