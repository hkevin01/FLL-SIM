"""Enhanced FLL Simulator View with full GUI integration

Provides a comprehensive simulator view with robot display, legends,
improved object visualization, and coding controls.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (QAction, QBrush, QColor, QFont, QIcon, QPainter, QPen,
                         QPixmap, QPolygonF)
from PyQt6.QtWidgets import (QCheckBox, QFileDialog, QGraphicsEllipseItem,
                             QGraphicsItem, QGraphicsPolygonItem,
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView,
                             QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QMainWindow, QMessageBox, QPushButton, QSplitter,
                             QStatusBar, QTabWidget, QTextEdit, QToolBar,
                             QVBoxLayout, QWidget)

from ..environment.game_map import GameMap
from ..visualization.background import BackgroundConfig, BackgroundRenderer

# Default colors for different object types
OBJECT_COLORS = {
    'robot': QColor(50, 150, 50),        # Green
    'obstacle': QColor(150, 75, 0),       # Brown
    'color_zone_red': QColor(255, 100, 100, 128),     # Red zone
    'color_zone_blue': QColor(100, 100, 255, 128),    # Blue zone
    'color_zone_yellow': QColor(255, 255, 100, 128),  # Yellow zone
    'color_zone_green': QColor(100, 255, 100, 128),   # Green zone
    'mission_area': QColor(0, 255, 0, 100),           # Mission area
    'mission_complete': QColor(0, 200, 0, 150),       # Completed mission
    'path': QColor(255, 255, 0),         # Robot path
    'waypoint': QColor(255, 100, 100),   # Waypoints
}


class RobotGraphicsItem(QGraphicsPolygonItem):
    """Graphics item representing the robot on the map."""

    def __init__(
        self, x: float, y: float, width: float, height: float, angle: float = 0
    ):
        """Initialize robot graphics item.

        Args:
            x, y: Position in mm
            width, height: Robot dimensions in mm
            angle: Rotation angle in degrees
        """
        # Create robot polygon (rectangle with direction indicator)
        # Main robot body (rectangle) + direction triangle
        half_width = width / 2
        half_height = height / 2

        polygon = QPolygonF([
            # Main rectangle body
            QPointF(-half_width, -half_height),     # Top-left
            QPointF(half_width, -half_height),      # Top-right
            QPointF(half_width, half_height),       # Bottom-right
            QPointF(-half_width, half_height),      # Bottom-left
            # Close to start point
            QPointF(-half_width, -half_height),
        ])

        super().__init__(polygon)

        self.setPos(x, y)
        self.setRotation(angle)
        self.setBrush(QBrush(OBJECT_COLORS['robot']))
        self.setPen(QPen(QColor(0, 0, 0), 2))
        self.setZValue(100)  # Above everything else

        # Robot properties
        self._width = width
        self._height = height

        # Add direction indicator (arrow)
        self._direction_indicator = QGraphicsPolygonItem()
        arrow_size = 10
        arrow_polygon = QPolygonF([
            QPointF(0, -half_height - arrow_size),      # Arrow tip
            QPointF(-arrow_size/2, -half_height),       # Left wing
            QPointF(arrow_size/2, -half_height),        # Right wing
        ])
        self._direction_indicator.setPolygon(arrow_polygon)
        self._direction_indicator.setBrush(QBrush(QColor(255, 255, 0)))  # Yellow
        self._direction_indicator.setPen(QPen(QColor(0, 0, 0), 1))
        self._direction_indicator.setParentItem(self)
        self._direction_indicator.setZValue(101)

    def update_position(self, x: float, y: float, angle: float = None):
        """Update robot position and rotation."""
        self.setPos(x, y)
        if angle is not None:
            self.setRotation(angle)


class LegendWidget(QWidget):
    """Widget displaying map legend and object information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(200)
        self.setMinimumWidth(150)

        layout = QVBoxLayout(self)

        # Legend title
        title = QLabel("Map Legend")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Legend items
        self._legend_list = QListWidget()
        layout.addWidget(self._legend_list)

        # Object count info
        self._info_label = QLabel("Objects: 0")
        layout.addWidget(self._info_label)

        self._setup_legend()

    def _setup_legend(self):
        """Setup legend items."""
        legend_items = [
            ("Robot", OBJECT_COLORS['robot']),
            ("Obstacles", OBJECT_COLORS['obstacle']),
            ("Red Zone", OBJECT_COLORS['color_zone_red']),
            ("Blue Zone", OBJECT_COLORS['color_zone_blue']),
            ("Yellow Zone", OBJECT_COLORS['color_zone_yellow']),
            ("Green Zone", OBJECT_COLORS['color_zone_green']),
            ("Mission Area", OBJECT_COLORS['mission_area']),
            ("Completed Mission", OBJECT_COLORS['mission_complete']),
            ("Robot Path", OBJECT_COLORS['path']),
            ("Waypoints", OBJECT_COLORS['waypoint']),
        ]

        for name, color in legend_items:
            item = QListWidgetItem(name)

            # Create color indicator pixmap
            pixmap = QPixmap(16, 16)
            pixmap.fill(color)
            item.setIcon(QIcon(pixmap))

            self._legend_list.addItem(item)

    def update_object_count(self, count: int):
        """Update object count display."""
        self._info_label.setText(f"Objects: {count}")


class CodeEditor(QTextEdit):
    """Simple code editor for robot programming."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up font and styling
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Monaco", 10)
        if not font.exactMatch():
            font = QFont("monospace", 10)

        self.setFont(font)

        # Default code template
        self.setPlainText("""# FLL Robot Code
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Direction
from pybricks.robotics import DriveBase

# Initialize the hub and motors
hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)

# Initialize the drive base
drive_base = DriveBase(
    left_motor, right_motor, wheel_diameter=56, axle_track=114
)

# Main program
def main():
    print("Starting FLL Robot Program...")

    # Move forward 500mm
    drive_base.straight(500)

    # Turn 90 degrees
    drive_base.turn(90)

    # Move forward again
    drive_base.straight(300)

    print("Program completed!")

if __name__ == "__main__":
    main()
""")


class EnhancedSimulatorView(QGraphicsView):
    """Enhanced simulator view with robot display and improved viz."""

    # Signals
    robot_moved = pyqtSignal(float, float, float)  # x, y, angle
    object_clicked = pyqtSignal(str, dict)  # object_type, properties

    def __init__(
        self,
        game_map: GameMap,
        *,
        mat_path: Optional[Path] = None,
        parent=None
    ):
        super().__init__(parent)
        self._game_map = game_map
        self._robot_item: Optional[RobotGraphicsItem] = None
        self._path_items: List[QGraphicsItem] = []
        self._object_items: List[QGraphicsItem] = []

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

        # Add map elements with improved visualization
        self._add_enhanced_map_elements()

        # Add robot
        self._add_robot()

        # Configure view settings
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Fit the whole mat in view initially
        if bg_item is not None:
            self.fitInView(
                bg_item.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio
            )

    def _add_enhanced_map_elements(self) -> None:
        """Add map elements with enhanced visualization and labels."""
        object_count = 0

        # Add obstacles with labels
        for i, obstacle in enumerate(self._game_map.obstacles):
            # Main obstacle shape
            item = QGraphicsEllipseItem(
                obstacle.x - obstacle.width/2,
                obstacle.y - obstacle.height/2,
                obstacle.width,
                obstacle.height
            )
            item.setBrush(QBrush(OBJECT_COLORS['obstacle']))
            item.setPen(QPen(QColor(0, 0, 0), 2))
            item.setZValue(10)
            self._scene.addItem(item)
            self._object_items.append(item)

            # Label
            label = QGraphicsTextItem(f"Obs {i+1}")
            label.setPos(obstacle.x - 15, obstacle.y - 30)
            label.setZValue(15)
            label.setDefaultTextColor(QColor(0, 0, 0))
            self._scene.addItem(label)
            self._object_items.append(label)

            object_count += 1

        # Add color zones with enhanced visualization
        for i, zone in enumerate(self._game_map.color_zones):
            # Determine zone color based on actual color or index
            zone_color = OBJECT_COLORS.get(f'color_zone_{zone.color}',
                                         list(OBJECT_COLORS.values())[i % 4 + 2])

            item = QGraphicsEllipseItem(
                zone.x - zone.width/2,
                zone.y - zone.height/2,
                zone.width,
                zone.height
            )
            item.setBrush(QBrush(zone_color))
            item.setPen(QPen(QColor(255, 255, 255), 2))
            item.setZValue(5)
            self._scene.addItem(item)
            self._object_items.append(item)

            # Label
            label = QGraphicsTextItem(f"Zone {i+1}")
            label.setPos(zone.x - 20, zone.y - 10)
            label.setZValue(15)
            label.setDefaultTextColor(QColor(255, 255, 255))
            font = label.font()
            font.setBold(True)
            label.setFont(font)
            self._scene.addItem(label)
            self._object_items.append(label)

            object_count += 1

        # Add coordinate grid lines
        self._add_coordinate_grid()

        return object_count

    def _add_coordinate_grid(self):
        """Add coordinate grid lines for reference."""
        w_mm = self._game_map.config.width
        h_mm = self._game_map.config.height

        grid_pen = QPen(QColor(200, 200, 200, 100), 1, Qt.PenStyle.DashLine)

        # Vertical lines every 300mm
        for x in range(300, int(w_mm), 300):
            line = self._scene.addLine(x, 0, x, h_mm, grid_pen)
            line.setZValue(-10)

            # Add coordinate label
            label = QGraphicsTextItem(f"{x}")
            label.setPos(x - 10, 10)
            label.setZValue(-5)
            label.setDefaultTextColor(QColor(150, 150, 150))
            self._scene.addItem(label)

        # Horizontal lines every 300mm
        for y in range(300, int(h_mm), 300):
            line = self._scene.addLine(0, y, w_mm, y, grid_pen)
            line.setZValue(-10)

            # Add coordinate label
            label = QGraphicsTextItem(f"{y}")
            label.setPos(10, y - 15)
            label.setZValue(-5)
            label.setDefaultTextColor(QColor(150, 150, 150))
            self._scene.addItem(label)

    def _add_robot(self):
        """Add robot to the scene."""
        # Default robot position and size
        robot_x = self._game_map.config.width / 4  # Start position
        robot_y = self._game_map.config.height / 2
        robot_width = 180  # 18cm
        robot_height = 200  # 20cm

        self._robot_item = RobotGraphicsItem(
            robot_x, robot_y, robot_width, robot_height
        )
        self._scene.addItem(self._robot_item)

        # Add robot label
        robot_label = QGraphicsTextItem("Robot")
        robot_label.setPos(robot_x - 15, robot_y + robot_height/2 + 10)
        robot_label.setZValue(105)
        robot_label.setDefaultTextColor(QColor(0, 100, 0))
        font = robot_label.font()
        font.setBold(True)
        robot_label.setFont(font)
        self._scene.addItem(robot_label)
        self._object_items.append(robot_label)

    def update_robot_position(self, x: float, y: float, angle: float = 0):
        """Update robot position on the map."""
        if self._robot_item:
            self._robot_item.update_position(x, y, angle)
            self.robot_moved.emit(x, y, angle)

    def add_waypoint(self, x: float, y: float, label: str = ""):
        """Add a waypoint marker to the map."""
        waypoint = QGraphicsEllipseItem(x - 10, y - 10, 20, 20)
        waypoint.setBrush(QBrush(OBJECT_COLORS['waypoint']))
        waypoint.setPen(QPen(QColor(0, 0, 0), 2))
        waypoint.setZValue(20)
        self._scene.addItem(waypoint)
        self._path_items.append(waypoint)

        if label:
            waypoint_label = QGraphicsTextItem(label)
            waypoint_label.setPos(x + 15, y - 10)
            waypoint_label.setZValue(25)
            waypoint_label.setDefaultTextColor(QColor(150, 0, 0))
            self._scene.addItem(waypoint_label)
            self._path_items.append(waypoint_label)

    def clear_path(self):
        """Clear all path and waypoint markers."""
        for item in self._path_items:
            self._scene.removeItem(item)
        self._path_items.clear()

    def toggle_background_visibility(self, visible: bool) -> None:
        """Toggle visibility of the background mat/grid."""
        self._background.set_visible(visible)

    def get_object_count(self) -> int:
        """Get total number of objects on the map."""
        return len(self._object_items)

    def resizeEvent(self, event):
        """Keep the whole mat visible on resize."""
        super().resizeEvent(event)
        bg = (
            self._background.get_graphics_item()
            if hasattr(self, "_background")
            else None
        )
        if bg is not None:
            self.fitInView(bg, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.fitInView(
                self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
            )


class FLLSimMainWindow(QMainWindow):
    """Main window for FLL Simulator with integrated controls."""

    def __init__(self, game_map: GameMap, mat_path: Optional[Path] = None):
        super().__init__()

        self._game_map = game_map
        self._mat_path = mat_path
        self._simulation_running = False

        self.setWindowTitle("FLL-Sim - Enhanced Simulator")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Setup the user interface."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create menu bar
        self._create_menu_bar()

        # Create toolbar
        self._create_toolbar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Load a robot program to begin")

        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        central_widget.setLayout(QHBoxLayout())
        central_widget.layout().addWidget(main_splitter)

        # Left panel: Simulator view and legend
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Simulator view
        self._simulator_view = EnhancedSimulatorView(
            self._game_map, mat_path=self._mat_path
        )

        # View controls
        view_controls = QHBoxLayout()

        self._bg_toggle = QCheckBox("Show Background")
        self._bg_toggle.setChecked(True)
        view_controls.addWidget(self._bg_toggle)

        zoom_in_btn = QPushButton("Zoom In")
        zoom_out_btn = QPushButton("Zoom Out")
        fit_view_btn = QPushButton("Fit View")

        view_controls.addWidget(zoom_in_btn)
        view_controls.addWidget(zoom_out_btn)
        view_controls.addWidget(fit_view_btn)
        view_controls.addStretch()

        left_layout.addLayout(view_controls)
        left_layout.addWidget(self._simulator_view)

        # Legend panel
        self._legend = LegendWidget()
        self._legend.update_object_count(self._simulator_view.get_object_count())

        simulator_splitter = QSplitter(Qt.Orientation.Horizontal)
        simulator_splitter.addWidget(left_widget)
        simulator_splitter.addWidget(self._legend)
        simulator_splitter.setSizes([800, 200])

        # Right panel: Code editor and controls
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Tabs for different panels
        tab_widget = QTabWidget()

        # Code editor tab
        code_widget = QWidget()
        code_layout = QVBoxLayout(code_widget)

        # Code editor toolbar
        code_toolbar = QHBoxLayout()

        load_code_btn = QPushButton("Load Code")
        save_code_btn = QPushButton("Save Code")
        run_code_btn = QPushButton("Run Code")
        stop_code_btn = QPushButton("Stop")

        run_code_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        stop_code_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")

        code_toolbar.addWidget(load_code_btn)
        code_toolbar.addWidget(save_code_btn)
        code_toolbar.addWidget(run_code_btn)
        code_toolbar.addWidget(stop_code_btn)
        code_toolbar.addStretch()

        code_layout.addLayout(code_toolbar)

        # Code editor
        self._code_editor = CodeEditor()
        code_layout.addWidget(self._code_editor)

        tab_widget.addTab(code_widget, "Robot Code")

        # Robot configuration tab
        robot_config_widget = self._create_robot_config_widget()
        tab_widget.addTab(robot_config_widget, "Robot Config")

        # Mission control tab
        mission_widget = self._create_mission_widget()
        tab_widget.addTab(mission_widget, "Missions")

        # Output/console tab
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)

        self._output_text = QTextEdit()
        self._output_text.setMaximumHeight(200)
        self._output_text.setPlainText("Console output will appear here...\n")
        self._output_text.setReadOnly(True)

        output_layout.addWidget(QLabel("Simulation Output:"))
        output_layout.addWidget(self._output_text)

        tab_widget.addTab(output_widget, "Output")

        right_layout.addWidget(tab_widget)

        # Add panels to main splitter
        main_splitter.addWidget(simulator_splitter)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([1000, 400])

        # Connect view controls
        zoom_in_btn.clicked.connect(lambda: self._simulator_view.scale(1.2, 1.2))
        zoom_out_btn.clicked.connect(lambda: self._simulator_view.scale(0.8, 0.8))
        fit_view_btn.clicked.connect(self._fit_view)

        # Connect code controls
        load_code_btn.clicked.connect(self._load_code)
        save_code_btn.clicked.connect(self._save_code)
        run_code_btn.clicked.connect(self._run_code)
        stop_code_btn.clicked.connect(self._stop_code)

        # Store buttons for later use
        self._run_code_btn = run_code_btn
        self._stop_code_btn = stop_code_btn

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Program", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_program)
        file_menu.addAction(new_action)

        load_action = QAction("&Load Program", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._load_code)
        file_menu.addAction(load_action)

        save_action = QAction("&Save Program", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_code)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(lambda: self._simulator_view.scale(1.2, 1.2))
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(lambda: self._simulator_view.scale(0.8, 0.8))
        view_menu.addAction(zoom_out_action)

        fit_view_action = QAction("&Fit to View", self)
        fit_view_action.setShortcut("Ctrl+0")
        fit_view_action.triggered.connect(self._fit_view)
        view_menu.addAction(fit_view_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Robot controls
        reset_action = QAction("Reset Robot", self)
        reset_action.triggered.connect(self._reset_robot)
        toolbar.addAction(reset_action)

        toolbar.addSeparator()

        # Simulation controls
        start_sim_action = QAction("Start Demo", self)
        start_sim_action.triggered.connect(self._start_demo)
        toolbar.addAction(start_sim_action)

        stop_sim_action = QAction("Stop Demo", self)
        stop_sim_action.triggered.connect(self._stop_demo)
        toolbar.addAction(stop_sim_action)

    def _fit_view(self):
        """Fit the view to show the entire map."""
        if hasattr(self._simulator_view, '_bg_item') and self._simulator_view._bg_item:
            bg = self._simulator_view._bg_item
            self._simulator_view.fitInView(bg.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _new_program(self):
        """Create a new robot program."""
        self._code_editor.setPlainText(
            "# New Robot Program\n"
            "from pybricks.hubs import EV3Brick\n"
            "from pybricks.ev3devices import Motor\n"
            "from pybricks.parameters import Port\n\n"
            "# Initialize the EV3 Brick\n"
            "ev3 = EV3Brick()\n\n"
            "# Initialize motors\n"
            "left_motor = Motor(Port.B)\n"
            "right_motor = Motor(Port.C)\n\n"
            "# Your program here\n"
            "print('Hello, FLL!')\n"
        )

    def _load_code(self):
        """Load robot code from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Robot Code", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self._code_editor.setPlainText(f.read())
                self.status_bar.showMessage(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load code: {str(e)}")

    def _save_code(self):
        """Save robot code to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Robot Code", "robot_program.py", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self._code_editor.toPlainText())
                self.status_bar.showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save code: {str(e)}")

    def _run_code(self):
        """Run the robot code."""
        self.status_bar.showMessage("Running robot code...")
        self._output_text.append(">>> Running robot program...")
        # Here you would integrate with the actual robot simulation
        self._output_text.append("Program execution completed.")

    def _stop_code(self):
        """Stop the running code."""
        self.status_bar.showMessage("Code execution stopped")
        self._output_text.append(">>> Execution stopped by user")

    def _start_demo(self):
        """Start a demo simulation."""
        self.status_bar.showMessage("Starting demo simulation...")
        self._output_text.append(">>> Demo simulation started")

    def _stop_demo(self):
        """Stop the demo simulation."""
        self.status_bar.showMessage("Demo simulation stopped")
        self._output_text.append(">>> Demo simulation stopped")

    def _reset_robot(self):
        """Reset robot to starting position."""
        start_x = int(self._game_map.config.width / 4)
        start_y = int(self._game_map.config.height / 2)

        self._robot_x.setValue(start_x)
        self._robot_y.setValue(start_y)
        self._robot_angle.setValue(0)

        self._simulator_view.update_robot_position(start_x, start_y, 0)
        self.status_bar.showMessage("Robot reset to starting position")

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About FLL-Sim",
            "FLL-Sim Enhanced Simulator\n\n"
            "A comprehensive FIRST LEGO League robot simulator\n"
            "with visual programming interface and real-time\n"
            "robot movement visualization.\n\n"
            "Features:\n"
            "• Visual map with robot tracking\n"
            "• Code editor with syntax highlighting\n"
            "• Robot configuration tools\n"
            "• Mission management\n"
            "• Real-time simulation output"
        )
        run_code_btn.clicked.connect(self._run_code)        start_x = int(self._game_map.config.width / 4)
        start_y = int(self._game_map.config.height / 2)

        self._robot_x.setValue(start_x)
        self._robot_y.setValue(start_y)
        self._robot_angle.setValue(0)

        self._simulator_view.update_robot_position(start_x, start_y, 0)
        self.status_bar.showMessage("Robot reset to starting position")

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About FLL-Sim",
            "FLL-Sim Enhanced Simulator\n\n"
            "A comprehensive FIRST LEGO League robot simulator\n"
            "with visual programming interface and real-time\n"
            "robot movement visualization.\n\n"
            "Features:\n"
            "• Visual map with robot tracking\n"
            "• Code editor with syntax highlighting\n"
            "• Robot configuration tools\n"
            "• Mission management\n"
            "• Real-time simulation output"
        )
        run_code_btn.clicked.connect(self._run_code)
