from typing import Union

import numba
import numpy as np

import custom_indicators as cta


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, length: int = 14, sequential=False) -> \
        Union[float, np.ndarray]:
    """
    :param high: np.ndarray
    :param low: np.ndarray
    :param close: np.ndarray
    :param length: int - default: 14
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """

    # Function atr (average true range) returns the RMA of true range.
    # True range is max(high - low, abs(high - close[1]), abs(low - close[1]))
    # https://www.tradingview.com/pine-script-reference/#fun_atr
    # github.com/ysdede

    if length < 1:
        raise ValueError('Bad parameters.')

    tr = tr_fast(high, low, close)
    res = cta.rma(tr, length, sequential=True)
    return res if sequential else res[-1]


@numba.njit(nopython=True)
def tr_fast(high, low, close):
    out = np.full_like(high, np.nan)

    for i in range(high.size):
        if np.isnan(high[i - 1]):
            out[i] = high[i] - low[i]
        else:
            out[i] = max((high[i] - low[i]), abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
    return out
