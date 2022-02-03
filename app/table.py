from position import Position
from shoe import Shoe


class Table:

    def __init__(self, max_bet=1000, bet_strategy='optimal'):
        self.max_bet = max_bet
        self.bet_strategy = bet_strategy
        self.shoe = Shoe()
        self.positions = {
            'Player 1': None,
            'Player 2': None,
            'Player 3': None,
            'Player 4': None,
            'Player 5': None,
            'Player 6': None,
            'Player 7': None,
            'Dealer': Position()
        }

    def is_open(self, position) -> bool:
        if (self.positions[position] is None):
            return True

    def join(self, player, position, buy_in_amount) -> bool:
        if (self.is_open(position)):
            self.positions[position] = Position(player, max_bet=self.max_bet, bet_strategy=self.bet_strategy)
            self.positions[position].buy_in(buy_in_amount)
            return True

    def leave(self, position) -> bool:
        if (not self.is_open(position)):
            self.positions[position] = None
            return True

    def is_round_over(self) -> bool:
        dealer_has_blackjack = self.positions['Dealer'].hands[0].is_blackjack()
        hand_needs_dealer_cards = lambda h: not h.is_busted() and not h.is_blackjack()
        position_needs_dealer_cards = lambda p: p and p.role == 'Player' and len(list(filter(hand_needs_dealer_cards, p.hands))) > 0
        players_need_dealer_cards = len(list(filter(position_needs_dealer_cards, self.positions.values()))) > 0
        round_is_over = dealer_has_blackjack or not players_need_dealer_cards
        return round_is_over

