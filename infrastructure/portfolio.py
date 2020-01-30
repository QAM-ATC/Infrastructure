import pandas as pd

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import asdict

from event import DataEvent, FillEvent, Order, Signal
from event_queue import EventQueue
from data_handler import DataHandler
from execution_handler import BacktestExecutionHandler


class Portfolio(ABC):
    @abstractmethod
    def update_fill(self, fill):
        pass

    @abstractmethod
    def send_order_from_signal(self, signal):
        pass


class BacktestPortfolio(Portfolio):
    def __init__(self, queue, data_handler, execution_handler, initial_capital=10000.0):
        self.queue = queue  # event queue
        self.data_handler = data_handler
        self.execution_handler = execution_handler
        self.symbol_list = data_handler.symbol_list

        self.current_orders_dict = {symbol: {} for symbol in self.symbol_list}
        self.current_positions = pd.Series(0, index=self.symbol_list, name=queue.current_time)
        self.current_holdings = self.construct_initial_holdings(initial_capital)  # series

        self.all_orders_list = []
        self.all_positions_list = [pd.Series(0, index=self.symbol_list, name=queue.current_time)]  # list of series
        self.all_holdings_list = [self.construct_initial_holdings(initial_capital)]  # list of series

    @property
    def current_orders(self):
        return pd.DataFrame(self.current_orders_dict)

    @property
    def all_orders(self):
        return pd.DataFrame(self.all_orders_list)

    @property
    def all_positions(self):
        return pd.DataFrame(self.all_positions_list)

    @property
    def all_holdings(self):
        df = pd.DataFrame(self.all_holdings_list)
        df["total"] = df.sum(axis=1)
        return df

    def construct_initial_holdings(self, initial_capital):  # market values of positions
        holdings = {symbol: 0.0 for symbol in self.symbol_list}
        holdings["cash"] = initial_capital
        holdings["commission"] = 0.0
        return pd.Series(holdings, name=self.queue.current_time)

    def update_positions(self, fill):
        self.current_positions.name = self.queue.current_time
        self.current_positions[fill.symbol] += fill.quantity
        self.all_positions_list.append(self.current_positions.copy())

    def update_holdings(self, fill):
        self.current_holdings.name = self.queue.current_time
        self.current_holdings["cash"] -= fill.cost
        self.current_holdings[fill.symbol] = self.current_positions[fill.symbol] * fill.cost
        self.current_holdings["commission"] += fill.commission
        self.all_holdings_list.append(self.current_holdings.copy())

    def update_limit_order_fill(self, fill):
        assert self.current_orders_dict[fill.symbol].get(fill.cost), f"No orders at price {fill.cost}"

        while fill.quantity > self.current_orders_dict[fill.symbol][fill.cost][0]:
            fill.quantity -= self.current_orders_dict[fill.symbol][fill.cost].pop()
            assert self.current_orders_dict[fill.symbol][fill.cost], "Fill quantity > outstanding orders"
        self.current_orders_dict[fill.symbol][fill.cost][0] -= fill.quantity

        if not self.current_orders_dict[fill.symbol][fill.cost][0]:  # if first element in deque == 0:
            self.current_orders_dict[fill.symbol][fill.cost].pop()  # remove that element
            if not self.current_orders_dict[fill.symbol][fill.cost]:  # if deque empty:
                del self.current_orders_dict[fill.symbol][fill.cost]  # remove deque

    def update_fill(self, fill_event):
        self.update_positions(fill_event)
        self.update_holdings(fill_event)
        if fill_event.order_type == "LMT":
            self.update_limit_order_fill(fill_event)

    def risk_check(self):
        return True

    def record_order(self, order, send_time):
        if order.order_type != "MKT":
            if self.current_orders_dict[order.symbol].get(order.price):
                self.current_orders_dict[order.symbol][order.price].append(order.quantity)
            else:
                self.current_orders_dict[order.symbol][order.price] = deque([order.quantity])
        self.all_orders_list.append(pd.Series(asdict(order), name=send_time))

    def send_order_from_signal(self, signal):
        latency_start = pd.Timestamp.utcnow()
        order_type = "MKT"  # currently MKT orders only

        if signal.signal_type == "EXIT":  # saw this in the guide
            direction = ["BUY", "SELL"][self.current_positions[signal.symbol] > 0]  # if currently long
            quantity = int(self.current_positions[signal.symbol] * signal.strength)
        else:
            direction = signal.signal_type
            quantity = int(signal.strength)

        if self.risk_check():
            order = Order(signal.symbol, signal.exchange, order_type, direction, quantity, 0.0)
            send_time = self.queue.current_time + (pd.Timestamp.utcnow() - latency_start)
            self.execution_handler.send_order(order, send_time)
            self.record_order(order, send_time)


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
    port = BacktestPortfolio(eq, dh, eh, init_cap)

    def test_update_fill(port, sym):
        temp = port.update_fill
        port.update_fill = lambda x: None
        et = pd.Timestamp.utcnow()
        fe = FillEvent(et, sym, "BitMEX", "MKT", 10, 5000)
        p0 = port.all_positions
        h0 = port.all_holdings
        port.update_fill(fe)
        h1 = port.all_holdings
        p1 = port.all_positions
        print("holdings:")
        print(h0)
        print(h1)
        print("positions:")
        print(p0)
        print(p1)
        port.update_fill = temp

    def test_send_order_from_signal(port, eq):
        sig = Signal(sym, "BitMEX", "BUY", 1.0)
        port.send_order_from_signal(sig)
        event = eq.get()
        print(event)

    def test_order_recording(port):
        print(port.current_orders)
        o0 = Order(sym, "BitMEX", "LMT", "SELL", 10, 7300)
        o1 = Order(sym, "BitMEX", "LMT", "SELL", 15, 7300)
        o2 = Order(sym, "BitMEX", "LMT", "SELL", 15, 7301)
        port.record_order(o0, pd.Timestamp.utcnow())
        port.record_order(o1, pd.Timestamp.utcnow())
        port.record_order(o2, pd.Timestamp.utcnow())
        print(port.current_orders)
        f0 = FillEvent(pd.Timestamp.utcnow(), sym, "BitMEX", "MKT", 5, 7300)
        f1 = FillEvent(pd.Timestamp.utcnow(), sym, "BitMEX", "MKT", 10, 7300)
        f2 = FillEvent(pd.Timestamp.utcnow(), sym, "BitMEX", "MKT", 10, 7300)
        port.update_fill(f0)
        print(port.current_orders)
        port.update_fill(f1)
        print(port.current_orders)
        port.update_fill(f2)
        print(port.current_orders)

    test_update_fill(port, sym)
    test_send_order_from_signal(port, eq)
    test_order_recording(port)
