"""
Curriculum Integration Module

Aligns FLL-Sim educational features with STEM education standards.
Integrates with teacher dashboards. Extensible API for mapping content to standards and reporting progress.
"""

from typing import Dict, List, Optional


class CurriculumStandard:
    """Represents a STEM curriculum standard."""

    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description


class CurriculumMapping:
    """Maps tutorials and assessments to curriculum standards."""

    def __init__(self):
        self.mapping: Dict[str, List[CurriculumStandard]] = {}
        self.progress: Dict[str, Dict[str, float]] = {}

    def add_mapping(
        self, feature_name: str, standards: List[CurriculumStandard]
    ):
        self.mapping[feature_name] = standards

    def get_standards(
        self, feature_name: str
    ) -> Optional[List[CurriculumStandard]]:
        return self.mapping.get(feature_name)

    def report_progress(self, feature_name: str, user_id: str, percent: float):
        if feature_name not in self.progress:
            self.progress[feature_name] = {}
        self.progress[feature_name][user_id] = percent

    def get_progress(self, feature_name: str, user_id: str) -> Optional[float]:
        return self.progress.get(feature_name, {}).get(user_id)
