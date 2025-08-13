"""
Sync Status Utility Module

Provides helper functions for tracking and reporting cloud sync status in FLL-Sim.
"""
from fll_sim.utils.errors import FLLSimError
from fll_sim.utils.logger import FLLLogger


class SyncStatusUtils:
    """Utility functions for cloud sync status tracking."""
    def __init__(self):
        self.logger = FLLLogger('SyncStatusUtils')
        self.status = {}

    def update_status(self, item, state):
        try:
            self.status[item] = state
            self.logger.info(f"Sync status updated: {item} = {state}")
        except Exception as e:
            self.logger.error(f"Update status error: {e}")
            raise FLLSimError(f"Update status error: {e}") from e

    def get_status(self, item):
        try:
            state = self.status.get(item, "unknown")
            self.logger.info(f"Sync status for {item}: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Get status error: {e}")
            raise FLLSimError(f"Get status error: {e}") from e

    def all_status(self):
        try:
            self.logger.info(f"All sync status: {self.status}")
            return self.status.copy()
        except Exception as e:
            self.logger.error(f"All status error: {e}")
            raise FLLSimError(f"All status error: {e}") from e
            raise FLLSimError(f"All status error: {e}") from e
