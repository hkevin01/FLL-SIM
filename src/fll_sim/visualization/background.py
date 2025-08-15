"""FLL Simulator Background Rendering

Provides background image and procedural rendering for the simulator GUI.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem


@dataclass
class BackgroundConfig:
    """Configuration for background rendering."""
    # Physical dimensions (mm)
    width_mm: float = 2400.0
    height_mm: float = 1200.0

    # Visual properties
    background_color: QColor = field(
        default_factory=lambda: QColor(240, 240, 240)
    )  # Light gray
    border_color: QColor = field(
        default_factory=lambda: QColor(20, 20, 20)
    )  # Dark gray
    border_width: int = 3

    # Mission area grid
    grid_size_mm: float = 300.0  # 30cm squares
    grid_color: QColor = field(
        default_factory=lambda: QColor(200, 200, 200)
    )
    grid_width: int = 1

    # Home base area (mm from edge)
    home_base_width_mm: float = 600.0  # 60cm
    home_base_color: QColor = field(
        default_factory=lambda: QColor(180, 220, 180)
    )  # Light green


class BackgroundRenderer:
    """Renders FLL table backgrounds for the simulator."""

    def __init__(self, config: Optional[BackgroundConfig] = None):
        """Initialize background renderer.

        Args:
            config: Background configuration. Uses defaults if None.
        """
        self._cfg = config or BackgroundConfig()
        self._pixmap: Optional[QPixmap] = None
        self._graphics_item: Optional[QGraphicsPixmapItem] = None

    def load_image(self, image_path: Path) -> bool:
        """Load background image from file.

        Args:
            image_path: Path to image file (PNG, JPG, etc.)

        Returns:
            True if image loaded successfully, False otherwise.
        """
        if not image_path.exists():
            return False

        image = QImage(str(image_path))
        if image.isNull():
            return False

        # Scale image to maintain aspect ratio within config dimensions
        pixmap = QPixmap.fromImage(image)
        self._pixmap = self._scale_image_to_fit(pixmap)
        return True

    def _scale_image_to_fit(self, pixmap: QPixmap) -> QPixmap:
        """Scale pixmap to fit within config dimensions maintaining aspect."""
        target_w = int(self._cfg.width_mm)
        target_h = int(self._cfg.height_mm)

        # Calculate scaling to fit within target while maintaining aspect
        scale_w = target_w / pixmap.width()
        scale_h = target_h / pixmap.height()
        scale = min(scale_w, scale_h)

        new_w = int(pixmap.width() * scale)
        new_h = int(pixmap.height() * scale)

        return pixmap.scaled(
            new_w, new_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def create_graphics_item(self) -> QGraphicsPixmapItem:
        """Create QGraphicsPixmapItem for the background.

        Returns:
            Graphics item ready to add to scene.
        """
        if self._pixmap is None:
            # Create procedural background if no image loaded
            self._pixmap = self._create_procedural_background()

        item = QGraphicsPixmapItem(self._pixmap)
        item.setZValue(-1000)  # Behind everything else

        # Center the image in the coordinate system
        item.setOffset(
            -self._pixmap.width() / 2,
            -self._pixmap.height() / 2
        )

        self._graphics_item = item
        return item

    def _create_procedural_background(self) -> QPixmap:
        """Create procedural FLL table background."""
        # Create pixmap with config dimensions
        w = int(self._cfg.width_mm)
        h = int(self._cfg.height_mm)
        pixmap = QPixmap(w, h)
        pixmap.fill(self._cfg.background_color)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw border
        pen = QPen(self._cfg.border_color, self._cfg.border_width)
        painter.setPen(pen)
        painter.drawRect(0, 0, w - 1, h - 1)

        # Draw mission grid
        self._draw_mission_grid(painter, w, h)

        # Draw home base areas
        self._draw_home_bases(painter, w, h)

        painter.end()
        return pixmap

    def _draw_mission_grid(self, painter: QPainter, w: int, h: int) -> None:
        """Draw mission area grid."""
        pen = QPen(self._cfg.grid_color, self._cfg.grid_width)
        painter.setPen(pen)

        grid_size = int(self._cfg.grid_size_mm)

        # Vertical lines
        x = grid_size
        while x < w:
            painter.drawLine(x, 0, x, h)
            x += grid_size

        # Horizontal lines
        y = grid_size
        while y < h:
            painter.drawLine(0, y, w, y)
            y += grid_size

    def _draw_home_bases(self, painter: QPainter, w: int, h: int) -> None:
        """Draw home base areas."""
        base_width = int(self._cfg.home_base_width_mm)

        # Left home base
        painter.fillRect(0, 0, base_width, h, self._cfg.home_base_color)

        # Right home base
        painter.fillRect(
            w - base_width,
            0,
            base_width,
            h,
            self._cfg.home_base_color,
        )

    def toggle_visibility(self) -> None:
        """Toggle background visibility."""
        if self._graphics_item:
            visible = self._graphics_item.isVisible()
            self._graphics_item.setVisible(not visible)

    def set_visible(self, visible: bool) -> None:
        """Set background visibility."""
        if self._graphics_item:
            self._graphics_item.setVisible(visible)

    def get_graphics_item(self) -> Optional[QGraphicsPixmapItem]:
        """Get the current graphics item."""
        return self._graphics_item
