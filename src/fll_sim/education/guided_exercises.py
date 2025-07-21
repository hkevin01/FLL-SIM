"""
Guided Programming Exercises Module

Provides interactive coding exercises with hints, solutions, and progress tracking.
Designed for modularity, extensibility, and integration with the main GUI.
"""

class ExerciseManager:
    """Manages guided exercises, hints, solutions, and user progress."""
    def __init__(self):
        # Initialize exercise registry and user progress tracking
        self.exercises = {}
        self.user_progress = {}

    def load_exercises(self):
        """Load available exercises from content directory or plugins."""
        # Example: Load exercises from a static dictionary
        self.exercises = {
            "ex1": {
                "steps": ["step1", "step2"],
                "solution": "print('Hello World')",
                "hints": ["Use print()"]
            },
        }

    def start_exercise(self, exercise_id):
        """Begin a guided exercise session for the given exercise ID."""
        if exercise_id in self.exercises:
            self.user_progress[exercise_id] = {"step": 0, "completed": False}
            return self.exercises[exercise_id]["steps"][0]
        return None

    def provide_hint(self, exercise_id, step):
        """Provide a hint for the current step in an exercise."""
        ex = self.exercises.get(exercise_id)
        if ex and step < len(ex["hints"]):
            return ex["hints"][step]
        return "No hint available."

    def check_solution(self, exercise_id, user_code):
        """Check user-submitted code against the solution."""
        ex = self.exercises.get(exercise_id)
        if ex and user_code.strip() == ex["solution"].strip():
            self.user_progress[exercise_id]["completed"] = True
            return True
        return False

    def track_progress(self, user_id, exercise_id, step):
        """Track user progress through exercise steps."""
        key = f"{user_id}:{exercise_id}"
        self.user_progress[key] = {"step": step}

    def get_progress(self, user_id, exercise_id):
        """Return current progress for a user in an exercise."""
        key = f"{user_id}:{exercise_id}"
        return self.user_progress.get(key, {"step": 0})
