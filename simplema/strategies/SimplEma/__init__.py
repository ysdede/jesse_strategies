import jesse.indicators as ta
from jesse import utils
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached


class SimplEma(Strategy):
    def __init__(self):
        super().__init__()
        self.lose_count = 0
        self.last_was_profitable = False
        self.pump_lookback = 3
        #  !
        self.multiplier = 1
        self.carpan = 33
        self.lose_limit = 4
        self.incr = True  # Martingale-like aggressive position sizing.
        self.donchian_filter_enabled = False
        # !

    def hyperparameters(self):
        return [
            # Capital/qty_to_risk, disabled. Optimizing position size is not recommended.
            {'name': 'qty_to_risk', 'type': int, 'min': 2, 'max': 8, 'default': 5},
            # target_pnl = n/10, 153 = 15.3%
            {'name': 'target_pnl', 'type': int, 'min': 25, 'max': 400, 'default': 153},
            # stoploss = n/1000, 172 = 17.2%
            {'name': 'stop', 'type': int, 'min': 10, 'max': 190, 'default': 172},
            # Donchian Channel Length
            {'name': 'donchlen', 'type': int, 'min': 8, 'max': 200, 'default': 81},
            # Dump/pump treshold level, n/10, 23 = 2.3%
            {'name': 'treshold', 'type': int, 'min': 20, 'max': 100, 'default': 23},
            {'name': 'ema_fast', 'type': int, 'min': 2, 'max': 20, 'default': 8},
            {'name': 'ema_slow', 'type': int, 'min': 21, 'max': 50, 'default': 22},
        ]

    @property
    def stop(self):
        return self.hp['stop'] / 1000

    @property
    def treshold(self):
        return self.hp['treshold'] / 10

    @property
    def target_pnl(self):
        return self.hp['target_pnl'] / 10

    @property
    def entry_donchian(self):
        return ta.donchian(self.candles, self.hp['donchlen'], sequential=False)

    def is_dp(self, index):
        open = self.candles[:, 1][index]
        close = self.candles[:, 2][index]
        return abs(open - close) * 100 / open > self.treshold

    @property
    def dump_pump(self):
        open = self.candles[:, 1][-self.pump_lookback]
        close = self.candles[:, 2][-1]
        multibar_dp = abs(open - close) * 100 / open > self.treshold
        return self.is_dp(-1) or self.is_dp(-2) or self.is_dp(-3) or multibar_dp

    @property
    @cached
    def slow_ema(self):
        return ta.ema(self.candles, self.hp['ema_slow'], sequential=True)

    @property
    @cached
    def fast_ema(self):
        return ta.ema(self.candles, self.hp['ema_fast'], sequential=True)

    def should_long(self) -> bool:
        dc = True
        if self.donchian_filter_enabled:
            dc = self.close >= self.entry_donchian[1]
        return utils.crossed(self.fast_ema, self.slow_ema, direction='above',
                             sequential=False) and not self.dump_pump and dc

    def should_short(self) -> bool:
        dc = True
        if self.donchian_filter_enabled:
            dc = self.close <= self.entry_donchian[1]
        return utils.crossed(self.fast_ema, self.slow_ema, direction='below',
                             sequential=False) and not self.dump_pump and dc

    @property
    def pos_size(self):
        # self.hp['qty_to_risk'] qty_to_risk parameter disabled. Optimizing position size is not recommended.
        ps = 10 * len(get_all_trading_routes())  # 15 x Number of routes

        if not self.last_was_profitable and self.lose_count <= self.lose_limit:
            return (self.capital / ps) * self.multiplier
        return self.capital / ps

    def go_long(self):
        sl = self.stop
        qty = (utils.size_to_qty(self.pos_size, self.price, fee_rate=self.fee_rate) * self.leverage) + 0.001
        self.buy = qty, self.price
        self.stop_loss = qty, self.price - (self.price * sl)

    def go_short(self):
        sl = self.stop
        qty = (utils.size_to_qty(self.pos_size, self.price, fee_rate=self.fee_rate) * self.leverage) + 0.001
        self.sell = qty, self.price
        self.stop_loss = qty, self.price + (self.price * sl)

    def update_position(self):
        # Take profit when hit!
        if self.position.pnl_percentage / self.position.leverage > self.target_pnl:
            self.liquidate()

        # Emergency exit! Close position at trend reversal
        if utils.crossed(self.fast_ema, self.slow_ema, sequential=False):
            self.liquidate()

    def on_stop_loss(self, order):
        self.last_was_profitable = False
        self.lose_count += 1
        self.multiplier = self.multiplier * (1 + (self.carpan / 50))

    def on_take_profit(self, order):
        self.last_was_profitable = True
        self.lose_count = 0
        self.multiplier = 1

    def before(self):
        pass

    def should_cancel(self) -> bool:
        return True

    def on_open_position(self, order):
        pass
