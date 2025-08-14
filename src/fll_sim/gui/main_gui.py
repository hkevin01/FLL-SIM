#!/usr/bin/env python3
"""
FLL-Sim GUI (PyQt6)
A minimal GUI that launches the simulator and uses themed icons.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import cast

from PyQt6 import QtCore, QtGui, QtWidgets

# Ensure src on path when launched directly
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root / "src"))


class SimulationThread(QtCore.QThread):
    status_update = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self, cmd: list[str]):
        super().__init__()
        self.cmd = cmd
        self.proc: subprocess.Popen | None = None

    def run(self) -> None:  # noqa: D401
        try:
            self.status_update.emit("Starting simulation…")
            env = os.environ.copy()
            env["PYTHONPATH"] = (
                f"{project_root / 'src'}:" + env.get("PYTHONPATH", "")
            )
            self.proc = subprocess.Popen(
                self.cmd,
                cwd=str(project_root),
                env=env,
            )
            self.proc.wait()
            rc = self.proc.returncode if self.proc else -1
            if rc == 0:
                self.status_update.emit("Simulation completed successfully")
            else:
                self.status_update.emit(f"Simulation exited with code {rc}")
        except (OSError, ValueError, RuntimeError) as e:
            self.status_update.emit(f"Simulation error: {e}")
        finally:
            self.finished.emit()

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.status_update.emit("Simulation stopping…")


class FLLSimMainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FLL-Sim - First Lego League Simulator")
        self.resize(1200, 800)

        # Icon: package icon or themed fallback
        icon_path = Path(__file__).parent / "icons" / "app.png"
        if icon_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        else:
            self.setWindowIcon(QtGui.QIcon.fromTheme("applications-education"))

        # Predefine thread attribute for linters
        self.sim_thread: SimulationThread | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(central)
        self.setCentralWidget(central)

        # Tabs (minimal but functional)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(self.tabs)

        # Quick tab
        quick = QtWidgets.QWidget(self)
        v = QtWidgets.QVBoxLayout(quick)
        self.status_label = QtWidgets.QLabel("Ready", quick)
        v.addWidget(self.status_label)
        b_start = QtWidgets.QPushButton("Start")
        b_start.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
        b_start.clicked.connect(self._start_simulation)
        b_stop = QtWidgets.QPushButton("Stop")
        b_stop.setIcon(QtGui.QIcon.fromTheme("media-playback-stop"))
        b_stop.clicked.connect(self._stop_simulation)
        self.progress = QtWidgets.QProgressBar()
        self.progress.setVisible(False)
        v.addWidget(b_start)
        v.addWidget(b_stop)
        v.addWidget(self.progress)
        self.tabs.addTab(quick, "Quick Start")

        # Missions tab (placeholder)
        missions = QtWidgets.QWidget(self)
        mv = QtWidgets.QVBoxLayout(missions)
        mv.addWidget(QtWidgets.QLabel("Available Missions"))
        self.missions_list = QtWidgets.QListWidget(missions)
        mv.addWidget(self.missions_list)
        self.tabs.addTab(missions, "Missions")

        # Status bar
        self.status_bar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Menu bar
        self._build_menus()

        # Keyboard shortcuts
        self._build_shortcuts()

    def _build_menus(self) -> None:
        menubar = self.menuBar()
        if menubar is None:
            menubar = QtWidgets.QMenuBar(self)
            self.setMenuBar(menubar)

        file_menu = cast(QtWidgets.QMenu, menubar.addMenu("&File"))
        act_open = QtGui.QAction(
            QtGui.QIcon.fromTheme("document-open"),
            "&Open Configuration…",
            self,
        )
        act_open.setShortcut(QtGui.QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self._load_configuration)
        file_menu.addAction(act_open)

        file_menu.addSeparator()
        act_exit = QtGui.QAction(
            QtGui.QIcon.fromTheme("application-exit"),
            "E&xit",
            self,
        )
        act_exit.setShortcut(QtGui.QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        sim_menu = cast(QtWidgets.QMenu, menubar.addMenu("&Simulation"))
        act_start = QtGui.QAction(
            QtGui.QIcon.fromTheme("media-playback-start"),
            "&Start",
            self,
        )
        act_start.setShortcut(QtGui.QKeySequence("F5"))
        act_start.triggered.connect(self._start_simulation)
        sim_menu.addAction(act_start)

        act_stop = QtGui.QAction(
            QtGui.QIcon.fromTheme("media-playback-stop"),
            "St&op",
            self,
        )
        act_stop.setShortcut(QtGui.QKeySequence("Shift+F5"))
        act_stop.triggered.connect(self._stop_simulation)
        sim_menu.addAction(act_stop)

        help_menu = cast(QtWidgets.QMenu, menubar.addMenu("&Help"))
        act_about = QtGui.QAction(
            QtGui.QIcon.fromTheme("help-about"),
            "&About FLL-Sim",
            self,
        )
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _build_shortcuts(self) -> None:
        # Already set via menu actions for common ones; add more if needed
        pass

    # --- Actions ---
    def _start_simulation(self) -> None:
        if self.sim_thread and self.sim_thread.isRunning():
            QtWidgets.QMessageBox.warning(
                self,
                "Warning",
                "Simulation is already running.",
            )
            return
        cmd = [
            sys.executable,
            "-m",
            "fll_sim.core.simulator",
            "--profile",
            "beginner",
            "--robot",
            "standard_fll",
            "--season",
            "2024",
        ]
        self.sim_thread = SimulationThread(cmd)
        self.sim_thread.status_update.connect(self.status_bar.showMessage)
        self.sim_thread.finished.connect(
            lambda: self._update_status("Simulation finished")
        )
        self.sim_thread.start()
        self._update_status("Simulation started")

    def _stop_simulation(self) -> None:
        if self.sim_thread and self.sim_thread.isRunning():
            self.sim_thread.stop()
        else:
            self._update_status("No simulation is running")

    def _load_configuration(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Configuration",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if path:
            self._update_status(f"Loaded configuration: {path}")

    def _show_about(self) -> None:
        QtWidgets.QMessageBox.about(
            self,
            "About FLL-Sim",
            (
                "<h3>FLL-Sim - First Lego League Simulator</h3>\n"
                "<p>Simulation environment for practicing FLL missions with a "
                "virtual robot.</p>\n"
                "<p>Launches the simulator module and provides basic tabs for "
                "getting started.</p>\n"
            ),
        )

    def _update_status(self, msg: str) -> None:
        self.status_label.setText(msg)
        self.status_bar.showMessage(msg)


def main() -> None:
    # Encourage a theme with icons
    QtGui.QIcon.setThemeName(os.environ.get("QT_ICON_THEME", "Adwaita"))

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("FLL-Sim")
    app.setApplicationVersion("0.8.0")
    app.setOrganizationName("FLL-Sim Project")

    # App icon fallback
    icon = QtGui.QIcon.fromTheme("applications-education")
    if not icon.isNull():
        app.setWindowIcon(icon)

    win = FLLSimMainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# Backward compatibility: older code expects FLLSimGUI symbol here
FLLSimGUI = FLLSimMainWindow
