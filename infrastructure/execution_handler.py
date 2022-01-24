import pandas as pd

from abc import ABC, abstractmethod

from event import FillEvent, Order
from event_queue import EventQueue
from data_handler import DataHandler

class ExecutionHandler(ABC):
    @abstractmethod
    def send_order(self, order):
        pass


class BacktestExecutionHandler(ExecutionHandler):
    def __init__(self, queue, data_handler):
        self.queue = queue
        self.data_handler = data_handler

    def calculate_fill_cost(self, order, reach_time):
        if order.order_type == "MKT":
            try:
                quotes = self.data_handler.lookahead[order.symbol]["QUOTES"].loc[reach_time:].iloc[0]
            except:
                return order.price
            if order.direction == "BUY":
                fill_price = quotes["askPrice"]
            else:
                fill_price = quotes["bidPrice"]
            return order.quantity * fill_price
        else:
            # will need self.data_handler.lookahead[order.symbol]["QUOTES"].loc[reach_time:] too
            return order.price

    def calculate_fill_quantity(self, order, reach_time):
        # for non-market orders
        return int(order.quantity)

    def calculate_latency(self, order, send_time):
        # will eventually use self.data_handler.lookahead[order.symbol]["QUOTES"].loc[reach_time:]
        # probably can split into send latency, receive latency
        return pd.Timedelta("3s")

    def send_order(self, order, send_time):
        reach_time = send_time + self.calculate_latency(order, send_time)
        sign = [1, -1][order.direction == "SELL"]
        quantity = sign * self.calculate_fill_quantity(order, reach_time)
        cost = sign * self.calculate_fill_cost(order, reach_time)
        # will need to figure out how the fills and orders work for each exchange
        fe = FillEvent(reach_time, order.symbol, order.exchange, order.order_type, quantity, cost)
        self.queue.put(fe)


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

    dh = DataHandler(start_time, all_data)
    eq = EventQueue(start_time)
    eh = BacktestExecutionHandler(eq, dh)
    order = Order(sym, "BitMEX", "MKT", "BUY", 10, 0)

    eh.send_order(order, start_time)
    print(eq.get())
