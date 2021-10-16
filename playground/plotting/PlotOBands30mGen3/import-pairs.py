import datetime
import sys
from time import sleep

from dateutil.parser import isoparse

try:
    from jesse.config import config
    from jesse.modes import import_candles_mode

    # from jesse.services import db

    config['app']['trading_mode'] = 'import-candles'
except:
    print('Check your routes.py file or project folder structure!')
    exit()

try:
    import pairs
except:
    print('Can not import pairs!')
    exit()

sloMo = False
debug = True

exchanges = []
start_date = str(datetime.date.today() - datetime.timedelta(days=2))
today = datetime.date.today()
pairs_list = None

def sleep2(n):
    if sloMo: sleep(n)


def print2(*args):
    if debug: print(*args)


def decode_parameter(arg):
    global exchanges
    global start_date
    try:
        isoparse(arg)
        start_date = arg
        return
    except ValueError:
        if arg.lower() == 'binance':
            exchanges.append('Binance Futures')
            return
        elif arg.lower() == 'ftx':
            exchanges.append('FTX Futures')
            return
        else:
            print2(f'Can not decode parameter. Given: {arg}')
            exit()


for arg in sys.argv[1:]:
    decode_parameter(arg)

if not exchanges:
    exchanges = ['Binance Futures', 'FTX Futures']

print2(f'Startdate: {start_date}, exchange(s): {exchanges}')

for exch in exchanges:
    if exch == 'Binance Futures':
        pairs_list = pairs.binance_perp_pairs
    elif exch == 'FTX Futures':
        pairs_list = pairs.ftx_perp_pairs
    if not pairs_list:
        print2('pairs_list is empty!')
        exit()

    for symbol in pairs_list:
        print2(f'Importing {exch} {symbol} {start_date} -> {today}')
        sleep2(5)

        try:
            import_candles_mode.run(exch, symbol, start_date, skip_confirmation=True)
        except KeyboardInterrupt:
            print('Terminated!')
            # db.close_connection()
            sys.exit()
        except:
            print2(f'Import error, skipping {exch} {symbol}')
            sleep2(5)

# db.close_connection()
