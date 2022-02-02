import unittest
from player import Player
from stats import Stats


class TestPlayer(unittest.TestCase):

    def setUp(self) -> None:
        self.player = Player()

    def test_initiates_a_player(self):
        self.assertIsInstance(self.player, Player)

    def test_player_has_stats(self):
        self.assertIsInstance(self.player.stats, Stats)

    def test_player_has_chips(self):
        self.assertIsInstance(self.player.chips, int)

    def test_player_has_a_bankroll_that_defaults_to_zero(self):
        self.assertIsInstance(self.player.bankroll, int)
        self.assertEqual(self.player.bankroll, 0)
        player = Player(bankroll=50000)
        self.assertEqual(player.bankroll, 50000)

    def test_player_has_bet_unit(self):
        self.assertIsInstance(self.player.bet_unit, int)

    def test_player_has_risk_of_ruin(self):
        self.assertIsInstance(self.player.risk_of_ruin, float)

    def test_player_can_use_bankroll_to_buy_chips_if_available_in_bankroll(self):
        is_bought = self.player.buy(100)
        self.assertFalse(is_bought)
        player = Player(bankroll=50000)
        is_bought = player.buy(100)
        self.assertTrue(is_bought)
        self.assertEqual(player.chips, 100)

    def test_calculate_bet_unit(self):
        player = Player(bankroll=50000)
        player.calculate_bet_unit(40.0)
        self.assertEqual(player.bet_unit, 250)

    def test_calculate_bet_unit_from_bankroll_and_risk_of_ruin(self):
        player = Player(bankroll=50000)
        self.assertEqual(player.bet_unit, 50)

    def test_add_to_bankroll_and_recalculate_bet_unit(self):
        player = Player(bankroll=50000)
        player.add_to_bankroll(50000)
        self.assertEqual(player.bet_unit, 100)
        

if __name__ == '__main__':
    unittest.main()
