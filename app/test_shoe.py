import unittest

from shoe import Shoe


class TestShoe(unittest.TestCase):

    def setUp(self) -> None:
        self.shoe = Shoe(number_of_decks=6)

    def test_initiliaze_a_shoe(self):
        self.assertIsInstance(self.shoe, Shoe)

    def test_shoe_has_randomized_cards(self):
        self.assertIsInstance(self.shoe.cards, list)
        self.assertTrue(len(self.shoe.cards) > 0)

    def test_shoe_has_a_hi_lo_running_count(self):
        self.assertIsInstance(self.shoe.count, int)

    def test_shoe_can_count_the_hi_lo_value_of_a_card(self):
        self.assertEqual(self.shoe.count_value.__name__, 'count_value') 
        self.assertTrue(callable(self.shoe.count_value))
        card_value = self.shoe.count_value({'r': 7, 's': 2})
        self.assertEqual(card_value, 0)
        card_value = self.shoe.count_value({'r': 4, 's': 2})
        self.assertEqual(card_value, 1)
        card_value = self.shoe.count_value({'r': 12, 's': 2})
        self.assertEqual(card_value, -1)

    def test_shoe_can_calculate_the_true_running_count(self):
        self.assertEqual(self.shoe.true_count.__name__, 'true_count') 
        self.assertTrue(callable(self.shoe.true_count))
        self.shoe.count = 4
        self.shoe.cards = self.shoe.cards[0:104]
        true_count = self.shoe.true_count()
        self.assertEqual(true_count, 2)

    def test_draw_card_takes_the_top_card_from_shoe(self):
        original_len = len(self.shoe.cards)
        top_card = self.shoe.cards[0]
        # with patch('Shoe.card_count_value', return_value=1)
        card = self.shoe.draw()
        after_top_card_drawn_len = len(self.shoe.cards)
        self.assertEqual(top_card, card)
        self.assertGreater(original_len, after_top_card_drawn_len)
        top_card = self.shoe.cards[0]
        card = self.shoe.draw()
        after_next_card_drawn_len = len(self.shoe.cards)
        self.assertEqual(top_card, card)
        self.assertGreater(after_top_card_drawn_len, after_next_card_drawn_len)


if __name__ == '__main__':
    unittest.main()
