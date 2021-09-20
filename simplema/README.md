# Simplema

This is my Hello World! strategy in Jesse.  

It is an [ema](https://www.investopedia.com/terms/e/ema.asp) trend follower strategy with fixed stop loss and take profit level, uses  [Martingale](https://en.wikipedia.org/wiki/Martingale_(betting_system))-like position sizing system, also utilizes a simple dump & pump filter to avoid sudden price movements.

Simplema is optimized using Jesse's GA algorithm for 2018->2021-06-26 period and picked best dnas for 2021 season.  
I've added optimization log file (ewoHyper2-Binance-BTC-USDT-2h.txt) for recycling.  

You can find sorted dnas files in jessepickerdata/dnafiles.
Default values in hyperoptimization parameters (over!)fits to ETH-USDT 30m, 2021 year.  
You can manually select dnas for additional pairs or fine tune default values manually or use the jesse-picker refinement tool.

## Theory
This is a simple strategy that involves opening long and short positions at ema crosses, as shown in the chart below. To better visualize trends, I use the elliot wave indicator.  

<img src="https://github.com/ysdede/jesse_strategies/blob/master/simplema/media/ETHUSDTPERP_2021-09-18_22-34-11.png?raw=true" width=100% height=100%>

At the first chart trend reverses before hitting target profit level. A simple cross check in def update_position calls self.liquidate

```python
def update_position(self):  
#...
     # Emergency exit! Close position at trend reversal  
     if utils.crossed(self.fast_ema, self.slow_ema, sequential=False):  
         self.liquidate()
 ```


<img src="https://github.com/ysdede/jesse_strategies/blob/master/simplema/media/ETHUSDTPERP_2021-09-18_22-40-49.png?raw=true" width=100% height=100%>

The trend price reaches the profit target in the second example, and the manual take profit in update position works.

```python
def update_position(self):  
    # Take profit when hit!  
    if self.position.pnl_percentage / self.position.leverage > self.target_pnl:  
        self.liquidate()
 ```

## Downsides
In sideways markets, moving averages suffer. To avoid losses, you must filter out tiny movements. Using RSI, ADX, Chandelier Exit, Optimized Trend Tracker or higher time frame trend will help with in detecting of fake movements.

<a href="https://github.com/ysdede/jesse_strategies/blob/master/simplema/media/ETHUSDTPERP_2021-09-18_23-01-49.png?raw=true"><img src="https://github.com/ysdede/jesse_strategies/blob/master/simplema/media/ETHUSDTPERP_2021-09-18_23-01-49.png?raw=true" width=100% height=100%>



## Installation

If you already have Jesse installed, skip this step.
     
Use the package manager pip to install Jesse.

```bash
pip install jesse
```

## Usage
Open the folder as a Jesse project in your favorite IDE or simply run the command line.  
Edit config.py to match your database settings.
```python
    'databases': {
        'postgres_host': '127.0.0.1',
        'postgres_name': 'jesse_db',
        'postgres_port': 5432,
        'postgres_username': 'jesse_user',
        'postgres_password': 'password',
    },
```
Import candles
```console
jesse import-candles "Binance Futures" ETH-USDT 2021-01-01
```
and run backtest
```console
jesse backtest 2021-05-01 2021-09-17
```
output:
```console
 CANDLES              |
----------------------+--------------------------
 period               |   259 days (8.63 months)
 starting-ending date | 2021-01-01 => 2021-09-17


 exchange        | symbol   | timeframe   | strategy   | DNA
-----------------+----------+-------------+------------+-------
 Binance Futures | ETH-USDT | 30m         | SimplEma   |


Executing simulation...  [####################################]  100%
Executed backtest simulation in:  23.39 seconds


 METRICS                         |
---------------------------------+----------------------------------
 Total Closed Trades             |                              442
 Total Net Profit                |           207,179.6906 (2071.8%)
 Starting => Finishing Balance   |             10,000 => 217,179.69
 Total Open Trades               |                                1
 Open PL                         |                        -1,990.13
 Total Paid Fees                 |                        20,570.11
 Max Drawdown                    |                           -26.8%
 Annual Return                   |                         7428.15%
 Expectancy                      |                   468.73 (4.69%)
 Avg Win | Avg Loss              |                3,224.44 | 667.01
 Ratio Avg Win / Avg Loss        |                             4.83
 Percent Profitable              |                              29%
 Longs | Shorts                  |                        50% | 50%
 Avg Holding Time                |  9 hours, 59 minutes, 43 seconds
 Winning Trades Avg Holding Time | 22 hours, 41 minutes, 23 seconds
 Losing Trades Avg Holding Time  |  4 hours, 45 minutes, 48 seconds
 Sharpe Ratio                    |                             3.67
 Calmar Ratio                    |                           277.14
 Sortino Ratio                   |                             8.98
 Winning Streak                  |                                5
 Losing Streak                   |                               17
 Largest Winning Trade           |                        75,320.47
 Largest Losing Trade            |                        -8,684.57
 Total Winning Trades            |                              129
 Total Losing Trades             |                              313
 Market Change                   |                           384.0%

```
## Disclaimer

The simple strategies presented here are solely for **educational purposes**. They are **insufficient for live trading.**

Please remember that the past performance of a strategy is not a guarantee of future results. **USE THEM AT YOUR OWN RISK**.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
