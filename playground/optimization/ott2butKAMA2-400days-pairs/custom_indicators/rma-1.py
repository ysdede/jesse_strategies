import numpy as np
from typing import Union
from talib import SMA

try:
    from numba import njit
except ImportError:
    njit = lambda a: a

from jesse.helpers import get_candle_source, slice_candles


def rma(candles: np.ndarray, length: int = 14, source_type="close", sequential=False) -> \
        Union[float, np.ndarray]:
    """
    Moving average used in RSI. It is the exponentially weighted moving average with alpha = 1 / length.
    RETURNS Exponential moving average of x with alpha = 1 / y.
    https://www.tradingview.com/pine-script-reference/#fun_rma

    :param candles: np.ndarray
    :param length: int - default: 14
    :param source_type: str - default: close
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """

    # Pine change() = np.ediff1d(x), min max aynı olmalı

    """
    print(an_array)
    [ 3 23  5 67 12 15 89]
    
    an_array = np.where(an_array > 20, 0, an_array)
    
    print(an_array)
    [ 3  0  5  0 12 15  0]
    """
    if length < 1:
        raise ValueError('Bad parameters.')

    # Accept normal array too.
    if len(candles.shape) == 1:
        source = candles
    else:
        candles = slice_candles(candles, sequential)
        source = get_candle_source(candles, source_type=source_type)

    res = rma_fast(source, length)

    return res if sequential else res[-1]


def sma(s, l):
    return SMA(s, l)


def rma_fast(source, _length):
    """
    Pine script:
    pine_rma(src, length) = >
    alpha = 1 / length
    sum = 0.0
    sum := na(sum[1]) ? sma(src, length): alpha * src + (1 - alpha) * nz(sum[1])
    """
    alpha = 1 / _length
    newseries = np.copy(source)

    for i in range(source.size):
        if np.isnan(newseries[i - 1]):
            newseries[i] = SMA(source, _length)
            """ret = np.cumsum(source, dtype=float)
            ret[_length:] = ret[_length:] - ret[:-_length]
            newseries[i] = ret[_length - 1:] / _length"""
        else:
            prev = newseries[i - 1]
            if np.isnan(prev):
                prev = 0
            newseries[i] = alpha * source[i] + (1 - alpha) * prev
    return newseries
