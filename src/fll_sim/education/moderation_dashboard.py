"""
Moderation Dashboard Module

Provides tools for moderators to review analytics, manage users,
and enforce community standards in FLL-Sim.
"""
from fll_sim.utils.logger import FLLLogger


class ModerationDashboard:
    def __init__(self):
        self.logger = FLLLogger("ModerationDashboard")
        self.moderator_actions = []

    def log_action(self, moderator_id, action):
        self.moderator_actions.append((moderator_id, action))
        self.logger.info(
            f"Moderator {moderator_id} performed action: {action}"
        )

    def get_actions(self):
        return self.moderator_actions
