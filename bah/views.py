from django.shortcuts import render

# Create your views here.

from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from bah.models import BAH_List

# for buy and hold backtesting
import os
import numpy as np
import pandas as pd
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
from zipline.api import order, record, symbol
from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters
from trading_calendars import get_calendar


class BAHIndexView(TemplateView):
    template_name = 'bah/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_list'] = ['BAH_List']
        return context

class BAHListView(ListView):
    model = BAH_List
    template_name_suffix=''

class BAHDetailView(DetailView):
    model = BAH_List

class BAHDeleteView(DeleteView):
    model = BAH_List
    success_url = reverse_lazy('bah:bah_list')

class BAHCreateView(CreateView):
    model = BAH_List
    fields = ['name','code','market','buy_quantity','buy_period', \
            'capital_base','start_date','end_date','div_period','expected_dividend']
    template_name_suffix='_create'

    def form_valid(self, form):
        # BAH data prepare
        bah = form.save(commit=False)

        name = form.cleaned_data['name']
        code = form.cleaned_data['code']
        market = form.cleaned_data['market']
        buy_quantity = form.cleaned_data['buy_quantity']
        buy_period = form.cleaned_data['buy_period']
        capital_base = form.cleaned_data['capital_base']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        div_period = form.cleaned_data['div_period']
        expected_dividend = form.cleaned_data['expected_dividend']

        # Backtesting
        def initialize(context):
            context.i = 0
            context.symbol = symbol(name)

        def handle_data(context, data):
            context.i += 1
            dividend_sum = 0

            if context.i == 1 or (context.i%buy_period) == 0:
                order(context.symbol, buy_quantity)
                
            if context.i%div_period == 0:
                dividend_sum = ((context.i/div_period) * buy_quantity * \
                        (div_period/buy_period)) * expected_dividend
            
            record(Price=data.current(context.symbol,'price'),dividend_sum=dividend_sum)
          
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
        bt_file_name = name+'_'+str(now)+'_BAH-BT.png'
        bt_file_path = file_home+bt_file_name
        bt_static_path = '/static/'+bt_file_name
           
        pv_file_name = name+'_'+str(now)+'_BAH-PV.png'
        pv_file_path = file_home+pv_file_name
        pv_static_path = '/static/'+pv_file_name

        plt.plot(result.index, result.Price)
        buy_trans = result.loc[[t != [] for t in result.transactions]]
        buy = buy_trans.loc[[t[0]['amount'] > 0 for t in buy_trans.transactions]]
        plt.plot(buy.index, result.Price.loc[buy.index],'^',markersize=5,color='r')
        plt.legend(loc='best')
        plt.savefig(bt_file_path,dpi=150)
        plt.clf()
        
        plt.plot(result.index, result.portfolio_value)
        plt.savefig(pv_file_path,dpi=150)
        plt.clf()

        # BAH result insert
        bah.name = name
        bah.code = code
        bah.market = market
        bah.start_date = start_date
        bah.end_date = end_date
        bah.buy_quantity = buy_quantity
        bah.buy_period = buy_period
        bah.capital_base = capital_base
        bah.div_period = div_period
        bah.expected_dividend = expected_dividend
        bah.dividend_sum = sum(result.dividend_sum)
        bah.expected_dividend_return = \
                sum(result.dividend_sum)/abs(sum(result.capital_used))*100
        bah.last_pv = result.portfolio_value[-1]
        bah.last_value = result.ending_value[-1]
        bah.last_cash = result.ending_cash[-1]
        bah.capital_used = sum(result.capital_used)
        if result.positions.values[-1] == []:
            bah.shares = 0
            bah.expected_return = ((result.ending_cash[-1]/sum(result.capital_used))-1)*100
        elif result.positions.values[-1] != []:
            bah.shares = result.positions.values[-1][0]['amount']
            bah.expected_return = ((result.portfolio_value[-1]/sum(result.capital_used))-1)*100

        bah.bt_path = bt_static_path
        bah.pv_path = pv_static_path

        form.save() 
        
        return super(BAHCreateView, self).form_valid(form)
