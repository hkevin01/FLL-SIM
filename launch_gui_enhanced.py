#!/usr/bin/env python3
"""Enhanced FLL-Sim GUI Launcher with integrated controls

Launches the enhanced FLL simulator with full GUI integration including:
- Robot visualization and control
- Code editor with syntax highlighting
- Mission management
- Real-time simulation output
- Background mat support
"""

import argparse
import os
import sys
from pathlib import Path

# Add project src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from fll_sim.assets.mats import get_mat_for_season
# FLL-Sim imports
from fll_sim.environment.game_map import GameMap
from fll_sim.gui.enhanced_simulator import FLLSimMainWindow
from fll_sim.scripts.fetch_mat import fetch_mat_image, fetch_mat_pdf


def main() -> None:
    """Launch the enhanced FLL-Sim GUI."""
    parser = argparse.ArgumentParser(
        description="FLL-Sim Enhanced GUI with integrated controls"
    )

    # Season and mat options
    parser.add_argument(
        "--season",
        default="latest",
        help="FLL season (e.g., '2024-submerged', 'latest')"
    )
    parser.add_argument(
        "--mat-path",
        type=Path,
        help="Path to mat image file"
    )
    parser.add_argument(
        "--mat-url",
        help="URL to download mat image from"
    )
    parser.add_argument(
        "--mat-pdf-url",
        help="URL to download mat PDF from"
    )
    parser.add_argument(
        "--mat-pdf-page",
        type=int,
        default=0,
        help="PDF page number to use (0-based)"
    )
    parser.add_argument(
        "--mat-pdf-dpi",
        type=int,
        default=300,
        help="DPI for PDF rasterization"
    )
    parser.add_argument(
        "--mat-pdf-page-label",
        help="PDF page label to find (e.g., 'Table')"
    )
    parser.add_argument(
        "--mat-pdf-toc-title",
        help="PDF table of contents title to find"
    )

    # GUI options
    parser.add_argument(
        "--exit-after",
        type=float,
        help="Exit after N seconds (for testing)"
    )

    args = parser.parse_args()

    # Set up headless mode if no display
    if os.environ.get("FLL_SIM_HEADLESS") == "1":
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    app = QApplication(sys.argv)
    app.setApplicationName("FLL-Sim Enhanced")
    app.setApplicationVersion("2.0")

    print("FLL-Sim Enhanced GUI started for season:", args.season)

    # Resolve season and mat
    mat_path = None

    if args.mat_path:
        mat_path = args.mat_path
        print(f"Using specified mat: {mat_path}")
    elif args.mat_url or args.mat_pdf_url:
        # Download mat to cache
        assets_dir = project_root / "assets" / "mats" / args.season
        assets_dir.mkdir(parents=True, exist_ok=True)
        cache_path = assets_dir / "mat.png"

        try:
            if args.mat_pdf_url:
                print(f"Downloading mat PDF from {args.mat_pdf_url}...")
                print(
                    f"  (page={args.mat_pdf_page}, dpi={args.mat_pdf_dpi})"
                )
                fetch_mat_pdf(
                    args.mat_pdf_url,
                    cache_path,
                    page=args.mat_pdf_page,
                    dpi=args.mat_pdf_dpi,
                    page_label=args.mat_pdf_page_label,
                    toc_title=args.mat_pdf_toc_title,
                )
            else:
                print(f"Downloading mat image from {args.mat_url}...")
                fetch_mat_image(args.mat_url, cache_path)

            mat_path = cache_path
            print(f"Mat cached to {cache_path}")
        except Exception as e:
            print(f"Failed to download mat: {e}")
    else:
        # Try to find local mat
        local_mat, width_mm, height_mm, resolved_season = get_mat_for_season(
            project_root, args.season
        )
        if local_mat:
            mat_path = local_mat
            print(f"Using background mat: {mat_path}")
        else:
            print(f"No mat found for season {args.season}")

    # Create game map with reasonable defaults
    from fll_sim.environment.game_map import ColorZone, MapConfig, Obstacle

    map_config = MapConfig(
        width=2400,  # 2.4m standard FLL table
        height=1200,  # 1.2m standard FLL table
        border_thickness=50
    )

    # Create game map with config
    game_map = GameMap(config=map_config)

    # Add some sample obstacles and zones for demonstration
    obstacles = [
        Obstacle(
            name="Sample Obstacle 1",
            x=600, y=300, width=25, height=25,
            color=(150, 75, 0)
        ),
        Obstacle(
            name="Sample Obstacle 2",
            x=1800, y=900, width=30, height=20,
            color=(100, 50, 25)
        ),
    ]

    color_zones = [
        ColorZone(
            name="Red Zone",
            x=300, y=600, width=200, height=200,
            color=(255, 100, 100), sensor_value="red"
        ),
        ColorZone(
            name="Blue Zone",
            x=2100, y=600, width=200, height=200,
            color=(100, 100, 255), sensor_value="blue"
        ),
        ColorZone(
            name="Green Zone",
            x=1200, y=300, width=300, height=150,
            color=(100, 255, 100), sensor_value="green"
        ),
    ]

    # Add elements to map
    for obstacle in obstacles:
        game_map.add_obstacle(obstacle)

    for zone in color_zones:
        game_map.add_color_zone(zone)

    # Create and show main window
    main_window = FLLSimMainWindow(game_map, mat_path=mat_path)
    main_window.show()

    # Auto-exit timer for testing
    if args.exit_after:
        QTimer.singleShot(int(args.exit_after * 1000), app.quit)

    # Run application
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
    main()
