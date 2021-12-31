import numpy as np
# import talib
from jesse import utils
# from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached

import custom_indicators as cta
from vars import tp_qtys

# Ott Bands strategy with fixed risk allocation
# Optimized with Optuna NSGA-II
# You can find raw optimization results in optuna_db_3, Band5min-LongOnly study
# See Results.csv for tested and picked parameters

class OB5FLong(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None
        self.initial_qty = 0
        self.fib = (0.01, 0.02, 0.03, 0.05, 0.08)
        
        # self.hp = {"max_risk_long": 52, "ott_bw_up": 149, "ott_len": 33, "ott_percent": 129, "tps_qty_index": 59}
        # self.hp = {"max_risk_long": 55, "ott_bw_up": 149, "ott_len": 33, "ott_percent": 129, "tps_qty_index": 77}
        # self.hp = {"max_risk_long": 55, "ott_bw_up": 148, "ott_len": 33, "ott_percent": 129, "tps_qty_index": 110}
        # self.hp = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 148, 'tps_qty_index': 110, 'max_risk_long': 55}
        # 40788117652 
        # 0371291110420653 
        # 0331291110610813 
        self.hp = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 111, 'tps_qty_index': 61, 'max_risk_long': 81}
        
    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 20, 'max': 55, 'default': 33},
            {'name': 'ott_percent', 'type': int, 'min': 70, 'max': 175, 'default': 129},
            {'name': 'ott_bw_up', 'type': int, 'min': 75, 'max': 125, 'default': 111},
            {'name': 'tps_qty_index', 'type': int, 'min': 60, 'max': 120, 'default': 61},
            {'name': 'max_risk_long', 'type': int, 'min': 20, 'max': 70, 'default': 81},
        ]
    
    
    @property
    def ott_len(self):
        return self.hp['ott_len']

    @property
    def ott_percent(self):
        return self.hp['ott_percent'] / 100
    
    @property
    def max_risk_long(self):
        return self.hp['max_risk_long'] / 10

    @property
    @cached
    def ott(self):
        return cta.ott(self.candles[-240:, 2], self.ott_len, self.ott_percent, ma_type='kama', sequential=True)

    @property
    @cached
    def ott_upper_band(self):
        multiplier = 1 + round((self.hp['ott_bw_up'] / 10000), 4)
        return np.multiply(self.ott.ott, multiplier)

    @property
    def cross_up_upper_band(self):
        return utils.crossed(self.ott.mavg, self.ott_upper_band, direction='above', sequential=False)

    @property
    def cross_down_upper_band(self):
        return utils.crossed(self.ott.mavg, self.ott_upper_band, direction='below', sequential=False)

    @property
    def cross_up(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='above', sequential=False)

    @property
    def cross_down(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='below', sequential=False)

    @property
    def calc_risk_for_long(self):
        sl = self.calc_long_stop
        margin_size = self.pos_size_in_usd * self.leverage
        margin_risk = margin_size * ((self.close - sl) / self.close)
        return margin_risk / self.capital * 100 <= self.max_risk_long
    

    def should_long(self) -> bool:
        return self.cross_up_upper_band and self.calc_risk_for_long

    def should_short(self) -> bool:
        return False

    @property
    def pos_size_in_usd(self):
        return self.capital / 10  # (len(get_all_trading_routes()) * 5)

    @property
    def pos_size(self):
        return utils.size_to_qty(self.pos_size_in_usd, self.price, fee_rate=self.fee_rate) * self.leverage

    def go_long(self):
        self.buy = self.pos_size, self.price

    def go_short(self):
        self.sell = self.pos_size, self.price

    @property
    def calc_long_stop(self):
        return self.ott.ott[-1]

    def on_open_position(self, order):
        # print(self.hp)
        
        if self.is_long:
            sl = self.calc_long_stop
            self.stop_loss = self.position.qty, sl

            qty = self.position.qty

            tp1_qty = qty * (tp_qtys[self.hp['tps_qty_index']][0] / 10)
            tp2_qty = qty * (tp_qtys[self.hp['tps_qty_index']][1] / 10)
            tp3_qty = qty * (tp_qtys[self.hp['tps_qty_index']][2] / 10)
            tp4_qty = qty * (tp_qtys[self.hp['tps_qty_index']][3] / 10)
            tp5_qty = qty * (tp_qtys[self.hp['tps_qty_index']][4] / 10)

            tp1_target_price = self.position.entry_price * (1 + (self.fib[0]))
            tp2_target_price = self.position.entry_price * (1 + (self.fib[1]))
            tp3_target_price = self.position.entry_price * (1 + (self.fib[2]))
            tp4_target_price = self.position.entry_price * (1 + (self.fib[3]))
            tp5_target_price = self.position.entry_price * (1 + (self.fib[4]))

            self.take_profit = [
                (tp1_qty, tp1_target_price),
                (tp2_qty, tp2_target_price),
                (tp3_qty, tp3_target_price),
                (tp4_qty, tp4_target_price),
                (tp5_qty, tp5_target_price)
            ]

        self.initial_qty = self.position.qty

    def update_position(self):
        if self.is_long and self.cross_down:  # _upper_band:
            self.liquidate()
    
    # def terminate(self):
        # print(self.hp)

        # if self.is_long and self.wt_sell:
        #     qty = (self.position.pnl_percentage / self.leverage) * (self.hp['tp_qty_multi'] / 100) * self.initial_qty
        #     if self.position.pnl > 0:
        #         self.take_profit = qty, self.price
        #
        # if self.is_short and self.wt_buy:
        #     qty = (self.position.pnl_percentage / self.leverage) * (self.hp['tp_qty_multi'] / 100) * self.initial_qty
        #     if self.position.pnl > 0:
        #         self.take_profit = qty, self.price

        # if True:  # Trailing stop
        #     if self.is_long and self.average_stop_loss:
        #         sl = self.ott.ott[-1]
        #
        #         if sl > self.average_stop_loss:  # and sl > self.average_entry_price:
        #             self.stop_loss = self.position.qty, sl
        #
        #     if self.is_short and self.average_stop_loss:
        #         sl = self.ott.ott[-1]
        #
        #         if sl < self.average_stop_loss:  # and sl < self.average_entry_price:
        #             self.stop_loss = self.position.qty, sl

    def should_cancel(self) -> bool:
        return True
