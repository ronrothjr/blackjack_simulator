## Blackjack Simulator

Python console application for running simulations of a blackjack session with specific tests and reporting of stats

#### How It Works

Blackjack Simulator is designed to run an H17 blackjack gaming session with 6 decks for a specified number of hours (80 hands per hour). It uses the basic strategy, counting, and deviations provided publicly by blackjackapprentice.com.

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
# run 10 iterations of the base_test simulation
python main.py --test base_test --iterations 10
```

Output:

```apache
STARTING 100 simulations for the following case:
{'starting_bankroll': 5000, 'starting_risk': 10.0, 'bankroll_threshold': 10000, 'threshold_risk': 1.0, 'hours_to_play': 8, 'number_of_simulations': 100}
FINISHED:
{'starting_bankroll': 5000, 'starting_risk': 10.0, 'bankroll_threshold': 10000, 'threshold_risk': 1.0, 'hours_to_play': 8, 'number_of_simulations': 100}
chance of success: 0.96
average winnings: 74857.94
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
* win_rate: the detailed list of win rates for each play hand to dealer up card matchup

The following command will start 100 simulations and display the individual card stats with win rates:

```apache
python main.py --test base_test --iterations 100  --sessions 50 --hours 5 --win_rates yes
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
