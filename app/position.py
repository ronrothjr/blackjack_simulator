from hand import Hand

class Position:

    def __init__(self, player=None):
        self.role = 'Dealer' if player is None else 'Player'
        self.player = player
        self.hands = []
        self.bet = 0
        self.insurance = 0

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

    def get_adjusted_bet_unit(self, count) -> int:
        bet_unit = self.player.calculate_bet_unit()
        adjusted_bet_unit = (count * 11 if count > 0 else 0) * bet_unit
        max_bet_adjustment = bet_unit * 11
        bet = bet_unit + (adjusted_bet_unit if adjusted_bet_unit <= max_bet_adjustment else max_bet_adjustment)
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
    