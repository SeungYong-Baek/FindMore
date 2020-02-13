from django.shortcuts import render

# Create your views here.

from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from sma.models import SMA_List

# for mean reversion analysis
import os
import numpy as np
import pandas as pd
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
from zipline.api import order_target, record, symbol, order
from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters
from trading_calendars import get_calendar


class SMAIndexView(TemplateView):
    template_name = 'sma/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_list'] = ['SMA_List']
        return context

class SMAListView(ListView):
    model = SMA_List
    template_name_suffix=''

class SMADetailView(DetailView):
    model = SMA_List

class SMADeleteView(DeleteView):
    model = SMA_List
    success_url = reverse_lazy('sma:sma_list')

class SMACreateView(CreateView):
    model = SMA_List
    fields = ['name','code','market','short_ma','long_ma','buy_quantity', \
            'sell_quantity','capital_base','start_date','end_date']
    template_name_suffix='_create'

    def form_valid(self, form):
        # SMA data prepare
        sma = form.save(commit=False)

        name = form.cleaned_data['name']
        code = form.cleaned_data['code']
        market = form.cleaned_data['market']
        short_ma = form.cleaned_data['short_ma']
        long_ma = form.cleaned_data['long_ma']
        buy_quantity = form.cleaned_data['buy_quantity']
        sell_quantity = form.cleaned_data['sell_quantity']
        capital_base = form.cleaned_data['capital_base']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        # Backtesting
        def initialize(context):
            context.i = 0
            context.symbol = symbol(name)
            context.hold = False

        def handle_data(context, data):
            context.i += 1
            if context.i < long_ma:
                return 
            
            buy = False
            sell = False 
            short_mavg = data.history(context.symbol,'price',short_ma,'1d').mean()
            long_mavg = data.history(context.symbol,'price',long_ma,'1d').mean() 
            
            if short_mavg > long_mavg and context.hold == False:
                order(context.symbol, buy_quantity)
                context.hold = True
                buy = True
            elif short_mavg < long_mavg and context.hold == True:
                order(context.symbol, -sell_quantity)
                context.hold = False
                sell = True 
                
            record(Price=data.current(context.symbol,'price'),short_mavg=short_mavg, \
                        long_mavg=long_mavg,buy=buy,sell=sell)
          
        # Data preparing
        df = fdr.DataReader(code, start_date, end_date)
        data = df[['Close']]
        data.columns = [name]
        xkrx = get_calendar('XKRX') 
           
        # Call backtesting
        if market == 'KOSPI' or market == 'KOSDAQ':
            algo = TradingAlgorithm(sim_params=create_simulation_parameters(capital_base=capital_base,\
                    trading_calendar=xkrx),initialize=initialize,handle_data=handle_data,trading_calendar=xkrx)
            result = algo.run(data) 
        elif market == 'NASDAQ': 
            algo = TradingAlgorithm(sim_params=create_simulation_parameters(capital_base=capital_base),\
                    initialize=initialize,handle_data=handle_data)
            result = algo.run(data) 

        # Quantile plot and save
        now=timezone.now()
        file_home = '/home/seungyong/FindMore/static/'
        bt_file_name = name+'_'+str(now)+'_SMA-BT.png'
        bt_file_path = file_home+bt_file_name
        bt_static_path = '/static/'+bt_file_name
           
        pv_file_name = name+'_'+str(now)+'_SMA-PV.png'
        pv_file_path = file_home+pv_file_name
        pv_static_path = '/static/'+pv_file_name

        plt.plot(result.index, result.Price)
        plt.plot(result.index, result.short_mavg)
        plt.plot(result.index, result.long_mavg)
        plt.legend(loc='best')
        if sell_quantity > 0:
            plt.plot(result.loc[result.buy == True].index,result.short_mavg[result.buy == True],'^',color='r',markersize=5)
            plt.plot(result.loc[result.sell == True].index,result.short_mavg[result.sell == True],'v',color='g',markersize=5)
        elif sell_quantity == 0:
            plt.plot(result.loc[result.buy == True].index,result.short_mavg[result.buy == True],'^',color='r',markersize=5)
        plt.savefig(bt_file_path,dpi=150)
        plt.clf()
        
        plt.plot(result.index, result.portfolio_value)
        plt.savefig(pv_file_path,dpi=150)
        plt.clf()

        # SMA result insert
        sma.name = name
        sma.code = code
        sma.market = market
        sma.start_date = start_date
        sma.end_date = end_date
        sma.short_ma = short_ma
        sma.long_ma = long_ma
        sma.buy_quantity = buy_quantity
        sma.sell_quantity = sell_quantity
        sma.capital_base = capital_base
        sma.last_pv = result.portfolio_value[-1]
        sma.last_value = result.ending_value[-1]
        sma.last_cash = result.ending_cash[-1]
        sma.capital_used = sum(result.capital_used)
        if result.positions.values[-1] == []: 
            sma.shares = 0
            sma.expected_return = ((result.ending_cash[-1]/capital_base)-1)*100
        elif result.positions.values[-1] != []:
            sma.shares = result.positions.values[-1][0]['amount']
            sma.expected_return = ((result.portfolio_value[-1]/capital_base)-1)*100
        sma.bt_path = bt_static_path
        sma.pv_path = pv_static_path

        form.save() 
        
        return super(SMACreateView, self).form_valid(form)
