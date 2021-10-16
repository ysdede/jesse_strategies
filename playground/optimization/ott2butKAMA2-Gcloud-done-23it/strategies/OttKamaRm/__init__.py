import talib
from jesse import utils
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached

import custom_indicators as cta


# Old ott2 but uses KAMA instead of VAR.
# Stoploss is still same.


class OttKamaRm(Strategy):
    def __init__(self):
        super().__init__()
        self.max_risk = 3.0

    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 2, 'max': 75, 'default': 36},  # 12
            {'name': 'ott_percent', 'type': int, 'min': 100, 'max': 800, 'default': 540},  # 540
            {'name': 'stop_loss', 'type': int, 'min': 50, 'max': 400, 'default': 122},
            {'name': 'risk_reward', 'type': int, 'min': 10, 'max': 80, 'default': 40},
            {'name': 'chop_rsi_len', 'type': int, 'min': 2, 'max': 75, 'default': 17},
            {'name': 'chop_bandwidth', 'type': int, 'min': 10, 'max': 350, 'default': 144},
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
        return self.hp['stop_loss'] / 10000

    @property
    @cached
    def RRR(self):
        return self.hp['risk_reward'] / 10

    @property
    @cached
    def ott(self):
        return cta.ott(self.candles[-960:, 2], self.ott_len, self.ott_percent, ma_type='kama', sequential=True)

    @property
    @cached
    def chop(self):
        return talib.RSI(self.candles[-960:, 2], self.hp['chop_rsi_len'])

    @property
    @cached
    def chop_upper_band(self):
        return 40 + (self.hp['chop_bandwidth'] / 10)

    @property
    @cached
    def chop_lower_band(self):
        return 60 - (self.hp['chop_bandwidth'] / 10)

    # //
    @property
    @cached
    def calc_risk_for_long(self):
        sl = self.calc_long_stop

        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((self.close - sl) / self.close)

        if (margin_risk / self.capital * 100) > self.max_risk:
            print(
                f'\nMargin Risk: {round(margin_risk)} | Capital: {round(self.capital)} | Risk % {round(margin_risk / self.capital * 100, 2)} | Price {self.close} | Stop price: {round(sl, 4)} | Stop diff: {round(self.close - sl, 4)} | Stoploss % {round((self.close - sl) / self.close * 100, 2)}')
            return False
        else:
            return True

    @property
    @cached
    def pos_size_in_usd(self):
        return self.capital / (len(get_all_trading_routes()) * 3)

    @property
    @cached
    def pos_size(self):
        return utils.size_to_qty(self.pos_size_in_usd, self.price, fee_rate=self.fee_rate) * self.leverage
    # //

    def should_long(self) -> bool:
        return self.cross_up and self.chop[-1] > self.chop_upper_band and self.calc_risk_for_long

    def should_short(self) -> bool:
        return False  # self.cross_down and self.chop[-1] < self.chop_lower_band

    def go_long(self):
        self.buy = self.pos_size, self.price

    def go_short(self):
        self.sell = self.pos_size, self.price

    @property
    @cached
    def calc_long_stop(self):
        return self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)

    @property
    @cached
    def calc_short_stop(self):
        return self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)

    def on_open_position(self, order):
        if self.is_long:
            sl = self.calc_long_stop  # self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)
            self.stop_loss = self.position.qty, sl
            tp = self.position.entry_price + (self.position.entry_price * (self.stop * self.RRR))
            self.take_profit = self.position.qty, tp

        if self.is_short:
            sl = self.calc_short_stop  # self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)
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

    def update_position(self):
        if self.is_long and self.cross_down:
            self.liquidate()
        if self.is_short and self.cross_up:
            self.liquidate()

        if True:  # Trailing stop
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
