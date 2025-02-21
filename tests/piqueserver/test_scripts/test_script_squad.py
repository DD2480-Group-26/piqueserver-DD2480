# test_script_squad.py
import unittest
import random
from piqueserver.scripts.squad import apply_script, branch_hits_squad, SIZE_OPTION, RESPAWN_TIME_OPTION, AUTO_SQUAD_OPTION

# --- Fake classes for testing ---

class FakeConnection:
    def __init__(self, protocol, name, team, squad=None, squad_pref=None):
        self.protocol = protocol
        self.name = name
        self.team = team
        self.squad = squad
        self.squad_pref = squad_pref
        self.respawn_time = None
        self.chat_messages = []
    def send_chat(self, msg):
        self.chat_messages.append(msg)
    def leave_squad(self):
        self.squad = None
        self.squad_pref = None
    def squad_broadcast(self, msg):
        # For testing, simply record the message.
        self.chat_messages.append(msg)
    # Dummy implementations for methods that may be called:
    def on_login(self, name):
        return
    def on_team_changed(self, old_team):
        return
    def on_spawn(self, pos):
        return
    def on_kill(self, killer, type, grenade):
        return
    def on_chat(self, value, global_message):
        return

class FakeProtocol:
    def __init__(self, squad_size, spectator_team,
                 respawn_time="normal_respawn", squad_respawn_time="squad_respawn"):
        self.squad_size = squad_size
        self.spectator_team = spectator_team
        self.respawn_time = respawn_time
        self.squad_respawn_time = squad_respawn_time
        self.players = {}

class DummyFollowTarget:
    def __init__(self, name):
        self.name = name

# Provide a dummy config dictionary with proper squad settings.
dummy_config = {
    'squad': {
         'size': 3,
         'respawn_time': 'squad_respawn_time',
         'auto_squad': True,
    }
}

# Helper to obtain the SquadConnection class via apply_script.
def get_squad_connection_class(protocol):
    _, SquadConnection = apply_script(protocol, FakeConnection, dummy_config)
    return SquadConnection

# --- Test cases ---

class TestJoinSquad(unittest.TestCase):
    def setUp(self):
        # Patch the config option getters so that SIZE_OPTION.get() returns 3, etc.
        self._old_size_get = SIZE_OPTION.get
        self._old_respawn_get = RESPAWN_TIME_OPTION.get
        self._old_auto_get = AUTO_SQUAD_OPTION.get
        SIZE_OPTION.get = lambda: 3
        RESPAWN_TIME_OPTION.get = lambda: "squad_respawn_time"
        AUTO_SQUAD_OPTION.get = lambda: True

        # Create a protocol with a squad size of 3 and a designated spectator team.
        self.protocol = FakeProtocol(squad_size=3, spectator_team="Spectators",
                                     respawn_time="normal_respawn", squad_respawn_time="squad_respawn")
        # Even if the protocol is constructed with squad_size=3, the apply_script call below will override it,
        # so we ensure the patched SIZE_OPTION.get() returns 3.
        self.protocol.squad_size = 3
        self.SquadConnection = get_squad_connection_class(self.protocol)
    
    def tearDown(self):
        # Restore the original config getters.
        SIZE_OPTION.get = self._old_size_get
        RESPAWN_TIME_OPTION.get = self._old_respawn_get
        AUTO_SQUAD_OPTION.get = self._old_auto_get

        # Print and reset the branch_hits_squad dictionary after each test.
        print("Branch squads:", branch_hits_squad)
     #   for key in branch_hits_squad:
      #      branch_hits_squad[key] = False

    def test_invalid_team_none(self):
        # When team is None, join_squad should do nothing (return None).
        conn = self.SquadConnection(self.protocol, "Alice", None)
        result = conn.join_squad("Alpha", None)
        self.assertIsNone(result)
    
    def test_invalid_team_spectator(self):
        # When team is the spectator team, join_squad returns nothing.
        conn = self.SquadConnection(self.protocol, "Bob", "Spectators")
        result = conn.join_squad("Alpha", None)
        self.assertIsNone(result)
    
    def test_squad_unchanged(self):
        # If already in the squad with the same follow target.
        conn = self.SquadConnection(self.protocol, "Charlie", "TeamA", squad="Alpha", squad_pref=None)
        result = conn.join_squad("Alpha", None)
        self.assertEqual(result, "Squad unchanged.")
    
    def test_squad_full(self):
        # Simulate a full squad by overriding get_squad on the instance.
        conn = self.SquadConnection(self.protocol, "Dana", "TeamA")
        conn.get_squad = lambda team, squadkey: (
            {'name': squadkey, 'players': [1, 2, 3]} if squadkey == "Full" else {'name': squadkey, 'players': []}
        )
        result = conn.join_squad("Full", None)
        self.assertEqual(result, "Squad Full is full. (limit 3)")
    
   
    def test_new_squad_with_follow(self):
        # Joining a new squad with a follow target.
        follow_target = DummyFollowTarget("Frank")
        conn = self.SquadConnection(self.protocol, "Grace", "TeamA")
        result = conn.join_squad("Gamma", follow_target)
        self.assertEqual(result, "You are now in squad Gamma, following Frank.")
        self.assertEqual(conn.squad, "Gamma")
        self.assertEqual(conn.squad_pref, follow_target)
    
    def test_change_follow_only(self):
        # Changing only the follow target while remaining in the same squad.
        old_follow = DummyFollowTarget("Heidi")
        conn = self.SquadConnection(self.protocol, "Ivan", "TeamA", squad="Delta", squad_pref=old_follow)
        result = conn.join_squad("Delta", None)
        self.assertEqual(result, "You are no longer following Heidi.")
        self.assertEqual(conn.squad, "Delta")
        self.assertIsNone(conn.squad_pref)
    
    def test_leave_squad(self):
        # Passing None as squad should leave the squad.
        conn = self.SquadConnection(self.protocol, "Judy", "TeamA", squad="Omega", squad_pref=None)
        result = conn.join_squad(None, None)
        self.assertIsNone(result)
        self.assertIsNone(conn.squad)
        self.assertEqual(conn.respawn_time, self.protocol.respawn_time)
        self.assertIn("You are no longer assigned to a squad.", conn.chat_messages)

if __name__ == '__main__':
    unittest.main()
