"""
Community Features Module

Provides shared content and collaboration tools for FLL-Sim users.
Extensible API for content sharing, discussion, and collaboration.
"""

from typing import List, Dict


class SharedContent:
    """Represents a piece of shared content."""

    def __init__(self, title: str, author: str, content: str):
        self.title = title
        self.author = author
        self.content = content


class CommunityManager:
    """Manages shared content and collaboration features."""

    def __init__(self):
        self.shared_content: List[SharedContent] = []
        self.user_discussions: Dict[str, List[str]] = {}
        self.user_likes: Dict[str, int] = {}

    def add_content(self, content: SharedContent):
        self.shared_content.append(content)
        self.user_likes[content.title] = 0

    def get_all_content(self) -> List[SharedContent]:
        return self.shared_content

    def add_discussion(self, content_title: str, message: str):
        if content_title not in self.user_discussions:
            self.user_discussions[content_title] = []
        self.user_discussions[content_title].append(message)

    def get_discussions(self, content_title: str) -> List[str]:
        return self.user_discussions.get(content_title, [])

    def like_content(self, content_title: str):
        if content_title in self.user_likes:
            self.user_likes[content_title] += 1

    def get_likes(self, content_title: str) -> int:
        return self.user_likes.get(content_title, 0)

    # Community features for Phase 4.5 and beyond
    def add_mission(self, mission_id, mission_data):
        if not hasattr(self, 'missions'):
            self.missions = {}
        self.missions[mission_id] = mission_data

    def add_robot(self, robot_id, robot_data):
        if not hasattr(self, 'robots'):
            self.robots = {}
        self.robots[robot_id] = robot_data

    def add_project(self, project_id, project_data):
        if not hasattr(self, 'projects'):
            self.projects = {}
        self.projects[project_id] = project_data

    def add_forum_post(self, forum_id, post):
        if not hasattr(self, 'forums'):
            self.forums = {}
        if forum_id not in self.forums:
            self.forums[forum_id] = []
        self.forums[forum_id].append(post)

    def add_competition(self, comp_id, comp_data):
        if not hasattr(self, 'competitions'):
            self.competitions = {}
        self.competitions[comp_id] = comp_data

    def get_mission(self, mission_id):
        return getattr(self, 'missions', {}).get(mission_id)

    def get_robot(self, robot_id):
        return getattr(self, 'robots', {}).get(robot_id)

    def get_project(self, project_id):
        return getattr(self, 'projects', {}).get(project_id)

    def get_forum_posts(self, forum_id):
        return getattr(self, 'forums', {}).get(forum_id, [])

    def get_competition(self, comp_id):
        return getattr(self, 'competitions', {}).get(comp_id)
