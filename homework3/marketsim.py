# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
#import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys as sys
import csv as csv

from order import Order
from metrics import Metrics

DATETIME = 0
VALUE = 1

def read_arguments(arguments):
    if len(arguments) == 3:
        return arguments[0], arguments[1], arguments[2]
    else:
        print 'Incorrect number of arguments, assume default arguments'
        # raise Exception
        return 1000000, "orders.csv", "values.csv"

def read_orders(file):
    reader = csv.reader(open(file, 'rU'), delimiter=',')
    orders_array = ['YEAR', 'MONTH', 'DAY', 'SYMBOL', 'ORDER', 'SHARES']
    for row in reader:
        orders_array = np.vstack([orders_array, np.delete(row, [6], axis=0)])
    orders_array = np.delete(orders_array, [0], axis=0)
    return orders_array

def get_orders_object(orders):
    result = []
    for order in orders:
        orderClass = Order(order)
        result.append(orderClass)
    return result

def get_symbols_and_dates(orders):
    symbols = []
    dates = []
    for order in orders:
        orderClass = Order(order)
        symbols.append(orderClass.get_symbol())
        dates.append(orderClass.get_date())
    return list(set(symbols)), dates
        
def get_close_prices(start_date, end_date, symbols):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)    
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)    
    ls_keys = ['close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    return d_data['close']

def checkForOrders(orderObjects, currentDate):
    result = []
    for order in orderObjects:
        if (order.get_date_16_00() == currentDate):
            result.append(order)
    return result

def get_current_price(prices, symbol, current_date):
    pricesSymbol = prices[symbol]
    return pricesSymbol[current_date]

def get_sym_pos(symbols, symbol):
    result = 0
    for x in xrange(0, len(symbols)):
        if (symbols[x]) == symbol:
            result = x
    return result

def calc_cash(order, currentCash, prices):
    result = 0
    if (order.get_type() == 'Buy'):
        result = currentCash - (int(order.get_shares()) * float(get_current_price(prices, order.get_symbol(), order.get_date_16_00())))
    else:
        result = currentCash + (int(order.get_shares()) * float(get_current_price(prices, order.get_symbol(), order.get_date_16_00())))
    return result

def calc_portfolio(order, currentPortfolio):
    result = 0
    if (order.get_type() == 'Buy'):
        result = currentPortfolio + int(order.get_shares())
    else:
        result = currentPortfolio - int(order.get_shares())
    return result

def update_cash_forward(resultMatrix, index, lenCashMatrix):
    updatedValue = resultMatrix[VALUE, index]
    for x in xrange(index, lenCashMatrix):
        resultMatrix[VALUE, x] = updatedValue
    return resultMatrix

def update_portfolio_forward(resultMatrix, index, lenPortfolioMatrix):
    for idxSym in xrange(0, len(resultMatrix[VALUE, index])):
        updatedValue = resultMatrix[VALUE, index][idxSym]
        for x in xrange(index, lenPortfolioMatrix):
            resultMatrix[VALUE, x][idxSym] = updatedValue
    return resultMatrix

def applyPricesToSymbols(currentValues, prices, symbols, currentDate):
    for x in xrange(0, len(symbols)):
        currentValues[x] = currentValues[x] * get_current_price(prices, symbols[x], currentDate)
    return currentValues

def applyCurrentDatePrices(resultMatrix, prices, symbols):
    lenPortfolioMatrix = len(prices.values)
    for x in xrange(0, lenPortfolioMatrix):
        resultMatrix[VALUE, x] = applyPricesToSymbols(resultMatrix[VALUE, x], prices, symbols, resultMatrix[DATETIME, x])
    return resultMatrix

def calculate_portfolio(symbols, prices, orders):
    lenPortfolioMatrix = len(prices.values)
    portfolio_matrix = np.zeros((lenPortfolioMatrix, len(symbols)))
    datetimesIndex = np.array(prices.index.to_pydatetime())
    resultMatrix = np.array([datetimesIndex, portfolio_matrix])
    orderObjects = get_orders_object(orders)    
    for x in xrange(0, lenPortfolioMatrix):
        dayOrders = checkForOrders(orderObjects, resultMatrix[DATETIME, x])
        for dayOrder in dayOrders:
            resultMatrix[VALUE, x][get_sym_pos(symbols, dayOrder.get_symbol())] = calc_portfolio(dayOrder, resultMatrix[VALUE, x][get_sym_pos(symbols, dayOrder.get_symbol())])
            resultMatrix = update_portfolio_forward(resultMatrix, x, lenPortfolioMatrix)
    
    #print '\n\nPortfolio shares: ' + str(resultMatrix[VALUE])
    resultMatrix = applyCurrentDatePrices(resultMatrix, prices, symbols)
    #print '\n\nPortfolio value: ' + str(resultMatrix[VALUE])
    return resultMatrix    

def calculate_cash(initial_cash, prices, orders):
    lenCashMatrix = len(prices.values)
    cash_matrix = np.zeros(lenCashMatrix)
    cash_matrix.fill(initial_cash)
    datetimesIndex = np.array(prices.index.to_pydatetime())
    resultMatrix = np.array([datetimesIndex, cash_matrix])
    orderObjects = get_orders_object(orders)
    for x in xrange(0, lenCashMatrix):
        dayOrders = checkForOrders(orderObjects, resultMatrix[DATETIME, x])
        for dayOrder in dayOrders:
            resultMatrix[VALUE, x] = calc_cash(dayOrder, resultMatrix[VALUE, x], prices)
            resultMatrix = update_cash_forward(resultMatrix, x, lenCashMatrix)
        
    #print resultMatrix[VALUE]
    return resultMatrix

def sum_portfolio_values(valueInCurrentDate):
    result = 0
    for value in valueInCurrentDate:
        result = result + value
    return result

def sum_cash_and_portfolio(cash, portfolio, size):
    for x in xrange(0, size):
        cash[VALUE, x] = cash[VALUE, x] + sum_portfolio_values(portfolio[VALUE, x])
    return cash

def write_output_file(filename, values, size):
    writer = csv.writer(open(filename, 'wb'), delimiter=',')
    for x in xrange(0, size):
        row_to_enter = [str(values[DATETIME, x]), str(values[VALUE, x])]
        writer.writerow(row_to_enter)

def main(arguments):
    try:
        initial_cash, orders_file, values_file = read_arguments(arguments)
    except Exception:
        print 'Call example: marketsim.py 1000000 orders.csv values.csv'
    print "Initial amount of cash: " + str(initial_cash) + "$"
    print "Reading from input file: " + str(orders_file)
    orders_array = read_orders(orders_file)
    symbols_list, dates_list = get_symbols_and_dates(orders_array)
    prices = get_close_prices(dates_list[0], dates_list[len(dates_list)-1] + dt.timedelta(days=1), symbols_list)
    cash = calculate_cash(initial_cash, prices, orders_array)
    portfolio = calculate_portfolio(symbols_list, prices, orders_array)
    total_values_by_date = sum_cash_and_portfolio(cash, portfolio, len(prices.values))
    print "Writing into output file: " + str(values_file)
    write_output_file(values_file, total_values_by_date, len(prices.values))
    print "Details of portfolio\n"
    metrics = Metrics(total_values_by_date[VALUE])
    print "Sharpe Ratio of Fund: " + str(metrics.get_sharpe_ratio())
    print "Total Return of Fund: " + str(metrics.get_cumulative_return())
    print "Standard Deviation of Fund: " + str(metrics.get_daily_std())
    print "Average Daily Return of Fund: " + str(metrics.get_daily_return())
    

if __name__ == '__main__':
    main(sys.argv)