from abc import ABC, abstractmethod


class ExecutionHandler(ABC):
    @abstractmethod
    def send_order(self, order):
        pass


class BacktestExecutionHandler(ExecutionHandler):
    def __init__(self, queue, data_handler):
        self.queue = queue
        self.data_handler = data_handler

    def calculate_fill_cost(self, order, reach_time):
        quotes = self.data_handler.lookahead[order.symbol]["QUOTES"].loc[reach_time:].iloc[0]
        if order.order_type == "MKT":
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
        return order.quantity

    def calculate_latency(self, order, send_time):
        # will eventually use self.data_handler.lookahead[order.symbol]["QUOTES"].loc[reach_time:]
        # probably can split into send latency, receive latency
        return pd.Timedelta("3s")

    def send_order(self, order, send_time):
        reach_time = send_time + self.calculate_latency(order, send_time)
        quantity = self.calculate_fill_quantity(order, reach_time)
        cost = self.calculate_fill_cost(order, reach_time)

        fe = FillEvent(reach_time, order.symbol, order.exchange, quantity, cost)
        self.queue.put(fe)


if __name__ == "__main__":
    import pandas as pd

    from event import FillEvent, Order
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

    dh = DataHandler(start_time, all_data)
    eq = EventQueue(start_time)
    eh = BacktestExecutionHandler(eq, dh)
    order = Order(sym, "BitMEX", "MKT", "BUY", 10, 0)

    eh.send_order(order, start_time)
    print(eq.get())
