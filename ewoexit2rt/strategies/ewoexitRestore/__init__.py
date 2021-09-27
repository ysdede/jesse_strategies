import jesse.indicators as ta
from jesse import utils
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached


class ewoexitRestore(Strategy):
    def __init__(self):
        super().__init__()
        self.chop_filter_enabled = True

    def hyperparameters(self):
        return [
            {'name': 'stop', 'type': int, 'min': 10, 'max': 80, 'default': 24},
            {'name': 'treshold', 'type': int, 'min': 10, 'max': 50, 'default': 17},
            {'name': 'ewoshort', 'type': int, 'min': 3, 'max': 30, 'default': 26},
            {'name': 'ewolong', 'type': int, 'min': 20, 'max': 60, 'default': 45},
            {'name': 'chop_rsi', 'type': int, 'min': 2, 'max': 30, 'default': 7},
            {'name': 'chop_band_width', 'type': int, 'min': 1, 'max': 150, 'default': 103},
            {'name': 'trend_ema_len', 'type': int, 'min': 3, 'max': 163, 'default': 54},
            {'name': 'exit_ema_fast', 'type': int, 'min': 2, 'max': 10, 'default': 7},
            {'name': 'exit_ema_slow', 'type': int, 'min': 20, 'max': 250, 'default': 52},
        ]

    @property
    @cached
    def spotcandles(self):
        spot_candles = self.get_candles(self.exchange, self.symbol, '1h')
        return spot_candles[:, 2]

    @property
    @cached
    def chop(self):
        return ta.rsi(self.candles, self.hp['chop_rsi'], sequential=True)

    @property
    @cached
    def qtytorisk(self):
        if len(get_all_trading_routes()) < 3:
            return 20 * len(get_all_trading_routes())
        else:
            return 8 * len(get_all_trading_routes())

    @property
    @cached
    def stop(self):
        return self.hp['stop'] / 1000

    @property
    @cached
    def treshold(self):
        return self.hp['treshold'] / 10

    @property
    @cached
    def fast_ema(self):
        return ta.ema(self.candles, self.hp['ewoshort'], sequential=True)

    @property
    @cached
    def slow_ema(self):
        return ta.ema(self.candles, self.hp['ewolong'], sequential=True)

    @property
    @cached
    def exit_fast_ema(self):
        return ta.ema(self.candles, self.hp['exit_ema_fast'], sequential=True)

    @property
    @cached
    def exit_slow_ema(self):
        return ta.ema(self.candles, self.hp['exit_ema_slow'], sequential=True)

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
                             sequential=False) and chop_filter and self.close > self.trend_ema and not self.dumpump

    def should_short(self) -> bool:
        chop_filter = True
        if self.chop_filter_enabled:
            chop_filter = self.chop[-1] < 50 - (self.hp['chop_band_width'] / 10)
        return utils.crossed(self.fast_ema, self.slow_ema, direction='below',
                             sequential=False) and chop_filter and self.close < self.trend_ema and not self.dumpump

    @property
    def calculatepositionsize(self):
        return self.capital / self.qtytorisk

    def go_long(self):
        sl = self.stop
        qty = utils.size_to_qty(self.calculatepositionsize, self.price, fee_rate=self.fee_rate) * self.leverage + 0.005
        self.buy = qty, self.price
        self.stop_loss = qty, self.price - (self.price * sl)

    def go_short(self):
        sl = self.stop
        qty = utils.size_to_qty(self.calculatepositionsize, self.price, fee_rate=self.fee_rate) * self.leverage + 0.005
        self.sell = qty, self.price
        self.stop_loss = qty, self.price + (self.price * sl)

    def update_position(self):
        if self.is_long and utils.crossed(self.exit_fast_ema, self.exit_slow_ema, direction='below', sequential=False):
            self.liquidate()

        if self.is_short and utils.crossed(self.exit_fast_ema, self.exit_slow_ema, direction='above', sequential=False):
            self.liquidate()

    def before(self):
        pass

    def should_cancel(self) -> bool:
        return True

    def on_open_position(self, order):
        pass
