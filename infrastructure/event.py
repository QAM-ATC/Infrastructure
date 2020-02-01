import pandas as pd

from abc import ABC
from functools import total_ordering
from dataclasses import dataclass, asdict

@total_ordering
class Event(ABC):
    def __eq__(self, other):
        return self.event_time == other.event_time

    def __lt__(self, other):
        return self.event_time < other.event_time


@dataclass
class DataEvent(Event):
    __slots__ = "event_time", "symbol", "table_name", "data", "type"
    event_time: pd.Timestamp
    symbol: str
    table_name: str
    data: pd.Series

    def __post_init__(self):  # can probably be optimised further
        self.type = "DATA"


@dataclass
class FillEvent(Event):
    __slots__ = "event_time", "symbol", "exchange", "order_type", "quantity", "cost", "type"
    event_time: pd.Timestamp
    symbol: str
    exchange: str
    order_type: str
    quantity: int  # change in securities held
    cost: float  # change in cash held

    @property
    def commission(self):  # will eventually contain exchange/broker-specific logic
        return abs(self.cost) * -0.005

    def __post_init__(self):  # can probably be optimised further
        self.type = "FILL"


@dataclass
class Signal:
    __slots__ = "symbol", "exchange", "signal_type", "strength"
    symbol: str
    exchange: str
    signal_type: str  # BUY/SELL/EXIT
    strength: float  # 0 to 1


@dataclass
class Order:
    __slots__ = "symbol", "exchange", "order_type", "direction", "quantity", "price"
    symbol: str
    exchange: str
    order_type: str  # MKT/LMT
    direction: str  # BUY/SELL
    quantity: int
    price: float  # only relevant to LMT


if __name__ == "__main__":
    o = Order("XBTUSD", "BitMEX", "MKT", "BUY", 5, 7250)
    s = pd.Series([1,2,3])
    de0 = DataEvent(pd.Timestamp.utcnow(), "XBTUSD", "DATA", s)
    de1 = DataEvent(pd.Timestamp.utcnow(), "XBTUSD", "DATA", s)
    print(de0 < de1)
    print(o)
    print(de0.type)
