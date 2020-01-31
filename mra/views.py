from django.shortcuts import render

# Create your views here.

from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from mra.models import MRA_List

# for mean reversion analysis
import os
import numpy as np
import pandas as pd
import FinanceDataReader as fdr
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt


class MRAIndexView(TemplateView):
    template_name = 'mra/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_list'] = ['MRA_List']
        return context

class MRAListView(ListView):
    model = MRA_List
    template_name_suffix=''

class MRADetailView(DetailView):
    model = MRA_List

class MRADeleteView(DeleteView):
    model = MRA_List
    success_url = reverse_lazy('mra:mra_list')

class MRACreateView(CreateView):
    model = MRA_List
    fields = ['name','code','market','start_date','end_date']
    template_name_suffix='_create'

    def form_valid(self, form):
        # MRA data prepare
        mra = form.save(commit=False)

        name = form.cleaned_data['name']
        code = form.cleaned_data['code']
        market = form.cleaned_data['market']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        # Data download
        df=fdr.DataReader(code, start_date, end_date)

        # Hurst
        def get_hurst_exponent(df):
            lags=range(2,100)
            ts=np.log(df)
            tau=[np.sqrt(np.std(np.subtract(ts[lag:],ts[:-lag]))) for lag in lags]
            poly=np.polyfit(np.log(lags), np.log(tau),1)
            hurst=poly[0]*2.0
            return hurst

        # Half-Life
        def get_half_life(df):
            price=pd.Series(df)
            lagged_price=price.shift(1).fillna(method='bfill')
            delta=price-lagged_price
            beta=np.polyfit(lagged_price,delta,1)[0]
            half_life=(-1*np.log(2)/beta)
            return half_life

        # Do the all test
        adf=ts.adfuller(df['Close'])
        hurst=get_hurst_exponent(df['Close'])
        half_life=get_half_life(df['Close'])

        # Quantile plot and save
        now=timezone.now()
        file_home = '/home/seungyong/FindMore/static/'
        file_name = name+'_'+str(now)+'_MRA.png'
        file_path = file_home+file_name
        static_path = '/static/'+file_name
        plt.boxplot(df['Close'],showmeans=True)
        plt.grid()
        plt.savefig(file_path)
        plt.clf()
        
        # MRA result insert
        mra.name = name
        mra.code = code
        mra.market = market
        mra.start_date = start_date
        mra.end_date = end_date
        mra.adf = adf[0]
        mra.adf_pv = adf[1]
        mra.adf_one = adf[4]['1%']
        mra.adf_five = adf[4]['5%']
        mra.hurst = hurst
        mra.half_life = half_life
        mra.mean = df['Close'].mean()
        mra.sd = df['Close'].std()
        mra.volume = df['Volume'].mean()
        mra.quantile_q1 = df['Close'].quantile(.15)
        mra.quantile_q2 = df['Close'].quantile(.5)
        mra.quantile_q3 = df['Close'].quantile(.85)
        mra.quantile_path = static_path

        form.save() 
        
        return super(MRACreateView, self).form_valid(form)
