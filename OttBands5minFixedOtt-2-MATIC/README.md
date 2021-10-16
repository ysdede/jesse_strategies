## OttBands 5min  

Trained between 2021-07-07 and 2021-10-15  
Training and testing periods are swapped and split changed to %50 - %50    
Training period is last 50 days as this day, 2021-10-15.  
Optimization mode is `Smart Sortino`

Be careful when changing leverage and position size.  

## Hyperparameters

```python
    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 5, 'max': 50, 'default': 31},
            {'name': 'ott_percent', 'type': int, 'min': 150, 'max': 350, 'default': 244},
            {'name': 'ott_bw', 'type': int, 'min': 60, 'max': 180, 'default': 119},
            {'name': 'tps_qty_index', 'type': int, 'min': 0, 'max': 125, 'default': 79},
            {'name': 'max_risk', 'type': int, 'min': 20, 'max': 70, 'default': 27},
        ]
```
### ott_len
This is the ma length of OTT indicator (ma is Kaufman Moving Average in this case)  

### ott_percent  
This is the percent parameter for the OTT indicator. Hyperopt parameter is divided by 100 to get more precision.  
244 = 2.44  
```python
    @property
    @cached
    def ott_percent(self):
        return self.hp['ott_percent'] / 100
```
### ott_bw
OTT bandwidth parameter. It's used by dividing it by 10_000  

```python
    @property
    @cached
    def ott_upper_band(self):
        multiplier = 1 + (self.hp['ott_bw'] / 10000)
        return np.multiply(self.ott.ott, multiplier)
```

I need to visualize the bands to make it clear.  
White lines are OTT bands. They are symmetric in this case. It's possible to use distinct bandwidth values.  
But it will cause bias, optimization will fit to market cycle, eg it will pick a smaller filter value for upper band in a bull run.  
And strategy will almost work **long only**. (Yes, I've tested it) It can be useful if used correctly and optimized frequently.  
Blue line is MAvg, ma line of OTT and purple one is OTT signal itself. Upper and lower bands calculated by multipling   
OTT signal by ott_bw value.

As seen on the image below bands help to filter small movements in sideways markets.  
Strategy will long or short only if the MAvg crosses upper/lower bands. And it will exit position when the MAV signal crosses  
OTT (middle) signal. 

This is the exit position condition:  
```python
    def update_position(self):
        if self.is_long and self.cross_down:  # self.cross_down_upper_band:
            self.liquidate()
        if self.is_short and self.cross_up:  # self.cross_up_lower_band:
            self.liquidate()
```
`self.cross_down` and `self.cross_up` checks for MAvg\~OTT crosses.  
There are commented out lines `self.cross_down_upper_band` and `self.cross_down_upper_band`    
If these are used instead of MAvg\~OTT cross, strategy will make more trades.  
Anyways you can test them with different parameters.  

<img src="https://s3.tradingview.com/snapshots/i/i6Z1cCky.png" width=100% height=100%>  


### tps_qty_index  

Qty index determined by `tps_qty_index` parameter.    

Take profit levels are predetermined by a list:  
```python
self.fib = (0.005, 0.01, 0.02, 0.04, 0.08)
```
At first it was a fibonacci series but modified after some tests and the name (self.fib) remained the same.  

Multipy fib number with 100 to find out take profit levels:  
0.005 = 0.5%  
0.04 = 4%  

It makes easier to calculate percentages.  

Quantities for take profit levels are picked from a list by a optimized tuple index.  
Tuples are located under `vars.py`  

```python
tp_qtys = (  # len = 126
    (1, 1, 1, 1, 6),
    (1, 1, 1, 2, 5),
    (1, 1, 1, 3, 4),
    (1, 1, 1, 4, 3),
    # .
    # ..
    (5, 1, 1, 2, 1),
    (5, 1, 2, 1, 1),
    (5, 2, 1, 1, 1),
    (6, 1, 1, 1, 1)
)
```
Every step multiplied by 10%, eg (1, 1, 1, 4, 3) = 10%, 10%, 10%, 40%, 30%  
so qtys for profit levels are:  

```console
Tp level    Qty  
0.5%        10%  
1%          10%  
2%          10%  
4%          40%  
8%          30%  
```

### max_risk
If determined margin risk for calculated stoploss is greater than **max_risk** don't trade. Yes, don't trade.  
It can be replaced with [risk-to-qty](https://docs.jesse.trade/docs/utils.html#risk-to-qty)  


Stoploss is current OTT Signal:  
```python
    @property
    @cached
    def calc_long_stop(self):
        return self.ott.ott[-1]
```


Risk for trade is calculated by method(s) below.  
```python
def calc_risk_for_long(self):
        sl = self.calc_long_stop

        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((self.close - sl) / self.close)

        if (margin_risk / self.capital * 100) > self.max_risk:
            print(
               f'\nLong Margin Risk: {round(margin_risk)} | Capital: {round(self.capital)} \| Risk % {round(margin_risk / self.capital * 100, 2)} | Price {self.close} | Stop price: {round(sl, 4)} | Stop diff: {round(self.close - sl, 4)} | Stoploss % {round((self.close - sl) / self.close * 100, 2)}')
            return False
        else:
            return True
```
It's stricly bound to max_risk hyperparameter and leverage and position size. If the conditions are not met
it will not enter trades or open more trades.

Yeah this is odd.

You can find optimization files under `storage/genetics`, chosen dnas under `jessetkdata/dnafiles` eg:  
`jessetkdata/dnafiles/MATIC-USDT 2021-09-01 2021-10-15.py`

```python
dnas = [
['Rd_:/', 61, 31, 33.37, 40, 35, 2.26, {'ott_len': 29, 'ott_percent': 302, 'ott_bw': 144, 'tps_qty_index': 28, 'max_risk': 24}],
['EmE?(', 48, 29, 23.84, 36, 25, 12.47, {'ott_len': 22, 'ott_percent': 325, 'ott_bw': 104, 'tps_qty_index': 36, 'max_risk': 20}],
['NlK+2', 46, 39, 22.85, 43, 41, 13.77, {'ott_len': 27, 'ott_percent': 322, 'ott_bw': 113, 'tps_qty_index': 5, 'max_risk': 26}],
['NeK+*', 56, 25, 29.72, 31, 19, 1.28, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 5, 'max_risk': 21}],
['X\\K/*', 47, 23, 14.25, 33, 18, -5.91, {'ott_len': 32, 'ott_percent': 282, 'ott_bw': 113, 'tps_qty_index': 11, 'max_risk': 21}],
['teR+2', 54, 22, 21.23, 42, 26, 6.76, {'ott_len': 48, 'ott_percent': 304, 'ott_bw': 124, 'tps_qty_index': 5, 'max_risk': 26}],
['NXwNA', 64, 14, 17.36, 66, 15, 19.41, {'ott_len': 27, 'ott_percent': 272, 'ott_bw': 180, 'tps_qty_index': 60, 'max_risk': 36}],
['NeG+2', 44, 43, 16.31, 45, 40, 22.08, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 107, 'tps_qty_index': 5, 'max_risk': 26}],
['geR+2', 53, 30, 15.66, 38, 26, 3.98, {'ott_len': 41, 'ott_percent': 304, 'ott_bw': 124, 'tps_qty_index': 5, 'max_risk': 26}],
['ZeX/7', 55, 43, 31.55, 34, 38, -9.44, {'ott_len': 33, 'ott_percent': 304, 'ott_bw': 133, 'tps_qty_index': 11, 'max_risk': 29}],
['peK+2', 48, 33, 19.92, 40, 22, 3.17, {'ott_len': 46, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 5, 'max_risk': 26}],
['ZYBN+', 42, 33, 12.84, 40, 25, 5.21, {'ott_len': 33, 'ott_percent': 274, 'ott_bw': 99, 'tps_qty_index': 60, 'max_risk': 22}],
['NeK12', 48, 47, 20.28, 51, 37, 17.57, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 14, 'max_risk': 26}],
['QeK+2', 45, 42, 17.56, 44, 36, 14.0, {'ott_len': 28, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 5, 'max_risk': 26}],
['NeK+,', 51, 35, 26.21, 38, 26, 7.85, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 5, 'max_risk': 23}],
['dMsPP', 70, 10, 12.16, 53, 13, 1.63, {'ott_len': 39, 'ott_percent': 244, 'ott_bw': 174, 'tps_qty_index': 63, 'max_risk': 45}],
['M<dY;', 90, 11, 12.4, 72, 11, 6.68, {'ott_len': 26, 'ott_percent': 201, 'ott_bw': 151, 'tps_qty_index': 78, 'max_risk': 32}],
['NeK+2', 44, 45, 15.37, 45, 37, 20.84, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 5, 'max_risk': 26}],
['\\cf(7', 46, 30, 24.63, 44, 34, 11.68, {'ott_len': 35, 'ott_percent': 299, 'ott_bw': 154, 'tps_qty_index': 0, 'max_risk': 29}],
['cLR,I', 50, 64, 32.87, 34, 79, -7.2, {'ott_len': 39, 'ott_percent': 241, 'ott_bw': 124, 'tps_qty_index': 6, 'max_risk': 41}],
['NeL+2', 45, 42, 17.46, 40, 37, 7.0, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 115, 'tps_qty_index': 5, 'max_risk': 26}],
['hu[86', 48, 31, 14.1, 42, 28, 4.25, {'ott_len': 41, 'ott_percent': 345, 'ott_bw': 137, 'tps_qty_index': 25, 'max_risk': 29}],
['NeK82', 46, 47, 18.94, 45, 37, 17.11, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 25, 'max_risk': 26}],
['NeKM2', 46, 47, 17.28, 45, 37, 18.66, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 59, 'max_risk': 26}],
['NeKB2', 48, 47, 13.23, 51, 37, 12.57, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 41, 'max_risk': 26}],
['NeK,2', 46, 47, 18.25, 48, 37, 23.27, {'ott_len': 27, 'ott_percent': 304, 'ott_bw': 113, 'tps_qty_index': 6, 'max_risk': 26}],
]
```

to test the dnas against to a specific time period run:

```Console
jesse-tk refine "jessetkdata/dnafiles/MATIC-USDT 2021-10-01 2021-10-15.py" 2021-09-01 2021-10-15
```
(jesse-tk is rewrite version of ex-jesse-picker, anyways you can use old tool)

```Console
47/51   eta: 00:00:36 | MATIC-USDT | 5m | 2021-10-01 -> 2021-10-15
Dna          Total  Longs Shorts Total Net    Max.     Annual     Win      Serenity Sharpe   Calmar   Winning  Losing   Largest      Largest      Winning    Losing   Paid     Market
String       Trades %     %      Profit %     DD %     Return %   Rate %   Index    Ratio    Ratio    Streak   Streak   Win. Trade   Los. Trade   Trades     Trades   Fees     Change %
NeK82        14     57    43     16.53        -2.01    6324.76    64       29.64    12.07    3154.08  4        3        345          -248         9          5        121.94   12.29
NXwNA        2      100   0      5.73         0.0      327.83     100      nan      7.3      inf      2        0        312          0            2          0        16.47    12.29
NeKB2        14     57    43     12.47        -1.46    2861.48    64       31.9     11.61    1965.87  4        3        330          -241         9          5        120.27   12.29
hu[86        10     60    40     14.26        -2.49    3298.73    70       28.88    9.94     1322.53  2        1        341          -235         7          3        85.75    12.29
NeKM2        14     57    43     15.85        -2.1     5460.68    64       28.28    11.36    2595.32  4        3        382          -222         9          5        121.53   12.29
X\K/*        8      62    38     10.8         -2.16    1537.6     62       27.96    8.46     712.64   2        2        448          -168         5          3        66.85    12.29
NeK+,        12     58    42     17.73        -2.55    7462.66    67       27.7     12.12    2921.41  4        3        377          -249         8          4        104.97   12.29
NeK+*        10     70    30     17.28        -2.55    6688.59    70       26.48    12.06    2618.38  5        3        367          -172         7          3        85.43    12.29
NeKU2        14     57    43     13.07        -1.86    3159.21    64       25.09    9.74     1696.5   4        3        433          -217         9          5        120.57   12.29
NeK:2        13     54    46     11.85        -1.65    2201.36    62       24.69    9.55     1333.38  4        3        356          -239         8          5        110.17   12.29
NeK*2        13     54    46     14.64        -2.55    3765.97    62       20.92    8.81     1474.27  4        3        454          -243         8          5        111.11   12.29
NeK-2        13     54    46     13.35        -2.2     2884.36    62       20.6     8.65     1310.34  4        3        431          -241         8          5        110.58   12.29
NeK12        13     54    46     12.56        -1.85    2498.92    62       20.44    9.7      1347.36  4        3        323          -239         8          5        110.19   12.29
NeK,2        14     57    43     15.92        -2.38    5257.3     64       19.94    8.82     2206.3   4        3        530          -246         9          5        121.77   12.29
NeK+0        13     54    46     15.17        -2.55    4263.47    62       18.59    9.8      1669.02  4        3        369          -244         8          5        111.25   12.29
NeK+2        13     54    46     15.17        -2.55    4263.47    62       18.59    9.8      1669.02  4        3        369          -244         8          5        111.25   12.29
NeK/2        13     54    46     11.76        -1.97    2057.24    62       16.97    7.7      1044.31  4        3        450          -238         8          5        109.98   12.29
NeK(2        13     54    46     13.76        -2.83    3061.9     54       14.92    6.95     1081.56  4        3        581          -241         7          6        110.87   12.29
\cf(7        8      62    38     13.84        -2.9     2852.66    62       14.85    6.97     982.34   2        2        602          -254         5          3        69.75    12.29
NeL+2        12     42    58     13.94        -2.55    3190.56    58       14.03    8.1      1249.01  3        2        375          -200         7          5        103.0    12.29
EmE?(        10     50    50     14.82        -2.71    4550.57    50       12.28    9.34     1676.12  3        4        456          -185         5          5        85.72    12.29
NeG+2        15     53    47     11.99        -2.96    1997.67    53       7.85     7.13     675.6    3        3        368          -238         8          7        127.1    12.29
Rd_:/        9      44    56     7.58         -2.89    675.48     67       3.83     6.51     233.96   3        2        348          -235         6          3        74.78    12.29
QeK+2        15     60    40     6.97         -4.17    551.09     47       2.91     4.48     132.22   2        3        370          -293         7          8        126.68   12.29
NeK/6        15     60    40     5.75         -4.65    414.89     53       2.8      3.55     89.3     2        4        438          -288         8          7        123.84   12.29
NlK+2        17     65    35     8.3          -4.43    775.86     47       2.25     4.82     175.23   3        4        375          -292         8          9        146.22   12.29
geR+2        12     50    50     6.31         -4.03    422.3      50       2.04     3.38     104.82   2        2        361          -287         6          6        101.37   12.29
JY>N)        17     53    47     7.12         -4.63    683.18     47       1.78     4.68     147.41   2        4        324          -213         8          9        140.72   12.29
Prh5M        14     57    43     7.71         -8.38    603.98     50       1.42     3.39     72.04    3        3        491          -332         7          7        117.57   12.29
teR+2        12     58    42     6.07         -4.92    394.76     50       1.29     3.57     80.29    2        3        353          -286         6          6        100.47   12.29
```

Another test with different period
```Console
jesse-tk refine "jessetkdata/dnafiles/MATIC-USDT 2021-09-01 2021-10-15.py" 2021-09-01 2021-10-15
```

```Console
51/51   eta: 00:00:00 | MATIC-USDT | 5m | 2021-09-01 -> 2021-10-15
Dna          Total  Longs Shorts Total Net    Max.     Annual     Win      Serenity Sharpe   Calmar   Winning  Losing   Largest      Largest      Winning    Losing   Paid     Market
String       Trades %     %      Profit %     DD %     Return %   Rate %   Index    Ratio    Ratio    Streak   Streak   Win. Trade   Los. Trade   Trades     Trades   Fees     Change %
Rd_:/        24     38    62     35.55        -2.89    1446.14    67       41.5     10.47    500.88   5        2        447          -302         16         8        232.2    -5.15
EmE?(        23     48    52     31.4         -2.95    999.53     57       18.13    7.26     339.19   3        4        526          -213         13         10       207.47   -5.15
NlK+2        30     63    37     24.74        -4.43    581.32     50       11.61    5.27     131.29   3        4        435          -339         15         15       284.55   -5.15
NeK+*        23     61    39     28.54        -4.03    745.27     57       10.35    6.92     184.94   5        3        404          -189         13         10       204.52   -5.15
EDFN+        50     54    46     33.02        -5.64    1218.13    50       9.51     6.16     215.85   3        4        414          -307         25         25       480.23   -5.15
X\K/*        20     45    55     16.07        -3.61    312.12     50       8.68     4.96     86.48    2        3        477          -207         10         10       169.15   -5.15
teR+2        19     53    47     21.45        -4.92    417.66     58       7.87     5.19     84.95    6        3        405          -328         11         8        173.15   -5.15
NXwNA        10     80    20     9.55         -3.39    166.8      60       6.45     4.18     49.19    3        2        332          -358         6          4        83.4     -5.15
NeG+2        36     58    42     23.03        -6.41    521.79     47       6.07     4.85     81.34    3        3        408          -264         17         19       320.34   -5.15
geR+2        26     42    58     13.94        -4.48    325.76     54       5.75     3.89     72.71    3        2        404          -320         14         12       232.38   -5.15
ZeX/7        34     53    47     28.38        -10.3    814.67     56       5.74     4.35     79.08    3        4        529          -364         19         15       326.68   -5.15
peK+2        31     48    52     23.99        -5.54    519.49     52       5.06     4.6      93.75    4        3        414          -324         16         15       280.24   -5.15
ZYBN+        28     50    50     15.96        -4.9     291.39     46       4.71     4.69     59.52    4        5        347          -227         13         15       237.15   -5.15
NeK12        39     54    46     25.13        -8.13    782.55     51       4.26     7.08     96.27    4        5        371          -275         20         19       343.53   -5.15
QeK+2        32     62    38     19.25        -5.24    367.67     47       4.2      4.5      70.21    3        3        415          -328         15         17       284.3    -5.15
NeK+,        28     54    46     23.51        -6.15    519.01     50       4.12     5.64     84.4     4        4        397          -263         14         14       242.91   -5.15
dMsPP        8      75    25     11.77        -4.03    151.74     75       4.02     4.38     37.7     5        2        367          -293         6          2        69.63    -5.15
M<dY;        8      88    12     10.55        -3.22    129.86     88       3.91     4.72     40.29    5        1        298          -359         7          1        68.75    -5.15
NeK+2        39     54    46     27.85        -8.77    777.78     49       3.76     6.12     88.68    4        5        414          -275         19         20       337.58   -5.15
\cf(7        25     76    24     25.31        -6.74    596.69     48       3.74     4.57     88.48    3        4        668          -337         12         13       220.8    -5.15
cLR,I        59     54    46     30.71        -12.3    1087.11    49       3.74     4.2      88.39    4        4        654          -470         29         30       559.68   -5.15
NeL+2        33     48    52     26.36        -7.84    687.92     48       3.73     5.75     87.75    4        5        420          -233         16         17       289.47   -5.15
hu[86        27     56    44     16.55        -4.91    361.81     52       3.68     4.72     73.64    3        5        358          -289         14         13       232.28   -5.15
NeK82        39     54    46     24.52        -8.31    681.53     49       3.62     6.51     81.98    4        5        377          -271         19         20       337.56   -5.15
NeKM2        39     54    46     23.61        -8.38    639.65     49       3.59     6.2      76.36    4        5        416          -242         19         20       337.97   -5.15
NeKB2        39     54    46     19.25        -8.01    596.87     51       3.25     7.09     74.5     4        5        367          -268         20         19       341.93   -5.15
NeK,2        39     54    46     26.61        -10.32   783.26     49       3.12     5.39     75.91    4        5        591          -275         19         20       346.41   -5.15
NeK:2        38     53    47     19.95        -8.46    538.49     50       3.07     6.15     63.63    4        5        394          -264         19         19       329.88   -5.15
NeKU2        39     54    46     19.98        -8.87    557.85     51       2.96     5.71     62.88    4        5        476          -239         20         19       340.84   -5.15
NeK*2        38     53    47     24.12        -9.7     589.53     47       2.86     5.16     60.78    4        5        498          -267         18         20       327.83   -5.15

```
I liked `NeK+*`, added it to routes and performed a random backtest

```python
routes = [

    ('Binance Futures', 'MATIC-USDT', '5m', 'OttBands5minFixed2', 'NeK+*'),

]

extra_candles = []

```

```console
jesse-tk random 2021-05-01 2021-10-15 50 20
```
Console output is

```Console
50/50   Remaining Time: 00:00:00
Pair       TF    Start Date   End Date     Total  Total Net    Max.     Annual     Win      Sharpe   Calmar       Winning  Losing   Largest      Largest      Winning    Losing     Market
                                           Trades Profit %     DD %     Return %   Rate %   Ratio    Ratio        Streak   Streak   Win. Trade   Los. Trade   Trades     Trades     Change %
MATIC-USDT 5m    2021-05-24   2021-06-13   6      15.15        -0.74    1230       83       9.62     1662.75      3        1        386          -153         5          1          22.65
MATIC-USDT 5m    2021-05-25   2021-06-14   6      15.15        -0.74    1230       83       9.62     1662.75      3        1        386          -153         5          1          -15.79
MATIC-USDT 5m    2021-05-23   2021-06-12   6      14.97        -0.74    1191       83       9.54     1611.27      3        1        368          -153         5          1          5.52
MATIC-USDT 5m    2021-05-21   2021-06-10   5      11.29        -0.74    614        80       8.13     830.0        2        1        363          -153         4          1          -18.42
MATIC-USDT 5m    2021-05-30   2021-06-19   8      15.99        -1.88    1423       75       8.92     757.67       3        1        386          -219         6          2          -18.46
MATIC-USDT 5m    2021-05-29   2021-06-18   8      15.99        -1.88    1423       75       8.92     757.67       3        1        386          -219         6          2          -17.7
MATIC-USDT 5m    2021-06-08   2021-06-28   6      13.76        -1.88    955        83       8.63     508.16       3        1        371          -202         5          1          -25.77
MATIC-USDT 5m    2021-06-07   2021-06-27   6      12.7         -1.88    790        83       7.97     420.45       3        1        371          -202         5          1          -32.14
MATIC-USDT 5m    2021-06-09   2021-06-29   8      11.76        -1.88    666        75       7.04     354.79       4        1        371          -209         6          2          -24.09
MATIC-USDT 5m    2021-06-15   2021-07-05   8      11.36        -1.88    617        75       7.24     328.31       4        1        349          -197         6          2          -25.98
MATIC-USDT 5m    2021-06-04   2021-06-24   9      14.6         -3.65    1126       67       7.57     308.21       3        2        384          -216         6          3          -35.47
MATIC-USDT 5m    2021-06-02   2021-06-22   9      14.6         -3.65    1126       67       7.57     308.21       3        2        384          -216         6          3          -39.82
MATIC-USDT 5m    2021-09-01   2021-09-21   10     14.17        -4.03    1060       60       7.71     263.05       4        3        383          -169         6          4          -14.9
MATIC-USDT 5m    2021-08-30   2021-09-19   10     13.34        -4.03    916        60       7.18     227.37       3        3        362          -174         6          4          -3.7
MATIC-USDT 5m    2021-06-13   2021-07-03   8      9.28         -1.88    408        75       6.11     217.25       4        1        349          -197         6          2          -18.21
MATIC-USDT 5m    2021-06-06   2021-06-26   8      10.76        -3.65    558        62       6.15     152.78       3        2        372          -209         5          3          -32.2
MATIC-USDT 5m    2021-07-07   2021-07-27   8      6.28         -1.91    206        50       4.0      107.46       2        1        362          -191         4          4          -10.13
MATIC-USDT 5m    2021-09-17   2021-10-07   8      8.93         -3.8     398        62       5.8      104.74       3        3        357          -175         5          3          -9.16
MATIC-USDT 5m    2021-09-09   2021-09-29   9      7.58         -3.04    293        56       5.29     96.15        4        2        368          -180         5          4          -21.4
MATIC-USDT 5m    2021-08-27   2021-09-16   9      8.78         -4.03    381        56       5.16     94.52        2        3        362          -174         5          4          3.83
MATIC-USDT 5m    2021-05-17   2021-06-06   3      4.48         -1.6     126        67       4.01     78.7         2        1        350          -169         2          1          -12.71
MATIC-USDT 5m    2021-05-16   2021-06-05   3      4.48         -1.6     126        67       4.04     78.63        1        1        346          -175         2          1          1.99
MATIC-USDT 5m    2021-09-11   2021-10-01   8      6.9          -3.8     254        50       4.73     66.88        4        3        373          -183         4          4          -13.74
MATIC-USDT 5m    2021-06-10   2021-06-30   8      6.75         -3.65    233        62       4.21     63.75        4        2        355          -200         5          3          -21.2
MATIC-USDT 5m    2021-05-18   2021-06-07   5      3.42         -1.6     90         60       3.1      56.27        2        1        350          -169         3          2          -9.8
MATIC-USDT 5m    2021-09-22   2021-10-12   11     5.6          -3.8     196        45       3.47     51.47        3        3        353          -165         5          6          18.78
MATIC-USDT 5m    2021-06-30   2021-07-20   12     8.15         -7.04    324        50       4.14     46.06        2        4        363          -215         6          6          -37.49
MATIC-USDT 5m    2021-08-23   2021-09-12   7      3.39         -2.51    91         43       2.42     36.33        2        2        356          -176         3          4          -19.14
MATIC-USDT 5m    2021-08-26   2021-09-15   9      4.81         -4.03    145        44       2.96     36.06        2        3        356          -176         4          5          -13.6
MATIC-USDT 5m    2021-06-25   2021-07-15   13     7.05         -7.04    254        54       3.65     36.02        2        4        344          -218         7          6          -22.85
MATIC-USDT 5m    2021-07-09   2021-07-29   7      3.16         -2.86    80         43       2.53     27.97        2        2        356          -157         3          4          -2.2
MATIC-USDT 5m    2021-05-09   2021-05-29   2      1.72         -1.6     39         50       2.02     24.13        1        1        346          -175         1          1          113.64
MATIC-USDT 5m    2021-08-22   2021-09-11   8      2.29         -2.61    63         38       1.83     24.01        2        2        353          -174         3          5          -17.92
MATIC-USDT 5m    2021-07-12   2021-08-01   9      3.98         -6.29    108        44       2.48     17.21        2        4        362          -187         4          5          4.04
MATIC-USDT 5m    2021-06-23   2021-07-13   12     4.18         -7.04    116        50       2.38     16.41        2        4        344          -218         6          6          -6.72
MATIC-USDT 5m    2021-07-06   2021-07-26   10     2.74         -5.11    67         40       1.71     13.12        2        3        350          -189         4          6          -14.62
MATIC-USDT 5m    2021-08-25   2021-09-14   8      1.77         -4.03    43         38       1.36     10.79        2        3        356          -176         3          5          -15.73
MATIC-USDT 5m    2021-06-28   2021-07-18   13     2.69         -7.04    66         46       1.55     9.31         2        4        335          -212         6          7          -27.77
MATIC-USDT 5m    2021-07-04   2021-07-24   10     2.17         -7.04    50         40       1.37     7.14         2        4        343          -204         4          6          -15.05
MATIC-USDT 5m    2021-09-20   2021-10-10   10     0.74         -3.8     26         30       0.94     6.79         2        3        341          -165         3          7          2.77
```

and it will create a csv file located at  
`jessetkdata/results/Random-Binance Futures-MATIC-USDT-5m-2021-05-01-2021-10-15-20211016 172631--20211016 172631.csv`

It's trained for last 50 days but surprisingly performs well at May, June 2021.
