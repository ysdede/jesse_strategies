import jesse.helpers as jh
import jesse.indicators as ta
from jesse import utils
from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached


class emacounter(Strategy):

    def __init__(self):
        super().__init__()
        self.losecount = 0
        self.wincount = 0
        self.winlimit = 2
        self.lastwasprofitable = False
        self.multiplier = 1
        self.incr = True  # Martingale-like aggressive position sizing.
        self.donchianfilterenabled = False
        self.skipenabled = False  # If last trade was profitable, skip next trade.
        self.enablelong = True
        self.enableshort = True
        self.settp = False
        self.dnaindex = 23
        self.initialstop = 0
        self.laststop = 0
        self.entryprice = 0
        self.enabletrailingstop = False
        self.dpfilterenabled = True
        self.enablemanualstop = False
        self.atrlen = 12
        self.atrstop = 0.85
        self.firstrun = True
        self.days = 0
        self.green_count = 4
        self.red_count = 4
        self.long_start = None
        self.short_start = None
        self.trend_long = False
        self.trend_short = False
        self.long_exit_start = 0
        self.short_exit_start = 0
        self.trend_long_exit = False
        self.trend_short_exit = False

        self.dnas = {
            1: {'dna': 'vaJpC;g', 'tpnl': 296, 'stop': 87, 'donlen': 183, 'pmpsize': 47, 'fast': 6, 'slow': 44},
            2: {"dna": 'vaJpp;g', "tpnl": 296, 'tpnl2': 296, "stop": 87, "donlen": 183, "pmpsize": 93, "fast": 6,
                "slow": 44},
            21: {'dna': 'BTC2h', 'tpnl': 296, 'tpnl2': 296, 'stop': 24, 'trstop': 48, 'donlen': 183, 'pmpsize': 47,
                 'fast': 6, 'slow': 44},
            22: {'dna': 'BNB30min', 'tpnl': 96, 'tpnl2': 96, 'stop': 18, 'trstop': 68, 'donlen': 183, 'pmpsize': 38,
                 'fast': 6, 'slow': 44},  # BNB 30min
            23: {'dna': 'ETH30m', 'tpnl': 184, 'tpnl2': 184, 'stop': 34, 'trstop': 48, 'donlen': 183, 'pmpsize': 38,
                 'fast': 6, 'slow': 44},  # ETH 30min
            25: {"dna": 'ADA', "tpnl": 130, 'tpnl2': 296, "stop": 51, "donlen": 183, "pmpsize": 32, "fast": 6,
                 "slow": 44},
            255: {"dna": 'Generic', "tpnl": 120, 'tpnl2': 296, "stop": 51, "donlen": 183, "pmpsize": 32, "fast": 6,
                  "slow": 44},
            7: {"dna": 'v^JpF/g', "tpnl": 281, "stop": 87, "donlen": 183, "pmpsize": 50, "fast": 4, "slow": 44},
            16: {"dna": 'vj3?o1l', "tpnl": 338, "stop": 35, "donlen": 64, "pmpsize": 92, "fast": 4, "slow": 46},
            # ada periyodu ve pmp işe yarar
            18: {"dna": 'vaQpJ;g', "tpnl": 296, "stop": 103, "donlen": 183, "pmpsize": 54, "fast": 6, "slow": 44},
            20: {"dna": 'vahpJ;g', "tpnl": 296, "stop": 156, "donlen": 183, "pmpsize": 54, "fast": 6, "slow": 44},
            3: {"dna": 'vXJp.._', "tpnl": 253, "stop": 87, "donlen": 183, "pmpsize": 26, "fast": 3, "slow": 41},
            4: {"dna": 'vXJp5._', "tpnl": 253, "stop": 87, "donlen": 183, "pmpsize": 33, "fast": 3, "slow": 41},
            5: {"dna": 'sYon51`', "tpnl": 258, "stop": 172, "donlen": 178, "pmpsize": 33, "fast": 4, "slow": 42},
            6: {"dna": 'vdfp5.)', "tpnl": 310, "stop": 151, "donlen": 183, "pmpsize": 33, "fast": 3, "slow": 21},
            61: {"dna": 'TRX', "tpnl": 290, "stop": 28, "donlen": 183, "pmpsize": 33, "fast": 3, "slow": 21},
            8: {"dna": 'vY\\n51`', "tpnl": 258, "stop": 128, "donlen": 178, "pmpsize": 33, "fast": 4, "slow": 42},
            9: {"dna": 'Z^JpF/Y', "tpnl": 281, "stop": 87, "donlen": 183, "pmpsize": 50, "fast": 4, "slow": 39},
            10: {"dna": 'kd9?;1H', "tpnl": 310, "stop": 49, "donlen": 64, "pmpsize": 39, "fast": 4, "slow": 33},
            11: {"dna": 'vdfp5@l', "tpnl": 310, "stop": 151, "donlen": 183, "pmpsize": 33, "fast": 7, "slow": 46},
            # ada 2h periyodu işe yarayabilir
            111: {"dna": 'vdfp5@l', "tpnl": 290, "stop": 28, "donlen": 183, "pmpsize": 33, "fast": 7, "slow": 46},
            12: {"dna": 'vdds59l', "tpnl": 310, "stop": 147, "donlen": 190, "pmpsize": 33, "fast": 6, "slow": 46},
            13: {"dna": 'vVJ/2._', "tpnl": 243, "stop": 87, "donlen": 25, "pmpsize": 30, "fast": 3, "slow": 41},
            14: {"dna": 'vN3BO,f', "tpnl": 205, "stop": 35, "donlen": 71, "pmpsize": 59, "fast": 3, "slow": 44},
            15: {"dna": 'vdos5>l', "tpnl": 310, "stop": 172, "donlen": 190, "pmpsize": 33, "fast": 7, "slow": 46},
            17: {"dna": 'vqopR,]', "tpnl": 372, "stop": 172, "donlen": 183, "pmpsize": 63, "fast": 3, "slow": 40},
            19: {"dna": 'v^JpF/U', "tpnl": 281, "stop": 87, "donlen": 183, "pmpsize": 50, "fast": 4, "slow": 38},
            191: {"dna": 'v^JpF/U', "tpnl": 140, "stop": 70, "donlen": 183, "pmpsize": 43, "fast": 7, "slow": 46},
            24: {'dna': 'BTC2h', 'tpnl': 296, 'tpnl2': 296, 'stop': 24, 'trstop': 48, 'donlen': 183, 'pmpsize': 47,
                 'fast': 6, 'slow': 44},
            999: {"dna": 'vdos5>l', "tpnl": 310, "stop": 172, "donlen": 190, "pmpsize": 33, "fast": 7, "slow": 46},
            # 22: {'dna': 'BNB30min', 'tpnl': 96, 'stop': 20, 'trstop': 68, 'donlen': 183, 'pmpsize': 38, 'fast': 6, 'slow': 44}, # BNB 30min
        }

    @property
    def targetpnl(self):
        return self.dnas[self.dnaindex]['tpnl'] / 1000

    @property
    def targetstop(self):
        return self.dnas[self.dnaindex]['stop'] / 1000

    @property
    def pumpsize(self):
        return self.dnas[self.dnaindex]['pmpsize']

    @property
    def ewofast(self):
        return self.dnas[self.dnaindex]['fast']

    @property
    def ewoslow(self):
        return self.dnas[self.dnaindex]['slow']

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
        if (
            len(get_all_trading_routes()) < 3
            or len(get_all_trading_routes()) >= 3
            and self.symbol.startswith('ETH-')
        ):
            return 10 * len(get_all_trading_routes())
        else:
            return 16 * len(get_all_trading_routes())

    @property
    @cached
    def slow_ema(self):
        return ta.ema(self.candles[-120:], self.ewoslow, sequential=True)

    @property
    @cached
    def fast_ema(self):
        return ta.ema(self.candles[-60:], self.ewofast, sequential=True)


    @property
    @cached
    def ema_exit_hl2(self):
        return ta.ema(self.candles[-120:], period=30, source_type='hl2', sequential=False)


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
        dp = self.dumpump if self.dpfilterenabled else False
        if utils.crossed(self.fast_ema, self.slow_ema, direction='above', sequential=False):
            self.long_start = self.candles[:, 0][-1]
            self.trend_long = True
            self.green_count += 1

            self.short_start = None
            self.trend_short = False
            self.red_count = 0

        if self.trend_long and self.candles[:, 0][-1] != self.long_start and self.fast_ema[-1] > self.slow_ema[-1]:
            self.green_count += 1
        if self.trend_long and self.trend_short:
            print('LONG & SHORT!')

        return self.trend_long and self.green_count > 1

    def should_short(self) -> bool:
        if utils.crossed(self.fast_ema, self.slow_ema, direction='below', sequential=False):
            self.short_start = self.candles[:, 0][-1]
            self.trend_short = True
            self.red_count += 1

            self.long_start = None
            self.trend_long = False
            self.green_count = 0

        if self.trend_short and self.candles[:, 0][-1] != self.short_start and self.fast_ema[-1] < self.slow_ema[-1]:
            self.red_count += 1
        return self.trend_short and self.red_count > 1

    @property
    def calcqty(self):
        if self.incr and not self.lastwasprofitable and self.losecount <= self.limit:
            return (self.capital / self.positionsize) * self.multiplier

        return self.capital / self.positionsize

    def go_long(self):
        self.entryprice = self.price
        sl = self.price - (self.price * self.targetstop)
        tp = self.price + (self.price * self.targetpnl)

        qty = (utils.size_to_qty(self.calcqty, self.price, fee_rate=self.fee_rate) * self.leverage) + 0.005
        # print('--->', self.symbol, 'Long position size:', round(self.calcqty, 2), 'USD, Capital:', round(self.capital, 2), 'Qty:', qty)
        self.buy = qty, self.price

        if not self.enablemanualstop:
            self.stop_loss = qty, sl

        if self.settp:
            self.take_profit = qty, tp

        self.initialstop = sl
        self.laststop = sl

    def go_short(self):
        self.entryprice = self.price
        sl = self.price + (self.price * self.targetstop)
        tp = self.price - (self.price * self.targetpnl)

        qty = (utils.size_to_qty(self.calcqty, self.price, fee_rate=self.fee_rate) * self.leverage) + 0.005
        # print('--->', self.symbol, 'Short position size:', round(self.calcqty, 2), 'USD, Capital:', round(self.capital, 2), 'Qty:', qty)
        self.sell = qty, self.price

        if not self.enablemanualstop:
            self.stop_loss = qty, sl

        if self.settp:
            self.take_profit = qty, tp

        self.initialstop = sl
        self.laststop = sl

    def update_position(self):
        if self.position.pnl_percentage / self.position.leverage > (self.targetpnl * 100):
            self.liquidate()

        if self.is_long and utils.crossed(self.fast_ema, self.slow_ema, direction='below', sequential=False) and not self.trend_long_exit:
            self.long_exit_start = self.candles[:, 0][-1]
            self.trend_long_exit = True
            self.red_count += 1

        if self.trend_long_exit and self.candles[:, 0][-1] != self.long_exit_start and self.fast_ema[-1] < self.slow_ema[-1]:
            self.red_count += 1

        if self.trend_long_exit and self.red_count > 1:
            self.liquidate()
        # --------------------
        if self.is_short and utils.crossed(self.fast_ema, self.slow_ema, direction='above', sequential=False) and not self.trend_short_exit:
            self.short_exit_start = self.candles[:, 0][-1]
            self.trend_short_exit = True
            self.green_count += 1

        if self.trend_short_exit and self.candles[:, 0][-1] != self.short_exit_start and self.fast_ema[-1] > self.slow_ema[-1]:
            self.green_count += 1

        if self.trend_short_exit and self.green_count > 1:
            self.liquidate()

        print('\n', jh.timestamp_to_time(self.candles[:, 0][-1]), 'Trend long', self.trend_long, 'Trend short', self.trend_short, 'greens:',
                  self.green_count, 'reds:', self.red_count,  ' | L/S', self.is_long, self.is_short)

        if self.is_long and self.close < self.ema_exit_hl2:
            self.liquidate()

        if self.is_short and self.close > self.ema_exit_hl2:
            self.liquidate()

        # c. Emergency exit! Close position at trend reversal
        if utils.crossed(self.fast_ema, self.slow_ema, sequential=False):
            pass
            # self.liquidate()


    def on_stop_loss(self, order):
        self.lastwasprofitable = False
        self.losecount += 1
        self.wincount = 0
        self.multiplier = self.multiplier * (1 + (self.carpan / 50))

    def on_take_profit(self, order):
        self.lastwasprofitable = True
        self.wincount += 1
        self.losecount = 0
        self.multiplier = 1

    def before(self):
        if self.firstrun:
            self.runonce()

    def runonce(self):
        if self.symbol.startswith('BTC'):
            self.dnaindex = 21
        if self.symbol.startswith('BNB'):
            self.dnaindex = 22
        if self.symbol.startswith('ETH'):
            self.dnaindex = 23
        if self.symbol.startswith('TRX-'):
            self.dnaindex = 999  # 6
        if self.symbol.startswith('ADA-'):
            self.dnaindex = 25
        if self.symbol.startswith('LTC-'):
            self.dnaindex = 19
        if self.symbol.startswith('NEO-'):
            self.dnaindex = 8
        if self.symbol.startswith('XRP-'):
            self.dnaindex = 12
        if self.symbol.startswith('QTUM-'):
            self.dnaindex = 15
        # print('\nFirst run!', self.symbol, 'Dna index: ', self.dnaindex)
        self.firstrun = False

    def should_cancel(self) -> bool:
        return True

    def on_open_position(self, order):
        self.long_start = None
        self.trend_long = False
        self.green_count = 0

        self.short_start = None
        self.trend_short = False
        self.red_count = 0

        self.trend_short_exit = False
        self.trend_long_exit = False

        self.long_exit_start = 0
        self.short_exit_start = 0
