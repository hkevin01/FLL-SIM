# Developer Guide: Extending Educational Features in FLL-Sim

## Overview
This guide explains how to extend and integrate new educational features (tutorials, assessments, curriculum integration, community tools) into the FLL-Sim platform. All development should use the `fll-sim-env` virtual environment for consistency and reproducibility.

## Architecture Principles
- **Modularity:** Educational features are implemented as independent, reusable modules in `src/fll_sim/education/`.
- **Extensible APIs:** Each module exposes clear interfaces for integration and extension.
- **Separation of Concerns:** UI, logic, and data management are separated for maintainability.
- **Testing:** All new features require automated unit tests in `tests/` and must be run using `fll-sim-env/bin/python`.

## Adding a New Educational Module
1. **Create a new Python file in `src/fll_sim/education/`**
2. **Define a base class or API for your feature**
3. **Implement core logic and public methods with docstrings and type hints**
4. **Add unit tests in `tests/test_education_modules.py`**
5. **Document your module in this guide and update API docs**

## Example: Adding a Tutorial Module
```python
# src/fll_sim/education/my_tutorial.py
class MyTutorial:
    """Custom tutorial module for FLL-Sim."""
    def __init__(self, steps: list[str]):
        self.steps = steps
    def run(self):
        for step in self.steps:
            print(step)
```

## Testing Your Module
- Add tests to `tests/test_education_modules.py`:
```python
import unittest
from src.fll_sim.education.my_tutorial import MyTutorial
class TestMyTutorial(unittest.TestCase):
    def test_run(self):
        tutorial = MyTutorial(["Step 1", "Step 2"])
        tutorial.run()
```
- Run tests with:
```
fll-sim-env/bin/python -m unittest tests/test_education_modules.py
```

## Best Practices
- Use type hints and docstrings for all public classes and methods
- Follow PEP8 and project style guides
- Keep modules small and focused
- Update documentation and API references
- Log changes in `/data/logs/change_log.txt`

## Extending Existing Features
- Inherit from base classes in `src/fll_sim/education/`
- Register new modules in the main application as needed
- Add integration tests for complex features

## API Reference
- See `/docs/api_education.md` for detailed module APIs

---
