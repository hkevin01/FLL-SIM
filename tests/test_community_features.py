"""
Test Community Features

Unit and integration tests for CommunityManager and shared content features.
"""
import unittest
from src.fll_sim.education.community_features import (
    CommunityManager,
    SharedContent
)


class TestCommunityManager(unittest.TestCase):
    def setUp(self):
        self.manager = CommunityManager()
        self.content = SharedContent(
            "Mission 1",
            "Alice",
            "Sample mission data"
        )
        self.manager.add_content(self.content)

    def test_add_content(self):
        self.assertEqual(len(self.manager.get_all_content()), 1)
        self.assertEqual(self.manager.get_likes("Mission 1"), 0)

    def test_like_content(self):
        self.manager.like_content("Mission 1")
        self.assertEqual(self.manager.get_likes("Mission 1"), 1)

    def test_discussion(self):
        self.manager.add_discussion("Mission 1", "Great mission!")
        self.assertIn(
            "Great mission!",
            self.manager.get_discussions("Mission 1")
        )

    def test_add_mission(self):
        self.manager.add_mission("m1", {"name": "Mission 1"})
        self.assertEqual(self.manager.get_mission("m1")["name"], "Mission 1")

    def test_add_robot(self):
        self.manager.add_robot("r1", {"type": "Standard"})
        self.assertEqual(self.manager.get_robot("r1")["type"], "Standard")

    def test_add_project(self):
        self.manager.add_project("p1", {"title": "Project 1"})
        self.assertEqual(self.manager.get_project("p1")["title"], "Project 1")

    def test_forum_posts(self):
        self.manager.add_forum_post("f1", "Welcome!")
        self.assertIn("Welcome!", self.manager.get_forum_posts("f1"))

    def test_competition(self):
        self.manager.add_competition("c1", {"event": "Qualifier"})
        self.assertEqual(
            self.manager.get_competition("c1")["event"],
            "Qualifier"
        )


if __name__ == "__main__":
    unittest.main()
