import pandas as pd

import sys
import time

from itertools import islice
from event_queue import EventQueue
from data_handler import DataHandler
from strategy import DollarWeightedMACD
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

def simulate_future_data(future_data, batch_size):
    for i in range(0, len(future_data), batch_size):
        yield future_data[i: i + batch_size]
        print(f"{i}/{len(future_data)}")

def main():
    if len(sys.argv) > 1:
        trades_csv_path = sys.argv[1]
    else:
        trades_csv_path = "play_data/XBTUSD_trades_191214_0434.csv"
    df = read_trades_csv(trades_csv_path)
    start_time = df.index[5]
    all_data = {"df_table": df}

    data_handler = DataHandler(start_time, all_data)
    future_data = data_handler.get_future_data(all_data, start_time)
    batch_size = 1
    future_data_generator = simulate_future_data(future_data, batch_size)
    event_queue = EventQueue(start_time)
    portfolio = BacktestPortfolio()
    strat = DollarWeightedMACD(data_handler.read_table("df_table"))

    empty_future_data = False
    while True:
        if not empty_future_data:
            try:
                new_data_events_from_broker = next(future_data_generator)
            except:
                empty_future_data = True
        print(new_data_events_from_broker)
        for new_data_event in new_data_events_from_broker:
            data_handler.update_data(new_data_event)
            event_queue.put(new_data_event)
        while event_queue.qsize() != 0:
            event = event_queue.get()
            if event.type == 'DATA':
                if strat.generate_signal(event.data.size, event.data.price) == 1:
                    print(True)
                    sys.exit()
        #time.sleep(2)

        

    # print(dwmacd.generate_signal(100000, 7500))
    # print(dwmacd.generate_signal(200000, 7000))
    # print(dwmacd.generate_signal(100000, 7000))
    # print(dwmacd.generate_signal(100000, 8000))


if __name__ == "__main__":
    main()