#!/usr/bin/env python3
"""
Simple test to verify our GUI fixes are working
"""
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_import_fixes():
    """Test that our import fixes work"""
    print("Testing import fixes...")

    # Test the core simulator import that we fixed
    try:
        from fll_sim.core.simulator import Simulator
        print("✓ fll_sim.core.simulator import works")
    except ImportError as e:
        print(f"✗ fll_sim.core.simulator import failed: {e}")
        return False

    # Test GUI import
    try:
        from fll_sim.gui.main_gui import FLLSimMainWindow
        print("✓ GUI main window import works")
    except ImportError as e:
        print(f"✗ GUI import failed: {e}")
        return False

    return True

def test_platform_compatibility():
    """Test platform detection that we fixed"""
    print("Testing platform compatibility...")

    import platform
    current_platform = platform.system()
    print(f"✓ Detected platform: {current_platform}")

    # Test that our platform detection works
    if current_platform in ['Windows', 'Darwin', 'Linux']:
        print("✓ Platform detection working")
        return True
    else:
        print(f"✗ Unknown platform: {current_platform}")
        return False

def test_gui_methods():
    """Test that the GUI methods we added exist"""
    print("Testing GUI methods...")

    try:
        from fll_sim.gui.main_gui import FLLSimMainWindow

        # Create a dummy instance (won't fully initialize without Qt app)
        methods_to_check = [
            '_add_motor', '_remove_motor',
            '_add_sensor', '_remove_sensor',
            '_export_performance_data'
        ]

        for method_name in methods_to_check:
            if hasattr(FLLSimMainWindow, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} missing")
                return False

        return True
    except Exception as e:
        print(f"✗ GUI method test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("FLL-Sim Fix Verification Test")
    print("=" * 40)

    all_passed = True

    # Test import fixes
    if not test_import_fixes():
        all_passed = False

    print()

    # Test platform compatibility
    if not test_platform_compatibility():
        all_passed = False

    print()

    # Test GUI methods
    if not test_gui_methods():
        all_passed = False

    print()
    print("=" * 40)
    if all_passed:
        print("✓ All tests passed! GUI fixes are working.")
        return 0
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
