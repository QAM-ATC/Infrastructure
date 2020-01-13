import pandas as pd

from event import DataEvent

class DataHandler:
    def __init__(self, start_time, all_data):
        self.past_data_dict = self.split_past_data(all_data, start_time)  # dict of lists of series
    
    def split_past_data(self, all_data, start_time):
        past_data = {}
        for table_name, df in all_data.items():  # for each table
            past_data[table_name] = []
            for _, row in df[:start_time].iterrows():  # for each row
                past_data[table_name].append(row)
        return past_data
    
    def read_table(self, table_name):
        return pd.DataFrame(self.past_data_dict[table_name])
        
    def get_future_data(self, all_data, start_time):
        future_data = [] # to be inserted into queue
        for table_name, df in all_data.items():  # for each table
            for event_time, data in df[start_time:].iterrows():  # for each row
                future_data.append(DataEvent(event_time, table_name, data))
        return future_data
    
    def update_data(self, data_event):
        table = data_event.table_name
        data = data_event.data
        self.past_data_dict[table].append(data)
        return None