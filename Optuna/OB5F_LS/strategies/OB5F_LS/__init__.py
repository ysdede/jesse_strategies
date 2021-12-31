import numpy as np
# import talib
from jesse import utils
# from jesse.services.selectors import get_all_trading_routes
from jesse.strategies import Strategy, cached
import talib

import custom_indicators as cta
from vars import tp_qtys

# Ott Bands strategy with fixed risk allocation
# Optimized with Optuna NSGA-II
# You can find raw optimization results in optuna_db_3, Band5min-LongOnly study
# See Results.csv for tested and picked parameters

class OB5F_LS(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None
        self.initial_qty = 0
        self.longs = 0
        self.shorts = 0
        
        self.fib = (0.01, 0.02, 0.03, 0.05, 0.08)
        
        # self.hp = {"max_risk_long": 52, "ott_bw_up": 149, "ott_len": 33, "ott_percent": 129, "tps_qty_index": 59}
        # self.hp = {"max_risk_long": 55, "ott_bw_up": 149, "ott_len": 33, "ott_percent": 129, "tps_qty_index": 77}
        # self.hp = {"max_risk_long": 55, "ott_bw_up": 148, "ott_len": 33, "ott_percent": 129, "tps_qty_index": 110}
        # self.hp = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 148, 'tps_qty_index': 110, 'max_risk_long': 55}
        # 40788117652 
        # 0371291110420653 
        # 0331291110610813 
        # 0331291121060523
        # 0371291110420653 
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 148, 'tps_qty_index': 110, 'max_risk_long': 55}
        
        # 0701701350640523
        self.hp_l = {'ott_len': 70, 'ott_percent': 170, 'ott_bw_up': 135, 'tps_qty_index': 64, 'max_risk_long': 52}  # Yeni favori
        
        # self.hp_l = {'ott_len': 37, 'ott_percent': 129, 'ott_bw_up': 111, 'tps_qty_index': 42, 'max_risk_long': 65}  # Canlıda kullanılmış
        
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 111, 'tps_qty_index': 65, 'max_risk_long': 85}
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 112, 'tps_qty_index': 106, 'max_risk_long': 52}
        # self.hp_l = {'ott_len': 33, 'ott_percent': 129, 'ott_bw_up': 111, 'tps_qty_index': 61, 'max_risk_long': 81}
        # 020 477 218 051 113 077 3
        # self.hp_s = {"ott_len": 20, "ott_percent": 477, "ott_bw_down": 218, "tps_qty_index": 51, "max_risk_short": 113, "signal_ma_len": 77}  # yeni
        # self.hp_s = {"ott_len": 28, "ott_percent": 477, "ott_bw_down": 244, "tps_qty_index": 116, "max_risk_short": 75, "signal_ma_len": 59}  # yeni 028 477 244 116 075 059 3 0284772441160750593
        # self.hp_s = {"ott_len": 26, "ott_percent": 524, "ott_bw_down": 234, "tps_qty_index": 124, "max_risk_short": 88, "signal_ma_len": 74}  # yeni 1 -  0265242341240880743 
        self.hp_s = {"ott_len": 31, "ott_percent": 333, "ott_bw_down": 184, "tps_qty_index": 51, "max_risk_short": 46, "signal_ma_len": 59}     # 0313331840510460593 Son Fav
        
        # 0523321840830300523 DENE
        # 0314021840210390763 dene
        # dene 0325142510770340713
        # 0265242341240880743 dene
        
        
        # 0204772181090990793
        # self.hp_s = {"ott_len": 20, "ott_percent": 477, "ott_bw_down": 218, "tps_qty_index": 109, "max_risk_short": 99, "signal_ma_len": 79}
        
    def hyperparameters(self):
        return [
            {'name': 'ott_len', 'type': int, 'min': 20, 'max': 55, 'default': 33},
            {'name': 'ott_percent', 'type': int, 'min': 70, 'max': 175, 'default': 129},
            {'name': 'ott_bw_up', 'type': int, 'min': 75, 'max': 125, 'default': 111},
            {'name': 'tps_qty_index', 'type': int, 'min': 60, 'max': 120, 'default': 61},
            {'name': 'max_risk_long', 'type': int, 'min': 20, 'max': 70, 'default': 81},
        ]
    
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
    
    # Short
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
        # print(self.hp)
        return self.cross_down_lower_band and self.calc_risk_for_short

    @property
    def pos_size_in_usd(self):
        return self.capital / 10  # (len(get_all_trading_routes()) * 5)

    @property
    def pos_size(self):
        return utils.size_to_qty(self.pos_size_in_usd, self.price, fee_rate=self.fee_rate) * self.leverage

    def go_long(self):
        self.buy = round(self.pos_size + 0.001, 4) * 2, self.price

    def go_short(self):
        self.sell = round(self.pos_size + 0.001, 4) * 2, self.price

    @property
    def calc_long_stop(self):
        return self.ott_l.ott[-1]
    
    @property
    def calc_short_stop(self):
        return self.ott_s.ott[-1]

    def on_open_position(self, order):
        # print(self.hp)
        
        if self.is_long:
            self.longs += 1
            sl = self.calc_long_stop
            self.stop_loss = self.position.qty, sl

            qty = self.position.qty

            tp1_qty = qty * (tp_qtys[self.hp_l['tps_qty_index']][0] / 10)
            tp2_qty = qty * (tp_qtys[self.hp_l['tps_qty_index']][1] / 10)
            tp3_qty = qty * (tp_qtys[self.hp_l['tps_qty_index']][2] / 10)
            tp4_qty = qty * (tp_qtys[self.hp_l['tps_qty_index']][3] / 10)
            tp5_qty = qty * (tp_qtys[self.hp_l['tps_qty_index']][4] / 10)

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
            
        if self.is_short:
            self.shorts += 1
            self.stop_loss = self.position.qty, self.calc_short_stop

            qty = self.position.qty

            tp1_qty = qty * (tp_qtys[self.hp_s['tps_qty_index']][0] / 10)
            tp2_qty = qty * (tp_qtys[self.hp_s['tps_qty_index']][1] / 10)
            tp3_qty = qty * (tp_qtys[self.hp_s['tps_qty_index']][2] / 10)
            tp4_qty = qty * (tp_qtys[self.hp_s['tps_qty_index']][3] / 10)
            tp5_qty = qty * (tp_qtys[self.hp_s['tps_qty_index']][4] / 10)

            tp1_target_price = self.position.entry_price * (1 - (self.fib[0]))
            tp2_target_price = self.position.entry_price * (1 - (self.fib[1]))
            tp3_target_price = self.position.entry_price * (1 - (self.fib[2]))
            tp4_target_price = self.position.entry_price * (1 - (self.fib[3]))
            tp5_target_price = self.position.entry_price * (1 - (self.fib[4]))

            self.take_profit = [
                (tp1_qty, tp1_target_price),
                (tp2_qty, tp2_target_price),
                (tp3_qty, tp3_target_price),
                (tp4_qty, tp4_target_price),
                (tp5_qty, tp5_target_price)
            ]

        self.initial_qty = self.position.qty

    def update_position(self):
        # if self.is_long and self.cross_down_lower_band and self.calc_risk_for_short:
        #     print(f"{self.symbol} should short")
            
        if self.is_long and self.cross_down_l:  # _upper_band:
            self.liquidate()
            
        # if self.is_short and self.cross_up_upper_band and self.calc_risk_for_long:
        #     print(f"\n{self.symbol} should long")

        if self.is_short and self.cross_up_s:  # self.cross_up_lower_band:
            self.liquidate()
    
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
