from magicBT.models import AccountModel, TimeSeries, IndicatorData, \
    StrategyMeasurement, StrategyBacktest, MockStrategy
from .portfolio import Portfolio, CallableInput
from magicBT.broker import TDBroker
from magicBT.enums import Indicator

from typing import Union, Callable, List, Dict, Tuple, Optional, Type

from datetime import datetime
import random
import threading
import inspect

class Backtestable:
    __DEFINED_METHODS = ["iteration", "stream", "__init__"]

    """
    A ready backtest object that can be ran using eitherna
    - a backtest function
    - implemented into an existing algorithm
    """
    def __init__(self, stock: str, account: AccountModel, timeseries: Dict[str, TimeSeries]):
          self.stock: str = stock
          self.account: AccountModel = account
          self.timeseries: Dict[str, TimeSeries] = timeseries
    
    def _rand_tune(self, tune_ratio: Tuple[int, int]):
         return random.uniform(tune_ratio[0], tune_ratio[1])
    

    def _run_strategy(self, 
        strategy: Callable[[CallableInput], Portfolio], 
        port: Portfolio, 
        tune_ratio: tuple[float, float]):

        CI: CallableInput = CallableInput(
                    portfolio=port,
                    stock=self.stock,
                    TS = self.timeseries,
                    auto_tune = self._rand_tune(tune_ratio))

        port = Portfolio(self.account.balance)
        port.trades.extend(strategy(CI).trades)

        return StrategyMeasurement(
            total_trades=len(port.trades),
            trades_average=-1,
            profits=port.calc_profits(),
            list_of_trades=port.trades
            )

    def run_defined_strategy(self,
                     strategy: MockStrategy,
                     stock: str,
                     args: dict | None,
                     logger: Callable | None = None,
                     transformer: Callable | None = None,
                     is_async: bool = True):
        """
        Runs a backtest with a more defined strategy class

        Args:
            `strategy` (MockStrategy): A mock strategy type that can be used as a starting class. Can use custom but must follow the format and includes those methods. Must accept parameter `StrategyBacktest`.
            `stock` (str): The stock or ticker
            `args` (dict or None): Additional arguments to go into the `strategy` via `StrategyBacktest.args` property.
            `logger` (Callable or None): A function that can log. Must take in one argument for the log message.
            `transformer` (Callable or None): A function that will transform the TimeSeries data, if needed.
            `is_async` (bool): Whether or not the functions in `strategy` are async or not.

        """
        sb: StrategyBacktest = StrategyBacktest(
            stock=stock,
            key=None,
            logger=logger,
            args=args
        )
        if not all(hasattr(strategy, method) for method in self.__DEFINED_METHODS):
            raise AttributeError("This strategy class does not have the needed functions to work with this method.")
        
        try:
            strat: MockStrategy = strategy(sb)

            for key, ts in self.timeseries.items():
                print(key)

        except Exception as ex:
            print(ex)
        
    def run(self, 
        strategy: Callable[[CallableInput], Portfolio], 
        tune_ratio: Optional[Tuple[float, float]] = None,
        tune_count: Optional[int] = 100) -> StrategyMeasurement:
        
        empty_port = Portfolio(balance=self.account.balance)
        smList: List[StrategyMeasurement] = []
        if tune_ratio:
            threads: List[threading.Thread] = []
            results: List[StrategyMeasurement] = []
            for i in range(tune_count):
                thread = threading.Thread(
                    target=lambda: results.append(self._run_strategy(
                    strategy=strategy,
                    port=Portfolio(balance=self.account.balance),
                    tune_ratio=tune_ratio))
                    )
                
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            smList.extend(results)
            
                
        else:
            return self._run_strategy(
                strategy=strategy,
                port=empty_port
            )
        return smList


class Backtest:
    """
    Configures a backtest
    """
    stock: str
    def __init__(self, api_key: str, credits: int, balance: str):
        self.api_key: str = api_key
        self.TDB = TDBroker(api_key, credits)
        self.account = AccountModel(
            initial_balance=balance,
            balance=balance
        )
        self.indicators: List[IndicatorData] = []
    
    def add_indicator(self, type: Indicator, data: object):
        self.indicators.append(
            IndicatorData(
            indicator=type,
            data=data)
            )
        
    def load_backtest(self, stock: str, 
                      intervals: List[str],
                      start_time: Union[datetime, str],
                      end_time: datetime | str | None = None) -> Backtestable:
        """
        Returns a class with the preconfigured backtest object ready with TimeSeries data
        :returns Backtestable
        """
        data: Dict[str, TimeSeries] = {i:self.TDB.gather_backtest(
            stock=stock,
            start_time=start_time,
            interval=i,
            indicators=self.indicators
        ) for i in intervals}
        return Backtestable(stock, account=self.account, timeseries=data)