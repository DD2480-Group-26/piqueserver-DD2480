import unittest
from collections import deque

from piqueserver.scripts.markers import apply_script, S_TEAMCHAT, branch_hits_chat, return_coverage_on_chat

# Dummy protocol – mimics only the minimal behavior needed.
class DummyProtocol:
    def __init__(self):
        self.allow_markers = True
        self.markers = []
    def broadcast_chat(self, message, irc=False):
        self.last_broadcast = message
    def broadcast_contained(self, message, team=None, **kwargs):
        self.last_contained = message

# Dummy team with minimal attributes.
class DummyTeam:
    def __init__(self, team_id, spectator=False):
        self.id = team_id
        self.spectator = spectator
        self.marker_count = {}
        self.intel_marker = None
        self.marker_calls = []
    def get_players(self):
        return []

# Dummy connection providing required methods.
class DummyConnection:
    def __init__(self, protocol, team):
        self.protocol = protocol
        self.team = team
        self.allow_markers = True
        self.last_marker = None
        self.sneak_presses = deque(maxlen=2)
    def send_chat(self, message):
        self.last_sent_chat = message
    def get_location(self):
        # For testing, return a fixed location.
        return (10, 10, 0)
    def get_there_location(self):
        # For testing, return a fixed location.
        return (15, 15)
    def make_marker(self, marker_class, location):
        self.marker_made = (marker_class, location)
    def on_chat(self, value, global_message):
        # Default base behavior: simply return the chat text.
        return value

class TestOnChat(unittest.TestCase):
    def setUp(self):
        # Reset the branch_hits_chat global (if needed) for clean tests.
        global branch_hits_chat
        for key in branch_hits_chat:
                    branch_hits_chat[key] = False        
        self.protocol = DummyProtocol()
        self.team = DummyTeam(team_id=0, spectator=False)
        self.base_connection = DummyConnection(self.protocol, self.team)
        
        MarkerProtocol, MarkerConnection = apply_script(DummyProtocol, DummyConnection, {})
        self.connection = MarkerConnection(self.protocol, self.team)
        self.connection.send_chat = self.base_connection.send_chat
        self.connection.get_location = self.base_connection.get_location
        self.connection.get_there_location = self.base_connection.get_there_location
        self.connection.make_marker = self.base_connection.make_marker
        self.connection.last_marker = None
        self.connection.sneak_presses = deque(maxlen=2)

    def tearDown(self):
        print("Branch coverage for on_spawn:", branch_hits_chat)

    def test_on_chat_no_trigger(self):
        if hasattr(self.base_connection, 'marker_made'):
            del self.base_connection.marker_made
        result = self.connection.on_chat("hello", False)
        self.assertEqual(result, "hello")
        self.assertFalse(hasattr(self.base_connection, 'marker_made'),
                         "No marker should be made when there is no trigger.")

    def test_on_chat_trigger_global(self):
        captured = {}
        def capture_send_chat(message):
            captured['msg'] = message
        self.connection.send_chat = capture_send_chat
        result = self.connection.on_chat("!here", True)
        self.assertEqual(captured.get('msg'), S_TEAMCHAT)
        self.assertEqual(result, "!here")

    def test_on_chat_trigger_marker_placement(self):
        captured = {}
        def capture_make_marker(marker_class, location):
            captured['marker'] = (marker_class.__name__, location)
        self.connection.make_marker = capture_make_marker
        self.connection.last_marker = None
        result = self.connection.on_chat("!here", False)
        self.assertEqual(captured.get('marker'), ("Here", (16, 10)))
        self.assertEqual(result, "!here")

class TestBranchCoverageOnChat(unittest.TestCase):
    def test_print_branch_coverage(self):
        coverage = return_coverage_on_chat()
        print("Branch coverage for on_spawn:", coverage)

if __name__ == '__main__':
    unittest.main()
