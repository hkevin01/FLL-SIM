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

    def reset(self):
        self.current_step = 0
        return self.steps[self.current_step]

    def is_complete(self):
        return self.current_step == len(self.steps) - 1


class TutorialManager:
    """Manages tutorials and user progress."""
    def __init__(self):
        self.tutorials: Dict[str, Tutorial] = {}
        self.user_progress: Dict[str, int] = {}

    def add_tutorial(self, tutorial: Tutorial):
        self.tutorials[tutorial.name] = tutorial

    def start_tutorial(self, name: str):
        tutorial = self.tutorials.get(name)
        if tutorial:
            tutorial.reset()
            return tutorial.get_current_step()
        return None

    def next_step(self, name: str):
        tutorial = self.tutorials.get(name)
        if tutorial:
            return tutorial.next_step()
        return None

    def prev_step(self, name: str):
        tutorial = self.tutorials.get(name)
        if tutorial:
            return tutorial.prev_step()
        return None

    def get_progress(self, name: str):
        tutorial = self.tutorials.get(name)
        if tutorial:
            return tutorial.current_step, len(tutorial.steps)
        return 0, 0
