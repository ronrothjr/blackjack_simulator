import random


class Deck:

    def __init__(self):
        self.ranks = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        self.suits = [1,2,3,4]
        self.cards = []
        [[self.cards.append({'r': r, 's': s}) for r in self.ranks] for s in self.suits]

    def shuffle(self) -> None:
        random.shuffle(self.cards)
