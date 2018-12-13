# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 11:57:02 2018

@author: Vitor Eller
"""

from HXLFactors import HXLFactors
import pandas as pd

prices = pd.read_excel('DataSetSPX.xlsx', sheet_name=5, index_col=0)
marketcap = pd.read_excel('DataSetSPX.xlsx', sheet_name=4, index_col=0)
assets = pd.read_excel('DataSetSPX.xlsx', sheet_name=3, index_col=0)
ROE = pd.read_excel('DataSetSPX.xlsx', sheet_name=2, index_col=0)
dividends = pd.read_excel('DataSetSPX.xlsx', sheet_name=1, index_col=0)

hxl = HXLFactors()

hxl.calculate_factors(prices, dividends, assets, ROE, marketcap)

securities = hxl.securities

HXLInvestment = hxl.HXLInvestment
