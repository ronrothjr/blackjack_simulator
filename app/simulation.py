import copy, datetime, json, operator, os
from concurrent.futures import ProcessPoolExecutor
from unittest import TextTestResult
from session import Session
from stats import Stats

risk_of_ruin = lambda bankroll, starting_risk, bankroll_threshold, threshold_risk: starting_risk if bankroll < bankroll_threshold else threshold_risk
output = []

class Simulation():

    def __init__(self, test_name=None, number_of_simulations=None, sessions=None, hours=None, win_rate=None, log=None):
        test_name = test_name if test_name else 'base_test'
        self.test_name = test_name
        number_of_simulations = number_of_simulations if number_of_simulations else 10
        sessions = sessions if sessions else 10
        self.get_cases(test_name, number_of_simulations, sessions, hours, win_rate, log)
        self.output = []

    def get_cases(self, test_name, number_of_simulations, sessions, hours, win_rate, log) -> None:
        self.timestamp = datetime.datetime.today().strftime("%Y%m%d%H%M%S%f")
        self.win_rate = win_rate
        self.local_path = os.path.dirname(os.path.realpath(__file__))
        if log:
            path = os.path.join(self.local_path, 'simulations')
            if not os.path.exists(path):
                os.makedirs(path)
            path = os.path.join(self.local_path, 'simulations', test_name)
            if not os.path.exists(path):
                os.makedirs(path)
            path = os.path.join(self.local_path, 'simulations', test_name, self.timestamp)
            if not os.path.exists(path):
                os.makedirs(path)
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
        self.log = log
        for case in self.cases:
            case['test_name'] = test_name
            case['folder'] = os.path.join(self.test_name, self.timestamp)
            if number_of_simulations:
                case['number_of_simulations'] = number_of_simulations
            if sessions:
                case['sessions'] = int(sessions)
            if hours:
                case['hours_per_session'] = int(hours)
            if log:
                case['log'] = True

    def start(self) -> None:
        simulations = []
        for case in self.cases:
            simulation = copy.deepcopy(self.base)
            simulation.update(case)
            simulations.append(simulation)
        path = os.path.join(self.local_path, 'simulations', self.test_name, self.timestamp)
        results_file = os.path.join(path, f'{self.test_name}.{self.timestamp}-results.txt')
        with (open(results_file, 'w+') if simulation['log'] else False) as results:
            if results:
                results.write(f'timestamp: {self.timestamp}\n')
            with ProcessPoolExecutor(max_workers=50) as executor:
                resp = executor.map(Simulation.run_simulation, simulations)
            if self.win_rate:
                self.collate_and_print_stats(resp, results)

    @staticmethod
    def run_simulation(simulation) -> None:
        stats = Stats()
        stats.timestamp = datetime.datetime.today().strftime("%Y%m%d%H%M%S%f")
        local_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(local_path, 'simulations', simulation["folder"])
        details_file = os.path.join(path, f'{simulation["test_name"]}.{stats.timestamp}-details.txt')
        with (open(details_file, 'w+') if simulation['log'] else False) as details:
            print(f'STARTING {simulation["number_of_simulations"]} simulations for the following case:\n{simulation}')
            results = {}
            results['starting_bankroll'] = simulation['starting_bankroll']
            results['wins'] = 0
            results['winnings'] = 0
            for x in range(0, simulation['number_of_simulations']):
                Simulation.run_sessions(simulation, results, stats, details)
            results['chance_of_success'] = results['wins'] / simulation['number_of_simulations']
            results['average_winnings'] = results['winnings'] / simulation['number_of_simulations']
            results['simulation'] = simulation
            output.append(results)
            finished = f'FINISHED:\n{simulation}'
            success = f'chance of success: {results["chance_of_success"]}'
            average = f'average winnings: {results["average_winnings"]}'
            print(finished)
            print(success)
            print(average)
            details.write(f'{finished}\n')
            details.write(f'{success}\n')
            details.write(f'{average}\n')
            stats.results = copy.deepcopy(results)
        return stats

    @staticmethod
    def run_sessions(simulation, results, stats, details):
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
            player = session_stats['Player 1']
            results['sessions'].append(session_stats)
            if details:
                stats_details = copy.deepcopy(dict(vars(player)))
                del stats_details['cards']
                details.write(f'{json.dumps(stats_details)}\n')
        results['wins'] += 1 if bankroll > results['starting_bankroll'] else 0
        results['winnings'] += bankroll - results['starting_bankroll'] if bankroll > results['starting_bankroll'] else 0
        if details:
            details.write(f'bankroll: {bankroll}\n')
            details.write(f'wins: {results["wins"]}\n')
            details.write(f'winnings: {results["winnings"]}\n')

    def collate_and_print_stats(self, resp: list[Stats], results) -> None:
        all_cards = {}
        for stats in resp:
            results.write(f'simulation: {stats.results["simulation"]}\n')
            results.write(f'chance of success: {stats.results["chance_of_success"]}\n')
            results.write(f'average winnings: {stats.results["average_winnings"]}\n')
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
            divisor = all_cards[c]['count'] if all_cards[c]['count'] else 1
            win_rate = all_cards[c]['wins'] / divisor
            all_cards[c]['win_rate'] = float("{:.4}".format(win_rate * 100))
        sorted_cards = sorted(all_cards.values(), key=lambda c: c['card'], reverse=True)
        for c in sorted_cards:
            output = f'{c["card"]} - count: {c["count"]}, wins: {c["wins"]}, win_rate: {c["win_rate"]}'
            results.write(f'{output}\n')


if __name__ == '__main__':
    options = {
        'test_name': 'base_test',
        'number_of_simulations': '100',
        'sessions': '10',
        'hours': '3',
        'win_rate': 'yes',
        'log': 'yes'
    }
    Simulation(**options).start()
