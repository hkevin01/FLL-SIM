"""
Backup Manager GUI integration for FLL-Sim

Provides user controls for scheduled cloud backups, status display, and error reporting.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox
from src.fll_sim.cloud.cloud_auto_backup import CloudAutoBackup
from src.fll_sim.utils.cloud_utils import CloudUtils
from src.fll_sim.utils.backup_utils import BackupUtils

class BackupManagerWidget(QWidget):
    """
    Widget for managing cloud auto backup in the GUI.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cloud_utils = CloudUtils()
        self.auto_backup = CloudAutoBackup(self.cloud_utils, interval=3600)
        self.backup_utils = BackupUtils()
        self._setup_ui()
        self._update_status()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.status_label = QLabel("Backup Status: Unknown")
        layout.addWidget(self.status_label)
        self.start_btn = QPushButton("Start Backup")
        self.stop_btn = QPushButton("Stop Backup")
        self.refresh_button = QPushButton("Refresh Backup List")
        self.restore_button = QPushButton("Restore Selected Backup")
        self.start_btn.clicked.connect(self._start_backup)
        self.stop_btn.clicked.connect(self._stop_backup)
        self.refresh_button.clicked.connect(self.load_backups)
        self.restore_button.clicked.connect(self.restore_selected)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(QLabel("Backup History"))
        self.backup_list = QListWidget()
        layout.addWidget(self.backup_list)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.restore_button)

    def _start_backup(self):
        try:
            self.auto_backup.start()
            self._update_status()
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def _stop_backup(self):
        try:
            self.auto_backup.stop()
            self._update_status()
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def _update_status(self):
        status = self.auto_backup.get_status()
        self.status_label.setText(f"Backup Status: {status}")

    def load_backups(self):
        self.backup_list.clear()
        backups = self.backup_utils.list_backups()
        for backup in backups:
            self.backup_list.addItem(backup)

    def restore_selected(self):
        selected = self.backup_list.currentItem()
        if selected:
            backup_name = selected.text()
            try:
                # Pass restore_path explicitly
                self.backup_utils.restore_backup(backup_name, restore_path="/home/kevin/Projects/FLL-SIM")
                QMessageBox.information(
                    self,
                    "Restore",
                    f"Backup '{backup_name}' restored successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Restore Error",
                    str(e)
                )
        else:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a backup to restore."
            )
