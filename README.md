# FindMore - Web based Stock Analysis

## Packages
* Python - Python 3.6, Pandas, FinanceDataReader, matplotlib, statsmodels
* Django - Nginx, uWSGI, MySQL
* Backtesting - Zipline(Quantopian, v1.3.0)
* FindMore 구성 방법 - https://github.com/SeungYong-Baek/FindMore/wiki

## Supported Features

### 1. Mean Reversion Analysis - Augmented Dickey Fuller Test, Hurst exponent, Half Life, Quantile

![Mean Reversion Analysis](/mra/MRA.png)
------------------------------------------------

### 2. Mean Reversion Analysis with Google Data Studio

* Django의 MySQL 데이터베이스를 Google Data Studio의 데이터 소스로 등록 필요
* findmore 데이터베이스의 Mean Reversion Analysis 앱 테이블(mra_mra_list)의 데이터를 소스로 사용함
* 데이터 소스 등록 후에 보고서 생성 필요

![Analysis with Google Data Studio-1](/mra/MRA_GOOGLE_DS-1.png)
![Analysis with Google Data Studio-2](/mra/MRA_GOOGLE_DS-2.png)
------------------------------------------------

### 3. Buy(regularly) and Hold - Zipline Backtest

![Buy And Hold](/bah/BAH.png)
------------------------------------------------

### 4. Simple Moving Average - Zipline Backtest

![Simple Moving Average](/sma/SMA.png)
------------------------------------------------
