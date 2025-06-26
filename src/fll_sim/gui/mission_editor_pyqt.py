"""
Mission Editor GUI Component using PyQt6

This module provides a visual editor for creating and modifying FLL missions.
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from fll_sim.environment.mission import FLLMissionFactory, Mission


class MissionEditorDialog(QDialog):
    """
    Mission editor dialog for creating and editing FLL missions using PyQt6.
    """
    
    def __init__(self, parent, mission: Optional[Mission] = None):
        """Initialize the mission editor dialog."""
        super().__init__(parent)
        self.mission = mission
        self.result = None
        
        self.setWindowTitle("Mission Editor")
        self.setGeometry(200, 200, 600, 400)
        self.setModal(True)
        
        self._create_interface()
        self._load_mission_data()
    
    def _create_interface(self):
        """Create the mission editor interface."""
        layout = QVBoxLayout(self)
        
        # Mission info section
        info_group = QGroupBox("Mission Information")
        info_layout = QFormLayout(info_group)
        
        # Name
        self.name_edit = QTextEdit()
        self.name_edit.setMaximumHeight(30)
        info_layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        info_layout.addRow("Description:", self.description_edit)
        
        # Season
        self.season_combo = QComboBox()
        self.season_combo.addItems(['2024', '2023'])
        info_layout.addRow("Season:", self.season_combo)
        
        layout.addWidget(info_group)
        
        # Templates section
        template_group = QGroupBox("Mission Templates")
        template_layout = QVBoxLayout(template_group)
        
        # Available templates list
        self.templates_list = QListWidget()
        self.templates_list.setMaximumHeight(150)
        template_layout.addWidget(self.templates_list)
        
        # Load available templates
        self._load_templates()
        
        # Template buttons
        template_btn_layout = QHBoxLayout()
        
        load_template_btn = QPushButton("Load Template")
        load_template_btn.clicked.connect(self._load_template)
        template_btn_layout.addWidget(load_template_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_templates)
        template_btn_layout.addWidget(refresh_btn)
        
        template_btn_layout.addStretch()
        template_layout.addLayout(template_btn_layout)
        
        layout.addWidget(template_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Mission")
        save_btn.clicked.connect(self._save_mission)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _load_templates(self):
        """Load available mission templates."""
        self.templates_list.clear()
        
        # Add some example templates
        templates = [
            "Coral Nursery (Transport)",
            "Shark Habitat (Precision)",
            "Ocean Cleanup (Innovation)",
            "Submersible (Bonus)",
            "Custom Mission"
        ]
        
        for template in templates:
            item = QListWidgetItem(template)
            self.templates_list.addItem(item)
    
    def _load_mission_data(self):
        """Load mission data into the interface."""
        if self.mission:
            self.name_edit.setPlainText(getattr(self.mission, 'name', ''))
            self.description_edit.setPlainText(
                getattr(self.mission, 'description', ''))
            season = getattr(self.mission, 'fll_season', '2024-SUBMERGED')
            if '-' in season:
                self.season_combo.setCurrentText(season.split('-')[0])
            else:
                self.season_combo.setCurrentText('2024')
    
    def _load_template(self):
        """Load selected mission template."""
        current_item = self.templates_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", 
                              "Please select a template to load.")
            return
        
        template_name = current_item.text()
        
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
            self.name_edit.setPlainText(data["name"])
            self.description_edit.setPlainText(data["description"])
    
    def _save_mission(self):
        """Save the mission."""
        name = self.name_edit.toPlainText().strip()
        if not name:
            QMessageBox.critical(self, "Error", "Mission name is required.")
            return
        
        self.result = {
            'name': name,
            'description': self.description_edit.toPlainText(),
            'season': self.season_combo.currentText(),
        }
        
        QMessageBox.information(self, "Success", 
                              "Mission template created successfully!")
        self.accept()
    
    def get_result(self):
        """Get the dialog result."""
        return self.result
