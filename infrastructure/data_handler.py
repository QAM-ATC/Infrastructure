import pandas as pd
from event import DataEvent


class DataHandler:
    def __init__(self, start_time, all_data):
        """
        Args:
            all_data (dict): {symbol: {table_name: pd.DataFrame}}
            start_time (pd.Timestamp):
        """
        self.lookahead = all_data
        self.past_data_dict = self.split_past_data(all_data, start_time)  # dict of lists of series
        self.symbol_list = list(self.past_data_dict.keys())

    def split_past_data(self, all_data, start_time):
        past_data = {}
        for symbol, sym_dic in all_data.items():  # for each symbol
            past_data[symbol] = {}
            for table_name, df in sym_dic.items():  # for each table
                past_data[symbol][table_name] = [row for (_, row) in df[:start_time].iterrows()]
                # can't get .apply() to work, it keeps appending the same duplicate value
        return past_data

    def read_table(self, symbol, table_name):
        return pd.DataFrame(self.past_data_dict[symbol][table_name])

    def update_data(self, data_event):
        self.past_data_dict[data_event.symbol][data_event.table_name].append(data_event.data)

    def get_future_data(self, all_data, start_time):
        future_data = []  # to be inserted into queue
        for symbol, sym_dic in all_data.items():  # for each symbol
            for table_name, df in sym_dic.items():  # for each table
                for event_time, data in df[start_time:].iterrows():  # for each row
                    future_data.append(DataEvent(event_time, symbol, table_name, data))
        return future_data


if __name__ == "__main__":

    def read_trades_csv(trades_csv_path):
        out_df = pd.read_csv(
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
        return out_df


    def main():
        trades_csv_path = "play_data/XBTUSD_trades_191214_0434.csv"

        df = read_trades_csv(trades_csv_path)
        start_time = df.index[1500]
        curr_time = pd.Timestamp.utcnow()

        symbol, table = "XBTUSD", "TRADES"

        all_data = {}
        all_data[symbol] = {}
        all_data[symbol][table] = df

        dh = DataHandler(start_time, all_data)

        t0 = df[:start_time]
        t1 = dh.read_table(symbol, table)

        # testing dh.split_past_data(), dh.read_table()
        assert (t0 - t1).sum().sum() == 0, f"sum = {(t0 - t1).sum().sum()}"

        vals = [420, 69]
        data = pd.Series(vals, index=df.columns, name=curr_time - pd.Timedelta("1s"))
        d = DataEvent(curr_time, symbol, table, data)
        dh.update_data(d)
        t2 = dh.read_table(symbol, table)

        # testing dh.update_data()
        assert 0 == (t2.iloc[:-1] - t1).sum().sum() and (t2.iloc[-1].tolist() == vals)

        future_data = dh.get_future_data(all_data, start_time)
        for i in future_data[:5]:
            assert type(i) == DataEvent
            assert i.symbol == symbol
            assert i.table_name == table
            assert type(i.data) == pd.Series or type(i.data) == pd.DataFrame
        print("DataHandler okay")


    main()
