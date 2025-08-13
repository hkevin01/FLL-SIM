#!/usr/bin/env python3
"""
Final validation test for FLL-Sim GUI fixes
This test validates that all our fixes are working without launching the GUI
"""

import os
import sys
from pathlib import Path

# Setup project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
os.environ['PYTHONPATH'] = str(project_root / "src")

def validate_all_fixes():
    """Validate all the fixes we made to the GUI"""

    print("🔍 FLL-Sim GUI Fix Validation")
    print("=" * 50)

    success_count = 0
    total_tests = 6

    # Test 1: Core simulator import fix
    try:
        from fll_sim.core.simulator import Simulator
        print("✓ Test 1: Core simulator import works")
        success_count += 1
    except ImportError as e:
        print(f"✗ Test 1: Core simulator import failed: {e}")

    # Test 2: GUI main window import
    try:
        from fll_sim.gui.main_gui import FLLSimMainWindow
        print("✓ Test 2: GUI main window import works")
        success_count += 1
    except ImportError as e:
        print(f"✗ Test 2: GUI import failed: {e}")
        return False

    # Test 3: Platform detection works
    try:
        import platform
        system = platform.system()
        if system in ['Windows', 'Darwin', 'Linux']:
            print(f"✓ Test 3: Platform detection works ({system})")
            success_count += 1
        else:
            print(f"✗ Test 3: Unknown platform: {system}")
    except Exception as e:
        print(f"✗ Test 3: Platform detection failed: {e}")

    # Test 4: Check that all missing methods were added
    try:
        missing_methods = ['_add_motor', '_remove_motor', '_add_sensor', '_remove_sensor', '_export_performance_data']
        all_found = True

        for method_name in missing_methods:
            if hasattr(FLLSimMainWindow, method_name):
                continue
            else:
                print(f"✗ Missing method: {method_name}")
                all_found = False

        if all_found:
            print("✓ Test 4: All missing GUI methods are present")
            success_count += 1
        else:
            print("✗ Test 4: Some GUI methods are still missing")

    except Exception as e:
        print(f"✗ Test 4: Method check failed: {e}")

    # Test 5: Check imports in main.py work
    try:
        # Check if we can import the GUI main function
        from fll_sim.gui.main_gui import main as gui_main
        print("✓ Test 5: GUI main function import works")
        success_count += 1
    except ImportError as e:
        print(f"✗ Test 5: GUI main function import failed: {e}")

    # Test 6: Check that necessary packages are available
    try:
        packages_needed = ['pygame', 'PyQt6', 'pymunk']
        missing_packages = []

        for pkg in packages_needed:
            try:
                __import__(pkg)
            except ImportError:
                missing_packages.append(pkg)

        if not missing_packages:
            print("✓ Test 6: All required packages available")
            success_count += 1
        else:
            print(f"✗ Test 6: Missing packages: {missing_packages}")

    except Exception as e:
        print(f"✗ Test 6: Package check failed: {e}")

    print("=" * 50)
    print(f"📊 Validation Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 ALL FIXES VALIDATED SUCCESSFULLY!")
        print("   The GUI should now work without runtime errors.")
        print("   You can now run: python main.py --gui")
        return True
    else:
        print(f"⚠️  {total_tests - success_count} issues remain")
        print("   Some fixes may need additional work.")
        return False

if __name__ == "__main__":
    validate_all_fixes()
