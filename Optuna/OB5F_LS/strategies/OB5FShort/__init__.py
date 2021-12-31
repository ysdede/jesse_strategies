import numpy as np
import talib
from jesse import utils
# from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached

import custom_indicators as cta
from vars import tp_qtys


class OB5FShort(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None
        self.initial_qty = 0
        self.fib = (0.01, 0.02, 0.03, 0.05, 0.08)
        # #max_risk_short: 40, ott_bw_down: 123, ott_len: 43, ott_percent: 116, tps_qty_index: 33
        # self.hp = {}
        # 0204772181090990793

        self.hp = {
            "ott_len": 20,
            "ott_percent": 477,
            "ott_bw_down": 218,
            "tps_qty_index": 109,
            "max_risk_short": 99,
            "signal_ma_len": 79
        }

    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 3, 'max': 43, 'default': 20},
            {'name': 'ott_percent', 'type': int,
                'min': 50, 'max': 600, 'default': 477},
            {'name': 'ott_bw_down', 'type': int,
                'min': 35, 'max': 240, 'default': 218},
            {'name': 'tps_qty_index', 'type': int,
                'min': 20, 'max': 120, 'default': 109},
            {'name': 'max_risk_short', 'type': int,
                'min': 20, 'max': 100, 'default': 99},
            {'name': 'signal_ma_len', 'type': int,
                'min': 3, 'max': 80, 'default': 79},
        ]

    @property
    def ott_len(self):
        return self.hp['ott_len']

    @property
    def ott_percent(self):
        return self.hp['ott_percent'] / 100

    @property
    def max_risk_short(self):
        return self.hp['max_risk_short'] / 10

    @property
    @cached
    def ott(self):
        return cta.ott(self.candles[-960:, 2], self.ott_len, self.ott_percent, ma_type='kama', sequential=True)

    @property
    @cached
    def signal_ma(self):
        return talib.KAMA(self.candles[-240:, 2], self.hp['signal_ma_len'])

    @property
    @cached
    def ott_lower_band(self):
        multiplier = 1 - (self.hp['ott_bw_down'] / 10000)
        return np.multiply(self.ott.ott, multiplier)

    @property
    def cross_down_lower_band(self):
        return utils.crossed(self.signal_ma, self.ott_lower_band, direction='below', sequential=False)

    @property
    def cross_up_lower_band(self):
        return utils.crossed(self.signal_ma, self.ott_lower_band, direction='above', sequential=False)

    @property
    def cross_up(self):
        return utils.crossed(self.signal_ma, self.ott.ott, direction='above', sequential=False)

    @property
    def cross_down(self):
        return utils.crossed(self.signal_ma, self.ott.ott, direction='below', sequential=False)

    @property
    def calc_risk_for_short(self):
        sl = self.calc_short_stop
        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((abs(self.close - sl)) / self.close)
        return margin_risk / self.capital * 100 <= self.max_risk_short

    def should_long(self) -> bool:
        return False

    def should_short(self) -> bool:
        # print(self.hp)
        return self.cross_down_lower_band and self.calc_risk_for_short

    @property
    def pos_size_in_usd(self):
        return self.capital / 10  # (len(get_all_trading_routes()) * 5)

    @property
    def pos_size(self):
        return utils.size_to_qty(self.pos_size_in_usd, self.price, precision=6, fee_rate=self.fee_rate) * self.leverage

    def go_long(self):
        self.buy = self.pos_size, self.price

    def go_short(self):
        self.sell = self.pos_size, self.price

    @property
    def calc_short_stop(self):
        return self.ott.ott[-1]

    def on_open_position(self, order):

        if self.is_short:
            self.stop_loss = self.position.qty, self.calc_short_stop

            qty = self.position.qty

            tp1_qty = qty * (tp_qtys[self.hp['tps_qty_index']][0] / 10)
            tp2_qty = qty * (tp_qtys[self.hp['tps_qty_index']][1] / 10)
            tp3_qty = qty * (tp_qtys[self.hp['tps_qty_index']][2] / 10)
            tp4_qty = qty * (tp_qtys[self.hp['tps_qty_index']][3] / 10)
            tp5_qty = qty * (tp_qtys[self.hp['tps_qty_index']][4] / 10)

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
        if self.is_short and self.cross_up:  # self.cross_up_lower_band:
            self.liquidate()

    # def terminate(self):
        # print(self.hp)

        # if True:  # Trailing stop

        #     if self.is_short and self.average_stop_loss:
        #         sl = self.ott.ott[-1]
        #
        #         if sl < self.average_stop_loss:  # and sl < self.average_entry_price:
        #             self.stop_loss = self.position.qty, sl

    def should_cancel(self) -> bool:
        return True
