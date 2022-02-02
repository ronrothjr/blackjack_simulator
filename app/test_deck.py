import unittest
from deck import Deck


class TestDeck(unittest.TestCase):

    def setUp(self) -> None:
        self.deck = Deck()

    def test_initialize_a_deck(self):
        self.assertIsInstance(self.deck, Deck)

    def test_deck_has_an_array_of_integers_for_card_ranks_and_suits(self):
        self.assertIsInstance(self.deck.ranks, list)
        self.assertIsInstance(self.deck.ranks[0], int)
        self.assertIsInstance(self.deck.suits, list)
        self.assertIsInstance(self.deck.suits[0], int)

    def test_deck_has_an_array_of_52_cards(self):
        self.assertIsInstance(self.deck.cards, list)
        self.assertEqual(len(self.deck.cards), 52)

    def test_shuffle_randomizes_the_cards(self):
        self.assertEqual(self.deck.cards[0:3], [{'r': 1, 's': 1}, {'r': 2, 's': 1}, {'r': 3, 's': 1}])
        self.deck.shuffle()
        self.assertNotEqual(self.deck.cards[0:3], [{'r': 1, 's': 1}, {'r': 2, 's': 1}, {'r': 3, 's': 1}])


if __name__ == '__main__':
    unittest.main()
