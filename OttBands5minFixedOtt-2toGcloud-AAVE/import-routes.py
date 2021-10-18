import datetime
import sys

try:
    from jesse.config import config
    from jesse.modes import import_candles_mode
    from jesse.routes import router
    from jesse.services import db
    config['app']['trading_mode'] = 'import-candles'
except Exception as e:
    print(e)
    print('Check your routes.py file or database settings in config.py')
    exit()

# If no start date is specified, the system will default to two days earlier.
# It's useful for executing script in a cron job to download deltas on a regular basis.

if len(sys.argv) < 2:
    start_date = str(datetime.date.today() - datetime.timedelta(days=2))
    print('Start date not provided, falling-back to two days earlier.', start_date)
else:
    start_date = sys.argv[1]

print(f'Startdate: {start_date}')

routes_list = router.routes

if not routes_list or len(routes_list) < 1:
    print('Check your routes.py file!')
    exit()

for i, t in enumerate(routes_list):
    pair = t.symbol
    exchange = t.exchange
    print(f'Importing {exchange} {pair}')

    try:
        import_candles_mode.run(exchange, pair, start_date, skip_confirmation=True)
    except KeyboardInterrupt:
        print('Terminated!')
        db.close_connection()
        sys.exit()
    except:
        print(f'Import error, skipping {exchange} {pair}')

db.close_connection()
