"""
Robot Designer GUI Component

Visual editor for robot configuration and customization.
"""

import json
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, Optional

from fll_sim.robot.robot import RobotConfig


class RobotDesignerDialog:
    """
    Robot designer dialog for configuring robot parameters.
    """
    
    def __init__(self, parent, robot_config: Optional[RobotConfig] = None):
        """Initialize the robot designer dialog."""
        self.parent = parent
        self.robot_config = robot_config
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Robot Designer")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_interface()
        self._load_robot_data()
    
    def _create_interface(self):
        """Create the robot designer interface."""
        # Main container with notebook
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Physical properties tab
        self._create_physical_tab(notebook)
        
        # Motor configuration tab
        self._create_motor_tab(notebook)
        
        # Sensor configuration tab
        self._create_sensor_tab(notebook)
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Robot", 
                  command=self._save_robot).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=self._cancel).pack(side='right')
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_defaults).pack(side='left')
    
    def _create_physical_tab(self, notebook):
        """Create physical properties configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Physical Properties")
        
        # Robot dimensions
        dim_frame = ttk.LabelFrame(frame, text="Dimensions", padding=10)
        dim_frame.pack(fill='x', padx=10, pady=10)
        
        # Width
        ttk.Label(dim_frame, text="Width (cm):").grid(
            row=0, column=0, sticky='w', padx=(0, 10))
        self.width_var = tk.DoubleVar(value=18.0)
        ttk.Spinbox(dim_frame, from_=10.0, to=50.0, increment=0.5,
                   textvariable=self.width_var, width=10).grid(
                       row=0, column=1, sticky='w')
        
        # Height
        ttk.Label(dim_frame, text="Height (cm):").grid(
            row=1, column=0, sticky='w', padx=(0, 10), pady=(5, 0))
        self.height_var = tk.DoubleVar(value=20.0)
        ttk.Spinbox(dim_frame, from_=10.0, to=50.0, increment=0.5,
                   textvariable=self.height_var, width=10).grid(
                       row=1, column=1, sticky='w', pady=(5, 0))
        
        # Mass properties
        mass_frame = ttk.LabelFrame(frame, text="Mass Properties", padding=10)
        mass_frame.pack(fill='x', padx=10, pady=10)
        
        # Mass
        ttk.Label(mass_frame, text="Mass (kg):").grid(
            row=0, column=0, sticky='w', padx=(0, 10))
        self.mass_var = tk.DoubleVar(value=1.5)
        ttk.Spinbox(mass_frame, from_=0.5, to=5.0, increment=0.1,
                   textvariable=self.mass_var, width=10).grid(
                       row=0, column=1, sticky='w')
        
        # Moment of inertia
        ttk.Label(mass_frame, text="Moment of Inertia:").grid(
            row=1, column=0, sticky='w', padx=(0, 10), pady=(5, 0))
        self.inertia_var = tk.DoubleVar(value=0.1)
        ttk.Spinbox(mass_frame, from_=0.01, to=1.0, increment=0.01,
                   textvariable=self.inertia_var, width=10).grid(
                       row=1, column=1, sticky='w', pady=(5, 0))
    
    def _create_motor_tab(self, notebook):
        """Create motor configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Motors")
        
        # Drive motors
        drive_frame = ttk.LabelFrame(frame, text="Drive Motors", padding=10)
        drive_frame.pack(fill='x', padx=10, pady=10)
        
        # Wheel diameter
        ttk.Label(drive_frame, text="Wheel Diameter (cm):").grid(
            row=0, column=0, sticky='w', padx=(0, 10))
        self.wheel_diameter_var = tk.DoubleVar(value=5.6)
        ttk.Spinbox(drive_frame, from_=2.0, to=15.0, increment=0.1,
                   textvariable=self.wheel_diameter_var, width=10).grid(
                       row=0, column=1, sticky='w')
        
        # Wheel separation
        ttk.Label(drive_frame, text="Wheel Separation (cm):").grid(
            row=1, column=0, sticky='w', padx=(0, 10), pady=(5, 0))
        self.wheel_separation_var = tk.DoubleVar(value=15.0)
        ttk.Spinbox(drive_frame, from_=5.0, to=30.0, increment=0.5,
                   textvariable=self.wheel_separation_var, width=10).grid(
                       row=1, column=1, sticky='w', pady=(5, 0))
        
        # Max speed
        ttk.Label(drive_frame, text="Max Speed (deg/s):").grid(
            row=2, column=0, sticky='w', padx=(0, 10), pady=(5, 0))
        self.max_speed_var = tk.DoubleVar(value=720.0)
        ttk.Spinbox(drive_frame, from_=100.0, to=2000.0, increment=10.0,
                   textvariable=self.max_speed_var, width=10).grid(
                       row=2, column=1, sticky='w', pady=(5, 0))
        
        # Additional motors
        aux_frame = ttk.LabelFrame(frame, text="Auxiliary Motors", padding=10)
        aux_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Motor list
        list_frame = ttk.Frame(aux_frame)
        list_frame.pack(fill='both', expand=True)
        
        columns = ('Port', 'Type', 'Max Speed')
        self.motors_tree = ttk.Treeview(list_frame, columns=columns, 
                                       show='headings', height=6)
        
        for col in columns:
            self.motors_tree.heading(col, text=col)
            self.motors_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                 command=self.motors_tree.yview)
        self.motors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.motors_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Motor buttons
        motor_btn_frame = ttk.Frame(aux_frame)
        motor_btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(motor_btn_frame, text="Add Motor", 
                  command=self._add_motor).pack(side='left', padx=(0, 5))
        ttk.Button(motor_btn_frame, text="Remove Motor", 
                  command=self._remove_motor).pack(side='left')
    
    def _create_sensor_tab(self, notebook):
        """Create sensor configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Sensors")
        
        # Sensor list
        sensor_frame = ttk.LabelFrame(frame, text="Attached Sensors", 
                                     padding=10)
        sensor_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        list_frame = ttk.Frame(sensor_frame)
        list_frame.pack(fill='both', expand=True)
        
        columns = ('Port', 'Type', 'Position', 'Orientation')
        self.sensors_tree = ttk.Treeview(list_frame, columns=columns, 
                                        show='headings', height=8)
        
        for col in columns:
            self.sensors_tree.heading(col, text=col)
            self.sensors_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                 command=self.sensors_tree.yview)
        self.sensors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sensors_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Sensor buttons
        sensor_btn_frame = ttk.Frame(sensor_frame)
        sensor_btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(sensor_btn_frame, text="Add Sensor", 
                  command=self._add_sensor).pack(side='left', padx=(0, 5))
        ttk.Button(sensor_btn_frame, text="Edit Sensor", 
                  command=self._edit_sensor).pack(side='left', padx=(0, 5))
        ttk.Button(sensor_btn_frame, text="Remove Sensor", 
                  command=self._remove_sensor).pack(side='left')
    
    def _load_robot_data(self):
        """Load robot configuration data."""
        if self.robot_config:
            # Load physical properties
            self.width_var.set(getattr(self.robot_config, 'width', 18.0))
            self.height_var.set(getattr(self.robot_config, 'height', 20.0))
            self.mass_var.set(getattr(self.robot_config, 'mass', 1.5))
            self.inertia_var.set(getattr(self.robot_config, 'inertia', 0.1))
            
            # Load motor properties
            self.wheel_diameter_var.set(
                getattr(self.robot_config, 'wheel_diameter', 5.6))
            self.wheel_separation_var.set(
                getattr(self.robot_config, 'wheel_separation', 15.0))
            self.max_speed_var.set(
                getattr(self.robot_config, 'max_speed', 720.0))
    
    def _add_motor(self):
        """Add a new auxiliary motor."""
        dialog = MotorDialog(self.dialog)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.motors_tree.insert('', 'end', values=(
                dialog.result['port'],
                dialog.result['type'],
                dialog.result['max_speed']
            ))
    
    def _remove_motor(self):
        """Remove selected motor."""
        selection = self.motors_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", 
                                 "Please select a motor to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Remove selected motor?"):
            self.motors_tree.delete(selection[0])
    
    def _add_sensor(self):
        """Add a new sensor."""
        dialog = SensorDialog(self.dialog)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.sensors_tree.insert('', 'end', values=(
                dialog.result['port'],
                dialog.result['type'],
                f"({dialog.result['x']}, {dialog.result['y']})",
                dialog.result['orientation']
            ))
    
    def _edit_sensor(self):
        """Edit selected sensor."""
        selection = self.sensors_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", 
                                 "Please select a sensor to edit.")
            return
        
        # Implementation would parse existing values and open edit dialog
        messagebox.showinfo("Edit Sensor", "Sensor editing not yet implemented.")
    
    def _remove_sensor(self):
        """Remove selected sensor."""
        selection = self.sensors_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", 
                                 "Please select a sensor to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Remove selected sensor?"):
            self.sensors_tree.delete(selection[0])
    
    def _reset_defaults(self):
        """Reset all values to defaults."""
        if messagebox.askyesno("Reset", "Reset all values to defaults?"):
            self.width_var.set(18.0)
            self.height_var.set(20.0)
            self.mass_var.set(1.5)
            self.inertia_var.set(0.1)
            self.wheel_diameter_var.set(5.6)
            self.wheel_separation_var.set(15.0)
            self.max_speed_var.set(720.0)
            
            # Clear additional components
            for item in self.motors_tree.get_children():
                self.motors_tree.delete(item)
            for item in self.sensors_tree.get_children():
                self.sensors_tree.delete(item)
    
    def _save_robot(self):
        """Save robot configuration."""
        self.result = {
            'width': self.width_var.get(),
            'height': self.height_var.get(),
            'mass': self.mass_var.get(),
            'inertia': self.inertia_var.get(),
            'wheel_diameter': self.wheel_diameter_var.get(),
            'wheel_separation': self.wheel_separation_var.get(),
            'max_speed': self.max_speed_var.get(),
        }
        
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


class MotorDialog:
    """Dialog for adding/editing motors."""
    
    def __init__(self, parent):
        """Initialize motor dialog."""
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Motor")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_interface()
    
    def _create_interface(self):
        """Create motor dialog interface."""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Port
        ttk.Label(main_frame, text="Port:").grid(
            row=0, column=0, sticky='w', pady=(0, 10))
        self.port_var = tk.StringVar()
        port_combo = ttk.Combobox(main_frame, textvariable=self.port_var,
                                 values=['A', 'B', 'C', 'D'], 
                                 state='readonly', width=15)
        port_combo.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Type
        ttk.Label(main_frame, text="Type:").grid(
            row=1, column=0, sticky='w', pady=(0, 10))
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var,
                                 values=['Large Motor', 'Medium Motor'], 
                                 state='readonly', width=15)
        type_combo.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
        # Max Speed
        ttk.Label(main_frame, text="Max Speed (deg/s):").grid(
            row=2, column=0, sticky='w', pady=(0, 10))
        self.max_speed_var = tk.DoubleVar(value=720.0)
        ttk.Spinbox(main_frame, from_=100.0, to=2000.0, increment=10.0,
                   textvariable=self.max_speed_var, width=15).grid(
                       row=2, column=1, sticky='w', pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky='ew', 
                         pady=(20, 0))
        
        ttk.Button(button_frame, text="OK", command=self._ok).pack(
            side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(
            side='right')
    
    def _ok(self):
        """Save motor configuration."""
        if not self.port_var.get() or not self.type_var.get():
            messagebox.showerror("Error", 
                               "Please fill in all required fields.")
            return
        
        self.result = {
            'port': self.port_var.get(),
            'type': self.type_var.get(),
            'max_speed': self.max_speed_var.get()
        }
        
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel dialog."""
        self.dialog.destroy()


class SensorDialog:
    """Dialog for adding/editing sensors."""
    
    def __init__(self, parent):
        """Initialize sensor dialog."""
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Sensor")
        self.dialog.geometry("350x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_interface()
    
    def _create_interface(self):
        """Create sensor dialog interface."""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Port
        ttk.Label(main_frame, text="Port:").grid(
            row=0, column=0, sticky='w', pady=(0, 10))
        self.port_var = tk.StringVar()
        port_combo = ttk.Combobox(main_frame, textvariable=self.port_var,
                                 values=['1', '2', '3', '4'], 
                                 state='readonly', width=15)
        port_combo.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Type
        ttk.Label(main_frame, text="Type:").grid(
            row=1, column=0, sticky='w', pady=(0, 10))
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var,
                                 values=['Color Sensor', 'Ultrasonic Sensor', 
                                        'Gyro Sensor', 'Touch Sensor'], 
                                 state='readonly', width=20)
        type_combo.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
        # Position
        ttk.Label(main_frame, text="Position (X, Y):").grid(
            row=2, column=0, sticky='w', pady=(0, 5))
        
        pos_frame = ttk.Frame(main_frame)
        pos_frame.grid(row=2, column=1, sticky='w', pady=(0, 10))
        
        self.x_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(pos_frame, from_=-20.0, to=20.0, increment=0.5,
                   textvariable=self.x_var, width=8).pack(side='left')
        
        ttk.Label(pos_frame, text=", ").pack(side='left')
        
        self.y_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(pos_frame, from_=-20.0, to=20.0, increment=0.5,
                   textvariable=self.y_var, width=8).pack(side='left')
        
        # Orientation
        ttk.Label(main_frame, text="Orientation (deg):").grid(
            row=3, column=0, sticky='w', pady=(0, 10))
        self.orientation_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(main_frame, from_=0.0, to=359.0, increment=1.0,
                   textvariable=self.orientation_var, width=15).grid(
                       row=3, column=1, sticky='w', pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky='ew', 
                         pady=(20, 0))
        
        ttk.Button(button_frame, text="OK", command=self._ok).pack(
            side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(
            side='right')
    
    def _ok(self):
        """Save sensor configuration."""
        if not self.port_var.get() or not self.type_var.get():
            messagebox.showerror("Error", 
                               "Please fill in all required fields.")
            return
        
        self.result = {
            'port': self.port_var.get(),
            'type': self.type_var.get(),
            'x': self.x_var.get(),
            'y': self.y_var.get(),
            'orientation': self.orientation_var.get()
        }
        
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel dialog."""
        self.dialog.destroy()
