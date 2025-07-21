"""
Robot Template Utility Module

Provides helper functions for creating, loading, and validating robot templates in FLL-Sim.
"""
import json
from src.fll_sim.utils.logger import FLLLogger
from src.fll_sim.utils.errors import FLLSimError

class RobotTemplateUtils:
    """Utility functions for robot template management."""
    def __init__(self):
        self.logger = FLLLogger('RobotTemplateUtils')

    def create_template(self, name, description, config):
        try:
            template = {
                'name': name,
                'description': description,
                'config': config
            }
            self.logger.info(f"Robot template created: {name}")
            return template
        except Exception as e:
            self.logger.error(f"Create template error: {e}")
            raise FLLSimError(f"Create template error: {e}") from e

    def save_template(self, template, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            self.logger.info(f"Robot template saved to {path}")
        except Exception as e:
            self.logger.error(f"Save template error: {e}")
            raise FLLSimError(f"Save template error: {e}") from e

    def load_template(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            self.logger.info(f"Robot template loaded from {path}")
            return template
        except Exception as e:
            self.logger.error(f"Load template error: {e}")
            raise FLLSimError(f"Load template error: {e}") from e
