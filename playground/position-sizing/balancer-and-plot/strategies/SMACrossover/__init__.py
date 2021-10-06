"""
Simple Moving Average Crossover Strategy
Author: FengkieJ (fengkiejunis@gmail.com)
Simple moving average crossover strategy is the ''hello world'' of algorithmic trading.
This strategy uses two SMAs to determine '''Golden Cross''' to signal for long position, and '''Death Cross''' to signal for short position.
"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

class SMACrossover(Strategy):
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
        if self.position.pnl_percentage/self.position.leverage > 29.6:
            self.liquidate()
        # If there exist long position, but the signal shows Death Cross, then close the position, and vice versa.
        if utils.crossed(self.fast_sma, self.slow_sma, sequential=False):
            self.liquidate()
