import datetime
import os
import statistics
import sys

import numpy as np
from jesse.routes import router


class balancer:
    def __init__(self, shared_vars, metrics, scaler=1, period=7, enabled=True):

        self.finish_date = sys.argv[-1]  # finish_date
        # print('Finish date', self.finish_date)

        self.sharpe = None
        self.sharpe_enabled = enabled
        self.sharpe_scaler = scaler
        self.period = period  # Days
        self.shared_vars = shared_vars
        self.metrics = metrics
        self.routes = router.routes
        self.my_share = 1
        self.shares = 50

        self.csv = []
        self.deviations = []
        self.normalized_deviations = []
        self.norm_devs_sum = []
        self.pairs = []
        self.results = []
        self.normalized_deviations_with_label = []
        self.deviations_with_label = []
        # self.shared_vars['Shares'] = 40
        self.header1 = ['Time']

        for _route in self.routes:
            sym = _route.symbol

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

    def get_sharpe(self, metrics):
        # --------------->
        if metrics:
            sharpe = float(metrics['sharpe_ratio'])

            if not np.isnan(sharpe):
                self.sharpe = sharpe
                return sharpe
        return None

    def stats(self, symbol, shared_vars, current_candle):
        epoch = current_candle[0] / 1000
        ts = datetime.datetime.utcfromtimestamp(epoch).strftime('%d/%m/%Y')

        if symbol == self.pairs[0]:  # Use first symbol in routes.py file as "master"
            sharpes = [shared_vars[sym]['Sharpe'] for sym in self.pairs]

            # print('\n SHARPES', sharpes)

            # Calculate avg. Sharpe
            mean = statistics.mean(sharpes)
            stdDev = statistics.stdev(sharpes)

            # Round array elements
            # sharpes = [round(x, 3) for x in sharpes]

            # Calculate deviation from average
            # self.deviations = [round(item - mean, 3) for item in sharpes]
            self.deviations = [item - mean for item in sharpes]

            # Boost deviations
            self.deviations = [x * self.sharpe_scaler for x in self.deviations]

            # Normalize deviations, resample minimum sharpe as "1" even it's negative,
            # eg. min sharpe == -1, resample it to 1 by adding +2, so another +2 sharpe will be resampled to +4
            self.normalized_deviations = [abs(min(self.deviations)) + item + 1 for item in self.deviations]

            self.norm_devs_sum = self.shares = sum(self.normalized_deviations)
            # self.shares = self.norm_devs_sum

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

            sharpes_rounded = [round(item, 3) for item in sharpes]
            deviations_rounded = [round(item, 3) for item in self.deviations]
            normalized_deviations_rounded = [round(item, 3) for item in self.normalized_deviations]

            sharpes_with_label = ['Sharpe', *sharpes_rounded]
            pairs_with_label = ['Symbol',
                                *self.pairs]  # I need to reuse pairs list and it's created only once in init
            self.deviations_with_label = ['Deviation', *deviations_rounded]
            self.normalized_deviations_with_label = ['Shares', *normalized_deviations_rounded]
            # self.deviations.insert(0, 'Deviation')
            # self.normalized_deviations.insert(0, 'Shares')

            # self.clearConsole()
            print()
            print('*' * len(self.sharpes_formatter))
            print(
                f'{ts} | Avg. Sharpe: {round(mean, 3)} | Std.Dev: {round(stdDev, 3)} | Shares: {round(self.norm_devs_sum, 3)} | Scaler: {self.sharpe_scaler}')
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

                mark = 'Sharpe' if self.sharpe_enabled else 'noSharpe'
                self.create_report(self.results,
                                   f'{self.sharpe_scaler}x {self.period}D {now}-{mark}.csv'.replace('/', '-'))

        # print(f"\nI'm {self.symbol}, MyShare is {self.shared_vars[self.symbol]['MyShare']}. Total Share is {
        # self.shared_vars['Shares']}")

    def create_report(self, _res, _fname):
        with open(_fname, 'w') as f:
            f.write(str(self.header1).replace('[', '').replace(']', '').replace(' ', '') + '\n')
            for srline in _res:
                f.write(str(srline).replace('[', '').replace(']', '').replace(' ', '') + '\n')
            os.fsync(f.fileno())
