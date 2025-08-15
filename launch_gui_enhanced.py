#!/usr/bin/env python3
# launch_gui_enhanced.py
"""
Enhanced GUI launcher with FLL mat background support.
Supports local mat images and URL downloading.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

# Ensure src on path when launched directly
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "src"))

from PyQt6.QtCore import QTimer  # noqa: E402
from PyQt6.QtWidgets import (QApplication, QCheckBox,  # noqa: E402
                             QMainWindow, QToolBar)

from fll_sim.assets.mats import get_mat_for_season  # noqa: E402
from fll_sim.environment.game_map import GameMap  # noqa: E402
from fll_sim.scripts.fetch_mat import fetch_mat_image  # noqa: E402
from fll_sim.scripts.fetch_mat import fetch_mat_pdf
from fll_sim.visualization.simulator_view import SimulatorView  # noqa: E402


class MainWindow(QMainWindow):
    """Main window with background toggle controls."""

    def __init__(self, view: SimulatorView):
        super().__init__()
        self.view = view
        self.setCentralWidget(view)
        self.setWindowTitle("FLL-Sim Enhanced GUI")

        # Add toolbar with background toggle
        toolbar = QToolBar("View", self)
        self.addToolBar(toolbar)

        self.bg_checkbox = QCheckBox("Show Map Background")
        self.bg_checkbox.setChecked(True)
        self.bg_checkbox.stateChanged.connect(self._on_toggle_bg)
        toolbar.addWidget(self.bg_checkbox)

    def _on_toggle_bg(self, state: int) -> None:
        """Toggle background visibility."""
        visible = bool(state)
        self.view.toggle_background_visibility(visible)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    p = argparse.ArgumentParser(
        description=(
            "FLL-Sim Enhanced GUI with background mat support"
        )
    )
    p.add_argument(
        "--season",
        default="latest",
        help=(
            "Season slug for GameMap.load_season, or 'latest' to pick the "
            "newest local mat"
        ),
    )
    p.add_argument(
        "--mat-path",
        default=None,
        help="Local path to mat image (PNG/JPG)",
    )
    p.add_argument(
        "--mat-url",
        default=None,
        help=(
            "Remote URL to mat image (PNG/JPG). Will be cached under "
            "assets/mats/<season>/mat.png"
        ),
    )
    p.add_argument(
        "--mat-pdf-url",
        default=None,
        help=(
            "Remote URL to mat PDF. Rasterizes to PNG and caches under "
            "assets/mats/<season>/mat.png"
        ),
    )
    p.add_argument(
        "--mat-pdf-page",
        type=int,
        default=0,
        help="PDF page index to rasterize (default 0)",
    )
    p.add_argument(
        "--mat-pdf-page-label",
        default=None,
        help="PDF page label to select (overrides index if found)",
    )
    p.add_argument(
        "--mat-pdf-toc-title",
        default=None,
        help="PDF TOC title to select (overrides index if found)",
    )
    p.add_argument(
        "--mat-pdf-dpi",
        type=int,
        default=300,
        help="DPI for PDF rasterization (default 300)",
    )
    p.add_argument(
        "--px-per-mm",
        type=float,
        default=2.0,
        help="View scaling; pixels per millimeter",
    )
    p.add_argument(
        "--exit-after",
        type=float,
        default=None,
        help="Auto-quit after N seconds (for testing)",
    )
    return p.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    app = QApplication([])

    # Resolve mat image and dimensions based on season
    repo_root = project_root
    _img, _w, _h, resolved_season = get_mat_for_season(
        repo_root, args.season
    )

    # Build/load map
    try:
        game_map = GameMap.load_season(resolved_season)
    except Exception as e:  # noqa: BLE001
        print(f"Warning: Failed to load season '{resolved_season}': {e}")
        print("Using default map instead.")
        game_map = GameMap()

    # Resolve mat image
    mat_arg: Optional[str] = args.mat_path
    mat_path = Path(mat_arg) if mat_arg else None
    if not mat_path and (args.mat_url or args.mat_pdf_url):
        # Cache under assets/mats/<season>/mat.png
        cache_dir = (
            project_root
            / "assets"
            / "mats"
            / (args.season or resolved_season)
        )
        cache_dir.mkdir(parents=True, exist_ok=True)
        mat_path = cache_dir / "mat.png"
        try:
            if args.mat_pdf_url:
                print(
                    f"Downloading mat PDF from {args.mat_pdf_url} "
                    f"(page={args.mat_pdf_page}, dpi={args.mat_pdf_dpi})..."
                )
                fetch_mat_pdf(
                    url=args.mat_pdf_url,
                    out_path=mat_path,
                    page=args.mat_pdf_page,
                    dpi=args.mat_pdf_dpi,
                    page_label=args.mat_pdf_page_label,
                    toc_title=args.mat_pdf_toc_title,
                )
            else:
                print(f"Downloading mat from {args.mat_url}...")
                fetch_mat_image(url=args.mat_url, out_path=mat_path)
            print(f"Mat cached to {mat_path}")
        except Exception as e:  # noqa: BLE001
            print(f"Warning: Failed to download mat: {e}")
            mat_path = None
    # If no explicit mat provided/downloaded, use latest available local mat
    if not mat_path and _img and _img.exists():
        mat_path = _img

    # Create view and window
    view = SimulatorView(
        game_map, mat_path=mat_path, px_per_mm=args.px_per_mm
    )
    window = MainWindow(view)
    window.show()

    # Auto-exit timer for testing
    if args.exit_after:
        QTimer.singleShot(int(args.exit_after * 1000), app.quit)

    print(f"FLL-Sim Enhanced GUI started for season: {resolved_season}")
    if mat_path and mat_path.exists():
        print(f"Using background mat: {mat_path}")
    else:
        print("Using procedural background (no mat image)")

    app.exec()


if __name__ == "__main__":
    main()
