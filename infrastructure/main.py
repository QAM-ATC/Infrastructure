import pandas as pd

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
        # nrows=30000
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

def main():
    if len(sys.argv) > 1:
        trades_csv_path = sys.argv[1]
    else:
        trades_csv_path = "play_data/XBTUSD_trades_191214_0434.csv"

    tdf = read_trades_csv(trades_csv_path)
    start_time = tdf.index[5]

    symbol = "XBTUSD"

    all_data = {}
    all_data[symbol] = {}
    all_data[symbol]["TRADES"] = tdf

    data_handler = DataHandler(start_time, all_data)
    event_queue = EventQueue(start_time)
    execution_handler = BacktestExecutionHandler(event_queue, data_handler)
    portfolio = BacktestPortfolio(event_queue, data_handler, execution_handler)
    strat = SimpleDollarWeightedMACD(event_queue, data_handler)

    # batch_size = 1
    # future_data_generator = simulate_future_data(future_data, batch_size)

    future_data = data_handler.get_future_data(all_data, start_time)
    event_queue.update_future_data(future_data)

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
        if event.type == 'DATA':
            signal = strat.calculate_signal(event)
            if signal:
                print(signal)
    print("end")
if __name__ == "__main__":
    main()