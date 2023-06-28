from enum import Enum

class Indicator(str, Enum):
    SMA = "sma"
    EMA = "ema"
    VWAP = "vwap"
    BB = "bb"

class Side(Enum):
    SHORT = 0
    LONG = 1
