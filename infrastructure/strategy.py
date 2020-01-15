import numpy as np
import pandas as pd

from abc import ABC, abstractmethod
from dataclasses import dataclass


class Strategy(ABC):
    @abstractmethod
    def generate_signal(self):
        pass


class DollarWeightedMACD(Strategy):
    def __init__(self, queue, data_handler):
        self.queue = queue
        self.data_handler = data_handler

        self.symbol = "XBTUSD"
        self.exchange = "BitMEX"
        group_width = 680850400  # arbitrary, eventually can dynamically adjust
        short_ma, long_ma = 5, 10  # maybe can EWM but will need more parameters
        tdf = self.data_handler.read_table(self.symbol, "TRADES")
        self.ddf, curr_bar = self.make_dwap_df_and_curr_bar(tdf, group_width)

        ma_vals = self.ddf["dwap"].values[-long_ma:]
        increasing = ma_vals[-short_ma:].sum() / short_ma > ma_vals.sum() / long_ma
        rem_width = group_width - (tdf["dollars"].cumsum().values % group_width)[-1]

        self.cache = self.DWMCache(ma_vals, increasing, curr_bar, rem_width)
        self.params = self.DWMParameters(group_width, short_ma, long_ma)

    @dataclass
    class DWMParameters:
        __slots__ = "group_width", "short_ma_window", "long_ma_window"
        group_width: float
        short_ma_window: int
        long_ma_window: int

    @dataclass
    class DWMCache:
        __slots__ = "ma_vals", "increasing", "curr_bar", "remaining_width"
        ma_vals: np.array  # each element is dwap, for each item in the window
        increasing: bool  # used to check direction changes to prevent duplicates
        curr_bar: pd.DataFrame  # columns: size, price, dollars
        remaining_width: float  # when curr bar full, update MAs

    def make_dwap_df_and_curr_bar(self, df, group_width):
        df["dollars"] = df["size"] * df["price"]
        df["group"] = (df["dollars"].cumsum() // group_width)  # will be affected by different initial conditions
        new_series = {}  # timestamp : dollar weighted average price

        for grp, gdf in df.groupby("group"):
            timestamp = gdf.index[-1]  # last timing, prevent lookahead
            dwap = (gdf["dollars"].values * gdf["price"].values).sum() / gdf["dollars"].values.sum()
            if grp == df["group"].max():
                curr_bar = gdf[["size", "price", "dollars"]].values  # for cache
            new_series[timestamp] = dwap

        ddf = pd.Series(new_series, name="dwap").to_frame()
        return ddf, curr_bar

    def generate_signal(self, data_event):
        # also updates cache, inefficient
        # should rewrite such that chache update is separate
        # needs to be updated such that it uses Signal objects

        new_row = np.array([[
            data_event.data["size"],
            data_event.data["price"],
            data_event.data["size"] * data_event.data["price"]
        ]])

        print(self.cache.ma_vals.sum() / self.params.long_ma_window)
        print(self.cache.ma_vals[-self.params.short_ma_window:].sum() / self.params.short_ma_window)

        self.cache.remaining_width -= new_row[0, 2]
        # print(self.cache.curr_bar)

        if self.cache.remaining_width > 0:  # old bar, update last val
            self.cache.curr_bar = np.append(self.cache.curr_bar, new_row, axis=0)

        else:  # new bar, does not account big txn that exceeds group width
            self.cache.remaining_width += self.params.group_width
            self.cache.curr_bar = new_row
            self.cache.ma_vals = np.roll(self.cache.ma_vals, -1)

        # print(self.cache.curr_bar)
        self.cache.ma_vals[-1] = ((self.cache.curr_bar[:, 1] * self.cache.curr_bar[:, 2]).sum()
                                  / self.cache.curr_bar[:, 2].sum())

        long_sma = self.cache.ma_vals.sum() / self.params.long_ma_window
        short_sma = self.cache.ma_vals[-self.params.short_ma_window:].sum() / self.params.short_ma_window

        print(long_sma)
        print(short_sma)

        new_inc = bool(short_sma > long_sma)
        old_inc = self.cache.increasing
        self.cache.increasing = new_inc

        signal_types = "SELL", "BUY"
        out = [None, None]
        # old_inc1=inc: direction change
        out[bool(old_inc == new_inc)] = Signal(self.symbol, self.exchange, signal_types[new_inc], 1.0)
        return out[0]

    def update_cache(self, size, price):
        # currently done inside generate signal
        print("updating cache")
        return None

    def update_parameters(self, df):
        # assumes df will be updated with all the relevant data
        print("updating parameters")
        return None


if __name__ == "__main__":
    from event import DataEvent, Signal
    from event_queue import EventQueue
    from data_handler import DataHandler


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

    # future_data = dh.get_future_data(all_data, start_time)
    # eq.update_future_data(future_data)

    strat = DollarWeightedMACD(eq, dh)

    data = pd.Series([10000, -200000], index=["size", "price"], name=tdf.index[1501])

    event_time = tdf.index[1501]
    de = DataEvent(event_time, sym, "TRADES", data)
    sig = strat.generate_signal(de)