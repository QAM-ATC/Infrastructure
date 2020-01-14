class Portfolio(ABC):
    @abstractmethod
    def update_fill(self):
        pass
    
    @abstractmethod
    def send_order_from_signal(self):
        pass
    
class BacktestPortfolio(Portfolio):
    def __init__(self, queue, symbol_list, all_data, initial_capital=10000.0):
        self.queue = queue  # event queue
        self.symbol_list = symbol_list 
        self.initial_capital = initial_capital
        
        start_time = self.queue.current_time
        self.all_positions_list = [pd.Series(0, index=symbol_list, name=start_time)]  # list of series
        self.all_holdings_list = [self.construct_current_holdings()]  # list of series
        
        self.current_positions = pd.Series(0, index=symbol_list, name=start_time)
        self.current_holdings = self.construct_current_holdings()  # series

    @property
    def all_positions(self):
        return pd.DataFrame(self.all_positions_list)
    
    @property
    def all_holdings(self):
        return pd.DataFrame(self.all_holdings_list)
    
    def construct_current_holdings(self):  # market values of positions
        holdings = {symbol: 0.0 for symbol in symbol_list}
        holdings["capital"] = self.initial_capital
        holdings["commission"] = 0.0
        holdings["total"] = self.initial_capital
        return pd.Series(holdings, name=self.queue.current_time)
    
    def update_fill(self, fill):
        # maybe can split position and holding updates
        self.current_positions.name = self.queue.current_time
        self.current_positions[fill.symbol] += fill.quantity
        self.all_positions_list.append(self.current_positions.copy())
        
        self.current_holdings.name = self.queue.current_time
        self.current_holdings["capital"] -= fill.cost
        # assuming constant prices between txns
        self.current_holdings[fill.symbol] = self.current_positions[fill.symbol] * fill.cost
        self.current_holdings["commission"] += fill.commission
        self.all_holdings_list.append(self.current_holdings.copy())
        
    def risk_check(self):
        return True
    
    def calculate_order_price(self, order_type):
        # relevant to limit orders
        if order_type == "MKT":
            return 0.0
        return 0.0
    
    def send_order_from_signal(self, sig):
        order_type = "MKT"
        if sig.signal_type == "EXIT":
            if self.current_positions[signal.symbol] < 0:
                direction = "BUY"
            else:
                direction = "SELL"
        else:
            direction = sig.signal_type
            
        quantity = int(10 * sig.strength)
        price = self.calculate_order_price(order_type)
        
        if self.risk_check():
            self.generate_fill_from_order(
                Order(sig.symbol, sig.exchange, order_type, direction, quantity, price)
            )
    
    def calculate_fill_cost(self, order):
        fill_price = 7000  # will eventually use future data
        return order.quantity * fill_price

    def calculate_fill_quantity(self, order):
        return order.quantity  # assumes 100% fill
    
    def calculate_latency(self, order):
        return pd.Timedelta("3s")
    
    def generate_fill_from_order(self, order):
        event_time = self.queue.current_time + self.calculate_latency(order)
        quantity = self.calculate_fill_quantity(order)
        cost = self.calculate_fill_cost(order)
        
        fill = FillEvent(event_time, order.symbol, order.exchange, quantity, cost)
        self.queue.put(fill)