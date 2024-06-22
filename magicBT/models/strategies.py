from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Callable
from abc import abstractmethod

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
    alloted: int


class MockStrategy():
    def __init__(self, init: StrategyBacktest):
        ...
    
    @abstractmethod
    async def stream(self, quote):
        ...
    
    @abstractmethod
    async def iteration(self, sii):
        ...

class MockLogger():
    @abstractmethod
    def backtest_log(message: str):
        ...
# class StrategyInitialization(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     stock: Stock
#     persistence: object
#     iMB: object
#     priv_key: str
#     alloted: float