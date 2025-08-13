"""
Mission Utility Module

Provides helper functions for mission creation, validation, and management in FLL-Sim.
"""
from fll_sim.utils.errors import FLLSimError
from fll_sim.utils.logger import FLLLogger


class MissionUtils:
    """Utility functions for mission management."""
    def __init__(self):
        self.logger = FLLLogger('MissionUtils')

    def validate_mission(self, mission_data):
        try:
            valid = isinstance(mission_data, dict) and 'name' in mission_data
            self.logger.info(f"Mission validation: {valid}")
            return valid
        except Exception as e:
            self.logger.error(f"Validate mission error: {e}")
            raise FLLSimError(f"Validate mission error: {e}") from e

    def save_mission(self, mission_data, mission_path):
        import json
        try:
            with open(mission_path, 'w', encoding='utf-8') as f:
                json.dump(mission_data, f, indent=2)
            self.logger.info(f"Mission saved to {mission_path}")
        except Exception as e:
            self.logger.error(f"Save mission error: {e}")
            raise FLLSimError(f"Save mission error: {e}") from e

    def load_mission(self, mission_path):
        import json
        try:
            with open(mission_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Mission loaded from {mission_path}")
            return data
        except Exception as e:
            self.logger.error(f"Load mission error: {e}")
            raise FLLSimError(f"Load mission error: {e}") from e
            raise FLLSimError(f"Load mission error: {e}") from e
