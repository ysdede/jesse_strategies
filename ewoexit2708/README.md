# ewoexit2708

Ema cross strategy trained @27/08/2021

## Theory
A slightly better ema cross strategy determines trend direction using a higher timeframe ema. To capture choppy zones, it utilizes an RSI filter. The ema values for trade entry and exits are distinct.  

It was optimized using the Jesse genetic algorithm, and dna - pair matching was performed to (over)fit with the help of additional tools.

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
Output:
```console
 CANDLES              |
----------------------+--------------------------
 period               |                  24 days
 starting-ending date | 2021-09-01 => 2021-09-25


 exchange    | symbol      | timeframe   | strategy    | DNA
-------------+-------------+-------------+-------------+-----------
 FTX Futures | OXY-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | HOLY-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | HBAR-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | HUM-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BAL-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | UNISWAP-USD | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ZEC-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | MEDIA-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | FIDA-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | IOTA-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ROOK-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | STORJ-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | STEP-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | THETA-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | EGLD-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BAT-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | SECO-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ALGO-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | TRX-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ETH-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | TOMO-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BAO-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ORBS-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | SHIT-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | EXCH-USD    | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ASD-USD     | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | MVDA10-USD  | 15m         | ewoexit2708 | 86lZ6^AX3

Executing simulation...  [####################################]  100%

 METRICS                         |
---------------------------------+---------------------------------
 Total Closed Trades             |                             298
 Total Net Profit                |              8,821.346 (88.21%)
 Starting => Finishing Balance   |             10,000 => 18,821.35
 Total Open Trades               |                               4
 Open PL                         |                          232.12
 Total Paid Fees                 |                          466.85
 Max Drawdown                    |                          -6.73%
 Annual Return                   |                     1022957.16%
 Expectancy                      |                     29.6 (0.3%)
 Avg Win | Avg Loss              |                   94.17 | 22.45
 Ratio Avg Win / Avg Loss        |                             4.2
 Percent Profitable              |                             45%
 Longs | Shorts                  |                       47% | 53%
 Avg Holding Time                | 15 hours, 6 minutes, 54 seconds
 Winning Trades Avg Holding Time |      1 day, 3 hours, 16 minutes
 Losing Trades Avg Holding Time  | 5 hours, 18 minutes, 28 seconds
 Sharpe Ratio                    |                           10.51
 Calmar Ratio                    |                       151992.21
 Sortino Ratio                   |                           38.12
 Winning Streak                  |                              17
 Losing Streak                   |                              25
 Largest Winning Trade           |                          496.79
 Largest Losing Trade            |                          -45.28
 Total Winning Trades            |                             133
 Total Losing Trades             |                             165
 Market Change                   |                          -1.23%
```


```console
$ jesse backtest 2021-02-01 2021-05-25
```
Output:
```console
----------------------+--------------------------
 period               |   113 days (3.77 months)
 starting-ending date | 2021-02-01 => 2021-05-25


 exchange    | symbol    | timeframe   | strategy    | DNA
-------------+-----------+-------------+-------------+-----------
 FTX Futures | ETC-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | FIL-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ETH-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | DOT-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | XTZ-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BNB-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | NEO-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | SOL-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | LINK-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | XLM-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | MATIC-USD | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | TRX-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BTC-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | AAVE-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ALGO-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ADA-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ATOM-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | XRP-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | LTC-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BCH-USD   | 15m         | ewoexit2708 | 86lZ6^AX3

Executing simulation...  [####################################]  100%

 METRICS                         |
---------------------------------+----------------------------------
 Total Closed Trades             |                             1448
 Total Net Profit                |             29,819.387 (298.19%)
 Starting => Finishing Balance   |              10,000 => 39,819.39
 Total Open Trades               |                                0
 Open PL                         |                                0
 Total Paid Fees                 |                          3,676.0
 Max Drawdown                    |                          -18.33%
 Annual Return                   |                         8243.64%
 Expectancy                      |                    20.59 (0.21%)
 Avg Win | Avg Loss              |                   141.84 | 36.94
 Ratio Avg Win / Avg Loss        |                             3.84
 Percent Profitable              |                              32%
 Longs | Shorts                  |                        55% | 45%
 Avg Holding Time                |             10 hours, 32 seconds
 Winning Trades Avg Holding Time | 21 hours, 38 minutes, 26 seconds
 Losing Trades Avg Holding Time  |  4 hours, 29 minutes, 21 seconds
 Sharpe Ratio                    |                              6.1
 Calmar Ratio                    |                           449.72
 Sortino Ratio                   |                             13.6
 Winning Streak                  |                               13
 Losing Streak                   |                               25
 Largest Winning Trade           |                         4,691.82
 Largest Losing Trade            |                          -113.96
 Total Winning Trades            |                              466
 Total Losing Trades             |                              982
 Market Change                   |                          408.07%
```
  

`$jesse backtest 2021-02-01 2021-09-25`  

Output:

```console
 CANDLES              |
----------------------+--------------------------
 period               |   236 days (7.87 months)
 starting-ending date | 2021-02-01 => 2021-09-25


 exchange    | symbol    | timeframe   | strategy    | DNA
-------------+-----------+-------------+-------------+-----------
 FTX Futures | ETC-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | FIL-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ETH-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | DOT-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | XTZ-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BNB-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | NEO-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | SOL-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | LINK-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | XLM-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | MATIC-USD | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | TRX-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BTC-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | AAVE-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ALGO-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ADA-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | ATOM-USD  | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | XRP-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | LTC-USD   | 15m         | ewoexit2708 | 86lZ6^AX3
 FTX Futures | BCH-USD   | 15m         | ewoexit2708 | 86lZ6^AX3

Executing simulation...  [####################################]  100%

 METRICS                         |
---------------------------------+----------------------------------
 Total Closed Trades             |                             3216
 Total Net Profit                |            93,057.2907 (930.57%)
 Starting => Finishing Balance   |             10,000 => 103,057.29
 Total Open Trades               |                                3
 Open PL                         |                         1,753.14
 Total Paid Fees                 |                        23,230.11
 Max Drawdown                    |                          -18.33%
 Annual Return                   |                         3532.68%
 Expectancy                      |                    28.94 (0.29%)
 Avg Win | Avg Loss              |                    272.97 | 96.7
 Ratio Avg Win / Avg Loss        |                             2.82
 Percent Profitable              |                              34%
 Longs | Shorts                  |                        53% | 47%
 Avg Holding Time                |             10 hours, 29 minutes
 Winning Trades Avg Holding Time | 21 hours, 33 minutes, 13 seconds
 Losing Trades Avg Holding Time  |   4 hours, 47 minutes, 2 seconds
 Sharpe Ratio                    |                             4.66
 Calmar Ratio                    |                           192.72
 Sortino Ratio                   |                            10.47
 Winning Streak                  |                               18
 Losing Streak                   |                               52
 Largest Winning Trade           |                         4,691.82
 Largest Losing Trade            |                          -330.85
 Total Winning Trades            |                             1093
 Total Losing Trades             |                             2123
 Market Change                   |                          469.18%

```

## Fitting
You can dump current dna values by running `jesse routes --dna`

```console
$ jesse routes --dna

 ewoexit2708     |
-----------------+-----
 stop            |  24
 treshold        |  17
 ewoshort        |  26
 ewolong         |  45
 chop_rsi        |   7
 chop_band_width | 103
 trend_ema_len   |  54
 exit_ema_fast   |   7
 exit_ema_slow   |  52

```
or check dna files located under ``jessepickerdata/dnafiles``  

First line of ``eth-15m-May-2021-ewoexitdnas.py``
```python
dnas = [
['86lZ6^AX3',
44, 129, 67.45, 37, 27, 6.04,
{'stop': 24, 'treshold': 17, 'ewoshort': 26, 'ewolong': 45, 'chop_rsi': 7, 'chop_band_width': 103, 'trend_ema_len': 54,
'exit_ema_fast': 7, 'exit_ema_slow': 52}],
]
```

Routes file template for mass backtest:
```python
routes = [
    ('FTX Futures', 'ANCHOR!', '15m', 'ewoexit2708', '86lZ6^AX3'),
]
extra_candles = [
    ('FTX Futures', 'ANCHOR!', '1h'),
]
```

```console
$ jesse-picker testpairs 2021-05-01 2021-09-25
```
Output:

```console
48/156  Remaining Time: 02:16:37 | Period: 2021-05-01 -> 2021-09-25
Pair       TF    Dna         Total  Total Net    Max.     Annual     Win      Sharpe   Calmar Winning  Losing   Largest      Largest      Winning    Losing     Market
                             Trades Profit %     DD %     Return %   Rate %   Ratio    Ratio  Streak   Streak   Win. Trade   Los. Trade   Trades     Trades     Change %
LUNA-USD   15m   86lZ6^AX3   98     175.35       -17.91   1116       33       2.77     62.31  5        11       5177         -766         32         66         140.82
FIL-USD    15m   86lZ6^AX3   103    129.08       -15.19   672        36       2.97     44.26  3        7        3393         -551         37         66         -61.29
FTM-USD    15m   86lZ6^AX3   56     115.82       -13.1    567        43       3.16     43.25  3        5        3462         -615         24         32         62.66
ETH-USD    15m   86lZ6^AX3   91     104.03       -11.89   480        40       3.45     40.41  4        7        1973         -467         36         55         5.7
DOT-USD    15m   86lZ6^AX3   101    164.15       -25.63   997        36       3.37     38.92  3        10       4557         -807         36         65         -15.6
XTZ-USD    15m   86lZ6^AX3   100    92.69        -11.85   404        40       2.53     34.11  3        6        3280         -510         40         60         24.44
BNB-USD    15m   86lZ6^AX3   107    91.75        -15.68   398        36       2.44     25.39  8        8        3086         -497         39         68         -42.95
SOL-USD    15m   86lZ6^AX3   70     60.89        -11.41   223        34       2.02     19.55  3        5        2860         -438         24         46         225.29
LINK-USD   15m   86lZ6^AX3   88     74.74        -18.17   296        38       2.36     16.29  3        9        2210         -460         33         55         -38.88
XLM-USD    15m   86lZ6^AX3   101    59.52        -16.56   216        37       1.94     13.06  2        7        2864         -384         37         64         -47.02
MATIC-USD  15m   86lZ6^AX3   106    58.08        -17.34   209        29       2.03     12.08  2        11       2774         -444         31         75         36.51
TRX-USD    15m   86lZ6^AX3   129    53.03        -15.51   186        39       1.93     11.96  4        7        2301         -366         50         79         -30.27
BTC-USD    15m   86lZ6^AX3   110    45.96        -18.35   154        37       2.13     8.4    4        7        1444         -372         41         69         -25.67
AAVE-USD   15m   86lZ6^AX3   99     57.53        -28.49   207        31       1.83     7.26   4        19       3302         -481         31         68         -36.82
ALGO-USD   15m   86lZ6^AX3   96     50.23        -27.73   173        35       1.84     6.23   3        11       1994         -382         34         62         27.84
ADA-USD    15m   86lZ6^AX3   102    39.35        -21.28   127        34       1.59     5.95   5        13       2304         -369         35         67         68.67
ATOM-USD   15m   86lZ6^AX3   84     37.81        -20.3    121        30       1.49     5.94   4        10       1908         -401         25         59         87.6
XRP-USD    15m   86lZ6^AX3   101    27.19        -16.9    81         31       1.27     4.79   3        8        2043         -382         31         70         -40.92
LTC-USD    15m   86lZ6^AX3   117    35.72        -24.62   112        40       1.67     4.57   7        11       2006         -395         47         70         -43.98
1INCH-USD  15m   86lZ6^AX3   78     27.38        -23.3    82         36       1.35     3.5    2        7        2012         -407         28         50         -54.89
BCH-USD    15m   86lZ6^AX3   111    16.07        -16.36   44         37       1.01     2.72   5        10       1180         -262         41         70         -48.53
AVAX-USD   15m   86lZ6^AX3   87     15.19        -17.23   42         36       0.88     2.42   2        6        1655         -337         31         56         120.62
UNI-USD    15m   86lZ6^AX3   94     5.37         -19.58   14         33       0.5      0.7    2        8        1104         -279         31         63         -51.58

```
  



## Downsides
It needs better stop loss and take profit calculation mechanism.  
Also see [bias_and_variance](https://machinelearningcompass.com/model_optimization/bias_and_variance/)


## Disclaimer

The simple strategies presented here are solely for **educational purposes**. They are **insufficient for live trading.**

Please remember that the past performance of a strategy is not a guarantee of future results. **USE THEM AT YOUR OWN RISK**.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
