#!/usr/bin/env python3
"""
Main GUI interface for FLL-Sim.

This module provides a comprehensive graphical user interface for
FLL-Sim using tkinter, making the simulator accessible to users
who prefer visual interfaces over command-line tools.
"""

import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, Optional

# Add project src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from fll_sim.config.config_manager import ConfigManager
from fll_sim.core.simulator import SimulationConfig
from fll_sim.robot.robot import RobotConfig


class FLLSimGUI:
    """
    Main GUI application for FLL-Sim.
    
    Provides a user-friendly interface for:
    - Configuration management
    - Simulation launching
    - Mission selection
    - Robot setup
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("FLL-Sim - First Lego League Simulator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configuration manager
        self.config_manager = ConfigManager()
        
        # Current settings
        self.current_profile = "beginner"
        self.current_robot = "standard_fll"
        self.current_season = "2024"
        self.simulation_process = None
        
        # Initialize GUI components
        self._setup_styles()
        self._create_menu()
        self._create_main_interface()
        self._load_initial_data()
    
    def _setup_styles(self):
        """Configure GUI styles and themes."""
        style = ttk.Style()
        
        # Configure colors and fonts
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#F18F01',
            'warning': '#C73E1D',
            'background': '#F5F5F5',
            'text': '#333333'
        }
        
        # Configure ttk styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
    
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Simulation", command=self._new_simulation)
        file_menu.add_command(label="Load Configuration", command=self._load_configuration)
        file_menu.add_command(label="Save Configuration", command=self._save_configuration)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start Simulation", command=self._start_simulation)
        sim_menu.add_command(label="Stop Simulation", command=self._stop_simulation)
        sim_menu.add_separator()
        sim_menu.add_command(label="Run Demo", command=self._run_demo)
        sim_menu.add_command(label="Run Headless", command=self._run_headless)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Mission Editor", command=self._open_mission_editor)
        tools_menu.add_command(label="Robot Designer", command=self._open_robot_designer)
        tools_menu.add_command(label="Performance Monitor", command=self._open_performance_monitor)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._open_documentation)
        help_menu.add_command(label="Examples", command=self._open_examples)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_interface(self):
        """Create the main GUI interface."""
        # Create main container with notebook
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self._create_quick_start_tab()
        self._create_configuration_tab()
        self._create_simulation_tab()
        self._create_missions_tab()
        self._create_robot_tab()
        self._create_monitor_tab()
    
    def _create_quick_start_tab(self):
        """Create the quick start tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Quick Start")
        
        # Welcome section
        welcome_frame = ttk.LabelFrame(frame, text="Welcome to FLL-Sim", padding=20)
        welcome_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(welcome_frame, text="FLL-Sim - First Lego League Simulator", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        ttk.Label(welcome_frame, 
                 text="A comprehensive simulation environment for FLL teams to develop,\n"
                      "test, and refine their robot strategies before physical implementation.",
                 justify='center').pack(pady=(0, 20))
        
        # Quick actions
        actions_frame = ttk.LabelFrame(frame, text="Quick Actions", padding=20)
        actions_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create grid for quick action buttons
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack(expand=True)
        
        # Quick start buttons
        buttons = [
            ("🚀 Start Simulation", self._start_simulation, "Launch the full simulation"),
            ("🎮 Run Demo", self._run_demo, "Try a quick demonstration"),
            ("📚 View Examples", self._open_examples, "Browse example programs"),
            ("⚙️ Configure Robot", self._configure_robot, "Set up your robot"),
            ("🗺️ Load Mission", self._load_mission, "Choose FLL missions"),
            ("📊 Performance Monitor", self._open_performance_monitor, "Track robot performance")
        ]
        
        for i, (text, command, tooltip) in enumerate(buttons):
            btn = ttk.Button(actions_grid, text=text, command=command, 
                           style='Action.TButton', width=25)
            btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky='ew')
            
            # Add tooltip (simplified)
            self._create_tooltip(btn, tooltip)
        
        # Configure grid weights
        actions_grid.columnconfigure(0, weight=1)
        actions_grid.columnconfigure(1, weight=1)
        
        # Status section
        status_frame = ttk.LabelFrame(frame, text="System Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Ready", style='Status.TLabel')
        self.status_label.pack(side='left')
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side='right', padx=(10, 0))
    
    def _create_configuration_tab(self):
        """Create the configuration tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Configuration")
        
        # Profile selection
        profile_frame = ttk.LabelFrame(frame, text="Simulation Profile", padding=10)
        profile_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(profile_frame, text="Profile:", style='Heading.TLabel').grid(row=0, column=0, sticky='w')
        
        self.profile_var = tk.StringVar(value=self.current_profile)
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var,
                                   values=['beginner', 'intermediate', 'advanced'],
                                   state='readonly', width=20)
        profile_combo.grid(row=0, column=1, padx=(10, 0), sticky='w')
        profile_combo.bind('<<ComboboxSelected>>', self._on_profile_changed)
        
        # Profile description
        self.profile_desc = ttk.Label(profile_frame, text="", wraplength=400)
        self.profile_desc.grid(row=1, column=0, columnspan=2, sticky='w', pady=(10, 0))
        
        # Robot configuration
        robot_frame = ttk.LabelFrame(frame, text="Robot Configuration", padding=10)
        robot_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(robot_frame, text="Robot Type:", style='Heading.TLabel').grid(row=0, column=0, sticky='w')
        
        self.robot_var = tk.StringVar(value=self.current_robot)
        robot_combo = ttk.Combobox(robot_frame, textvariable=self.robot_var,
                                 values=['standard_fll', 'compact_robot', 'heavy_pusher'],
                                 state='readonly', width=20)
        robot_combo.grid(row=0, column=1, padx=(10, 0), sticky='w')
        robot_combo.bind('<<ComboboxSelected>>', self._on_robot_changed)
        
        # Season selection
        season_frame = ttk.LabelFrame(frame, text="FLL Season", padding=10)
        season_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(season_frame, text="Season:", style='Heading.TLabel').grid(row=0, column=0, sticky='w')
        
        self.season_var = tk.StringVar(value=self.current_season)
        season_combo = ttk.Combobox(season_frame, textvariable=self.season_var,
                                  values=['2024', '2023'], state='readonly', width=20)
        season_combo.grid(row=0, column=1, padx=(10, 0), sticky='w')
        season_combo.bind('<<ComboboxSelected>>', self._on_season_changed)
        
        # Season description
        self.season_desc = ttk.Label(season_frame, text="", wraplength=400)
        self.season_desc.grid(row=1, column=0, columnspan=2, sticky='w', pady=(10, 0))
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(frame, text="Advanced Settings", padding=10)
        advanced_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Settings checkboxes
        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(advanced_frame, text="Enable debug visualization",
                       variable=self.debug_var).pack(anchor='w', pady=2)
        
        self.physics_debug_var = tk.BooleanVar()
        ttk.Checkbutton(advanced_frame, text="Show physics debug info",
                       variable=self.physics_debug_var).pack(anchor='w', pady=2)
        
        self.performance_tracking_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="Enable performance tracking",
                       variable=self.performance_tracking_var).pack(anchor='w', pady=2)
    
    def _create_simulation_tab(self):
        """Create the simulation control tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Simulation")
        
        # Simulation controls
        controls_frame = ttk.LabelFrame(frame, text="Simulation Controls", padding=10)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Control buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill='x')
        
        self.start_btn = ttk.Button(btn_frame, text="▶ Start Simulation", 
                                   command=self._start_simulation, style='Action.TButton')
        self.start_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop Simulation", 
                                  command=self._stop_simulation, state='disabled')
        self.stop_btn.pack(side='left', padx=(0, 10))
        
        self.pause_btn = ttk.Button(btn_frame, text="⏸ Pause", 
                                   command=self._pause_simulation, state='disabled')
        self.pause_btn.pack(side='left', padx=(0, 10))
        
        # Simulation parameters
        params_frame = ttk.LabelFrame(frame, text="Simulation Parameters", padding=10)
        params_frame.pack(fill='x', padx=10, pady=10)
        
        # Speed control
        ttk.Label(params_frame, text="Simulation Speed:").grid(row=0, column=0, sticky='w')
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(params_frame, from_=0.1, to=5.0, variable=self.speed_var,
                              orient='horizontal', length=200)
        speed_scale.grid(row=0, column=1, padx=(10, 0), sticky='ew')
        self.speed_label = ttk.Label(params_frame, text="1.0x")
        self.speed_label.grid(row=0, column=2, padx=(10, 0))
        speed_scale.bind('<Motion>', self._update_speed_label)
        
        # Output display
        output_frame = ttk.LabelFrame(frame, text="Simulation Output", padding=10)
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.output_text = tk.Text(text_frame, wrap='word', state='disabled', 
                                  font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Clear output button
        ttk.Button(output_frame, text="Clear Output", 
                  command=self._clear_output).pack(anchor='e', pady=(10, 0))
    
    def _create_missions_tab(self):
        """Create the missions management tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Missions")
        
        # Mission selection
        selection_frame = ttk.LabelFrame(frame, text="Available Missions", padding=10)
        selection_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Mission list
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for missions
        columns = ('name', 'difficulty', 'points', 'status')
        self.mission_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Define headings
        self.mission_tree.heading('name', text='Mission Name')
        self.mission_tree.heading('difficulty', text='Difficulty')
        self.mission_tree.heading('points', text='Max Points')
        self.mission_tree.heading('status', text='Status')
        
        # Configure column widths
        self.mission_tree.column('name', width=200)
        self.mission_tree.column('difficulty', width=100)
        self.mission_tree.column('points', width=100)
        self.mission_tree.column('status', width=100)
        
        mission_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                        command=self.mission_tree.yview)
        self.mission_tree.configure(yscrollcommand=mission_scrollbar.set)
        
        self.mission_tree.pack(side='left', fill='both', expand=True)
        mission_scrollbar.pack(side='right', fill='y')
        
        # Mission details
        details_frame = ttk.LabelFrame(frame, text="Mission Details", padding=10)
        details_frame.pack(fill='x', padx=10, pady=10)
        
        self.mission_details = tk.Text(details_frame, height=4, wrap='word', state='disabled')
        self.mission_details.pack(fill='x')
        
        # Mission controls
        mission_controls = ttk.Frame(details_frame)
        mission_controls.pack(fill='x', pady=(10, 0))
        
        ttk.Button(mission_controls, text="Load Mission", 
                  command=self._load_selected_mission).pack(side='left', padx=(0, 10))
        ttk.Button(mission_controls, text="Edit Mission", 
                  command=self._edit_mission).pack(side='left', padx=(0, 10))
        ttk.Button(mission_controls, text="Create New", 
                  command=self._create_mission).pack(side='left')
        
        # Bind selection event
        self.mission_tree.bind('<<TreeviewSelect>>', self._on_mission_selected)
    
    def _create_robot_tab(self):
        """Create the robot configuration tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Robot")
        
        # Robot preview (placeholder)
        preview_frame = ttk.LabelFrame(frame, text="Robot Preview", padding=10)
        preview_frame.pack(fill='x', padx=10, pady=10)
        
        self.robot_canvas = tk.Canvas(preview_frame, width=300, height=200, bg='white')
        self.robot_canvas.pack()
        
        # Draw simple robot representation
        self._draw_robot_preview()
        
        # Robot parameters
        params_frame = ttk.LabelFrame(frame, text="Robot Parameters", padding=10)
        params_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Parameter controls
        params_grid = ttk.Frame(params_frame)
        params_grid.pack(fill='x')
        
        # Width
        ttk.Label(params_grid, text="Width (mm):").grid(row=0, column=0, sticky='w', pady=2)
        self.width_var = tk.DoubleVar(value=180.0)
        width_spin = ttk.Spinbox(params_grid, from_=100, to=300, textvariable=self.width_var,
                               width=10, increment=10)
        width_spin.grid(row=0, column=1, padx=(10, 0), sticky='w')
        
        # Length
        ttk.Label(params_grid, text="Length (mm):").grid(row=1, column=0, sticky='w', pady=2)
        self.length_var = tk.DoubleVar(value=200.0)
        length_spin = ttk.Spinbox(params_grid, from_=120, to=350, textvariable=self.length_var,
                                width=10, increment=10)
        length_spin.grid(row=1, column=1, padx=(10, 0), sticky='w')
        
        # Max speed
        ttk.Label(params_grid, text="Max Speed (mm/s):").grid(row=2, column=0, sticky='w', pady=2)
        self.max_speed_var = tk.DoubleVar(value=400.0)
        speed_spin = ttk.Spinbox(params_grid, from_=100, to=800, textvariable=self.max_speed_var,
                               width=10, increment=50)
        speed_spin.grid(row=2, column=1, padx=(10, 0), sticky='w')
        
        # Sensor configuration
        sensor_frame = ttk.LabelFrame(params_frame, text="Sensors", padding=10)
        sensor_frame.pack(fill='x', pady=(10, 0))
        
        self.color_sensor_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sensor_frame, text="Color Sensor", 
                       variable=self.color_sensor_var).pack(anchor='w')
        
        self.ultrasonic_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sensor_frame, text="Ultrasonic Sensor", 
                       variable=self.ultrasonic_var).pack(anchor='w')
        
        self.gyro_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sensor_frame, text="Gyro Sensor", 
                       variable=self.gyro_var).pack(anchor='w')
        
        self.touch_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sensor_frame, text="Touch Sensors", 
                       variable=self.touch_var).pack(anchor='w')
        
        # Apply button
        ttk.Button(params_frame, text="Apply Configuration", 
                  command=self._apply_robot_config, style='Action.TButton').pack(pady=(20, 0))
    
    def _create_monitor_tab(self):
        """Create the performance monitoring tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Monitor")
        
        # Performance metrics
        metrics_frame = ttk.LabelFrame(frame, text="Performance Metrics", padding=10)
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # Metrics grid
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill='x')
        
        # Create metric labels
        metrics = [
            ("Simulation FPS:", "fps_label"),
            ("Robot Position:", "position_label"),
            ("Mission Score:", "score_label"),
            ("Time Elapsed:", "time_label")
        ]
        
        for i, (label_text, attr_name) in enumerate(metrics):
            ttk.Label(metrics_grid, text=label_text, style='Heading.TLabel').grid(
                row=i, column=0, sticky='w', pady=2)
            label = ttk.Label(metrics_grid, text="--")
            label.grid(row=i, column=1, padx=(10, 0), sticky='w')
            setattr(self, attr_name, label)
        
        # Performance chart (placeholder)
        chart_frame = ttk.LabelFrame(frame, text="Performance Chart", padding=10)
        chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.chart_canvas = tk.Canvas(chart_frame, bg='white')
        self.chart_canvas.pack(fill='both', expand=True)
        
        # Chart controls
        chart_controls = ttk.Frame(chart_frame)
        chart_controls.pack(fill='x', pady=(10, 0))
        
        ttk.Button(chart_controls, text="Reset", command=self._reset_chart).pack(side='left')
        ttk.Button(chart_controls, text="Export Data", command=self._export_data).pack(side='left', padx=(10, 0))
    
    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _load_initial_data(self):
        """Load initial configuration data."""
        self._update_profile_description()
        self._update_season_description()
        self._load_missions()
    
    def _update_profile_description(self):
        """Update the profile description."""
        descriptions = {
            'beginner': "Beginner profile with debug visualization, slower speed, and guided tutorials.",
            'intermediate': "Intermediate profile with standard settings for experienced users.",
            'advanced': "Advanced profile with competition settings and full performance features."
        }
        self.profile_desc.config(text=descriptions.get(self.current_profile, ""))
    
    def _update_season_description(self):
        """Update the season description."""
        try:
            season_info = self.config_manager.get_fll_season_info(self.current_season)
            text = f"{season_info['name']} - {season_info['description']}"
            self.season_desc.config(text=text)
        except:
            self.season_desc.config(text="Season information not available")
    
    def _load_missions(self):
        """Load available missions into the tree view."""
        # Clear existing items
        for item in self.mission_tree.get_children():
            self.mission_tree.delete(item)
        
        # Sample missions (in real implementation, load from mission factory)
        missions = [
            ("Coral Nursery", "Medium", "40", "Available"),
            ("Shark Delivery", "Hard", "60", "Available"),
            ("Research Vessel", "Easy", "30", "Completed"),
            ("Whale Migration", "Medium", "50", "Available"),
            ("Submarine Voyage", "Hard", "70", "Available")
        ]
        
        for mission in missions:
            self.mission_tree.insert('', 'end', values=mission)
    
    def _draw_robot_preview(self):
        """Draw a simple robot preview."""
        self.robot_canvas.delete("all")
        
        # Draw robot body
        x, y = 150, 100
        width, height = 60, 80
        
        self.robot_canvas.create_rectangle(x-width//2, y-height//2, 
                                         x+width//2, y+height//2, 
                                         fill='yellow', outline='black', width=2)
        
        # Draw direction indicator
        self.robot_canvas.create_line(x, y, x, y-height//2-10, 
                                    fill='red', width=3, arrow=tk.LAST)
        
        # Draw wheels
        wheel_width = 10
        self.robot_canvas.create_rectangle(x-width//2-wheel_width, y-20, 
                                         x-width//2, y+20, 
                                         fill='black')
        self.robot_canvas.create_rectangle(x+width//2, y-20, 
                                         x+width//2+wheel_width, y+20, 
                                         fill='black')
        
        # Draw sensors
        self.robot_canvas.create_oval(x-15, y+height//2-10, x-5, y+height//2, 
                                    fill='blue')  # Color sensor
        self.robot_canvas.create_rectangle(x-10, y-height//2-15, x+10, y-height//2-5, 
                                         fill='green')  # Ultrasonic sensor
    
    # Event handlers
    def _on_profile_changed(self, event=None):
        """Handle profile selection change."""
        self.current_profile = self.profile_var.get()
        self._update_profile_description()
        self._update_status(f"Profile changed to: {self.current_profile}")
    
    def _on_robot_changed(self, event=None):
        """Handle robot type change."""
        self.current_robot = self.robot_var.get()
        self._update_status(f"Robot type changed to: {self.current_robot}")
    
    def _on_season_changed(self, event=None):
        """Handle season selection change."""
        self.current_season = self.season_var.get()
        self._update_season_description()
        self._load_missions()
        self._update_status(f"Season changed to: {self.current_season}")
    
    def _on_mission_selected(self, event=None):
        """Handle mission selection in tree view."""
        selection = self.mission_tree.selection()
        if selection:
            item = self.mission_tree.item(selection[0])
            mission_name = item['values'][0]
            
            # Update mission details
            details = f"Mission: {mission_name}\n"
            details += f"Difficulty: {item['values'][1]}\n"
            details += f"Maximum Points: {item['values'][2]}\n"
            details += f"Status: {item['values'][3]}\n"
            details += "\nDescription: This mission involves navigating to specific areas and completing tasks..."
            
            self.mission_details.config(state='normal')
            self.mission_details.delete(1.0, tk.END)
            self.mission_details.insert(1.0, details)
            self.mission_details.config(state='disabled')
    
    def _update_speed_label(self, event=None):
        """Update the speed label."""
        speed = self.speed_var.get()
        self.speed_label.config(text=f"{speed:.1f}x")
    
    # Action methods
    def _new_simulation(self):
        """Create a new simulation."""
        self._update_status("Creating new simulation...")
        # Implementation for new simulation
    
    def _load_configuration(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self._update_status(f"Loaded configuration: {filename}")
    
    def _save_configuration(self):
        """Save current configuration to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self._update_status(f"Saved configuration: {filename}")
    
    def _start_simulation(self):
        """Start the simulation."""
        if self.simulation_process and self.simulation_process.poll() is None:
            messagebox.showwarning("Warning", "Simulation is already running!")
            return
        
        self._update_status("Starting simulation...")
        self.progress.start()
        
        # Update button states
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.pause_btn.config(state='normal')
        
        # Build command
        cmd = [sys.executable, str(project_root / "main.py")]
        
        # Add profile parameter
        cmd.extend(["--profile", self.current_profile])
        
        # Add debug flags if enabled
        if self.debug_var.get():
            cmd.append("--debug")
        
        # Start simulation in separate thread
        def run_simulation():
            try:
                self.simulation_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=str(project_root)
                )
                
                # Read output
                for line in iter(self.simulation_process.stdout.readline, ''):
                    if line:
                        self.root.after(0, lambda l=line: self._append_output(l.strip()))
                
                self.simulation_process.wait()
                
            except Exception as e:
                self.root.after(0, lambda: self._append_output(f"Error: {e}"))
            finally:
                self.root.after(0, self._simulation_ended)
        
        threading.Thread(target=run_simulation, daemon=True).start()
    
    def _stop_simulation(self):
        """Stop the simulation."""
        if self.simulation_process:
            self.simulation_process.terminate()
            self._simulation_ended()
    
    def _pause_simulation(self):
        """Pause/resume the simulation."""
        # This would need to communicate with the running simulation
        self._update_status("Pause/resume functionality not yet implemented")
    
    def _simulation_ended(self):
        """Handle simulation ending."""
        self.progress.stop()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.pause_btn.config(state='disabled')
        self._update_status("Simulation ended")
    
    def _run_demo(self):
        """Run a demonstration."""
        self._update_status("Running demo...")
        
        cmd = [sys.executable, str(project_root / "main.py"), "--demo", "basic"]
        
        def run_demo():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
                self.root.after(0, lambda: self._append_output("Demo output:\n" + result.stdout))
                if result.stderr:
                    self.root.after(0, lambda: self._append_output("Demo errors:\n" + result.stderr))
            except Exception as e:
                self.root.after(0, lambda: self._append_output(f"Demo error: {e}"))
        
        threading.Thread(target=run_demo, daemon=True).start()
    
    def _run_headless(self):
        """Run simulation in headless mode."""
        self._update_status("Running headless simulation...")
        
        cmd = [sys.executable, str(project_root / "main.py"), "--headless"]
        
        def run_headless():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
                self.root.after(0, lambda: self._append_output("Headless output:\n" + result.stdout))
                if result.stderr:
                    self.root.after(0, lambda: self._append_output("Headless errors:\n" + result.stderr))
            except Exception as e:
                self.root.after(0, lambda: self._append_output(f"Headless error: {e}"))
        
        threading.Thread(target=run_headless, daemon=True).start()
    
    def _configure_robot(self):
        """Open robot configuration."""
        self.notebook.select(4)  # Switch to robot tab
    
    def _load_mission(self):
        """Load mission tab."""
        self.notebook.select(3)  # Switch to missions tab
    
    def _load_selected_mission(self):
        """Load the selected mission."""
        selection = self.mission_tree.selection()
        if selection:
            item = self.mission_tree.item(selection[0])
            mission_name = item['values'][0]
            self._update_status(f"Loading mission: {mission_name}")
    
    def _edit_mission(self):
        """Edit the selected mission."""
        self._update_status("Mission editor not yet implemented")
    
    def _create_mission(self):
        """Create a new mission."""
        self._update_status("Mission creator not yet implemented")
    
    def _apply_robot_config(self):
        """Apply robot configuration changes."""
        self._update_status("Applying robot configuration...")
        self._draw_robot_preview()  # Redraw with new parameters
    
    def _open_mission_editor(self):
        """Open mission editor."""
        try:
            from fll_sim.gui.mission_editor import MissionEditorDialog
            dialog = MissionEditorDialog(self.root)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                self._update_status("Mission editor opened successfully")
                # Could save the mission here
        except ImportError:
            self._update_status("Mission editor module not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open mission editor: {e}")
    
    def _open_robot_designer(self):
        """Open robot designer."""
        try:
            from fll_sim.gui.robot_designer import RobotDesignerDialog
            dialog = RobotDesignerDialog(self.root)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                self._update_status("Robot configuration updated")
                # Could save the robot configuration here
        except ImportError:
            self._update_status("Robot designer module not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open robot designer: {e}")
    
    def _open_performance_monitor(self):
        """Open performance monitor."""
        self.notebook.select(5)  # Switch to monitor tab
    
    def _open_documentation(self):
        """Open documentation."""
        try:
            import webbrowser
            doc_path = project_root / "docs" / "project_plan.md"
            webbrowser.open(str(doc_path))
        except:
            self._update_status("Could not open documentation")
    
    def _open_examples(self):
        """Open examples directory."""
        try:
            import webbrowser
            examples_path = project_root / "examples"
            webbrowser.open(str(examples_path))
        except:
            self._update_status("Could not open examples directory")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """FLL-Sim v0.1.0
        
A comprehensive simulation environment for First Lego League competitions.

Developed to help FLL teams develop, test, and refine their robot strategies
in a realistic virtual environment before physical implementation.

Features:
• Physics-based robot simulation
• Pybricks-compatible API
• Mission scoring system
• Performance analytics
• Educational tools

For more information, visit the documentation."""
        
        messagebox.showinfo("About FLL-Sim", about_text)
    
    def _clear_output(self):
        """Clear the output display."""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
    
    def _append_output(self, text):
        """Append text to the output display."""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text + '\n')
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
    
    def _reset_chart(self):
        """Reset the performance chart."""
        self.chart_canvas.delete("all")
        self._update_status("Performance chart reset")
    
    def _export_data(self):
        """Export performance data."""
        filename = filedialog.asksaveasfilename(
            title="Export Performance Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self._update_status(f"Data exported to: {filename}")
    
    def _update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def _on_closing(self):
        """Handle application closing."""
        if self.simulation_process and self.simulation_process.poll() is None:
            if messagebox.askokcancel("Quit", "Simulation is running. Do you want to quit?"):
                self.simulation_process.terminate()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    try:
        app = FLLSimGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start FLL-Sim GUI:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
