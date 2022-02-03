import copy, random, traceback
from bot import Bot
from hand import Hand
from player import Player
from position import Position
from stats import Stats
from table import Table


class Dealer:

    def __init__(self, table, quit_while_behind=-100, quit_while_ahead=1000, stats=None):
        self.table: Table = table
        self.positions: list[Position] = table.positions
        self.bot = Bot(quit_while_behind, quit_while_ahead)
        self.stats = stats if stats else Stats()
        self.discard = []
        self.shuffle_in = False

    def deal_round(self, add_player) -> int:
        try:
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
        except Exception as e:
            print(e)
            traceback.print_stack()
            return 0

    def leave_or_join(self):
        pass

    def take_bet(self, position: str) -> bool:
        if (not self.table.is_open(position)):
            p = self.positions[position]
            divisor = p.player.stats.bankroll if p.player.stats.bankroll else 1
            win_lose = (p.player.bankroll + p.player.chips - p.player.stats.bankroll) / divisor
            params = self.bot.get_params({
                'is_bet': True,
                'is_insurance': False,
                'win_lose': win_lose,
                'hand': None,
                'hands': [],
                'up_card': 1,
                'shoe': self.table.shoe,
                'is_player': True
            })
            make_bet = self.bot.make_bet(params)
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
                p.hands = []
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

    def get_card_or_shuffle_in(self):
        card = self.table.shoe.draw()
        if not card:
            self.table.shoe.refill_the_shoe(copy.deepcopy(self.discard))
            card = self.table.shoe.draw()
            self.shuffle_in = True
            self.discard = []
        return card

    def deal_table(self) -> None:
        for x in ['hole', 'up']:
            for p in self.positions.values():
                if p and p.hands:
                    for h in p.hands:
                        card = self.get_card_or_shuffle_in()
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
                        divisor = p.player.stats.bankroll if p.player.stats.bankroll else 1
                        win_lose = p.player.bankroll - p.player.stats.bankroll / divisor
                        params = self.bot.get_params({
                            'is_bet': False,
                            'is_insurance': True,
                            'win_lose': win_lose,
                            'hand': h,
                            'hands': p.hands,
                            'up_card': up_card,
                            'shoe': self.table.shoe,
                            'is_player': True
                        })
                        decision = self.bot.get_insurance(params)
                        if decision:
                            p.get_insurance(h.bet)
                            p.player.stats.insurance += 1
                            self.stats.insurance += 1

    def deal_hand(self, p: Position, hand: Hand, player: bool) -> None:
        win_lose = 0
        if p.player:    
            divisor = p.player.stats.bankroll if p.player.stats.bankroll else 1
            win_lose = p.player.bankroll - p.player.stats.bankroll / divisor
        dealer = self.positions['Dealer'].hands[0].cards
        up_card = 10 if dealer[1]['r'] > 9 else dealer[1]['r']
        while not hand.final:
            if self.table.is_round_over():
                if hand.is_blackjack():
                    hand.final = 'blackjack'
                else:
                    hand.final = hand.final if hand.final else 'stand'
            true_count = self.table.shoe.true_count()
            params = self.bot.get_params({
                'is_bet': False,
                'is_insurance': False,
                'win_lose': win_lose,
                'hand': hand,
                'hands': p.hands,
                'up_card': up_card,
                'shoe': self.table.shoe,
                'is_player': player
            })
            move = self.bot.make_a_move(params)
            if hand.is_blackjack() and not hand.doubled and not hand.split:
                hand.final = 'blackjack'
            elif hand.is_twentyone():
                hand.final = 'twentyone'
            elif hand.is_busted():
                hand.final = 'busted'
            elif move == 'surrender':
                hand.final = 'surrender'
            elif move == 'split':
                hand.split = True
                cards = copy.copy(hand.cards)
                hand.split_aces = cards[0]['r'] == 1 and cards[1]['r'] == 1
                split_hand = copy.copy(hand)
                hand.cards = [cards[0]]
                hand.split = True
                card = self.get_card_or_shuffle_in()
                hand.get_card(card)
                split_hand.cards = [cards[1]]
                split_hand.split = True
                card = self.get_card_or_shuffle_in()
                split_hand.get_card(card)
                self.deal_hand(p, split_hand, player)
            elif move == 'double':
                bet_made = p.make_a_bet(bet=hand.bet, count=true_count)
                if bet_made:
                    hand.bet += hand.bet
                    hand.doubled = True
                    card = self.get_card_or_shuffle_in()
                    hand.get_card(card)
                    hand.final = 'stand'
                else:
                    card = self.get_card_or_shuffle_in()
                    hand.get_card(card)
            elif move == 'stand':
                hand.final = 'stand'
            elif move == 'hit':
                card = self.get_card_or_shuffle_in()
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
                    self.set_stats(p, h, d, p.player, h.outcome)
        return balance

    def set_stats(self, position: Position, p: Hand, d: Hand, player: Player, outcome):
        if not position:
            return
        if not p:
            return
        if d.final == 'blackjack' and p.final != 'blackjack' and p.insurance:
            player.stats.insurance_claims += 1
            self.stats.insurance_claims += 1
        setattr(player.stats, outcome, getattr(player.stats, outcome) + 1)
        setattr(self.stats, outcome, getattr(self.stats, outcome) + 1)
        if p.doubled:
            setattr(player.stats, 'doubles', getattr(player.stats, 'doubles') + 1)
            setattr(self.stats, 'doubles', getattr(self.stats, 'doubles') + 1)
        self.set_card_stats(self.stats, p, d)
        self.set_card_stats(player.stats, p, d)
    
    def set_card_stats(self, stats, p: Hand, d: Hand):
        cards = list([c['r'] for c in p.cards[:2]])
        cards.sort()
        cards = ','.join([str(card if card < 11 else 10) for card in cards])
        dealer = d.cards[0]["r"] if d.cards[0]["r"] < 10 else 10
        case = f'{cards}-{dealer}'
        card_case = stats.cards.get(case, {'count': 0, 'wins': 0})
        count = card_case.get('count') + 1
        wins = card_case.get('wins') + (1 if p.outcome in ['pay', 'blackjack'] else 0)
        card_case.update(count=count, wins=wins)
        stats.cards[case] = card_case

    def blackjack(self, hand: Hand, player: Player) -> int:
        win = int(hand.bet * 1.5)
        player.chips += hand.bet + win
        player.stats.balance += win
        player.stats.win += 1
        divisor = player.stats.hands if player.stats.hands else 1
        player.stats.win_percentage = player.stats.win / divisor
        self.stats.win += 1
        return win
    
    def pay(self, hand: Hand, player: Player) -> int:
        win = hand.bet * 2
        player.chips += win - hand.insurance
        player.stats.balance += hand.bet - hand.insurance
        player.stats.win += 1
        divisor = player.stats.hands if player.stats.hands else 1
        player.stats.win_percentage = player.stats.win / divisor
        self.stats.win += 1
        return hand.bet - hand.insurance
    
    def push(self, hand: Hand, player: Player) -> int:
        player.chips += hand.bet - hand.insurance
        player.stats.balance += 0 - hand.insurance
        player.stats.win += 1
        self.stats.win += 1
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
                for h in p.hands:
                    self.discard += copy.deepcopy(h.cards)
                p.clear_cards()
        is_shoe_depleted = len(self.table.shoe.cards) < players * 5
        if is_shoe_depleted or self.shuffle_in:
            self.discard = []
            self.shuffle_in = False
            self.table.shoe.refill_the_shoe()
