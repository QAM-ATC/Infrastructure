the first step is to have an API in to fetch all equities data for all our equity indices (if i'm not wrong yahoo finance has one)

So this would include like MSCII World, MSCI EM, Asia Pacific ex Jap, China Onshore, China Offshore... 

From the  data, we can then find out the relevant indicators we want:
1) Sharpe Ratio
2) Sortino Ratio
3) Fwd P/E against consensus
4) 1Y & 3Y returns
5) Correlation
...

after which, we can have a summary sheet that has the top maybe 2-3 indices that has the best risk adjusted returns, is still relatively inexpensive, and hopefully provides the best diversification benefits due to the indicators mentioned above.

useful data visualisations will be needed to filter through all these ticker information
 
From here, we can then do an optimal solver to create an efficient frontier with the % optimal weightages.




# task 
1.select 10 historical  from yahoo(https://finance.yahoo.com/quote/MSFT/history?period1=1600443604&period2=1631979604&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true)  combine them to be the single csv file with with column name as name of ticker and index as timestamps(eg Sep 17,2021)

overall frame of the website and different session

2, api 1 

3: api2 and covariance matrix visualization

4: portfolio Value visulization using final Data  https://www.highcharts.com/demo/stock/basic-line 
5: gui for setting global variable


# backend API 

api 1: retrieve finalData using frequency, historical period,tickerweight,tickers as parameter.  return data in this format:
[[1568813400000,55.69]....]

api 2  : getCovarianceMatrix() 







# structure 

global variable:

data: csv file with header, convert into pandas.core.frame.DataFrame. 

tickers:list of string(stock chosen)

tickerweight: dictionary of stock name and its weight

historical period:  last n month

frequency: daily, weekly, monthy // average out the data or what??

finalData: list of 2-element list eg [[1568813400000,55.69]....]



# technology 
python flask as backend

front end: highcharts library, react 

https://quant-risk.readthedocs.io/en/latest/#portfolio 

