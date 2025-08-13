"""
User Profile Utility Module

Provides helper functions for user profile management, validation, and sync in FLL-Sim.
"""
import json

from fll_sim.utils.errors import FLLSimError
from fll_sim.utils.logger import FLLLogger


class UserProfileUtils:
    """Utility functions for user profile management."""
    def __init__(self):
        self.logger = FLLLogger('UserProfileUtils')

    def save_profile(self, profile_data, profile_path):
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
            self.logger.info(f"Profile saved to {profile_path}")
        except Exception as e:
            self.logger.error(f"Save profile error: {e}")
            raise FLLSimError(f"Save profile error: {e}") from e

    def load_profile(self, profile_path):
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Profile loaded from {profile_path}")
            return data
        except Exception as e:
            self.logger.error(f"Load profile error: {e}")
            raise FLLSimError(f"Load profile error: {e}") from e

    def validate_profile(self, profile_data):
        try:
            valid = isinstance(profile_data, dict) and 'username' in profile_data
            self.logger.info(f"Profile validation: {valid}")
            return valid
        except Exception as e:
            self.logger.error(f"Validate profile error: {e}")
            raise FLLSimError(f"Validate profile error: {e}") from e
            self.logger.error(f"Validate profile error: {e}")
            raise FLLSimError(f"Validate profile error: {e}") from e
