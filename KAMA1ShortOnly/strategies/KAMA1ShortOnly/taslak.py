import talib
from jesse import utils
from jesse.strategies import Strategy, cached
import custom_indicators as cta
from jesse.services.selectors import get_all_trading_routes


class Ott2butKAMARe3(Strategy):
    def __init__(self):
        super().__init__()
        self.trade_ts = None
        self.kasa = None
        self.is_reversal = False

        self.stop_losses = []
        self.take_profits = []
        self.reversals = []

        self.sl_in_usd = 0.0
        self.tp_in_usd = 0.0
        self.revs_in_usd = 0.0

        self.log_enabled = False
        self.n_of_routes = len(get_all_trading_routes())
        
        self.margin_pos_size = False

    def hyperparameters(self):
        return [
            {'name': 'ott_ma_len', 'type': int,
                'min': 5, 'max': 105, 'default': 63},
            {'name': 'ott_percent', 'type': int, 'min': 1500,
                'max': 6500, 'default': 2323},  # 2.323
            {'name': 'stop_loss', 'type': int, 'min': 1000,
                'max': 3000, 'default': 2899},  # 0.02899 ~ %2.9
            {'name': 'risk_reward', 'type': int, 'min': 200, 'max': 1200,
                'default': 542},  # 5.42 * stop_loss, 5.42 * 2.9
            {'name': 'chop_bandwidth', 'type': int, 'min': 1200, 'max': 3200,
                'default': 1327},  # treshold for long: RSI 53.27
        ]

    @property
    @cached
    def ott_len(self):
        return self.hp['ott_ma_len']

    @property
    @cached
    def ott_percent(self):
        return self.hp['ott_percent'] / 1000

    @property
    @cached
    def stop(self):
        return self.hp['stop_loss'] / 100000

    @property
    @cached
    def RRR(self):
        return self.hp['risk_reward'] / 100

    @property
    @cached
    def chop_bw(self):
        return self.hp['chop_bandwidth'] / 100

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
    @cached
    def chop_lower_band(self):
        return 60 - self.chop_bw

    @property
    def pos_size_usd(self):
        return self.capital * 0.1
        # return self.available_margin / 4 if self.margin_pos_size else self.capital / (self.n_of_routes * 5)
        #
        # return self.capital / 15 * self.leverage  # (self.n_of_routes * 5)
        # return self.available_margin / 2

    @property
    @cached
    def pos_size_qty(self):
        return utils.size_to_qty((self.pos_size_usd), self.price, fee_rate=self.fee_rate) * self.leverage

    def should_long(self) -> bool:
        # check_margin = self.pos_size_usd * self.leverage < self.available_margin
        # if not check_margin:
        #     print(f'\033[91m\n Not enough margin: {round(self.pos_size_usd * self.leverage, 2)} < {round(self.available_margin, 2)}\033[0m')
        #     return False

        return self.cross_up and self.chop[-1] > self.chop_upper_band

    def should_short(self) -> bool:
        # return self.cross_down and self.chop[-1] < self.chop_lower_band
        return False

    def go_long(self):
        self.buy = self.pos_size_qty, self.price

    def go_short(self):
        self.sell = self.pos_size_qty, self.price

    def on_open_position(self, order):
        self.kasa = self.capital

        if self.is_long:
            sl = self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)
            self.stop_loss = self.position.qty, sl
            tp = self.position.entry_price + \
                (self.position.entry_price * (self.stop * self.RRR))
            # self.console(f'\nLong: {self.position.entry_price} -> {tp}')
            self.take_profit = self.position.qty, tp

        if self.is_short:
            sl = self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)
            self.stop_loss = self.position.qty, sl
            tp = self.position.entry_price - \
                (self.position.entry_price * (self.stop * self.RRR))
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
        # close_type = 'Reversal' if self.is_reversal else 'TP/SL'

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

        # print console in color
        # self.console(f'\033[92m\nTake profit: {self.position.entry_price} -> {order.price}\033[0m')
        # self.console(f'\nTake profit: {self.position.entry_price} -> {order.price}')

    def update_position(self):
        if self.position.pnl_percentage / self.leverage >= self.stop * self.RRR * 100:
            self.liquidate()
            self.console(
                f'\033[92m\n Manual Take profit: {self.position.entry_price} -> {self.price} -> {self.position.pnl_percentage}\033[0m')

        if self.is_long and self.cross_down:
            self.liquidate()
            self.is_reversal = True

        if self.is_short and self.cross_up:
            self.liquidate()

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

        # Useless trailing stop loss thing
        # if self.is_long and self.average_stop_loss:
        #     sl = self.ott.ott[-1] - (self.ott.ott[-1] * self.stop)

        #     if sl > self.average_stop_loss and sl > self.average_entry_price:
        #         self.stop_loss = self.position.qty, sl

        # if self.is_short and self.average_stop_loss:
        #     sl = self.ott.ott[-1] + (self.ott.ott[-1] * self.stop)

        #     if sl < self.average_stop_loss and sl < self.average_entry_price:
        #         self.stop_loss = self.position.qty, sl

    def console(self, *msg):
        if self.log_enabled:
            print(*msg)
        # self.logger.info(msg)

    def should_cancel(self) -> bool:
        return True
