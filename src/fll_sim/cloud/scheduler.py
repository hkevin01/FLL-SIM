"""
Cloud Sync Scheduler Module

Provides scheduling and automation for cloud sync operations in FLL-Sim.
"""
import threading
import time

from fll_sim.utils.logger import FLLLogger


class CloudSyncScheduler:
    """Schedules and automates cloud sync operations."""
    def __init__(self, sync_manager, interval=300):
        self.logger = FLLLogger('CloudSyncScheduler')
        self.sync_manager = sync_manager
        self.interval = interval  # seconds
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()
            self.logger.info("Cloud sync scheduler started.")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self.logger.info("Cloud sync scheduler stopped.")

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.sync_manager.sync_profile("auto-scheduled-profile")
                self.logger.info("Automated cloud sync completed.")
            except Exception as e:
                self.logger.error(f"Cloud sync error: {e}")
            time.sleep(self.interval)
                self.logger.error(f"Cloud sync error: {e}")
            time.sleep(self.interval)
