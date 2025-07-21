"""
Unit tests for FLL-Sim educational modules:
- tutorial system
- assessment tools
- curriculum integration
- community features
"""

import unittest
from src.fll_sim.education.tutorial_system import (
    TutorialStep,
    Tutorial,
)
from src.fll_sim.education.assessment_tools import (
    Assessment,
    AssessmentResult,
    AssessmentManager,
)
from src.fll_sim.education.curriculum_integration import (
    CurriculumStandard,
    CurriculumMapping,
)
from src.fll_sim.education.community_features import (
    SharedContent,
    CommunityManager,
)


class TestTutorialSystem(unittest.TestCase):
    def test_tutorial_progress(self):
        steps = [
            TutorialStep('Step 1', 'Intro'),
            TutorialStep('Step 2', 'Do something')
        ]
        tutorial = Tutorial('Demo', steps)
        self.assertEqual(tutorial.current_step, 0)
        tutorial.next_step()
        self.assertEqual(tutorial.current_step, 1)


class DummyAssessment(Assessment):
    def grade(self, submission):
        return AssessmentResult(score=100.0, feedback='Great job!')


class TestAssessmentManager(unittest.TestCase):
    def test_assessment_grading(self):
        manager = AssessmentManager()
        assessment = DummyAssessment('Quiz')
        manager.add_assessment(assessment)
        result = manager.grade_assessment('Quiz', 'answer')
        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.feedback, 'Great job!')


class TestCurriculumMapping(unittest.TestCase):
    def test_mapping(self):
        mapping = CurriculumMapping()
        std = CurriculumStandard('CS1', 'Description')
        mapping.add_mapping('Tutorial', [std])
        self.assertEqual(mapping.get_standards('Tutorial')[0].code, 'CS1')


class TestCommunityManager(unittest.TestCase):
    def test_content_and_discussion(self):
        manager = CommunityManager()
        content = SharedContent('Title', 'Author', 'Content')
        manager.add_content(content)
        self.assertEqual(manager.get_all_content()[0].title, 'Title')
        manager.add_discussion('Title', 'Nice work!')
        self.assertEqual(manager.get_discussions('Title')[0], 'Nice work!')


if __name__ == '__main__':
    unittest.main()
