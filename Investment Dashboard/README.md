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
