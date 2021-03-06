# -*- coding: utf-8 -*-
"""
Created on Wed May 17 13:42:21 2017

@author: kanghua
"""
import numpy as np
import pandas as pd

from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import CustomFactor

class HurstExp(CustomFactor):  
    inputs = [USEquityPricing.close]  
    window_length = int(252*0.5)  
    def Hurst(self, ts):  
        lags=np.arange(2,20)  
        tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
        n = len(lags)  
        x = np.log(lags)  
        y = np.log(tau)  
        poly = (n*(x*y).sum() - x.sum()*y.sum()) / (n*(x*x).sum() - x.sum()*x.sum())
        return poly*2.0  

    def compute(self, today, assets, out, close):  
        SERIES = np.nan_to_num(close)  
        hurst_exp_per_asset = list(map(self.Hurst, [SERIES[:,col_id].flatten() for col_id in np.arange(SERIES.shape[1])]))   
        out[:] = hurst_exp_per_asset
           

class Beta(CustomFactor):
    inputs = [USEquityPricing.close,USEquityPricing.volume]
    outputs = ['pbeta', 'vbeta','dbeta']

    window_length = 5 #TODO FIX IT
    def _beta(self,ts):
        ts[np.isnan(ts)] = 0 #TODO FIX it ?
        reg = np.polyfit(np.arange(len(ts)),ts,1)
        return reg[0]

    def compute(self, today, assets, out, close, volume):
        price_pct = pd.DataFrame(close, columns=assets).pct_change()[1:]
        volume_pct = pd.DataFrame(volume, columns=assets).pct_change()[1:]
        out[:].pbeta = price_pct.apply(self._beta)
        out[:].vbeta = volume_pct.apply(self._beta)
        out[:].dbeta = np.abs(out[:].vbeta - out[:].pbeta)