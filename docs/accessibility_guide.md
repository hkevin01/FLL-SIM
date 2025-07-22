# FLL-Sim Accessibility Guide

This guide describes accessibility features and best practices for FLL-Sim.

## Features
- Screen reader support (PyQt6 integration, planned)
- Keyboard navigation (planned)
- Color contrast and UI accessibility checks (planned)
- Customizable accessibility options per user

## How to Enable
- Accessibility features can be enabled via the GUI settings or config files.
- Use the Accessibility menu in the GUI to enable screen reader or keyboard navigation.
- Accessibility options can be set per user profile.
- See `src/fll_sim/education/accessibility.py` for implementation details.

## Developer Checklist
- Use semantic UI elements and labels
- Ensure all controls are keyboard accessible
- Test color contrast and font sizes
- Provide alt text for images and icons

## Developer Notes
- Accessibility features are managed by the `AccessibilityHelper` class in `src/fll_sim/education/accessibility.py`.
- Future improvements will include localization and additional assistive technologies.

## Roadmap
- [ ] Implement screen reader support in GUI
- [ ] Add keyboard navigation to all interactive elements
- [ ] Integrate accessibility checks in CI pipeline

For feedback or suggestions, open an issue or PR.
