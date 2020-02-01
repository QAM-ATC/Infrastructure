import numpy as np
import pandas as pd

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass

from event import DataEvent, Signal
from event_queue import EventQueue
from data_handler import DataHandler


class Strategy(ABC):
    @abstractmethod
    def calculate_signal_from_data(self, data):
        pass

    @abstractmethod
    def calculate_signal_from_data_event(self, data_event):
        pass


class _DWMADeque(deque):
    def __init__(self, width, trades_df, *args, **kwargs):
        self.width = width
        self.dollar_price_sum = 0
        self.dollar_sum = 0
        if type(trades_df) == pd.DataFrame:
            self.load_data(trades_df)
        super().__init__(*args, **kwargs)

    def append(self, data):
        size, price = data.to_list()
        self.dollar_sum += size * price
        self.dollar_price_sum += size * price ** 2
        while len(self) > 1 and self.dollar_sum > self.width:
            self.popleft()
        super().append((size, price))

    def appendleft(self, data):
        size, price = data.to_list()
        self.dollar_sum += size * price
        self.dollar_price_sum += size * price ** 2
        super().append((size, price))

    def popleft(self):
        size, price = super().popleft()
        self.dollar_sum -= size * price
        self.dollar_price_sum -= size * price ** 2
        return size, price

    def load_data(self, trades_df):
        for _, data in trades_df.iloc[::-1].iterrows():  # from the most recent
            size, price = data.to_list()
            if self.dollar_sum + (size * price) < self.width:
                self.append(data)
            else:
                break

    @property
    def dwap(self):
        return self.dollar_price_sum / self.dollar_sum


class DollarWeightedMACD(Strategy):
    def __init__(self, historical_trades_df):
        self.symbol = "XBTUSD"
        self.exchange = "BitMEX"

        self.group_width = 680850400  # arbitrary, eventually can dynamically adjust
        self.short_ma = 5
        self.long_ma = 10  # maybe can EWM but will need more parameters

        self.short_width = self.group_width * self.short_ma
        self.long_width = self.group_width * self.long_ma

        self.short_deque = _DWMADeque(self.short_width, historical_trades_df)
        self.long_deque = _DWMADeque(self.long_width, historical_trades_df)

        self.previously_increasing = self.currently_increasing  # for checking for direction changes

    @property
    def currently_increasing(self):
        return self.short_deque.dwap > self.long_deque.dwap

    def update_cache(self, data):
        self.short_deque.append(data)
        self.long_deque.append(data)
        self.previously_increasing = self.currently_increasing

    def calculate_signal_from_data(self, data):  # for for-loop backtesting
        prev = self.previously_increasing
        self.update_cache(data)

        if prev == self.currently_increasing:  # if no direction change
            return None

        signal_type = ["SELL", "BUY"][self.currently_increasing]
        return Signal(self.symbol, self.exchange, signal_type, 1)

    def calculate_signal_from_data_event(self, data_event):
        return self.calculate_signal_from_data(data_event.data)


if __name__ == "__main__":
    def read_trades_csv(trades_csv_path):
        df = pd.read_csv(
            trades_csv_path,
            usecols=["received", "size", "price"],
            parse_dates=["received"],
            index_col="received",
            nrows=30000
        )
        return df

    def read_quotes_csv(quotes_csv_path):
        df = pd.read_csv(
            quotes_csv_path,
            usecols=["bidSize", "bidPrice", "askPrice", "askSize", "recorded"],
            parse_dates=["recorded"],
            index_col="recorded",
        )
        df.index.name = "received"
        return df

    trades_csv_path = "play_data/XBTUSD_trades_191214_0434.csv"
    quotes_csv_path = "play_data/XBTUSD_quotes_191214_0434.csv"

    tdf = read_trades_csv(trades_csv_path)
    qdf = read_quotes_csv(quotes_csv_path)

    sym = "XBTUSD"
    all_data = {sym: {}}
    all_data[sym]["TRADES"] = tdf
    all_data[sym]["QUOTES"] = qdf

    init_cap = 100000
    start_time = tdf.index[1500]  # start time
    end_time = tdf.index[-1]
    qdf = qdf.loc[:end_time]

    dh = DataHandler(start_time, all_data)
    eq = EventQueue(start_time)
    strat = DollarWeightedMACD(eq, dh)

    data0 = pd.Series([1000, -200000], index=["size", "price"], name=tdf.index[1501])
    data1 = pd.Series([1000, 2000000], index=["size", "price"], name=tdf.index[1501])
    event_time = tdf.index[1501]
    print(strat.previously_increasing)
    de = DataEvent(event_time, sym, "TRADES", data0)

    strat.update_lookbacks(de)
    print(strat.calculate_signal(de))

    print("data0")
    for i in range(5):
        de = DataEvent(event_time, sym, "TRADES", data0)
        sig = strat.calculate_signal(de)
        if sig:
            print(sig)

    print("data1")
    for i in range(5):
        de = DataEvent(event_time, sym, "TRADES", data1)
        sig = strat.calculate_signal(de)
        if sig:
            print(sig)

    def check_deque():
        sdeq = _DWMADeque(40, None)
        sdeq.append(pd.Series([1,10], index=["size", "price"]))
        print(sdeq)
        sdeq.append(pd.Series([1,20], index=["size", "price"]))
        print(sdeq)
        sdeq.append(pd.Series([2,10], index=["size", "price"]))
        print(sdeq)

    # check_deque()