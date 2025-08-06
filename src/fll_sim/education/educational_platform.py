"""
Enhanced Educational System Integration for FLL-Sim

Integrates all educational components: interactive tutorials, visual programming,
mission builder, and student tracking into a cohesive learning platform.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.fll_sim.education.interactive_tutorial_system import \
    InteractiveTutorialSystem
from src.fll_sim.education.mission_builder import MissionBuilder
from src.fll_sim.education.student_tracking import StudentTrackingSystem
from src.fll_sim.education.visual_programming import VisualProgrammingInterface
from src.fll_sim.utils.docker_strategy import UniversalDockerStrategy
from src.fll_sim.utils.logger import FLLLogger


class EducationalPlatform:
    """Main educational platform integrating all learning components."""

    def __init__(self):
        self.logger = FLLLogger('EducationalPlatform')

        # Initialize core systems
        self.tutorial_system = InteractiveTutorialSystem()
        self.visual_programming = VisualProgrammingInterface()
        self.mission_builder = MissionBuilder(self.tutorial_system)
        self.student_tracking = StudentTrackingSystem()
        self.docker_strategy = UniversalDockerStrategy()

        # Current session state
        self.current_student_id: Optional[str] = None
        self.current_session_id: Optional[str] = None
        self.active_activities: Dict[str, Any] = {}

        # Integration settings
        self.auto_track_progress = True
        self.auto_award_achievements = True
        self.generate_recommendations = True

        self.logger.info("Educational Platform initialized successfully")

    def start_student_session(self, student_name: str, grade_level: str = "",
                            class_section: str = "") -> str:
        """Start a new student learning session."""
        # Register student if not exists
        existing_students = [
            s for s in self.student_tracking.students.values()
            if s.name == student_name
        ]

        if existing_students:
            self.current_student_id = existing_students[0].student_id
        else:
            self.current_student_id = self.student_tracking.register_student(
                student_name, grade_level, class_section
            )

        self.current_session_id = str(uuid.uuid4())

        self.logger.info(f"Started session for student: {student_name}")
        return self.current_session_id

    def start_tutorial(self, tutorial_id: str) -> Dict[str, Any]:
        """Start a tutorial and track progress."""
        if not self.current_student_id:
            return {'error': 'No active student session'}

        # Start tutorial
        tutorial = self.tutorial_system.get_tutorial(tutorial_id)
        if not tutorial:
            return {'error': 'Tutorial not found'}

        # Start tracking activity
        activity_id = self.student_tracking.start_activity(
            student_id=self.current_student_id,
            activity_type=self.student_tracking.ActivityType.TUTORIAL,
            activity_id=tutorial_id,
            activity_name=tutorial.title,
            session_id=self.current_session_id
        )

        self.active_activities[tutorial_id] = activity_id

        # Start tutorial
        self.tutorial_system.start_tutorial(tutorial_id)

        return {
            'tutorial': {
                'id': tutorial.id,
                'title': tutorial.title,
                'description': tutorial.description,
                'category': tutorial.category,
                'difficulty': tutorial.difficulty,
                'estimated_time': tutorial.estimated_time,
                'current_step': 0,
                'total_steps': len(tutorial.steps)
            },
            'activity_id': activity_id
        }

    def complete_tutorial_step(self, tutorial_id: str, success: bool = True,
                             code_written: str = "", notes: str = "") -> Dict[str, Any]:
        """Complete a tutorial step and update progress."""
        result = self.tutorial_system.complete_current_step(tutorial_id, success)

        if success and tutorial_id in self.active_activities:
            # Update activity progress
            activity_id = self.active_activities[tutorial_id]
            if activity_id in self.student_tracking.activities:
                activity = self.student_tracking.activities[activity_id]
                activity.program_code += f"\n# Step completed:\n{code_written}"

                if notes:
                    activity.reflection_notes += f"\n{notes}"

        # Check if tutorial is complete
        tutorial = self.tutorial_system.get_tutorial(tutorial_id)
        if tutorial and result.get('tutorial_complete'):
            self.complete_tutorial(tutorial_id, success=True)

        return result

    def complete_tutorial(self, tutorial_id: str, success: bool = True) -> Dict[str, Any]:
        """Complete a tutorial and update student progress."""
        if tutorial_id not in self.active_activities:
            return {'error': 'Tutorial not active'}

        activity_id = self.active_activities[tutorial_id]
        tutorial = self.tutorial_system.get_tutorial(tutorial_id)

        # Calculate score based on completion
        score = 100 if success else 0

        # Complete activity tracking
        self.student_tracking.complete_activity(
            activity_id=activity_id,
            success=success,
            score=score,
            max_score=100
        )

        # Remove from active activities
        del self.active_activities[tutorial_id]

        return {
            'tutorial_completed': True,
            'tutorial_title': tutorial.title if tutorial else 'Unknown',
            'score': score,
            'achievements_earned': self._get_recent_achievements()
        }

    def start_mission(self, mission_id: str) -> Dict[str, Any]:
        """Start a mission and track progress."""
        if not self.current_student_id:
            return {'error': 'No active student session'}

        mission = self.mission_builder.missions.get(mission_id)
        if not mission:
            return {'error': 'Mission not found'}

        # Start tracking activity
        activity_id = self.student_tracking.start_activity(
            student_id=self.current_student_id,
            activity_type=self.student_tracking.ActivityType.MISSION,
            activity_id=mission_id,
            activity_name=mission.name,
            session_id=self.current_session_id
        )

        self.active_activities[mission_id] = activity_id

        return {
            'mission': {
                'id': mission.id,
                'name': mission.name,
                'description': mission.description,
                'difficulty_level': mission.difficulty_level,
                'estimated_duration': mission.estimated_duration,
                'objectives': len(mission.objectives),
                'max_score': self.mission_builder._calculate_max_score(mission)
            },
            'activity_id': activity_id
        }

    def complete_mission(self, mission_id: str, score: int,
                        completion_time: int, success: bool = True,
                        program_code: str = "", reflection: str = "") -> Dict[str, Any]:
        """Complete a mission and update student progress."""
        if mission_id not in self.active_activities:
            return {'error': 'Mission not active'}

        activity_id = self.active_activities[mission_id]
        mission = self.mission_builder.missions.get(mission_id)
        max_score = self.mission_builder._calculate_max_score(mission) if mission else 100

        # Complete activity tracking
        self.student_tracking.complete_activity(
            activity_id=activity_id,
            success=success,
            score=score,
            max_score=max_score,
            program_code=program_code,
            reflection_notes=reflection
        )

        # Update activity with timing
        if activity_id in self.student_tracking.activities:
            self.student_tracking.activities[activity_id].time_spent = completion_time

        # Remove from active activities
        del self.active_activities[mission_id]

        return {
            'mission_completed': True,
            'mission_name': mission.name if mission else 'Unknown',
            'score': score,
            'max_score': max_score,
            'completion_time': completion_time,
            'achievements_earned': self._get_recent_achievements()
        }

    def start_visual_programming(self, project_name: str = "New Project") -> Dict[str, Any]:
        """Start a visual programming session."""
        if not self.current_student_id:
            return {'error': 'No active student session'}

        # Create new visual program
        program_id = self.visual_programming.create_program(project_name)

        # Start tracking activity
        activity_id = self.student_tracking.start_activity(
            student_id=self.current_student_id,
            activity_type=self.student_tracking.ActivityType.PROGRAMMING,
            activity_id=program_id,
            activity_name=f"Visual Programming: {project_name}",
            session_id=self.current_session_id
        )

        self.active_activities[program_id] = activity_id

        return {
            'program_id': program_id,
            'activity_id': activity_id,
            'available_blocks': self.visual_programming.get_available_block_types(),
            'workspace_info': {
                'name': project_name,
                'created_at': datetime.now().isoformat()
            }
        }

    def save_visual_program(self, program_id: str, reflection: str = "") -> Dict[str, Any]:
        """Save a visual programming project and update progress."""
        if program_id not in self.active_activities:
            return {'error': 'Program not active'}

        # Generate code from visual blocks
        generated_code = self.visual_programming.generate_code(program_id)
        validation_result = self.visual_programming.validate_program(program_id)

        activity_id = self.active_activities[program_id]

        # Update activity with generated code
        if activity_id in self.student_tracking.activities:
            activity = self.student_tracking.activities[activity_id]
            activity.program_code = generated_code
            activity.reflection_notes = reflection

            # Count lines of code for achievements
            lines_count = len(generated_code.split('\n'))
            activity.skills_practiced.append(f"coding_{lines_count}_lines")

        return {
            'saved': True,
            'generated_code': generated_code,
            'validation': validation_result,
            'lines_of_code': len(generated_code.split('\n'))
        }

    def complete_visual_programming(self, program_id: str,
                                  reflection: str = "") -> Dict[str, Any]:
        """Complete a visual programming session."""
        if program_id not in self.active_activities:
            return {'error': 'Program not active'}

        # Save program first
        save_result = self.save_visual_program(program_id, reflection)

        activity_id = self.active_activities[program_id]

        # Determine success based on validation
        success = save_result.get('validation', {}).get('is_valid', False)
        score = 85 if success else 60  # Give partial credit for attempt

        # Complete activity tracking
        self.student_tracking.complete_activity(
            activity_id=activity_id,
            success=success,
            score=score,
            max_score=100,
            program_code=save_result.get('generated_code', ''),
            reflection_notes=reflection
        )

        # Remove from active activities
        del self.active_activities[program_id]

        return {
            'programming_completed': True,
            'success': success,
            'score': score,
            'generated_code': save_result.get('generated_code', ''),
            'achievements_earned': self._get_recent_achievements()
        }

    def get_student_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive student dashboard data."""
        if not self.current_student_id:
            return {'error': 'No active student session'}

        # Get student analytics
        analytics = self.student_tracking.get_student_analytics(self.current_student_id)

        # Get available content
        available_tutorials = self.tutorial_system.get_available_tutorials()
        available_missions = self.mission_builder.get_mission_list()

        # Get recommendations
        recommendations = self._generate_learning_recommendations()

        # Get recent progress
        student = self.student_tracking.get_student(self.current_student_id)
        recent_achievements = sorted(
            analytics.get('achievements', []),
            key=lambda x: x['earned_at'],
            reverse=True
        )[:3]

        return {
            'student_info': analytics.get('student_info', {}),
            'progress_summary': {
                'level': student.level if student else 1,
                'total_points': student.total_points if student else 0,
                'achievements_count': len(recent_achievements),
                'activities_completed': analytics.get('performance_analytics', {}).get('completed_activities', 0)
            },
            'performance_trends': analytics.get('performance_analytics', {}),
            'skill_progress': analytics.get('skill_mastery', {}),
            'recent_achievements': recent_achievements,
            'available_content': {
                'tutorials': len(available_tutorials),
                'missions': len(available_missions),
                'visual_programming': True
            },
            'recommendations': recommendations,
            'active_session': {
                'session_id': self.current_session_id,
                'started_at': datetime.now().isoformat(),
                'active_activities': len(self.active_activities)
            }
        }

    def get_instructor_dashboard(self, class_id: Optional[str] = None) -> Dict[str, Any]:
        """Get instructor dashboard with class analytics."""
        if class_id:
            class_analytics = self.student_tracking.get_class_analytics(class_id)
            return {
                'class_analytics': class_analytics,
                'content_management': {
                    'tutorials': len(self.tutorial_system.tutorials),
                    'missions': len(self.mission_builder.missions),
                    'achievements': len(self.student_tracking.achievements)
                },
                'student_progress': class_analytics.get('student_summaries', [])
            }
        else:
            # Overall system dashboard
            return {
                'system_overview': {
                    'total_students': len(self.student_tracking.students),
                    'total_tutorials': len(self.tutorial_system.tutorials),
                    'total_missions': len(self.mission_builder.missions),
                    'total_achievements': len(self.student_tracking.achievements)
                },
                'recent_activity': self._get_recent_system_activity(),
                'content_statistics': self._get_content_statistics()
            }

    def setup_development_environment(self, project_path: str = ".") -> Dict[str, Any]:
        """Setup Docker development environment for the educational platform."""
        try:
            # Generate Docker configuration for Python project
            generated_files = self.docker_strategy.generate_development_environment(
                project_type=self.docker_strategy.ProjectType.PYTHON_BASIC,
                include_database=True,
                include_cache=True,
                output_dir=f"{project_path}/docker"
            )

            # Validate setup
            validation = self.docker_strategy.validate_docker_setup(project_path)

            return {
                'setup_successful': True,
                'generated_files': list(generated_files.keys()),
                'validation': validation,
                'next_steps': [
                    "Run 'docker/scripts/dev-up.sh' to start development environment",
                    "Access the application at http://localhost:8000",
                    "View logs with 'docker-compose logs -f'",
                    "Run tests with 'docker/scripts/test.sh'"
                ]
            }
        except Exception as e:
            self.logger.error(f"Failed to setup development environment: {e}")
            return {
                'setup_successful': False,
                'error': str(e)
            }

    def _get_recent_achievements(self) -> List[Dict[str, Any]]:
        """Get recently earned achievements for current student."""
        if not self.current_student_id:
            return []

        student = self.student_tracking.get_student(self.current_student_id)
        if not student:
            return []

        # Get achievements earned in the last 5 minutes (recent)
        recent_cutoff = datetime.now().timestamp() - 300  # 5 minutes ago

        recent_achievements = []
        for achievement_id, earned_at in student.achievements_earned.items():
            if earned_at.timestamp() > recent_cutoff:
                achievement = self.student_tracking.achievements.get(achievement_id)
                if achievement:
                    recent_achievements.append({
                        'id': achievement.id,
                        'name': achievement.name,
                        'description': achievement.description,
                        'icon': achievement.icon,
                        'points': achievement.points,
                        'earned_at': earned_at.isoformat()
                    })

        return recent_achievements

    def _generate_learning_recommendations(self) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations."""
        if not self.current_student_id:
            return []

        recommendations = []
        student = self.student_tracking.get_student(self.current_student_id)
        if not student:
            return recommendations

        # Analyze skill gaps
        beginner_skills = [
            skill for skill, assessment in student.skill_assessments.items()
            if assessment.level.value == 'beginner'
        ]

        # Recommend tutorials for skill gaps
        for skill in beginner_skills[:2]:  # Top 2 skill gaps
            matching_tutorials = [
                t for t in self.tutorial_system.tutorials.values()
                if skill in t.skills_developed
            ]
            if matching_tutorials:
                tutorial = matching_tutorials[0]  # Get first match
                recommendations.append({
                    'type': 'tutorial',
                    'title': f"Improve {skill.replace('_', ' ').title()}",
                    'description': f"Try the '{tutorial.title}' tutorial",
                    'action': {
                        'type': 'start_tutorial',
                        'tutorial_id': tutorial.id
                    }
                })

        # Recommend missions based on progress
        completed_missions = sum(
            1 for activity_id in student.activities
            if (activity_id in self.student_tracking.activities and
                self.student_tracking.activities[activity_id].type.value == 'mission' and
                self.student_tracking.activities[activity_id].success)
        )

        if completed_missions < 3:
            easy_missions = [
                m for m in self.mission_builder.missions.values()
                if m.difficulty_level <= 2
            ]
            if easy_missions:
                mission = easy_missions[0]
                recommendations.append({
                    'type': 'mission',
                    'title': 'Try a Mission Challenge',
                    'description': f"Take on the '{mission.name}' mission",
                    'action': {
                        'type': 'start_mission',
                        'mission_id': mission.id
                    }
                })

        # Recommend visual programming
        programming_activities = sum(
            1 for activity_id in student.activities
            if (activity_id in self.student_tracking.activities and
                self.student_tracking.activities[activity_id].type.value == 'programming')
        )

        if programming_activities < 2:
            recommendations.append({
                'type': 'programming',
                'title': 'Try Visual Programming',
                'description': 'Create programs using drag-and-drop blocks',
                'action': {
                    'type': 'start_visual_programming'
                }
            })

        return recommendations[:3]  # Return top 3 recommendations

    def _get_recent_system_activity(self) -> List[Dict[str, Any]]:
        """Get recent system-wide activity."""
        activities = []

        # Get recent student registrations
        recent_students = sorted(
            self.student_tracking.students.values(),
            key=lambda s: s.created_at,
            reverse=True
        )[:5]

        for student in recent_students:
            activities.append({
                'type': 'student_registration',
                'message': f"New student registered: {student.name}",
                'timestamp': student.created_at.isoformat()
            })

        # Get recent completed activities
        all_activities = sorted(
            [a for a in self.student_tracking.activities.values() if a.completed_at],
            key=lambda a: a.completed_at,
            reverse=True
        )[:10]

        for activity in all_activities:
            student = self.student_tracking.get_student(activity.student_id)
            student_name = student.name if student else "Unknown"

            activities.append({
                'type': 'activity_completion',
                'message': f"{student_name} completed {activity.activity_name}",
                'timestamp': activity.completed_at.isoformat(),
                'success': activity.success
            })

        return sorted(activities, key=lambda a: a['timestamp'], reverse=True)[:10]

    def _get_content_statistics(self) -> Dict[str, Any]:
        """Get statistics about educational content."""
        return {
            'tutorials': {
                'total': len(self.tutorial_system.tutorials),
                'by_category': self.tutorial_system.get_tutorial_categories_stats(),
                'completion_rate': self._calculate_tutorial_completion_rate()
            },
            'missions': {
                'total': len(self.mission_builder.missions),
                'by_difficulty': self._get_mission_difficulty_stats(),
                'average_score': self._calculate_average_mission_score()
            },
            'achievements': {
                'total': len(self.student_tracking.achievements),
                'by_type': self._get_achievement_type_stats(),
                'most_earned': self._get_most_earned_achievements()
            }
        }

    def _calculate_tutorial_completion_rate(self) -> float:
        """Calculate overall tutorial completion rate."""
        tutorial_activities = [
            a for a in self.student_tracking.activities.values()
            if a.type.value == 'tutorial' and a.completed_at is not None
        ]

        if not tutorial_activities:
            return 0.0

        completed = sum(1 for a in tutorial_activities if a.success)
        return (completed / len(tutorial_activities)) * 100

    def _get_mission_difficulty_stats(self) -> Dict[int, int]:
        """Get mission count by difficulty level."""
        stats = {}
        for mission in self.mission_builder.missions.values():
            level = mission.difficulty_level
            stats[level] = stats.get(level, 0) + 1
        return stats

    def _calculate_average_mission_score(self) -> float:
        """Calculate average score across all mission attempts."""
        mission_activities = [
            a for a in self.student_tracking.activities.values()
            if (a.type.value == 'mission' and a.score is not None and
                a.max_score is not None)
        ]

        if not mission_activities:
            return 0.0

        total_percentage = sum(
            (a.score / a.max_score) * 100 for a in mission_activities
        )
        return total_percentage / len(mission_activities)

    def _get_achievement_type_stats(self) -> Dict[str, int]:
        """Get achievement count by type."""
        stats = {}
        for achievement in self.student_tracking.achievements.values():
            achievement_type = achievement.type.value
            stats[achievement_type] = stats.get(achievement_type, 0) + 1
        return stats

    def _get_most_earned_achievements(self) -> List[Dict[str, Any]]:
        """Get most frequently earned achievements."""
        earning_counts = {}

        for student in self.student_tracking.students.values():
            for achievement_id in student.achievements_earned:
                earning_counts[achievement_id] = earning_counts.get(achievement_id, 0) + 1

        # Sort by earning frequency
        most_earned = sorted(
            earning_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        result = []
        for achievement_id, count in most_earned:
            achievement = self.student_tracking.achievements.get(achievement_id)
            if achievement:
                result.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'earned_count': count
                })

        return result
