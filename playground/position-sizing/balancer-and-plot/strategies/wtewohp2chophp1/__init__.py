import datetime

import talib
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached
from jesse import utils
import jesse.indicators as ta
import custom_indicators as cta
import numpy as np

# wtewoHyper1 clone with calculated exit points

class wtewohp2chophp1(Strategy):
    def __init__(self):
        super().__init__()
        self.initial_qty = 0
        self.exit_counter = 0
        self.chopfilter = True
        self.shared_vars['AAVE-USDT'] = {'id': 'AAVE-USDT', 'Sharpe': 0.0, 'Calmar': 0.0, 'Total': 0, 'Multip': 1,
                                         'WinRate': 0, 'Shares': 0, 'MyShare': 1}

    # 2018-01-01 2020-08-01

    def hyperparameters(self):
        return [
            {'name': 'chop_rsi', 'type': int, 'min': 3, 'max': 30, 'default': 14},
            {'name': 'chop_upper_limit', 'type': int, 'min': 50, 'max': 80, 'default': 60},
            {'name': 'chop_lower_limit', 'type': int, 'min': 20, 'max': 50, 'default': 40},
        ]

    @property
    def spotcandles(self):
        spot_candles = self.get_candles(self.exchange, self.symbol, '1h')
        return spot_candles[:, 2]


    @property
    def dema(self):
        return talib.DEMA(self.spotcandles, 17)

    @property
    @cached
    def chop(self):
        return cta.chop(self.candles, self.hp['chop_rsi'], sequential=True)

    @property
    @cached
    def stop(self):
        return 28 / 1000  # self.hp['stop'] / 1000

    @property
    @cached
    def treshold(self):
        return 37 / 10  # self.hp['treshold'] / 10  # 38/10  #

    @property
    @cached
    def fastemalen(self):
        return 10  # self.hp['ewoshort']

    @property
    @cached
    def slowemalen(self):
        return 32  # self.hp['ewolong']

    @property
    @cached
    def oblevel(self):
        return 83  # self.hp['oblevel']

    @property
    @cached
    def oslevel(self):
        return -86  # self.hp['oslevel'] * -1

    @property
    @cached
    def maxpartialliq(self):
        return 6  # self.hp['maxpartialliq']

    @property
    @cached
    def initialexitqty(self):
        return 3 / 20  # self.hp['initialexitqty'] / 20

    @property
    @cached
    def qtydivider(self):
        return 15 / 100  # self.hp['qtydivider'] / 100

    @property
    @cached
    def fast_ema(self):
        return ta.ema(self.candles, self.fastemalen, sequential=True)

    @property
    @cached
    def slow_ema(self):
        return ta.ema(self.candles, self.slowemalen, sequential=True)

    @property
    @cached
    def wt(self):
        obl = self.oblevel
        osl = self.oslevel
        return ta.wt(self.candles, wtchannellen=9, wtaveragelen=12, wtmalen=3, oblevel=obl, oslevel=osl,
                     source_type="close", sequential=True)

    @property
    def wt_crossed(self):
        return utils.crossed(
            self.wt.wt1, self.wt.wt2, direction=None, sequential=False
        )

    @property
    def wt_cross_up(self):
        return self.wt.wt2[-1] - self.wt.wt1[-1] <= 0

    @property
    def wt_cross_down(self):
        return self.wt.wt2[-1] - self.wt.wt1[-1] >= 0

    @property
    def wt_oversold(self):
        return self.wt.wtOversold[-1]

    @property
    def wt_overbought(self):
        return self.wt.wtOverbought[-1]

    @property
    def wt_buy(self):
        return self.wt_oversold and self.wt_cross_up and self.wt_crossed

    @property
    def wt_sell(self):
        return self.wt_crossed and self.wt_cross_down and self.wt_overbought

    def isdildo(self, index):
        open = self.candles[:, 1][index]
        close = self.candles[:, 2][index]
        return abs(open - close) * 100 / open > self.treshold

    @property
    def dumpump(self):
        open = self.candles[:, 1][-2]
        close = self.candles[:, 2][-1]
        multibardildo = abs(open - close) * 100 / open > self.treshold
        return multibardildo or self.isdildo(-1) or self.isdildo(-2) or self.isdildo(-3)  # or self.isdildo(-4)

    def should_long(self) -> bool:
        cap = self.chop[-1] > self.hp['chop_upper_limit'] if self.chopfilter else True
        return utils.crossed(self.fast_ema, self.slow_ema, direction='above',
                             sequential=False) and not self.dumpump and cap and self.close > self.dema[-1]

    def should_short(self) -> bool:
        cap = self.chop[-1] < self.hp['chop_lower_limit'] if self.chopfilter else True
        return utils.crossed(self.fast_ema, self.slow_ema, direction='below',
                             sequential=False) and not self.dumpump and cap and self.close < self.dema[-1]

    @property
    def calculatepositionsize(self):
        return self.capital / 8
        # return self.shared_vars[self.symbol]['MyShare'] * (self.capital / (self.shared_vars['Shares'] * 2))

    def go_long(self):
        sl = self.stop
        qty = (utils.size_to_qty(self.calculatepositionsize, self.price,
                                 fee_rate=self.fee_rate) * self.leverage) + 0.005
        self.buy = qty, self.price
        self.stop_loss = qty, self.price - (self.price * sl)
        self.initial_qty = qty
        self.exit_counter = 0

    def go_short(self):
        sl = self.stop
        qty = (utils.size_to_qty(self.calculatepositionsize, self.price,
                                 fee_rate=self.fee_rate) * self.leverage) + 0.005
        self.sell = qty, self.price
        self.stop_loss = qty, self.price + (self.price * sl)
        self.initial_qty = qty
        self.exit_counter = 0

    def update_position(self):
        if self.is_long and self.wt_sell:
            self.partial_liq()

        if self.is_short and self.wt_buy:
            self.partial_liq()

        #     c. Emergency exit! Close position at trend reversal
        if utils.crossed(self.fast_ema, self.slow_ema, sequential=False):
            self.liquidate()

    def liq(self, qty):
        if self.position.pnl > 0:
            self.take_profit = qty, self.position.current_price
        else:
            self.stop_loss = qty, self.position.current_price

    def partial_liq(self):
        if self.exit_counter == self.maxpartialliq:
            self.liquidate()
            self.exit_counter = 0
            return

        # If it's first exit in current position make it special
        if self.exit_counter == 0:
            qty = self.position.qty * self.initialexitqty
            self.exit_counter += 1
            self.liq(qty)
            return

        # Partial exit with wavetrend buy/sell sig. Calculate it with eg. position.qty * 0.25
        if self.exit_counter < self.maxpartialliq:
            qty = self.position.qty * self.qtydivider
            self.exit_counter += 1
            self.liq(qty)
            return

    def before(self):
        self.stats()

    def should_cancel(self) -> bool:
        return True

    def on_open_position(self, order):
        pass

    def stats(self):
        # --------------->
        epoch = self.current_candle[0] / 1000
        ts = datetime.datetime.utcfromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')
        day = datetime.datetime.utcfromtimestamp(epoch).strftime('%d')
        hour = datetime.datetime.utcfromtimestamp(epoch).strftime('%H')
        minute = datetime.datetime.utcfromtimestamp(epoch).strftime('%M')
        # print(f'{self.symbol};{ts};{round(sharpe, 2)};{round(calmar, 2)}')

        if hour == '00' and minute == '00' and self.metrics:
            sharpe = float(self.metrics['sharpe_ratio'])
            calmar = float(self.metrics['calmar_ratio'])
            winrate = float(self.metrics['win_rate'])
            total = self.metrics['total']

            if not np.isnan(sharpe):
                self.shared_vars[self.symbol]['Sharpe'] = sharpe
                self.shared_vars[self.symbol]['Calmar'] = calmar
                self.shared_vars[self.symbol]['Total'] = total
                self.shared_vars[self.symbol]['WinRate'] = winrate

            # print(f"\nI'm {self.symbol}, MyShare is {self.shared_vars[self.symbol]['MyShare']}. Total Share is {self.shared_vars['Shares']}")