import random


class Hand:

    def __init__(self, bet=0):
        self.cards = []
        self.bet = bet
        self.insurance = 0
        self.busted = False
        self.doubled = False
        self.split = False
        self.final = ''
        self.outcome = ''

    def get_card(self, card) -> None:
        self.cards.append(card)

    def set_cards(self, cards) -> 'Hand':
        self.cards = cards
        return self

    def card_total(self) -> int:
        total = 0
        aces = []
        for card in self.cards:
            if card['r'] == 1:
                aces.append(1)
            else:
                total += 10 if card['r'] > 10 else card['r']
        for card in aces:
            total += 11 if total <= 10 and len(aces) == 1 else 1
        return total

    def soft_total(self) -> int:
        total = 0
        for card in self.cards:
            total += 10 if card['r'] > 10 else ( 11 if card['r'] == 1 else card['r'])
        return total

    def is_busted(self) -> bool:
        return self.card_total() > 21

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.card_total() == 21

    def is_twentyone(self) -> bool:
        return self.card_total() == 21
