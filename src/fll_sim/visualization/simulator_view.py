# src/fll_sim/visualization/simulator_view.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsScene, QGraphicsView

from ..environment.game_map import GameMap
from .background import BackgroundConfig, BackgroundRenderer


class SimulatorView(QGraphicsView):
    """
    A QGraphicsView for displaying the FLL-Sim game map with background
    support.

    Features:
    - Background mat image support (scaled to physical size)
    - Procedural fallback background
    - Real-world coordinate system (millimeters)
    - Proper scaling and fit-to-view behavior
    """

    def __init__(
        self,
        game_map: GameMap,
        *,
        mat_path: Optional[Path] = None,
        px_per_mm: float = 2.0,
        parent=None
    ):
        super().__init__(parent)
        self._px_per_mm = px_per_mm
        self._game_map = game_map

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Scene units are mm - get dimensions from map config
        w_mm = game_map.config.width
        h_mm = game_map.config.height
        self._scene.setSceneRect(QRectF(0, 0, w_mm, h_mm))

        # Background renderer
        bg_cfg = BackgroundConfig(width_mm=w_mm, height_mm=h_mm)
        self._background = BackgroundRenderer(config=bg_cfg)

        # Load image if provided
        if mat_path:
            self._background.load_image(mat_path)

        # Add background to scene
        bg_item = self._background.create_graphics_item()
        self._scene.addItem(bg_item)

        # Add map elements (obstacles, color zones, etc.)
        self._add_map_elements()

        # Configure view settings
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Fit the whole mat in view initially
        self.fitInView(
            self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    def _add_map_elements(self) -> None:
        """Add obstacles, color zones, and other map elements to the scene."""
        # Add obstacles
        for obstacle in self._game_map.obstacles:
            rect_item = QGraphicsEllipseItem(
                obstacle.x - obstacle.width/2,
                obstacle.y - obstacle.height/2,
                obstacle.width,
                obstacle.height
            )
            rect_item.setBrush(QBrush(QColor(*obstacle.color)))
            rect_item.setZValue(10)  # Above background
            self._scene.addItem(rect_item)

        # Add color zones
        for zone in self._game_map.color_zones:
            zone_item = QGraphicsEllipseItem(
                zone.x - zone.width/2,
                zone.y - zone.height/2,
                zone.width,
                zone.height
            )
            # Semi-transparent
            zone_item.setBrush(QBrush(QColor(*zone.color, 128)))
            zone_item.setZValue(5)  # Above background, below obstacles
            self._scene.addItem(zone_item)

    def toggle_background_visibility(self, visible: bool) -> None:
        """Toggle visibility of the background mat/grid."""
        self._background.set_visible(visible)

    def resizeEvent(self, event):
        """Keep the whole mat visible on resize."""
        super().resizeEvent(event)
        # Keep the whole mat visible
        self.fitInView(
            self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    def get_background_renderer(self) -> BackgroundRenderer:
        """Access to the background renderer for additional configuration."""
        return self._background
