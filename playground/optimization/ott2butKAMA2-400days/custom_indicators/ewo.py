import numpy as np
import talib
from typing import Union

from jesse.helpers import get_candle_source, slice_candles


def ewo(candles: np.ndarray, short_period: int = 5, long_period: int = 35, source_type="close", sequential=False) -> \
Union[float, np.ndarray]:
    """
    Elliott Wave Oscillator
    :param candles: np.ndarray
    :param short_period: int - default: 5
    :param long_period: int - default: 34
    :param source_type: str - default: close
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """

    candles = slice_candles(candles, sequential)

    src = get_candle_source(candles, source_type)
    ewo = np.subtract(talib.EMA(src, timeperiod=short_period), talib.EMA(src, timeperiod=long_period))

    if sequential:
        return ewo
    else:
        return ewo[-1]