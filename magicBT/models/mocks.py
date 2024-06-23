from abc import abstractmethod
from .strategies import StrategyBacktest

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