# ewoexit2 re-trained

Ema cross strategy better trained between 2021-02-01 2021-08-25.

## Theory
A slightly better ema cross strategy determines trend direction using a higher timeframe ema. To capture choppy zones, it utilizes an RSI filter. The ema values for trade entry and exits are distinct.  

It was optimized using the Jesse genetic algorithm, and dna - pair matching was performed to fit with the help of additional tools.

## Installation

If you already have Jesse installed, skip this step.
     
Use the package manager pip to install Jesse.

```bash
pip install jesse
```

## Usage
Open the folder as a Jesse project in your favorite IDE or simply run the command line.  

### Importing candles  
You can use [import-routes.py](https://github.com/ysdede/import-routes) to retrieve only the symbols in your routes file. I've already placed a copy in the strategy folder.

```console
$ python import-routes.py 2021-01-01
```
and run backtest
```console
jesse backtest 2021-09-01 2021-09-25
```
# jesse-picker pick
### Picking best dnas from log file

We already have a ~4500 lines optimization log file located at `storage/genetics/ewoexit-Binance Futures-ETH-USDT-15m-2021-02-01-2021-08-25.txt`  

Running `jesse-picker` with `pick` parameter selects and sorts dna strings with given options.  
`jesse-picker pick log_file_name sort_criteria n1 n2`  
#### Sort criterias:  
pnl1: Sort by PNL1, optimization phase pnl  
pnl2: Sort by PNL2, test (short) phase pnl  
wr1: Sort by winrate1, optimization phase winrate  
wr2: Sort by winrate2, test (short) phase winrate  


#### Magic numbers:  
n1, n2: pick best performing n dnas from lists. Enter huge numbers to get all dnas.  

eg:  


```console
G:\ewoexit2>jesse-picker pick "storage/genetics/ewoexit-Binance Futures-ETH-USDT-15m-2021-02-01-2021-08-25.txt" pnl2 100 500
```  

Output:
```console 
Strategy name: ewoexitRestore Strat Class: <class 'strategies.ewoexitRestore.ewoexitRestore'>
Total 403 unique dnas found.
Picked dnas count: 403
Validated dna file. 403/403
```
This will create a python file containing selected dnas at jessepickerdata\dnafiles\\**strategyname**+dnas.py  
eg: 'jessepickerdata\dnafiles\ewoexitRestorednas.py'  

#### Array elements explained:  
[dna_string, win_rate1, total_trades_1, pnl_1, win_rate_2, total_trades_2, pnl_2, dict {optimization parameters as name: value pairs}],  

```python
dnas = [
['*qDIIT)@q', 35, 115, 437.73, 36, 22, 4.13, {'stop': 12, 'treshold': 47, 'ewoshort': 13, 'ewolong': 37, 'chop_rsi': 14, 'chop_band_width': 84, 'trend_ema_len': 5, 'exit_ema_fast': 4, 'exit_ema_slow': 233}],
['(UDD0p)vq', 29, 133, 394.14, 17, 29, 10.99, {'stop': 10, 'treshold': 33, 'ewoshort': 13, 'ewolong': 34, 'chop_rsi': 5, 'chop_band_width': 137, 'trend_ema_len': 5, 'exit_ema_fast': 10, 'exit_ema_slow': 233}],
['(qDIIT)5q', 31, 134, 380.21, 33, 24, 2.96, {'stop': 10, 'treshold': 47, 'ewoshort': 13, 'ewolong': 37, 'chop_rsi': 14, 'chop_band_width': 84, 'trend_ema_len': 5, 'exit_ema_fast': 3, 'exit_ema_slow': 233}],
['(UDDIN)vq', 30, 120, 372.69, 35, 20, 29.32, {'stop': 10, 'treshold': 33, 'ewoshort': 13, 'ewolong': 34, 'chop_rsi': 14, 'chop_band_width': 73, 'trend_ema_len': 5, 'exit_ema_fast': 10, 'exit_ema_slow': 233}],

# .
# .
['PU4aB^[6v', 34, 63, 166.92, 72, 11, 27.0, {'stop': 45, 'treshold': 33, 'ewoshort': 7, 'ewolong': 49, 'chop_rsi': 11, 'chop_band_width': 103, 'trend_ema_len': 106, 'exit_ema_fast': 3, 'exit_ema_slow': 247}],
['(<Xt;@vYv', 24, 79, 161.85, 38, 13, 28.08, {'stop': 10, 'treshold': 20, 'ewoshort': 19, 'ewolong': 58, 'chop_rsi': 9, 'chop_band_width': 46, 'trend_ema_len': 161, 'exit_ema_fast': 7, 'exit_ema_slow': 247}],
['(nX[;@vYv', 20, 97, 152.71, 43, 16, 32.89, {'stop': 10, 'treshold': 45, 'ewoshort': 19, 'ewolong': 46, 'chop_rsi': 9, 'chop_band_width': 46, 'trend_ema_len': 161, 'exit_ema_fast': 7, 'exit_ema_slow': 247}],
['r42OV8u?a', 46, 89, 103.59, 57, 21, 9.33, {'stop': 76, 'treshold': 16, 'ewoshort': 6, 'ewolong': 40, 'chop_rsi': 18, 'chop_band_width': 31, 'trend_ema_len': 159, 'exit_ema_fast': 4, 'exit_ema_slow': 186}],
]
```


#  jesse-picker refine
We've created a general-purpose dna file that we can use to find the best dnas fit for a given pair.  

Replace the dna strings in routes.py with anchor. (don't search for table flipping emoji online, it will print it out with error a message at first run.  

routes.py example:
```python
routes = [
    ('FTX Futures', 'ETH-USD', '15m', 'ewoexitRestore', '(╯°□°)╯︵ ┻━┻'),
]
extra_candles = [
    ('FTX Futures', 'ETH-USD', '1h'),
]
```
run
```console
G:\ewoexit2>jesse-picker refine jessepickerdata/dnafiles/ewoexitRestorednas.py 2021-06-01 2021-09-03
```

```console
35/403
Pair       TF    Dna         Total  Total Net    Max.     Annual     Win      Sharpe   Calmar  Winning  Losing   Largest      Largest      Winning    Losing     Market
                             Trades Profit %     DD %     Return %   Rate %   Ratio    Ratio   Streak   Streak   Win. Trade   Los. Trade   Trades     Trades     Change %
ETH-USD    15m   AQTB<3v2v   56     38.83        -6.0     178        45       3.08     29.7    5        6        1138         -234         25         31         8.78
ETH-USD    15m   A`TB<3v2v   56     38.83        -6.0     178        45       3.08     29.7    5        6        1138         -234         25         31         8.78
ETH-USD    15m   fDTG<3v2v   50     43.5         -7.63    209        50       3.47     27.35   5        5        1126         -283         25         25         8.78
ETH-USD    15m   YUT@;>t6v   52     39.97        -7.12    185        48       3.12     26.05   5        5        1138         -370         25         27         8.78
ETH-USD    15m   YDTB;3q2v   53     38.36        -6.8     175        45       3.03     25.77   5        6        1120         -366         24         29         8.78
ETH-USD    15m   pqGI(Ca@v   47     38.13        -6.83    174        51       2.98     25.48   5        6        1090         -270         24         23         8.78
ETH-USD    15m   ?UTD<<vvv   47     40.0         -7.38    186        49       3.1      25.16   8        7        1147         -222         23         24         8.78
ETH-USD    15m   =UTD<<vvv   48     38.29        -7.18    175        48       2.99     24.36   8        7        1153         -212         23         25         8.78
ETH-USD    15m   VbT?<;vGv   49     38.39        -7.28    176        49       3.0      24.13   5        5        1114         -353         24         25         8.78
ETH-USD    15m   rqTI<Tv0v   45     41.96        -8.79    198        49       3.46     22.57   5        7        1108         -283         22         23         8.78
ETH-USD    15m   VbT?<;v,v   56     34.44        -6.78    152        45       2.79     22.39   4        6        990          -342         25         31         8.78
ETH-USD    15m   1bT?<;vuv   57     35.82        -7.46    160        42       2.83     21.42   5        8        1141         -132         24         33         8.78
ETH-USD    15m   pqGIFCi@v   47     39.08        -8.52    180        51       3.09     21.12   5        6        1073         -275         24         23         8.78
ETH-USD    15m   YDYB;3r2v   50     35.31        -7.5     157        50       3.02     20.92   5        5        722          -270         25         25         8.78
ETH-USD    15m   YDYB;3l2v   51     35.07        -7.5     155        49       3.0      20.74   5        6        722          -270         25         26         8.78
ETH-USD    15m   mqTW;Cv@r   48     32.84        -7.07    143        46       2.8      20.16   5        5        1067         -283         22         26         8.78
ETH-USD    15m   f^TB<3v2v   52     37.55        -8.69    170        46       2.95     19.6    5        6        1120         -447         24         28         8.78

```

It will test all dnas given in dna file with routes.
It will create a new dna file sorted by Calmar at `jessepickerdata/dnafiles/ETH-USD 2021-09-01 2021-09-25.py`  
You can use this as input dna file in the future refinements.

I chose ```=bdOSb@l3``` because I made a bunch of refinements in past with a lot of symbols and find out that they have this dna in common.  
It's not number one in performance lists but appears in the top of most pair's backtests. And it performs well on random period tests.  


```console
G:\ewoexit2>jesse backtest 2021-06-01 2021-09-25
```
```console
 period               |   116 days (3.87 months)
 starting-ending date | 2021-06-01 => 2021-09-25

 exchange    | symbol    | timeframe   | strategy       | DNA
-------------+-----------+-------------+----------------+-----------
 FTX Futures | ADA-USD   | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | AAVE-USD  | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | FIL-USD   | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | DOT-USD   | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | IOTA-USD  | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | LINK-USD  | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | BCH-USD   | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | 1INCH-USD | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | UNI-USD   | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | TRX-USD   | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | ETH-USD   | 15m         | ewoexitRestore | =bdOSb@l3
 FTX Futures | NEO-USD   | 15m         | ewoexitRestore | =bdOSb@l3

 METRICS                         |
---------------------------------+---------------------------------
 Total Closed Trades             |                             596
 Total Net Profit                |           14,778.2788 (147.78%)
 Starting => Finishing Balance   |             10,000 => 24,778.28
 Total Open Trades               |                               1
 Open PL                         |                          -47.74
 Total Paid Fees                 |                        1,234.45
 Max Drawdown                    |                          -3.35%
 Annual Return                   |                        1595.77%
 Expectancy                      |                    24.8 (0.25%)
 Avg Win | Avg Loss              |                   93.91 | 32.83
 Ratio Avg Win / Avg Loss        |                            2.86
 Percent Profitable              |                             45%
 Longs | Shorts                  |                       47% | 53%
 Avg Holding Time                | 15 hours, 18 minutes, 5 seconds
 Winning Trades Avg Holding Time |   1 day, 56 minutes, 24 seconds
 Losing Trades Avg Holding Time  | 7 hours, 15 minutes, 52 seconds
 Sharpe Ratio                    |                            5.88
 Calmar Ratio                    |                          476.15
 Sortino Ratio                   |                           22.34
 Winning Streak                  |                              10
 Losing Streak                   |                              16
 Largest Winning Trade           |                        1,017.61
 Largest Losing Trade            |                          -78.65
 Total Winning Trades            |                             271
 Total Losing Trades             |                             325
 Market Change                   |                          -5.14%

```

# jesse-picker testpairs

Backtests all pairs given in [pairs.py](https://github.com/ysdede/jesse-picker/blob/master/jessepicker/pairs.py) with current dna.  
Replace symbol field with keyword 'ANCHOR!'

Routes file template for mass backtest:
```python
routes = [
    ('FTX Futures', 'ANCHOR!', '15m', 'ewoexit2', '=bdOSb@l3'),
]
extra_candles = [
    ('FTX Futures', 'ANCHOR!', '1h'),
]
```
run

```console
jesse-picker testpairs 2021-06-01 2021-09-25
```

It will print out backtest results per symbol sorted by performance and create a report file:  
`jessepickerdata/results/Pairs-FTX Futures-15m--2021-06-01--2021-09-25--20210927 024722.csv`  
Naming convention: Pairs-{exchange}-{timeframe}--{startDate}--{finishDate}--{testTime}.csv  

Console output:
```console
18/156  2021-06-01   2021-09-25
Pair       TF   Total  Total Net  Max.     Annual     Win      Sharpe   Calmar  Winning  Losing   Largest      Largest      Winning  Losing     Market
                Trades Profit %   DD %     Return %   Rate %   Ratio    Ratio   Streak   Streak   Win. Trade   Los. Trade   Trades   Trades     Change %
ADA-USD    15m  44     49.63      -3.37    252        66       4.75     74.55   12       4        1285         -229         29       15         31.89
DOT-USD    15m  54     51.61      -6.98    266        44       3.26     38.18   4        5        1213         -238         24       30         32.94
LINK-USD   15m  45     42.8       -7.25    204        53       4.06     28.11   3        7        870          -192         24       21         -26.84
ETH-USD    15m  44     24.98      -5.32    100        45       3.07     18.9    3        7        691          -190         20       24         8.78
AVAX-USD   15m  49     26.5       -7.96    108        41       2.11     13.6    3        4        1048         -194         20       29         300.83
BTC-USD    15m  40     14.11      -3.87    51         50       2.33     13.16   4        3        491          -165         20       20         15.3
FTM-USD    15m  51     19.77      -9.32    76         39       1.68     8.1     4        6        1152         -183         20       31         277.26
XRP-USD    15m  45     13.35      -8.21    48         38       1.71     5.82    3        6        1082         -184         17       28         -8.62
SOL-USD    15m  51     13.64      -11.7    49         37       1.35     4.19    3        8        887          -185         19       32         327.25
MATIC-USD  15m  41     8.84       -11.1    30         39       1.14     2.72    3        6        923          -178         16       25         -39.38
ATOM-USD   15m  56     7.05       -16.38   24         38       0.71     1.44    3        5        956          -180         21       35         205.99
XTZ-USD    15m  67     3.35       -19.77   11         33       0.46     0.55    2        14       935          -176         22       45         95.31
FTT-USD    15m  0      0          0        0          0        0        0       0        0        0            0            0        0          0
AXS-USD    15m  0      0          0        0          0        0        0       0        0        0            0            0        0          0
DOGE-USD   15m  0      0          0        0          0        0        0       0        0        0            0            0        0          0
SRM-USD    15m  49     -6.31      -22.15   -18        22       -0.48    -0.83   4        11       1089         -176         11       38         65.42
ALGO-USD   15m  47     -7.15      -18.09   -21        30       -0.68    -1.14   3        6        694          -151         14       33         92.32
LUNA-USD   15m  58     -19.59     -23.85   -49        24       -2.01    -2.07   3        19       1057         -156         14       44         519.87
```
  
I've picked some of them and created a routes file:  
```python
routes = [
    ('Binance Futures', 'ADA-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'AAVE-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'FIL-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'DOT-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'IOTA-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'LINK-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'BCH-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', '1INCH-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'UNI-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'TRX-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    # .
    ('Binance Futures', 'ETH-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
    ('Binance Futures', 'NEO-USDT', '15m', 'ewoexitRestore', '=bdOSb@l3'),
]
extra_candles = [
    ('Binance Futures', 'ADA-USDT', '1h'),
    ('Binance Futures', 'AAVE-USDT', '1h'),
    ('Binance Futures', 'FIL-USDT', '1h'),
    ('Binance Futures', 'DOT-USDT', '1h'),
    ('Binance Futures', 'IOTA-USDT', '1h'),
    ('Binance Futures', 'LINK-USDT', '1h'),
    ('Binance Futures', 'BCH-USDT', '1h'),
    ('Binance Futures', '1INCH-USDT', '1h'),
    ('Binance Futures', 'UNI-USDT', '1h'),
    ('Binance Futures', 'TRX-USDT', '1h'),
    ('Binance Futures', 'ETH-USDT', '1h'),
    ('Binance Futures', 'NEO-USDT', '1h'),
]
```
In addition, I realized that FTX does not have sufficient candle data for some symbols, so I switched to Binance Futures. The strategy will be tested on Binance after being trained with FTX data. It'll be fun.

```console
----------------------+--------------------------
 period               |   224 days (7.47 months)
 starting-ending date | 2021-02-15 => 2021-09-27


 exchange        | symbol     | timeframe   | strategy       | DNA
-----------------+------------+-------------+----------------+-----------
 Binance Futures | ADA-USDT   | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | AAVE-USDT  | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | FIL-USDT   | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | DOT-USDT   | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | IOTA-USDT  | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | LINK-USDT  | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | BCH-USDT   | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | 1INCH-USDT | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | UNI-USDT   | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | TRX-USDT   | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | ETH-USDT   | 15m         | ewoexitRestore | =bdOSb@l3
 Binance Futures | NEO-USDT   | 15m         | ewoexitRestore | =bdOSb@l3


Executing simulation...  [####################################]  100%
Executed backtest simulation in:  270.46 seconds


 METRICS                         |
---------------------------------+----------------------------------
 Total Closed Trades             |                             1122
 Total Net Profit                |            98,024.3456 (980.24%)
 Starting => Finishing Balance   |             10,000 => 108,024.35
 Total Open Trades               |                                6
 Open PL                         |                          2,715.6
 Total Paid Fees                 |                         9,017.45
 Max Drawdown                    |                          -18.53%
 Annual Return                   |                          4649.0%
 Expectancy                      |                    87.37 (0.87%)
 Avg Win | Avg Loss              |                  396.51 | 126.66
 Ratio Avg Win / Avg Loss        |                             3.13
 Percent Profitable              |                              41%
 Longs | Shorts                  |                        46% | 54%
 Avg Holding Time                | 13 hours, 50 minutes, 12 seconds
 Winning Trades Avg Holding Time |    1 day, 34 minutes, 24 seconds
 Losing Trades Avg Holding Time  |  6 hours, 24 minutes, 13 seconds
 Sharpe Ratio                    |                             4.58
 Calmar Ratio                    |                           250.91
 Sortino Ratio                   |                            13.85
 Winning Streak                  |                               10
 Losing Streak                   |                               17
 Largest Winning Trade           |                         6,628.67
 Largest Losing Trade            |                          -678.52
 Total Winning Trades            |                              459
 Total Losing Trades             |                              663
 Market Change                   |                           13.67%
```
# Random Backtest
Perform 50 rounds of random backtests for a 14-day period between 2021-02-15 and 2021-09-27.
I am aware that the random sample duration is as short as 14 days, yet we trade 12 pairs in parallel and have 80 trades every sample. A short-term stress test can assist us understand the performance of the strategy and parameters. By the way, don't be deceived by samples that has very high sharpe ratio.

```console
jesse-picker random 2021-02-15 2021-09-27 50 14
```

```console
50/50   Remaining Time: 00:00:00
Pair       TF    Start Date   End Date     Total  Total Net    Max.     Annual     Win      Sharpe   Calmar       Winning  Losing   Largest      Largest      Winning    Losing     Market
                                           Trades Profit %     DD %     Return %   Rate %   Ratio    Ratio        Streak   Streak   Win. Trade   Los. Trade   Trades     Trades     Change %
ADA-USDT   15m   2021-06-12   2021-06-26   73     82.11        -3.87    216049410  63       9.12     55816700.84  10       11       649          -103         46         27         -23.58
ADA-USDT   15m   2021-06-13   2021-06-27   73     80.0         -3.87    162875149  63       8.92     42079047.78  10       11       649          -103         46         27         -22.52
ADA-USDT   15m   2021-06-10   2021-06-24   72     75.82        -3.87    91896586   62       8.61     23731410.93  11       11       684          -80          45         27         -27.79
ADA-USDT   15m   2021-06-14   2021-06-28   71     67.83        -3.47    29632681   68       7.93     8532991.15   11       7        600          -103         48         23         -23.9
ADA-USDT   15m   2021-06-20   2021-07-04   74     58.62        -6.27    7510169    54       7.14     1198076.17   10       11       610          -98          40         34         -8.03
ADA-USDT   15m   2021-08-25   2021-09-08   90     49.14        -5.28    1675994    39       8.74     317439.61    7        15       1053         -77          35         55         4.33
ADA-USDT   15m   2021-06-05   2021-06-19   87     43.18        -5.59    620470     55       9.44     110925.37    12       11       645          -80          48         39         -18.76
ADA-USDT   15m   2021-05-18   2021-06-01   52     40.02        -5.71    360672     42       6.13     63143.86     9        10       662          -77          22         30         -28.25
ADA-USDT   15m   2021-08-30   2021-09-13   90     38.44        -4.51    273449     30       7.55     60632.38     7        15       1027         -90          27         63         9.04
ADA-USDT   15m   2021-05-09   2021-05-23   57     38.07        -6.11    256222     40       5.97     41963.87     6        10       745          -87          23         34         -46.07
ADA-USDT   15m   2021-05-11   2021-05-25   48     36.16        -6.1     182666     40       5.79     29950.37     6        10       734          -86          19         29         -36.37
ADA-USDT   15m   2021-05-16   2021-05-30   47     35.23        -6.11    154491     43       5.8      25277.87     6        10       720          -84          20         27         -43.3
ADA-USDT   15m   2021-07-23   2021-08-06   84     29.45        -2.85    53340      50       10.87    18716.32     10       8        550          -77          42         42         34.4
ADA-USDT   15m   2021-08-03   2021-08-17   80     26.93        -2.17    33014      57       11.03    15232.85     7        5        480          -72          46         34         31.26
ADA-USDT   15m   2021-06-04   2021-06-18   92     31.79        -5.6     82518      55       7.9      14744.73     10       11       657          -81          51         41         -18.34
ADA-USDT   15m   2021-05-26   2021-06-09   70     31.75        -6.62    81980      59       6.98     12391.06     9        6        490          -72          41         29         -5.07
ADA-USDT   15m   2021-08-04   2021-08-18   80     25.71        -2.17    26075      52       10.31    12042.34     7        5        485          -73          42         38         26.15
ADA-USDT   15m   2021-05-30   2021-06-13   74     29.88        -6.62    57834      55       6.57     8737.7       9        11       488          -82          41         33         -1.74
ADA-USDT   15m   2021-05-30   2021-06-13   74     29.88        -6.62    57834      55       6.57     8737.7       9        11       488          -82          41         33         -1.74
ADA-USDT   15m   2021-05-15   2021-05-29   47     27.97        -6.1     40297      36       4.85     6606.41      6        10       713          -83          17         30         -43.5
ADA-USDT   15m   2021-08-23   2021-09-06   91     26.53        -5.28    30563      40       9.58     5783.94      6        15       1073         -72          36         55         20.59
ADA-USDT   15m   2021-07-19   2021-08-02   72     22.88        -2.73    14931      47       9.4      5465.99      10       7        542          -73          34         38         27.45
ADA-USDT   15m   2021-05-27   2021-06-10   79     25.22        -6.61    23711      52       5.6      3586.1       9        10       493          -82          41         38         -11.02
ADA-USDT   15m   2021-09-08   2021-09-22   61     20.59        -4.18    9423       46       5.08     2252.74      8        7        296          -72          28         33         -18.35
ADA-USDT   15m   2021-05-17   2021-05-31   40     22.64        -6.63    14234      32       4.11     2146.96      4        12       655          -76          13         27         -39.67
ADA-USDT   15m   2021-07-21   2021-08-04   80     18.45        -2.86    6053       45       7.31     2114.43      10       8        538          -76          36         44         43.22
ADA-USDT   15m   2021-08-22   2021-09-05   95     21.14        -5.28    10537      39       7.88     1994.59      6        15       1070         -72          37         58         16.76
ADA-USDT   15m   2021-09-11   2021-09-25   59     17.82        -4.72    5308       44       4.42     1125.67      8        7        303          -74          26         33         -10.9
ADA-USDT   15m   2021-08-21   2021-09-04   92     18.03        -5.29    5547       40       6.81     1049.17      6        15       1066         -66          37         55         10.96
ADA-USDT   15m   2021-05-23   2021-06-06   60     19.1         -6.61    6929       60       5.59     1047.83      10       6        493          -70          36         24         14.84
ADA-USDT   15m   2021-07-01   2021-07-15   69     13.7         -3.48    2175       51       8.06     625.71       7        9        329          -67          35         34         -9.97
ADA-USDT   15m   2021-07-02   2021-07-16   62     12.54        -3.48    1674       47       7.51     480.61       6        9        322          -65          29         33         -8.08
ADA-USDT   15m   2021-07-10   2021-07-24   61     10.37        -2.22    1004       52       6.77     452.37       12       6        239          -68          32         29         -11.21
ADA-USDT   15m   2021-03-18   2021-04-01   70     13.53        -6.5     2095       37       4.36     322.16       6        8        356          -69          26         44         14.38
ADA-USDT   15m   2021-07-07   2021-07-21   49     9.0          -3.02    714        43       6.23     236.28       6        5        238          -63          21         28         -29.04
ADA-USDT   15m   2021-04-15   2021-04-29   63     9.88         -6.04    890        38       4.31     147.3        6        17       288          -68          24         39         0.92
ADA-USDT   15m   2021-04-22   2021-05-06   76     9.88         -6.19    889        41       4.37     143.69       6        14       299          -70          31         45         25.36
ADA-USDT   15m   2021-07-03   2021-07-17   62     6.29         -3.55    341        45       3.97     96.03        6        9        234          -62          28         34         -14.42
ADA-USDT   15m   2021-04-29   2021-05-13   74     7.04         -6.34    423        32       2.76     66.78        5        14       309          -62          24         50         6.07
ADA-USDT   15m   2021-08-17   2021-08-31   74     5.14         -5.25    239        42       2.54     45.43        6        7        256          -67          31         43         -2.11

```

Random test will create a report file at: `jessepickerdata/results/Binance Futures-15m--20210927 182519--20210927 182519.csv`  
This is the average of 50 tests:  
```
Total   Total   Max.   Annual      Win     Sharpe  Calmar   Winning  Losing   Largest   Largest  Num .of  Num. of  Market
Trades  Profit  DD %   Profit      Rate %  Ratio   Ratio    Strike   Strike   Winning   Losing   Wins     Loses    Change
71.28   23.48   -5.27  10241168    43.78   5.30    2642679  7.00     10.24    500.98    -74.32   31.30    39.98    -0.68
```

# Insert Chart-image here

https://github.com/ysdede/ewoexit2rt/blob/master/media/chart.png?raw=true

Chart: Results sorted by date

As seen on the chart strategy performs too bad at March 2021, we can isolate routes and perform single backtests to find out what's happening.



## Downsides
It, like ewoexit2708, requires an improved stop loss and take profit calculation mechanism.
It is optimized for a limited duration of time. It must be re-optimized and refined on a regular basis to match market conditions.
Also see [bias_and_variance](https://machinelearningcompass.com/model_optimization/bias_and_variance/)


## Disclaimer

The simple strategies presented here are solely for **educational purposes**. They are **insufficient for live trading.**

Please remember that the past performance of a strategy is not a guarantee of future results. **USE THEM AT YOUR OWN RISK**.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)