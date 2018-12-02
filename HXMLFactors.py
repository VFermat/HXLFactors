# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 19:11:36 2018

@author: Vitor Eller
"""

import numpy as np
import pandas as pd

class HXLFactors(object):
    
    def investment_factor(self, high_returns, low_returns):
        """
        Calculates the one factor based on the returns of specific portfolios.
        
        :param high_returns: List, Array, or Series with the returns of each of the 6 High portfolios
        :param low_returns: List, Array, or Series with the returns of each of the 6 Low portfolios
        :return: Float. The Investmen Factor for that month.
        """
        average_high = np.mean(high_returns)
        average_low = np.mean(low_returns)
        factor = average_high - average_low
        return factor
    
    def get_portfolios(self, stocks):
        """
        Gets which stocks are in each portfolio based on its classification (i.e. SHIALR)
        
        :param sotkcs: A pandas DataFrame containing stock`s information.
        :return: A Dict where keys are the classification, and values are the stocks on that classification`s portfolio.
        """
        
        portfolios = {}
        
        for stockcls in stocks['stockcls'].unique():
            portfolios[stockcls] = stocks[stocks['stockcls'] == stockcls].index.values
        
        return portfolios
    
    @staticmethod
    def _classify_stocks(stocks, month):
        """
        Sort all stocks based on Size, I/A and ROE.
        
        :param stocks: A pandas DataFrame containing stock`s information.
        :param month: Str. Checks if it`s June. Used to re-classify Size and I/A.
        :return: A pandas DataFrame with stock`s information and classification.
        """
        
        classified_stocks = stocks.copy()
        
        if month == "June":
            classified_stocks['sizemdn'] = np.median(classified_stocks['marketcap'])
            classified_stocks['clssize'] = classified_stocks.apply(_size_class, axis=1)
            classified_stocks['I/A30%'] = np.percentile(classified_stocks['I/A'], 30)
            classified_stocks['I/A70%'] = np.percentile(classified_stocks['I/A'], 70)
            classified_stocks['clsI/A'] = classified_stocks.apply(_IA_class, axis=1)
        
        
        classified_stocks['ROE30%'] = np.percentile(classified_stocks['ROE'], 30)
        classified_stocks['ROE70%'] = np.percentile(classified_stocks['ROE'], 70)
        classified_stocks['clsROE'] = classified_stocks.apply(_ROE_class, axis=1)
        classified_stocks['stockcls'] = classified_stocks['clssize'] + classified_stocks['clsI/A'] + classified_stocks['clsROE']
    
        return classified_stocks
    
    @staticmethod
    def _size_class(row):
        """ Classifies a Stock based on its Size and its rank among all other stocks """
        if row['marketcap'] <= row['sizemdn']:
            value = 'S'
        elif row['marketcap'] > row['sizemdn']:
            value = 'B'
        elif row['marketcap'] == np.nan:
            value = np.nan
        return value
    
    @staticmethod
    def _IA_class(row):
        """ Classifies a Stock based on its I/A Ratio and its rank among all other stocks """
        if row['I/A'] == np.nan:
            value = np.nan
        elif row['I/A'] <= row['I/A30%']:
            value = 'LIA'
        elif row['I/A'] <= row['I/A70%']:
            value = 'MIA'
        else:
            value = 'HIA'
        return value
    
    @staticmethod
    def _ROE_class(row):
        """ Classifies a Stock based on its ROE and its rank among all other stocks """
        if row['ROE'] == np.nan:
            value = np.nan
        elif row['ROE'] <= row['ROE30%']:
            value = 'LR'
        elif row['ROE'] <= row['ROE70%']:
            value = 'MR'
        else:
            value = 'HR'
        return value
    
"""
Algorithm:
    Receive Stocks Data;
    Compute I/A for all stocks at the end of every June.
    Compute monthly ROE for all stocks.
    Do every month:
        Start Sorting:
            Create 3 specific DataFrames:
                Size; I/A, ROE
            If Is June:
                For size:
                    Grab the Median Market Cap for the stocks
                    Top will be B
                    Bottom will be S
                For I/A:
                    Rank stocks based on I/A.
                    Top 30% Will be HIA
                    Middle 40% Will be MIA
                    Bottom 30% will be LIA
            For ROE:
                Rank stocks based on ROE.
                Top 30% will be HR
                Middle 40% will be MR
                Bottom 30% will be LR
        Create Portfolio:
            Take the intersection of the sorted DataFrames and classify the stocks. (example: BHIALR - Big, High I/A, Low ROE)
            Calculate each stock`s return for the month.
            Get 6 HIA portfolios (BHIAHR, BHIAMR, BHIALR, SHIAHR, SHIAMR, SHIALR)
            Get 6 LIA portfolios (BLIAHR, BLIAMR, BLIALR, SLIAHR, SLIAMR, SLIALR)
            Get 6 HR portfolios
            Get 6 LR portfolios
        Get returns:
            Get value-weighted return for each portfolio.
            Get simple average return for each group (HIA, LIA, HR, LR)
        Calculate Factors:
            Ria = Average(HIA) - Average(LIA)
            Rroe = Average(HR) - Average(LR)
"""