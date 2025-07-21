"""
Assessment Tools Module

Provides automated progress tracking and grading for FLL-Sim educational features.
Extensible API for integrating with curriculum and reporting systems.
"""


class AssessmentResult:
    """Represents the result of an assessment."""

    def __init__(self, score: float, feedback: str):
        self.score = score
        self.feedback = feedback


class Assessment:
    """Base class for assessments."""

    def __init__(self, name: str):
        self.name = name

    def grade(self, submission):
        raise NotImplementedError


class AssessmentManager:
    """Manages assessments and user progress."""

    def __init__(self):
        self.assessments = {}
        self.user_scores = {}

    def add_assessment(self, assessment: Assessment):
        self.assessments[assessment.name] = assessment

    def grade_assessment(self, name: str, submission):
        assessment = self.assessments.get(name)
        if assessment:
            result = assessment.grade(submission)
            self.user_scores[name] = result.score
            return result
        return AssessmentResult(0.0, "Assessment not found.")

    def get_user_score(self, name: str):
        return self.user_scores.get(name, None)


class QuizAssessment(Assessment):
    """Example implementation of a quiz assessment."""

    def __init__(self, name: str, correct_answers: dict):
        super().__init__(name)
        self.correct_answers = correct_answers

    def grade(self, submission):
        score = 0
        feedback = []
        for q, ans in submission.items():
            if self.correct_answers.get(q) == ans:
                score += 1
            else:
                feedback.append(f"Incorrect answer for {q}")
        total = len(self.correct_answers)
        percent = score / total * 100 if total > 0 else 0
        feedback_msg = "; ".join(feedback) if feedback else "All correct!"
        return AssessmentResult(percent, feedback_msg)
