# Bollinger bands simulator

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import numpy as np
import math as math

from bollinger import Bollinger

def get_close_prices (start_date, end_date, symbols):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)    
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)    
    ls_keys = ['close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))        
    return d_data['close']    
    

if __name__ == '__main__':
    # Inputs
    start_date = dt.datetime(2009, 1, 1)
    end_date = dt.datetime(2011, 12, 31)
    symbols = ['AAPL', 'MSFT', 'IBM']
    
    current_date = dt.datetime(2010, 5, 12, 16, 00, 00)
    current_symbol = 'MSFT'
    
    prices_serie = get_close_prices(start_date, end_date, symbols)

    bollinger_obj = Bollinger(prices_serie)
    
                                                
    print 'Bollinger value: ' + str(bollinger_obj.get_value(current_date, current_symbol))
    

