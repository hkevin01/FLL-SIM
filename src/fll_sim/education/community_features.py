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

    def add_content(self, content: SharedContent):
        self.shared_content.append(content)

    def get_all_content(self) -> List[SharedContent]:
        return self.shared_content

    def add_discussion(self, content_title: str, message: str):
        if content_title not in self.user_discussions:
            self.user_discussions[content_title] = []
        self.user_discussions[content_title].append(message)

    def get_discussions(self, content_title: str) -> List[str]:
        return self.user_discussions.get(content_title, [])
