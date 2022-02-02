import random
from deck import Deck


class Shoe:

    def __init__(self, number_of_decks=6):
        self.number_of_decks = number_of_decks
        self.cards = []
        self.count = 0
        self.refill_the_shoe()

    def refill_the_shoe(self, cards=None) -> None:
        if cards:
            self.cards = cards
        else:
            self.cards = []
            self.count = 0
            for x in range(self.number_of_decks):
                self.cards += Deck().cards
        random.shuffle(self.cards)
        # burn card
        card = self.draw()

    def draw(self) -> dict:
        if len(self.cards) == 0:
            return None
        card = self.cards.pop(0)
        self.count += self.count_value(card)
        return card

    def count_value(self, card) -> int:
        if card['r'] in [2,3,4,5,6]:
            return 1
        if card['r'] in [1,10,11,12,13]:
            return -1
        return 0

    def true_count(self) -> int:
        divisor = len(self.cards) / 52
        return int( self.count / (divisor if divisor > 0 else 1) )
