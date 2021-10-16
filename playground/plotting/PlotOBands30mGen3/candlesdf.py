import os
import numpy as np
import pandas as pd
import pytest
from jesse import utils, validate_cwd
from jesse import research
research.init()
import jesse.indicators as ta


def get_candles_as_df(exchange, symbol, tf, start, finish):
    # os.chdir(os.getcwd())
    # validate_cwd()
    candles = research.get_candles(exchange, symbol, tf, start, finish)
    columns = ["Date", "Open", "Close", "High", "Low", "Volume"]
    df = pd.DataFrame(data=candles, index=pd.to_datetime(candles[:, 0], unit="ms"), columns=columns)
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")

    ohlcv = utils.numpy_candles_to_dataframe(candles, name_date="Date", name_open="Open", name_high="High",
                                             name_low="Low", name_close="Close", name_volume="Volume")
    return df
