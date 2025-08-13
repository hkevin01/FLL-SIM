"""Cloud Auto Backup Module.

Provides scheduled cloud backup functionality for FLL-Sim.

This module defines a lightweight scheduler that periodically triggers a
project backup using a provided cloud utility object.
"""
import threading
import time
from typing import Any

from fll_sim.utils.logger import FLLLogger


class CloudAutoBackup:
    """Schedules and automates cloud backups."""
    def __init__(self, cloud_utils: Any, interval: int = 3600):
        self.logger = FLLLogger('CloudAutoBackup')
        self.cloud_utils = cloud_utils
        self.interval: int = interval  # seconds
        self._stop_event = threading.Event()
        self._thread = None

    def start(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()
            self.logger.info("Cloud auto backup started.")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self.logger.info("Cloud auto backup stopped.")

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.cloud_utils.backup_project(
                    "/home/kevin/Projects/FLL-SIM",
                    "data/backups",
                )
                self.logger.info("Automated cloud backup completed.")
            except Exception as e:
                self.logger.error(f"Cloud backup error: {e}")
            time.sleep(self.interval)

    def get_status(self) -> str:
        """Return current backup status."""
        if self._thread and self._thread.is_alive():
            return "Running"
        return "Stopped"
