from params import Params
from strategies import get_strategies
from strategy import Strategy


class Bot:

    def __init__(self, quit_while_behind=-100, quit_while_ahead=1000) -> None:
        self.dealer_moves = {
            'hit': self.hit,
            'stand': self.stand
        }
        self.strategies = {}
        self.add_strategies([Strategy(s) for s in get_strategies(quit_while_behind, quit_while_ahead)])

    def add_strategies(self, strategies) -> None:
        if not isinstance(strategies, list):
            strategies = [strategies]
        for strategy in strategies:
            if not self.strategies.get(strategy.move):
                self.strategies[strategy.move] = []
            self.strategies[strategy.move].append(strategy)

    def apply_strategies(self, params, strategies) -> str:
        for strategy in strategies:
            if strategy.pretest(params) and strategy.match(params):
                return strategy.move
        return ''

    def get_params(self, params) -> Params:
        win_lose = params['win_lose']
        is_bet = params['is_bet']
        is_insurance = params['is_insurance']
        cards = [c['r'] for c in params['hand'].cards] if params['hand'] else []
        number_of_cards = len(params['hand'].cards) if params['hand'] else 0
        hard_total = params['hand'].card_total() if params['hand'] else 0
        is_soft_total = number_of_cards == 2 and params['hand'].soft_total() > 11 and 1 in cards if params['hand'] else False
        true_count = params['shoe'].true_count()
        is_player = params.get('is_player', True)
        return Params(number_of_cards, win_lose, is_bet, is_insurance, cards, params['up_card'], hard_total, is_player, is_soft_total, true_count)

    def make_bet(self, is_bet, is_insurance, win_lose, hand, up_card, shoe, is_player=True) -> str:
        params = self.get_params({'is_bet': is_bet, 'is_insurance': is_insurance, 'win_lose': win_lose, 'hand': hand, 'up_card': up_card, 'shoe': shoe, 'is_player': is_player})
        if is_player:
            for strategy in self.strategies.values():
                move = self.apply_strategies(params, strategy)
                if move:
                    return move
        return ''

    def get_insurance(self, is_bet, is_insurance, win_lose, hand, up_card, shoe, is_player=True) -> str:
        params = self.get_params({'is_bet': is_bet, 'is_insurance': is_insurance, 'win_lose': win_lose, 'hand': hand, 'up_card': up_card, 'shoe': shoe, 'is_player': is_player})
        is_player_without_a_blackjack = is_player and not hand.is_blackjack()
        if is_player_without_a_blackjack:
            for strategy in self.strategies.values():
                move = self.apply_strategies(params, strategy)
                if move:
                    return move
        return ''

    def make_a_move(self, is_bet, is_insurance, win_lose, hand, up_card, shoe, is_player=True) -> str:
        params = self.get_params({'is_bet': is_bet, 'is_insurance': is_insurance, 'win_lose': win_lose, 'hand': hand, 'up_card': up_card, 'shoe': shoe, 'is_player': is_player})
        if is_player:
            for strategy in self.strategies.values():
                move = self.apply_strategies(params, strategy)
                if move:
                    return move
        else:
            for move, test in self.dealer_moves.items():
                if test(params):
                    return move

    def hit(self, _: Params) -> bool:
        return _.hard_total < 17

    def stand(self, _: Params) -> bool:
        return _.hard_total >= 17
