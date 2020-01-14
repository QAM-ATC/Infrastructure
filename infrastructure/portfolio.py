from abc import ABC, abstractmethod

class Portfolio(ABC):
    @abstractmethod
    def update_fill(self):
        pass

    @abstractmethod
    def send_order_from_signal(self):
        pass

class BacktestPortfolio(Portfolio):
    def __init__(self, queue, data_handler, initial_capital=10000.0):
        self.queue = queue  # event queue
        self.data_handler = data_handler
        self.symbol_list = data_handler.symbol_list

        self.all_positions_list = [pd.Series(0, index=self.symbol_list, name=queue.current_time)]  # list of series
        self.all_holdings_list = [self.construct_initial_holdings(initial_capital)]  # list of series
        
        self.current_positions = pd.Series(0, index=self.symbol_list, name=queue.current_time)
        self.current_holdings = self.construct_initial_holdings(initial_capital)  # series

    @property
    def all_positions(self):
        return pd.DataFrame(self.all_positions_list)
    
    @property
    def all_holdings(self):
        return pd.DataFrame(self.all_holdings_list)
    
    def construct_initial_holdings(self, initial_capital):  # market values of positions
        holdings = {symbol: 0.0 for symbol in self.symbol_list}
        holdings["cash"] = initial_capital
        holdings["commission"] = 0.0
        holdings["total"] = initial_capital
        return pd.Series(holdings, name=self.queue.current_time)
    
    def update_positions(self, fill_event):
        # maybe can split position and holding updates
        self.current_positions.name = self.queue.current_time
        self.current_positions[fill_event.symbol] += fill_event.quantity
        self.all_positions_list.append(self.current_positions.copy())

    def update_holdings(self, fill_event):
        self.current_holdings.name = self.queue.current_time
        self.current_holdings["cash"] -= fill_event.cost
        self.current_holdings[fill_event.symbol] = self.current_positions[fill_event.symbol] * fill_event.cost
        self.current_holdings["commission"] += fill_event.commission
        self.all_holdings_list.append(self.current_holdings.copy())

    def update_fill(self, fill_event):
        self.update_positions(fill_event)
        self.update_holdings(fill_event)
        
    def risk_check(self):
        return True

    def send_order_from_signal(self, signal):
        latency_start = pd.Timestamp.utcnow()
        order_type = "MKT"  # currently MKT orders only
        if signal.signal_type == "EXIT":
            if self.current_positions[signal.symbol] < 0:
                direction = "BUY"
            else:
                direction = "SELL"
        else:
            direction = signal.signal_type
            
        quantity = int(10 * signal.strength)
        price = 0.0  # MKT order
        
        if self.risk_check():
            order = Order(signal.symbol, signal.exchange, order_type, direction, quantity, price)
            send_time = self.queue.current_time + pd.Timestamp.utcnow() - latency_start
            self.generate_fill_from_order(order, send_time)

    def calculate_fill_cost(self, order, fill_time):
        quotes = self.data_handler.lookahead[order.symbol]["QUOTES"].loc[fill_time:].iloc[0]
        if order.order_type == "MKT":
            if order.direction == "BUY":
                fill_price = quotes["askPrice"]
            else:
                fill_price = quotes["bidPrice"]
            return order.quantity * fill_price
        else:
            return order.price

    def calculate_fill_quantity(self, order, fill_time):
        # for non-market orders
        return order.quantity

    def calculate_latency(self, order, send_time):
        # will eventually be a function of volume as well
        return pd.Timedelta("3s")

    def generate_fill_from_order(self, order, send_time):
        fill_time = send_time + self.calculate_latency(order, send_time)
        quantity = self.calculate_fill_quantity(order, fill_time)
        cost = self.calculate_fill_cost(order, fill_time)

        fe = FillEvent(fill_time, order.symbol, order.exchange, quantity, cost)
        self.queue.put(fe)


if __name__ == "__main__":
    import pandas as pd
    from event import DataEvent, FillEvent, Order, Signal
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
    port = BacktestPortfolio(eq, dh, init_cap)

    def check_update_fill(port, sym):
        et = pd.Timestamp.utcnow()
        exchange, quantity, cost = "BitMEX", 10, 5000
        fe = FillEvent(et, sym, exchange, quantity, cost)
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

    # check_update_fill(port, fe)

    def check_send_order_from_signal(port, eq):
        exchange, type, strength = "BitMEX", "BUY", 1.0
        sig = Signal(sym, exchange, type, strength)

        port.send_order_from_signal(sig)
        event = eq.get()
        print(event)

    # check_send_order_from_signal(port, eq)

