"""
Test suite for CloudAutoBackup module
"""
import time
import unittest
from unittest.mock import MagicMock

from fll_sim.cloud.cloud_auto_backup import CloudAutoBackup


class TestCloudAutoBackup(unittest.TestCase):
    def setUp(self):
        self.mock_utils = MagicMock()
        self.backup = CloudAutoBackup(self.mock_utils, interval=1)

    def test_start_and_stop(self):
        self.backup.start()
        time.sleep(2)
        self.assertEqual(self.backup.get_status(), "Running")
        self.backup.stop()
        self.assertEqual(self.backup.get_status(), "Stopped")

    def test_backup_called(self):
        self.backup.start()
        time.sleep(2)
        self.backup.stop()
        self.assertTrue(self.mock_utils.backup_project.called)

    def test_multiple_starts(self):
        self.backup.start()
        self.backup.start()  # Should not start a new thread
        time.sleep(2)
        self.backup.stop()
        self.assertEqual(self.backup.get_status(), "Stopped")

    def test_exception_handling(self):
        self.mock_utils.backup_project.side_effect = Exception("Backup error")
        self.backup.start()
        time.sleep(2)
        self.backup.stop()
        # Check that logger.error was called
        self.assertTrue(any("Backup error" in str(call) for call in self.backup.logger.error.call_args_list))

if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
