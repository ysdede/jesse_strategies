import numpy as np
import talib
from jesse import utils
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached

import custom_indicators as cta
from vars import tp_qtys


# Old ott2 but uses KAMA instead of VAR.
# Stoploss is still same.


class OttBands30mGen3(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None
        self.initial_qty = 0
        self.fib = (0.01, 0.02, 0.03, 0.05, 0.08)

    def hyperparameters(self):
        return [
            {'name': 'ott_ubw', 'type': int, 'min': 20, 'max': 225, 'default': 99},
            {'name': 'ott_dbw', 'type': int, 'min': 20, 'max': 225, 'default': 99},
            {'name': 'long_tps_qty_index', 'type': int, 'min': 0, 'max': 125, 'default': 62},
            {'name': 'short_tps_qty_index', 'type': int, 'min': 0, 'max': 125, 'default': 62},
            {'name': 'chop_rsi_len', 'type': int, 'min': 5, 'max': 25, 'default': 19},
            {'name': 'chop_bandwidth', 'type': int, 'min': 25, 'max': 225, 'default': 141},
            {'name': 'max_risk', 'type': int, 'min': 10, 'max': 50, 'default': 35},
            #
        ]

    @property
    @cached
    def max_risk(self):
        return self.hp['max_risk'] / 10

    @property
    @cached
    def ott_len(self):
        return 15  # self.hp['ott_len']

    @property
    @cached
    def ott_percent(self):
        return 0.89  # 89 / 100  # self.hp['ott_percent'] / 100

    @property
    @cached
    def ott(self):
        return cta.ott(self.candles[-960:, 2], self.ott_len, self.ott_percent, ma_type='kama', sequential=True)

    @property
    @cached
    def ott_upper_band(self):
        multiplier = 1 + (self.hp['ott_ubw'] / 10000)
        return np.multiply(self.ott.ott, multiplier)

    @property
    @cached
    def ott_lower_band(self):
        multiplier = 1 - (self.hp['ott_dbw'] / 10000)
        return np.multiply(self.ott.ott, multiplier)

    @property
    @cached
    def cross_up_upper_band(self):
        return utils.crossed(self.ott.mavg, self.ott_upper_band, direction='above', sequential=False)

    @property
    @cached
    def cross_down_upper_band(self):
        return utils.crossed(self.ott.mavg, self.ott_upper_band, direction='below', sequential=False)

    @property
    @cached
    def cross_down_lower_band(self):
        return utils.crossed(self.ott.mavg, self.ott_lower_band, direction='below', sequential=False)

    @property
    @cached
    def cross_up_lower_band(self):
        return utils.crossed(self.ott.mavg, self.ott_lower_band, direction='above', sequential=False)

    @property
    @cached
    def cross_up(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='above', sequential=False)

    @property
    @cached
    def cross_down(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='below', sequential=False)

    @property
    @cached
    def chop(self):
        return talib.RSI(self.candles[-960:, 2], self.hp['chop_rsi_len'])

    @property
    @cached
    def chop_upper_band(self):
        return self.chop[-1] > 40 + (self.hp['chop_bandwidth'] / 10)

    @property
    @cached
    def chop_lower_band(self):
        return self.chop[-1] < 60 - (self.hp['chop_bandwidth'] / 10)

    @property
    @cached
    def calc_risk_for_long(self):
        sl = self.calc_long_stop

        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((self.close - sl) / self.close)
        sl_x_lev = ((self.close - sl) / self.close)  # * self.leverage
        # print('sl_x_lev', sl_x_lev)
        leveraged_risk = (self.close - sl) * self.leverage
        # if self.capital / leveraged_risk > self.hp['max_risk'] / 10:
        if (margin_risk / self.capital * 100) > self.max_risk:
            #print(
            #    f'\nLong Margin Risk: {round(margin_risk)} | Capital: {round(self.capital)} | Risk % {round(margin_risk / self.capital * 100, 2)} | Price {self.close} | Stop price: {round(sl, 4)} | Stop diff: {round(self.close - sl, 4)} | Stoploss % {round((self.close - sl) / self.close * 100, 2)}')
            return False
        else:
            return True

    @property
    @cached
    def calc_risk_for_short(self):
        sl = self.calc_short_stop

        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((abs(self.close - sl)) / self.close)
        # leveraged_risk = (self.close - sl) * self.leverage
        # if self.capital / leveraged_risk > self.hp['max_risk'] / 10:
        if (margin_risk / self.capital * 100) > self.max_risk:
            #print(
            #    f'\nShort Margin Risk: {round(margin_risk)} | Capital: {round(self.capital)} | Risk % {round(margin_risk / self.capital * 100, 2)} | Price {self.close} | Stop price: {round(sl, 4)} | Stop diff: {round(self.close - sl, 4)} | Stoploss % {round(abs(self.close - sl) / self.close * 100, 2)}')
            return False
        else:
            return True

    def should_long(self) -> bool:
        return self.cross_up_upper_band and self.chop_upper_band and self.calc_risk_for_long

    def should_short(self) -> bool:
        return self.cross_down_lower_band and self.chop_lower_band and self.calc_risk_for_short

    @property
    @cached
    def pos_size_in_usd(self):
        return self.capital / (len(get_all_trading_routes()) * 10)

    @property
    @cached
    def pos_size(self):
        return utils.size_to_qty(self.pos_size_in_usd, self.price, fee_rate=self.fee_rate) * self.leverage

    def go_long(self):
        self.buy = self.pos_size, self.price
        # self.trade_ts = self.candles[:, 0][-1]

    def go_short(self):
        self.sell = self.pos_size, self.price
        # self.trade_ts = self.candles[:, 0][-1]

    @property
    @cached
    def calc_long_stop(self):
        return self.ott.ott[-1]

    @property
    @cached
    def calc_short_stop(self):
        return self.ott.ott[-1]

    def on_open_position(self, order):
        if self.is_long:
            sl = self.calc_long_stop
            self.stop_loss = self.position.qty, sl

            qty = self.position.qty

            tp1_qty = qty * (tp_qtys[self.hp['long_tps_qty_index']][0] / 10)
            tp2_qty = qty * (tp_qtys[self.hp['long_tps_qty_index']][1] / 10)
            tp3_qty = qty * (tp_qtys[self.hp['long_tps_qty_index']][2] / 10)
            tp4_qty = qty * (tp_qtys[self.hp['long_tps_qty_index']][3] / 10)
            tp5_qty = qty * (tp_qtys[self.hp['long_tps_qty_index']][4] / 10)

            tp1_target_price = self.position.entry_price * (1 + (self.fib[0]))
            tp2_target_price = self.position.entry_price * (1 + (self.fib[1]))
            tp3_target_price = self.position.entry_price * (1 + (self.fib[2]))
            tp4_target_price = self.position.entry_price * (1 + (self.fib[3]))
            tp5_target_price = self.position.entry_price * (1 + (self.fib[4]))

            self.take_profit = [
                (tp1_qty, tp1_target_price),
                (tp2_qty, tp2_target_price),
                (tp3_qty, tp3_target_price),
                (tp4_qty, tp4_target_price),
                (tp5_qty, tp5_target_price)
            ]

        if self.is_short:
            sl = self.calc_short_stop
            self.stop_loss = self.position.qty, sl

            qty = self.position.qty

            tp1_qty = qty * (tp_qtys[self.hp['short_tps_qty_index']][0] / 10)
            tp2_qty = qty * (tp_qtys[self.hp['short_tps_qty_index']][1] / 10)
            tp3_qty = qty * (tp_qtys[self.hp['short_tps_qty_index']][2] / 10)
            tp4_qty = qty * (tp_qtys[self.hp['short_tps_qty_index']][3] / 10)
            tp5_qty = qty * (tp_qtys[self.hp['short_tps_qty_index']][4] / 10)

            tp1_target_price = self.position.entry_price * (1 - (self.fib[0]))
            tp2_target_price = self.position.entry_price * (1 - (self.fib[1]))
            tp3_target_price = self.position.entry_price * (1 - (self.fib[2]))
            tp4_target_price = self.position.entry_price * (1 - (self.fib[3]))
            tp5_target_price = self.position.entry_price * (1 - (self.fib[4]))

            self.take_profit = [
                (tp1_qty, tp1_target_price),
                (tp2_qty, tp2_target_price),
                (tp3_qty, tp3_target_price),
                (tp4_qty, tp4_target_price),
                (tp5_qty, tp5_target_price)
            ]

        self.initial_qty = self.position.qty

    def update_position(self):
        if self.is_long and self.cross_down:  # _upper_band:
            self.liquidate()
        if self.is_short and self.cross_up:  # self.cross_up_lower_band:
            self.liquidate()

        # if self.is_long and self.wt_sell:
        #     qty = (self.position.pnl_percentage / self.leverage) * (self.hp['tp_qty_multi'] / 100) * self.initial_qty
        #     if self.position.pnl > 0:
        #         self.take_profit = qty, self.price
        #
        # if self.is_short and self.wt_buy:
        #     qty = (self.position.pnl_percentage / self.leverage) * (self.hp['tp_qty_multi'] / 100) * self.initial_qty
        #     if self.position.pnl > 0:
        #         self.take_profit = qty, self.price

        # if True:  # Trailing stop
        #     if self.is_long and self.average_stop_loss:
        #         sl = self.ott.ott[-1]
        #
        #         if sl > self.average_stop_loss:  # and sl > self.average_entry_price:
        #             self.stop_loss = self.position.qty, sl
        #
        #     if self.is_short and self.average_stop_loss:
        #         sl = self.ott.ott[-1]
        #
        #         if sl < self.average_stop_loss:  # and sl < self.average_entry_price:
        #             self.stop_loss = self.position.qty, sl

    def should_cancel(self) -> bool:
        return True
