import unittest
from unittest.mock import MagicMock, patch
import random

from piqueserver.scripts.squad import apply_script

# --- Dummy Classes to simulate protocol, connection, and players ---

class DummyConnection:
    def on_spawn(self, pos):
        return "base_spawn"
    def on_team_changed(self, old_team):
        return "team_changed"
    def on_login(self, name):
        return "login_called"
    def on_chat(self, value, global_message):
        return "chat_called"

class DummyProtocol:
    def __init__(self):
        self.players = {}  # dict of players
        self.respawn_time = 0
        self.squad_respawn_time = 15  # arbitrary respawn time for squad members
        self.squad_size = 2         # set a small squad size for testing
        self.auto_squad = False
        self.spectator_team = "spectators"

class DummyPosition:
    def __init__(self, pos):
        self._pos = pos
    def get(self):
        return self._pos

class DummyWorld:
    def __init__(self, pos):
        self.position = DummyPosition(pos)

class DummyPlayer:
    def __init__(self, name, hp, team, squad=None, invisible=False, god=False, pos=(0, 0, 0)):
        self.name = name
        self.hp = hp
        self.team = team
        self.squad = squad
        self.invisible = invisible
        self.god = god
        self.world_object = DummyWorld(pos)
        self.sent_chats = []
    def send_chat(self, msg):
        self.sent_chats.append(msg)

# --- TestCase for on_spawn in SquadConnection ---

class TestOnSpawn(unittest.TestCase):
    def setUp(self):
        # Set up a dummy protocol and connection.
        self.protocol = DummyProtocol()
        self.connection = DummyConnection()
        # apply_script returns (protocol, SquadConnectionClass)
        proto, SquadConnectionClass = apply_script(self.protocol, DummyConnection, {})
        self.SquadConnection = SquadConnectionClass
        # Create an instance of SquadConnection and assign required attributes.
        self.instance = self.SquadConnection()
        self.instance.protocol = self.protocol
        self.instance.team = "red"
        self.instance.name = "tester"
        # Replace methods with mocks to track calls.
        self.instance.send_chat = MagicMock()
        self.instance.set_location_safe = MagicMock()

    def test_on_spawn_no_squad(self):
        """
        When self.squad is None, the squad branch is skipped.
        on_spawn should simply call the base connection's on_spawn,
        and no chat or location changes should occur.
        """
        self.instance.squad = None
        self.instance.squad_pref = None
        result = self.instance.on_spawn((0, 0, 0))
        self.assertEqual(result, "base_spawn")
        self.instance.send_chat.assert_not_called()
        self.instance.set_location_safe.assert_not_called()

    def test_on_spawn_with_valid_squad_pref(self):
        """
        When self.squad is set and a valid squad_pref exists,
        on_spawn should send a chat message (listing squadmates) and
        call set_location_safe with the follow location of squad_pref.
        """
        self.instance.squad = "Bravo"
        # Create a valid squad_pref (leader) who meets all conditions.
        valid_pref = DummyPlayer(name="leader", hp=100, team="red",
                                 squad="Bravo", invisible=False, god=False, pos=(5, 5, 5))
        self.instance.squad_pref = valid_pref
        # Also add the leader and another squadmate to the protocol.
        self.protocol.players["leader"] = valid_pref
        mate = DummyPlayer(name="mate", hp=100, team="red",
                           squad="Bravo", invisible=False, god=False, pos=(20, 20, 20))
        self.protocol.players["mate"] = mate

        result = self.instance.on_spawn((0, 0, 0))
        self.assertEqual(result, "base_spawn")
        # Verify that a chat message was sent containing the squad name.
        self.instance.send_chat.assert_called()
        # Verify that set_location_safe was called with valid_pref's location.
        self.instance.set_location_safe.assert_called_with((5, 5, 5))

    def test_on_spawn_with_live_member(self):
        """
        When self.squad is set, squad_pref is None (or invalid),
        but there is at least one live squadmate,
        on_spawn should choose a live member (via random.choice) and
        call set_location_safe with that member's follow location.
        """
        self.instance.squad = "Bravo"
        self.instance.squad_pref = None
        live_member = DummyPlayer(name="live", hp=100, team="red",
                                  squad="Bravo", invisible=False, god=False, pos=(10, 10, 10))
        self.protocol.players["live"] = live_member

        # Patch random.choice so it returns our live_member deterministically.
        with patch("random.choice", return_value=live_member):
            result = self.instance.on_spawn((0, 0, 0))
            self.assertEqual(result, "base_spawn")
            self.instance.send_chat.assert_called()
            self.instance.set_location_safe.assert_called_with((10, 10, 10))

    def test_on_spawn_with_only_dead_squadmates(self):
        """
        When self.squad is set and there are squadmates but all are dead (hp=0),
        on_spawn should send the chat message but not call set_location_safe
        (since no live member exists).
        """
        self.instance.squad = "Bravo"
        self.instance.squad_pref = None
        dead_member = DummyPlayer(name="dead", hp=0, team="red",
                                  squad="Bravo", invisible=False, god=False, pos=(30, 30, 30))
        self.protocol.players["dead"] = dead_member

        result = self.instance.on_spawn((0, 0, 0))
        self.assertEqual(result, "base_spawn")
        self.instance.send_chat.assert_called()
        self.instance.set_location_safe.assert_not_called()

if __name__ == "__main__":
    unittest.main()
