"""
Test Cloud Utility Module

Unit tests for CloudUtils backup, restore, and list_backups functions.
"""
import os
import shutil
import unittest

from fll_sim.utils.cloud_utils import CloudUtils


class TestCloudUtils(unittest.TestCase):
    def setUp(self):
        self.utils = CloudUtils()
        self.test_dir = 'test_project_dir'
        self.backup_dir = 'test_backup_dir'
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, 'file.txt'), 'w') as f:
            f.write('test')

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
        shutil.rmtree(self.backup_dir, ignore_errors=True)

    def test_backup_and_restore(self):
        backup_path = self.utils.backup_project(self.test_dir, self.backup_dir)
        self.assertTrue(os.path.exists(backup_path))
        restore_dir = 'test_restore_dir'
        restored_path = self.utils.restore_project(backup_path, restore_dir)
        self.assertTrue(os.path.exists(restored_path))
        shutil.rmtree(restore_dir, ignore_errors=True)

    def test_list_backups(self):
        self.utils.backup_project(self.test_dir, self.backup_dir)
        backups = self.utils.list_backups(self.backup_dir)
        self.assertIn(os.path.basename(self.test_dir), backups)

if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
