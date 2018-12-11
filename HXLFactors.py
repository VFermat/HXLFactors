# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 15:45:02 2018

@author: Vitor Eller
"""

import pandas as pd
from pandas.tseries.offsets import *

class HXLFactors(object):
    
    def calculate_factors(self, prices, dividends, assets, ROE, marketcap):
        
        # Creating Base Panel
        self.securities = self._create_base_panel(prices, dividends, assets, ROE, marketcap)
        self.securities = self._get_IA_info(self.securities)
        self.securites = self._get_return(self.securities)
        self.securities = self._get_benchmarks(self.securities)
        
    @staticmethod        
    def _get_benchmarks(securities):
        pass
    
    @staticmethod
    def _get_return(securities):
        """
        Calculates the return for each security over time and related information.
    
        Parameters
        ----------
        securities : Panel like
            A panel containing the information on stocks. 
            
        Return
        ----------
        n_securities : Panel
            Updated panel containing the return for each security over time.
        """
        
        n_securities = securities.copy()
        
        n_securities['lprice'] = n_securities['price'].shift(1, axis=1)
        n_securities['pdifference'] = n_securities['price'] - n_securities['lprice']
        n_securities['gain'] = n_securities['dividends'] + n_securities['pdifference']
        n_securities['return'] = n_securities['gain']/n_securities['lprice']
        
        # Creates a return field which is shifted one month back. Will be used 
        # when calculating the factors
        n_securities['lreturn'] = n_securities['return'].shift(-1, axis=1)
        
        return n_securities
        
        
    @staticmethod
    def _get_IA_info(securities):
        """
        Calculates the Investment over Assets ratio and related information
    
        Parameters
        ----------
        securities : Panel like
            A panel containing the information on stocks. 
            
        Return
        ----------
        n_securities : Panel
            Updated panel containing Investment over Assets ratio and related information.
        """
        
        n_securities = securities.copy()
        # Calculates 1-year-lagged-assets
        n_securities['lassets'] = n_securities['assets'].shift(12, axis=1)
        # Calculates Investment
        n_securities['investment'] = n_securities['assets'] - n_securities['lassets']
        # Calculates Investment over Assets ratio
        n_securities['I/A'] = n_securities['investment']/n_securities['lassets']
        
        return n_securities
        
    @staticmethod
    def _create_base_panel(prices, dividends, assets, ROE, marketcap):
        """
        Method which creates the Base Panel for the class. We will calculate 
        the factors based on calculations made upon this panel
        
        Parameters
        ----------
        prices : DataFrame like
            DataFrame with securities prices along time
        dividends : DataFrame like
            DataFrame with securities given dividends per stock along time
        assets : DataFrame like
            DataFrame with securities assets along time
        ROE : DataFrame like
            DataFrame with securities ROE along time
        prices : DataFrame like
            DataFrame with securities marketcap along time
        
        Returns
        ----------
        securities : Panel
            A Panel containing consolidated information about the securities
        
        """
        
        dic = {
               'assets': assets,
               'ROE': ROE,
               'price': prices,
               'marketcap': marketcap,
               'dividends': dividends
                }
        
        securities = pd.Panel(data=dic)
        return securities
    
    
"""
TO DO:
    Maneira para que todos os index sejam o ultimo dia do mes.
    Arrumar um jeito de fazer groupby com panels.
"""