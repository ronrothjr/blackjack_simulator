## Blackjack Simulator

Python console application for running simulations of a blackjack session with specific tests and reporting of stats

The purpose of this simulator is to help determine the optimal bankroll and betting strategy during a new blackjack player's first year, but it can be used to start with any bankroll and the code can be altered to handle any scenario required.

Each simulation will result in a bankroll increase or decrease after the specified number of sessions are completed. A bankroll increase is marked as a success and the increase is included in the average winnings. Understand that these numbers are based on perfect game play, counting, deviations, betting strategies, and NOT being "backed off" by the casino. If you find that you can't get in an 8-hour session, then you should use the `--hours` flag to alter the session time.

Sample simulation output:
```apache
chance of success: 0.96
average winnings: 74857.94
```

#### How It Works

Blackjack Simulator is designed to run an H17 blackjack gaming session with 6 decks for a specified number of hours (80 hands per hour). It uses the basic strategy, counting, and deviations provided publicly by https://www.blackjackapprenticeship.com/.

Risk of ruin is part of a betting strategy where the size of your bet in relation to your bankroll determines your risk of losing your money.

| Risk of Ruin | Bet Units |
|--------------|-----------|
| 40%          | 200       |
| 20%          | 400       |
| 10%          | 500       |
| 1%           | 1000      |

Tests are defined in `app/cases.json`. You edit them, add your own, and run them like so:

```apache
cd app
# run 1000 iterations of the base_test simulation
python main.py --test base_test --iterations 1000
```

Output:

```apache
STARTING 1000 simulations for the following case:
{'starting_bankroll': 5000, 'starting_risk': 10.0, 'bankroll_threshold': 10000, 'threshold_risk': 1.0, 'hours_per_session': 8, 'test_name': 'base_test', 'folder': 'base_test\\20220203081954847207', 'number_of_simulations': 1000, 'sessions': 12, 'log': True}
FINISHED:
simulation: {'starting_bankroll': 5000, 'starting_risk': 10.0, 'bankroll_threshold': 10000, 'threshold_risk': 1.0, 'hours_per_session': 8, 'test_name': 'base_test', 'folder': 'base_test\\20220203081954847207', 'number_of_simulations': 1000, 'sessions': 12, 'log': True}
chance of success: 0.811
average winnings: 6513.232
```

Simulation options are as follows:

* test: the test cases to run - defaulted to base_test
  * starting bankroll: $5,000
  * starting risk of ruin: 10% (a bet unit of 1/500th of the bankroll)
  * threshold bankroll: $10,000
  * threshold risk: 1% (after the threshold bankroll is reached, the bet unit will go down to 1/1000th of the bankroll
* iterations: the number of simulations to run - defaulted to 10
* sessions: the number of sessions incliuded in each simulation - defaulted to 10
* hours: the number of hours (80 hands per hour) to include in each session - defaulted by the test (usually 8)
* win_rate: the detailed list of win rates for each player hand to dealer up card matchup
* log: record the details of each simulation in the /app/simulations folder

The following command will start 100 simulations and display the individual card stats with win rates:

```apache
python main.py --test base_test --iterations 100  --sessions 50 --hours 5 --win_rates yes --log yes
```

Sample output:

```apache
8,10-9 - count: 6747, wins: 2297, win_rate: 34.04
8,10-8 - count: 6493, wins: 2407, win_rate: 37.07
8,10-7 - count: 6664, wins: 4175, win_rate: 62.65
8,10-6 - count: 6694, wins: 3950, win_rate: 59.01
8,10-5 - count: 6595, wins: 3602, win_rate: 54.62
8,10-4 - count: 6585, wins: 3497, win_rate: 53.11
8,10-3 - count: 6636, wins: 3301, win_rate: 49.74
8,10-2 - count: 6686, wins: 3307, win_rate: 49.46
8,10-10 - count: 27791, wins: 8970, win_rate: 32.28
8,10-1 - count: 7127, wins: 1871, win_rate: 26.25
```

The two numbers before the dash are the player cards and the number after the dash is the dealer's up card.
