from stats import Stats


class Player:

    def __init__(self, bankroll=0, bet_unit=0, risk_of_ruin=1.0):
        self.stats = Stats()
        self.stats.bankroll = int(bankroll)
        self.chips = 0
        self.bankroll = bankroll
        self.bet_unit = bet_unit
        self.risk_of_ruin = risk_of_ruin
        self.ror_sets = [
            {'bet_units': 200, 'risk_of_ruin': 40.0},
            {'bet_units': 300, 'risk_of_ruin': 30.0},
            {'bet_units': 400, 'risk_of_ruin': 20.0},
            {'bet_units': 500, 'risk_of_ruin': 10.0},
            {'bet_units': 750, 'risk_of_ruin': 5.0},
            {'bet_units': 1000, 'risk_of_ruin': 1.0}
        ]
        self.calculate_bet_unit()

    def calculate_bet_unit(self, risk_of_ruin=None) -> None:
        if risk_of_ruin:
            self.risk_of_ruin = risk_of_ruin
        total_units = self.bankroll + self.chips
        if total_units < 1000:
            return 5
        ror = list(filter(lambda x: (x['risk_of_ruin'] == self.risk_of_ruin), self.ror_sets))
        bet_units = ror[0]['bet_units']
        ror_bet = int(total_units / bet_units)
        allowed_bet = int(ror_bet / 5) * 5
        self.bet_unit = allowed_bet if allowed_bet > 5 else 5
        return self.bet_unit

    def add_to_bankroll(self, amount) -> None:
        self.bankroll += amount
        self.stats.bankroll += amount
        self.calculate_bet_unit()

    def buy(self, amount) -> bool:
        if self.bankroll >= amount:
            self.chips = amount
            return True
