from datetime import datetime

import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import custom_indicators as cta
from jesse import research

research.init()

import jesse.indicators as ta

eth_candles = research.get_candles('Binance', 'ETH-USDT', '15m', '2021-09-01', '2021-09-15')
eth_sma_50 = ta.sma(eth_candles, 50, sequential=True)
eth_close = eth_candles[:, 2]

pred, out = cta.pid(eth_close, Kp=0, Ki=0, Kd=0.001)

# convect timestamps into a format that is supported for plotting
times = []
for c in eth_candles:
    times.append(datetime.fromtimestamp(c[0] / 1000))


plt.figure(figsize=(15, 6))
plt.plot(times, eth_close, color='black', label='ETH')
# plt.plot(times, eth_sma_50, color='yellow', label='SMA 50')
plt.plot(times, pred, color='red', label='P')
plt.legend()
plt.show()
