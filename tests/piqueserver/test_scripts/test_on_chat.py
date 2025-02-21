import unittest
from piqueserver.scripts.markers import apply_script

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

    def test_no_marker_trigger(self, bound_on_chat):
        handler = FakeHandler()
        result = apply_script.on_chat("hello", False)
        assert handler.sent_messages == []
        assert handler.marker_made is None
        assert result == "on_chat_result"

    def test_global_message_marker(self, bound_on_chat):
        handler = FakeHandler()
        result = apply_script.on_chat("test", True)
        assert "TeamChat" in handler.sent_messages
        assert handler.marker_made is None
        assert result == "on_chat_result"

    def test_cooldown_marker(self, bound_on_chat):
        handler = FakeHandler()
        result = apply_script.on_chat("test", False)
        assert "Wait" in handler.sent_messages
        assert handler.marker_made is None
        assert result == "on_chat_result"

    def test_always_there_fail(self, bound_on_chat):
        handler = FakeHandler()
        handler.last_marker = None
        handler.there_location = None
        result = apply_script.on_chat("always", False)
        assert "Fail" in handler.sent_messages
        assert handler.marker_made is None
        assert result == "on_chat_result"

    def test_get_location_marker_team0(self, bound_on_chat):
        handler = FakeHandler()
        handler.last_marker = None
        result = apply_script.on_chat("test", False)
        assert handler.marker_made == (DummyMarker, (16, 20))
        assert result == "on_chat_result"

    def test_get_location_marker_team1(self, bound_on_chat):
        handler = FakeHandler()
        handler.team.id = 1
        handler.last_marker = None
        result = apply_script.on_chat("test", False)
        assert handler.marker_made == (DummyMarker, (4, 20))
        assert result == "on_chat_result"
