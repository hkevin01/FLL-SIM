"""
Onboarding Wizard Module

Provides onboarding workflows for new users and educators in FLL-Sim.
"""

from src.fll_sim.utils.logger import FLLLogger

class OnboardingWizard:
    """Manages onboarding workflows for new users and educators."""
    def __init__(self):
        self.logger = FLLLogger("OnboardingWizard")
        self.steps = [
            "Welcome to FLL-Sim!",
            "Set up your robot and environment.",
            "Explore tutorials and guided exercises.",
            "Review the developer and educator guides.",
            "Start your first simulation!"
        ]
        self.current_step = 0
        self.logger.info("Onboarding wizard initialized.")

    def start_onboarding(self, user_type="student"):
        """Starts the onboarding process for a given user type."""
        self.logger.info(f"Starting onboarding for {user_type}")
        self.current_step = 0
        return self.steps[self.current_step]

    def next_step(self):
        """Advances to the next step in the onboarding process."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.logger.info(f"Onboarding step: {self.steps[self.current_step]}")
            return self.steps[self.current_step]
        self.logger.info("Onboarding complete.")
        return "Onboarding complete."

    def prev_step(self):
        """Goes back to the previous step in the onboarding process."""
        if self.current_step > 0:
            self.current_step -= 1
            self.logger.info(f"Moved to step {self.current_step}: {self.steps[self.current_step]}")
            return self.steps[self.current_step]
        return self.steps[0]

    def get_current_step(self):
        """Returns the current step in the onboarding process."""
        return self.steps[self.current_step]

    def reset(self):
        """Resets the onboarding process to the initial state."""
        self.current_step = 0
        self.logger.info("Onboarding reset.")
        return self.steps[self.current_step]
