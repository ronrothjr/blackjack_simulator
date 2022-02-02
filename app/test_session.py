import unittest
from dealer import Dealer
from session import Session
from table import Table


class TestSession(unittest.TestCase):

    def setUp(self) -> None:
        self.session = Session()

    def test_initialize_a_session(self):
        self.assertIsInstance(self.session, Session)
        self.assertIsInstance(self.session.table, Table)
        self.assertIsInstance(self.session.dealer, Dealer)
        self.assertIsInstance(self.session.positions, dict)
        self.assertIsInstance(self.session.rounds_to_play, int)

    def test_session_can_run_a_session(self):
        self.assertEqual(self.session.run_session.__name__, 'run_session') 
        self.assertTrue(callable(self.session.run_session))

    def test_session_can_add_players(self):
        self.assertEqual(self.session.add_players.__name__, 'add_players') 
        self.assertTrue(callable(self.session.add_players))

    def test_session_can_add_player(self):
        self.assertEqual(self.session.add_player.__name__, 'add_player') 
        self.assertTrue(callable(self.session.add_player))

    def test_session_can_update_bankroll(self):
        self.assertEqual(self.session.update_bankroll.__name__, 'update_bankroll') 
        self.assertTrue(callable(self.session.update_bankroll))

    def test_session_can_add_player(self):
        self.assertEqual(self.session.report_stats.__name__, 'report_stats') 
        self.assertTrue(callable(self.session.report_stats))

    def test_session_can_deal_many_rounds_of_blackjack_and_replace_players_with_empty_bankrolls(self):
        self.session.run_session()
        dealer_stats = self.session.dealer.stats
        player_stats = self.session.dealer.positions['Player 1'].player.stats
        self.session.report_stats()
        self.assertEqual(self.session.rounds_to_play, dealer_stats.rounds)


if __name__ == '__main__':
    unittest.main()
