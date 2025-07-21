"""
Onboarding Wizard Module

Provides onboarding wizards and guidance for new users and educators in FLL-Sim.
"""

from src.fll_sim.utils.logger import FLLLogger

class OnboardingWizard:
    """Guides new users and educators through initial setup and usage."""
    def __init__(self):
        self.logger = FLLLogger('OnboardingWizard')
        self.steps = [
            "Welcome to FLL-Sim!",
            "Set up your robot and environment.",
            "Explore tutorials and guided exercises.",
            "Review the developer and educator guides.",
            "Start your first simulation!"
        ]
        self.current_step = 0
        self.logger.info("Onboarding wizard initialized.")

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.logger.info(f"Moved to step {self.current_step}: {self.steps[self.current_step]}")
            return self.steps[self.current_step]
        self.logger.info("Onboarding complete.")
        return "Onboarding complete."

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.logger.info(f"Moved to step {self.current_step}: {self.steps[self.current_step]}")
            return self.steps[self.current_step]
        return self.steps[0]

    def get_current_step(self):
        return self.steps[self.current_step]
