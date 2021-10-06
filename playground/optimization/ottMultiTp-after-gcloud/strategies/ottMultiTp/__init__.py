import talib
from jesse import utils
from jesse.strategies import Strategy, cached
from jesse.services.selectors import get_all_trading_routes

import custom_indicators as cta

from vars import tps


# Old ott2 but uses KAMA instead of VAR.
# Stoploss is still same.

# Added multiple take profit points.
# Edited hps min-max values.
# Reduced chop_bandwidth resolution

class ottMultiTp(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None

    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 2, 'max': 80, 'default': 45},  # 12
            {'name': 'ott_percent', 'type': int, 'min': 200, 'max': 700, 'default': 419},  # 540
            {'name': 'stop_loss', 'type': int, 'min': 10, 'max': 400, 'default': 90},
            {'name': 'risk_reward', 'type': int, 'min': 20, 'max': 100, 'default': 49},
            {'name': 'chop_rsi_len', 'type': int, 'min': 2, 'max': 65, 'default': 6},
            {'name': 'chop_bandwidth', 'type': int, 'min': 1, 'max': 25, 'default': 18},
            {'name': 'tps_index', 'type': int, 'min': 0, 'max': 170, 'default': 0},
        ]

    @property
    @cached
    def tp1_qty(self):
        return tps[self.hp['tps_index']][0] / 20  # 1 = 0.05, 18 = 0.90

    @property
    @cached
    def tp2_qty(self):
        return tps[self.hp['tps_index']][1] / 20

    @property
    @cached
    def tp3_qty(self):
        return tps[self.hp['tps_index']][2] / 20

    @property
    @cached
    def ott_len(self):
        return self.hp['ott_len']

    @property
    @cached
    def ott_percent(self):
        return self.hp['ott_percent'] / 100

    @property
    @cached
    def stop(self):
        return self.hp['stop_loss'] / 10000  # 122 / 10000  #

    @property
    @cached
    def RRR(self):
        return self.hp['risk_reward'] / 10  # 40 / 10

    @property
    @cached
    def ott(self):
        return cta.ott(self.candles[-960:, 2], self.ott_len, self.ott_percent, ma_type='kama', sequential=True)

    @property
    @cached
    def chop(self):
        return talib.RSI(self.candles[-960:, 2], self.hp['chop_rsi_len'])
        # return jta.rsi(self.candles[-240:, 2], self.hp['chop_rsi_len'], sequential=True)
        # return cta.cae(self.candles[-240:, 2], self.hp['chop_rsi_len'], sequential=True)

    @property
    @cached
    def chop_upper_band(self):
        return 40 + (self.hp['chop_bandwidth'])

    @property
    @cached
    def chop_lower_band(self):
        return 60 - (self.hp['chop_bandwidth'])

    def should_long(self) -> bool:
        return self.cross_up and self.chop[-1] > self.chop_upper_band

    def should_short(self) -> bool:
        return self.cross_down and self.chop[-1] < self.chop_lower_band

    @property
    @cached
    def pos_size(self):
        return utils.size_to_qty(self.capital/(len(get_all_trading_routes()) * 8), self.price, fee_rate=self.fee_rate) * self.leverage  # + 0.001

    def go_long(self):
        self.buy = self.pos_size, self.price
        # self.trade_ts = self.candles[:, 0][-1]

    def go_short(self):
        self.sell = self.pos_size, self.price
        # self.trade_ts = self.candles[:, 0][-1]

    def on_open_position(self, order):
        if self.is_long:
            sl = self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)
            self.stop_loss = self.position.qty, sl
            # tp = self.position.entry_price + (self.position.entry_price * (self.stop * self.RRR))
            tp1 = self.position.entry_price + (self.position.entry_price * self.stop)
            tp3 = self.position.entry_price + (self.position.entry_price * self.stop * self.RRR)
            tp2 = (tp1 + tp3) / 2

            # self.take_profit = self.position.qty, tp
            qty = self.position.qty

            self.take_profit = [
                (qty * self.tp1_qty, tp1),
                (qty * self.tp2_qty, tp2),
                (qty * self.tp3_qty, tp3)
            ]

        if self.is_short:
            sl = self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)
            self.stop_loss = self.position.qty, sl
            # tp = self.position.entry_price - (self.position.entry_price * (self.stop * self.RRR))

            tp1 = self.position.entry_price - (self.position.entry_price * self.stop)
            tp3 = self.position.entry_price - (self.position.entry_price * self.stop * self.RRR)
            tp2 = (tp1 + tp3) / 2

            # self.take_profit = self.position.qty, tp
            qty = self.position.qty
            self.take_profit = [
                (qty * self.tp1_qty, tp1),
                (qty * self.tp2_qty, tp2),
                (qty * self.tp3_qty, tp3)
            ]

    @property
    @cached
    def cross_up(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='above', sequential=False)

    @property
    @cached
    def cross_down(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='below', sequential=False)

    def update_position(self):
        if self.is_long and self.cross_down:
            self.liquidate()
        if self.is_short and self.cross_up:
            self.liquidate()

        if False:  # Trailing stop
            if self.is_long and self.average_stop_loss:
                sl = self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)

                if sl > self.average_stop_loss and sl > self.average_entry_price:
                    self.stop_loss = self.position.qty, sl

            if self.is_short and self.average_stop_loss:
                sl = self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)

                if sl < self.average_stop_loss and sl < self.average_entry_price:
                    self.stop_loss = self.position.qty, sl

    def should_cancel(self) -> bool:
        return True
