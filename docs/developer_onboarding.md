# FLL-Sim Developer Onboarding Guide

Welcome to the FLL-Sim project! This guide will help you set up your development environment, understand the codebase, and contribute effectively.

## Getting Started
1. Clone the repository and set up the Python virtual environment (`fll-sim-env`).
2. Install dependencies: `pip install -r requirements.txt`
3. Review coding standards: PEP8, type hints, docstrings, modular architecture.
4. Run tests: `pytest` and `pytest-cov` for coverage.

## Codebase Overview
- `src/fll_sim/education/`: Educational modules (tutorials, assessments, curriculum, community, plugin, i18n, accessibility)
- `src/fll_sim/core/`: Simulation engine
- `src/fll_sim/gui/`: GUI components (PyQt6)
- `tests/`: Automated tests

## Contributing
- Follow code style and documentation standards.
- Add/modify tests for new features.
- Document all public APIs and modules.
- Use pre-commit hooks for linting and formatting.

## CI/CD
- All pushes trigger linting, testing, and coverage checks.
- PRs require passing tests and code review.

## Resources
- See `docs/` for project plan, test plan, and technical documentation.
- Ask questions in the community forums or open an issue.

Happy coding!
