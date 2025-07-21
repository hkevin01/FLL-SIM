"""
Accessibility Helpers Module

Provides utilities for screen reader support, keyboard navigation, and other accessibility features in FLL-Sim GUI.
Designed for integration with PyQt6 and future accessibility improvements.
"""

from typing import Optional

class AccessibilityHelper:
    """Provides accessibility utilities for GUI components."""
    def __init__(self):
        self.screen_reader_enabled: bool = False
        self.keyboard_navigation_enabled: bool = True
        self.last_accessible_event: Optional[str] = None

    def enable_screen_reader(self) -> None:
        self.screen_reader_enabled = True
        self.last_accessible_event = "Screen reader enabled"
        # Integrate with PyQt6 accessibility APIs as needed

    def disable_screen_reader(self) -> None:
        self.screen_reader_enabled = False
        self.last_accessible_event = "Screen reader disabled"

    def enable_keyboard_navigation(self) -> None:
        self.keyboard_navigation_enabled = True
        self.last_accessible_event = "Keyboard navigation enabled"
        # Integrate with PyQt6 focus and tab order APIs

    def disable_keyboard_navigation(self) -> None:
        self.keyboard_navigation_enabled = False
        self.last_accessible_event = "Keyboard navigation disabled"

    def is_accessible(self) -> bool:
        return self.screen_reader_enabled or self.keyboard_navigation_enabled

    def get_last_event(self) -> Optional[str]:
        return self.last_accessible_event
