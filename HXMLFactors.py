# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 19:11:36 2018

@author: Vitor Eller
"""

import numpy as np
import pandas as pd

class HXLFactors(object):
    
    def __init__(self, prices, assets, ROE, marketcap):
        """
        Initializes the class creating the initial pandas DataFrame to be used on the 
        construction of the factors.
        
        :param prices: A pandas DataFrame with all securities prices throughout the time.
        :param assets: A pandas DataFrame with all securities assets throughout the time.
        :param ROE: A pandas DataFrame with all securities Return on Common Equity (ROE) throughout the time.
        :param marketcap: A pandas DataFrame with all securities MarketCap throughout the time.
        """        
        
        self.prices = prices
        self.assets = assets
        self.ROE = ROE
        self.marketcap = marketcap
        self.high_IA = ['BHIAHR', 'BHIAMR', 'BHIALR', 'SHIAHR', 'SHIAMR', 'SHIALR']
        self.low_IA = ['BLIAHR', 'BLIAMR', 'BLIALR', 'SLIAHR', 'SLIAMR', 'SLIALR']
        self.high_ROE = ['BHIAHR', 'BMIAHR', 'BLIAHR', 'SHIAHR', 'SMIAHR', 'SLIAHR']
        self.low_ROE = ['BHIALR', 'BMIALR', 'BLIALR', 'SHIALR', 'SMIALR', 'SLIALR']
        
        stocks = pd.DataFrame(index=self.prices.index)
        stocks["Prices"] = self.prices[self.prices.columns[0]]
        stocks["Assets"] = self.assets[self.assets.columns[0]]
        stocks["ROE"] = self.ROE[self.ROE.columns[0]]
        stocks["marketcap"] = self.marketcap[self.marketcap.columns[0]]
        stocks["I/A"] = 0
        self.stocks = stocks
        
    def calculate_factor(self):
        
        self.factors = pd.DataFrame(index=["HXLInvestment", "HXLProfitability"])
        
        for month in range(1, self.prices.shape[1]):
            new_stocks = pd.DataFrame(index=self.prices.index) 
            new_stocks["Prices"] = self.prices[self.prices.columns[month]]
            new_stocks["Assets"] = self.assets[self.assets.columns[month]]
            new_stocks["ROE"] = self.ROE[self.ROE.columns[month]]
            new_stocks["marketcap"] = self.marketcap[self.marketcap.columns[month]]
            
            if month != 1:
                new_stocks["clssize"] = self.stocks["clssize"]
                new_stocks["clsI/A"] = self.stocks["clsI/A"]
            
            if "june" in self.prices.columns[month]:
                new_stocks["I/A"] = self._get_IA(self.stocks, new_stocks)
            else:
                new_stocks["I/A"] = self.stocks["I/A"]
                
            new_stocks = self.classify_stocks(new_stocks, self.prices.columns[month])
            
            if month != 1:
                portfolios = [key for key in self._get_portfolios(new_stocks)]
                portfolios_return = pd.DataFrame(index=portfolios, columns=["prtflreturn"])
                portfolios_return["prtflreturn"] = [self._get_returns(self.stocks, new_stocks, prtfl) for prtfl in portfolios]
                try:
                    high_IA = portfolios_return.loc[self.high_IA].prtflreturn
                except:
                    continue
                low_IA = portfolios_return.loc[self.low_IA].prtflreturn
                high_ROE = portfolios_return.loc[self.high_ROE].prtflreturn
                low_ROE = portfolios_return.loc[self.low_ROE].prtflreturn
                HXLInvestment = self._factor(high_IA, low_IA)
                HXLProfitability = self._factor(high_ROE, low_ROE)
                self.factors[self.prices.columns[month]] = pd.Series([HXLInvestment, HXLProfitability])
                
            self.stocks = new_stocks
        
    def classify_stocks(self, stocks, month):
        """
        Sort all stocks based on Size, I/A and ROE.
        
        :param stocks: A pandas DataFrame containing stock`s information.
        :param month: Str. Checks if it`s June. Used to re-classify Size and I/A.
        :return: A pandas DataFrame with stock`s information and classification.
        """
        
        classified_stocks = stocks.copy()
        
        if "june" in month:
            classified_stocks['sizemdn'] = classified_stocks['marketcap'].median()
            classified_stocks['clssize'] = classified_stocks.apply(self._size_class, axis=1)
            classified_stocks['I/A30%'] = np.nanpercentile(classified_stocks['I/A'], 30)
            classified_stocks['I/A70%'] = np.nanpercentile(classified_stocks['I/A'], 70)
            classified_stocks['clsI/A'] = classified_stocks.apply(self._IA_class, axis=1)
        
        
        classified_stocks['ROE30%'] = np.nanpercentile(classified_stocks['ROE'], 30)
        classified_stocks['ROE70%'] = np.nanpercentile(classified_stocks['ROE'], 70)
        classified_stocks['clsROE'] = classified_stocks.apply(self._ROE_class, axis=1)
        classified_stocks['stockcls'] = classified_stocks['clssize'] + classified_stocks['clsI/A'] + classified_stocks['clsROE']
    
        return classified_stocks    
    
    @staticmethod
    def _factor(high_returns, low_returns):
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
    
    @staticmethod
    def _get_portfolios(stocks):
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
    def _get_returns(stocks, new_stocks, stockcls):
        stocks_used = stocks[stocks["stockcls"] == stockcls]
        new_stocks_used = new_stocks[new_stocks["stockcls"] == stockcls]
        new_stocks_used["price_difference"] = (new_stocks_used["Prices"] - stocks_used["Prices"])/stocks_used["Prices"]
        treturn = np.sum(new_stocks_used["price_difference"]*new_stocks_used["marketcap"])
        tweight = np.sum(new_stocks_used["marketcap"])
        portfolio_return = treturn/tweight
        return portfolio_return
    
    @staticmethod
    def _get_IA(stocks, new_stocks):
        investment = new_stocks['Assets'] - stocks['Assets']
        IA = investment/new_stocks['Assets']
        return IA
        
    
    @staticmethod
    def _size_class(row):
        """ Classifies a Stock based on its Size and its rank among all other stocks """
        if row['marketcap'] == np.nan:
            value = np.nan
        elif row['marketcap'] <= row['sizemdn']:
            value = 'S'
        else:
            value = 'B'
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