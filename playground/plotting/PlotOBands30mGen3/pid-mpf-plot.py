import os

import mplfinance as mpf
from jesse import validate_cwd

from candlesdf import get_candles_as_df

# TODO  https://github.com/matplotlib/mplfinance
# TODO  https://github.com/matplotlib/mplfinance/tree/master/examples
os.chdir(os.getcwd())
validate_cwd()
candles = get_candles_as_df('Binance Futures', 'AAVE-USDT', '5m', '2021-08-20', '2021-08-21')
# type='candle', type='line', type='renko', or type='pnf' ohlc


mpf.plot(candles, type='candle', mav=(10, 30), volume=True)
