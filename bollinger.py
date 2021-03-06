import numpy as np
import pandas as pd

class Bollinger:

    def __init__(self, prices):
        self.prices = prices
                                                  
    def get_average(self, naRets):
        naMean = np.mean(naRets, axis=0)
        return naMean   
    
    def get_stdev(self, naRets):
        stdev_daily = np.std(naRets, axis=0)
        return stdev_daily

    def get_value(self, date, symbol):
        result = 0
        symbol_values = self.prices[symbol]
        rolling_mid = pd.rolling_mean(symbol_values, 20);
        rolling_stdev = pd.rolling_std(symbol_values, 20)        
        bollinger_val = (symbol_values - rolling_mid) / (rolling_stdev)
        result = bollinger_val.ix[date]                
        return result                    