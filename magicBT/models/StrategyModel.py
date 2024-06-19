from pydantic import BaseModel, Field
from typing import Optional, List


class StrategyOrder(BaseModel):
    symbol: str
    qty: int
    side: str
    take_profit: Optional[float] = Field(default=-1)
    stop_price: Optional[float] = Field(default=-1)
    

class StrategyResponse(BaseModel):
    responses: Optional[List[StrategyOrder]]


