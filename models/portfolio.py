from magicBT.models import BConfig, Trade, Handle, TimeSeries
from pydantic import BaseModel
from typing import Union, List, Dict, Optional
from uuid import uuid4
from numpy import float32


class Portfolio:
    def __init__(self, balance: float):
        self.orders: Dict[str, Trade] = {}
        self.trades: List[Trade] = []
        self.init_balance: float = balance
        self.balance: float = balance
    
    def close_all(self, close_price: Union[float, float32]):
        """
        Closes all positions
        """
        self.trades.append([
            order.close(close_price) for key, order in self.orders.items()
        ])
        self.orders.clear()

    def close(self, key: str, close_price: Union[float, float32]):
        """
        Closes a position from the order key
        """
        order = self.orders[key]
        if not order:
            return KeyError("Order does not exist.")
        self.trades.append(order.close(close_price))
    
    def place_order(self, trade: Trade) -> Union[str, None]:
        """
        Places an order on either side
        Adds to an existing order if it exists and adjusts the cost basis
        """
        for key, _trade in self.orders.items():
            if _trade.side == trade.side and _trade.symbol == trade.symbol:
                # congregate order
                self.orders[key] = (_trade + trade)
                return key
        key = str(uuid4())
        self.orders[key] = trade
        return key

    def get_order(self, key: str) -> Trade:
        order: Trade = self.orders[key]
        if not order:
            return KeyError("Order does not exist.")
        return order
    
    def reduce_position(self, key: str, close_price: float, by: float):
        """
        Reduces a position by a percentage
        `key` can be used as the trade ID or the symbol.
        """
        for _key, item in self.orders.items():
            if item.symbol == key or _key == key:
                close_pos = Trade(
                    symbol = item.symbol,
                    qty = int(item.qty * by),
                    side = item.side,
                    bought_at=item.bought_at,
                    closed = 1,
                    closed_at = close_price
                )
                self.trades.append(close_pos)
                item.qty -= close_pos.qty
        
    def calc_profits(self) -> float:
        return sum([(trade.qty * trade.closed_at) - (trade.qty * trade.bought_at) 
                    for trade in self.trades if trade.closed])
    
    def calc_pl_count(self):
        return {'P': sum([1
                    for trade in self.trades 
                    if trade.closed and trade.closed_at > trade.bought_at]),
                'L': sum([1
                    for trade in self.trades 
                    if trade.closed and trade.closed_at < trade.bought_at])}
    
    def calc_pl(self):
        return {'P': [trade
                    for trade in self.trades 
                    if trade.closed and trade.closed_at > trade.bought_at],
                'L': [trade
                    for trade in self.trades 
                    if trade.closed and trade.closed_at < trade.bought_at]}
    
class CallableInput(BaseModel):
    portfolio: Portfolio
    stock: str
    TS: Dict[str, TimeSeries]
    auto_tune: Optional[float] = None

    class Config(BConfig):
        ...