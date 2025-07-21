"""
Cloud Sync Automation Test Suite

Automated tests for CloudSyncScheduler and cloud sync automation in FLL-Sim.
"""
import unittest
import time
from unittest.mock import MagicMock
from src.fll_sim.cloud.scheduler import CloudSyncScheduler
from src.fll_sim.cloud.status_reporter import CloudSyncStatusReporter

class DummySyncManager:
    def __init__(self):
        self.synced = []
    def sync_profile(self, profile):
        self.synced.append(profile)
    def get_synced_items(self):
        return self.synced

class TestCloudSyncScheduler(unittest.TestCase):
    def setUp(self):
        self.manager = DummySyncManager()
        self.scheduler = CloudSyncScheduler(self.manager, interval=1)
    def test_automation(self):
        self.scheduler.start()
        time.sleep(2.5)
        self.scheduler.stop()
        self.assertGreaterEqual(len(self.manager.get_synced_items()), 2)
        self.assertIn("auto-scheduled-profile", self.manager.get_synced_items())
    def test_start_and_stop(self):
        self.scheduler.start()
        self.assertTrue(self.scheduler._thread.is_alive())
        self.scheduler.stop()
        self.assertFalse(self.scheduler._thread.is_alive())
    def test_run_sync(self):
        self.manager.sync_profile = MagicMock()
        self.scheduler.start()
        time.sleep(0.2)
        self.scheduler.stop()
        self.manager.sync_profile.assert_called_with("auto-scheduled-profile")

class TestCloudSyncStatusReporter(unittest.TestCase):
    def setUp(self):
        self.mock_manager = MagicMock()
        self.mock_manager.get_synced_items.return_value = ["profile1", "profile2"]
        self.reporter = CloudSyncStatusReporter(self.mock_manager)
    def test_log_status_and_history(self):
        self.reporter.log_status("profile1", "synced")
        history = self.reporter.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["item"], "profile1")
        self.assertEqual(history[0]["status"], "synced")
    def test_report_current_status(self):
        history = self.reporter.report_current_status()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["item"], "profile1")
        self.assertEqual(history[1]["item"], "profile2")

if __name__ == "__main__":
    unittest.main()
