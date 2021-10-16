'''
This file contains a animation demo using mplfinance "external axes mode",
in which animate both the display of candlesticks as well as the display
of MACD (Moving Average Convergence Divergence) visual analysis.

In this example, instead of creating the Figure and Axes external to mplfiance,
we allow mplfinance to create the Figure and Axes using its "panel method", and
set kwarg `returnfig=True` so that mplfinance will return the Figure and Axes.

We then take those Axes and pass them back into mplfinance ("external axes mode")
as part of the animation.

Note that presently mplfinance does not support "blitting" (blitting makes animation
more efficient).  Nonetheless, the animation is efficient enough to update at least
once per second, and typically more frequently depending on the size of the plot.
'''

import os

import matplotlib.animation as animation
import mplfinance as mpf
from jesse import validate_cwd
from simple_pid import PID

from candlesdf import get_candles_as_df
from custom_indicators import pid

os.chdir(os.getcwd())
validate_cwd()
idf = get_candles_as_df('Binance Futures', 'BNB-USDT', '15m', '2021-09-01', '2021-10-10')

mpf.__version__

# =======
#  MACD:
wcn = 120

pidx = PID(1, 4, 0, setpoint=0)  # 1, 1, 0.001
pidy = PID(1, 4, 0, setpoint=0)  # 1, 1, 0.001

# pidx.sample_time = 0.04
# pidy.sample_time = 0.04

pidx.output_limits = (0, 1000)
pidy.output_limits = (0, 1000)

pidmulti = 1

pidxval = 0
pidyval = 0

farkx = 0
farky = 0

df = idf.iloc[0:wcn]

ma = df['Close'].ewm(span=3, adjust=False).mean()

exp12 = df['Close'].ewm(span=12, adjust=False).mean()
exp26 = df['Close'].ewm(span=26, adjust=False).mean()
macd = exp12 - exp26
signal = macd.ewm(span=9, adjust=False).mean()
histogram = macd - signal

apds = [mpf.make_addplot(ma, color='lime'),
        mpf.make_addplot(exp26, color='c'),
        mpf.make_addplot(histogram, type='bar', width=0.7, panel=1,
                         color='dimgray', alpha=1, secondary_y=False),
        # mpf.make_addplot(macd, panel=1, color='fuchsia', secondary_y=True),
        # mpf.make_addplot(signal, panel=1, color='b', secondary_y=True),
        ]

s = mpf.make_mpf_style(base_mpf_style='classic', rc={'figure.facecolor': 'lightgray'})

fig, axes = mpf.plot(df, type='candle', addplot=apds, figscale=1.8, figratio=(8, 5), title='\n\nPI',
                     style=s, volume=False, panel_ratios=(6, 2), returnfig=True)

ax_main = axes[0]
ax_emav = ax_main
ax_hisg = axes[2]
ax_macd = axes[3]
ax_sign = ax_macd
# ax_volu = axes[4]

df = idf


def animate(ival):
    if (wcn + ival) > len(df):
        print('20+ival >')
        return

    # data = df.iloc[1 + ival:(1 + wcn + ival)]
    data = df.iloc[0 + ival:(0 + wcn + ival)]
    #
    # farkx = currPos[0] - _kordinat[0]
    # farky = currPos[1] - _kordinat[1]

    pidxval = pidx(farkx)
    pidyval = pidy(farky)
    #

    # ma = data['Close'].ewm(span=2, adjust=False).mean()
    # ma = pid(data['Close'].to_numpy())
    data = df.iloc[0 + ival:(0 + wcn + ival)]
    # ma, out = pid(df['Close'].to_numpy())[0 + ival:(0 + wcn + ival)]

    pred, out = pid(df['Close'].to_numpy())
    # pred, out = pid(df['Close'].ewm(span=2, adjust=False).mean())

    pred = pred[0 + ival:(0 + wcn + ival)]
    out = out[0 + ival:(0 + wcn + ival)]
    # exp12 = data['Close'].ewm(span=12, adjust=False).mean()
    # exp26 = data['Close'].ewm(span=26, adjust=False).mean()
    # macd = out # exp12 - exp26
    # signal = out # macd.ewm(span=9, adjust=False).mean()
    histogram = out  # macd - signal
    apds = [mpf.make_addplot(pred, color='red', ax=ax_emav),
            # mpf.make_addplot(exp26, color='c', ax=ax_emav),
            mpf.make_addplot(histogram, type='bar', width=0.7,
                             color='dimgray', alpha=1, ax=ax_hisg),
            # mpf.make_addplot(macd, color='fuchsia', ax=ax_macd),
            # mpf.make_addplot(signal, color='b', ax=ax_sign),
            ]

    for ax in axes:
        ax.clear()
    mpf.plot(data, type='candle', addplot=apds, ax=ax_main, volume=False)
    # plt.pause(0.200)


ani = animation.FuncAnimation(fig, animate, interval=250)

#
# animate(1)
# animate(2)
# animate(3)
# animate(4)
# animate(5)
mpf.show()
