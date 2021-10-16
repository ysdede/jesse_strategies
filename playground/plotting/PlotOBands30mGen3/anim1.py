'''
This file contains a simple animation demo using mplfinance "external axes mode".

Note that presently mplfinance does not support "blitting" (blitting makes animation
more efficient).  Nonetheless, the animation is efficient enough to update at least
once per second, and typically more frequently depending on the size of the plot.
'''
import pandas as pd
import mplfinance as mpf
import matplotlib.animation as animation
import os
from jesse import validate_cwd

from candlesdf import get_candles_as_df
os.chdir(os.getcwd())
validate_cwd()
df = get_candles_as_df('Binance Futures', 'BTC-USDT', '1m', '2021-10-08', '2021-10-10')

fig = mpf.figure(style='charles', figsize=(7, 8))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(3, 1, 3)


def animate(ival):
    if (20 + ival) > len(df):
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return
    data = df.iloc[0:(20 + ival)]
    ax1.clear()
    ax2.clear()
    mpf.plot(data, ax=ax1, volume=ax2, type='candle')


ani = animation.FuncAnimation(fig, animate, interval=100)

mpf.show()
