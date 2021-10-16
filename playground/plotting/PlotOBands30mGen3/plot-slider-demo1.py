from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import custom_indicators as cta
from jesse import research

research.init()

import jesse.indicators as ta

# Define initial parameters
init_Kp = 1.18
init_Ki = 3.337
init_Kd = -1.37

eth_candles = research.get_candles('Binance Futures', 'ETH-USDT', '2h', '2021-08-01', '2021-09-01')
eth_sma_6 = ta.sma(eth_candles, 6, sequential=True)
eth_close = eth_candles[:, 2]

pred, out = cta.pid(eth_close, Kp=init_Kp, Ki=init_Ki, Kd=init_Kd)

# convect timestamps into a format that is supported for plotting
times = []
for c in eth_candles:
    times.append(datetime.fromtimestamp(c[0] / 1000))


# The parametrized function to be plotted
def f(t, amplitude, frequency):
    return amplitude * np.sin(2 * np.pi * frequency * t)


t = np.linspace(0, 1, 1000)

# Create the figure and the line that we will manipulate
fig, ax = plt.subplots()
line, = plt.plot(times, eth_close, color='black', label='ETH', lw=1)
line2, = plt.plot(times, pred, color='green', label='Pred', lw=1)
# plt.plot(t, f(t, init_amplitude, init_frequency), lw=2)
ax.set_xlabel('Time [s]')

axcolor = 'lightgoldenrodyellow'
ax.margins(x=0)

# adjust the main plot to make room for the sliders
plt.subplots_adjust(left=0.25, bottom=0.25)

# Make a horizontal slider to control the frequency.
axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
freq_slider = Slider(
    ax=axfreq,
    label='Ki',
    valmin=-5,
    valmax=5,
    valinit=init_Ki,
)

# Make a vertically oriented slider to control the amplitude
axamp = plt.axes([0.1, 0.25, 0.0225, 0.63], facecolor=axcolor)
amp_slider = Slider(
    ax=axamp,
    label="Kp",
    valmin=-5,
    valmax=5,
    valinit=init_Kp,
    orientation="vertical"
)

# Make a vertically oriented slider to control the amplitude
axKd = plt.axes([0.15, 0.25, 0.025, 0.5], facecolor=axcolor)
Kd_slider = Slider(
    ax=axKd,
    label="Kd",
    valmin=-5,
    valmax=5,
    valinit=init_Kd,
    orientation="vertical"
)


# The function to be called anytime a slider's value changes
def update(val):
    # plt.plot(times, eth_close, color='black', label='ETH')
    pred, out = cta.pid(eth_close, amp_slider.val, freq_slider.val, Kd_slider.val)
    line.set_ydata(eth_close)
    line2.set_ydata(pred)
    fig.canvas.draw_idle()


# register the update function with each slider
freq_slider.on_changed(update)
amp_slider.on_changed(update)
Kd_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')


def reset(event):
    freq_slider.reset()
    amp_slider.reset()
    Kd_slider.reset()


button.on_clicked(reset)

plt.show()
