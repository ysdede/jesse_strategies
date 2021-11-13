from collections import namedtuple

import numba
import numpy as np

import custom_indicators as cta

CE = namedtuple('CE', ['longStop', 'shortStop', 'DIR'])


def ce(high: np.ndarray, low: np.ndarray, close: np.ndarray, length: int = 22, mult: float = 3.0, useClose=True,
       sequential=False) -> CE:
    """
    :param high: np.ndarray
    :param low: np.ndarray
    :param close: np.ndarray
    :param length: int - default: 22
    :param mult: int - default: 3.0
    :param useClose: bool - default: True
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """

    if length < 1 or mult <= 0:
        raise ValueError('Bad parameters.')

    atr = np.multiply(cta.atr(high, low, close, length=length, sequential=True), mult)

    longStop, shortStop, DIR = ce_fast(high, low, close, atr, length)

    # print(f'LS: {longStop.size} SS: {shortStop.size} Candles: {high.size}')

    if sequential:
        return CE(longStop, shortStop, DIR)
    else:
        return CE(longStop[-1], shortStop[-1], DIR[-1])


@numba.njit
def ce_fast(high, low, close, atr, length):
    longStop = np.full_like(high, np.nan)

    for i in range(length, longStop.size):
        longStop[i] = max(close[i - length + 1:i + 1])

    longStop = longStop - atr

    for i in range(length, longStop.size):
        if close[i - 1] > longStop[i - 1]:
            longStop[i] = max(longStop[i], longStop[i - 1])

    shortStop = np.full_like(low, np.nan)

    for i in range(length, shortStop.size):
        shortStop[i] = min(close[i - length + 1:i + 1])

    shortStop = shortStop + atr

    for i in range(length, shortStop.size):
        if close[i - 1] < shortStop[i - 1]:
            shortStop[i] = min(shortStop[i], shortStop[i - 1])

    DIR = np.full_like(longStop, 1)

    for i in range(length, DIR.size):
        if close[i] > shortStop[i-1]:
            DIR[i] = 1
        elif close[i] < longStop[i-1]:
            DIR[i] = -1

    return longStop, shortStop, DIR
