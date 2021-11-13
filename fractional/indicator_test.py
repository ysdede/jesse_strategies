from jesse import research
import custom_indicators as cta
research.init()

eth_candles = research.get_candles('Binance Futures', 'ETH-USDT', '5m', '2021-08-01', '2021-09-01')

eth_close = eth_candles[-480:, 2]

for i in range(600, 650):
    len = i / 10
    ott_out = cta.ottf(eth_close, len, 1.5, sequential=True)
    print(f'{ott_out.ott[-400:]}', ott_out.ott.size)
