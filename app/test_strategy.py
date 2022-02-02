import unittest
from bot import Bot
from hand import Hand
from shoe import Shoe
from strategy import Strategy


class TestStrategy(unittest.TestCase):

    def setUp(self) -> None:
        self.strategy = Strategy({
            'move': 'split',
            'pretest': lambda _: _.is_player and _.number_of_cards == 2,
            'index': lambda _: _.update(cards=','.join([str(card) for card in _.cards])),
            'index_on': 'cards',
            'matrix': {
                '1,1': True,
                '8,8': True
            }
        })

    def test_initialize_a_strategy(self):
        self.assertIsInstance(self.strategy, Strategy)

    def test_strategy_has_a_move_property(self):
        self.assertIsInstance(self.strategy.move, str)

    def test_strategy_has_a_matrix_property(self):
        self.assertIsInstance(self.strategy.matrix, dict)

    def test_strategy_has_a_index_property(self):
        self.assertEqual(self.strategy.index.__name__, '<lambda>')

    def test_strategy_has_a_rule_for_matching(self):
        bot = Bot()
        shoe = Shoe()
        params = bot.get_params({'is_bet': False, 'is_insurance': False, 'win_lose': 0, 'hand': Hand().set_cards([{'r':1}, {'r':1}]), 'up_card': 6, 'shoe': shoe, 'is_player': True})
        is_pretested = self.strategy.pretest(params)
        self.assertTrue(is_pretested)
        self.assertEqual(self.strategy.match.__name__, 'match')
        self.assertTrue(callable(self.strategy.match))
        is_split = self.strategy.match(params)
        self.assertTrue(is_split)
        params = bot.get_params({'is_bet': False, 'is_insurance': False, 'win_lose': 0, 'hand': Hand().set_cards([{'r':8}, {'r':8}]), 'up_card': 6, 'shoe': shoe, 'is_player': True})
        is_split = self.strategy.match(params)
        self.assertTrue(is_split)


if __name__ == '__main__':
    unittest.main()
