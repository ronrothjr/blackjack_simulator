class Params:

    def __init__(self, number_of_cards, win_lose, is_bet, is_insurance, cards, hands, up_card, hard_total, is_player, is_soft_total, true_count):
        self.number_of_cards = number_of_cards
        self.win_lose = win_lose
        self.is_bet = is_bet
        self.is_insurance = is_insurance
        self.cards = cards
        self.hands = hands
        self.up_card = up_card
        self.hard_total = hard_total
        self.is_player = is_player
        self.is_soft_total = is_soft_total
        self.true_count = true_count

    def update(self, number_of_cards=None, win_lose=None, is_bet=None, is_insurance=None, cards=None, hands=None, up_card=None, hard_total=None, is_player=None, is_soft_total=None, true_count=None) -> None:
        self.number_of_cards = number_of_cards if number_of_cards is not None else self.number_of_cards
        self.win_lose = win_lose if win_lose is not None else self.win_lose
        self.is_bet = is_bet if is_bet is not None else self.is_bet
        self.is_insurance = is_insurance if is_insurance is not None else self.is_insurance
        self.cards = cards if cards is not None else self.cards
        self.hands = hands if hands is not None else self.hands
        self.up_card = up_card if up_card is not None else self.up_card
        self.hard_total = hard_total if hard_total is not None else self.hard_total
        self.is_player = is_player if is_player is not None else self.is_player
        self.is_soft_total = is_soft_total if is_soft_total is not None else self.is_soft_total
        self.true_count = true_count if true_count is not None else self.true_count
