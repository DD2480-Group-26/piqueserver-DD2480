import unittest
from unittest.mock import MagicMock, patch
import random

from piqueserver.scripts.squad import apply_script, return_coverage_on_spawn

# Dummy classes to simulate protocol, connection, and players

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
        self.players = {}  
        self.respawn_time = 0
        self.squad_respawn_time = 15  # respawn time for squad members
        self.squad_size = 5         # set a small squad size for testing
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
        # Reset branch coverage dictionary before each test.
        from piqueserver.scripts.squad import branch_coverage_on_spawn
        for key in branch_coverage_on_spawn:
            branch_coverage_on_spawn[key] = False

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

    def tearDown(self):
        # Print branch coverage for on_spawn after each test.
        from piqueserver.scripts.squad import branch_coverage_on_spawn
        print("Branch coverage for on_spawn:", branch_coverage_on_spawn)

    def test_no_squad(self):
        """If self.squad is None, on_spawn should not send any chat or change location."""
        self.instance.squad = None
        self.instance.squad_pref = None
        result = self.instance.on_spawn((0, 0, 0))
        self.assertEqual(result, "base_spawn")
        self.instance.send_chat.assert_not_called()
        self.instance.set_location_safe.assert_not_called()

    def test_all_alone(self):
        """
        When squad is set but there are no other players (all_members is empty),
        the function should send the "all alone" chat message and not call set_location_safe.
        """
        self.instance.squad = "Alpha"
        self.instance.squad_pref = None
        # Do not populate protocol.players so that get_squad returns an empty list.
        result = self.instance.on_spawn((0, 0, 0))
        self.assertEqual(result, "base_spawn")
        self.instance.send_chat.assert_called_with("You are in squad Alpha, all alone.")
        self.instance.set_location_safe.assert_not_called()

    def test_valid_squad_pref(self):
        """
        When a valid squad_pref exists (satisfies hp, team, visible, mortal),
        on_spawn should send the chat message (listing squadmates) and use squad_pref's location.
        """
        self.instance.squad = "Bravo"
        valid_pref = DummyPlayer("leader", 100, "red", squad="Bravo", pos=(5, 5, 5))
        self.instance.squad_pref = valid_pref
        # Populate protocol.players so that get_squad finds two players.
        self.protocol.players["leader"] = valid_pref
        mate = DummyPlayer("mate", 100, "red", squad="Bravo", pos=(10, 10, 10))
        self.protocol.players["mate"] = mate
        result = self.instance.on_spawn((0, 0, 0))
        self.assertEqual(result, "base_spawn")
        expected_msg = "You are in squad Bravo with leader (100 hp) and mate (100 hp)."
        self.instance.send_chat.assert_called_with(expected_msg)
        self.instance.set_location_safe.assert_called_with((5, 5, 5))

    def test_live_member(self):
        """
        When squad_pref is None but at least one live squad member exists,
        on_spawn should call set_location_safe with the follow location of a live member.
        """
        self.instance.squad = "Charlie"
        self.instance.squad_pref = None
        live_member = DummyPlayer("live", 100, "red", squad="Charlie", pos=(7, 7, 7))
        self.protocol.players["live"] = live_member
        expected_msg = "You are in squad Charlie with live (100 hp)."
        with patch("random.choice", return_value=live_member):
            result = self.instance.on_spawn((0, 0, 0))
            self.assertEqual(result, "base_spawn")
            self.instance.send_chat.assert_called_with(expected_msg)
            self.instance.set_location_safe.assert_called_with((7, 7, 7))

    def test_no_live_member(self):
        """
        When squad members exist but none are 'live' (hp == 0),
        on_spawn should send the squad chat message but not call set_location_safe.
        """
        self.instance.squad = "Delta"
        self.instance.squad_pref = None
        dead_member = DummyPlayer("dead", 0, "red", squad="Delta", pos=(8, 8, 8))
        self.protocol.players["dead"] = dead_member
        expected_msg = "You are in squad Delta with dead (DEAD)."
        result = self.instance.on_spawn((0, 0, 0))
        self.assertEqual(result, "base_spawn")
        self.instance.send_chat.assert_called_with(expected_msg)
        self.instance.set_location_safe.assert_not_called()

    def test_chat_message_loop_branches(self):
        """
        Test a scenario with three squad members to exercise all branches in the loop constructing
        the chat message: the first, a middle, and the last iteration.
        Also, since squad_pref is None, the location is chosen from a live member.
        """
        self.instance.squad = "Echo"
        self.instance.squad_pref = None
        p1 = DummyPlayer("p1", 100, "red", squad="Echo", pos=(1, 1, 1))
        p2 = DummyPlayer("p2", 0, "red", squad="Echo", pos=(2, 2, 2))   # Dead
        p3 = DummyPlayer("p3", 50, "red", squad="Echo", pos=(3, 3, 3))
        self.protocol.players["p1"] = p1
        self.protocol.players["p2"] = p2
        self.protocol.players["p3"] = p3
        expected_msg = "You are in squad Echo with p1 (100 hp), p2 (DEAD) and p3 (50 hp)."
        with patch("random.choice", return_value=p1):
            result = self.instance.on_spawn((0, 0, 0))
            self.assertEqual(result, "base_spawn")
            self.instance.send_chat.assert_called_with(expected_msg)
            self.instance.set_location_safe.assert_called_with((1, 1, 1))

# A separate test to print the branch coverage dictionary.
class TestBranchCoverageOnSpawn(unittest.TestCase):
    def test_print_branch_coverage(self):
        coverage = return_coverage_on_spawn()
        print("Branch coverage for on_spawn:", coverage)
        # Optionally assert that at least one branch was hit:
        # self.assertTrue(any(coverage.values()))

if __name__ == "__main__":
    unittest.main()
