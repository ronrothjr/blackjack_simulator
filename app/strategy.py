import copy
from re import I
from params import Params


class Strategy:

    def __init__(self, options) -> None:
        self.move = options['move']
        self.pretest = options['pretest']
        self.matrix = options['matrix']
        self.index = options['index'] or (lambda _: ','.join([str(card) for card in _.c]))
        self.index_on = options['index_on']

    def match(self, _: Params) -> bool:
        params = copy.copy(_)
        params.cards.sort()
        self.index(params)
        index_param = getattr(params, self.index_on)
        match_index = self.matrix.get(index_param, False)
        if isinstance(match_index, bool):
            return match_index
        if callable(match_index):
            is_match = match_index(params)
            return is_match
        return False
