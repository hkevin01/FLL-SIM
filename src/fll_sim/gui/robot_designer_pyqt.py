"""
Robot Designer GUI Component using PyQt6

Visual editor for robot configuration and customization.
"""

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from fll_sim.robot.robot import RobotConfig


class RobotDesignerDialog(QDialog):
    """
    Robot designer dialog for configuring robot parameters using PyQt6.
    """
    
    def __init__(self, parent, robot_config: Optional[RobotConfig] = None):
        """Initialize the robot designer dialog."""
        super().__init__(parent)
        self.robot_config = robot_config
        self.result = None
        
        self.setWindowTitle("Robot Designer")
        self.setGeometry(200, 200, 700, 500)
        self.setModal(True)
        
        self._create_interface()
        self._load_robot_data()
    
    def _create_interface(self):
        """Create the robot designer interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Physical properties tab
        self._create_physical_tab(tab_widget)
        
        # Motor configuration tab
        self._create_motor_tab(tab_widget)
        
        # Sensor configuration tab
        self._create_sensor_tab(tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Robot")
        save_btn.clicked.connect(self._save_robot)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _create_physical_tab(self, tab_widget):
        """Create physical properties configuration tab."""
        widget = QTabWidget()
        layout = QVBoxLayout(widget)
        
        # Robot dimensions
        dim_group = QGroupBox("Dimensions")
        dim_layout = QFormLayout(dim_group)
        
        # Width
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(10.0, 50.0)
        self.width_spin.setValue(18.0)
        self.width_spin.setSuffix(" cm")
        self.width_spin.setSingleStep(0.5)
        dim_layout.addRow("Width:", self.width_spin)
        
        # Height
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(10.0, 50.0)
        self.height_spin.setValue(20.0)
        self.height_spin.setSuffix(" cm")
        self.height_spin.setSingleStep(0.5)
        dim_layout.addRow("Height:", self.height_spin)
        
        layout.addWidget(dim_group)
        
        # Mass properties
        mass_group = QGroupBox("Mass Properties")
        mass_layout = QFormLayout(mass_group)
        
        # Mass
        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setRange(0.5, 5.0)
        self.mass_spin.setValue(1.5)
        self.mass_spin.setSuffix(" kg")
        self.mass_spin.setSingleStep(0.1)
        mass_layout.addRow("Mass:", self.mass_spin)
        
        # Moment of inertia
        self.inertia_spin = QDoubleSpinBox()
        self.inertia_spin.setRange(0.01, 1.0)
        self.inertia_spin.setValue(0.1)
        self.inertia_spin.setSingleStep(0.01)
        self.inertia_spin.setDecimals(3)
        mass_layout.addRow("Moment of Inertia:", self.inertia_spin)
        
        layout.addWidget(mass_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, "Physical Properties")
    
    def _create_motor_tab(self, tab_widget):
        """Create motor configuration tab."""
        widget = QTabWidget()
        layout = QVBoxLayout(widget)
        
        # Drive motors
        drive_group = QGroupBox("Drive Motors")
        drive_layout = QFormLayout(drive_group)
        
        # Wheel diameter
        self.wheel_diameter_spin = QDoubleSpinBox()
        self.wheel_diameter_spin.setRange(2.0, 15.0)
        self.wheel_diameter_spin.setValue(5.6)
        self.wheel_diameter_spin.setSuffix(" cm")
        self.wheel_diameter_spin.setSingleStep(0.1)
        drive_layout.addRow("Wheel Diameter:", self.wheel_diameter_spin)
        
        # Wheel separation
        self.wheel_separation_spin = QDoubleSpinBox()
        self.wheel_separation_spin.setRange(5.0, 30.0)
        self.wheel_separation_spin.setValue(15.0)
        self.wheel_separation_spin.setSuffix(" cm")
        self.wheel_separation_spin.setSingleStep(0.5)
        drive_layout.addRow("Wheel Separation:", self.wheel_separation_spin)
        
        # Max speed
        self.max_speed_spin = QDoubleSpinBox()
        self.max_speed_spin.setRange(100.0, 2000.0)
        self.max_speed_spin.setValue(720.0)
        self.max_speed_spin.setSuffix(" deg/s")
        self.max_speed_spin.setSingleStep(10.0)
        drive_layout.addRow("Max Speed:", self.max_speed_spin)
        
        layout.addWidget(drive_group)
        
        # Additional motors
        aux_group = QGroupBox("Auxiliary Motors")
        aux_layout = QVBoxLayout(aux_group)
        
        # Motor tree
        self.motors_tree = QTreeWidget()
        self.motors_tree.setHeaderLabels(['Port', 'Type', 'Max Speed'])
        aux_layout.addWidget(self.motors_tree)
        
        # Motor buttons
        motor_btn_layout = QHBoxLayout()
        
        add_motor_btn = QPushButton("Add Motor")
        add_motor_btn.clicked.connect(self._add_motor)
        motor_btn_layout.addWidget(add_motor_btn)
        
        remove_motor_btn = QPushButton("Remove Motor")
        remove_motor_btn.clicked.connect(self._remove_motor)
        motor_btn_layout.addWidget(remove_motor_btn)
        
        motor_btn_layout.addStretch()
        aux_layout.addLayout(motor_btn_layout)
        
        layout.addWidget(aux_group)
        
        tab_widget.addTab(widget, "Motors")
    
    def _create_sensor_tab(self, tab_widget):
        """Create sensor configuration tab."""
        widget = QTabWidget()
        layout = QVBoxLayout(widget)
        
        # Sensor list
        sensor_group = QGroupBox("Attached Sensors")
        sensor_layout = QVBoxLayout(sensor_group)
        
        self.sensors_tree = QTreeWidget()
        self.sensors_tree.setHeaderLabels(['Port', 'Type', 'Position', 'Orientation'])
        sensor_layout.addWidget(self.sensors_tree)
        
        # Sensor buttons
        sensor_btn_layout = QHBoxLayout()
        
        add_sensor_btn = QPushButton("Add Sensor")
        add_sensor_btn.clicked.connect(self._add_sensor)
        sensor_btn_layout.addWidget(add_sensor_btn)
        
        edit_sensor_btn = QPushButton("Edit Sensor")
        edit_sensor_btn.clicked.connect(self._edit_sensor)
        sensor_btn_layout.addWidget(edit_sensor_btn)
        
        remove_sensor_btn = QPushButton("Remove Sensor")
        remove_sensor_btn.clicked.connect(self._remove_sensor)
        sensor_btn_layout.addWidget(remove_sensor_btn)
        
        sensor_btn_layout.addStretch()
        sensor_layout.addLayout(sensor_btn_layout)
        
        layout.addWidget(sensor_group)
        
        tab_widget.addTab(widget, "Sensors")
    
    def _load_robot_data(self):
        """Load robot configuration data."""
        if self.robot_config:
            # Load physical properties
            self.width_spin.setValue(getattr(self.robot_config, 'width', 18.0))
            self.height_spin.setValue(getattr(self.robot_config, 'height', 20.0))
            self.mass_spin.setValue(getattr(self.robot_config, 'mass', 1.5))
            self.inertia_spin.setValue(getattr(self.robot_config, 'inertia', 0.1))
            
            # Load motor properties
            self.wheel_diameter_spin.setValue(
                getattr(self.robot_config, 'wheel_diameter', 5.6))
            self.wheel_separation_spin.setValue(
                getattr(self.robot_config, 'wheel_separation', 15.0))
            self.max_speed_spin.setValue(
                getattr(self.robot_config, 'max_speed', 720.0))
    
    def _add_motor(self):
        """Add a new auxiliary motor."""
        dialog = MotorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                item = QTreeWidgetItem([
                    result['port'],
                    result['type'],
                    f"{result['max_speed']} deg/s"
                ])
                self.motors_tree.addTopLevelItem(item)
    
    def _remove_motor(self):
        """Remove selected motor."""
        current_item = self.motors_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", 
                              "Please select a motor to remove.")
            return
        
        reply = QMessageBox.question(self, "Confirm", "Remove selected motor?")
        if reply == QMessageBox.StandardButton.Yes:
            index = self.motors_tree.indexOfTopLevelItem(current_item)
            self.motors_tree.takeTopLevelItem(index)
    
    def _add_sensor(self):
        """Add a new sensor."""
        dialog = SensorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                item = QTreeWidgetItem([
                    result['port'],
                    result['type'],
                    f"({result['x']}, {result['y']})",
                    f"{result['orientation']}°"
                ])
                self.sensors_tree.addTopLevelItem(item)
    
    def _edit_sensor(self):
        """Edit selected sensor."""
        current_item = self.sensors_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", 
                              "Please select a sensor to edit.")
            return
        
        QMessageBox.information(self, "Edit Sensor", 
                              "Sensor editing not yet implemented.")
    
    def _remove_sensor(self):
        """Remove selected sensor."""
        current_item = self.sensors_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", 
                              "Please select a sensor to remove.")
            return
        
        reply = QMessageBox.question(self, "Confirm", "Remove selected sensor?")
        if reply == QMessageBox.StandardButton.Yes:
            index = self.sensors_tree.indexOfTopLevelItem(current_item)
            self.sensors_tree.takeTopLevelItem(index)
    
    def _reset_defaults(self):
        """Reset all values to defaults."""
        reply = QMessageBox.question(self, "Reset", 
                                   "Reset all values to defaults?")
        if reply == QMessageBox.StandardButton.Yes:
            self.width_spin.setValue(18.0)
            self.height_spin.setValue(20.0)
            self.mass_spin.setValue(1.5)
            self.inertia_spin.setValue(0.1)
            self.wheel_diameter_spin.setValue(5.6)
            self.wheel_separation_spin.setValue(15.0)
            self.max_speed_spin.setValue(720.0)
            
            # Clear additional components
            self.motors_tree.clear()
            self.sensors_tree.clear()
    
    def _save_robot(self):
        """Save robot configuration."""
        self.result = {
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
            'mass': self.mass_spin.value(),
            'inertia': self.inertia_spin.value(),
            'wheel_diameter': self.wheel_diameter_spin.value(),
            'wheel_separation': self.wheel_separation_spin.value(),
            'max_speed': self.max_speed_spin.value(),
        }
        
        self.accept()
    
    def get_result(self):
        """Get the dialog result."""
        return self.result


class MotorDialog(QDialog):
    """Dialog for adding/editing motors."""
    
    def __init__(self, parent):
        """Initialize motor dialog."""
        super().__init__(parent)
        self.result = None
        
        self.setWindowTitle("Add Motor")
        self.setGeometry(300, 300, 300, 200)
        self.setModal(True)
        
        self._create_interface()
    
    def _create_interface(self):
        """Create motor dialog interface."""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Port
        self.port_combo = QComboBox()
        self.port_combo.addItems(['A', 'B', 'C', 'D'])
        form_layout.addRow("Port:", self.port_combo)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Large Motor', 'Medium Motor'])
        form_layout.addRow("Type:", self.type_combo)
        
        # Max Speed
        self.max_speed_spin = QDoubleSpinBox()
        self.max_speed_spin.setRange(100.0, 2000.0)
        self.max_speed_spin.setValue(720.0)
        self.max_speed_spin.setSuffix(" deg/s")
        self.max_speed_spin.setSingleStep(10.0)
        form_layout.addRow("Max Speed:", self.max_speed_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._ok)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _ok(self):
        """Save motor configuration."""
        if not self.port_combo.currentText() or not self.type_combo.currentText():
            QMessageBox.critical(self, "Error", 
                                "Please fill in all required fields.")
            return
        
        self.result = {
            'port': self.port_combo.currentText(),
            'type': self.type_combo.currentText(),
            'max_speed': self.max_speed_spin.value()
        }
        
        self.accept()
    
    def get_result(self):
        """Get the dialog result."""
        return self.result


class SensorDialog(QDialog):
    """Dialog for adding/editing sensors."""
    
    def __init__(self, parent):
        """Initialize sensor dialog."""
        super().__init__(parent)
        self.result = None
        
        self.setWindowTitle("Add Sensor")
        self.setGeometry(300, 300, 350, 300)
        self.setModal(True)
        
        self._create_interface()
    
    def _create_interface(self):
        """Create sensor dialog interface."""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Port
        self.port_combo = QComboBox()
        self.port_combo.addItems(['1', '2', '3', '4'])
        form_layout.addRow("Port:", self.port_combo)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            'Color Sensor', 'Ultrasonic Sensor', 
            'Gyro Sensor', 'Touch Sensor'
        ])
        form_layout.addRow("Type:", self.type_combo)
        
        # Position X
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-20.0, 20.0)
        self.x_spin.setValue(0.0)
        self.x_spin.setSuffix(" cm")
        self.x_spin.setSingleStep(0.5)
        form_layout.addRow("Position X:", self.x_spin)
        
        # Position Y
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-20.0, 20.0)
        self.y_spin.setValue(0.0)
        self.y_spin.setSuffix(" cm")
        self.y_spin.setSingleStep(0.5)
        form_layout.addRow("Position Y:", self.y_spin)
        
        # Orientation
        self.orientation_spin = QDoubleSpinBox()
        self.orientation_spin.setRange(0.0, 359.0)
        self.orientation_spin.setValue(0.0)
        self.orientation_spin.setSuffix("°")
        self.orientation_spin.setSingleStep(1.0)
        form_layout.addRow("Orientation:", self.orientation_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._ok)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _ok(self):
        """Save sensor configuration."""
        if not self.port_combo.currentText() or not self.type_combo.currentText():
            QMessageBox.critical(self, "Error", 
                                "Please fill in all required fields.")
            return
        
        self.result = {
            'port': self.port_combo.currentText(),
            'type': self.type_combo.currentText(),
            'x': self.x_spin.value(),
            'y': self.y_spin.value(),
            'orientation': self.orientation_spin.value()
        }
        
        self.accept()
    
    def get_result(self):
        """Get the dialog result."""
        return self.result
