import unittest
from hand import Hand


class TestHand(unittest.TestCase):

    def setUp(self) -> None:
        self.hand = Hand(10)

    def test_initialize_a_hand(self):
        self.assertIsInstance(self.hand, Hand)

    def test_hand_has_cards(self):
        self.assertIsInstance(self.hand.cards, list)

    def test_hand_has_a_bet(self):
        self.assertIsInstance(self.hand.bet, int)
        self.assertEqual(self.hand.bet, 10)

    def test_hand_has_a_bet(self):
        self.assertIsInstance(self.hand.insurance, int)
        self.assertEqual(self.hand.insurance, 0)

    def test_hand_has_a_doubled_flag(self):
        self.assertIsInstance(self.hand.doubled, bool)
        self.assertEqual(self.hand.doubled, False)

    def test_hand_has_a_final_resolution(self):
        self.assertIsInstance(self.hand.final, str)
        self.assertEqual(self.hand.final, '')

    def test_hand_has_an_outcome(self):
        self.assertIsInstance(self.hand.outcome, str)
        self.assertEqual(self.hand.outcome, '')

    def test_add_card(self):
        self.hand.get_card({'r': 1, 's': 1})
        self.assertEqual(len(self.hand.cards), 1)

    def test_setting_cards(self):
        cards=[{'r': 8, 's': 1}, {'r': 4, 's': 1}]
        self.hand.set_cards(cards)
        self.assertEqual(self.hand.cards, cards)

    def test_counting_card_totals(self):
        self.hand.get_card({'r': 2, 's': 1})
        card_total = self.hand.card_total()
        self.assertEqual(card_total, 2)
        self.hand.get_card({'r': 8, 's': 1})
        card_total = self.hand.card_total()
        self.assertEqual(card_total, 10)
        self.hand.get_card({'r': 1, 's': 1})
        card_total = self.hand.card_total()
        self.assertEqual(card_total, 21)
        self.hand.get_card({'r': 1, 's': 1})
        card_total = self.hand.card_total()
        self.assertEqual(card_total, 12)

    def test_if_hand_is_busted(self):
        self.hand.get_card({'r': 2, 's': 1})
        is_busted = self.hand.is_busted()
        self.assertFalse(is_busted)
        self.hand.get_card({'r': 8, 's': 1})
        self.hand.get_card({'r': 4, 's': 1})
        self.hand.get_card({'r': 13, 's': 1})
        is_busted = self.hand.is_busted()
        self.assertTrue(is_busted)

    def test_if_hand_is_blackjack(self):
        self.hand.get_card({'r': 1, 's': 1})
        self.hand.get_card({'r': 13, 's': 1})
        is_blackjack = self.hand.is_blackjack()
        self.assertTrue(is_blackjack)

    def test_if_hand_is_twentyone(self):
        self.hand.get_card({'r': 1, 's': 1})
        self.hand.get_card({'r': 6, 's': 1})
        self.hand.get_card({'r': 4, 's': 1})
        is_twentyone = self.hand.is_twentyone()
        self.assertTrue(is_twentyone)

    def test_that_hand_accepts_cards(self):
        hand = Hand(bet=10)
        cards=[{'r': 8, 's': 1}, {'r': 4, 's': 1}]
        hand.set_cards(cards)
        self.assertEqual(hand.cards, cards)


if __name__ == '__main__':
    unittest.main()
