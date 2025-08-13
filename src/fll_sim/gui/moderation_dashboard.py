"""
Moderation Dashboard GUI for FLL-Sim

Provides a user interface for community content moderation and analytics visualization.
"""
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QPushButton,
                             QVBoxLayout, QWidget)

from fll_sim.education.moderation_analytics import (AnalyticsDashboard,
                                                    ModerationManager)


class ModerationDashboardWidget(QWidget):
    """
    Widget for managing community moderation and viewing analytics.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = ModerationManager()
        self.analytics = AnalyticsDashboard()
        self._setup_ui()
        self._update_submissions()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.submissions_list = QListWidget()
        layout.addWidget(QLabel("Pending Submissions:"))
        layout.addWidget(self.submissions_list)
        btn_layout = QHBoxLayout()
        self.approve_btn = QPushButton("Approve")
        self.reject_btn = QPushButton("Reject")
        self.approve_btn.clicked.connect(self._approve)
        self.reject_btn.clicked.connect(self._reject)
        btn_layout.addWidget(self.approve_btn)
        btn_layout.addWidget(self.reject_btn)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Analytics:"))
        self.analytics_label = QLabel("")
        layout.addWidget(self.analytics_label)

    def _update_submissions(self):
        self.submissions_list.clear()
        for content in self.manager.submissions:
            self.submissions_list.addItem(content.get("title", "Untitled"))
        self._update_analytics()

    def _approve(self):
        idx = self.submissions_list.currentRow()
        if idx >= 0:
            self.manager.moderate_content(idx, True)
            self._update_submissions()

    def _reject(self):
        idx = self.submissions_list.currentRow()
        if idx >= 0:
            self.manager.moderate_content(idx, False)
            self._update_submissions()

    def _update_analytics(self):
        stats = self.analytics.get_stats()
        self.analytics_label.setText(str(stats))
