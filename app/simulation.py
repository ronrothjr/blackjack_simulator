import copy, json, operator, os
from concurrent.futures import ProcessPoolExecutor
from unittest import TextTestResult
from session import Session
from stats import Stats

risk_of_ruin = lambda bankroll, starting_risk, bankroll_threshold, threshold_risk: starting_risk if bankroll < bankroll_threshold else threshold_risk
output = []

class Simulation():

    def __init__(self, test_name=None, number_of_simulations=None, sessions=None, hours=None, win_rate=None):
        test_name = test_name if test_name else 'base_test'
        number_of_simulations = number_of_simulations if number_of_simulations else 10
        sessions = sessions if sessions else 10
        self.get_cases(test_name, number_of_simulations, sessions, hours, win_rate)
        self.output = []

    def get_cases(self, test_name, number_of_simulations, sessions, hours, win_rate) -> None:
        self.win_rate = win_rate
        self.local_path = os.path.dirname(os.path.realpath(__file__))
        records = open(os.path.join(self.local_path, 'cases.json'), 'r')
        file_str = records.read()
        simulations = json.loads(file_str)
        number_of_simulations = int(number_of_simulations) if number_of_simulations else simulations['number_of_simulations']
        tests = simulations['tests']
        test = tests.get(test_name)
        base = test['base']
        self.base = base if base else simulations['base']
        cases = test['cases']
        self.cases = cases if cases else [self.base]
        for case in self.cases:
            if number_of_simulations:
                case['number_of_simulations'] = number_of_simulations
            if sessions:
                case['sessions'] = int(sessions)
            if hours:
                case['hours_per_session'] = int(hours)

    def start(self) -> None:
        simulations = []
        for case in self.cases:
            simulation = copy.deepcopy(self.base)
            simulation.update(case)
            simulations.append(simulation)
        with ProcessPoolExecutor(max_workers=50) as executor:
            resp = executor.map(Simulation.run_simulation, simulations)
        if self.win_rate:
            self.collate_and_print_stats(resp)

    @staticmethod
    def run_simulation(simulation) -> None:
        stats = Stats()
        print(f'STARTING {simulation["number_of_simulations"]} simulations for the following case:\n{simulation}')
        results = {}
        results['starting_bankroll'] = simulation['starting_bankroll']
        results['wins'] = 0
        results['winnings'] = 0
        for x in range(0, simulation['number_of_simulations']):
            Simulation.run_sessions(simulation, results, stats)
        results['chance_of_success'] = results['wins'] / simulation['number_of_simulations']
        results['average_winnings'] = results['winnings'] / simulation['number_of_simulations']
        output.append(results)
        win_lose = results["bankroll"] - results["starting_bankroll"]
        print(f'FINISHED:\n{simulation}')
        print(f'bankroll: {results["bankroll"]} ({"+" if win_lose > 0 else ""}{win_lose})')
        print(f'chance of success: {results["chance_of_success"]}')
        print(f'average winnings: {results["average_winnings"]}')
        return stats

    @staticmethod
    def run_sessions(simulation, results, stats):
        bankroll = int(results['starting_bankroll'])
        results['sessions'] = []
        for x in range(0, simulation['sessions']):
            ror = risk_of_ruin(bankroll, simulation['starting_risk'], simulation['bankroll_threshold'], simulation['threshold_risk'])
            options = simulation.get('options', {})
            options.update({'bankroll': bankroll, 'risk_of_ruin': ror, 'hours_per_session': simulation['hours_per_session']})
            session = Session(options=options, stats=stats)
            bankroll = session.run_session().options.bankroll
            session_stats = session.report_stats()
            stats = session_stats['Dealer']
            results['sessions'].append(session_stats)
            # print(vars(stats))
        # print(f'bankroll: {bankroll}')
        results['bankroll'] = bankroll
        results['wins'] += 1 if bankroll > results['starting_bankroll'] else 0
        results['winnings'] += bankroll - results['starting_bankroll'] if bankroll > results['starting_bankroll'] else 0

    def collate_and_print_stats(self, resp) -> None:
        all_cards = {}
        for stats in resp:
            keys = list(stats.cards.keys())
            keys.sort()
            for c in keys:
                all_cards[c] = all_cards.get(c, {'count': 0, 'wins': 0})
                card = stats.cards.get(c)
                count = card.get('count', 0)
                wins = card.get('wins', 0)
                all_cards[c]['card'] = c
                all_cards[c]['count'] += count
                all_cards[c]['wins'] += wins
        keys = list(all_cards.keys())
        keys.sort()
        for c in keys:
            win_rate = all_cards[c]['wins'] / all_cards[c]['count']
            all_cards[c]['win_rate'] = float("{:.4}".format(win_rate * 100))
        sorted_cards = sorted(all_cards.values(), key=lambda c: c['card'], reverse=True)
        for c in sorted_cards:
            print(f'{c["card"]} - count: {c["count"]}, wins: {c["wins"]}, win_rate: {c["win_rate"]}')


if __name__ == '__main__':
    options = {
        'test_name': 'base_test',
        'number_of_simulations': '100',
        'sessions': '10',
        'hours': '3',
        'win_rate': 'yes'
    }
    Simulation(**options).start()
