"""
Enhanced Student Progress Tracking System for FLL-Sim

Provides comprehensive analytics, achievements, progress tracking, and
reporting capabilities for educational use.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from fll_sim.utils.logger import FLLLogger


class SkillLevel(Enum):
    """Student skill proficiency levels."""
    BEGINNER = "beginner"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ActivityType(Enum):
    """Types of student activities that can be tracked."""
    TUTORIAL = "tutorial"
    MISSION = "mission"
    PROGRAMMING = "programming"
    ASSESSMENT = "assessment"
    PROJECT = "project"
    CHALLENGE = "challenge"


class AchievementType(Enum):
    """Types of achievements."""
    MILESTONE = "milestone"
    SKILL_MASTERY = "skill_mastery"
    CREATIVITY = "creativity"
    PERSEVERANCE = "perseverance"
    COLLABORATION = "collaboration"
    LEADERSHIP = "leadership"
    TECHNICAL = "technical"
    PROBLEM_SOLVING = "problem_solving"


@dataclass
class LearningObjective:
    """Represents a specific learning objective."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = "general"
    difficulty_level: int = 1  # 1-5 scale
    prerequisite_objectives: List[str] = field(default_factory=list)
    skills_developed: List[str] = field(default_factory=list)
    assessment_criteria: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Achievement:
    """Represents an achievement or badge that can be earned."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: AchievementType = AchievementType.MILESTONE
    icon: str = "🏆"

    # Criteria for earning the achievement
    criteria: Dict[str, Any] = field(default_factory=dict)

    # Points and rewards
    points: int = 0

    # Metadata
    difficulty: int = 1  # 1-5 scale
    is_hidden: bool = False  # Hidden until earned
    category: str = "general"
    prerequisite_achievements: List[str] = field(default_factory=list)

    # Educational value
    learning_objectives: List[str] = field(default_factory=list)
    skills_demonstrated: List[str] = field(default_factory=list)


@dataclass
class SkillAssessment:
    """Assessment of a specific skill."""
    skill_name: str = ""
    level: SkillLevel = SkillLevel.BEGINNER
    confidence: float = 0.0  # 0.0 to 1.0
    last_demonstrated: Optional[datetime] = None
    evidence_activities: List[str] = field(default_factory=list)  # IDs
    instructor_notes: str = ""


@dataclass
class StudentActivity:
    """Record of a student activity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str = ""
    type: ActivityType = ActivityType.TUTORIAL
    activity_id: str = ""  # Tutorial, mission, etc. ID
    activity_name: str = ""

    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    time_spent: Optional[int] = None  # seconds

    # Performance
    score: Optional[int] = None
    max_score: Optional[int] = None
    attempts: int = 1
    success: bool = False

    # Learning data
    learning_objectives_addressed: List[str] = field(default_factory=list)
    skills_practiced: List[str] = field(default_factory=list)
    mistakes_made: List[str] = field(default_factory=list)
    help_requested: List[str] = field(default_factory=list)

    # Context
    session_id: str = ""
    group_activity: bool = False
    peer_collaboration: bool = False

    # Artifacts
    program_code: str = ""
    solution_approach: str = ""
    reflection_notes: str = ""


@dataclass
class StudentProgress:
    """Comprehensive student progress tracking."""
    student_id: str = ""
    name: str = ""
    grade_level: str = ""
    class_section: str = ""

    # Overall progress
    total_points: int = 0
    level: int = 1
    experience_points: int = 0

    # Time tracking
    total_time_spent: int = 0  # seconds
    sessions_count: int = 0
    last_active: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    # Achievements
    achievements_earned: Dict[str, datetime] = field(default_factory=dict)

    # Skills assessment
    skill_assessments: Dict[str, SkillAssessment] = field(default_factory=dict)

    # Learning objectives
    objectives_completed: Dict[str, datetime] = field(default_factory=dict)
    objectives_in_progress: List[str] = field(default_factory=list)

    # Activity history
    activities: List[str] = field(default_factory=list)  # Activity IDs

    # Performance trends
    recent_scores: List[Tuple[datetime, int]] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

    # Preferences and learning style
    preferred_activities: List[str] = field(default_factory=list)
    learning_style_indicators: Dict[str, float] = field(default_factory=dict)

    # Goals and planning
    current_goals: List[str] = field(default_factory=list)
    goal_deadlines: Dict[str, datetime] = field(default_factory=dict)


@dataclass
class ClassProgress:
    """Class-wide progress and analytics."""
    class_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    class_name: str = ""
    instructor: str = ""
    academic_year: str = ""

    # Students
    students: List[str] = field(default_factory=list)  # Student IDs

    # Class metrics
    average_score: float = 0.0
    completion_rate: float = 0.0
    engagement_level: float = 0.0

    # Learning objectives
    class_objectives: List[str] = field(default_factory=list)
    objectives_mastery: Dict[str, float] = field(default_factory=dict)

    # Common challenges
    common_mistakes: List[Tuple[str, int]] = field(default_factory=list)
    help_topics: List[Tuple[str, int]] = field(default_factory=list)

    # Collaborative activities
    group_projects: List[str] = field(default_factory=list)
    peer_learning_sessions: List[str] = field(default_factory=list)


class StudentTrackingSystem:
    """Main system for tracking student progress and analytics."""

    def __init__(self):
        self.logger = FLLLogger('StudentTracking')

        # Core data storage
        self.students: Dict[str, StudentProgress] = {}
        self.activities: Dict[str, StudentActivity] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.learning_objectives: Dict[str, LearningObjective] = {}
        self.classes: Dict[str, ClassProgress] = {}

        # Current session tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        # Analytics cache
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_expiry: Dict[str, datetime] = {}

        # Initialize default content
        self._initialize_default_achievements()
        self._initialize_default_objectives()

        self.logger.info("Student Tracking System initialized")

    def _initialize_default_achievements(self):
        """Initialize default achievements."""
        # Milestone achievements
        first_steps = Achievement(
            name="First Steps",
            description="Complete your first tutorial",
            type=AchievementType.MILESTONE,
            icon="👶",
            criteria={"tutorials_completed": 1},
            points=10,
            difficulty=1,
            category="tutorials",
            skills_demonstrated=["basic_navigation"]
        )

        mission_master = Achievement(
            name="Mission Master",
            description="Complete 5 missions successfully",
            type=AchievementType.MILESTONE,
            icon="🎯",
            criteria={"missions_completed": 5},
            points=50,
            difficulty=2,
            category="missions",
            skills_demonstrated=["mission_planning", "robot_control"]
        )

        code_warrior = Achievement(
            name="Code Warrior",
            description="Write 100 lines of robot code",
            type=AchievementType.TECHNICAL,
            icon="⚔️",
            criteria={"code_lines_written": 100},
            points=30,
            difficulty=2,
            category="programming",
            skills_demonstrated=["programming", "problem_solving"]
        )

        persistent_learner = Achievement(
            name="Persistent Learner",
            description="Retry a failed mission until successful",
            type=AchievementType.PERSEVERANCE,
            icon="💪",
            criteria={"retry_success": True},
            points=25,
            difficulty=2,
            category="mindset",
            skills_demonstrated=["persistence", "growth_mindset"]
        )

        sensor_specialist = Achievement(
            name="Sensor Specialist",
            description="Successfully use all sensor types",
            type=AchievementType.SKILL_MASTERY,
            icon="📡",
            criteria={"sensors_used": ["color", "distance", "gyro", "touch"]},
            points=40,
            difficulty=3,
            category="sensors",
            skills_demonstrated=["sensor_integration", "data_analysis"]
        )

        creative_coder = Achievement(
            name="Creative Coder",
            description="Create an innovative solution approach",
            type=AchievementType.CREATIVITY,
            icon="🎨",
            criteria={"innovative_solution": True},
            points=35,
            difficulty=3,
            category="creativity",
            skills_demonstrated=["creative_thinking", "innovation"]
        )

        for achievement in [first_steps, mission_master, code_warrior,
                          persistent_learner, sensor_specialist, creative_coder]:
            self.achievements[achievement.id] = achievement

        self.logger.info(f"Initialized {len(self.achievements)} achievements")

    def _initialize_default_objectives(self):
        """Initialize default learning objectives."""
        objectives = [
            LearningObjective(
                name="Basic Robot Movement",
                description="Control robot movement in all directions",
                category="movement",
                difficulty_level=1,
                skills_developed=["motor_control", "spatial_reasoning"],
                assessment_criteria={
                    "forward_movement": True,
                    "turning": True,
                    "precise_positioning": True
                }
            ),
            LearningObjective(
                name="Sensor Integration",
                description="Use sensors to gather environmental data",
                category="sensors",
                difficulty_level=2,
                prerequisite_objectives=["Basic Robot Movement"],
                skills_developed=["data_collection", "sensor_interpretation"],
                assessment_criteria={
                    "color_detection": True,
                    "distance_measurement": True,
                    "sensor_based_decisions": True
                }
            ),
            LearningObjective(
                name="Mission Strategy",
                description="Plan and execute mission objectives efficiently",
                category="strategy",
                difficulty_level=3,
                prerequisite_objectives=["Basic Robot Movement", "Sensor Integration"],
                skills_developed=["strategic_planning", "optimization"],
                assessment_criteria={
                    "mission_completion": True,
                    "time_efficiency": True,
                    "resource_optimization": True
                }
            ),
            LearningObjective(
                name="Problem Decomposition",
                description="Break complex problems into manageable parts",
                category="problem_solving",
                difficulty_level=3,
                skills_developed=["analytical_thinking", "modular_design"],
                assessment_criteria={
                    "problem_analysis": True,
                    "solution_planning": True,
                    "implementation_steps": True
                }
            ),
            LearningObjective(
                name="Code Debugging",
                description="Identify and fix errors in robot programs",
                category="programming",
                difficulty_level=4,
                prerequisite_objectives=["Problem Decomposition"],
                skills_developed=["debugging", "logical_reasoning"],
                assessment_criteria={
                    "error_identification": True,
                    "systematic_testing": True,
                    "solution_verification": True
                }
            )
        ]

        for objective in objectives:
            self.learning_objectives[objective.id] = objective

        self.logger.info(f"Initialized {len(self.learning_objectives)} learning objectives")

    # Student Management
    def register_student(self, name: str, grade_level: str = "",
                        class_section: str = "") -> str:
        """Register a new student."""
        student = StudentProgress(
            name=name,
            grade_level=grade_level,
            class_section=class_section
        )

        self.students[student.student_id] = student

        # Initialize skill assessments
        default_skills = [
            "programming", "problem_solving", "robot_control", "sensor_usage",
            "mission_planning", "debugging", "creativity", "collaboration"
        ]

        for skill in default_skills:
            student.skill_assessments[skill] = SkillAssessment(
                skill_name=skill,
                level=SkillLevel.BEGINNER,
                confidence=0.0
            )

        self.logger.info(f"Registered student: {name}")
        return student.student_id

    def get_student(self, student_id: str) -> Optional[StudentProgress]:
        """Get student progress data."""
        return self.students.get(student_id)

    def update_student_info(self, student_id: str, **kwargs) -> bool:
        """Update student information."""
        if student_id not in self.students:
            return False

        student = self.students[student_id]
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)

        return True

    # Activity Tracking
    def start_activity(self, student_id: str, activity_type: ActivityType,
                      activity_id: str, activity_name: str,
                      session_id: Optional[str] = None) -> str:
        """Start tracking a new student activity."""
        if student_id not in self.students:
            self.logger.error(f"Student not found: {student_id}")
            return ""

        activity = StudentActivity(
            student_id=student_id,
            type=activity_type,
            activity_id=activity_id,
            activity_name=activity_name,
            session_id=session_id or str(uuid.uuid4())
        )

        self.activities[activity.id] = activity
        self.students[student_id].activities.append(activity.id)

        # Update session tracking
        if activity.session_id not in self.active_sessions:
            self.active_sessions[activity.session_id] = {
                'student_id': student_id,
                'started_at': datetime.now(),
                'activities': []
            }

        self.active_sessions[activity.session_id]['activities'].append(activity.id)

        self.logger.debug(f"Started activity: {activity_name} for {student_id}")
        return activity.id

    def complete_activity(self, activity_id: str, success: bool = True,
                         score: Optional[int] = None,
                         max_score: Optional[int] = None,
                         program_code: str = "",
                         reflection_notes: str = "") -> bool:
        """Complete an activity and record results."""
        if activity_id not in self.activities:
            return False

        activity = self.activities[activity_id]
        activity.completed_at = datetime.now()
        activity.success = success
        activity.score = score
        activity.max_score = max_score
        activity.program_code = program_code
        activity.reflection_notes = reflection_notes

        # Calculate time spent
        if activity.started_at:
            time_spent = (activity.completed_at - activity.started_at).total_seconds()
            activity.time_spent = int(time_spent)

        # Update student progress
        student = self.students[activity.student_id]
        student.last_active = activity.completed_at
        student.sessions_count += 1

        if activity.time_spent:
            student.total_time_spent += activity.time_spent

        if score is not None:
            student.recent_scores.append((activity.completed_at, score))
            # Keep only last 10 scores
            if len(student.recent_scores) > 10:
                student.recent_scores = student.recent_scores[-10:]

        # Check for achievements
        self._check_achievements(activity.student_id, activity)

        # Update skill assessments
        self._update_skill_assessments(activity.student_id, activity)

        # Clear analytics cache for this student
        self._invalidate_analytics_cache(activity.student_id)

        self.logger.debug(f"Completed activity: {activity.activity_name}")
        return True

    def record_mistake(self, activity_id: str, mistake_description: str):
        """Record a mistake made during an activity."""
        if activity_id in self.activities:
            activity = self.activities[activity_id]
            activity.mistakes_made.append(mistake_description)

    def record_help_request(self, activity_id: str, help_topic: str):
        """Record a help request during an activity."""
        if activity_id in self.activities:
            activity = self.activities[activity_id]
            activity.help_requested.append(help_topic)

    def update_activity_attempts(self, activity_id: str):
        """Increment attempt counter for an activity."""
        if activity_id in self.activities:
            self.activities[activity_id].attempts += 1

    # Achievement System
    def _check_achievements(self, student_id: str, activity: StudentActivity):
        """Check if student earned any achievements from this activity."""
        student = self.students[student_id]

        for achievement_id, achievement in self.achievements.items():
            # Skip if already earned
            if achievement_id in student.achievements_earned:
                continue

            # Check if prerequisites are met
            if not self._check_achievement_prerequisites(student, achievement):
                continue

            # Check criteria
            if self._evaluate_achievement_criteria(student, achievement, activity):
                self._award_achievement(student_id, achievement_id)

    def _check_achievement_prerequisites(self, student: StudentProgress,
                                       achievement: Achievement) -> bool:
        """Check if student meets achievement prerequisites."""
        for prereq_id in achievement.prerequisite_achievements:
            if prereq_id not in student.achievements_earned:
                return False
        return True

    def _evaluate_achievement_criteria(self, student: StudentProgress,
                                     achievement: Achievement,
                                     latest_activity: StudentActivity) -> bool:
        """Evaluate if achievement criteria are met."""
        criteria = achievement.criteria

        # Tutorial completion criteria
        if "tutorials_completed" in criteria:
            completed_tutorials = sum(
                1 for activity_id in student.activities
                if (activity_id in self.activities and
                    self.activities[activity_id].type == ActivityType.TUTORIAL and
                    self.activities[activity_id].success)
            )
            if completed_tutorials < criteria["tutorials_completed"]:
                return False

        # Mission completion criteria
        if "missions_completed" in criteria:
            completed_missions = sum(
                1 for activity_id in student.activities
                if (activity_id in self.activities and
                    self.activities[activity_id].type == ActivityType.MISSION and
                    self.activities[activity_id].success)
            )
            if completed_missions < criteria["missions_completed"]:
                return False

        # Code lines written
        if "code_lines_written" in criteria:
            total_lines = sum(
                len(self.activities[activity_id].program_code.split('\n'))
                for activity_id in student.activities
                if (activity_id in self.activities and
                    self.activities[activity_id].program_code)
            )
            if total_lines < criteria["code_lines_written"]:
                return False

        # Retry success (persistence)
        if "retry_success" in criteria:
            if (latest_activity.attempts <= 1 or not latest_activity.success):
                return False

        # Sensors used
        if "sensors_used" in criteria:
            required_sensors = set(criteria["sensors_used"])
            used_sensors = set()

            for activity_id in student.activities:
                if activity_id in self.activities:
                    activity = self.activities[activity_id]
                    # This would need to be extracted from program analysis
                    # For now, simplified check based on activity content
                    if "color" in activity.program_code.lower():
                        used_sensors.add("color")
                    if "distance" in activity.program_code.lower():
                        used_sensors.add("distance")
                    if "gyro" in activity.program_code.lower():
                        used_sensors.add("gyro")
                    if "touch" in activity.program_code.lower():
                        used_sensors.add("touch")

            if not required_sensors.issubset(used_sensors):
                return False

        # Innovation/creativity (simplified)
        if "innovative_solution" in criteria:
            # This would need more sophisticated analysis
            if (len(latest_activity.program_code) > 200 and
                latest_activity.success and
                "creative" in latest_activity.reflection_notes.lower()):
                return True
            return False

        return True

    def _award_achievement(self, student_id: str, achievement_id: str):
        """Award an achievement to a student."""
        student = self.students[student_id]
        achievement = self.achievements[achievement_id]

        student.achievements_earned[achievement_id] = datetime.now()
        student.total_points += achievement.points

        # Add skills demonstrated
        for skill in achievement.skills_demonstrated:
            if skill in student.skill_assessments:
                assessment = student.skill_assessments[skill]
                assessment.confidence = min(1.0, assessment.confidence + 0.1)
                assessment.last_demonstrated = datetime.now()

        self.logger.info(f"Achievement awarded: {achievement.name} to {student.name}")

    # Skill Assessment
    def _update_skill_assessments(self, student_id: str, activity: StudentActivity):
        """Update skill assessments based on activity performance."""
        student = self.students[student_id]

        # Map activity types to skills
        skill_mapping = {
            ActivityType.TUTORIAL: ["basic_skills", "learning_ability"],
            ActivityType.MISSION: ["mission_planning", "robot_control"],
            ActivityType.PROGRAMMING: ["programming", "problem_solving"],
            ActivityType.ASSESSMENT: ["knowledge_application"]
        }

        relevant_skills = skill_mapping.get(activity.type, [])
        relevant_skills.extend(activity.skills_practiced)

        for skill in relevant_skills:
            if skill in student.skill_assessments:
                assessment = student.skill_assessments[skill]

                # Update based on success and score
                if activity.success:
                    confidence_boost = 0.05
                    if activity.score and activity.max_score:
                        score_ratio = activity.score / activity.max_score
                        confidence_boost *= score_ratio

                    assessment.confidence = min(1.0, assessment.confidence + confidence_boost)
                    assessment.last_demonstrated = activity.completed_at
                    assessment.evidence_activities.append(activity.id)

                    # Update skill level based on confidence
                    if assessment.confidence >= 0.8:
                        assessment.level = SkillLevel.EXPERT
                    elif assessment.confidence >= 0.6:
                        assessment.level = SkillLevel.ADVANCED
                    elif assessment.confidence >= 0.4:
                        assessment.level = SkillLevel.PROFICIENT
                    elif assessment.confidence >= 0.2:
                        assessment.level = SkillLevel.DEVELOPING
                    else:
                        assessment.level = SkillLevel.BEGINNER

                # Keep only recent evidence (last 5 activities)
                if len(assessment.evidence_activities) > 5:
                    assessment.evidence_activities = assessment.evidence_activities[-5:]

    def assess_skill_manually(self, student_id: str, skill_name: str,
                             level: SkillLevel, confidence: float,
                             notes: str = "") -> bool:
        """Manually assess a student's skill level."""
        if student_id not in self.students:
            return False

        student = self.students[student_id]

        if skill_name not in student.skill_assessments:
            student.skill_assessments[skill_name] = SkillAssessment(
                skill_name=skill_name
            )

        assessment = student.skill_assessments[skill_name]
        assessment.level = level
        assessment.confidence = max(0.0, min(1.0, confidence))
        assessment.instructor_notes = notes
        assessment.last_demonstrated = datetime.now()

        return True

    # Analytics and Reporting
    def get_student_analytics(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a student."""
        cache_key = f"student_analytics_{student_id}"

        # Check cache
        if (cache_key in self.analytics_cache and
            cache_key in self.cache_expiry and
            self.cache_expiry[cache_key] > datetime.now()):
            return self.analytics_cache[cache_key]

        if student_id not in self.students:
            return {}

        student = self.students[student_id]
        student_activities = [
            self.activities[aid] for aid in student.activities
            if aid in self.activities
        ]

        # Time-based analytics
        total_time = student.total_time_spent
        avg_session_time = (total_time / student.sessions_count
                           if student.sessions_count > 0 else 0)

        # Performance analytics
        completed_activities = [a for a in student_activities if a.completed_at]
        success_rate = (sum(1 for a in completed_activities if a.success) /
                       len(completed_activities) if completed_activities else 0)

        scored_activities = [a for a in completed_activities
                           if a.score is not None and a.max_score is not None]
        avg_score_percentage = (
            sum(a.score / a.max_score for a in scored_activities) /
            len(scored_activities) if scored_activities else 0
        ) * 100

        # Recent performance trend
        recent_trend = "stable"
        if len(student.recent_scores) >= 3:
            recent_avg = sum(score for _, score in student.recent_scores[-3:]) / 3
            older_avg = sum(score for _, score in student.recent_scores[-6:-3]) / 3 if len(student.recent_scores) >= 6 else recent_avg

            if recent_avg > older_avg * 1.1:
                recent_trend = "improving"
            elif recent_avg < older_avg * 0.9:
                recent_trend = "declining"

        # Activity breakdown
        activity_breakdown = {}
        for activity_type in ActivityType:
            count = sum(1 for a in student_activities if a.type == activity_type)
            activity_breakdown[activity_type.value] = count

        # Skill mastery overview
        skill_mastery = {}
        for skill, assessment in student.skill_assessments.items():
            skill_mastery[skill] = {
                'level': assessment.level.value,
                'confidence': assessment.confidence,
                'last_demonstrated': (assessment.last_demonstrated.isoformat()
                                    if assessment.last_demonstrated else None)
            }

        # Learning objectives progress
        objectives_progress = {
            'completed': len(student.objectives_completed),
            'in_progress': len(student.objectives_in_progress),
            'total_available': len(self.learning_objectives)
        }

        # Common challenges
        all_mistakes = []
        for activity in student_activities:
            all_mistakes.extend(activity.mistakes_made)

        mistake_frequency = {}
        for mistake in all_mistakes:
            mistake_frequency[mistake] = mistake_frequency.get(mistake, 0) + 1

        common_challenges = sorted(mistake_frequency.items(),
                                 key=lambda x: x[1], reverse=True)[:5]

        analytics = {
            'student_info': {
                'id': student.student_id,
                'name': student.name,
                'grade_level': student.grade_level,
                'class_section': student.class_section,
                'level': student.level,
                'total_points': student.total_points,
                'achievements_count': len(student.achievements_earned)
            },
            'time_analytics': {
                'total_time_hours': round(total_time / 3600, 2),
                'sessions_count': student.sessions_count,
                'avg_session_time_minutes': round(avg_session_time / 60, 2),
                'last_active': (student.last_active.isoformat()
                              if student.last_active else None)
            },
            'performance_analytics': {
                'success_rate': round(success_rate * 100, 1),
                'avg_score_percentage': round(avg_score_percentage, 1),
                'recent_trend': recent_trend,
                'total_activities': len(student_activities),
                'completed_activities': len(completed_activities)
            },
            'activity_breakdown': activity_breakdown,
            'skill_mastery': skill_mastery,
            'objectives_progress': objectives_progress,
            'common_challenges': common_challenges,
            'achievements': [
                {
                    'id': aid,
                    'name': self.achievements[aid].name,
                    'earned_at': earned_at.isoformat(),
                    'points': self.achievements[aid].points
                }
                for aid, earned_at in student.achievements_earned.items()
                if aid in self.achievements
            ]
        }

        # Cache the result
        self.analytics_cache[cache_key] = analytics
        self.cache_expiry[cache_key] = datetime.now() + timedelta(minutes=15)

        return analytics

    def get_class_analytics(self, class_id: str) -> Dict[str, Any]:
        """Get analytics for an entire class."""
        if class_id not in self.classes:
            return {}

        class_data = self.classes[class_id]
        class_students = [self.students[sid] for sid in class_data.students
                         if sid in self.students]

        if not class_students:
            return {'error': 'No students found in class'}

        # Aggregate student analytics
        all_activities = []
        total_points = 0
        total_achievements = 0

        for student in class_students:
            student_activities = [
                self.activities[aid] for aid in student.activities
                if aid in self.activities
            ]
            all_activities.extend(student_activities)
            total_points += student.total_points
            total_achievements += len(student.achievements_earned)

        # Class performance metrics
        completed_activities = [a for a in all_activities if a.completed_at]
        class_success_rate = (
            sum(1 for a in completed_activities if a.success) /
            len(completed_activities) if completed_activities else 0
        )

        scored_activities = [a for a in completed_activities
                           if a.score is not None and a.max_score is not None]
        class_avg_score = (
            sum(a.score / a.max_score for a in scored_activities) /
            len(scored_activities) if scored_activities else 0
        ) * 100

        # Individual student summaries
        student_summaries = []
        for student in class_students:
            analytics = self.get_student_analytics(student.student_id)
            student_summaries.append({
                'id': student.student_id,
                'name': student.name,
                'total_points': student.total_points,
                'achievements_count': len(student.achievements_earned),
                'success_rate': analytics['performance_analytics']['success_rate'],
                'recent_trend': analytics['performance_analytics']['recent_trend']
            })

        # Common challenges across class
        all_mistakes = []
        for activity in all_activities:
            all_mistakes.extend(activity.mistakes_made)

        mistake_frequency = {}
        for mistake in all_mistakes:
            mistake_frequency[mistake] = mistake_frequency.get(mistake, 0) + 1

        class_challenges = sorted(mistake_frequency.items(),
                                key=lambda x: x[1], reverse=True)[:10]

        return {
            'class_info': {
                'id': class_data.class_id,
                'name': class_data.class_name,
                'instructor': class_data.instructor,
                'student_count': len(class_students)
            },
            'class_performance': {
                'success_rate': round(class_success_rate * 100, 1),
                'avg_score_percentage': round(class_avg_score, 1),
                'total_activities': len(all_activities),
                'avg_points_per_student': round(total_points / len(class_students), 1),
                'avg_achievements_per_student': round(total_achievements / len(class_students), 1)
            },
            'student_summaries': sorted(student_summaries,
                                      key=lambda x: x['total_points'], reverse=True),
            'common_challenges': class_challenges,
            'activity_distribution': {
                activity_type.value: sum(1 for a in all_activities if a.type == activity_type)
                for activity_type in ActivityType
            }
        }

    def generate_progress_report(self, student_id: str,
                               include_recommendations: bool = True) -> Dict[str, Any]:
        """Generate a comprehensive progress report for a student."""
        analytics = self.get_student_analytics(student_id)
        if not analytics:
            return {}

        student = self.students[student_id]

        # Strengths and areas for improvement
        strengths = []
        improvement_areas = []

        # Analyze skill assessments
        for skill, assessment in student.skill_assessments.items():
            if assessment.level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]:
                strengths.append(skill)
            elif assessment.level == SkillLevel.BEGINNER:
                improvement_areas.append(skill)

        # Recommendations
        recommendations = []
        if include_recommendations:
            # Based on skill gaps
            for area in improvement_areas[:3]:  # Top 3 areas
                recommendations.append(
                    f"Focus on {area} through targeted practice and tutorials"
                )

            # Based on performance trends
            if analytics['performance_analytics']['recent_trend'] == 'declining':
                recommendations.append(
                    "Consider reviewing recent concepts and seeking additional support"
                )
            elif analytics['performance_analytics']['recent_trend'] == 'improving':
                recommendations.append(
                    "Great progress! Consider taking on more challenging activities"
                )

            # Based on activity patterns
            activity_counts = analytics['activity_breakdown']
            if activity_counts.get('mission', 0) < 3:
                recommendations.append(
                    "Try more mission activities to apply your skills in context"
                )

        return {
            'student': analytics['student_info'],
            'summary': {
                'overall_performance': analytics['performance_analytics'],
                'time_investment': analytics['time_analytics'],
                'achievements': len(analytics['achievements']),
                'skill_mastery_count': sum(
                    1 for skill_data in analytics['skill_mastery'].values()
                    if skill_data['level'] in ['advanced', 'expert']
                )
            },
            'strengths': strengths,
            'improvement_areas': improvement_areas,
            'recommendations': recommendations,
            'recent_achievements': sorted(
                analytics['achievements'],
                key=lambda x: x['earned_at'],
                reverse=True
            )[:5],
            'objectives_progress': analytics['objectives_progress'],
            'generated_at': datetime.now().isoformat()
        }

    # Class Management
    def create_class(self, class_name: str, instructor: str,
                    academic_year: str = "") -> str:
        """Create a new class."""
        class_progress = ClassProgress(
            class_name=class_name,
            instructor=instructor,
            academic_year=academic_year
        )

        self.classes[class_progress.class_id] = class_progress
        self.logger.info(f"Created class: {class_name}")
        return class_progress.class_id

    def add_student_to_class(self, student_id: str, class_id: str) -> bool:
        """Add a student to a class."""
        if student_id not in self.students or class_id not in self.classes:
            return False

        class_data = self.classes[class_id]
        if student_id not in class_data.students:
            class_data.students.append(student_id)

            # Update student's class section
            self.students[student_id].class_section = class_data.class_name

        return True

    def remove_student_from_class(self, student_id: str, class_id: str) -> bool:
        """Remove a student from a class."""
        if class_id not in self.classes:
            return False

        class_data = self.classes[class_id]
        if student_id in class_data.students:
            class_data.students.remove(student_id)

            # Clear student's class section if this was their only class
            if student_id in self.students:
                other_classes = [
                    c for c in self.classes.values()
                    if student_id in c.students and c.class_id != class_id
                ]
                if not other_classes:
                    self.students[student_id].class_section = ""

        return True

    # Utility Methods
    def _invalidate_analytics_cache(self, student_id: str):
        """Invalidate analytics cache for a student."""
        cache_key = f"student_analytics_{student_id}"
        if cache_key in self.analytics_cache:
            del self.analytics_cache[cache_key]
        if cache_key in self.cache_expiry:
            del self.cache_expiry[cache_key]

    def export_student_data(self, student_id: str,
                           include_activities: bool = True) -> Dict[str, Any]:
        """Export student data for backup or transfer."""
        if student_id not in self.students:
            return {}

        student = self.students[student_id]

        exported_data = {
            'student_info': {
                'id': student.student_id,
                'name': student.name,
                'grade_level': student.grade_level,
                'class_section': student.class_section,
                'created_at': student.created_at.isoformat()
            },
            'progress': {
                'total_points': student.total_points,
                'level': student.level,
                'experience_points': student.experience_points,
                'total_time_spent': student.total_time_spent,
                'sessions_count': student.sessions_count,
                'last_active': (student.last_active.isoformat()
                              if student.last_active else None)
            },
            'achievements': [
                {
                    'achievement_id': aid,
                    'earned_at': earned_at.isoformat()
                }
                for aid, earned_at in student.achievements_earned.items()
            ],
            'skill_assessments': {
                skill: {
                    'level': assessment.level.value,
                    'confidence': assessment.confidence,
                    'last_demonstrated': (assessment.last_demonstrated.isoformat()
                                        if assessment.last_demonstrated else None),
                    'instructor_notes': assessment.instructor_notes
                }
                for skill, assessment in student.skill_assessments.items()
            },
            'objectives': {
                'completed': [
                    {
                        'objective_id': oid,
                        'completed_at': completed_at.isoformat()
                    }
                    for oid, completed_at in student.objectives_completed.items()
                ],
                'in_progress': student.objectives_in_progress
            }
        }

        if include_activities:
            activities_data = []
            for activity_id in student.activities:
                if activity_id in self.activities:
                    activity = self.activities[activity_id]
                    activities_data.append({
                        'id': activity.id,
                        'type': activity.type.value,
                        'activity_name': activity.activity_name,
                        'started_at': activity.started_at.isoformat(),
                        'completed_at': (activity.completed_at.isoformat()
                                       if activity.completed_at else None),
                        'success': activity.success,
                        'score': activity.score,
                        'max_score': activity.max_score,
                        'time_spent': activity.time_spent,
                        'attempts': activity.attempts
                    })

            exported_data['activities'] = activities_data

        return exported_data

    def get_achievement_list(self) -> List[Dict[str, Any]]:
        """Get list of all available achievements."""
        return [
            {
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'type': achievement.type.value,
                'icon': achievement.icon,
                'points': achievement.points,
                'difficulty': achievement.difficulty,
                'category': achievement.category,
                'is_hidden': achievement.is_hidden
            }
            for achievement in self.achievements.values()
        ]

    def get_learning_objectives_list(self) -> List[Dict[str, Any]]:
        """Get list of all learning objectives."""
        return [
            {
                'id': objective.id,
                'name': objective.name,
                'description': objective.description,
                'category': objective.category,
                'difficulty_level': objective.difficulty_level,
                'skills_developed': objective.skills_developed
            }
            for objective in self.learning_objectives.values()
        ]
