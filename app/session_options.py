class SessionOptions:

    def __init__(self, options=None):
        options = options if options else dict()
        self.bankroll: int = options.get('bankroll', 5000)
        self.risk_of_ruin: int = options.get('risk_of_ruin', 1.0)
        self.buy_in: int = options.get('buy_in', 1000)
        self.number_of_players: int = options.get('number_of_players', 1)
        self.hours_per_session: int = options.get('hours_per_session', 100)
        self.re_join_after_bust: bool = options.get('re_join_after_bust', True)
        self.quit_while_behind:int = options.get('quit_while_behind', -100)
        self.quit_while_ahead:int = options.get('quit_while_behind', 1000)
