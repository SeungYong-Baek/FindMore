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
df = fdr.DataReader('000150',start,end)
quantity = 10
period = 20
d_period = 60
dividend = 1300

# Backtesting
def initialize(context):
    context.i = 0
    context.symbol = symbol('DOOSAN')

def handle_data(context, data):
    context.i += 1
    dividend_sum = 0

    if context.i == 1 or context.i%period == 0:
        order(context.symbol, quantity) 
    
    if context.i%d_period == 0:
        dividend_sum = ((context.i/d_period)*quantity*(d_period/period))*dividend
        print(dividend_sum)

    record(Price=data.current(context.symbol,'price'),dividend_sum=dividend_sum)

data = df[['Close']]
data.columns = ['DOOSAN']
xkrx_calendar=get_calendar('XKRX')

algo = TradingAlgorithm(sim_params=create_simulation_parameters(capital_base=30000000,trading_calendar=xkrx_calendar),\
        initialize=initialize,handle_data=handle_data,trading_calendar=xkrx_calendar)
result = algo.run(data) 

# Plot
plt.plot(result.index, result.Price)
buy_trans = result.loc[[t != [] for t in result.transactions]]
buy = buy_trans.loc[[t[0]['amount'] > 0 for t in buy_trans.transactions]]
plt.plot(buy.index, result.Price.loc[buy.index],'^',markersize=5,color='r')
plt.legend(loc='best')
plt.show()

plt.plot(result.index, result.portfolio_value)
plt.show()
