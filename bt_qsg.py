""""""
# from __future__ import (
#     absolute_import, division, print_function, unicode_literals
# )
# import datetime
import logging, logging.config

import backtrader as bt

import pandas
from pandas import Timestamp


DEBUG = True
DB = "/home/la/dev/data/tiingo_sm.db"

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

ctx = {}


import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])


# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    strats = cerebro.optstrategy(
        TestStrategy,
        maperiod=range(10, 31))

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/orcl-1995-2014.txt')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2000, 12, 31),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Run over everything
    cerebro.run(maxcpus=1)

# =======

# class PandasDataUSA(bt.feeds.PandasData):

#     lines = ("SPXL", "SPXS")
#     params = (
#         ("datetime", None),
#         ("SPXL", -1), ("SPXS", -1),
#         ("open", None), ("high", None), ("low", None), ("close", None),
#         ("volume", None), ("openinterest", None),
#     )
#     datafields = bt.feeds.PandasData.datafields + (["SPXL", "SPXS",])


# # Create a Stratey
# class TestStrategy(bt.Strategy):
#     params = (
#         ('maperiod', 3),
#     )

#     def log(self, txt, dt=None):
#         ''' Logging function fot this strategy'''
#         dt = dt or self.datas[0].datetime.date(0)
#         print('%s, %s' % (dt.isoformat(), txt))

#     def __init__(self):
#         # Keep a reference to the "close" line in the data[0] dataseries
#         # self.dataclose = self.datas[0].close
#         self.dataclose = self.datas[0].SPXL

#         # To keep track of pending orders and buy price/commission
#         self.order = None
#         self.buyprice = None
#         self.buycomm = None

#         # Add a MovingAverageSimple indicator
#         self.sma = bt.indicators.SimpleMovingAverage(
#             self.datas[0], period=self.params.maperiod)

#     def notify_order(self, order):
#         if order.status in [order.Submitted, order.Accepted]:
#             # Buy/Sell order submitted/accepted to/by broker - Nothing to do
#             return

#         # Check if an order has been completed
#         # Attention: broker could reject order if not enough cash
#         if order.status in [order.Completed]:
#             if order.isbuy():
#                 self.log(
#                     'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
#                     (order.executed.price,
#                      order.executed.value,
#                      order.executed.comm))

#                 self.buyprice = order.executed.price
#                 self.buycomm = order.executed.comm
#             else:  # Sell
#                 self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
#                          (order.executed.price,
#                           order.executed.value,
#                           order.executed.comm))

#             self.bar_executed = len(self)

#         elif order.status in [order.Canceled, order.Margin, order.Rejected]:
#             self.log('Order Canceled/Margin/Rejected')

#         self.order = None

#     def notify_trade(self, trade):
#         if not trade.isclosed:
#             return

#         self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
#                  (trade.pnl, trade.pnlcomm))

#     def next(self):
#         # Simply log the closing price of the series from the reference
#         # self.log('Close, %.2f' % self.dataclose[0])
#         self.log(txt=f"close: {self.dataclose[0]:.2f}")

#         # Check if an order is pending ... if yes, we cannot send a 2nd one
#         if self.order:
#             return

#         # Check if we are in the market
#         if not self.position:

#             # Not yet ... we MIGHT BUY if ...
#             # if self.dataclose[0] > self.sma[0]:
#             if self.dataclose[0] < self.dataclose[-1]:

#                 # BUY, BUY, BUY!!! (with all possible default parameters)
#                 self.log('BUY CREATE, %.2f' % self.dataclose[0])

#                 # Keep track of the created order to avoid a 2nd order
#                 self.order = self.buy()

#         else:

#             # if self.dataclose[0] < self.sma[0]:
#             if len(self) >= (self.bar_executed + 2):
#                 # SELL, SELL, SELL!!! (with all possible default parameters)
#                 self.log('SELL CREATE, %.2f' % self.dataclose[0])

#                 # Keep track of the created order to avoid a 2nd order
#                 self.order = self.sell()


# if __name__ == '__main__':

#     if DEBUG: logger.debug(f"******* START BACKTEST *******")

#     spx_dict = {
#         'index': [Timestamp('2025-07-02 04:00:00'), Timestamp('2025-07-03 04:00:00'), Timestamp('2025-07-07 04:00:00'), Timestamp('2025-07-08 04:00:00'), Timestamp('2025-07-09 04:00:00'), Timestamp('2025-07-10 04:00:00'), Timestamp('2025-07-11 04:00:00'), Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00')],
#         'columns': ['SPXL', 'SPXS'],
#         'data': [[17468, 466], [17902, 455], [17552, 465], [17528, 466], [17763, 459], [17927, 454], [17739, 460], [17796, 458], [17740, 460], [17669, 462], [18035, 452], [18074, 452], [18208, 448], [18118, 450], [18519, 440], [18662, 437], [18808, 434], [18826, 434], [18732, 436], [18610, 439], [18526, 441], [17516, 465], [18140, 450], [18062, 450], [18296, 445], [18375, 443], [18680, 436], [18670, 437], [19093, 426]],
#         'index_names': ['datetime'], 'column_names': [None]
#     }
#     spx_df = pandas.DataFrame.from_dict(data=spx_dict, orient="tight")
#     spx_df.name = "spx"
#     sig_dict = {
#         'index': [Timestamp('2025-07-02 04:00:00'), Timestamp('2025-07-03 04:00:00'), Timestamp('2025-07-07 04:00:00'), Timestamp('2025-07-08 04:00:00'), Timestamp('2025-07-09 04:00:00'), Timestamp('2025-07-10 04:00:00'), Timestamp('2025-07-11 04:00:00'), Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00')],
#         'columns': ['HYG', 'XLF', 'XLY', 'sum'],
#         'data': [[0, 0, 0, 0], [-1, 0, -1, -2], [-1, -1, -1, -3], [1, -1, 1, 1], [1, 1, 1, 3], [-1, -1, 1, -1], [-1, -1, 1, -1], [-1, -1, -1, -3], [-1, -1, -1, -3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [-1, 1, -1, -1], [-1, 1, -1, -1], [1, -1, 1, 1], [-1, -1, 1, -1], [-1, -1, -1, -3], [-1, -1, -1, -3], [1, -1, -1, -1], [1, -1, -1, -1], [1, 1, 1, 3], [1, 1, 1, 3], [1, -1, 1, 1], [-1, -1, 1, -1], [-1, 1, 1, 1], [1, 1, 1, 3], [1, 1, 1, 3]],
#         'index_names': ['date'], 'column_names': [None]
#     }
#     sig_df = pandas.DataFrame.from_dict(data=sig_dict, orient="tight")
#     sig_df.name = "sig"

#     # Create a cerebro entity
#     cerebro = bt.Cerebro()

#     # Add a strategy
#     cerebro.addstrategy(TestStrategy)

#     data = PandasDataUSA(dataname=spx_df, datetime=-1)

#     # Add the Data Feed to Cerebro
#     cerebro.adddata(data)

#     # Set our desired cash start
#     cerebro.broker.setcash(10_000_000.0)

#     # Add a FixedSize sizer according to the stake
#     cerebro.addsizer(bt.sizers.FixedSize, stake=10)

#     # Set the commission
#     cerebro.broker.setcommission(commission=0.0)

#     # Print out the starting conditions
#     # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
#     print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")

#     # Run over everything
#     cerebro.run()

#     # Print out the final result
#     # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
#     print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")

#     # cerebro.plot()
