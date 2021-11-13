import math
from collections import namedtuple

import numba
import numpy as np
import talib
from jesse.helpers import get_candle_source, slice_candles

OTT = namedtuple('OTT', ['ott', 'mavg'])


def ottf(candles: np.ndarray, length: int = 62, percent: float = 1.4, ma_type="kama", source_type="close",
        sequential=False) -> OTT:
    """
    :param candles: np.ndarray
    :param length: int - default: 2
    :param percent: int - default: 1.4
    :param ma_type: str - default: var
    :param source_type: str - default: close
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """

    if length < 2 or percent <= 0:
        raise ValueError('Bad parameters.')

    # Accept normal array too.
    if len(candles.shape) == 1:
        source = candles
    else:
        candles = slice_candles(candles, sequential)
        source = get_candle_source(candles, source_type=source_type)

    floor = math.floor(length)
    ceil = math.ceil(length)

    floor_kama = talib.KAMA(source, timeperiod=floor)

    if floor == ceil:
        ott_series = ott_fast(floor_kama, percent, floor)
        return OTT(ott_series, floor_kama) if sequential else OTT(ott_series[-1], floor_kama[-1])

    ceil_fraction = round(length % 1, 2)
    floor_fraction = round(1 - ceil_fraction, 2)

    ceil_kama = talib.KAMA(source, timeperiod=ceil)

    floor_ott = ott_fast(floor_kama, percent, floor)
    ceil_ott = ott_fast(ceil_kama, percent, ceil)

    fractional_ma = (floor_kama * floor_fraction) + (ceil_kama * ceil_fraction)
    fractional_ott = (floor_ott * floor_fraction) + (ceil_ott * ceil_fraction)

    return OTT(fractional_ott, fractional_ma) if sequential else OTT(fractional_ott[-1], fractional_ma[-1])


@numba.njit
def ott_fast(MAvg, percent, length):
    fark = np.multiply(np.multiply(MAvg, percent), 0.01)
    # >>>>>>>
    longStop = np.subtract(MAvg, fark)
    longStopPrev = np.copy(longStop)

    for i in range(length, longStop.size):
        if MAvg[i] > longStop[i - 1]:
            longStop[i] = max(longStop[i], longStop[i - 1])
            longStopPrev[i] = longStop[i - 1]

    for i in range(length, longStop.size):
        if MAvg[i] > longStopPrev[i]:
            longStop[i] = max(longStop[i], longStopPrev[i])
            longStopPrev[i] = longStop[i - 1]
    # <<<<<>>>>>>>
    shortStop = np.add(MAvg, fark)
    shortStopPrev = np.copy(shortStop)
    for i in range(length, shortStop.size):
        if MAvg[i] < shortStop[i - 1]:
            shortStop[i] = min(shortStop[i], shortStop[i - 1])
            shortStopPrev[i] = shortStop[i - 1]

    for i in range(length, shortStop.size):
        if MAvg[i] < shortStopPrev[i]:
            shortStop[i] = min(shortStop[i], shortStopPrev[i])
            shortStopPrev[i] = shortStop[i - 1]
    # <<<<<>>>>>>>
    dir = np.full_like(longStop, 1)
    temp_dir = dir[length - 1]
    for i in range(length, dir.size):
        if temp_dir < 0 and MAvg[i] > shortStopPrev[i]:
            temp_dir = dir[i] = 1
        elif temp_dir < 0 and MAvg[i] < shortStopPrev[i]:
            temp_dir = dir[i] = -1

        elif temp_dir > 0 and MAvg[i] < longStopPrev[i]:
            temp_dir = dir[i] = -1
    # <<<<<>>>>>>>

    MT = np.where(dir > 0, longStop, shortStop)
    OTT = np.where(MAvg > MT, MT * (200 + percent) /
                   200, MT * (200 - percent) / 200)
    return np.concatenate((np.full(2, 0), OTT[:-2]))
