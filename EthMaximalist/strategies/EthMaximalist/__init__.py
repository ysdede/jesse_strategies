import custom_indicators as cta
import talib
from jesse import utils
from jesse.strategies import Strategy, cached


class EthMaximalist(Strategy):
    """ A Long only Jesse strategy makes profits from reversals.
    Inherited from Ott2butKAMARe3
    Backtest 2020-02-15 -> 2021-11-15

    Event           Count   Mean %      Total USDT
    Stoploss        4       -18.055     -117240
    Take profit     3       92.234      158436
    Trend reversal  122     4.281       1017463

    Position size increased to match benchmark's drawdown.
    See 'pos_size_usd' method.

    Args:
        See Readme.md for more info
    """

    def __init__(self):
        super().__init__()
        self.kasa = None
        self.is_reversal = False

        self.stop_losses = []
        self.take_profits = []
        self.reversals = []

        self.sl_in_usd = 0.0
        self.tp_in_usd = 0.0
        self.revs_in_usd = 0.0
        self.log_enabled = False

        # Parameters
        self.ott_len = 24
        self.ott_percent = 4.6
        self.stop = 0.028
        self.RRR = 9.85
        self.chop_bw = 30.25

        self.pos_size_scaler = 0.17
        
    @property
    @cached
    def ott(self):
        return cta.ott(self.candles[-960:, 2], self.ott_len, self.ott_percent, ma_type='kama', sequential=True)

    @property
    @cached
    def chop(self):
        return talib.RSI(self.candles[-140:, 2], 14)

    @property
    @cached
    def chop_upper_band(self):
        return 40 + self.chop_bw

    @property
    def pos_size_usd(self):
        return self.capital * self.pos_size_scaler
        # return self.available_margin / 4 if self.margin_pos_size else self.capital / (self.n_of_routes * 5)

    @property
    @cached
    def pos_size_qty(self):
        return utils.size_to_qty(self.pos_size_usd, self.price, fee_rate=self.fee_rate) * self.leverage

    def should_long(self):
        return self.cross_up and self.chop[-1] > self.chop_upper_band

    def should_short(self):
        return False

    def go_long(self):
        self.buy = self.pos_size_qty, self.price

    def go_short(self):
        pass

    def on_open_position(self, order):
        self.kasa = self.capital

        if self.is_long:
            sl = self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)
            self.stop_loss = self.position.qty, sl
            tp = self.position.entry_price + \
                (self.position.entry_price * (self.stop * self.RRR))
            # self.console(f'\nLong: {self.position.entry_price} -> {tp}')
            self.take_profit = self.position.qty, tp

    @property
    def cross_up(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='above', sequential=False)

    @property
    def cross_down(self):
        return utils.crossed(self.ott.mavg, self.ott.ott, direction='below', sequential=False)

    def on_close_position(self, order):
        diff = self.capital - self.kasa
        diff_percent = diff / self.kasa * 100
        color_code = '\033[92m' if diff > 0 else '\033[91m'

        if self.is_reversal:
            self.reversals.append(diff_percent)
            self.revs_in_usd += diff
            close_type = 'Reversal'
            self.is_reversal = False
        elif diff < 0:
            self.stop_losses.append(diff_percent)
            self.sl_in_usd += diff
            close_type = 'Stoploss'
        else:
            self.take_profits.append(diff_percent)
            self.tp_in_usd += diff
            close_type = 'Take Profit'

        self.console(
            f'\n{color_code}{close_type} | Balance: {round(self.kasa)}->{round(self.capital)} Diff: {round(diff)} %{round(diff_percent, 2)}\033[0m')
        self.kasa = None
        self.is_reversal = False

    def update_position(self):
        if self.position.pnl_percentage / self.leverage >= self.stop * self.RRR * 100:
            self.liquidate()
            self.console(
                f'\033[92m\n Manual Take profit: {self.position.entry_price} -> {self.price} -> {self.position.pnl_percentage}\033[0m')

        if self.is_long and self.cross_down:
            self.liquidate()
            self.is_reversal = True

    def terminate(self):
        # pass
        # print statistical mean values of self.stop_losses and self.reversals and self.take_profits

        from statistics import mean

        print(self.symbol, '\x1b[92mMEAN VALUES')

        sl_mean = round(mean(self.stop_losses), 3) if len(
            self.stop_losses) > 0 else 0
        tp_mean = round(mean(self.take_profits), 3) if len(
            self.take_profits) > 0 else 0
        rev_mean = round(mean(self.reversals), 3) if len(
            self.reversals) > 0 else 0

        print(f'Stoploss: {len(self.stop_losses)}',
              f'Mean: {sl_mean}%', f'{round(self.sl_in_usd)} USD')
        print(f'Take profit: {len(self.take_profits)}',
              f'Mean: {tp_mean}%', f'{round(self.tp_in_usd)} USD')
        print(f'Reversal: {len(self.reversals)}', f'Mean: {rev_mean}%',
              f'{round(self.revs_in_usd)} USD', end='')
        print('\x1b[0m')
        print('~'*50)

    def console(self, *msg):
        if self.log_enabled:
            print(*msg)

    def should_cancel(self) -> bool:
        return True
