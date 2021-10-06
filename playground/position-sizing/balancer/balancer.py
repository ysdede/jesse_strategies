import datetime
import os
import statistics
import sys
import numpy as np
import talib
from jesse.routes import router
from jesse.strategies import Strategy, cached
from jesse import utils
import jesse.indicators as ta
from jesse.services.selectors import get_all_trading_routes
import custom_indicators as cta


class balancer:
    def __init__(self, routes, finish_date, shared_vars, metrics, scaler=4, enabled=True):
        self.finish_date = finish_date
        print('Finish date', self.finish_date)

        self.sharpe = None
        self.sharpe_enabled = enabled
        self.sharpe_scaler = scaler
        self.shared_vars = shared_vars
        self.metrics = metrics
        self.routes = routes
        self.my_share = 1
        self.shares = 50

        self.csv = []
        self.deviations = []
        self.normalized_deviations = []
        self.norm_devs_sum = []
        self.pairs = []
        self.results = []
        self.normalized_deviations_with_label = []
        # self.shared_vars['Shares'] = 40
        self.header1 = ['Time']

        for _route in self.routes:
            sym = _route.symbol
            print(sym)

            self.shared_vars[sym] = {'id': sym, 'Sharpe': 0.0, 'Calmar': 0.0, 'Total': 0, 'Multip': 1,
                                     'WinRate': 0, 'MyShare': 1}
            self.header1.append(sym)

        self.header1.append('Mean')

        for _route in self.routes:
            sym = _route.symbol
            self.pairs.append(sym)

        self.header_formatter = '{: <12} {: <6}'
        self.pairs_formatter = '{: <10}' * (len(self.pairs) + 1)  # Pairs list created once at init.
        self.sharpes_formatter = '{: <10}' * (len(self.pairs) + 1)  # Statistics re-calculated every loop
        self.deviations_formatter = '{: <10}' * (len(self.pairs) + 1)  # +1 for labels
        self.normalized_deviations_formatter = '{: <10}' * (len(self.pairs) + 1)

        # self.pairs.insert(0, 'symbol')

    def tick(self, current_candle):
        epoch = current_candle[0] / 1000
        hour = datetime.datetime.utcfromtimestamp(epoch).strftime('%H')
        minute = datetime.datetime.utcfromtimestamp(epoch).strftime('%M')
        return hour == '00' and minute == '00'

    def get_sharpe(self, current_candle, metrics):
        # --------------->
        if metrics:
            sharpe = float(metrics['sharpe_ratio'])

            if not np.isnan(sharpe):
                self.sharpe = sharpe
                return sharpe
        return None

    def stats(self, symbol, shared_vars, current_candle, metrics):
        # --------------->
        epoch = current_candle[0] / 1000
        ts = datetime.datetime.utcfromtimestamp(epoch).strftime('%d/%m/%Y')
        # ---------------------

        if symbol == 'ETH-USDT':
            sharpes = []

            for sym in self.pairs:
                sharpes.append(shared_vars[sym]['Sharpe'])
            print('\n SHARPES', sharpes)

            # Calculate avg. Sharpe
            mean = round(statistics.mean(sharpes), 3)
            stdDev = statistics.stdev(sharpes)

            # Round array elements
            sharpes = [round(x, 3) for x in sharpes]

            # Calculate deviation from average
            self.deviations = [round(item - mean, 3) for item in sharpes]

            # Boost deviations
            self.deviations = [round(x * 1, 3) for x in self.deviations]

            # Normalize deviations, resample minimum sharpe as "1" even it's negative,
            # eg. min sharpe == -1, resample it to 1 by adding +2, so another +2 sharpe will be resampled to +4
            self.normalized_deviations = [round(abs(min(self.deviations)) + item + 1, 3) for item in
                                          self.deviations]

            self.norm_devs_sum = round(sum(self.normalized_deviations), 3)
            self.shares = self.norm_devs_sum

            # sharpes.append(mean)

            # for dev in self.deviations:
            #     sharpes.append(dev)

            # for norm_dev in self.normalized_deviations:
            #     sharpes.append(norm_dev)

            # if int(day) % 2 == 0 and hour == '00' and minute == '00':

            # Fill shares per symbol
            # Moved to strategy

            # sharpes.append(self.norm_devs_sum)
            # sharpes.insert(0, ts)

            # create csv row before modifing lists
            # TODO: or don't modify original lists, create temp lists to print out
            row = [ts]
            for sh in sharpes:
                row.append(sh)
            row.append(mean)
            for dev in self.deviations:
                row.append(dev)
            for nd in self.normalized_deviations:
                row.append(nd)
            row.append(self.norm_devs_sum)

            self.results.append(row)

            sharpes_with_label = ['Sharpe', *sharpes]
            pairs_with_label = ['Symbol',
                                *self.pairs]  # I need to reuse pairs list and it's created only once in init
            self.deviations_with_label = ['Deviation', *self.deviations]
            # self.deviations.insert(0, 'Deviation')
            # self.normalized_deviations.insert(0, 'Shares')
            self.normalized_deviations_with_label = ['Shares', *self.normalized_deviations]
            # self.clearConsole()
            print()
            print('*' * len(self.sharpes_formatter))
            print(f'{ts} | Avg. Sharpe: {mean} | Std.Dev: {round(stdDev, 3)} | Shares: {self.norm_devs_sum}')
            print(self.pairs_formatter.format(*pairs_with_label))
            print(self.sharpes_formatter.format(*sharpes_with_label))
            print(self.deviations_formatter.format(*self.deviations_with_label))
            print(self.normalized_deviations_formatter.format(*self.normalized_deviations_with_label))

            tomorrow = datetime.datetime.utcfromtimestamp(epoch + 86400).strftime('%Y-%m-%d')
            if tomorrow == self.finish_date:
                now = datetime.datetime.now().strftime('%d%m%Y-%H%M')
                csv_header = ['Time']
                for sym in self.pairs:
                    csv_header.append(sym)
                csv_header.append('mean')
                for sym in self.pairs:
                    csv_header.append(f'{sym} dev')

                for sym in self.pairs:
                    csv_header.append(f'{sym} Share')

                if self.sharpe_enabled:
                    mark = 'Sharpe'
                else:
                    mark = 'noSharpe'
                self.createreport(self.results, f'{now}-{mark}.csv'.replace('/', '-'))

        # print(f"\nI'm {self.symbol}, MyShare is {self.shared_vars[self.symbol]['MyShare']}. Total Share is {self.shared_vars['Shares']}")

    def createreport(self, _res, _fname):
        # Create csv report
        f = open(_fname, 'w')
        f.write(str(self.header1).replace('[', '').replace(']', '').replace(' ', '') + '\n')
        for srline in _res:
            f.write(str(srline).replace('[', '').replace(']', '').replace(' ', '') + '\n')
        os.fsync(f.fileno())
        f.close()
