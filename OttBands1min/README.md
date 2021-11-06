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
PS C:\jesse-projects\OttBands1min> jesse-tk pick "storage/genetics/OttBands1min-Binance Futures-BTC-USDT-1m-2021-06-01-2021-09-09.txt" pnl2 50 250
Strategy name: OttBands1min Strategy Class: <class 'strategies.OttBands1min.OttBands1min'>
Total 342 unique dnas found.
Picked dnas count: 332
self.dna_fn jessetkdata/dnafiles/OttBands1mindnas.py
p: jessetkdata.dnafiles.OttBands1mindnas
Validated dna. 332/332
```

```python
dnas = [
['GqmJ', 49, 63, 17.22, 57, 42, 26.97, {'ott_len': 22, 'ott_percent': 287, 'ott_bw': 351, 'tps_qty_index': 430}],
['HZg*', 33, 24, 9.03, 58, 12, 23.83, {'ott_len': 22, 'ott_percent': 200, 'ott_bw': 321, 'tps_qty_index': 25}],
['smB^', 51, 52, 20.28, 65, 29, 18.76, {'ott_len': 49, 'ott_percent': 272, 'ott_bw': 138, 'tps_qty_index': 684}],
['qmB^', 51, 52, 20.28, 65, 29, 18.76, {'ott_len': 48, 'ott_percent': 272, 'ott_bw': 138, 'tps_qty_index': 684}],
['7DXP', 56, 23, 6.16, 54, 11, 18.3, {'ott_len': 11, 'ott_percent': 116, 'ott_bw': 247, 'tps_qty_index': 506}],
['nlF;', 66, 57, 15.92, 71, 35, 17.17, {'ott_len': 46, 'ott_percent': 268, 'ott_bw': 158, 'tps_qty_index': 241}],
# ... more
```

