import pandas as pd

from abc import ABC
from functools import total_ordering
from dataclasses import dataclass, asdict

@total_ordering
class Event(ABC):
    def __post_init__(self):
        assert type(self.event_time) == pd.Timestamp, \
            "pd.Timestamp event_time required"

    def __eq__(self, other):
        return self.event_time == other.event_time

    def __lt__(self, other):
        return self.event_time < other.event_time


@dataclass
class DataEvent(Event):
    __slots__ = "event_time", "symbol", "table_name", "data"
    event_time: pd.Timestamp
    symbol: str
    table_name: str
    data: pd.Series

    def __post_init__(self):
        self.type = "DATA"


@dataclass
class FillEvent(Event):
    __slots__ = "event_time", "symbol", "exchange", "quantity", "cost"
    event_time: pd.Timestamp
    symbol: str
    exchange: str
    quantity: int  # change in securities held
    cost: float  # change in cash held

    @property
    def commission(self):
        # will eventually contain exchange/broker-specific logic
        return self.cost * 0.005


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

    def record(self, send_time):
        return pd.Series(asdict(self), name=send_time)

if __name__ == "__main__":
    o = Order("XBTUSD", "BitMEX", "MKT", "BUY", 5, 7250)
    print(o.record(pd.Timestamp.utcnow()))
