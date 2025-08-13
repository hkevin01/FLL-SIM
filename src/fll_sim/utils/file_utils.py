"""
File Utility Module

Provides helper functions for file operations, validation, and safe file handling in FLL-Sim.
"""
import os
import shutil

from fll_sim.utils.errors import FLLSimError
from fll_sim.utils.logger import FLLLogger


class FileUtils:
    """Utility functions for file operations and validation."""
    def __init__(self):
        self.logger = FLLLogger('FileUtils')

    def safe_copy(self, src, dst):
        try:
            shutil.copy2(src, dst)
            self.logger.info(f"Copied file from {src} to {dst}")
        except Exception as e:
            self.logger.error(f"Copy error: {e}")
            raise FLLSimError(f"Copy error: {e}") from e

    def safe_delete(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
                self.logger.info(f"Deleted file: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                self.logger.info(f"Deleted directory: {path}")
        except Exception as e:
            self.logger.error(f"Delete error: {e}")
            raise FLLSimError(f"Delete error: {e}") from e

    def validate_file(self, path):
        try:
            valid = os.path.exists(path) and os.path.isfile(path)
            self.logger.info(f"File validation for {path}: {valid}")
            return valid
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            raise FLLSimError(f"Validation error: {e}") from e
            self.logger.error(f"Validation error: {e}")
            raise FLLSimError(f"Validation error: {e}") from e
