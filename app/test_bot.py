import unittest
from bot import Bot
from hand import Hand
from shoe import Shoe


class TestBot(unittest.TestCase):

    def setUp(self) -> None:
        self.bot = Bot()
        self.shoe = Shoe()

    def test_initialize_a_bot(self):
        self.assertIsInstance(self.bot, Bot)

    def test_bot_has_strategies(self):
        self.assertIsInstance(self.bot.strategies, dict)

    def test_bot_can_add_strategies(self):
        self.assertTrue(callable(self.bot.add_strategies))
        self.assertEqual(self.bot.add_strategies.__name__, 'add_strategies')

    def test_bot_can_apply_strategies(self):
        self.assertTrue(callable(self.bot.apply_strategies))
        self.assertEqual(self.bot.apply_strategies.__name__, 'apply_strategies')
        hand = Hand(bet=10).set_cards([{'r': 8, 's': 1}, {'r': 8, 's': 1}])
        params = self.bot.get_params({
            'is_bet': False,
            'is_insurance': False,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand],
            'up_card': 6,
            'shoe': Shoe(),
            'player': True}
        )
        move = self.bot.apply_strategies(params, self.bot.strategies['split'])
        self.assertEqual(move, 'split')

    def test_bot_can_add_a_strategy_for_split_move(self):
        self.assertEqual(len(self.bot.strategies.keys()), 7)

    def test_bot_has_moves(self):
        self.assertIsInstance(self.bot.dealer_moves, dict)
        moves = [x for x in self.bot.dealer_moves.keys()]
        self.assertEqual(moves, ['hit', 'stand'])
        self.assertEqual(self.bot.dealer_moves['stand'].__name__, 'stand')

    def test_bot_can_make_a_bet(self):
        self.assertTrue(callable(self.bot.make_bet))
        self.assertEqual(self.bot.make_bet.__name__, 'make_bet')

    def test_bot_can_decide_to_make_a_bet(self):
        hand = Hand(bet=10).set_cards([{'r': 8, 's': 1}, {'r': 9, 's': 1}])
        self.shoe.count = 36
        params = self.bot.get_params({
            'is_bet': True,
            'is_insurance': False,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand],
            'up_card': 1,
            'shoe': self.shoe
        })
        move = self.bot.make_bet(params)
        self.assertEqual(move, 'bet')

    def test_bot_can_get_insurance(self):
        self.assertTrue(callable(self.bot.get_insurance))
        self.assertEqual(self.bot.get_insurance.__name__, 'get_insurance')

    def test_bot_can_decide_to_get_insurance(self):
        hand = Hand(bet=10).set_cards([{'r': 8, 's': 1}, {'r': 9, 's': 1}])
        self.shoe.count = 36
        params = self.bot.get_params({
            'is_bet': False,
            'is_insurance': True,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand],
            'up_card': 1,
            'shoe': self.shoe
        })
        move = self.bot.get_insurance(params)
        self.assertEqual(move, 'insurance')

    def test_bot_can_make_a_move(self):
        self.assertTrue(callable(self.bot.make_a_move))
        self.assertEqual(self.bot.make_a_move.__name__, 'make_a_move')

    def test_bot_stands_if_hand_card_total_is_17_or_above(self):
        hand = Hand(bet=10).set_cards([{'r': 8, 's': 1}, {'r': 9, 's': 1}])
        params = self.bot.get_params({
            'is_bet': False,
            'is_insurance': False,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand],
            'up_card': 6,
            'shoe': self.shoe
        })
        move = self.bot.make_a_move(params)
        self.assertEqual(move, 'stand')

    def test_bot_hits_if_hand_card_total_is_less_than_17(self):
        hand = Hand(bet=10).set_cards([{'r': 8, 's': 1}, {'r': 7, 's': 1}])
        params = self.bot.get_params({
            'is_bet': False,
            'is_insurance': False,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand],
            'up_card': 7,
            'shoe': self.shoe
        })
        move = self.bot.make_a_move(params)
        self.assertEqual(move, 'hit')

    def test_bot_splits_on_aces_or_eights(self):
        hand = Hand(bet=10).set_cards([{'r': 8, 's': 1}, {'r': 8, 's': 1}])
        params = self.bot.get_params({
            'is_bet': False,
            'is_insurance': False,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand],
            'up_card': 6,
            'shoe': self.shoe
        })
        move = self.bot.make_a_move(params)
        self.assertEqual(move, 'split')
        hand = Hand(bet=10).set_cards([{'r': 1, 's': 1}, {'r': 1, 's': 1}])
        move = self.bot.make_a_move(params)
        self.assertEqual(move, 'split')

    def test_bot_splits_on_aces_only_twice(self):
        hand = Hand(bet=10).set_cards([{'r': 1, 's': 1}, {'r': 1, 's': 1}])
        hand_1 = Hand(bet=10).set_cards([{'r': 1, 's': 1}, {'r': 1, 's': 1}])
        hand_1.split = True 
        hand_1.split_aces = True
        hand_2 = Hand(bet=10).set_cards([{'r': 1, 's': 1}, {'r': 1, 's': 1}])
        hand_2.split = True 
        hand_2.split_aces = True
        params = self.bot.get_params({
            'is_bet': False,
            'is_insurance': False,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand_1, hand_2],
            'up_card': 7,
            'shoe': self.shoe
        })
        move = self.bot.make_a_move(params)
        self.assertEqual(move, 'hit')

    def test_bot_doubles_down_on_natural_eleven(self):
        hand = Hand(bet=10).set_cards([{'r': 8, 's': 1}, {'r': 3, 's': 1}])
        params = self.bot.get_params({
            'is_bet': False,
            'is_insurance': False,
            'win_lose': 0,
            'hand': hand,
            'hands': [hand],
            'up_card': 6,
            'shoe': self.shoe
        })
        move = self.bot.make_a_move(params)
        self.assertEqual(move, 'double')


if __name__ == '__main__':
    unittest.main()
