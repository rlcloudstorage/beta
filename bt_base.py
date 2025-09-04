""""""
import argparse, logging, logging.config

import backtrader as bt

from temp import data

usa_bull = data.SPXL_sig
usa_bear = data.SPXS

DEBUG = True
# DEBUG = False


logging.config.fileConfig(fname="logger.ini")
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class ApproximatePercentSizer(bt.Sizer):
    """based on percent of starting cash, shares are rounded to nearest 100"""
    params = (('percents', 80), )

    def _getsizing(self, comminfo, cash, data, isbuy):
        return int(round(self.broker.startingcash * self.params.percents / 100 / data[0], -2))


class PandasDataSignal(bt.feeds.PandasData):
    """"""
    lines = ("TS", )
    params = (
        ("datetime", None),
        ("TS", -1), ("SPXL", -1), ("SPXS", -1),
        ("open", -1), ("high", -1), ("low", -1), ("close", -1), ("volume", -1),
        ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["TS"])


class St(bt.Strategy):
    """"""
    params = (
        ('maperiod', 4),
        # ('printlog', False),
    )

    def __init__(self):
        # keep track of pending orders, price, commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # add an indicator
        # self.ts_sig = bt.indicators.CrossOver(self.datas[0].TS, 0, plotname="TS Signal", subplot=True)
        # self.ts_sig = bt.indicators.ExponentialMovingAverage(
        self.ts_sig = bt.indicators.MovingAverageSimple(
            self.datas[0].TS, period=self.params.maperiod, plothlines=[0.0], plotname="TS Signal", subplot=True
        )
        # if DEBUG: logger.debug(f"__init__.self.ts_sig.__dict__: {self.ts_sig.__dict__}")
        if DEBUG:
            logger.debug(f"__init__.self.ts_sig.data: {[i for i in self.ts_sig.data]}")

    def log(self, txt, dt=None):
        """"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")
        # with open("backtrader.log", "a") as f:
        #     print(f"{dt.isoformat()}, {txt}", file=f)

    def notify_cashvalue(self, cash, value):
        """"""
        self.log(txt=f"cash on Hand: {cash:,.2f}, account Value: {value:,.2f}")

    def notify_order(self, order):
        """"""
        if order.status in [order.Submitted, order.Accepted]:
            self.log(txt=f"order submitted/accepted: status {order.status}")
            return

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(txt=f"BUY EXECUTED, Price: {order.executed.price:,.2f}, Cost: {order.executed.value:,.2f}, Comm {order.executed.comm:,.2f}")
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log(txt=f"SELL EXECUTED, Price: {order.executed.price:,.2f}, Cost: {order.executed.value:,.2f}, Comm {order.executed.comm:,.2f}")
            self.bar_executed = len(self)

        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            self.log(txt=f"Order canceled/margin/rejected: status {order.status}")
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(txt=f"TRADE PROFIT/LOSS, Gross {trade.pnl:,.2f}, Net {trade.pnlcomm:,.2f}")

    def next(self):
        """"""
        in_bull = self.getposition(self.datas[0])
        in_bear = self.getposition(self.datas[1])
        if DEBUG: logger.debug(f"*** ts_sig: {self.ts_sig[0]} ***")

        # check bear (short) position
        match bool(in_bear):
            case True:  # already short
                if self.ts_sig > 0:  # take profit
                    self.order = self.close(self.datas[1])
                    self.log(txt=f"CREATE SELL bear @ {self.datas[1][0]:,.2f}")
                elif self.ts_sig <= 0:  # hold
                    pass
            case False:  # might short
                if self.ts_sig >= 0:  # not yet
                    pass
                elif self.ts_sig < 0:  # short now
                    self.order = self.buy(self.datas[1])
                    self.log(txt=f"CREATE BUY bear @ {self.datas[1][0]:,.2f}")

        # check bull (long) position
        match bool(in_bull):
            case True:  # already long
                if self.ts_sig <= 0:  # take profit
                    self.log(txt=f"CREATE SELL bull @ {self.datas[0][0]:,.2f}")
                    self.order = self.close(self.datas[0])
                elif self.ts_sig > 0:  # hold
                    pass
            case False:  # might long
                if self.ts_sig <= 0:  # not yet
                    pass
                elif self.ts_sig > 0:  # long now
                    self.order = self.buy(self.datas[0])
                    self.log(txt=f"CREATE BUY bull @ {self.datas[0][0]:,.2f}")

        if in_bull or in_bear:
            self.log(txt=f"{in_bull.size} shares bull @ {in_bull.price:.2f}, {in_bear.size} shares bear @ {in_bear.price:.2f}")

    def stop(self):
        self.log(txt=f"\nMA period {self.params.maperiod}, ending value {self.broker.getvalue():.2f}")


def run_strat(args=None):
    if DEBUG: logger.debug(f"******* bt_base.py START BACKTRADER *******")

    args = parse_args(args)

    cerebro = bt.Cerebro()

    # Data feed kwargs
    kwargs = dict()
    # Data feed
    bull_data = PandasDataSignal(dataname=args.bull_data, datetime=-1, **kwargs)
    bull_data.plotmaster = bull_data
    bear_data = bt.feeds.PandasData(dataname=args.bear_data, datetime=-1, **kwargs)
    cerebro.adddata(data=bull_data, name="bull")
    cerebro.adddata(data=bear_data, name="bear")
    # if DEBUG:
    #     [logger.debug(f"cerebro.datas: {cerebro.datas[i]}, {d._name} data:\n{d._dataname}\n")  for i, d in enumerate(cerebro.datas)]
    # Broker
    cerebro.broker.setcash(100_000.00)
    cerebro.broker.setcommission(0.001)
    # Sizer
    cerebro.addsizer(ApproximatePercentSizer, percents=20)
    # Strategy
    cerebro.addstrategy(St)
    # cerebro.optstrategy(St, maperiod=range(1, 8))
    # Execute
    cerebro.run()
    # cerebro.run(maxcpus=1)
    # Plot if requested
    if args.plot:
        cerebro.plot(**eval('dict(' + args.plot + ')'))


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=('Packages and Kalman')
    )
    parser.add_argument('--bull_data', default=usa_bull, required=False, help='Data to read in')
    parser.add_argument('--bear_data', default=usa_bear, required=False, help='Data to read in')
    parser.add_argument('--plot', required=False, default='', nargs='?', const='{}', metavar='kwargs', help='kwargs in key=value format')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    run_strat()
