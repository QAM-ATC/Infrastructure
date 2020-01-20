import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import time

from itertools import islice
from event_queue import EventQueue
from data_handler import DataHandler
from strategy import DollarWeightedMACD, SimpleDollarWeightedMACD
from execution_handler import BacktestExecutionHandler
from portfolio import BacktestPortfolio

def read_trades_csv(trades_csv_path):
    df = pd.read_csv(
        trades_csv_path,
        usecols=[
            "received",
            "size",
            "price"
        ],
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

def simulate_future_data(future_data, batch_size):
    for i in range(0, len(future_data), batch_size):
        yield future_data[i: i + batch_size]
        print(f"{i}/{len(future_data)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        trades_csv_path = sys.argv[1]
    else:
        trades_csv_path = "play_data/XBTUSD_trades_191214_0434.csv"
        quotes_csv_path = "play_data/XBTUSD_quotes_191214_0434.csv"

    class Timer:
        def start(self, message):
            print(message, end=" ")
            self.starting_time = pd.Timestamp.utcnow()

        def stop(self):
            print(pd.Timestamp.utcnow()-self.starting_time)

    timer = Timer()

    timer.start("reading quotes")
    tdf = read_trades_csv(trades_csv_path)
    timer.stop()

    timer.start("reading trades")
    qdf = read_quotes_csv(quotes_csv_path)
    qdf = qdf.loc[:tdf.index[-1]]
    timer.stop()

    start_time = tdf.index[1500]

    symbol = "XBTUSD"

    all_data = {}
    all_data[symbol] = {}
    all_data[symbol]["TRADES"] = tdf
    all_data[symbol]["QUOTES"] = qdf

    timer.start("initializing data_handler")
    data_handler = DataHandler(start_time, all_data)
    timer.stop()

    timer.start("initializing event_queue")
    event_queue = EventQueue(start_time)
    timer.stop()

    timer.start("initializing execution_handler")
    execution_handler = BacktestExecutionHandler(event_queue, data_handler)
    timer.stop()

    timer.start("initializing portfolio")
    portfolio = BacktestPortfolio(event_queue, data_handler, execution_handler)
    timer.stop()

    timer.start("initializing strat")
    strat = SimpleDollarWeightedMACD(event_queue, data_handler)
    timer.stop()

    # batch_size = 1
    # future_data_generator = simulate_future_data(future_data, batch_size)
    timer.start("getting future data")  # bottleneck
    future_data = data_handler.get_future_data(all_data, start_time)
    timer.stop()

    timer.start("loading queue")
    event_queue.update_future_data(future_data)
    timer.stop()

    # empty_future_data = False
    # while True:
    #     if not empty_future_data:
    #         try:
    #             new_data_events_from_broker = next(future_data_generator)
    #         except:
    #             empty_future_data = True
    #     print(new_data_events_from_broker)
    #     for new_data_event in new_data_events_from_broker:
    #         data_handler.update_data(new_data_event)
    #         event_queue.put(new_data_event)
    #     while event_queue.qsize() != 0:
    #         event = event_queue.get()
    #         if event.type == 'DATA':
    #             if strat.generate_signal(event.data.size, event.data.price) == 1:
    #                 print(True)
    #                 sys.exit()
    #     #time.sleep(2)

    while not event_queue.empty():
        event = event_queue.get(False)
        if event.type == "DATA":
            sig = strat.calculate_signal(event)
            if sig:
                sig.signal_type = ["SELL", "BUY"][sig.signal_type != "BUY"]
                portfolio.send_order_from_signal(sig)
        elif event.type == "FILL":
            portfolio.update_fill(event)

    print(portfolio.all_orders)
    print(portfolio.all_holdings)
    print(portfolio.all_positions)
    portfolio.all_holdings.plot()
