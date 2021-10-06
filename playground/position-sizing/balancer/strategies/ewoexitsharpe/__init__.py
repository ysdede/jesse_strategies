import datetime
import os
import statistics
import sys

import numpy as np
import talib
from jesse.routes import router
from jesse.strategies import Strategy, cached
from jesse import utils
import jesse.indicators as ta
from jesse.services.selectors import get_all_trading_routes
import custom_indicators as cta
import balancer


class ewoexitsharpe(Strategy):
    def __init__(self):
        super().__init__()

        self.finish_date = sys.argv[-1]
        self.chop_filter_enabled = True
        self.initial_qty = 0
        self.exit_counter = 0
        self.qty_per_exit = 0
        self.clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        # ---------------------------> SHARPE
        self.bl = balancer.balancer(router.routes, self.finish_date, self.shared_vars, self.metrics, 1, True)
        self.shared_vars['Shares'] = 40
        # print('BL Pairs', self.bl.pairs)
        self.days = 0

        self.header1 = ['Time']
        # self.csv_rows = np.array(self.header1)
        self.results = []
        self.formatter = '{: <12} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6} {: <6}'

        # <--------------------------- SHARPE

    def hyperparameters(self):
        return [
            {'name': 'stop', 'type': int, 'min': 10, 'max': 80, 'default': 42},
            {'name': 'treshold', 'type': int, 'min': 10, 'max': 50, 'default': 15},  # / 10
            {'name': 'ewoshort', 'type': int, 'min': 3, 'max': 30, 'default': 25},
            {'name': 'ewolong', 'type': int, 'min': 20, 'max': 60, 'default': 28},
            {'name': 'chop_rsi', 'type': int, 'min': 2, 'max': 30, 'default': 11},
            {'name': 'chop_band_width', 'type': int, 'min': 1, 'max': 150, 'default': 33},
            {'name': 'trend_ema_len', 'type': int, 'min': 3, 'max': 163, 'default': 122},
            {'name': 'exit_ema_fast', 'type': int, 'min': 2, 'max': 10, 'default': 9},
            {'name': 'exit_ema_slow', 'type': int, 'min': 20, 'max': 250, 'default': 180},
        ]

    @property
    @cached
    def candles_60(self):
        return self.candles[-60:]

    @property
    @cached
    def candles_240(self):
        return self.candles[-240:]

    @property
    @cached
    def close_60(self):
        return self.candles[-60:, 2]

    @property
    @cached
    def close_240(self):
        return self.candles[-240:, 2]

    @property
    @cached
    def spotcandles(self):
        spot_candles = self.get_candles(self.exchange, self.symbol, '1h')
        return spot_candles[:, 2]

    @property
    @cached
    def chop(self):
        return cta.chop(self.close_60, self.hp['chop_rsi'], sequential=True)

    @property
    @cached
    def stop(self):
        return self.hp['stop'] / 1000

    @property
    @cached
    def treshold(self):
        return self.hp['treshold'] / 10  # 38/10  #

    @property
    @cached
    def fast_ema(self):
        return ta.ema(self.close_60, self.hp['ewoshort'], sequential=True)

    @property
    @cached
    def slow_ema(self):
        return ta.ema(self.close_240, self.hp['ewolong'], sequential=True)

    @property
    @cached
    def exit_fast_ema(self):
        return ta.ema(self.close_60, self.hp['exit_ema_fast'], sequential=True)

    @property
    @cached
    def exit_slow_ema(self):
        return ta.ema(self.close_240, self.hp['exit_ema_slow'], sequential=True)

    @property
    @cached
    def trend_ema(self):
        return ta.ema(self.spotcandles, self.hp['trend_ema_len'], sequential=False)

    def isdildo(self, index):
        open = self.candles[:, 1][index]
        close = self.candles[:, 2][index]
        return abs(open - close) * 100 / open > self.treshold

    @property
    @cached
    def dumpump(self):
        open = self.candles[:, 1][-2]
        close = self.candles[:, 2][-1]
        multibardildo = abs(open - close) * 100 / open > self.treshold
        return multibardildo or self.isdildo(-1) or self.isdildo(-2) or self.isdildo(-3)  # or self.isdildo(-4)

    def should_long(self) -> bool:
        chop_filter = True
        if self.chop_filter_enabled:
            chop_filter = self.chop[-1] > 50 + (self.hp['chop_band_width'] / 10)
        return utils.crossed(self.fast_ema, self.slow_ema, direction='above',
                             sequential=False) and not self.dumpump and chop_filter and self.close > self.trend_ema

    def should_short(self) -> bool:
        chop_filter = True
        if self.chop_filter_enabled:
            chop_filter = self.chop[-1] < 50 - (self.hp['chop_band_width'] / 10)
        return utils.crossed(self.fast_ema, self.slow_ema, direction='below',
                             sequential=False) and not self.dumpump and chop_filter and self.close < self.trend_ema

    @property
    def positionsize(self):
        if self.bl.sharpe_enabled:
            print('\n', self.shared_vars[self.symbol]['MyShare'], '---------------------------------------')
            return self.shared_vars[self.symbol]['MyShare'] * (self.capital / (self.shared_vars['Shares'] * 4))
        else:
            return self.capital / (10 * len(get_all_trading_routes()))

    def go_long(self):
        sl = self.stop
        qty = utils.size_to_qty(self.positionsize, self.price, fee_rate=self.fee_rate) * self.leverage + 0.005
        self.buy = qty, self.price
        self.stop_loss = qty, self.price - (self.price * sl)
        self.initial_qty = qty
        self.exit_counter = 0

    def go_short(self):
        sl = self.stop
        qty = utils.size_to_qty(self.positionsize, self.price, fee_rate=self.fee_rate) * self.leverage + 0.005
        self.sell = qty, self.price
        self.stop_loss = qty, self.price + (self.price * sl)
        self.initial_qty = qty
        self.exit_counter = 0

    def update_position(self):
        if self.position.pnl_percentage / self.position.leverage > 40:
            pass  # self.liquidate()

        if self.is_long and utils.crossed(self.exit_fast_ema, self.exit_slow_ema, direction='below', sequential=False):
            self.liquidate()

        if self.is_short and utils.crossed(self.exit_fast_ema, self.exit_slow_ema, direction='above', sequential=False):
            self.liquidate()

        #     c. Emergency exit! Close position at trend reversal
        # if utils.crossed(self.fast_ema, self.slow_ema, sequential=False):
        #    self.liquidate()

    def before(self):
        # Get sharpe per symbol at 00:00
        if self.bl.tick(self.current_candle):
            if self.bl.get_sharpe(self.current_candle, self.metrics):
                self.shared_vars[self.symbol]['Sharpe'] = self.bl.get_sharpe(self.current_candle, self.metrics)

                self.bl.stats(self.symbol, self.shared_vars, self.current_candle, self.metrics)

            if self.bl.shares:
                self.shared_vars['Shares'] = self.bl.shares

            if self.bl.normalized_deviations:
                # print('self.bl.normalized_deviations', self.bl.normalized_deviations)
                for i, sym in enumerate(self.bl.pairs):
                    self.shared_vars[sym]['MyShare'] = self.bl.normalized_deviations[i]

    def should_cancel(self) -> bool:
        return True

    def on_open_position(self, order):
        pass

