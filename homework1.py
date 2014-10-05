# Simulation function, four symbols

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import datetime as dt

def get_close_prices (start_date, end_date, symbols):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)    
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)    
    ls_keys = ['close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))        
    return d_data['close'].values    
    
def simulate_portfolio (start_date, end_date, symbols, allocations):
    _sharpe = 0.0
    _vol = 0.0
    _daily_ret = 0.0
    _cumulative_ret = 0.0
    
    prices = get_close_prices(start_date, end_date, symbols)
    normalized_prices = prices/ prices[0, :]
    allocated_prices = normalized_prices * allocations
    
    return _vol, _daily_ret, _sharpe, _cumulative_ret

# Inputs
start_date = dt.datetime(2011, 1, 1)
end_date = dt.datetime(2011, 12, 31)
symbols = ['GOOG', 'AAPL', 'GLD', 'XOM']
allocations = [0.2, 0.3, 0.4, 0.1]

volatility, daily_return, sharpe_ratio, cumulative_return = simulate_portfolio(start_date, end_date, symbols, allocations)

print 'Sharpe Ratio: ' + str(sharpe_ratio)
print 'Volatility (stdev of daily returns): ' + str(volatility)
print 'Average Daily Return: ' + str(daily_return)
print 'Cumulative Return: ' + str(cumulative_return)
    
