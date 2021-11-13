from collections import namedtuple

import numba
import numpy as np
from jesse.helpers import get_candle_source, slice_candles

BBR = namedtuple('bbr', ['upper', 'middle', 'lower', 'ratio'])


def bbr(candles: np.ndarray, length: int = 20, source_type="close", mult: float = 2.0, sequential=False) -> BBR:
    # Bollinger Bands with Ratio % in pure Python & Numba
    # github.com/ysdede

    """
    :param candles: np.ndarray
    :param length: int - default: 2
    :param source_type: str - default: close
    :param mult: float - default: 2.0
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """

    if length < 1 or mult < 0.001:
        raise ValueError('Bad parameters.')

    if len(candles.shape) == 1:
        source = candles
    else:
        candles = slice_candles(candles, sequential)
        source = get_candle_source(candles, source_type=source_type)

    out = np.empty(source.size)
    basis = sma(source, length, out)

    upper, lower, ratio = bb_fast(mult, source, length, basis)

    if sequential:
        return BBR(upper, basis, lower, ratio)
    else:
        return BBR(upper[-1], basis[-1], lower[-1], ratio[-1])


@numba.njit(nopython=True)
def bb_fast(mult, source, length, basis):
    dev = np.multiply(mult, np.std(source[-length:]))
    upper = basis + dev
    lower = basis - dev
    ratio = (source - lower) / (upper - lower)
    return upper, lower, ratio


@numba.njit(nopython=True)
def sma(src, length, out):
    asum = 0.0
    count = 0
    for i in range(length):
        asum += src[i]
        count += 1
        out[i] = asum / count
    for i in range(length, src.size):
        asum += src[i] - src[i - length]
        out[i] = asum / count
    return out
