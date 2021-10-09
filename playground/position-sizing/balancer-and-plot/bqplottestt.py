import datetime

from bqplot import pyplot as plt
fig = plt.figure(title="Apple Mar-2020 CandleStick Chart")

from jesse import research
research.init()
import numpy as np
import jesse.indicators as ta

aave_candles = research.get_candles('Binance Futures', 'AAVE-USDT', '5m', '2021-08-17', '2021-08-21')
aave_ema_10 = ta.sma(aave_candles, 10, sequential=True)
aave_ema_30 = ta.sma(aave_candles, 30, sequential=True)
aave_ts = aave_candles[:, 0]
aave_open = aave_candles[:, 1]
aave_close = aave_candles[:, 2]
aave_high = aave_candles[:, 3]
aave_low = aave_candles[:, 4]
aave_volume = aave_candles[:, 5]

times = [datetime.datetime.fromtimestamp(c[0] / 1000) for c in aave_candles]
fig.layout.width="800px"


ohlc = plt.ohlc(x=times, y=[aave_open,aave_high,aave_low,aave_close],
                marker="candle", stroke="blue")

ohlc.colors=["lime", "tomato"]
plt.xlabel("Date")

plt.show()
