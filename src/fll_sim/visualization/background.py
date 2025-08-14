# src/fll_sim/visualization/background.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import (
    QGraphicsPixmapItem, QGraphicsItemGroup, QGraphicsRectItem
)


@dataclass
class BackgroundConfig:
    """Configuration for map background rendering."""
    # Physical size of the mat in millimeters (FLL table/mat is typically
    # 2362 x 1143 mm, adjust per season if needed)
    width_mm: float
    height_mm: float
    # Optional: grayscale alpha of procedural grid, 0 disables
    grid_mm: float = 150.0
    grid_alpha: int = 32
    border_thickness_mm: float = 70.0
    # x,y,w,h for a "home/base" area in mm
    base_zone_mm: Tuple[float, float, float, float] = (0, 0, 450, 450)
    background_color: QColor = QColor(245, 245, 245)
    border_color: QColor = QColor(20, 20, 20)
    grid_color: QColor = QColor(0, 0, 0, 32)


class BackgroundRenderer:
    """
    Renders a background for the GameMap into a QGraphicsScene.

    - If an image is available, it is scaled to [width_mm, height_mm]
      in scene units (mm).
    - Otherwise, draws a procedural FLL-style table with border, base zone,
      and subtle grid.
    """

    def __init__(
        self,
        px_per_mm: float,
        cfg: BackgroundConfig,
        image_path: Optional[Path] = None,
    ) -> None:
        self._px_per_mm = float(px_per_mm)
        self._cfg = cfg
        self._image_path = Path(image_path) if image_path else None

        # Group to hold background items; negative Z so it stays behind
        # everything.
        self.group = QGraphicsItemGroup()
        self.group.setZValue(-1000)

        # Build background once
        self._build()

    @property
    def item(self) -> QGraphicsItemGroup:
        return self.group

    def _build(self) -> None:
        # Scene rect in mm
        rect_mm = QRectF(0, 0, self._cfg.width_mm, self._cfg.height_mm)

        # Try image first
        if self._image_path and self._image_path.exists():
            pix_item = self._build_image_background(rect_mm, self._image_path)
            if pix_item:
                self.group.addToGroup(pix_item)
                return  # done

        # Fallback: procedural
        self._build_procedural_background(rect_mm)

    def _build_image_background(
        self, rect_mm: QRectF, path: Path
    ) -> Optional[QGraphicsPixmapItem]:
        img = QImage(str(path))
        if img.isNull():
            return None

        # Create a pixmap sized to mm->px scaling
        target_px_w = max(1, int(round(rect_mm.width() * self._px_per_mm)))
        target_px_h = max(1, int(round(rect_mm.height() * self._px_per_mm)))
        pix = QPixmap(target_px_w, target_px_h)
        pix.fill(Qt.GlobalColor.transparent)

        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        # Draw scaled with aspect fit, then center on target canvas
        img_scaled = img.scaled(
            target_px_w, target_px_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        x = (target_px_w - img_scaled.width()) // 2
        y = (target_px_h - img_scaled.height()) // 2
        p.drawImage(x, y, img_scaled)
        p.end()

        item = QGraphicsPixmapItem(pix)
        # Place at (0,0) in mm; scale item so 1 scene unit == 1 mm
        item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        # Convert px into scene mm by scaling
        # The pixmap currently has pixel dimensions, but our scene uses
        # mm units; so set scale so that pixmap pixel -> mm:
        # 1px -> 1/self._px_per_mm mm.
        scale = 1.0 / self._px_per_mm
        item.setScale(scale)
        item.setOffset(0, 0)
        item.setZValue(-1000)
        return item

    def _build_procedural_background(self, rect_mm: QRectF) -> None:
        # Base fill
        base = QGraphicsRectItem(rect_mm)
        base.setBrush(QBrush(self._cfg.background_color))
        base.setPen(QPen(Qt.PenStyle.NoPen))
        base.setZValue(-1000)
        self.group.addToGroup(base)

        # Border (table wall)
        if self._cfg.border_thickness_mm > 0:
            t = self._cfg.border_thickness_mm
            # Outer rect for visual wall; draw as 4 rects for clarity
            w = rect_mm.width()
            h = rect_mm.height()
            walls = [
                QRectF(0, 0, w, t),             # top
                QRectF(0, h - t, w, t),         # bottom
                QRectF(0, 0, t, h),             # left
                QRectF(w - t, 0, t, h),         # right
            ]
            for r in walls:
                wall = QGraphicsRectItem(r)
                wall.setBrush(QBrush(self._cfg.border_color))
                wall.setPen(QPen(Qt.PenStyle.NoPen))
                wall.setZValue(-999)
                self.group.addToGroup(wall)

        # Grid
        if self._cfg.grid_mm and self._cfg.grid_alpha > 0:
            step = self._cfg.grid_mm
            x = step
            while x < rect_mm.width():
                line = QGraphicsRectItem(QRectF(x, 0, 0.5, rect_mm.height()))
                line.setPen(QPen(Qt.PenStyle.NoPen))
                line.setBrush(QBrush(self._cfg.grid_color))
                line.setZValue(-998)
                self.group.addToGroup(line)
                x += step
            y = step
            while y < rect_mm.height():
                line = QGraphicsRectItem(QRectF(0, y, rect_mm.width(), 0.5))
                line.setPen(QPen(Qt.PenStyle.NoPen))
                line.setBrush(QBrush(self._cfg.grid_color))
                line.setZValue(-998)
                self.group.addToGroup(line)
                y += step

        # Base/home zone
        bx, by, bw, bh = self._cfg.base_zone_mm
        base_zone = QGraphicsRectItem(QRectF(bx, by, bw, bh))
        base_zone.setBrush(QBrush(QColor(200, 230, 255)))
        base_zone.setPen(QPen(QColor(80, 120, 180), 2))
        base_zone.setZValue(-997)
        self.group.addToGroup(base_zone)
