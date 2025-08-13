"""
Cloud Sync Module
"""

from typing import Any, List

from fll_sim.utils.logger import FLLLogger


class CloudSyncManager:
    """Manages cloud sync and collaboration for user profiles and projects."""

    synced_items: List[Any]

    def __init__(self) -> None:
        self.logger = FLLLogger('CloudSyncManager')
        self.synced_items = []

    def sync_profile(self, profile: object) -> None:
        self.synced_items.append(profile)
        self.logger.info(f"Profile synced: {profile}")

    def sync_project(self, project: object) -> None:
        self.synced_items.append(project)
        self.logger.info(f"Project synced: {project}")

    def get_synced_items(self) -> List[Any]:
        return self.synced_items

    def rollback(self, index: int) -> object:
        try:
            item = self.synced_items.pop(index)
            self.logger.info(f"Rolled back: {item}")
            return item
        except IndexError as e:
            self.logger.error(f"Rollback error: {e}")
            return None
            return None
