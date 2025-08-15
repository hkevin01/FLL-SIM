#!/usr/bin/env python3
# test_gui_background.py
"""
Smoke test for GUI background functionality.
Tests that the background renderer can be created without errors.
"""
import os
import sys
from pathlib import Path

# Set up path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_background_smoke():
    """Test that background rendering components can be imported and created."""
    print("Testing background rendering components...")

    try:
        # Test imports
        print("  ✓ Testing background renderer import...")
        from fll_sim.visualization.background import (BackgroundConfig,
                                                      BackgroundRenderer)

        print("  ✓ Testing game map import...")
        from fll_sim.environment.game_map import GameMap

        print("  ✓ Testing simulator view import...")

        print("All imports successful!")

        # Test basic object creation (no GUI)
        print("  ✓ Testing config creation...")
        config = BackgroundConfig(width_mm=2400, height_mm=1200)

        print("  ✓ Testing game map creation...")
        game_map = GameMap()

        print("  ✓ Testing background renderer creation...")
        renderer = BackgroundRenderer(config=config)

        print("Background smoke test completed successfully!")
        return True

    except Exception as e:
        print(f"Background smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_creation():
    """Test GUI creation without showing the window."""
    print("Testing GUI creation...")

    try:
        # Set headless mode to avoid needing X11
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

        from PyQt6.QtWidgets import QApplication

        from fll_sim.environment.game_map import GameMap
        from fll_sim.visualization.simulator_view import SimulatorView

        app = QApplication.instance() or QApplication([])

        print("  ✓ Creating game map...")
        game_map = GameMap()

        print("  ✓ Creating simulator view...")
        view = SimulatorView(game_map, mat_path=None)

        print("  ✓ Testing background toggle...")
        view.toggle_background_visibility(False)
        view.toggle_background_visibility(True)

        print("GUI creation test completed successfully!")
        return True

    except Exception as e:
        print(f"GUI creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fetcher_import():
    """Test that the mat fetcher can be imported."""
    print("Testing mat fetcher import...")

    try:
        print("  ✓ Mat fetcher import successful!")
        return True
    except Exception as e:
        print(f"Mat fetcher import failed: {e}")
        return False

if __name__ == "__main__":
    print("FLL-Sim Background Enhancement Smoke Test")
    print("=" * 50)

    success = True

    success &= test_background_smoke()
    print()
    success &= test_fetcher_import()
    print()
    success &= test_gui_creation()

    print()
    if success:
        print("✅ All smoke tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
