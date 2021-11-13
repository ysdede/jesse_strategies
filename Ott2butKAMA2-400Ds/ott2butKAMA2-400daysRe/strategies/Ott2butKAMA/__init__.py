import talib
from jesse import utils
from jesse.strategies import Strategy, cached

import custom_indicators as cta


class Ott2butKAMA(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None

    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 55, 'max': 75, 'default': 69},
            {'name': 'ott_percent', 'type': int, 'min': 180, 'max': 210, 'default': 189},
            {'name': 'stop_loss', 'type': int, 'min': 130, 'max': 240, 'default': 232},
            {'name': 'risk_reward', 'type': int, 'min': 30, 'max': 80, 'default': 40},
            {'name': 'chop_bandwidth', 'type': int, 'min': 160, 'max': 320, 'default': 290},
        ]

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
        return cta.ott(self.candles[-480:, 2], self.ott_len, self.ott_percent, ma_type='kama', sequential=True)

    @property
    @cached
    def chop(self):
        return talib.RSI(self.candles[-240:, 2], 14)
        # return jta.rsi(self.candles[-240:, 2], self.hp['chop_rsi_len'], sequential=True)
        # return cta.cae(self.candles[-240:, 2], self.hp['chop_rsi_len'], sequential=True)

    @property
    @cached
    def chop_upper_band(self):
        return 40 + (self.hp['chop_bandwidth'] / 10)

    @property
    @cached
    def chop_lower_band(self):
        return 60 - (self.hp['chop_bandwidth'] / 10)

    def should_long(self) -> bool:
        return self.cross_up and self.chop[-1] > self.chop_upper_band

    def should_short(self) -> bool:
        return False  # self.cross_down and self.chop[-1] < self.chop_lower_band

    @property
    @cached
    def pos_size(self):
        return utils.size_to_qty((self.capital / 10), self.price, fee_rate=self.fee_rate) * self.leverage  # + 0.001

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
            tp = self.position.entry_price + (self.position.entry_price * (self.stop * self.RRR))
            self.take_profit = self.position.qty, tp

        if self.is_short:
            sl = self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)
            self.stop_loss = self.position.qty, sl
            tp = self.position.entry_price - (self.position.entry_price * (self.stop * self.RRR))
            self.take_profit = self.position.qty, tp

    @property
    @cached
    def cross_up(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='above', sequential=False)

    @property
    @cached
    def cross_down(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='below', sequential=False)

    def update_position(self):  # sourcery skip: merge-nested-ifs
        if self.is_long:
            if self.cross_down:
                self.liquidate()
        if self.is_short:
             if self.cross_up:
                self.liquidate()

        # if True:  # Trailing stop
        #     if self.is_long and self.average_stop_loss:
        #         sl = self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)
        #
        #         if sl > self.average_stop_loss and sl > self.average_entry_price:
        #             self.stop_loss = self.position.qty, sl
        #
        #     if self.is_short and self.average_stop_loss:
        #         sl = self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)
        #
        #         if sl < self.average_stop_loss and sl < self.average_entry_price:
        #             self.stop_loss = self.position.qty, sl

    def should_cancel(self) -> bool:
        return True
