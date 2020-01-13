import pandas as pd

from abc import ABC
from functools import total_ordering
from dataclasses import dataclass

@total_ordering
class Event(ABC):
    def __post_init__(self):
        assert type(self.event_time) == pd.Timestamp,\
        "pd.Timestamp event_time required"
    def __eq__(self, other):
        return self.event_time == other.event_time
    def __lt__(self, other):
        return self.event_time < other.event_time
    
@dataclass
class DataEvent(Event):
    __slots__ = "event_time", "table_name", "data"
    event_time : pd.Timestamp
    table_name : str
    data : pd.Series

    def __post_init__(self):
        self.type = "DATA"
        