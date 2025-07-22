"""
Backup Utilities Module

Provides functions for listing, restoring, and managing backups in FLL-Sim.
"""
import os
import shutil
from src.fll_sim.utils.logger import FLLLogger
from src.fll_sim.utils.errors import FLLSimError

class BackupUtils:
    """Utility functions for backup history and restore management."""
    def __init__(self, backup_dir="data/backups"):
        self.logger = FLLLogger('BackupUtils')
        self.backup_dir = backup_dir

    def list_backups(self):
        """List all backup directories."""
        try:
            backups = [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))]
            self.logger.info(f"Found backups: {backups}")
            return backups
        except Exception as e:
            self.logger.error(f"Error listing backups: {e}")
            raise FLLSimError(f"Error listing backups: {e}")

    def restore_backup(self, backup_name, restore_path="/home/kevin/Projects/FLL-SIM"):
        """Restore a backup to the given path."""
        backup_path = os.path.join(self.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            raise FLLSimError(f"Backup '{backup_name}' does not exist.")
        try:
            for item in os.listdir(backup_path):
                s = os.path.join(backup_path, item)
                d = os.path.join(restore_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            self.logger.info(f"Backup '{backup_name}' restored to {restore_path}.")
        except Exception as e:
            self.logger.error(f"Restore backup error: {e}")
            raise FLLSimError(f"Restore backup error: {e}")

    def delete_backup(self, backup_name):
        """Delete a backup directory."""
        try:
            path = os.path.join(self.backup_dir, backup_name)
            shutil.rmtree(path)
            self.logger.info(f"Deleted backup {backup_name}")
        except Exception as e:
            self.logger.error(f"Delete error: {e}")
            raise FLLSimError(f"Delete error: {e}")
