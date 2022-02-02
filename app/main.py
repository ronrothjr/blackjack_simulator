import argparse
from simulation import Simulation

def get_args():
    parser = argparse.ArgumentParser(
        description="A Blackjack Simulation that executes the specified tests"
        )
    parser.add_argument('--test', action='store', required=False,
                        help='The name of the test to run')
    parser.add_argument('--iterations', action='store', required=False, default=None,
                        help='The number of simulations to run')
    parser.add_argument('--sessions', action='store', required=False, default=None,
                        help='The number of sessions per iteration')
    parser.add_argument('--hours', action='store', required=False, default=None,
                        help='The number of hours per session')
    parser.add_argument('--win_rate', action='store', required=False, default=None,
                        help='Show win rates for each hand against the dealer up card')
    return parser.parse_args()

def main():
    args = get_args()
    Simulation(test_name=args.test, number_of_simulations=args.iterations, sessions=args.sessions, hours=args.hours, win_rate=args.win_rate).start()

if __name__ == '__main__':
    main()
