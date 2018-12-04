# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 22:04:57 2018

@author: Vitor Eller
"""

from HXMLFactors import HXLFactors
import pandas as pd

months = {
        '01': 'january',
        '02': 'february',
        '03': 'march',
        '04': 'april',
        '05': 'may',
        '06': 'june',
        '07': 'july',
        '08': 'august',
        '09': 'september',
        '10': 'october',
        '11': 'november',
        '12': 'december'
        }

prices = pd.read_excel('DataSet.xlsx', sheet_name=0, index_col=0)
prices = prices.drop(labels=prices.columns[0], axis=1)

ROE = pd.read_excel('DataSet.xlsx', sheet_name=1, index_col=0)
ROE = ROE.drop(labels=ROE.columns[0], axis=1)

marketcap = pd.read_excel('DataSet.xlsx', sheet_name=2, index_col=0)
marketcap = marketcap.drop(labels=marketcap.columns[0], axis=1)

assets = pd.read_excel('DataSet.xlsx', sheet_name=3, index_col=0)
assets = assets.drop(labels=assets.columns[0], axis=1)

def change_columns(column):
    date = str(column).split()
    date = date[0].split('-')
    date = date[:2]
    date[1] = months[date[1]]
    date = "".join(date)
    return date
    
prices.columns = prices.columns.to_series().apply(change_columns)
ROE.columns = ROE.columns.to_series().apply(change_columns)
marketcap.columns = marketcap.columns.to_series().apply(change_columns)
assets.columns = assets.columns.to_series().apply(change_columns)


factor = HXLFactors(prices, assets, ROE, marketcap)


factor.calculate_factor()

factorr = factor.factors

factorr = factorr.iloc[:, 21:]

factorr = factorr.transpose()
means = factorr.mean()