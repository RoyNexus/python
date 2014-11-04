import numpy as np
import copy
import datetime as dt
import csv as csv

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

from datetime import date
from bollinger import Bollinger

'''At every event Buy 100 shares of the equity, and Sell them 5 trading days later. In case not enough days are available Sell them on the last trading day. (Similar to what the homework 4 description wanted). '''

AMOUNT = 100
DELIMITER = ','

def get_current_date(index, timestamps_array):
    try:
        date_obj = timestamps_array[index].to_pydatetime()
    except Exception:
        date_obj = timestamps_array[len(timestamps_array)-1].to_pydatetime()
    
    return date_obj.year, date_obj.month, date_obj.day
    
def write_order(index_buy_date, timestamps_array, symbol, writer):
    year, month, day = get_current_date(index_buy_date, timestamps_array)    
    buy_row = [str(year), str(month), str(day), symbol, 'Buy', str(AMOUNT)]
    year, month, day = get_current_date(index_buy_date + 5, timestamps_array)
    sell_row = [str(year), str(month), str(day), symbol, 'Sell', str(AMOUNT)]
    writer.writerow(buy_row)
    writer.writerow(sell_row)

def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['close']    
    print "Finding Events"
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    print "Creating orders.csv"
    writer = csv.writer(open('orders.csv', 'wb'), delimiter=DELIMITER)
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            #f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            #f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            #f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            #f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            #if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
            #    df_events[s_sym].ix[ldt_timestamps[i]] = 1
            bollinger_obj = Bollinger(df_close)
            equity_today = bollinger_obj.get_value(ldt_timestamps[i], s_sym)
            equity_yesterday = bollinger_obj.get_value(ldt_timestamps[i - 1], s_sym)
            mkt_today = bollinger_obj.get_value(ldt_timestamps[i], 'SPY')
            
            if equity_today < -2.0 and equity_yesterday >= -2.0 and mkt_today >= 1.4:
                write_order(i, ldt_timestamps, s_sym, writer)

    return df_events


if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    ls_keys = ['close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    df_events = find_events(ls_symbols, d_data)
    print 'Finished'

