from dealer import Dealer
from player import Player
from position import Position
from session_options import SessionOptions
from table import Table


class Session:

    def __init__(self, table=None, dealer=None, options: SessionOptions=None, stats=None):
        self.stats = stats
        self.options = SessionOptions(options)
        self.table: Table = table if table else Table()
        self.dealer: Dealer = dealer if dealer else Dealer(table=self.table, stats=stats)
        self.positions: list(Position) = self.table.positions
        self.rounds_to_play: int = self.options.hours_per_session * 80

    def run_session(self) -> 'Session':
        self.add_players(1)
        [self.dealer.deal_round(self.add_player) for x in range(0, self.rounds_to_play)]
        self.update_bankroll()
        return self

    def update_bankroll(self) -> None:
        player_stats = self.dealer.positions['Player 1'].player.stats
        self.options.bankroll += player_stats.balance

    def add_players(self, number_of_players=None) -> None:
        number_of_players = number_of_players if number_of_players else self.options.number_of_players
        for x in range(1, number_of_players + 1):
            self.add_player(self.dealer.table, f'Player {x}')
    
    def add_player(self, table, position) -> None:
        if self.options.re_join_after_bust:
            player = Player(bankroll=self.options.bankroll, risk_of_ruin=self.options.risk_of_ruin)
            table.join(player, position, self.options.buy_in)

    def report_stats(self) -> dict:
        stats = {}
        stats['Dealer'] = self.dealer.stats
        for name, position in self.dealer.positions.items():
            if position and position.player:
                stats[name] = position.player.stats
        return stats
