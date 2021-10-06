"""
Simple Moving Average Crossover Strategy
Author: FengkieJ (fengkiejunis@gmail.com)
Simple moving average crossover strategy is the ''hello world'' of algorithmic trading.
This strategy uses two SMAs to determine '''Golden Cross''' to signal for long position, and '''Death Cross''' to signal for short position.
"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils
import mplfinance as mpf
import matplotlib.animation as animation
import os
from jesse import validate_cwd
from candlesdf import get_candles_as_df
import matplotlib.pyplot as plt


class SMACrossover2(Strategy):
    def __init__(self):
        super().__init__()
        self.firstrun = True
        self.counter = 1
        """self.idf = None
        self.ax_main = None
        self.axes = None
        self.ax_emav = None
        self.ax_hisg = None
        self.ax_macd = None
        self.ax_sign = None
        self.ax_volu = None
        self.df = None"""

        self.idf = get_candles_as_df('Binance Futures', 'AAVE-USDT', '5m', '2021-08-20', '2021-08-21')

        # =======
        #  MACD:

        self.df = self.idf.iloc[0:30]

        exp12 = self.df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = self.df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        apds = [mpf.make_addplot(exp12, color='lime'),
                mpf.make_addplot(exp26, color='c'),
                mpf.make_addplot(histogram, type='bar', width=0.7, panel=1,
                                 color='dimgray', alpha=1, secondary_y=False),
                mpf.make_addplot(macd, panel=1, color='fuchsia', secondary_y=True),
                mpf.make_addplot(signal, panel=1, color='b', secondary_y=True),
                ]

        s = mpf.make_mpf_style(base_mpf_style='classic', rc={'figure.facecolor': 'lightgray'})

        fig, self.axes = mpf.plot(self.df, type='candle', addplot=apds, figscale=1.5, figratio=(7, 5), title='\n\nMACD',
                                  style=s, volume=True, volume_panel=2, panel_ratios=(6, 3, 2), returnfig=True)

        self.ax_main = self.axes[0]
        self.ax_emav = self.ax_main
        self.ax_hisg = self.axes[2]
        self.ax_macd = self.axes[3]
        self.ax_sign = self.ax_macd
        self.ax_volu = self.axes[4]
        self.df = self.idf
        # mpf.show()


    @property
    def slow_sma(self):
        return ta.ema(self.candles, 44, sequential=True)

    @property
    def fast_sma(self):
        return ta.ema(self.candles, 6, sequential=True)

    def should_long(self) -> bool:
        # Golden Cross (reference: https://www.investopedia.com/terms/g/goldencross.asp)
        # Fast SMA above Slow SMA
        return utils.crossed(self.fast_sma, self.slow_sma, direction='above', sequential=False)
        # return self.fast_sma > self.slow_sma

    def should_short(self) -> bool:
        # Death Cross (reference: https://www.investopedia.com/terms/d/deathcross.asp)
        # Fast SMA below Slow SMA
        return utils.crossed(self.fast_sma, self.slow_sma, direction='below', sequential=False)
        # return self.fast_sma < self.slow_sma

    def should_cancel(self) -> bool:
        return False

    def go_long(self):
        # Open long position and use entire balance to buy
        qty = utils.size_to_qty(self.capital, self.price, fee_rate=self.fee_rate)

        self.buy = qty, self.price
        self.stop_loss = qty, self.price - (self.price * 0.024)

    def go_short(self):
        # Open short position and use entire balance to sell
        qty = utils.size_to_qty(self.capital, self.price, fee_rate=self.fee_rate)

        self.sell = qty, self.price
        self.stop_loss = qty, self.price + (self.price * 0.024)

    def update_position(self):
        if self.position.pnl_percentage / self.position.leverage > 29.6:
            self.liquidate()
        # If there exist long position, but the signal shows Death Cross, then close the position, and vice versa.
        if utils.crossed(self.fast_sma, self.slow_sma, sequential=False):
            self.liquidate()

    def before(self):
        self.animate(self.counter)
        self.counter += 1
        # plt.pause(0.05)
        if self.firstrun:
            self.runonce()

    def runonce(self):
        print('First!')
        self.firstrun = False

    def animate(self, ival):
        if (20 + ival) > len(self.df):
            print('20+ival >')
            return
        data = self.df.iloc[0:(30 + ival)]
        exp12 = data['Close'].ewm(span=12, adjust=False).mean()
        exp26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        apds = [mpf.make_addplot(exp12, color='lime', ax=self.ax_emav),
                mpf.make_addplot(exp26, color='c', ax=self.ax_emav),
                mpf.make_addplot(histogram, type='bar', width=0.7,
                                 color='dimgray', alpha=1, ax=self.ax_hisg),
                mpf.make_addplot(macd, color='fuchsia', ax=self.ax_macd),
                mpf.make_addplot(signal, color='b', ax=self.ax_sign),
                ]

        for ax in self.axes:
            ax.clear()
        mpf.plot(data, type='candle', addplot=apds, ax=self.ax_main, volume=self.ax_volu)
        print('Plott')
        plt.pause(0.05)



