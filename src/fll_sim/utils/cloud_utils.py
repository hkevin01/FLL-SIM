"""Cloud utilities for backup and sync in FLL-Sim.

This module provides filesystem-based backup helpers that can be adapted to
real cloud providers in the future. It uses simple directory copy operations
to snapshot and restore project state.
"""

from __future__ import annotations

import os
import shutil
from typing import List

from fll_sim.utils.errors import FLLSimError
from fll_sim.utils.logger import FLLLogger


class CloudUtils:
    """Utility functions for cloud sync and backup."""

    def __init__(self) -> None:
        self.logger = FLLLogger("CloudUtils")

    def backup_project(self, project_path: str, backup_dir: str) -> str:
        """Create or update a project backup directory.

        Returns the path to the backup.
        """
        try:
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(
                backup_dir,
                os.path.basename(project_path),
            )
            shutil.copytree(project_path, backup_path, dirs_exist_ok=True)
            self.logger.info(f"Project backed up to {backup_path}")
            return backup_path
        except Exception as e:  # pragma: no cover - surfaced to GUI/logs
            self.logger.error(f"Backup error: {e}")
            raise FLLSimError(f"Backup error: {e}") from e

    def restore_project(self, backup_path: str, restore_dir: str) -> str:
        """Restore a project backup into the restore directory.

        Returns the path to the restored project.
        """
        try:
            restore_path = os.path.join(
                restore_dir,
                os.path.basename(backup_path),
            )
            shutil.copytree(backup_path, restore_path, dirs_exist_ok=True)
            self.logger.info(f"Project restored to {restore_path}")
            return restore_path
        except Exception as e:  # pragma: no cover - surfaced to GUI/logs
            self.logger.error(f"Restore error: {e}")
            raise FLLSimError(f"Restore error: {e}") from e

    def list_backups(self, backup_dir: str) -> List[str]:
        """List available backups in the backup directory."""
        try:
            backups = [
                f for f in os.listdir(backup_dir)
                if os.path.isdir(os.path.join(backup_dir, f))
            ]
            self.logger.info(f"Backups found: {backups}")
            return backups
        except Exception as e:  # pragma: no cover - surfaced to GUI/logs
            self.logger.error(f"List backups error: {e}")
            raise FLLSimError(f"List backups error: {e}") from e

    def backup_exists(self, backup_dir: str, project_name: str) -> bool:
        """Return whether a named project backup exists."""
        backup_path = os.path.join(backup_dir, project_name)
        exists = os.path.exists(backup_path) and os.path.isdir(backup_path)
        self.logger.info(f"Backup exists for {project_name}: {exists}")
        return exists

    def delete_backup(self, backup_dir: str, project_name: str) -> bool:
        """Delete a specific backup if it exists."""
        backup_path = os.path.join(backup_dir, project_name)
        try:
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
                self.logger.info(f"Backup deleted: {backup_path}")
                return True
            self.logger.info(f"No backup found to delete: {backup_path}")
            return False
        except Exception as e:  # pragma: no cover - surfaced to GUI/logs
            self.logger.error(f"Delete backup error: {e}")
            raise FLLSimError(f"Delete backup error: {e}") from e
