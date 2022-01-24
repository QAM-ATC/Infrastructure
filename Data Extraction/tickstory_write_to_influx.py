# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 00:51:55 2020

@author: User
"""

import pandas as pd
import strict_rfc3339 as rfc
from influxdb import InfluxDBClient
client = InfluxDBClient(host='localhost', port=8086)


def write_points_from_csv_to_influx(filename: str, symbol: str):
    #filename - e.g. "EURUSD_Ticks_06.01.2017-06.01.2017.csv" (with .csv extension)
    #symbol - instrument pair e.g. "EURUSD"
    try:
        df = pd.read_csv(filename, header=0, dtype='str')
        print("df.shape", df.shape)
    except: 
        return
    print("df.shape" , df.shape)
    print("df size", df.count())
    print(df.head())
    bid = df.iloc[:,2]
    ask = df.iloc[:,1]
    bid_vol = df.iloc[:,4]
    ask_vol = df.iloc[:,3]
    time = df.iloc[:,0]
    lines = [] 
    
    for d in range(len(df)) :
        timestamp = str(rfc.rfc3339_to_timestamp(time[d][:4]+'-'+time[d][4:6]+'-'+time[d][6:8]+'T'+time[d][9:17]+"."+time[d][18:]+"000000Z"))
        len_stamp = len(timestamp)
        timestamp = timestamp[:10]+timestamp[11:len_stamp]+'0'*(20-len_stamp)
        lines.append(symbol  + ",type="+symbol
             + " "
             + "bid=" + bid[d] + ","
             + "ask=" + ask[d] + ","
             + "bid_vol=" + bid_vol[d] + ","
             + "ask_vol=" + ask_vol[d] + " "
             + timestamp)
    
    print(str(len(lines)) + " lines")
    thefile = open(filename[:-4] + '.txt', 'x', newline='')
    
    
    for item in lines:
        thefile.write(item+'\n')
        
    thefile.close()
    
    # write to influx
    client.write_points(lines, database='dukascopy', time_precision='n', batch_size=10000, protocol='line')
