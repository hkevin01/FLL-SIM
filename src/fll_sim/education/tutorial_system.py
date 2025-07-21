"""
Tutorial System Module

Provides interactive step-by-step learning modules for FLL-Sim.
Modular, extensible API for adding new tutorials and learning paths.
"""

from typing import List, Dict, Optional


class TutorialStep:
    """Represents a single step in a tutorial."""
    def __init__(self, title: str, content: str, hint: str = None):
        self.title = title
        self.content = content
        self.hint = hint


class Tutorial:
    """A complete tutorial consisting of multiple steps."""

    def __init__(self, name: str, steps: list):
        self.name = name
        self.steps = steps
        self.current_step = 0

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            return self.steps[self.current_step]
        return None

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            return self.steps[self.current_step]
        return None

    def get_current_step(self):
        return self.steps[self.current_step]


class TutorialManager:
    """Manages tutorials, user progress, and module loading."""

    def __init__(self):
        # Initialize tutorial registry and user progress tracking
        self.tutorials = {}
        self.user_progress = {}

    def load_tutorials(self):
        """Load available tutorials from content directory or plugins."""
        pass

    def start_tutorial(self, tutorial_id):
        """Begin a tutorial session for the given tutorial ID."""
        pass

    def track_progress(self, user_id, tutorial_id, step):
        """Track user progress through tutorial steps."""
        pass

    def get_progress(self, user_id, tutorial_id):
        """Return current progress for a user in a tutorial."""
        pass

    def add_tutorial(self, tutorial: Tutorial):
        self.tutorials[tutorial.name] = tutorial
        self.user_progress[tutorial.name] = 0

    def get_tutorial(self, name: str):
        return self.tutorials.get(name)

    def set_user_progress(self, tutorial_name: str, step_index: int):
        if tutorial_name in self.tutorials:
            self.user_progress[tutorial_name] = step_index

    def get_user_progress(self, tutorial_name: str):
        return self.user_progress.get(tutorial_name, 0)
