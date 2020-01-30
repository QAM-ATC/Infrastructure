import pandas as pd

from functools import total_ordering

from event import DataEvent


@total_ordering
class DataEventGenerator:
    # maybe there's a simpler way of doing this
    def __init__(self, symbol, table_name, df):
        self.symbol = symbol
        self.table_name = table_name

        self.iterrows_gen = df.iterrows()
        _, self.curr_series = next(self.iterrows_gen)
        self.not_empty = True

    def __bool__(self):
        return self.not_empty

    def __eq__(self, other):
        return self.curr_time == other.curr_time

    def __lt__(self, other):
        return self.curr_time < other.curr_time

    @property
    def curr_time(self):
        return self.curr_series.name

    def get_earliest_event(self):
        out = self.curr_series
        try:
            _, self.curr_series = next(self.iterrows_gen)
        except StopIteration:
            self.not_empty = False
        return DataEvent(out.name, self.symbol, self.table_name, out)


class DataHandler:
    def __init__(self, start_time, all_data):
        self.start_time = start_time
        self.lookahead = all_data  # naming to prevent accidental lookahead bias
        self.past_data_dict = self.split_past_data()  # dict of lists of series
        self.symbol_list = list(self.past_data_dict.keys())

    def split_past_data(self):
        past_data = {}
        for symbol, sym_dic in self.lookahead.items():  # for each symbol
            past_data[symbol] = {}
            for table_name, df in sym_dic.items():  # for each table
                past_data[symbol][table_name] = [row for _, row in df[:self.start_time].iterrows()]
                # can't get .apply() to work, it keeps appending the same duplicate value
        return past_data

    def read_table(self, symbol, table_name):
        return pd.DataFrame(self.past_data_dict[symbol][table_name])

    def update_data(self, data_event):
        self.past_data_dict[data_event.symbol][data_event.table_name].append(data_event.data)

    def get_future_data_generator(self):
        # overall, this method 3 seconds slower than the list method for getting future data
        # makes sense because this will only be faster if queue insertions are taking a long time
        # I might have accidentally prematurely optimised here but I think this will be useful
        # in the future when we deal with more tick data sources for longer durations, insertions take a while
        de_gen_list = []
        for symbol, sym_dic in self.lookahead.items():  # for each symbol
            for table_name, df in sym_dic.items():  # for each table
                de_gen_list.append(DataEventGenerator(symbol, table_name, df[self.start_time:]))

        while de_gen_list:
            out = min(de_gen_list).get_earliest_event()
            de_gen_list = [i for i in de_gen_list if i]  # removes empty generators
            yield out

    def get_future_data_list(self):
        future_data = []  # to be inserted into queue
        for symbol, sym_dic in self.lookahead.items():  # for each symbol
            for table_name, df in sym_dic.items():  # for each table
                ir = df[self.start_time:].iterrows()
                data_events = [DataEvent(data.name, symbol, table_name, data) for _, data in ir]
                future_data.extend(data_events)
        return future_data


if __name__ == "__main__":
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

    def main():
        trades_csv_path = "play_data/XBTUSD_trades_191214_0434.csv"
        quotes_csv_path = "play_data/XBTUSD_quotes_191214_0434.csv"

        tdf = read_trades_csv(trades_csv_path).iloc[:2000]
        qdf = read_quotes_csv(quotes_csv_path)
        qdf = qdf.loc[:tdf.index[-1]]

        start_time = tdf.index[0]
        symbol = "XBTUSD"

        all_data = {}
        all_data[symbol] = {}
        all_data[symbol]["TRADES"] = tdf
        all_data[symbol]["QUOTES"] = qdf

        curr_time = pd.Timestamp.utcnow()

        dh = DataHandler(start_time, all_data)

        def test_split_past_data_and_read_table(dh):
            tdf = read_trades_csv(trades_csv_path).iloc[:2000]
            t0 = tdf[:start_time]
            t1 = dh.read_table(symbol, "TRADES")
            assert (t0 - t1).sum().sum() == 0, f"sum = {(t0 - t1).sum().sum()}"
            print("DataHandler.split_past_data() and DataHandler.read_table() okay")

        def test_update_data(dh):
            vals = [420, 69]
            data = pd.Series(vals, index=tdf.columns, name=curr_time - pd.Timedelta("1s"))
            d = DataEvent(curr_time, symbol, "TRADES", data)
            dh.update_data(d)
            t1 = dh.read_table(symbol, "TRADES")
            t2 = dh.read_table(symbol, "TRADES")
            assert 0 == (t2.iloc[:-1] - t1).sum().sum() and (t2.iloc[-1].tolist() == vals)
            print("DataHandler.update_data() okay")

        def test_get_future_data(dh):
            future_data = dh.get_future_data_list()
            curr_time = None
            curr_table = None
            count = 0

            for data_event in future_data:
                count += 1
                prev_time = curr_time
                prev_table = curr_table
                assert type(data_event) == DataEvent, "wrong event"
                assert type(data_event.data) == pd.Series or type(data_event.data) == pd.DataFrame, "wrong data"
                curr_time = data_event.data.name
                curr_table = data_event.table_name

                if curr_time and prev_time and curr_table == prev_table:
                    assert curr_time >= prev_time, "not sorted"

            print("DataHandler.get_future_data_list() okay")

        def test_data_generator(dh):
            data_gen = dh.get_future_data_generator()
            curr_time = None
            count = 0

            for data_event in data_gen:
                count += 1
                prev_time = curr_time
                assert type(data_event) == DataEvent, "wrong event"
                assert type(data_event.data) == pd.Series or type(data_event.data) == pd.DataFrame, "wrong data"
                curr_time = data_event.data.name
                if curr_time and prev_time:
                    assert curr_time >= prev_time, "not sorted"

            assert len(tdf[start_time:]) + len(qdf[start_time:]) == count, "length mismatch"
            print("DataHandler.get_data_event_generators() okay")

        test_split_past_data_and_read_table(dh)
        test_update_data(dh)
        test_get_future_data(dh)
        test_data_generator(dh)
        print("DataHandler okay")

    main()
