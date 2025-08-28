""""""
import logging, logging.config

import backtrader as bt

from temp import data


DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', True),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            # dt = dt or self.datas[0].datetime.date(0)
            dt = dt or self.datas[1].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        # self.dataclose = self.datas[0].close
        self.dataclose = self.datas[1].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            # self.datas[0], period=self.params.maperiod)
            self.datas[1], period=self.params.maperiod)

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
        # self.log('Close, %.2f' % self.dataclose[0])
        self.log('Close, %.2f' % self.dataclose[1])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            # if self.dataclose[0] > self.sma[0]:
            if self.dataclose[1] > self.sma[1]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                # self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.log('BUY CREATE, %.2f' % self.dataclose[1])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            # if self.dataclose[0] < self.sma[0]:
            if self.dataclose[1] < self.sma[1]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                # self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.log('SELL CREATE, %.2f' % self.dataclose[1])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)


if __name__ == '__main__':

    # # Create a cerebro entity
    # cerebro = bt.Cerebro()
    cerebro = bt.Cerebro(stdstats=True, cheat_on_open=True, optreturn=False)
    # optreturn=False

    # Add a strategy
    strats = cerebro.optstrategy(
        TestStrategy,
        maperiod=range(14, 18))

    # # Add the Data Feed to Cerebro
    # cerebro.adddata(data)
    # spxl = bt.feeds.PandasData(dataname=SPXL, datetime=-1)
    spxl = bt.feeds.PandasData(dataname=data.SPXL, datetime=-1)
    cerebro.adddata(data=spxl, name="SPXL")
    spxs = bt.feeds.PandasData(dataname=data.SPXS, datetime=-1)
    cerebro.adddata(data=spxs, name="SPXS")

    # Set our desired cash start
    cerebro.broker.setcash(100_000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Run over everything
    cerebro.run(maxcpus=1)

    # cerebro.plot()
