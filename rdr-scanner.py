
# RDR scanner based on https://www.t3live.com/blog/scott-redler-rdr-fast-cash-lesson-one/
# 
# Looks at stocks with market cap > 1B
# 
# TODO: use websocket to poll current-price of ticker so the alerting can happen immediately when the price is reclaimed
# TODO: add email/text alerting
#

from numpy import NaN
import yfinance as yf
from datetime import date, timedelta
import datetime as dt
import websocket
import json


f = open("stock-data-all.csv", "r")
stocks = ""
for x in f:
    stock = x.split(",")[0].strip()
    stocks = stocks + " " + stock

print (stocks)

global data 

today = date.today()
start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
end = (today - timedelta(days=0)).strftime("%Y-%m-%d")
print("start = %s, end = %s" % (start, end))
data = yf.download(stocks, start=start, end=end, interval = "1d", auto_adjust = True, group_by='ticker')
print(data)
print("Total number of rows = %d" % len(data))


global consecutiveRed
consecutiveRed = False

try: 
    n = 0
    f = open("trades.txt", "a")

    while n < len(data.columns):
        stock = data.columns[n][0]
        for i in range(1, len(data)-1):
            # size = len(data.columns) / 5
            close = data[stock]["Close"][i]
            prevClose = data[stock]["Close"][i-1]
            open = data[stock]["Open"][i]

            if close == NaN:
                break

            # A red candlestick is a price chart indicating that the closing price of a security is below both 
            # the price at which it opened and previously closed.
            if (close < open and close < prevClose):
                isConsectuiveRed = True
            else:
                isConsectuiveRed = False
                # print ("\t %s: %s" %(stock, isConsectuiveRed))
                break
        
        n = n + 5       # there are 5 elements in the dataframe
        if isConsectuiveRed == True:
            # print("Is consecutive red for %s: %s"  % (stock, isConsectuiveRed))
            # print ("\tDEBUG: CLOSE (%f) < OPEN (%f) and CLOSE (%f) < PREV-CLOSE (%f)" % (close, open, close, prevClose))
            prevDayLow = data[stock]["Low"][len(data)-2]
            ticker = yf.Ticker(stock).info      # Get current price
            if ticker['dayLow'] < prevDayLow and ticker['regularMarketPrice'] < prevDayLow:
                f.write("FOUND RDR. Needs to reclaim %f for %s. Current price: %f\n" % (prevDayLow, stock, ticker['regularMarketPrice']))
                print("\t--->> FOUND RDR. Needs to reclaim %f for %s. Current price: %f" % (prevDayLow, stock, ticker['regularMarketPrice']))

except:
    print("Error")
