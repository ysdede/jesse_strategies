import datetime
import plotly.graph_objects as go
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

# convect timestamps into a format that is supported for plotting
times = [datetime.datetime.fromtimestamp(c[0] / 1000) for c in aave_candles]
candlestick = go.Candlestick(
                            x=times,
                            open=aave_open,
                            high=aave_high,
                            low=aave_low,
                            close=aave_close
                            )

fig = go.Figure(data=[candlestick])

fig.show()
