"""Command line interface entrypoints for FLL-Sim.

Provides two console scripts:
  * fll-sim      -> headless / simulation focused entrypoint
  * fll-sim-gui  -> launches the PyQt6 GUI

Both honor:
  --headless / FLL_SIM_HEADLESS=1  : force headless mode
  --exit-after SECONDS             : auto-exit (used for CI smoke tests)
  --tutorial NAME                  : (future) tutorial launch hook

These wrappers keep imports light to speed cold start and allow PyInstaller
to collect the correct symbols.
"""
from __future__ import annotations

import argparse
import os
import signal
import sys
import threading
import time
from typing import Optional


def _parse_common_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fll-sim",
        description="FLL-Sim – First Lego League Simulator"
    )
    parser.add_argument("--headless", action="store_true", help="Run without opening a graphical window")
    parser.add_argument("--exit-after", type=float, default=None, help="Exit automatically after N seconds (CI/testing)")
    parser.add_argument("--tutorial", type=str, default=None, help="Launch a specific tutorial (scaffolding)")
    parser.add_argument("--profile", type=str, default="beginner", help="Simulation profile (beginner|intermediate|advanced)")
    parser.add_argument("--season", type=str, default="2024", help="FLL season year (default: 2024)")
    parser.add_argument("--demo", choices=["basic", "pybricks", "missions", "ai"], help="Run a specific demo and exit")
    return parser.parse_args(argv)

def _schedule_exit(after: float):
    def _killer():
        time.sleep(after)
        os.kill(os.getpid(), signal.SIGINT)
    t = threading.Thread(target=_killer, daemon=True)
    t.start()

def main(argv: Optional[list[str]] = None) -> int:
    """Console entrypoint for simulation / headless usage."""
    args = _parse_common_args(argv or sys.argv[1:])
    if args.headless:
        os.environ["FLL_SIM_HEADLESS"] = "1"
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if args.exit_after and args.exit_after > 0:
        _schedule_exit(args.exit_after)
    from importlib import \
        import_module  # noqa: F401  (placeholder for future dynamic loads)
    try:
        from fll_sim import __version__  # type: ignore
    except Exception:
        __version__ = "0.0.0-dev"
    print(f"FLL-Sim v{__version__} – profile={args.profile} season={args.season} headless={bool(args.headless)}")
    # Import the main simulation function
    old_path = sys.path.copy()
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    try:
        from main import run_simulation_demo  # noqa: E402
    finally:
        sys.path[:] = old_path
    if args.demo:
        print(f"Running demo: {args.demo}")
    run_simulation_demo(headless=bool(args.headless))
    return 0

def gui(argv: Optional[list[str]] = None) -> int:
    """GUI entrypoint (also supports --headless for CI smoke tests)."""
    args = _parse_common_args(argv or sys.argv[1:])
    if args.headless:
        os.environ["FLL_SIM_HEADLESS"] = "1"
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if args.exit_after and args.exit_after > 0:
        _schedule_exit(args.exit_after)
    try:
        from fll_sim.gui.main_gui import main as gui_main  # noqa: E402
    except Exception as e:
        print(f"Failed to import GUI: {e}", file=sys.stderr)
        return 1
    print("Launching FLL-Sim GUI...")
    gui_main()
    return 0

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
