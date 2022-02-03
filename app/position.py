from hand import Hand

class Position:

    def __init__(self, player=None, max_bet=1000, bet_strategy='optimal'):
        self.role = 'Dealer' if player is None else 'Player'
        self.player = player
        self.hands = []
        self.bet = 0
        self.insurance = 0
        self.max_bet = max_bet
        self.bet_strategy = bet_strategy
        self.bet_spreads = {
            'optimal': [
                {'mulitplier': 1, 'calc': lambda count: count == 0},
                {'mulitplier': 1, 'calc': lambda count: count == 1},
                {'mulitplier': 4, 'calc': lambda count: count == 2},
                {'mulitplier': 8, 'calc': lambda count: count == 3},
                {'mulitplier': 12, 'calc': lambda count: count == 4},
                {'mulitplier': 16, 'calc': lambda count: count == 5},
                {'mulitplier': 20, 'calc': lambda count: count >= 6}
            ],
            'kelly': [
                {'mulitplier': 1, 'calc': lambda count: count == 0},
                {'mulitplier': 5, 'calc': lambda count: count == 1},
                {'mulitplier': 12, 'calc': lambda count: count == 2},
                {'mulitplier': 19, 'calc': lambda count: count == 3},
                {'mulitplier': 20, 'calc': lambda count: count >= 4}
            ]
        }

    def buy_in(self, amount) -> 'Position':
        if (self.player.bankroll >= amount):
            self.player.bankroll -= amount
            self.player.chips += amount
        return self

    def add_hand(self, hand=None) -> 'Position':
        self.hands.append(hand if hand else Hand(self.bet))
        return self

    def get_insurance(self, bet=None) -> None:
        insurance = int((bet if bet else self.bet) * 0.5)
        self.insurance = insurance
        for h in self.hands:
            if (insurance > self.player.chips):
                self.buy_in(insurance)
            if (insurance <= self.player.chips):
                self.player.chips -= insurance
                h.insurance = insurance
    
    def get_bet_spread(self, count) -> int:
        for spread in self.bet_spreads[self.bet_strategy]:
            if spread['calc'](count):
                multiplier = spread['mulitplier']
                return multiplier
        return 0

    def get_adjusted_bet_unit(self, count) -> int:
        bet_unit = self.player.calculate_bet_unit()
        spread = self.get_bet_spread(count)
        adjusted_bet = (spread - 1 if spread > 1 else 0) * bet_unit
        bet = bet_unit + adjusted_bet if adjusted_bet + bet_unit <= self.max_bet else self.max_bet
        return bet

    def make_a_bet(self, bet=None, count=0) -> bool:
        adjusted_bet_unit = self.get_adjusted_bet_unit(count)
        bet = adjusted_bet_unit if bet is None else bet
        if (bet > self.player.chips):
            self.buy_in(bet)
        if (bet <= self.player.chips):
            self.player.chips -= bet
            self.bet += bet
            if (len(self.hands) == 0):
                self.add_hand()
            return True

    def clear_cards(self) -> None:
        self.hands = []
    