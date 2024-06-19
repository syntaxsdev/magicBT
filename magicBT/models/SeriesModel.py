from magicBT.enums import Indicator

from pydantic import BaseModel
from pydantic.functional_validators import field_validator
from typing import Dict, Any
import numpy as np


class DConfig:
    arbitrary_types_allowed = True
    allow_mutation = False

def convert_to_float32(cls, v):
    return np.float32(v)

def convert_to_int32(cls, v):
    return np.int32(v)

class SingleSeries(BaseModel):
    datetime: np.datetime64
    open: np.float32
    high: np.float32
    low: np.float32
    close: np.float32
    volume: np.int32
    """
    ma_1: Optional[np.float32]
    ma_2: Optional[np.float32]
    ma_3: Optional[np.float32]
    ma_4: Optional[np.float32]
    ma_5: Optional[np.float32]
    ma_6: Optional[np.float32] 
    """
    indicator_fields: Dict[str, Any] = dict()

    def __init__(self, **data):
            super().__init__(**data)
            self.move_extra_keys(data)
            
            
    def move_extra_keys(self, data: dict):
        # Move all unexpected fields to indicator_fields
        for name in data.keys():
            if name not in self.__fields__:
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

    class Config(DConfig):
        extra = "allow"


class TimeSeries(BaseModel):
    series: list[SingleSeries] = []

    def remove_duplicates(self):
        self.series = list(set(self.series))
    
    def extend(self, obj: object, sort: bool = False) -> int:
        self.series.extend([
            SingleSeries.parse_obj(o) if not type(o) == SingleSeries 
            else o
            for o in obj])

        # auto remove and sort
        self.remove_duplicates()
        if sort:
            self.sort()
        return 1

    def sort(self):
        self.series = sorted(self.series, key=lambda x: x.datetime)


class IndicatorData(BaseModel):
    indicator: Indicator
    data: dict
