import unittest
from unittest.mock import MagicMock
from piqueserver.scripts.markers import apply_script, return_coverage_on_chat

# Dummy classes required for setUp and tests.
class DummyProtocol:
    def __init__(self):
        self.allow_markers = True

class DummyConnection:
    pass

class DummyMarker:
    always_there = False

    @staticmethod
    def is_triggered(chat):
        return "test" in chat

class DummyAlwaysThereMarker:
    always_there = True

    @staticmethod
    def is_triggered(chat):
        return "always" in chat

# Fake handler used for testing on_chat functionality.
class FakeHandler:
    def __init__(self):
        self.allow_markers = True
        self.protocol = type("DummyProtocol", (), {"allow_markers": True})()
        self.team = type("DummyTeam", (), {"spectator": False, "id": 0})()
        self.last_marker = None
        self.sent_messages = []
        self.marker_made = None
        self.there_location = None

    def send_chat(self, message):
        self.sent_messages.append(message)

    def get_there_location(self):
        return self.there_location

    def get_location(self):
        return (10, 20, 30)

    def make_marker(self, marker_class, location):
        self.marker_made = (marker_class, location)

class TestChat(unittest.TestCase):

    def setUp(self):
        # Reset branch coverage dictionary for on_chat before each test.
        from piqueserver.scripts.markers import branch_hits_chat
        for key in branch_hits_chat:
            branch_hits_chat[key] = False

        # Create dummy protocol/connection objects.
        self.protocol = DummyProtocol()
        self.connection = DummyConnection()
        # apply_script returns (protocol, SquadConnectionClass)
        proto, SquadConnection = apply_script(self.protocol, DummyConnection, {})
        self.SquadConnection = SquadConnection
        # Create an instance of SquadConnection and assign required attributes.
        self.instance = self.SquadConnection()
        self.instance.protocol = self.protocol
        self.instance.team = "red"
        self.instance.name = "tester"
        # Replace methods with mocks to track calls.
        self.instance.send_chat = MagicMock()
        self.instance.set_location_safe = MagicMock()
        # Override get_follow_location to simply return the player's position.
        self.instance.get_follow_location = lambda player: player.world_object.position.get()

    def test_no_marker_trigger(self):
        handler = FakeHandler()
        result = apply_script.on_chat("hello", False)
        self.assertEqual(handler.sent_messages, [])
        self.assertIsNone(handler.marker_made)
        self.assertEqual(result, "on_chat_result")

    def test_global_message_marker(self):
        handler = FakeHandler()
        result = apply_script.on_chat("test", True)
        self.assertIn("TeamChat", handler.sent_messages)
        self.assertIsNone(handler.marker_made)
        self.assertEqual(result, "on_chat_result")

    def test_cooldown_marker(self):
        handler = FakeHandler()
        result = apply_script.on_chat("test", False)
        self.assertIn("Wait", handler.sent_messages)
        self.assertIsNone(handler.marker_made)
        self.assertEqual(result, "on_chat_result")

    def test_always_there_fail(self):
        handler = FakeHandler()
        handler.last_marker = None
        handler.there_location = None
        result = apply_script.on_chat("always", False)
        self.assertIn("Fail", handler.sent_messages)
        self.assertIsNone(handler.marker_made)
        self.assertEqual(result, "on_chat_result")

    def test_get_location_marker_team0(self):
        handler = FakeHandler()
        handler.last_marker = None
        result = apply_script.on_chat("test", False)
        self.assertEqual(handler.marker_made, (DummyMarker, (16, 20)))
        self.assertEqual(result, "on_chat_result")

    def test_get_location_marker_team1(self):
        handler = FakeHandler()
        handler.team.id = 1
        handler.last_marker = None
        result = apply_script.on_chat("test", False)
        self.assertEqual(handler.marker_made, (DummyMarker, (4, 20)))
        self.assertEqual(result, "on_chat_result")

class TestBranchCoverageOnChat(unittest.TestCase):
    def test_print_branch_coverage(self):
        coverage = return_coverage_on_chat()
        print("Branch coverage for on_chat: ", coverage)

if __name__ == "__main__":
    unittest.main()