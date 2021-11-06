import custom_indicators as cta
import numpy as np
from jesse import utils
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached
from vars import tp_qtys


class OttBands1min(Strategy):
    def __init__(self):
        super().__init__()
        # self.profit_levels = (0.01, 0.02, 0.03, 0.05, 0.08)
        # self.profit_levels = (0.01, 0.02, 0.04, 0.08, 0.16)
        self.profit_levels = (0.005, 0.01, 0.02, 0.04, 0.08)
        self.ott_ma_type = 'kama'

    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 2, 'max': 52, 'default': 18},
            {'name': 'ott_percent', 'type': int, 'min': 10, 'max': 310, 'default': 200},
            {'name': 'ott_bw', 'type': int, 'min': 10, 'max': 400, 'default': 80},
            {'name': 'tps_qty_index', 'type': int, 'min': 0, 'max': 1000, 'default': 241},
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
    def ott(self):
        return cta.ott(self.candles[-240:, 2], self.ott_len, self.ott_percent, ma_type=self.ott_ma_type, sequential=True)

    @property
    @cached
    def ott_upper_band(self):
        multiplier = 1 + (self.hp['ott_bw'] / 10000)
        return np.multiply(self.ott.ott, multiplier)

    @property
    @cached
    def ott_lower_band(self):
        multiplier = 1 - (self.hp['ott_bw'] / 10000)
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
    def pos_size_in_usd(self):
        return self.capital / 10  # (len(get_all_trading_routes()) * 2)

    @property
    @cached
    def calc_long_stop(self):
        return self.ott.ott[-1]

    @property
    @cached
    def calc_short_stop(self):
        return self.ott.ott[-1]

    def should_long(self) -> bool:
        return self.cross_up_upper_band

    def should_short(self) -> bool:
        return self.cross_down_lower_band

    @property
    @cached
    def pos_size(self):
        return utils.size_to_qty(self.pos_size_in_usd, self.price, fee_rate=self.fee_rate) * self.leverage

    def go_long(self):
        self.buy = self.pos_size, self.price

    def go_short(self):
        self.sell = self.pos_size, self.price

    def on_open_position(self, order):
        qty = self.position.qty

        tps = []
        qty_curve = tp_qtys[self.hp['tps_qty_index']]

        if self.is_long:
            # sl = self.calc_long_stop
            # self.stop_loss = self.position.qty, sl

            for index, _qty in enumerate(qty_curve):
                if _qty > 0:
                    tps.append(
                        ((qty * _qty), self.position.entry_price * (1 + (self.profit_levels[index]))))

        if self.is_short:
            # sl = self.calc_short_stop
            # self.stop_loss = self.position.qty, sl

            for index, _qty in enumerate(qty_curve):
                if _qty > 0:
                    tps.append(
                        ((qty * _qty), self.position.entry_price * (1 - (self.profit_levels[index]))))

        self.take_profit = tps

    @cached
    def update_position(self):
        if self.is_long and self.cross_down:  # _upper_band:
            self.liquidate()

        if self.is_short and self.cross_up:  # self.cross_up_lower_band:
            self.liquidate()

    def should_cancel(self) -> bool:
        return True
