"""
Cloud Utility Module

Provides helper functions for cloud sync, user profile management,
and project backup in FLL-Sim.
"""


class CloudUtils:
    """Utility functions for cloud sync and backup."""
    def __init__(self):
        from src.fll_sim.utils.logger import FLLLogger
        self.logger = FLLLogger('CloudUtils')

    def backup_project(self, project_path, backup_dir):
        import os
        import shutil
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            backup_path = os.path.join(
                backup_dir,
                os.path.basename(project_path)
            )
            shutil.copytree(project_path, backup_path, dirs_exist_ok=True)
            self.logger.info(f"Project backed up to {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Backup error: {e}")
            from src.fll_sim.utils.errors import FLLSimError
            raise FLLSimError(f"Backup error: {e}") from e

    def restore_project(self, backup_path, restore_dir):
        import os
        import shutil
        try:
            restore_path = os.path.join(
                restore_dir,
                os.path.basename(backup_path)
            )
            shutil.copytree(backup_path, restore_path, dirs_exist_ok=True)
            self.logger.info(f"Project restored to {restore_path}")
            return restore_path
        except Exception as e:
            self.logger.error(f"Restore error: {e}")
            from src.fll_sim.utils.errors import FLLSimError
            raise FLLSimError(f"Restore error: {e}") from e

    def list_backups(self, backup_dir):
        import os
        try:
            backups = [
                f for f in os.listdir(backup_dir)
                if os.path.isdir(os.path.join(backup_dir, f))
            ]
            self.logger.info(f"Backups found: {backups}")
            return backups
        except Exception as e:
            self.logger.error(f"List backups error: {e}")
            from src.fll_sim.utils.errors import FLLSimError
            raise FLLSimError(f"List backups error: {e}") from e
