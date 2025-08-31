""""""
import logging, logging.config

import backtrader as bt

from temp import data


DEBUG = True
# DEBUG = False

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


class ApproximatePercentSizer(bt.Sizer):
    params = (('percents', 40), )

    def _getsizing(self, comminfo, cash, data, isbuy):
        """"""
        # if DEBUG: logger.debug(f"self.broker.startingcash: {self.broker.startingcash}\n")
        return int(round(self.broker.startingcash * self.params.percents / 100 / data[0], -2))


class PandasDataOHLCC(bt.feeds.PandasData):
    """"""
    lines = ("cwap",)
    params = (
        ("datetime", None),
        ("cwap", -1),
        ("open", -1), ("high", -1), ("low", -1), ("close", -1),
        ("volume", -1), ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["cwap",])


class PandasSignalDataUSA(bt.feeds.PandasData):
    """"""
    lines = ("HYG", "XLF", "XLY", "sum")
    params = (
        ("datetime", None),
        ("HYG", -1), ("XLF", -1), ("XLY", -1), ("sum", -1),
        ("open", None), ("high", None), ("low", None), ("close", None),
        ("volume", None), ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["HYG", "XLF", "XLY", "sum"])


class TradeLongShort(bt.Strategy):
    """"""
    params = (
        ('period_1', 2),
        ('period_2', 5),
        # ('prepend_constant', True),
    )

    def __init__(self):
        """"""
        self.SPXL = self.datas[0].close
        self.SPXS = self.datas[1].close

        ma_1 = bt.indicators.SMA(self.SPXL, period=self.p.period_1)
        ma_2 = bt.indicators.SMA(self.SPXL, period=self.p.period_2)

        cross = bt.ind.CrossOver(ma_1, ma_2)

        self.buy_sig = cross > 0
        self.sell_sig = cross < 0

        self.order = None


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
            self.log(txt=f"order completed: status {order.status}")
            if order.isbuy():
                self.log(txt=f"BUY EXECUTED, Price: {order.executed.price:,.2f}, Cost: {order.executed.value:,.2f}, Comm {order.executed.comm:,.2f}")
            elif order.issell():
                self.log(txt=f"SELL EXECUTED, Price: {order.executed.price:,.2f}, Cost: {order.executed.value:,.2f}, Comm {order.executed.comm:,.2f}")
            self.bar_executed = len(self)
        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            self.log(txt=f"Order canceled/margin/rejected: status {order.status}")
        self.order = None


    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(txt=f"OPERATION PROFIT, GROSS {trade.pnl:,.2f}, NET {trade.pnlcomm:,.2f}")


    def next(self):
        """"""
        # if DEBUG: logger.debug(f" *** self._orderspending:\n{[ i.p.__dict__ for i in self._orderspending]}")

        in_spxl = self.getposition(self.dnames.SPXL)
        in_spxs = self.getposition(self.dnames.SPXS)

        # long (position in SPXL)?
        match bool(in_spxl):
            case True:  # already in market
                if self.sell_sig:  # take profit
                    self.log(txt=f"CREATE SELL SPXL @ {self.SPXL[0]:,.2f}")
                    self.order = self.close(self.dnames.SPXL)
                elif self.buy_sig:  # hold position
                    pass
            case False:  # might go long
                if self.buy_sig:  # long now
                    self.log(txt=f"CREATE BUY SPXL @ {self.SPXL[0]:,.2f}")
                    self.order = self.buy(self.dnames.SPXL)
                elif self.sell_sig:  # not yet
                    pass

        # short (position in SPXS)?
        match bool(in_spxs):
            case True:  # already short
                if self.buy_sig:  # take profit
                    self.log(txt=f"CREATE SELL SPXS @ {self.SPXS[0]:,.2f}")
                    self.order = self.close(self.dnames.SPXS)
                elif self.sell_sig:  # hold position
                    pass
            case False:  # might short
                if self.buy_sig:  # not yet
                    pass
                elif self.sell_sig:  # short now
                    self.log(txt=f"CREATE BUY SPXS @ {self.SPXS[0]:,.2f}")
                    self.order = self.buy(self.dnames.SPXS)

        if in_spxl or in_spxs:
            self.log(txt=f"{in_spxl.size} shares SPXL @ {in_spxl.price:.2f}, {in_spxs.size} shares SPXS @ {in_spxs.price:.2f}")


def main() -> None:
    if DEBUG: logger.debug(f"main()")


if __name__ == "__main__":
    if DEBUG: logger.debug(f"******* START BACKTRADER *******")

    SPXL = bt.feeds.PandasData(dataname=data.SPXL, datetime=-1, name="SPXL")
    SPXS = bt.feeds.PandasData(dataname=data.SPXS, datetime=-1, name="SPXS")

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100_000.00)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.adddata(data=SPXL, )
    cerebro.adddata(data=SPXS, )
    cerebro.addsizer(ApproximatePercentSizer, percents=40)
    cerebro.addstrategy(TradeLongShort)
    # cerebro.addwriter(bt.WriterFile, csv=True)

    # if DEBUG: logger.debug(f"cerebro.__dict__: {cerebro.__dict__}")
    # if DEBUG: [logger.debug(f"{d._name} data:\n{d._dataname}\n")  for d in cerebro.datas]

    print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")
    cerebro.run()
    print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")

    # cerebro.plot()
