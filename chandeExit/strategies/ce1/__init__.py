import custom_indicators as cta
from jesse import utils
from jesse.strategies import Strategy, cached


class ce1(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None

    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 1, 'max': 25, 'default': 6},
            {'name': 'ott_percent', 'type': int, 'min': 1, 'max': 400, 'default': 1},
            {'name': 'ce_atr_len', 'type': int, 'min': 1, 'max': 40, 'default': 39},
            {'name': 'ce_mult', 'type': int, 'min': 10, 'max': 50, 'default': 13},
        ]

    @property
    @cached
    def ott_len(self):
        return self.hp['ott_len']

    @property
    @cached
    def ott_percent(self):
        return self.hp['ott_percent'] / 10

    @property
    @cached
    def ott(self):
        return cta.ott(self.candles[-480:,2], self.ott_len, self.ott_percent, sequential=True)

    @property
    @cached
    def chande_exit(self):
        return cta.ce(self.candles[-480:, 3], self.candles[-480:, 4], self.candles[-480:, 2],
                      length=self.hp['ce_atr_len'], mult=self.hp['ce_mult']/10, useClose=True, sequential=False)

    @property
    @cached
    def cross_up(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='above', sequential=False)

    @property
    @cached
    def cross_down(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='below', sequential=False)

    def should_long(self) -> bool:

        # bb_ratio = cta.bbr(self.candles, 20, 'close', 2.0, True).ratio
        # short_stop = self.chande_exit.shortStop
        # chop = cta.cae(self.candles, 14, sequential=True)
        # and bb_ratio[-1] > 0.5  # and chop[-1] > 53 # and self.close > short_stop[-2]  #
        return self.cross_up

    def should_short(self) -> bool:
        # long_stop = self.chande_exit.longStop
        # bb_ratio = cta.bbr(self.candles, 20, 'close', 2.0, False).ratio
        # chop = cta.cae(self.candles, 14, sequential=False)
        # and bb_ratio < 0  # self.close < long_stop[-2] #  and self.cross_down # and chop < 40
        return self.cross_down

    @property
    @cached
    def pos_size(self):
        return (utils.size_to_qty((self.capital / 10), self.price, fee_rate=self.fee_rate) * self.leverage) + 0.001

    def go_long(self):
        self.buy = self.pos_size, self.price
        # self.trade_ts = self.candles[:, 0][-1]

    def go_short(self):
        self.sell = self.pos_size, self.price
        # self.trade_ts = self.candles[:, 0][-1]

    def on_open_position(self, order):
        if self.is_long:
            self.stop_loss = self.position.qty, self.chande_exit.longStop
            # tp = self.close * 1.035
            # self.take_profit = self.position.qty/3, tp
            # tp = self.close * 1.11
            # self.take_profit = self.position.qty / 2, tp

        if self.is_short:
            self.stop_loss = self.position.qty, self.chande_exit.shortStop
            # tp = self.ott.mavg[-1] - (self.ott.mavg[-1] * (self.stop * self.RRR))
            # self.take_profit = self.position.qty/1, self.close * 0.93

    def update_position(self):
        if self.is_long and self.cross_down:
            self.liquidate()
        if self.is_short and self.cross_up:
            self.liquidate()

        if self.is_long and self.average_stop_loss:
            # tp = self.position.entry_price + (self.position.entry_price * (self.stop * self.RRR))
            long_stop = self.chande_exit.longStop

            if long_stop > self.average_stop_loss and long_stop > self.average_entry_price:
                self.stop_loss = self.position.qty, long_stop

        if self.is_short and self.average_stop_loss:
            short_stop = self.chande_exit.shortStop

            if short_stop < self.average_stop_loss and short_stop < self.average_entry_price:
                self.stop_loss = self.position.qty, short_stop

    def should_cancel(self) -> bool:
        return True
