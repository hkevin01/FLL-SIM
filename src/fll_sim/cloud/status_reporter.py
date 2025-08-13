"""
Cloud Sync Status Reporter Module

Provides reporting and logging for cloud sync status and history in FLL-Sim.
"""
import datetime

from fll_sim.utils.errors import FLLSimError
from fll_sim.utils.logger import FLLLogger


class CloudSyncStatusReporter:
    """Reports and logs cloud sync status and history."""
    def __init__(self, sync_manager):
        self.logger = FLLLogger('CloudSyncStatusReporter')
        self.sync_manager = sync_manager
        self.history = []

    def log_status(self, item, status):
        timestamp = datetime.datetime.now().isoformat()
        entry = {'item': item, 'status': status, 'timestamp': timestamp}
        self.history.append(entry)
        self.logger.info(f"Sync status: {item} = {status} at {timestamp}")

    def get_history(self):
        return self.history

    def report_current_status(self):
        try:
            items = self.sync_manager.get_synced_items()
            for item in items:
                self.log_status(item, "synced")
            return self.history
        except Exception as e:
            self.logger.error(f"Status report error: {e}")
            raise FLLSimError(f"Status report error: {e}") from e
