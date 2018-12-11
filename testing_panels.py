# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 15:51:58 2018

@author: Vitor Eller
"""

import pandas as pd
from pandas.tseries.offsets import *
import numpy as np

prices = pd.read_excel('DataSet.xlsx', sheet_name=0, index_col=0)
prices = prices.drop(labels=prices.columns[0], axis=1)

ROE = pd.read_excel('DataSet.xlsx', sheet_name=1, index_col=0)
ROE = ROE.drop(labels=ROE.columns[0], axis=1)

marketcap = pd.read_excel('DataSet.xlsx', sheet_name=2, index_col=0)
marketcap = marketcap.drop(labels=marketcap.columns[0], axis=1)

assets = pd.read_excel('DataSet.xlsx', sheet_name=3, index_col=0)
assets = assets.drop(labels=assets.columns[0], axis=1)

dic = {
       'assets': assets,
       'ROE': ROE,
       'prices': prices,
       'marketcap': marketcap
       }

securities = pd.Panel(data=dic)

securities

securities['lassets'] = securities['assets'].shift(12, axis=1)

securities['I/A'] = (securities['assets'] - securities['lassets'])/securities['lassets']

securities['30IA'] = np.nanpercentile(securities['I/A'], 30)

fsecurities = securities.to_frame(filter_observations=False)

abev = fsecurities.loc['ABEV3 BS Equity']

ia = fsecurities['I/A'].describe(percentiles=[0.3, 0.7]).reset_index()