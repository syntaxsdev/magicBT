from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Callable
from abc import abstractmethod

from .common import Trade

class StrategyOrder(BaseModel):
    symbol: str
    qty: int
    side: str
    take_profit: Optional[float] = Field(default=-1)
    stop_price: Optional[float] = Field(default=-1)
    

class StrategyResponse(BaseModel):
    responses: Optional[List[StrategyOrder]]


class StrategyBacktest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stock: str
    key: str | None
    logger: Callable | None = None
    args: dict | None = None

class StrategyBacktestIteration(BaseModel):
    intervals: list[type]
    positions: list[Trade]