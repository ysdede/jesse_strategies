import datetime

from jesse.strategies import Strategy

import custom_indicators as cta


class OTTTest(Strategy):
    def __init__(self):
        super().__init__()
        self.ts = None
        self.output = None
        self.pinescript = """//@version=4
study("OTT TEST", precision=6, overlay=true)


tick =
"""

        self.pineplot = """
plot(tick, color=color.lime, style=plot.style_line, linewidth=1)
                """

    def should_long(self) -> bool:
        ott = cta.ottf(self.candles, 62.5, sequential=True).ott
        value = round(float(ott[-1]), 6)

        epoch = self.current_candle[0] / 1000
        self.ts = datetime.datetime.utcfromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')
        year = int(datetime.datetime.utcfromtimestamp(epoch).strftime('%Y'))
        month = int(datetime.datetime.utcfromtimestamp(epoch).strftime('%m'))
        day = int(datetime.datetime.utcfromtimestamp(epoch).strftime('%d'))
        hour = int(datetime.datetime.utcfromtimestamp(epoch).strftime('%H'))

        self.pinescript = self.pinescript + f'\n     year == {year} and month == {month} and dayofmonth == {day} and hour == {hour} ? {value}: '
        self.output = ott
        return False

    def terminate(self):
        print('Backtest is done')
        print('\n', self.ts, round(self.output[-1], 6))
        self.writepine()

    def writepine(self):
        self.pinescript = self.pinescript + 'na\n'
        self.pinescript = self.pinescript + self.pineplot

        with open('ott.pine', "w") as f:
            f.write(self.pinescript)

    def should_short(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        pass

    def go_short(self):
        pass
