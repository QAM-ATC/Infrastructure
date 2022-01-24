import numpy as np
import pandas as pd
import time, datetime
from datetime import datetime
import json
from flask import Flask, request, jsonify
from flask_restful import  reqparse


import yfinance as yf
import pandas as pd

#start flask app
app = Flask(__name__)


parser = reqparse.RequestParser()
parser.add_argument('list', type=list)





def getData(tickers,period='1mo',interval='5d'):
    
    df_list = list()
    for ticker in tickers:
        print(ticker)
        data = yf.download(ticker, group_by="Ticker", period=period,interval=interval)
        data[ticker] = data['Close']  # add this column because the dataframe doesn't contain a column with the ticker
        df_list.append(data[ticker])
    # combine all dataframes into a single dataframe
    df = pd.concat(df_list,axis=1,join="inner")
    return df
def correlationJson(dataFrame):
    correlation_Matrix=dataFrame.corr(method='pearson')
    answer=[]
    correlationInDic=correlation_Matrix.to_dict()
    for i in correlation_Matrix.columns:
        data={}
        data['id']=i
        data['data']=correlationInDic[i]
        data['data']=[]
        for j in  correlationInDic[i]:
            temp={}
            temp['x']=j
            temp['y']=correlationInDic[i][j]
            data['data'].append(temp)
        answer.append(data)
    return jsonify(answer)

    
    


def getValueSeries(data,weights=[0.5,0.5]):
    temp = pd.DataFrame((data*weights).sum(axis=1) / (data*weights).sum(axis=1).iloc[0])
    temp.columns = ['Portfolio']
    temp['timeStamp'] = temp.index
    return temp

@app.route('/stocks')
def debug():
    my_csv = pd.read_csv('stocks.csv')
    column = my_csv.Symbol
    result=jsonify(column.tolist())
    result.headers.add('Access-Control-Allow-Origin', '*')
    return result

# sample url
# http://127.0.0.1:5000/getGraphValue?stocks=SPY&stocks=AAPL&frequency=1d

# https://pypi.org/project/yfinance/
# https://stackoverflow.com/questions/63107594/how-to-deal-with-multi-level-column-names-downloaded-with-yfinance/63107801#63107801
@app.route('/getGraphValue',methods = ['GET'])
def get():
    stocksList=request.args.getlist('stocks')
    frequency=request.args.get('frequency',None)
    period=request.args.get('period',None)
    
    df=getValueSeries(getData(stocksList,period=period,interval=frequency))
    print(df)
    df['timeStamp']=df['timeStamp'].apply(lambda x: (int)(x.timestamp()*1000))
    #df['timeStamp']=pd.to_datetime(df['timeStamp']).astype(int)
    result = df.values.tolist()
    
    result=jsonify(result)
    #resultList=result.values.to
    result.headers.add('Access-Control-Allow-Origin', '*')
    return result


@app.route('/getCorrelation',methods = ['GET'])
def getCorrelation():
    stocksList=request.args.getlist('stocks')
    frequency=request.args.get('frequency',None)
    period=request.args.get('period',None)
    result=correlationJson(getData(stocksList,period=period,interval=frequency))
    result.headers.add('Access-Control-Allow-Origin', '*')
    return result



if __name__ == '__main__':
    print("Starting main loop")
    app.run(debug=True,port=5000,host="127.0.0.1")