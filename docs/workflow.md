# FLL-Sim Workflow Guide

## Setup
- Clone the repository
- Create and activate the virtual environment (`fll-sim-env`)
- Install dependencies: `pip install -r requirements.txt`
- Run setup script: `python setup.py`

## Development
- Follow PEP8, use type hints and docstrings
- Use `black` for formatting, `flake8` for linting, and `mypy` for type checking
- Add/modify tests in `tests/`
- Use pre-commit hooks for code quality

## Testing
- Run all tests: `pytest` or `python -m unittest discover tests`
- Check coverage: `pytest --cov=src` or `python -m coverage run -m unittest discover tests`

## CI/CD
- All pushes trigger linting, testing, and coverage checks via GitHub Actions
- PRs require passing tests and code review

## Logging & Error Handling
- All modules use centralized logging (`src/fll_sim/utils/logger.py`)
- Use custom error types from `src/fll_sim/utils/errors.py`

## Configuration
- Main config: `config/app_config.json`
- .copilot/config.json and package.json for dev tooling

## Contribution
- See `docs/developer_onboarding.md` for onboarding
- Open issues or PRs for improvements

## Common Commands
- `npm run lint` (lint Python code)
- `npm run typecheck` (type check)
- `npm run format` (format code)
- `npm run test` (run tests)
- `npm run coverage` (run coverage)

## Automation & Advanced Testing
- All new features require unit, integration, and edge case tests
- Use CI/CD pipeline for automated linting, testing, and coverage
- Test plugin/content ecosystem with sample plugins and integration tests

## Plugin & Content Ecosystem
- Add plugins in `src/fll_sim/plugins/`
- Validate and load plugins via `PluginManager`
- Use sample plugins for demonstration and testing

## Internationalization & Accessibility
- Add translations in `src/fll_sim/education/i18n.py`
- Enable accessibility features via `AccessibilityHelper`

## Community & Collaboration
- Use community features in `src/fll_sim/education/community_features.py`
- Share missions, robots, and projects via platform tools

## Documentation
- Update `docs/project_plan.md` and `docs/test_plan.md` with new phases and checkboxes
- Document all new modules and features
