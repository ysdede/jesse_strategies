import numpy as np
from jesse import utils
from jesse.strategies import Strategy, cached
import talib

import custom_indicators as cta
from vars import tp_qtys
import json

# Ott Bands strategy with fixed risk allocation
# Optimized with Optuna NSGA-II
# Optuna optimization results removed. See OB5F_LS
# Exchange rules have been added. For rounding concerns, minimum quantity, quantity precision, and quote precision are used.
# Added a mechanism to liquidate remaining quantities when all take profit points are reached to eliminate any potential live/paper trading issues.
# Leverage must be to 10x!

class OB5F_LSv2(Strategy):
    def __init__(self):
        super().__init__()
        self.rules = None
        self.quantityPrecision = 6
        self.quotePrecision = 8
        self.minQty = 0.01
        self.run_once = True

        self.tps_hit_max = len(tp_qtys[0])
        self.tps_hit = 0

        self.trade_ts = None
        self.initial_qty = 0
        self.longs = 0
        self.shorts = 0

        self.fib = (0.01, 0.02, 0.03, 0.05, 0.08)

        # self.hp_l = {'ott_len': 37, 'ott_percent': 129, 'ott_bw_up': 111, 'tps_qty_index': 42, 'max_risk_long': 65}
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 111, 'tps_qty_index': 65, 'max_risk_long': 85}
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 112, 'tps_qty_index': 106, 'max_risk_long': 52}
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 111, 'tps_qty_index': 61, 'max_risk_long': 81}
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 148, 'tps_qty_index': 110, 'max_risk_long': 55}
        self.hp_l = {'ott_len': 70,
                     'ott_percent': 170,
                     'ott_bw_up': 135,
                     'tps_qty_index': 64,
                     'max_risk_long': 52}

        # 0523321840830300523
        # 0314021840210390763
        # 0325142510770340713
        # 0265242341240880743
        # 0204772181090990793
        # self.hp_s = {"ott_len": 20, "ott_percent": 477, "ott_bw_down": 218, "tps_qty_index": 51, "max_risk_short": 113, "signal_ma_len": 77}
        # self.hp_s = {"ott_len": 28, "ott_percent": 477, "ott_bw_down": 244, "tps_qty_index": 116, "max_risk_short": 75, "signal_ma_len": 59}
        # self.hp_s = {"ott_len": 26, "ott_percent": 524, "ott_bw_down": 234, "tps_qty_index": 124, "max_risk_short": 88, "signal_ma_len": 74}
        # self.hp_s = {"ott_len": 20, "ott_percent": 477, "ott_bw_down": 218, "tps_qty_index": 109, "max_risk_short": 99, "signal_ma_len": 79}
        self.hp_s = {"ott_len": 31,
                     "ott_percent": 333,
                     "ott_bw_down": 184,
                     "tps_qty_index": 51,
                     "max_risk_short": 46,
                     "signal_ma_len": 59}

    def first_run(self):
        try:
            with open('BinanceFuturesExchangeInfo.json') as f:
                data = json.load(f)

            for i in data['symbols']:
                if i['symbol'] == self.symbol.replace('-', ''):
                    self.rules = i
        except:
            print("BinanceFuturesExchangeInfo.json not found")

        if self.rules:
            self.quantityPrecision = int(self.rules['quantityPrecision'])
            self.quotePrecision = int(self.rules['quotePrecision'])
            self.minQty = float(self.rules['filters'][1]['minQty'])
            print(f"\n{self.symbol} rules set - quantityPrecision:{self.quantityPrecision}, minQty:{self.minQty}, quotePrecision:{self.quotePrecision}")

        print(f"\n{self.symbol} - {self.tps_hit_max=}")

        self.run_once = False

    @property
    def ott_len_l(self):
        return self.hp_l['ott_len']

    @property
    def ott_percent_l(self):
        return self.hp_l['ott_percent'] / 100

    @property
    def ott_len_s(self):
        return self.hp_s['ott_len']

    @property
    def ott_percent_s(self):
        return self.hp_s['ott_percent'] / 100

    @property
    def max_risk_long(self):
        return self.hp_l['max_risk_long'] / 10

    @property
    def max_risk_short(self):
        return self.hp_s['max_risk_short'] / 10

    @property
    @cached
    def ott_l(self):
        return cta.ott(self.candles[-240:, 2], self.ott_len_l, self.ott_percent_l, ma_type='kama', sequential=True)

    @property
    @cached
    def ott_s(self):
        return cta.ott(self.candles[-240:, 2], self.ott_len_s, self.ott_percent_s, ma_type='kama', sequential=True)

    @property
    @cached
    def ott_upper_band(self):
        multiplier = 1 + round((self.hp_l['ott_bw_up'] / 10000), 4)
        return np.multiply(self.ott_l.ott, multiplier)

    @property
    def cross_up_upper_band(self):
        return utils.crossed(self.ott_l.mavg, self.ott_upper_band, direction='above', sequential=False)

    @property
    def cross_down_upper_band(self):
        return utils.crossed(self.ott_l.mavg, self.ott_upper_band, direction='below', sequential=False)

    @property
    def cross_up_l(self):
        return utils.crossed(self.ott_l.mavg, self.ott_l.ott, direction='above', sequential=False)

    @property
    def cross_down_l(self):
        return utils.crossed(self.ott_l.mavg, self.ott_l.ott, direction='below', sequential=False)

    @property
    @cached
    def signal_ma_s(self):  # Just for short
        return talib.KAMA(self.candles[-240:, 2], self.hp_s['signal_ma_len'])

    @property
    def cross_up_s(self):
        return utils.crossed(self.signal_ma_s, self.ott_s.ott, direction='above', sequential=False)

    @property
    def cross_down_s(self):
        return utils.crossed(self.signal_ma_s, self.ott_s.ott, direction='below', sequential=False)

    @property
    @cached
    def ott_lower_band(self):
        multiplier = 1 - (self.hp_s['ott_bw_down'] / 10000)
        return np.multiply(self.ott_s.ott, multiplier)

    @property
    def cross_down_lower_band(self):
        return utils.crossed(self.signal_ma_s, self.ott_lower_band, direction='below', sequential=False)

    @property
    def cross_up_lower_band(self):
        return utils.crossed(self.signal_ma_s, self.ott_lower_band, direction='above', sequential=False)

    @property
    def calc_risk_for_long(self):
        sl = self.calc_long_stop
        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((self.close - sl) / self.close)
        return margin_risk / self.capital * 100 <= self.max_risk_long

    @property
    def calc_risk_for_short(self):
        sl = self.calc_short_stop
        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((abs(self.close - sl)) / self.close)
        return margin_risk / self.capital * 100 <= self.max_risk_short

    def should_long(self) -> bool:
        return self.cross_up_upper_band and self.calc_risk_for_long

    def should_short(self) -> bool:
        return self.cross_down_lower_band and self.calc_risk_for_short

    @property
    def pos_size_in_usd(self):
        return self.capital / 10

    @property
    def pos_size(self):
        qty = utils.size_to_qty(self.pos_size_in_usd,self.price, precision=self.quantityPrecision, fee_rate=self.fee_rate) * self.leverage
        return max(self.minQty, qty)

    def go_long(self):
        self.buy = self.pos_size, round(self.price, self.quotePrecision)

    def go_short(self):
        self.sell = self.pos_size, round(self.price, self.quotePrecision)

    @property
    def calc_long_stop(self):
        return round(self.ott_l.ott[-1], self.quotePrecision)

    @property
    def calc_short_stop(self):
        return round(self.ott_s.ott[-1], self.quotePrecision)

    def on_open_position(self, order):
        self.tps_hit = 0
        qty = self.position.qty
        share = self.position.qty / 10
        tps = []

        if self.is_long:
            side = 'Long'
            self.longs += 1
            sl = self.calc_long_stop

            for i in range(self.tps_hit_max):
                p = round(self.position.entry_price * (1 + self.fib[i]), self.quotePrecision)
                q = round(tp_qtys[self.hp_l['tps_qty_index']][i] * share, self.quantityPrecision + 1)
                tps.append((q, p))

        if self.is_short:
            side = 'Short'
            self.shorts += 1
            sl = self.calc_short_stop

            for i in range(self.tps_hit_max):
                p = round(self.position.entry_price * (1 - self.fib[i]), self.quotePrecision)
                q = round(tp_qtys[self.hp_s['tps_qty_index']][i] * share, self.quantityPrecision + 1)
                tps.append((q, p))

        tp4_validation = round(qty - (tps[0][0] + tps[1][0] + tps[2][0] + tps[3][0]), self.quantityPrecision + 1)
        qty_validation = round(tps[0][0] + tps[1][0] + tps[2][0] + tps[3][0] + tps[4][0], self.quantityPrecision + 1)

        print(f"\n {self.symbol} {side}, tps: {tps} {tp4_validation=}, {qty=} {qty_validation=}")

        if qty_validation != qty:
            print(f'\n {side} QTY != Sum(qtys) {qty}!={qty_validation}' * 4)

        if tp4_validation != tps[4][0]:
            print(f'\n {side} tp4 qty != validation tp4 qty {tps[4][0]}!={tp4_validation}' * 4)

        self.stop_loss = qty, sl
        self.take_profit = tps
        self.initial_qty = self.position.qty

    def on_close_position(self, order):
        self.tps_hit += 1

    def update_position(self):

        if self.is_long and self.cross_down_l:
            self.liquidate()

        if self.is_short and self.cross_up_s:
            self.liquidate()

        # Probably unnecessary Kill switch
        if self.tps_hit >= self.tps_hit_max:
            self.liquidate()
            print(f'\n{self.symbol} Kill Switch: {self.tps_hit_max} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    def watch_list(self):
        return [
            ('Symbol', self.symbol),
            ('Longs', self.longs),
            ('Shorts', self.shorts)
        ]

    def terminate(self):
        ratio = round(self.longs / (self.longs + self.shorts), 2) if self.longs > 0 else 0
        print(f"{self.symbol} - longs:{self.longs}, shorts:{self.shorts}, total:{self.longs + self.shorts}, ratio:{ratio}")

    def should_cancel(self) -> bool:
        return False

    def before(self) -> None:
        if self.run_once:
            self.first_run()
