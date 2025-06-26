"""
Mission Editor GUI Component

This module provides a visual editor for creating and modifying FLL missions.
Allows users to design mission layouts, set scoring rules, and define 
objectives.
"""

import json
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from fll_sim.environment.mission import FLLMissionFactory, Mission


class MissionEditorDialog:
    """
    Mission editor dialog for creating and editing FLL missions.
    """
    
    def __init__(self, parent, mission: Optional[Mission] = None):
        """Initialize the mission editor dialog."""
        self.parent = parent
        self.mission = mission
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Mission Editor")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_interface()
        self._load_mission_data()
    
    def _create_interface(self):
        """Create the mission editor interface."""
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Mission info section
        info_frame = ttk.LabelFrame(main_frame, text="Mission Information", 
                                   padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        
        # Name
        ttk.Label(info_frame, text="Name:").grid(
            row=0, column=0, sticky='w', padx=(0, 10))
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var, width=40).grid(
            row=0, column=1, sticky='ew')
        
        # Description
        ttk.Label(info_frame, text="Description:").grid(
            row=1, column=0, sticky='nw', padx=(0, 10), pady=(10, 0))
        self.description_text = tk.Text(info_frame, height=4, width=40)
        self.description_text.grid(row=1, column=1, sticky='ew', 
                                  pady=(10, 0))
        
        # Season
        ttk.Label(info_frame, text="Season:").grid(
            row=2, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.season_var = tk.StringVar(value="2024")
        season_combo = ttk.Combobox(info_frame, textvariable=self.season_var, 
                                   values=['2024', '2023'], state='readonly', 
                                   width=15)
        season_combo.grid(row=2, column=1, sticky='w', pady=(10, 0))
        
        info_frame.columnconfigure(1, weight=1)
        
        # Templates section
        template_frame = ttk.LabelFrame(main_frame, text="Mission Templates", 
                                       padding=10)
        template_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Available templates list
        self.templates_listbox = tk.Listbox(template_frame, height=8)
        self.templates_listbox.pack(fill='both', expand=True)
        
        # Load available templates
        self._load_templates()
        
        # Template buttons
        template_btn_frame = ttk.Frame(template_frame)
        template_btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(template_btn_frame, text="Load Template", 
                  command=self._load_template).pack(side='left', padx=(0, 5))
        ttk.Button(template_btn_frame, text="Refresh", 
                  command=self._load_templates).pack(side='left')
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Mission", 
                  command=self._save_mission).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=self._cancel).pack(side='right')
    
    def _load_templates(self):
        """Load available mission templates."""
        self.templates_listbox.delete(0, 'end')
        
        # Add some example templates
        templates = [
            "Coral Nursery (Transport)",
            "Shark Habitat (Precision)",
            "Ocean Cleanup (Innovation)",
            "Submersible (Bonus)",
            "Custom Mission"
        ]
        
        for template in templates:
            self.templates_listbox.insert('end', template)
    
    def _load_mission_data(self):
        """Load mission data into the interface."""
        if self.mission:
            self.name_var.set(getattr(self.mission, 'name', ''))
            self.description_text.insert('1.0', 
                                        getattr(self.mission, 'description', ''))
            season = getattr(self.mission, 'fll_season', '2024-SUBMERGED')
            if '-' in season:
                self.season_var.set(season.split('-')[0])
            else:
                self.season_var.set('2024')
    
    def _load_template(self):
        """Load selected mission template."""
        selection = self.templates_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", 
                                 "Please select a template to load.")
            return
        
        template_name = self.templates_listbox.get(selection[0])
        
        # Example template data
        template_data = {
            "Coral Nursery (Transport)": {
                "name": "Coral Nursery",
                "description": "Transport coral pieces to the nursery area for "
                             "restoration points.",
            },
            "Shark Habitat (Precision)": {
                "name": "Shark Habitat",
                "description": "Precisely place sharks in their designated "
                             "habitat zones.",
            },
            "Ocean Cleanup (Innovation)": {
                "name": "Ocean Cleanup",
                "description": "Remove debris from the ocean using innovative "
                             "techniques.",
            },
            "Submersible (Bonus)": {
                "name": "Submersible",
                "description": "Operate the submersible for bonus exploration "
                             "points.",
            }
        }
        
        if template_name in template_data:
            data = template_data[template_name]
            self.name_var.set(data["name"])
            self.description_text.delete('1.0', 'end')
            self.description_text.insert('1.0', data["description"])
    
    def _save_mission(self):
        """Save the mission."""
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Mission name is required.")
            return
        
        self.result = {
            'name': self.name_var.get().strip(),
            'description': self.description_text.get('1.0', 'end-1c'),
            'season': self.season_var.get(),
        }
        
        messagebox.showinfo("Success", "Mission template created successfully!")
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()
