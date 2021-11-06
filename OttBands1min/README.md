Flexible & optimized take profit levels:

```python
hyperparameters:
{'name': 'tps_qty_index', 'type': int, 'min': 0, 'max': 1000, 'default': 241}

self.profit_levels = (0.005, 0.01, 0.02, 0.04, 0.08)

tp_qtys = (
    (0.0, 0.1, 0.3, 0.4, 0.2),
    (0.0, 0.1, 0.3, 0.6, 0.0),
    (0.0, 0.1, 0.4, 0.0, 0.5),
    (0.0, 0.1, 0.4, 0.1, 0.4),
    (0.0, 0.2, 0.0, 0.3, 0.5))
```

```console
steam@SOYO MINGW64 /c/jesse-projects/git/jesse_strategies/OttBands1min (master)
$ jesse-tk pick "storage\genetics\OttBands1min-Binance Futures-BTC-USDT-1m-2021-06-01-2021-09-09.txt" pnl2 50 550
Strategy name: OttBands1min Strategy Class: <class 'strategies.OttBands1min.OttBands1min'>
Total 342 unique dnas found.
Picked dnas count: 342
self.dna_fn jessetkdata/dnafiles/OttBands1mindnas.py
p: jessetkdata.dnafiles.OttBands1mindnas
Validated dna. 342/342
```
Created dna file: jessetkdata/dnafiles/OttBands1mindnas.py  

```python
dnas = [
['GqmJ', 49, 63, 17.22, 57, 42, 26.97, {'ott_len': 22, 'ott_percent': 287, 'ott_bw': 351, 'tps_qty_index': 430}],
['HZg*', 33, 24, 9.03, 58, 12, 23.83, {'ott_len': 22, 'ott_percent': 200, 'ott_bw': 321, 'tps_qty_index': 25}],
['smB^', 51, 52, 20.28, 65, 29, 18.76, {'ott_len': 49, 'ott_percent': 272, 'ott_bw': 138, 'tps_qty_index': 684}],
['qmB^', 51, 52, 20.28, 65, 29, 18.76, {'ott_len': 48, 'ott_percent': 272, 'ott_bw': 138, 'tps_qty_index': 684}],
['7DXP', 56, 23, 6.16, 54, 11, 18.3, {'ott_len': 11, 'ott_percent': 116, 'ott_bw': 247, 'tps_qty_index': 506}],
['nlF;', 66, 57, 15.92, 71, 35, 17.17, {'ott_len': 46, 'ott_percent': 268, 'ott_bw': 158, 'tps_qty_index': 241}],
['k/9P', 46, 13, 4.17, 60, 5, 15.14, {'ott_len': 44, 'ott_percent': 37, 'ott_bw': 94, 'tps_qty_index': 506}],
['ulH2', 50, 12, 12.38, 75, 12, 15.05, {'ott_len': 51, 'ott_percent': 268, 'ott_bw': 168, 'tps_qty_index': 127}],
# ... more
```

```console
$ jesse-tk refine jessetkdata/dnafiles/OttBands1mindnas.py 2021-09-16 2021-11-05  

342/342 eta: 00:00:00 | ETH-USDT | 1m | 2021-09-16 -> 2021-11-05
Dna          Total  Longs Shorts Total Net    Max.     Annual     Win      Serenity Sharpe   Calmar   Winning  Losing   Largest      Largest      Winning    Losing   Paid     Market
String       Trades %     %      Profit %     DD %     Return %   Rate %   Index    Ratio    Ratio    Streak   Streak   Win. Trade   Los. Trade   Trades     Trades   Fees     Change %
VM?s         12     50    50     3.4          -0.45    27.06      67       39.78    5.83     59.58    4        2        76.99        -31.15       8          4        48.35    25.51
i47F         7      43    57     3.44         -0.19    27.39      86       26.97    5.6      147.56   4        1        95.46        -19.12       6          1        28.34    25.51
Z6:k         7      43    57     3.36         -0.07    26.66      86       340.7    4.51     398.78   3        1        87.34        -1.0         6          1        28.43    25.51
ulK2         5      60    40     4.2          -0.78    34.2       80       2.52     4.29     43.69    3        1        178.86       -80.36       4          1        20.52    25.51
tl_5         5      60    40     4.2          -0.78    34.2       80       2.52     4.29     43.69    3        1        178.86       -80.36       4          1        20.52    25.51
Q@M^         5      60    40     4.2          -0.78    34.2       80       2.52     4.29     43.69    3        1        178.86       -80.36       4          1        20.52    25.51
>8:Z         17     35    65     4.0          -1.45    32.43      65       2.86     3.98     22.44    5        3        97.4         -91.72       11         6        69.31    25.51
v+7v         3      33    67     0.75         0.0      5.47       100      nan      3.97     inf      3        0        46.17        0.0          3          0        11.98    25.51
`j)F         58     47    53     12.07        -5.1     126.03     62       1.54     3.75     24.73    8        4        155.89       -277.78      36         22       237.35   25.51
veLM         5      60    40     2.04         -0.61    15.57      80       2.47     3.69     25.45    3        1        79.31        -18.62       4          1        20.2     25.51
gT?4         16     62    38     6.01         -1.77    51.84      69       2.82     3.6      29.33    4        2        191.12       -166.94      11         5        65.21    25.51
HRBB         12     58    42     3.51         -1.84    27.97      67       2.64     3.42     15.24    6        2        145.45       -194.09      8          4        47.87    25.51
ej)F         54     43    57     9.09         -4.66    86.36      63       2.98     3.22     18.52    13       3        149.26       -181.7       34         20       216.84   25.51
_Y+F         87     48    52     9.3          -5.24    88.95      56       1.9      2.91     16.98    6        5        150.06       -320.56      49         38       358.3    25.51
Uw.p         54     54    46     5.52         -2.61    46.94      54       2.25     2.79     18.02    3        3        143.08       -201.06      29         25       222.06   25.51
^g.S         68     51    49     7.43         -2.92    67.01      57       2.19     2.73     22.98    5        5        117.74       -214.66      39         29       275.26   25.51
hY.t         71     49    51     4.88         -3.66    40.6       70       1.62     2.64     11.08    13       2        68.89        -136.15      50         21       284.78   25.51
iY+_         83     51    49     7.6          -5.44    68.93      51       1.34     2.61     12.67    6        8        120.85       -178.3       42         41       329.58   25.51
dH=e         12     58    42     2.34         -1.57    17.97      75       0.61     2.58     11.44    5        1        123.54       -161.52      9          3        48.43    25.51
Xu0>         61     61    39     5.57         -3.78    47.43      70       1.71     2.18     12.56    10       3        79.3         -224.44      43         18       246.12   25.51
ulH2         19     68    32     6.58         -5.97    57.74      58       1.36     2.17     9.68     5        3        207.88       -316.58      11         8        76.23    25.51
hY.=         71     48    52     5.46         -6.15    46.33      66       0.57     2.17     7.54     12       3        158.2        -150.8       47         24       282.05   25.51
hY.l         82     49    51     4.44         -4.47    36.42      59       0.49     2.12     8.15     9        4        73.97        -134.49      48         34       326.0    25.51
w28^         4      50    50     1.01         -0.33    7.47       75       2.02     2.1      22.63    2        1        123.04       -33.43       3          1        16.02    25.51
gY:4         90     70    30     6.82         -6.57    60.31      56       0.52     2.07     9.18     6        5        196.92       -191.99      50         40       365.31   25.51
```