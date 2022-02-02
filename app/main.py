import argparse
from simulation import Simulation

def get_args():
    parser = argparse.ArgumentParser(
        description="A Blackjack Simulation that executes the specified tests"
        )
    parser.add_argument('--test', action='store', required=True,
                        help='The name of the test to run')
    parser.add_argument('--iterations', action='store', required=False, default=None,
                        help='The number of simulations to run')
    return parser.parse_args()

def main():
    args = get_args()
    Simulation(test_name=args.test, number_of_simulations=args.iterations).start()

if __name__ == '__main__':
    main()
