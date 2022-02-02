def get_strategies(quit_while_behind, quite_while_ahead):
    strategies = [
        {
            'move': 'bet',
            'pretest': lambda _: _.is_bet,
            'index': lambda _: _.update(is_bet=str(_.is_bet)),
            'index_on': 'is_bet',
            'matrix': {
                'True': lambda _: _.true_count > -1 and _.win_lose > quit_while_behind and _.win_lose < quite_while_ahead
            }
        },
        {
            'move': 'insurance',
            'pretest': lambda _: _.is_insurance and _.up_card == 1,
            'index': lambda _: _.update(up_card=str(_.up_card)),
            'index_on': 'up_card',
            'matrix': {
                '1': lambda _: _.true_count >= 3
            }
        },
        {
            'move': 'split',
            'pretest': lambda _: _.number_of_cards == 2 and len(_.hands) < 4 and not _.is_bet and not _.is_insurance,
            'index': lambda _: _.update(cards=','.join([str(card if card < 11 else 10) for card in _.cards])),
            'index_on': 'cards',
            'matrix': {
                '1,1': True,
                '10,10': lambda _: _.true_count >= 4 and _.up_card == 6 or _.true_count >= 5 and _.up_card == 6 or _.true_count >= 6 and _.up_card == 4,
                '9,9': lambda _: _.up_card <= 9 and _.up_card != 7,
                '8,8': True,
                '7,7': lambda _: _.up_card < 8,
                '6,6': lambda _: _.up_card < 7,
                '4,4': lambda _: _.up_card in [4, 5],
                '3,3': lambda _: _.up_card in [2, 3],
                '2,2': lambda _: _.up_card in [2, 3]
            }
        },
        {
            'move': 'double',
            'pretest': lambda _: _.number_of_cards == 2 and not _.is_bet and not _.is_insurance,
            'index': lambda _: _.update(hard_total=str(_.hard_total)),
            'index_on': 'hard_total',
            'matrix': {
                '19': lambda _: _.is_soft_total and ((_.true_count <= 0 and _.up_card == 6) or (_.true_count > 0 and _.true_count < 3 and _.up_card == 5) or (_.true_count >= 3 and _.up_card == 4)),
                '18': lambda _: _.is_soft_total and _.up_card < 7 and _.up_card > 1,
                '17': lambda _: _.is_soft_total and _.up_card < 7 and ((_.true_count <= 0 and _.up_card > 2) or (_.true_count > 0 and _.up_card == 2)),
                '16': lambda _: _.is_soft_total and _.up_card < 7 and _.up_card > 3,
                '15': lambda _: _.is_soft_total and _.up_card in [5, 6],
                '14': lambda _: _.is_soft_total and _.up_card in [5, 6],
                '11': True,
                '10': lambda _: _.up_card < 9 and _.up_card > 1,
                '9': lambda _: _.up_card < 7 and _.up_card > 2
            }
        },
        {
            'move': 'surrender',
            'pretest': lambda _: _.number_of_cards == 2 and not _.is_bet and not _.is_insurance,
            'index': lambda _:_.update(hard_total=str(_.hard_total)),
            'index_on': 'hard_total',
            'matrix': {
                '17': lambda _: _.up_card == 1,
                '16': lambda _: _.up_card in [1, 10] or (_.up_card == 9 and _.true_count < 0) or (_.up_card == 8 and _.true_count > 3),
                '15': lambda _: _.up_card == 1 and _.true_count > -2 or _.up_card == 10 and _.true_count < 1 or _.up_card == 9 and _.true_count > 1
            }
        },
        {
            'move': 'stand',
            'pretest': lambda _: not _.is_bet and not _.is_insurance,
            'index': lambda _: _.update(hard_total=str(_.hard_total)),
            'index_on': 'hard_total',
            'matrix': {
                '21': True,
                '20': True,
                '19': True,
                '18': True,
                '17': True,
                '16': lambda _: _.up_card < 7 and _.up_card > 1 or _.true_count > 2 and _.up_card == 1 or _.true_count > -1 and _.up_card == 10 or _.true_count > 3 and _.up_card == 9,
                '15': lambda _: _.up_card < 7 and _.up_card > 1 or _.true_count > 4 and _.up_card == 1 or _.true_count > 3 and _.up_card == 10,
                '14': lambda _: _.up_card < 7 and _.up_card > 1,
                '13': lambda _: _.up_card < 7 and _.up_card > 2 or _.true_count < 0 and _.up_card == 2,
                '12': lambda _: _.up_card < 7 and _.up_card > 4 or _.true_count < 1 and _.up_card == 4 or _.true_count > 1 and _.up_card == 3 or _.true_count > 2 and _.up_card == 2,
                '10': lambda _: _.true_count > 2 and _.up_card == 1 or _.true_count > 3 and _.up_card == 10,
                '9': lambda _: _.true_count > 0 and _.up_card == 2 or _.true_count > 2 and _.up_card == 7,
                '8': lambda _: _.true_count > 1 and _.up_card == 6
            }
        },
        {
            'move': 'hit',
            'pretest': lambda _: not _.is_bet and not _.is_insurance,
            'index': lambda _: _.update(hard_total=str(_.hard_total)),
            'index_on': 'hard_total',
            'matrix': {
                '16': True,
                '15': True,
                '14': True,
                '13': True,
                '12': True,
                '11': True,
                '10': True,
                '9': True,
                '8': True,
                '7': True,
                '6': True,
                '5': True,
                '4': True
            }
        }
    ]
    return strategies