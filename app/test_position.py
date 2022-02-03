import unittest
from hand import Hand
from player import Player
from position import Position


class TestPosition(unittest.TestCase):

    def setUp(self) -> None:
        self.position = Position()

    def test_initiates_a_player(self):
        self.assertIsInstance(self.position, Position)

    def test_position_allows_a_player_to_buy_in(self):
        self.assertEqual(self.position.buy_in.__name__, 'buy_in') 
        self.assertTrue(callable(self.position.buy_in))

    def test_position_allows_a_player_to_buy_in(self):
        self.assertEqual(self.position.get_insurance.__name__, 'get_insurance') 
        self.assertTrue(callable(self.position.get_insurance))

    def test_position_can_determine_the_bet_spread_based_on_the_count(self):
        self.assertEqual(self.position.get_bet_spread.__name__, 'get_bet_spread') 
        self.assertTrue(callable(self.position.get_bet_spread))

    def test_position_can_determine_the_adjust_bet_unit_based_on_the_count(self):
        self.assertEqual(self.position.get_adjusted_bet_unit.__name__, 'get_adjusted_bet_unit') 
        self.assertTrue(callable(self.position.get_adjusted_bet_unit))

    def test_position_role_defaults_to_dealer_if_no_player(self):
        self.assertIsInstance(self.position.role, str)
        self.assertEqual(self.position.role, 'Dealer')

    def test_position_decreases_player_bankroll_with_buy_in_amount(self):
        player = Player(50000)
        position = Position(player)
        position.buy_in(1000)
        self.assertEqual(player.bankroll, 49000)

    def test_position_has_list_of_hands_a_bet_and_insurance(self):
        self.assertIsInstance(self.position.hands, list)
        self.assertIsInstance(self.position.bet, int)
        self.assertIsInstance(self.position.insurance, int)

    def test_position_can_receive_a_bet_from_the_player(self):
        player = Player(50000)
        position = Position(player)
        position.buy_in(1000)
        position.make_a_bet()
        self.assertEqual(player.chips, 950)
        self.assertEqual(position.bet, 50)
        self.assertIsInstance(position.hands[0], Hand)
        self.assertEqual(position.hands[0].bet, 50)

    def test_position_can_double_the_bet_on_count_of_2(self):
        player = Player(50000)
        position = Position(player)
        position.buy_in(1000)
        position.make_a_bet(count=2)
        self.assertEqual(player.chips, 800)
        self.assertEqual(position.bet, 200)
        self.assertIsInstance(position.hands[0], Hand)
        self.assertEqual(position.hands[0].bet, 200)

    def test_position_can_receive_a_specified_bet_from_the_player(self):
        player = Player(50000)
        position = Position(player)
        position.buy_in(1000)
        position.make_a_bet(20)
        self.assertEqual(player.chips, 980)
        self.assertEqual(position.bet, 20)
        self.assertIsInstance(position.hands[0], Hand)
        self.assertEqual(position.hands[0].bet, 20)

    def test_position_can_get_insurance(self):
        player = Player(50000)
        position = Position(player)
        position.buy_in(1000)
        position.make_a_bet(20)
        position.get_insurance()
        self.assertEqual(player.chips, 970)
        self.assertEqual(position.insurance, 10)
        self.assertIsInstance(position.hands[0], Hand)
        self.assertEqual(position.hands[0].bet, 20)


    def test_clearing_cards(self):
        player = Player(50000)
        position = Position(player)
        position.buy_in(1000)
        position.make_a_bet()
        self.assertIsInstance(position.hands[0], Hand)
        position.clear_cards()
        self.assertEqual(len(position.hands), 0)
        

if __name__ == '__main__':
    unittest.main()
