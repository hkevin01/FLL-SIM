"""
Cloud Sync Module

Provides cloud sync and collaboration features for user profiles and projects.
"""


class CloudSyncManager:
    """Manages cloud sync and collaboration for user profiles and projects."""
    def __init__(self):
        from src.fll_sim.utils.logger import FLLLogger
        self.logger = FLLLogger('CloudSyncManager')
        self.synced_items = []

    def sync_profile(self, profile):
        self.synced_items.append(profile)
        self.logger.info(f"Profile synced: {profile}")

    def sync_project(self, project):
        self.synced_items.append(project)
        self.logger.info(f"Project synced: {project}")

    def get_synced_items(self):
        return self.synced_items

    def rollback(self, index):
        from src.fll_sim.utils.errors import FLLSimError
        try:
            item = self.synced_items.pop(index)
            self.logger.info(f"Rolled back: {item}")
            return item
        except Exception as e:
            self.logger.error(f"Rollback error: {e}")
            raise FLLSimError(f"Rollback error: {e}") from e
