# magicBT

### What is it?
magicBT is an equity backtester for both stocks and crypto. It provides as close as real time simulation, allowing you to tweak the very intervals to your liking.

### How to Install
Once you download this package, use `pip install -e .` and then call it in your script as such
```python
from magicBT import Backtest, Backtestable

bt = Backtest(api_key="xxx", credits=55, balance=100_000)
```
#### Example
- Grab the 10 SMA and 50 SMA data with the OHLCV data for botht the 1 min and 5 minute.
```python
from magicBT.enums import Indicator

bt.add_indicator(Indicator.SMA, {'time_period':10})
bt.add_indicator(Indicator.SMA, {'time_period': 50})

aaplBT = bt.load_backtest(stock="AAPL", intervals=["1min", "5min"], start_time="2023/4/1")
```


### Run a backtest
```python
from magicBT.models import CallableInput, Portfolio

def strategy1(input: CallableInput) -> Portfolio:
    port: Portfolio = input.portfolio
    bal = port.balance
    ...
    return port

aaplBT.run(strategy1, tune_ratio=(0.0001, 0.009))
```

#### tune_ratio
`tune_ratio` is an optional parameter but if used will tune your backtest model `X` times with a random float between `[x, y]` so that you can use this to see the best
parameter or threshold to use. The default tune is 100 tunes.