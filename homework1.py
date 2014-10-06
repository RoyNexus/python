# Simulation function, four symbols

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import numpy as np
import math as math

def get_average(naRets):
    naMean = np.mean(naRets, axis=0)
    return naMean[0]

def get_sharpe_ratio(naRets): 
    """ 
    @summary Returns the daily Sharpe ratio of the returns. 
    @param naRets: 1d numpy array or list of daily returns 
    @return Annualized rate of return, not converted to percent 
    """ 
    fDev = np.std( naRets - 1, axis=0 ) 
    fMean = get_average(naRets)
    # fMean = np.mean( naRets - 1, axis=0 ) 
    ''' Convert to yearly standard deviation ''' 
    fSharpe = ((fMean * math.sqrt(252)) / fDev)
    return fSharpe[0]

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
    # Normalize
    normalized_prices = prices/ prices[0, :]
    # Weighted portfolio with allocations
    allocated_prices = normalized_prices * allocations
    # Sum each row of the portfolio
    portfolio_values =  allocated_prices.sum(axis=1)    
    # Last element is the cumulative return
    _cumulative_ret = portfolio_values[-1]
    # Compute daily returns
    daily_rets = tsu.returnize0(portfolio_values)
    # Get Sharpe Ratio
    _sharpe = get_sharpe_ratio(daily_rets)
    # Get stdev of daily returns
    stdev_daily = np.std(daily_rets - 1, axis=0)
    _vol = stdev_daily[0];
    _daily_ret = get_average(daily_rets)
    
    return _vol, _daily_ret, _sharpe, _cumulative_ret

def is_valid_allocations(allocation):    
    total = 0.0
    for value in allocation:
        total += value
    return total == 1.0

# Inputs
start_date = dt.datetime(2010, 1, 1)
end_date = dt.datetime(2010, 12, 31)
symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']

# allocations = [0.3, 0.2, 0.3, 0.2]

def legal_allocation(start, end, step):
    while start <= end:
        yield start
        start += step

max_sharpe_ratio = -1.0
optimal_allocations = [0.0, 0.0, 0.0, 0.0]

for A1 in legal_allocation(0.0, 1.0, 0.1):
    for A2 in legal_allocation(0.0, 1.0, 0.1):
        for A3 in legal_allocation(0.0, 1.0, 0.1):
            for A4 in legal_allocation(0.0, 1.0, 0.1):
                allocations = [A1, A2, A3, A4]
                print 'Trying allocations: ' + str(allocations)
                if is_valid_allocations(allocations):                
                    # Call simulate() function
                    print 'Legal allocations: ' + str(allocations)
                    volatility, daily_return, sharpe_ratio, cumulative_return = simulate_portfolio(start_date, end_date, symbols, allocations)
                    if (sharpe_ratio >= max_sharpe_ratio):
                        max_sharpe_ratio = sharpe_ratio   
                        optimal_allocations = allocations
                
                    
print 'Optimal allocations: ' + str(optimal_allocations)
print 'Sharpe Ratio: ' + str(max_sharpe_ratio)

#print 'Sharpe Ratio: ' + str(sharpe_ratio)
#print 'Volatility (stdev of daily returns): ' + str(volatility)
#print 'Average Daily Return: ' + str(daily_return)
#print 'Cumulative Return: ' + str(cumulative_return)
    
