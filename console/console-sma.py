#!/home/seungyong/zipline/bin/python3

from datetime import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt
from zipline.api import order_target, record, symbol, order
from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters
from trading_calendars import get_calendar
import FinanceDataReader as fdr

start = datetime(2018,1,1)
end = datetime(2018,12,31)
df=fdr.DataReader('000150',start,end)

# Backtesting
def initialize(context):
    context.i = 0
    context.symbol = symbol('DOOSAN')
    context.hold = False

def handle_data(context, data):
    context.i += 1
    if context.i < 20:
        return
    
    buy = False
    sell = False
    ma5 = data.history(context.symbol, 'price', 5, '1d').mean()
    ma20 = data.history(context.symbol, 'price', 20, '1d').mean()
    
    if ma5 > ma20 and context.hold == False:
        order(context.symbol, 100)
        context.hold = True
        buy = True
    elif ma5 < ma20 and context.hold == True:
        order(context.symbol, -100)
        context.hold = False
        sell = True
    
    record(Price=data.current(context.symbol,'price'),ma5=ma5,ma20=ma20,buy=buy,sell=sell)

data = df[['Close']]
data.columns = ['DOOSAN']
xkrx_calendar=get_calendar('XKRX')

algo = TradingAlgorithm(sim_params=create_simulation_parameters(capital_base=50000000,trading_calendar=xkrx_calendar),\
        initialize=initialize,handle_data=handle_data,trading_calendar=xkrx_calendar)
result = algo.run(data) 

# Plot
print(result.transactions.values) 

plt.plot(result.index, result.Price)
plt.plot(result.index, result.ma5)
plt.plot(result.index, result.ma20)
plt.legend(loc='best')
plt.plot(result.loc[result.buy == True].index, result.ma5[result.buy == True], '^')
plt.plot(result.loc[result.sell == True].index, result.ma5[result.sell == True], 'v')
plt.show()

plt.plot(result.index, result.portfolio_value)
plt.show()
