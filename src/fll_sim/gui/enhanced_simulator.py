"""Enhanced FLL Simulator View with full GUI integration.

This module provides a simulator view with:
- Properly scaled background mat
- Correctly sized barriers (obstacles) rendered as rectangles
- Color zones rendered as rectangles
- Robot drawn with a correct arrow-like polygon (front tip) and
    correct point order
- A main window with menus, toolbar, tabs, and basic controls
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (QAction, QActionGroup, QBrush, QColor, QFont,
                         QPainter, QPen, QPolygonF)
from PyQt6.QtWidgets import (QCheckBox, QFileDialog, QFormLayout,
                             QGraphicsItem, QGraphicsPolygonItem,
                             QGraphicsRectItem, QGraphicsScene,
                             QGraphicsTextItem, QGraphicsView, QHBoxLayout,
                             QLabel, QListWidget, QListWidgetItem, QMainWindow,
                             QMenuBar, QMessageBox, QPushButton, QSpinBox,
                             QSplitter, QStatusBar, QTabWidget, QTextEdit,
                             QToolBar, QVBoxLayout, QWidget)

from ..environment.game_map import GameMap
from ..visualization.background import BackgroundConfig, BackgroundRenderer

# Colors
OBJECT_COLORS = {
    "robot": QColor(50, 150, 50),
    "obstacle": QColor(150, 75, 0),
    "waypoint": QColor(255, 100, 100),
}

# Standard sensor color mapping (fallbacks used if zone.color absent)
SENSOR_COLOR_MAP = {
    "red": QColor(255, 80, 80, 150),
    "blue": QColor(80, 80, 255, 150),
    "green": QColor(80, 200, 80, 150),
    "yellow": QColor(255, 230, 80, 150),
    "black": QColor(40, 40, 40, 150),
    "white": QColor(245, 245, 245, 150),
}


class RobotGraphicsItem(QGraphicsPolygonItem):
    """Robot drawn as an arrow-like polygon pointing up (-Y)."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        angle: float = 0,
    ):
        half_w = width / 2
        half_h = height / 2
        # Create arrow-like robot shape with front tip pointing up (-Y)
        # Points ordered clockwise starting from front tip
        poly = QPolygonF(
            [
                QPointF(0, -half_h - 15),  # front tip (pointing up)
                QPointF(half_w * 0.6, -half_h),  # right shoulder
                QPointF(half_w, -half_h * 0.3),  # right side
                QPointF(half_w, half_h),  # right back
                QPointF(-half_w, half_h),  # left back
                QPointF(-half_w, -half_h * 0.3),  # left side
                QPointF(-half_w * 0.6, -half_h),  # left shoulder
            ]
        )
        super().__init__(poly)
        self.setPos(x, y)
        self.setRotation(angle)
        self.setBrush(QBrush(OBJECT_COLORS["robot"]))
        self.setPen(QPen(QColor(0, 0, 0), 2))
        self.setZValue(100)

    def update_position(
        self, x: float, y: float, angle: Optional[float] = None
    ) -> None:
        self.setPos(x, y)
        if angle is not None:
            self.setRotation(angle)


class LegendWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMaximumWidth(220)
        layout = QVBoxLayout(self)
        title = QLabel("Map Legend")
        f = QFont()
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.list = QListWidget()
        layout.addWidget(self.list)
        for name, color in [
            ("Robot", OBJECT_COLORS["robot"]),
            ("Obstacle", OBJECT_COLORS["obstacle"]),
            ("Waypoint", OBJECT_COLORS["waypoint"]),
        ]:
            item = QListWidgetItem(name)
            item.setForeground(color)
            self.list.addItem(item)

        self.info = QLabel("Objects: 0")
        layout.addWidget(self.info)

    def update_object_count(self, n: int) -> None:
        self.info.setText(f"Objects: {n}")


class EnhancedSimulatorView(QGraphicsView):
    robot_moved = pyqtSignal(float, float, float)

    def __init__(
        self,
        game_map: GameMap,
        *,
        mat_path: Optional[Path] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._game_map = game_map
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._robot_item: Optional[RobotGraphicsItem] = None
        self._object_items: List[QGraphicsItem] = []
        self._path_items: List[QGraphicsItem] = []

        w_mm = game_map.config.width
        h_mm = game_map.config.height
        self._scene.setSceneRect(QRectF(0, 0, w_mm, h_mm))

        # Background
        bg_cfg = BackgroundConfig(width_mm=w_mm, height_mm=h_mm)
        self._background = BackgroundRenderer(config=bg_cfg)
        if mat_path:
            self._background.load_image(mat_path)
        self._bg_item = self._background.create_graphics_item()
        self._scene.addItem(self._bg_item)

        # Objects
        self._add_map_objects()
        self._add_robot()

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.fitInView(
            self._bg_item.boundingRect(),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def _add_map_objects(self) -> None:
        # Obstacles as rectangles centered at (x, y)
        for i, ob in enumerate(self._game_map.obstacles):
            w = float(ob.width)
            h = float(ob.height)
            rect = QGraphicsRectItem(-w / 2, -h / 2, w, h)
            rect.setPos(ob.x, ob.y)
            if getattr(ob, "angle", 0.0):
                rect.setRotation(ob.angle)
            rect.setBrush(QBrush(OBJECT_COLORS["obstacle"]))
            rect.setPen(QPen(QColor(0, 0, 0), 2))
            rect.setZValue(10)
            self._scene.addItem(rect)
            self._object_items.append(rect)

            lbl = QGraphicsTextItem(f"Obs {i+1}")
            lbl.setDefaultTextColor(QColor(0, 0, 0))
            lbl.setPos(ob.x - w / 2, ob.y - h / 2 - 18)
            lbl.setZValue(15)
            self._scene.addItem(lbl)
            self._object_items.append(lbl)

        # Color zones as rectangles centered at (x, y)
        for i, z in enumerate(self._game_map.color_zones):
            w = float(z.width)
            h = float(z.height)
            rect = QGraphicsRectItem(-w / 2, -h / 2, w, h)
            rect.setPos(z.x, z.y)
            if getattr(z, "angle", 0.0):
                rect.setRotation(z.angle)
            # prefer sensor_value mapping; else explicit color; else default
            sensor_key = getattr(z, "sensor_value", "") or ""
            qcol = SENSOR_COLOR_MAP.get(sensor_key, None)
            if qcol is None:
                col = getattr(z, "color", None)
                if isinstance(col, (list, tuple)) and 3 <= len(col) <= 4:
                    if len(col) == 3:
                        qcol = QColor(col[0], col[1], col[2])
                    else:
                        qcol = QColor(col[0], col[1], col[2], col[3])
                else:
                    qcol = QColor(100, 100, 255, 128)
            rect.setBrush(QBrush(qcol))
            rect.setPen(QPen(QColor(255, 255, 255), 2))
            rect.setZValue(5)
            self._scene.addItem(rect)
            self._object_items.append(rect)

            lbl = QGraphicsTextItem(f"Zone {i+1}")
            lbl.setDefaultTextColor(QColor(0, 0, 0))
            lbl.setPos(z.x - w / 2, z.y - h / 2 - 18)
            lbl.setZValue(15)
            self._scene.addItem(lbl)
            self._object_items.append(lbl)

        # Light grid, every 300mm
        pen = QPen(QColor(200, 200, 200, 100), 1, Qt.PenStyle.DashLine)
        total_w = int(self._game_map.config.width)
        total_h = int(self._game_map.config.height)
        for x in range(300, total_w, 300):
            self._scene.addLine(x, 0, x, total_h, pen)
        for y in range(300, total_h, 300):
            self._scene.addLine(0, y, total_w, y, pen)

    def _add_robot(self) -> None:
        x = self._game_map.config.width / 4
        y = self._game_map.config.height / 2
        self._robot_item = RobotGraphicsItem(x, y, 180, 200)
        self._scene.addItem(self._robot_item)

        lbl = QGraphicsTextItem("Robot")
        lbl.setDefaultTextColor(QColor(0, 100, 0))
        f = lbl.font()
        f.setBold(True)
        lbl.setFont(f)
        lbl.setPos(x - 20, y + 120)
        lbl.setZValue(105)
        self._scene.addItem(lbl)
        self._object_items.append(lbl)

    def update_robot_position(
        self, x: float, y: float, angle: float = 0
    ) -> None:
        if self._robot_item:
            self._robot_item.update_position(x, y, angle)
            self.robot_moved.emit(x, y, angle)

    def toggle_background_visibility(self, visible: bool) -> None:
        self._bg_item.setVisible(visible)

    def get_object_count(self) -> int:
        return len(self._object_items)

    def get_background_item(self) -> QGraphicsItem:
        """Return the background graphics item."""
        return self._bg_item

    def resizeEvent(self, event) -> None:
        """Handle window resize events."""
        super().resizeEvent(event)
        if self._bg_item is not None:
            self.fitInView(self._bg_item, Qt.AspectRatioMode.KeepAspectRatio)

    def set_scale_mode(self, mode: str) -> None:
        """Set background scale mode and refit view."""
        self._background.set_scale_mode(mode)
        if self._bg_item is not None:
            self.fitInView(self._bg_item, Qt.AspectRatioMode.KeepAspectRatio)


class FLLSimMainWindow(QMainWindow):
    def __init__(
        self, game_map: GameMap, mat_path: Optional[Path] = None
    ) -> None:
        super().__init__()
        self._game_map = game_map
        self._mat_path = mat_path

        self.setWindowTitle("FLL-Sim - Enhanced Simulator")
        self.resize(1400, 900)

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left: view + controls
        left = QWidget()
        left_layout = QVBoxLayout(left)

        # View controls
        controls = QHBoxLayout()
        self._bg_toggle = QCheckBox("Show Background")
        self._bg_toggle.setChecked(True)
        zoom_in = QPushButton("Zoom In")
        zoom_out = QPushButton("Zoom Out")
        fit_view = QPushButton("Fit View")
        controls.addWidget(self._bg_toggle)
        controls.addStretch(1)
        controls.addWidget(zoom_in)
        controls.addWidget(zoom_out)
        controls.addWidget(fit_view)

        self._view = EnhancedSimulatorView(
            self._game_map, mat_path=self._mat_path
        )
        left_layout.addLayout(controls)
        left_layout.addWidget(self._view)

        # Legend
        legend = LegendWidget()
        legend.update_object_count(self._view.get_object_count())

        splitter_left = QSplitter(Qt.Orientation.Horizontal)
        splitter_left.addWidget(left)
        splitter_left.addWidget(legend)
        splitter_left.setSizes([900, 250])

        # Right: tabs
        right = QWidget()
        right_layout = QVBoxLayout(right)
        tabs = QTabWidget()

        # Code tab
        code_tab = QWidget()
        code_layout = QVBoxLayout(code_tab)
        bar = QHBoxLayout()
        load_btn = QPushButton("Load Code")
        save_btn = QPushButton("Save Code")
        run_btn = QPushButton("Run Code")
        stop_btn = QPushButton("Stop")
        bar.addWidget(load_btn)
        bar.addWidget(save_btn)
        bar.addWidget(run_btn)
        bar.addWidget(stop_btn)
        bar.addStretch(1)
        code_layout.addLayout(bar)
        self._editor = QTextEdit()
        code_layout.addWidget(self._editor)
        tabs.addTab(code_tab, "Robot Code")

        # Robot config tab
        cfg_tab = QWidget()
        cfg_layout = QFormLayout(cfg_tab)
        self._robot_x = QSpinBox()
        self._robot_y = QSpinBox()
        self._robot_angle = QSpinBox()
        self._robot_x.setRange(0, int(self._game_map.config.width))
        self._robot_y.setRange(0, int(self._game_map.config.height))
        self._robot_angle.setRange(-180, 180)
        self._robot_x.setValue(int(self._game_map.config.width / 4))
        self._robot_y.setValue(int(self._game_map.config.height / 2))
        self._robot_angle.setValue(0)
        cfg_layout.addRow("Robot X (mm)", self._robot_x)
        cfg_layout.addRow("Robot Y (mm)", self._robot_y)
        cfg_layout.addRow("Angle (deg)", self._robot_angle)
        tabs.addTab(cfg_tab, "Robot Config")

        # Output tab
        out_tab = QWidget()
        out_layout = QVBoxLayout(out_tab)
        out_layout.addWidget(QLabel("Simulation Output:"))
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setMaximumHeight(220)
        out_layout.addWidget(self._output)
        tabs.addTab(out_tab, "Output")

        right_layout.addWidget(tabs)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(splitter_left)
        splitter.addWidget(right)
        splitter.setSizes([1000, 400])

        layout.addWidget(splitter)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

        # Menu and toolbar
        self._build_menu()
        self._build_toolbar()

        # Wiring
        self._bg_toggle.toggled.connect(
            self._view.toggle_background_visibility
        )
        zoom_in.clicked.connect(lambda: self._view.scale(1.2, 1.2))
        zoom_out.clicked.connect(lambda: self._view.scale(0.8, 0.8))
        fit_view.clicked.connect(
            lambda: self._view.fitInView(
                self._view.get_background_item(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        )
        load_btn.clicked.connect(self._load_code)
        save_btn.clicked.connect(self._save_code)
        run_btn.clicked.connect(self._run_code)
        stop_btn.clicked.connect(self._stop_code)
        self._robot_x.valueChanged.connect(
            lambda v: self._view.update_robot_position(
                v, self._robot_y.value(), self._robot_angle.value()
            )
        )
        self._robot_y.valueChanged.connect(
            lambda v: self._view.update_robot_position(
                self._robot_x.value(), v, self._robot_angle.value()
            )
        )
        self._robot_angle.valueChanged.connect(
            lambda v: self._view.update_robot_position(
                self._robot_x.value(), self._robot_y.value(), v
            )
        )

    def _build_menu(self) -> None:
        m = self.menuBar()
        if m is None:
            m = QMenuBar(self)
            self.setMenuBar(m)
        file_menu = m.addMenu("&File")
        if file_menu is None:
            return
        act_new = QAction("&New Program", self)
        act_new.triggered.connect(self._new_program)
        file_menu.addAction(act_new)
        act_load = QAction("&Load Program", self)
        act_load.triggered.connect(self._load_code)
        file_menu.addAction(act_load)
        act_save = QAction("&Save Program", self)
        act_save.triggered.connect(self._save_code)
        file_menu.addAction(act_save)
        file_menu.addSeparator()
        act_quit = QAction("E&xit", self)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        view_menu = m.addMenu("&View")
        if view_menu is None:
            return
        act_fit = QAction("&Fit to View", self)
        act_fit.triggered.connect(
            lambda: self._view.fitInView(
                self._view.get_background_item(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        )
        view_menu.addAction(act_fit)
        view_menu.addSeparator()

        # Scale mode actions with exclusive checkable group
        scale_group = QActionGroup(self)
        scale_group.setExclusive(True)

        self._scale_cover = QAction("Scale: &Cover", self)
        self._scale_cover.setCheckable(True)
        self._scale_cover.setChecked(True)  # Default mode
        self._scale_cover.triggered.connect(
            lambda: self._set_scale_mode("cover")
        )
        scale_group.addAction(self._scale_cover)
        view_menu.addAction(self._scale_cover)

        self._scale_contain = QAction("Scale: Co&ntain", self)
        self._scale_contain.setCheckable(True)
        self._scale_contain.triggered.connect(
            lambda: self._set_scale_mode("contain")
        )
        scale_group.addAction(self._scale_contain)
        view_menu.addAction(self._scale_contain)

        self._scale_stretch = QAction("Scale: &Stretch", self)
        self._scale_stretch.setCheckable(True)
        self._scale_stretch.triggered.connect(
            lambda: self._set_scale_mode("stretch")
        )
        scale_group.addAction(self._scale_stretch)
        view_menu.addAction(self._scale_stretch)

        help_menu = m.addMenu("&Help")
        if help_menu is None:
            return
        act_about = QAction("&About", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main")
        self.addToolBar(tb)
        act_reset = QAction("Reset Robot", self)
        act_reset.triggered.connect(self._reset_robot)
        tb.addAction(act_reset)

    # Actions
    def _new_program(self) -> None:
        self._editor.setPlainText(
            "# New Robot Program\nprint('Hello, FLL!')\n"
        )

    def _load_code(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Robot Code", "", "Python Files (*.py);;All Files (*)"
        )
        if path:
            try:
                self._editor.setPlainText(
                    Path(path).read_text(encoding="utf-8")
                )
                self.status.showMessage(f"Loaded: {path}")
            except (OSError, UnicodeDecodeError) as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to load code: {e}"
                )

    def _save_code(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Robot Code",
            "robot_program.py",
            "Python Files (*.py);;All Files (*)",
        )
        if path:
            try:
                Path(path).write_text(
                    self._editor.toPlainText(), encoding="utf-8"
                )
                self.status.showMessage(f"Saved: {path}")
            except OSError as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to save code: {e}"
                )

    def _run_code(self) -> None:
        self._output.append(">>> Running robot program...")
        self.status.showMessage("Running robot code…")
        self._output.append("Program execution completed.")

    def _stop_code(self) -> None:
        self._output.append(">>> Execution stopped by user")
        self.status.showMessage("Code execution stopped")

    def _reset_robot(self) -> None:
        x = int(self._game_map.config.width / 4)
        y = int(self._game_map.config.height / 2)
        self._robot_x.setValue(x)
        self._robot_y.setValue(y)
        self._robot_angle.setValue(0)
        self._view.update_robot_position(x, y, 0)
        self.status.showMessage("Robot reset")

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About FLL-Sim",
            "FLL-Sim Enhanced Simulator\n\n"
            "Robot visualization with correct arrow shape, and obstacles\n"
            "rendered as rectangles with accurate sizing.",
        )

    def _set_scale_mode(self, mode: str) -> None:
        """Set the background scale mode and update the status."""
        self._view.set_scale_mode(mode)
        self.status.showMessage(f"Scale mode set to: {mode}")

