import unittest
from hand import Hand
from player import Player
from position import Position
from shoe import Shoe
from table import Table


class TestTable(unittest.TestCase):

    def setUp(self) -> None:
        self.table = Table()

    def add_player_and_bet(self):
        player = Player(50000)
        self.table.join(player, 'Player 1', 200)

    def test_initiate_a_table(self):
        self.assertIsInstance(self.table, Table)

    def test_table_has_shoe_of_randomized_cards(self):
        self.assertIsInstance(self.table.shoe, Shoe)

    def test_table_has_positions(self):
        self.assertIsInstance(self.table.positions, dict)

    def test_table_can_tell_if_round_is_over(self):
        self.assertEqual(self.table.is_round_over.__name__, 'is_round_over') 
        self.assertTrue(callable(self.table.is_round_over))
        self.table.positions = {
            'Player 1': Position(Player(5000, 1000)).add_hand(Hand().set_cards([{'r':9},{'r':8}])),
            'Player 2': None,
            'Dealer': Position().add_hand(Hand().set_cards([{'r':1},{'r':10}]))
        }
        is_round_over = self.table.is_round_over()
        self.assertTrue(is_round_over)
        self.table.positions = {
            'Player 1': Position(Player(5000, 1000)).add_hand(Hand().set_cards([{'r':1},{'r':10}])),
            'Dealer': Position().add_hand(Hand().set_cards([{'r':9},{'r':2}]))
        }
        is_round_over = self.table.is_round_over()
        self.assertTrue(is_round_over)

    def test_table_has_a_player_in_the_dealer_position_and_seven_player_positions(self):
        self.assertIsInstance(self.table.positions['Dealer'], Position)
        positions = [p for p in self.table.positions.keys()]
        self.assertEqual(positions, ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5', 'Player 6', 'Player 7', 'Dealer'])

    def test_player_can_join_table_at_an_open_position_and_join_returns_a_boolean_if_player_joined(self):
        player = Player()
        has_player_joined = self.table.join(player, 'Player 1', 200)
        self.assertTrue(has_player_joined)
        self.assertEqual(self.table.positions['Player 1'].player, player)

    def test_player_cannot_join_table_at_an_occupied_position(self):
        player1 = Player()
        self.table.join(player1, 'Player 1', 200)
        player2 = Player()
        has_player_joined = self.table.join(player2, 'Player 1', 200)
        self.assertFalse(has_player_joined)
        self.assertEqual(self.table.positions['Player 1'].player, player1)

    def test_if_position_is_open(self):
        is_open = self.table.is_open('Player 1')
        self.assertTrue(is_open)
        player = Player()
        has_player_joined = self.table.join(player, 'Player 1', 200)
        self.assertTrue(has_player_joined)
        is_open = self.table.is_open('Player 1')
        self.assertFalse(is_open)

    def test_player_can_leave_a_position_if_occupied(self):
        player = Player()
        self.table.join(player, 'Player 1', 200)
        self.assertEqual(self.table.positions['Player 1'].player, player)
        player_left = self.table.leave('Player 2')
        self.assertFalse(player_left)
        player_left = self.table.leave('Player 1')
        self.assertTrue(player_left)
        is_open = self.table.is_open('Player 1')
        self.assertTrue(is_open)


if __name__ == '__main__':
    unittest.main()
