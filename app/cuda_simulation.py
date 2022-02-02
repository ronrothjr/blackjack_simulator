import copy, json, os, random
from concurrent.futures import ProcessPoolExecutor
from numba import jit, cuda


@cuda.jit
def run_simulation(simulation) -> None:


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
                'pretest': lambda _: _.number_of_cards == 2 and not _.is_bet and not _.is_insurance,
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


    class Stats:

        def __init__(self):
            self.cards = {}
            self.bankroll = 0
            self.rounds = 0
            self.leaves = 0
            self.hands = 0
            self.insurance = 0
            self.insurance_claims = 0
            self.win = 0
            self.blackjack = 0
            self.doubles = 0
            self.pay = 0
            self.lose = 0
            self.push = 0
            self.surrender = 0
            self.balance = 0
            self.win_percentage = 0


    class Params:

        def __init__(self, number_of_cards, win_lose, is_bet, is_insurance, cards, up_card, hard_total, is_player, is_soft_total, true_count):
            self.number_of_cards = number_of_cards
            self.win_lose = win_lose
            self.is_bet = is_bet
            self.is_insurance = is_insurance
            self.cards = cards
            self.up_card = up_card
            self.hard_total = hard_total
            self.is_player = is_player
            self.is_soft_total = is_soft_total
            self.true_count = true_count

        def update(self, number_of_cards=None, win_lose=None, is_bet=None, is_insurance=None, cards=None, up_card=None, hard_total=None, is_player=None, is_soft_total=None, true_count=None) -> None:
            self.number_of_cards = number_of_cards if number_of_cards is not None else self.number_of_cards
            self.win_lose = win_lose if win_lose is not None else self.win_lose
            self.is_bet = is_bet if is_bet is not None else self.is_bet
            self.is_insurance = is_insurance if is_insurance is not None else self.is_insurance
            self.cards = cards if cards is not None else self.cards
            self.up_card = up_card if up_card is not None else self.up_card
            self.hard_total = hard_total if hard_total is not None else self.hard_total
            self.is_player = is_player if is_player is not None else self.is_player
            self.is_soft_total = is_soft_total if is_soft_total is not None else self.is_soft_total
            self.true_count = true_count if true_count is not None else self.true_count


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


    class Deck:

        def __init__(self):
            self.ranks = [1,2,3,4,5,6,7,8,9,10,11,12,13]
            self.suits = [1,2,3,4]
            self.cards = []
            [[self.cards.append({'r': r, 's': s}) for r in self.ranks] for s in self.suits]

        def shuffle(self) -> None:
            random.shuffle(self.cards)


    class Shoe:

        def __init__(self, number_of_decks=6):
            self.number_of_decks = number_of_decks
            self.cards = []
            self.count = 0
            self.refill_the_shoe()

        def refill_the_shoe(self) -> None:
            self.cards = []
            self.count = 0
            for x in range(self.number_of_decks):
                self.cards += Deck().cards
            random.shuffle(self.cards)

        def draw(self) -> dict:
            card = self.cards.pop(0)
            self.count += self.count_value(card)
            return card

        def count_value(self, card) -> int:
            if card['r'] in [2,3,4,5,6]:
                return 1
            if card['r'] in [1,10,11,12,13]:
                return -1
            return 0

        def true_count(self) -> int:
            divisor = len(self.cards) / 52
            return int( self.count / (divisor if divisor > 0 else 1) )


    class Hand:

        def __init__(self, bet=0):
            self.cards = []
            self.bet = bet
            self.insurance = 0
            self.doubled = False
            self.final = ''
            self.outcome = ''

        def get_card(self, card) -> None:
            self.cards.append(card)

        def set_cards(self, cards) -> 'Hand':
            self.cards = cards
            return self

        def card_total(self) -> int:
            total = 0
            aces = []
            for card in self.cards:
                if card['r'] == 1:
                    aces.append(1)
                else:
                    total += 10 if card['r'] > 10 else card['r']
            for card in aces:
                total += 11 if total <= 10 and len(aces) == 1 else 1
            return total

        def soft_total(self) -> int:
            total = 0
            for card in self.cards:
                total += 10 if card['r'] > 10 else ( 11 if card['r'] == 1 else card['r'])
            return total

        def is_busted(self) -> bool:
            return self.card_total() > 21

        def is_blackjack(self) -> bool:
            return len(self.cards) == 2 and self.card_total() == 21

        def is_twentyone(self) -> bool:
            return self.card_total() == 21


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
            if self.bankroll > 0:
                ror = list(filter(lambda x: (x['risk_of_ruin'] == self.risk_of_ruin), self.ror_sets))
                self.bet_unit = int(self.bankroll / ror[0]['bet_units'])

        def add_to_bankroll(self, amount) -> None:
            self.bankroll += amount
            self.stats.bankroll += amount
            self.calculate_bet_unit()

        def buy(self, amount) -> bool:
            if self.bankroll >= amount:
                self.chips = amount
                return True


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

        def add_hand(self) -> None:
            self.hands.append(Hand(self.bet))

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
            adjusted_bet_unit = (count * 11 if count > 0 else 0) * self.player.bet_unit
            max_bet_adjustment = self.player.bet_unit * 11
            bet = self.player.bet_unit + (adjusted_bet_unit if adjusted_bet_unit <= max_bet_adjustment else max_bet_adjustment)
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


    class Table:

        def __init__(self):
            self.shoe = Shoe()
            self.positions = {
                'Player 1': None,
                'Player 2': None,
                'Player 3': None,
                'Player 4': None,
                'Player 5': None,
                'Player 6': None,
                'Player 7': None,
                'Dealer': Position()
            }

        def is_open(self, position) -> bool:
            if (self.positions[position] is None):
                return True

        def join(self, player, position, buy_in_amount) -> bool:
            if (self.is_open(position)):
                self.positions[position] = Position(player)
                self.positions[position].buy_in(buy_in_amount)
                return True

        def leave(self, position) -> bool:
            if (not self.is_open(position)):
                self.positions[position] = None
                return True


    class Dealer:

        def __init__(self, table, quit_while_behind=-100, quit_while_ahead=1000):
            self.table: Table = table
            self.positions: list[Position] = table.positions
            self.bot = Bot(quit_while_behind, quit_while_ahead)
            self.stats = Stats()

        def deal_round(self, add_player) -> int:
            self.get_bets(add_player)
            self.deal_table()
            self.get_insurance()
            self.resolve_hands()
            balance = self.resolve_bets()
            self.clear_table()
            self.stats.balance += balance
            self.stats.rounds += 1
            self.stats.win_percentage = self.stats.win / (self.stats.hands if self.stats.hands > 0 else 1)
            return balance

        def leave_or_join(self):
            pass

        def take_bet(self, position: str) -> bool:
            if (not self.table.is_open(position)):
                p = self.positions[position]
                loss = (p.player.bankroll + p.player.chips - p.player.stats.bankroll) / p.player.stats.bankroll
                if loss:
                    loss
                make_bet = self.bot.make_bet(True, False, loss, None, 1, self.table.shoe, True)
                if make_bet:
                    true_count = self.table.shoe.true_count()
                    bet_made = p.make_a_bet(count=true_count)
                    if not bet_made:
                        bet_made
                    return bet_made
                return False

        def get_bets(self, add_player=None) -> None:
            for n, p in self.positions.items():
                if p and p.role == 'Dealer':
                    p.add_hand()
                elif p and p.role == 'Player':
                    bet_made = self.take_bet(n)
                    if bet_made:
                        p.player.stats.hands += 1
                    elif bet_made and add_player:
                        p.player.stats.leaves += 1
                        self.stats.leaves += 1
                        self.table.leave(n)
                        add_player(self.table, n)

        def deal_table(self) -> None:
            for x in ['hole', 'up']:
                for p in self.positions.values():
                    if p and p.hands:
                        for h in p.hands:
                            card = self.table.shoe.draw()
                            h.get_card(card)

        def get_insurance(self) -> None:
            dealer = self.positions['Dealer'].hands[0].cards
            up_card = 10 if dealer[1]['r'] > 9 else dealer[1]['r']
            if not up_card == 1:
                return
            for n, p in self.positions.items():
                if p and p.role == 'Player' and not p.insurance:
                    if p.hands:
                        for h in p.hands:
                            loss = p.player.bankroll - p.player.stats.bankroll / p.player.stats.bankroll
                            decision = self.bot.get_insurance(False, True, loss, h, up_card, self.table.shoe, True)
                            if decision:
                                p.get_insurance(h.bet)
                                p.player.stats.insurance += 1
                                self.stats.insurance += 1

        def deal_hand(self, p: Position, hand: Hand, player: bool) -> None:
            loss = p.player.bankroll - p.player.stats.bankroll / p.player.stats.bankroll if p.player else 0
            dealer = self.positions['Dealer'].hands[0].cards
            up_card = 10 if dealer[1]['r'] > 9 else dealer[1]['r']
            while not hand.final:
                true_count = self.table.shoe.true_count()
                move = self.bot.make_a_move(False, False, loss, hand, up_card, self.table.shoe, player)
                if hand.is_blackjack():
                    hand.final = 'blackjack'
                elif hand.is_twentyone():
                    hand.final = 'twentyone'
                elif hand.is_busted():
                    hand.final = 'busted'
                elif move == 'surrender':
                    hand.final = 'surrender'
                elif move == 'split':
                    cards = copy.copy(hand.cards)
                    split_to_hand = copy.copy(hand)
                    hand.cards = [cards[0]]
                    card = self.table.shoe.draw()
                    hand.get_card(card)
                    split_to_hand.cards = [cards[1]]
                    card = self.table.shoe.draw()
                    split_to_hand.get_card(card)
                    self.deal_hand(p, split_to_hand, player)
                elif move == 'double':
                    bet_made = p.make_a_bet(bet=hand.bet, count=true_count)
                    if bet_made:
                        hand.bet += hand.bet
                        hand.doubled = True
                        card = self.table.shoe.draw()
                        hand.get_card(card)
                        hand.final = 'stand'
                    else:
                        card = self.table.shoe.draw()
                        hand.get_card(card)
                elif move == 'stand':
                    hand.final = 'stand'
                elif move == 'hit':
                    card = self.table.shoe.draw()
                    hand.get_card(card)
            self.stats.hands += 1 if player else 0

        def resolve_hands(self) -> None:
            for p in self.positions.values():
                if p and p.hands:
                    player = p.role == 'Player'
                    if player:
                        p.player.stats.rounds += 1 if player else 0
                    for h in p.hands:
                        self.deal_hand(p, h, player)

        def get_outcome(self, d: Hand, p: Hand) -> str:
            final_outcome = None
            d_total = d.card_total()
            p_total = p.card_total()
            outcomes = [
                {'result': 'blackjack', 'test': p.final == 'blackjack' and d.final != 'blackjack'},
                {'result': 'lose', 'test': d.final == 'blackjack' and p.final != 'blackjack'},
                {'result': 'surrender', 'test': p.final == 'surrender'},
                {'result': 'lose', 'test': p.final == 'busted'},
                {'result': 'pay', 'test': p.final in ['stand', 'twentyone'] and p_total > d_total or d.final == 'busted'},
                {'result': 'lose', 'test': p.final and p_total < d_total},
                {'result': 'push', 'test': p.final and p_total == d_total}
            ]
            for outcome in outcomes:
                if outcome['test']:
                    final_outcome = outcome['result']
                    break
            return final_outcome
        
        def resolve_bets(self) -> int:
            balance = 0
            resolutions = {
                'blackjack': self.blackjack,
                'pay': self.pay,
                'push': self.push,
                'lose': self.lose,
                'surrender': self.surrender
            }
            d = self.positions['Dealer'].hands[0]
            for p in self.positions.values():
                if p and p.role == 'Player' and p.hands:
                    for h in p.hands:
                        h.outcome = self.get_outcome(d, h)
                        balance += resolutions[h.outcome](h, p.player)
                        self.get_card_stats(p, h, d, p.player, h.outcome)
            return balance

        def get_card_stats(self, position: Position, p: Hand, d: Hand, player: Player, outcome):
            if d.final == 'blackjack' and p.final != 'blackjack' and p.insurance:
                player.stats.insurance_claims += 1
                self.stats.insurance_claims += 1
            setattr(player.stats, outcome, getattr(player.stats, outcome) + 1)
            setattr(self.stats, outcome, getattr(self.stats, outcome) + 1)
            if p.doubled:
                setattr(player.stats, 'doubles', getattr(player.stats, 'doubles') + 1)
                setattr(self.stats, 'doubles', getattr(self.stats, 'doubles') + 1)
        
        def blackjack(self, hand: Hand, player: Player) -> int:
            win = int(hand.bet * 1.5)
            player.chips += hand.bet + win
            player.stats.balance += win
            player.stats.win += 1
            player.stats.win_percentage = player.stats.win / player.stats.hands
            self.stats.win += 1
            return win
        
        def pay(self, hand: Hand, player: Player) -> int:
            win = hand.bet * 2
            player.chips += win - hand.insurance
            player.stats.balance += hand.bet - hand.insurance
            player.stats.win += 1
            player.stats.win_percentage = player.stats.win / player.stats.hands
            self.stats.win += 1
            return hand.bet - hand.insurance
        
        def push(self, hand: Hand, player: Player) -> int:
            player.chips += hand.bet - hand.insurance
            player.stats.balance += 0 - hand.insurance
            return 0 - hand.insurance
        
        def lose(self, hand: Hand, player: Player) -> int:
            player.stats.balance += -(hand.bet) - hand.insurance
            return -(hand.bet) - hand.insurance
        
        def surrender(self, hand: Hand, player: Player) -> int:
            win = int(hand.bet * 0.5) - hand.insurance
            player.chips += win
            player.stats.balance += win
            return win

        def clear_table(self) -> None:
            players = 1
            for p in self.positions.values():
                if p and p.hands:
                    p.bet = 0
                    players += 1
                    p.clear_cards()
            is_shoe_depleted = len(self.table.shoe.cards) < players * 20
            if is_shoe_depleted:
                self.table.shoe.refill_the_shoe()


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


    class Session:

        def __init__(self, table=None, dealer=None, options: SessionOptions=None):
            self.options = SessionOptions(options)
            self.table: Table = table if table else Table()
            self.dealer: Dealer = dealer if dealer else Dealer(self.table)
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


    risk_of_ruin = lambda bankroll, starting_risk, bankroll_threshold, threshold_risk: starting_risk if bankroll < bankroll_threshold else threshold_risk
    print(f'STARTING {simulation["number_of_simulations"]} simulations for the following case:\n{simulation}')
    results = {}
    results['starting_bankroll'] = simulation['starting_bankroll']
    results['wins'] = 0
    results['winnings'] = 0
    for x in range(0, simulation['number_of_simulations']):
        bankroll = int(results['starting_bankroll'])
        results['sessions'] = []
        for x in range(0, 24):
            ror = risk_of_ruin(bankroll, simulation['starting_risk'], simulation['bankroll_threshold'], simulation['threshold_risk'])
            options = simulation.get('options', {})
            options.update({'bankroll': bankroll, 'risk_of_ruin': ror, 'hours_per_session': simulation['hours_per_session']})
            session = Session(options=options)
            bankroll = session.run_session().options.bankroll
            results['sessions'].append(session.report_stats())
            # print(vars(stats))
        # print(f'bankroll: {bankroll}')
        results['wins'] += 1 if bankroll > results['starting_bankroll'] else 0
        results['winnings'] += bankroll - results['starting_bankroll'] if bankroll > results['starting_bankroll'] else 0
    results['chance_of_success'] = results['wins'] / simulation['number_of_simulations']
    results['average_winnings'] = results['winnings'] / simulation['number_of_simulations']
    print(f'FINISHED:\n{simulation}')
    print(f'chance of success: {results["chance_of_success"]}')
    print(f'average winnings: {results["average_winnings"]}')


class Simulation():

    def __init__(self, test_name, number_of_simulations=None):
        self.get_cases(test_name, number_of_simulations)
        self.output = []

    def get_cases(self, test_name, number_of_simulations) -> None:
        self.local_path = os.path.dirname(os.path.realpath(__file__))
        records = open(os.path.join(self.local_path, 'cases.json'), 'r')
        file_str = records.read()
        simulations = json.loads(file_str)
        number_of_simulations = int(number_of_simulations) if number_of_simulations else simulations['number_of_simulations']
        tests = simulations['tests']
        test = tests.get(test_name)
        base = test['base']
        self.base = base if base else simulations['base']
        self.base.update(number_of_simulations=number_of_simulations)
        cases = test['cases']
        self.cases = cases if cases else [self.base]

    def start(self) -> None:
        simulations = []
        for case in self.cases:
            simulation = copy.deepcopy(self.base)
            simulation.update(case)
            simulations.append(simulation)
        with ProcessPoolExecutor(max_workers=50) as executor:
            resp = executor.map(run_simulation, simulations)


if __name__ == '__main__':
    Simulation('base_test', '500').start()