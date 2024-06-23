from magicBT.enums import Side, Indicator

from typing import Union, List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from pydantic.functional_validators import field_validator
import numpy as np

def convert_to_float32(cls, v):
    return np.float32(v)

def convert_to_int32(cls, v):
    return np.int32(v)

def convert_to_strn(cls, v):
    return np.bytes_(v)


def convert_to_bool(cls, v):
    return np.bool(v)

class AccountModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    initial_balance: np.float32
    balance: np.float32
    total_trades: Optional[np.int32] = 0

    _validate_float = field_validator(
            'initial_balance', 'balance',
            mode="before")(convert_to_float32)
        
    _validate_int = field_validator(
        'total_trades',
        mode="before")(convert_to_int32)


class Trade(BaseModel):
    symbol: str
    qty: np.float32
    side: Side
    bought_at: np.float32
    cost_basis: Optional[np.float32]
    closed_at: Optional[np.float32]
    closed: np.bool = 0

    _validate_float = field_validator(
            'qty', 'cost_basis', 'closed_at', 'bought_at',
            mode="before")(convert_to_float32)
        
    _validate_int = field_validator(
        'closed',
        mode="before")(convert_to_bool)
    

    def close(self, close_price: Union[float, np.float32]):
        self.closed = 1
        self.closed_at = close_price
        return self
    
    def __add__(self, other: 'Trade'):
        if not isinstance(other, Trade):
            return NotImplemented
        if self.symbol == other.symbol and self.side == other.side and not self.closed and not other.closed:
            total_qty = self.qty + other.qty
            return Trade(
                symbol=self.symbol,
                qty=total_qty,
                bought_at=((self.bought_at * self.qty) + (other.bought_at * other.qty)) / total_qty, #cost_basis essentially
                side=self.side
                )
        return ValueError("Could not add to this trade because it is the same stock.")

        
    model_config = ConfigDict(arbitrary_types_allowed=True)


class StrategyMeasurement(BaseModel):
    total_trades: int
    trades_average: Optional[float]
    profits: Optional[float]
    list_of_trades: Optional[List[Trade]]



class Handle(BaseModel):
    key: str 
    obj: object


class SingleSeries(BaseModel):
    datetime: np.datetime64
    open: np.float32
    high: np.float32
    low: np.float32
    close: np.float32
    volume: np.int32
    indicator_fields: Dict[str, Any] = dict()

    def __init__(self, **data):
            super().__init__(**data)
            self.move_extra_keys(data)
            
            
    def move_extra_keys(self, data: dict):
        # Move all unexpected fields to indicator_fields
        for name in data.keys():
            if name not in self.model_fields:
                # Apply parse_extra_fields to each extra field
                parsed_value = self.parse_extra_fields(self.__dict__[name])
                self.indicator_fields[name] = parsed_value
                delattr(self, name)

    def parse_extra_fields(cls, v):
        if type(v) == float:
            return np.float32(v)
        elif type(v) == str:
            try: 
                return np.float32(v) if float(v) else v
            except: return v
        elif type(v) == int:
            return np.int32(v)
        
    def __hash__(self):
        return hash((self.datetime, self.open, self.high, self.low, self.close, self.volume))

    
    _validate_float = field_validator(
        'open', 'high', 'low', 'close', #'ma_1', 'ma_2', 'ma_3', 'ma_4', 'ma_5', 'ma_6',
        mode="before")(convert_to_float32)
    
    _validate_int = field_validator(
        'volume',
        mode="before")(convert_to_int32)
    
    @field_validator('datetime', mode="before")
    def convert_to_datetime64(cls, v):
        return np.datetime64(v)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class TimeSeries(BaseModel):
    series: list[SingleSeries] = []

    def remove_duplicates(self):
        self.series = list(set(self.series))
    
    def extend(self, obj: object) -> int:
        self.series.extend([
            SingleSeries.model_validate(o) if not type(o) == SingleSeries 
            else o
            for o in obj])

        # auto remove and sort
        self.remove_duplicates()
        self.sort()
        return 1

    def sort(self):
        self.series = sorted(self.series, key=lambda x: x.datetime)

class IndicatorData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    indicator: Indicator
    data: dict
