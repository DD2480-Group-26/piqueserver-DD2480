import unittest
from piqueserver.core_commands.movement import branch_coverage
from unittest.mock import MagicMock, patch

class TestDoMove(unittest.TestCase):
    def setUp(self):
        # Mock connection and protocol
        self.connection = MagicMock()
        self.connection.name = "Player1"
        self.connection.admin = False
        self.connection.rights.move_others = False
        self.connection.protocol = MagicMock()
        self.connection.protocol.players = {"Player1": self.connection}

        # Mock map height function
        self.connection.protocol.map.get_height = MagicMock(return_value=100)
        
    def tearDown(self):
        print("Branches do_move:", branch_coverage)

    @patch('piqueserver.core_commands.movement.get_player')
    def test_move_self_valid_sector(self, mock_get_player):
        """Test moving the player to a valid sector (1 argument)."""
        mock_get_player.return_value = self.connection

        from piqueserver.core_commands.movement import do_move
        do_move(self.connection, ["A1"])

        # Assert correct coordinates (A1 converted to x, y, z)
        self.connection.set_location.assert_called_once_with((32, 32, 98))

    @patch('piqueserver.core_commands.movement.get_player')
    def test_move_self_valid_coordinates(self, mock_get_player):
        """Test moving self using explicit x, y, z (3 arguments)."""
        mock_get_player.return_value = self.connection

        from piqueserver.core_commands.movement import do_move
        do_move(self.connection, ["10", "20", "30"])

        # Assert correct coordinates
        self.connection.set_location.assert_called_once_with((10, 20, 30))

    

    @patch('piqueserver.core_commands.movement.get_player')
    def test_move_other_with_permission(self, mock_get_player):
        """Test moving another player when admin or move_others right is set."""
        other_player = MagicMock()
        mock_get_player.return_value = other_player

        self.connection.admin = True  # Give admin permissions

        from piqueserver.core_commands.movement import do_move
        do_move(self.connection, ["OtherPlayer", "10", "20", "30"])

        # Verify the other player's location is updated
        other_player.set_location.assert_called_once_with((10, 20, 30))


    def test_invalid_player_context(self):
        """Test calling do_move from a non-player connection."""
        from piqueserver.core_commands.movement import do_move
        self.connection.protocol.players = {}  # Empty, so no players exist

        with self.assertRaises(ValueError):
            do_move(self.connection, ["A1"])

if __name__ == '__main__':
    unittest.main()