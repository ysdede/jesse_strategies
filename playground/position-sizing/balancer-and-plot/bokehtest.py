import datetime
from math import pi
from bokeh.plotting import figure
from bokeh.io import output_notebook,show
from bokeh.resources import INLINE

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
times = [int(c[0] / 1000000) for c in aave_candles]
output_notebook(resources=INLINE)

inc = aave_close > aave_open
dec = aave_open > aave_close

w = 12*60*60*1000

p = figure(x_axis_type="datetime", plot_width=800, plot_height=500, title = "Apple, March - 2020")

p.segment(times, aave_high, times, aave_low, color="black")

p.vbar(times[inc], w, aave_open[inc], aave_close[inc], fill_color="lawngreen", line_color="red")

p.vbar(times[dec], w, aave_open[dec], aave_close[dec], fill_color="tomato", line_color="lime")

show(p)
