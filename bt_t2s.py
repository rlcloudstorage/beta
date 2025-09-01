""""""
import logging, logging.config

import backtrader as bt
# import pandas as pd

from temp import data

BULL = data.SPXL
BEAR = data.SPXS
SIGNAL = data.signal
DEBUG = True
# DEBUG = False

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


class ApproximatePercentSizer(bt.Sizer):
    """based on percent of starting cash, shares are rounded to nearest 100"""
    params = (('percents', 40), )

    def _getsizing(self, comminfo, cash, data, isbuy):
        # return int(round(cash * self.params.percents / 100 / data[0], -2))
        return int(round(self.broker.startingcash * self.params.percents / 100 / data[0], -2))


class LongShortIndicator(bt.Indicator):
    """"""
    lines = ("TS", )

    def __init__(self):
        # self.TS = cerebro.datas[2].TS
        # self.lines.TS = self.TS
        self.lines.TS = self.data
        super(LongShortIndicator, self).__init__()

        if DEBUG: logger.debug(f"LongShortIndicator self.TS: {[i for i in self.TS]}")
        if DEBUG: logger.debug(f"LongShortIndicator self.lines.TS: {[i for i in self.lines.TS]}")

    # def next(self):
    #     self.lines.TS[0] = self.TS[0]
    #     if DEBUG: logger.debug(f"self.lines.TS[0]: {self.lines.TS[0]}")


class PandasSignalData(bt.feeds.PandasData):
    """TS: sg filter time shift slope direction change"""
    lines = ("TS", )
    params = (
        ("datetime", None),
        ("TS", -1),
        ("open", None), ("high", None), ("low", None), ("close", None), ("volume", None),
        ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["TS", ])


class TradeLongShort(bt.Strategy):
    """"""
    params = (('prepend_constant', True),)

    def __init__(self):
        """"""
        # self.bull = self.datas[0].close
        # self.bear = self.datas[1].close
        self.ts_sig = None

        if DEBUG: logger.debug(f"__init__.TS: {[i for i in self.datas[2].TS]}")

        self.ts_sig = LongShortIndicator(self.datas[2].TS)
        self.order = None
        self.buyprice = None
        self.buycomm = None


    def log(self, txt, dt=None):
        """"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")
        # with open("backtrader.log", "a") as f:
        #     print(f"{dt.isoformat()}, {txt}", file=f)


    def notify_cashvalue(self, cash, value):
        """"""
        self.log(txt=f"Cash on Hand: {cash:,.2f}, Account Value: {value:,.2f}")


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
        self.log(txt=f"TRADE PROFIT/LOSS, GROSS {trade.pnl:,.2f}, NET {trade.pnlcomm:,.2f}")


    def next(self):
        """"""
        # if DEBUG: logger.debug(f" *** self._orderspending:\n{[ i.p.__dict__ for i in self._orderspending]}")

        in_bull = self.getposition(self.datas[0])
        in_bear = self.getposition(self.datas[1])

        # long (position in SPXL)?
        match bool(in_bull):
            case True:  # already in market
                if self.ts_sig <= 0:  # take profit
                    self.log(txt=f"CREATE SELL BULL @ {self.datas[0][0]:,.2f}")
                    self.order = self.close(self.datas[0])
                elif self.ts_sig > 0:  # hold position
                    pass
            case False:  # might go long
                if self.ts_sig > 0:  # long now
                    self.log(txt=f"CREATE BUY  @ {self.datas[0][0]:,.2f}")
                    self.order = self.buy(self.datas[0])
                elif self.ts_sig <= 0:  # not yet
                    pass

        # short (position in SPXS)?
        match bool(in_bear):
            case True:  # already short
                if self.ts_sig > 0:  # take profit
                    self.log(txt=f"CREATE SELL SPXS @ {self.datas[1][0]:,.2f}")
                    self.order = self.close(self.datas[1])
                elif self.ts_sig <= 0:  # hold position
                    pass
            case False:  # might short
                if self.ts_sig >= 0:  # not yet
                    pass
                elif self.ts_sig < 0:  # short now
                    self.log(txt=f"CREATE BUY SPXS @ {self.datas[1][0]:,.2f}")
                    self.order = self.buy(self.datas[1])

        if in_bull or in_bear:
            self.log(txt=f"{in_bull.size} shares SPXL @ {in_bull.price:.2f}, {in_bear.size} shares SPXS @ {in_bear.price:.2f}")


if __name__ == "__main__":
    if DEBUG: logger.debug(f"******* START BACKTRADER *******")

    bull = bt.feeds.PandasData(dataname=BULL, datetime=-1, name="bull")
    bear = bt.feeds.PandasData(dataname=BEAR, datetime=-1, name="bear")
    signal = PandasSignalData(dataname=SIGNAL, datetime=-1, name="signal")

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100_000.00)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.adddata(data=bull, )
    cerebro.adddata(data=bear, )
    cerebro.adddata(data=signal)
    cerebro.addsizer(ApproximatePercentSizer, percents=40)
    cerebro.addstrategy(TradeLongShort)
    # cerebro.addwriter(bt.WriterFile, csv=True)

    # if DEBUG: logger.debug(f"cerebro.__dict__: {cerebro.__dict__}")
    if DEBUG: [logger.debug(f"cerebro.datas: {cerebro.datas[i]}, {d._name} data:\n{d._dataname}\n")  for i, d in enumerate(cerebro.datas)]

    print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")
    cerebro.run()
    print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")

    # cerebro.plot(figsize=(10, 7.5))
