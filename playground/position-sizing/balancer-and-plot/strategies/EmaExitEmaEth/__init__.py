import jesse.indicators as ta
from jesse import utils
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached


class EmaExitEmaEth(Strategy):
    def __init__(self):
        super().__init__()
        self.losecount = 0
        self.wincount = 0
        self.lastwasprofitable = False
        self.multiplier = 1
        self.incr = True  # Martingale-like aggressive position sizing.
        self.dpfilterenabled = True
        self.initialstop = 0
        self.laststop = 0
        self.entryprice = 0

    def hyperparameters(self):
        return [
            {'name': 'stop', 'type': int, 'min': 10, 'max': 80, 'default': 21},
            {'name': 'treshold', 'type': int, 'min': 10, 'max': 50, 'default': 38},  # / 10
            {'name': 'fast_ema', 'type': int, 'min': 3, 'max': 35, 'default': 6},
            {'name': 'slow_ema', 'type': int, 'min': 20, 'max': 50, 'default': 44},
            {'name': 'long_exit_ema', 'type': int, 'min': 5, 'max': 25, 'default': 8},
            {'name': 'short_exit_ema', 'type': int, 'min': 5, 'max': 25, 'default': 8},
        ]
        # 23: {'dna': 'ETH30m', 'tpnl': 184, 'tpnl2': 184, 'stop': 21, 'trstop': 48, 'donlen': 183, 'pmpsize': 38, 'fast': 6, 'slow': 44},  # ETH 30min

    @property
    @cached
    def long_exit_ema(self):
        return ta.ema(self.candles[-60:], period=self.hp['long_exit_ema'], source_type='low', sequential=True)

    @property
    @cached
    def short_exit_ema(self):
        return ta.ema(self.candles[-60:], period=self.hp['short_exit_ema'], source_type='high', sequential=True)

    @property
    @cached
    def exit_ema_fast(self):
        return ta.ema(self.candles[-12:], period=3, source_type='close', sequential=True)

    @property
    @cached
    def long_exit(self):
        return utils.crossed(self.exit_ema_fast, self.long_exit_ema, direction='below', sequential=False)

    @property
    @cached
    def short_exit(self):
        return utils.crossed(self.exit_ema_fast, self.short_exit_ema, direction='above', sequential=False)

    @property
    def targetstop(self):
        return self.hp['stop'] / 1000

    @property
    def pumpsize(self):
        return self.hp['treshold']

    @property
    def limit(self):
        return 4

    @property
    def carpan(self):
        return 33

    @property
    def pumplookback(self):
        return 3

    @property
    @cached
    def positionsize(self):
        return 20

    @property
    @cached
    def fast_ema(self):
        return ta.ema(self.candles[-60:], self.hp['fast_ema'], sequential=True)

    @property
    @cached
    def slow_ema(self):
        return ta.ema(self.candles[-120:], self.hp['slow_ema'], sequential=True)


    @cached
    def isdildo(self, index):
        open = self.candles[:, 1][index]
        close = self.candles[:, 2][index]
        return abs(open - close) * 100 / open > self.pumpsize / 10

    @property
    @cached
    def dumpump(self):
        open = self.candles[:, 1][-self.pumplookback]
        close = self.candles[:, 2][-1]
        multibardildo = abs(open - close) * 100 / open > self.pumpsize / 10
        return multibardildo or self.isdildo(-1) or self.isdildo(-2) or self.isdildo(-3)

    def should_long(self) -> bool:
        dp = self.dumpump
        return utils.crossed(self.fast_ema, self.slow_ema, direction='above', sequential=False) and not dp

    def should_short(self) -> bool:
        dp = self.dumpump
        return utils.crossed(self.fast_ema, self.slow_ema, direction='below', sequential=False) and not dp

    @property
    def calcqty(self):
        if self.incr and not self.lastwasprofitable and self.losecount <= self.limit:
            return (self.capital / self.positionsize) * self.multiplier

        return self.capital / self.positionsize

    def go_long(self):
        self.entryprice = self.price
        sl = self.price - (self.price * self.targetstop)

        qty = (utils.size_to_qty(self.calcqty, self.price, fee_rate=self.fee_rate) * self.leverage) + 0.001
        # print('--->', self.symbol, 'Long position size:', round(self.calcqty, 2), 'USD, Capital:', round(self.capital, 2), 'Qty:', qty)
        self.buy = qty, self.price
        self.stop_loss = qty, sl
        self.initialstop = sl
        self.laststop = sl

    def go_short(self):
        self.entryprice = self.price
        sl = self.price + (self.price * self.targetstop)

        qty = (utils.size_to_qty(self.calcqty, self.price, fee_rate=self.fee_rate) * self.leverage) + 0.001
        # print('--->', self.symbol, 'Short position size:', round(self.calcqty, 2), 'USD, Capital:', round(self.capital, 2), 'Qty:', qty)
        self.sell = qty, self.price
        self.stop_loss = qty, sl
        self.initialstop = sl
        self.laststop = sl

    def update_position(self):
        if self.is_long and self.long_exit:
            self.liquidate()

        if self.is_short and self.short_exit:
            self.liquidate()

        # if self.position.pnl_percentage / self.position.leverage > (self.targetpnl * 100):
        #     self.liquidate()

        # c. Emergency exit! Close position at trend reversal
        if utils.crossed(self.fast_ema, self.slow_ema, sequential=False):
            self.liquidate()

    def on_stop_loss(self, order):
        self.lastwasprofitable = False
        self.losecount += 1
        self.multiplier = self.multiplier * 1.66

    def on_take_profit(self, order):
        self.lastwasprofitable = True
        self.losecount = 0
        self.multiplier = 1

    def before(self):
        pass

    def should_cancel(self) -> bool:
        return True

    def on_open_position(self, order):
        pass
