import copy, unittest
from dealer import Dealer
from hand import Hand
from player import Player
from table import Table


class TestDealer(unittest.TestCase):

    def setUp(self) -> None:
        table = Table()
        self.dealer = Dealer(table)

    def test_initialize_a_dealer(self):
        self.assertIsInstance(self.dealer, Dealer)
        self.assertIsInstance(self.dealer.discard, list)

    def test_dealer_allows_players_to_leave_or_join(self):
        self.assertEqual(self.dealer.leave_or_join.__name__, 'leave_or_join') 
        self.assertTrue(callable(self.dealer.leave_or_join))

    def test_dealer_can_take_bets(self):
        self.assertEqual(self.dealer.take_bet.__name__, 'take_bet') 
        self.assertTrue(callable(self.dealer.take_bet))

    def test_dealer_has_a_resolve_hands_method(self):
        self.assertEqual(self.dealer.get_insurance.__name__, 'get_insurance') 
        self.assertTrue(callable(self.dealer.get_insurance))

    def test_dealer_has_a_resolve_hands_method(self):
        self.assertEqual(self.dealer.resolve_hands.__name__, 'resolve_hands') 
        self.assertTrue(callable(self.dealer.resolve_hands))

    def test_dealer_has_a_get_outcome_method(self):
        self.assertEqual(self.dealer.get_outcome.__name__, 'get_outcome') 
        self.assertTrue(callable(self.dealer.get_outcome))

    def test_dealer_has_a_resolve_bets_method(self):
        self.assertEqual(self.dealer.resolve_bets.__name__, 'resolve_bets') 
        self.assertTrue(callable(self.dealer.resolve_bets))

    def test_dealer_has_a_deal_round_method(self):
        self.assertEqual(self.dealer.deal_round.__name__, 'deal_round') 
        self.assertTrue(callable(self.dealer.deal_round))

    def test_dealer_has_a_set_card_stats_method(self):
        self.assertEqual(self.dealer.set_card_stats.__name__, 'set_card_stats') 
        self.assertTrue(callable(self.dealer.set_card_stats))

    def test_dealer_has_a_get_card_or_shuffle_in_method(self):
        self.assertEqual(self.dealer.get_card_or_shuffle_in.__name__, 'get_card_or_shuffle_in') 
        self.assertTrue(callable(self.dealer.get_card_or_shuffle_in))

    def test_player_can_bet_at_a_position(self):
        self.add_player_one()
        self.dealer.get_bets()
        self.assertEqual(self.dealer.table.positions['Player 1'].bet, 50)
        is_bet_taken = self.dealer.take_bet('Player 2')
        self.assertFalse(is_bet_taken)

    def test_shuffle_in_when_shoe_is_empty_while_dealing_the_table(self):
        self.add_player_one()
        self.dealer.discard += copy.deepcopy(self.dealer.table.shoe.cards)
        self.dealer.table.shoe.cards = self.dealer.table.shoe.cards = []
        self.dealer.get_bets()
        self.dealer.deal_table()
        self.assertGreater(len(self.dealer.table.shoe.cards), 300)

    def test_deal_cards_to_positions_with_a_bet(self):
        self.add_player_one()
        self.dealer.get_bets()
        player2 = Player(50000)
        self.dealer.table.join(player2, 'Player 2', 200)
        self.dealer.deal_table()
        dealer = self.dealer.table.positions['Dealer']
        p1 = self.dealer.table.positions['Player 1']
        p2 = self.dealer.table.positions['Player 2']
        self.assertGreater(len(dealer.hands), 0)
        self.assertEqual(len(dealer.hands[0].cards), 2)
        self.assertGreater(len(p1.hands), 0)
        self.assertEqual(len(p1.hands[0].cards), 2)
        self.assertEqual(len(p2.hands), 0)

    def test_dealer_asks_bot_to_make_moves_for_player_until_hand_is_resolved(self):
        self.add_player_one()
        self.dealer.get_bets()
        self.dealer.deal_table()
        p1 = self.dealer.table.positions['Player 1']
        hand = p1.hands[0]
        player = p1.role != 'Dealer'
        self.dealer.deal_hand(p1, hand, player)
        self.assertTrue(p1.hands[0].final)

    def test_dealer_can_resolve_all_hands_on_the_table(self):
        self.add_player_one()
        self.dealer.get_bets()
        self.dealer.deal_table()
        self.dealer.resolve_hands()
        d = self.dealer.table.positions['Dealer'].hands[0]
        self.assertTrue(d.final)

    def test_dealer_can_get_outcome_of_winning_hands(self):
        d = Hand(10).set_cards([{'r': 8, 's': 1}, {'r': 9, 's': 1}])
        d.final = 'stand'
        p = Hand(10).set_cards([{'r': 13, 's': 1}, {'r': 1, 's': 1}])
        p.final = 'stand'
        outcome = self.dealer.get_outcome(d, p)
        self.assertEqual(outcome, 'pay')

    def test_dealer_can_get_outcome_of_losing_hands(self):
        d = Hand(10).set_cards([{'r': 8, 's': 1}, {'r': 9, 's': 1}])
        d.final = 'stand'
        p = Hand(10).set_cards([{'r': 8, 's': 1}, {'r': 4, 's': 1}])
        p.final = 'stand'
        outcome = self.dealer.get_outcome(d, p)
        self.assertEqual(outcome, 'lose')

    def test_dealer_can_get_outcome_of_even_hands(self):
        d = Hand(10).set_cards([{'r': 8, 's': 1}, {'r': 9, 's': 1}])
        d.final = 'stand'
        p = Hand(10).set_cards([{'r': 12, 's': 1}, {'r': 7, 's': 1}])
        p.final = 'stand'
        outcome = self.dealer.get_outcome(d, p)
        self.assertEqual(outcome, 'push')

    def test_dealer_can_resolve_busted_hands(self):
        d = Hand(10).set_cards([{'r': 8, 's': 1}, {'r': 9, 's': 1}])
        d.final = 'stand'
        p = Hand(10).set_cards([{'r': 12, 's': 1}, {'r': 4, 's': 1}, {'r': 10, 's': 1}])
        p.final = 'busted'
        outcome = self.dealer.get_outcome(d, p)
        self.assertEqual(outcome, 'lose')

    def test_dealer_can_resolve_all_bets(self):
        self.add_players()
        self.dealer.get_bets()
        self.dealer.deal_table()
        [p1, p2, p3, p4] = self.set_round_one_hands()
        self.dealer.resolve_hands()
        p1_initial_chips = int(p1.player.chips)
        p2_initial_chips = int(p2.player.chips)
        p3_initial_chips = int(p3.player.chips)
        p4_initial_chips = int(p4.player.chips)
        self.dealer.resolve_bets()
        p1_updated_chips = int(p1.player.chips)
        p2_updated_chips = int(p2.player.chips)
        p3_updated_chips = int(p3.player.chips)
        p4_updated_chips = int(p4.player.chips)
        self.assertEqual(p1.hands[0].outcome, 'pay')
        self.assertEqual(p2.hands[0].outcome, 'push')
        self.assertEqual(p3.hands[0].outcome, 'lose')
        self.assertEqual(p4.hands[0].outcome, 'surrender')
        self.assertTrue(p1_updated_chips == p1_initial_chips + 20)
        self.assertTrue(p2_updated_chips == p2_initial_chips + 10)
        self.assertEqual(p3_updated_chips, p3_initial_chips)
        self.assertEqual(p4_updated_chips, p4_initial_chips + 5)

    def test_clearing_cards_from_table(self):
        self.add_player_one()
        self.dealer.table.shoe.cards = self.dealer.table.shoe.cards = []
        self.dealer.clear_table()
        dealer = self.dealer.table.positions['Dealer']
        p1 = self.dealer.table.positions['Player 1']
        self.assertEqual(len(dealer.hands), 0)
        self.assertEqual(len(p1.hands), 0)
        self.assertEqual(len(self.dealer.table.shoe.cards), 311) # less burn card

    def add_player_one(self):
        player = Player(50000)
        self.dealer.table.join(player, 'Player 1', 1000)

    def add_player_two(self):
        player2 = Player(50000)
        self.dealer.table.join(player2, 'Player 2', 1000)

    def add_player_three(self):
        player3 = Player(50000)
        self.dealer.table.join(player3, 'Player 3', 1000)

    def add_player_four(self):
        player3 = Player(50000)
        self.dealer.table.join(player3, 'Player 4', 1000)

    def add_player_five(self):
        player3 = Player(50000)
        self.dealer.table.join(player3, 'Player 5', 1000)

    def add_players(self):
        self.add_player_one()
        self.add_player_two()
        self.add_player_three()
        self.add_player_four()

    def add_players_only(self, number_of_players):
        for x in range(1, number_of_players + 1):
            self.add_player(self.dealer.table, f'Player {x}')
    
    def add_player(self, table, position):
        player = Player(bankroll=50000)
        table.join(player, position, 1000)

    def get_player_positions(self):
        p1 = self.dealer.table.positions['Player 1']
        p2 = self.dealer.table.positions['Player 2']
        p3 = self.dealer.table.positions['Player 3']
        return [p1, p2, p3]

    def set_round_one_hands(self):
        dealer = self.dealer.table.positions['Dealer']
        p1 = self.dealer.table.positions['Player 1']
        p2 = self.dealer.table.positions['Player 2']
        p3 = self.dealer.table.positions['Player 3']
        p4 = self.dealer.table.positions['Player 4']
        dealer.hands[0] = Hand().set_cards([{'r': 12, 's': 1}, {'r': 10, 's': 1}])
        p1.hands[0] = Hand(10).set_cards([{'r': 13, 's': 1}, {'r': 1, 's': 1}])
        p2.hands[0] = Hand(10).set_cards([{'r': 10, 's': 1}, {'r': 13, 's': 1}])
        p3.hands[0] = Hand(10).set_cards([{'r': 5, 's': 1}, {'r': 8, 's': 1}])
        p4.hands[0] = Hand(10).set_cards([{'r': 6, 's': 1}, {'r':11, 's': 1}])
        dealer.hands[0].final = 'stand'
        p1.hands[0].final = 'stand'
        p2.hands[0].final = 'stand'
        p3.hands[0].final = 'stand'
        p4.hands[0].final = 'surrender'
        return [p1, p2, p3, p4]


if __name__ == '__main__':
    unittest.main()
