import numpy as np
from simple_pid import PID


def pid(candles: np.ndarray,
        Kp: float = 1,
        Ki: float = 1,
        Kd: float = 0.01,
        setpoint: float = 0,
        output_min: int = -1000,
        output_max: int = 1000,
        source_type="close",
        sequential=True):
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

    pid1 = PID(Kp, Ki, Kd, setpoint=setpoint)  # 1, 1, 0.001

    # pid1.sample_time = 0.04

    pid1.output_limits = (-1000, 1000)

    pidmulti = 1
    pid1val, fark1 = 0, 0

    source = candles

    out = np.full_like(source, np.nan)
    forecast = np.copy(source)

    for i in range(source.size-1):

        diff = source[i] - forecast[i]

        out[i] = pid1(diff)
        # out[i] = pid1(source[i])
        forecast[i+1] = source[i] + out[i]/10  # * (1 + (out[i] / 1000))
        print(
            f'fc[i - 1] {forecast[i - 1]} fc[i] {forecast[i]} source[i] {source[i]} diff: {diff} out[i] {out[i]} forecast[i] {forecast[i]}')

    return forecast, out
