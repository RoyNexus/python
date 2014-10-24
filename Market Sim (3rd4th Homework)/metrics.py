# QSTK Imports
import QSTK.qstkutil.tsutil as tsu

# Third Party Imports
import numpy as np
import math as math

class Metrics:

    def __init__(self, grossValues):
        self.grossValues = grossValues
        
    def get_sharpe_ratio(self):
        grossValuesFloat = self.grossValues.astype('float') 
        normalized_prices = grossValuesFloat / grossValuesFloat[0]
        daily_rets = tsu.returnize0(normalized_prices)
        daily_rets = daily_rets.astype('float')        
        fDev = np.std(daily_rets - 1, axis=0) 
        fMean = self.get_average(daily_rets)
        # fMean = np.mean( naRets - 1, axis=0 ) 
        ''' Convert to yearly standard deviation ''' 
        fSharpe = ((fMean * math.sqrt(252)) / fDev)
        return fSharpe[0]
        
    def get_cumulative_return(self):
        grossValuesFloat = self.grossValues.astype('float') 
        normalized_prices = grossValuesFloat / grossValuesFloat[0]
        cumulative_ret = normalized_prices[-1]
        return cumulative_ret
        
    def get_daily_std(self):
        grossValuesFloat = self.grossValues.astype('float') 
        normalized_prices = grossValuesFloat / grossValuesFloat[0]
        daily_rets = tsu.returnize0(normalized_prices)
        daily_rets = daily_rets.astype('float')
        stdev_daily = np.std(daily_rets - 1, axis=0)
        volatility = stdev_daily[0];
        return volatility
        
    def get_daily_return(self):
        grossValuesFloat = self.grossValues.astype('float') 
        normalized_prices = grossValuesFloat / grossValuesFloat[0]
        daily_rets = tsu.returnize0(normalized_prices)
        daily_return = self.get_average(daily_rets)
        return daily_return
        
    def get_average(self, naRets):
        naMean = np.mean(naRets, axis=0)
        return naMean[0]                 
                    
    def __str__(self):
        return str(self.grossValues)