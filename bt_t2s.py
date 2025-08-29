""""""
import logging, logging.config

import backtrader as bt

from temp import data


DEBUG = True
# DEBUG = False

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


class PandasDataOHLCC(bt.feeds.PandasData):

    lines = ("cwap",)
    params = (
        ("datetime", None),
        ("cwap", -1),
        ("open", -1), ("high", -1), ("low", -1), ("close", -1),
        ("volume", -1), ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["cwap",])


class PandasSignalDataUSA(bt.feeds.PandasData):

    lines = ("HYG", "XLF", "XLY", "sum")
    params = (
        ("datetime", None),
        ("HYG", -1), ("XLF", -1), ("XLY", -1), ("sum", -1),
        ("open", None), ("high", None), ("low", None), ("close", None),
        ("volume", None), ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["HYG", "XLF", "XLY", "sum"])


class TradeSPXLorSPXS(bt.Strategy):
    """"""

    params = (
        ('period_1', 3),
        ('period_2', 7),
        # ('prepend_constant', True),
    )

    def log(self, txt, dt=None):
        """"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        self.SPXL = self.datas[0].close
        self.SPXS = self.datas[1].close

        ma1 = bt.indicators.SMA(self.SPXL, period=self.p.period_1)
        ma2 = bt.indicators.SMA(self.SPXL, period=self.p.period_2)

        cross = bt.ind.CrossOver(ma1, ma2)

        self.buy_sig = cross > 0
        self.sell_sig = cross < 0

        self.order = None
        # self.exec_price = None
        # self.sale_comm = None

        print(f"datanames: {self.getdatanames()}")

    def notify_cashvalue(self, cash, value):
        """"""
        self.log(f"Cash Available: {cash:,.2f}, Account Value: {value:,.2f}")

    def notify_order(self, order):
        """"""
        if order.status in [order.Submitted, order.Accepted]:
            if DEBUG: logger.debug(f"order submitted/accepted: status {order.status}")
            return

        if order.status in [order.Completed]:  # Note: broker could reject order if not enough cash
            if DEBUG: logger.debug(f"order completed: status {order.status}")
            # self.exec_price = order.executed.price
            # self.sale_comm = order.executed.comm

            if order.isbuy():
                self.log(txt=f"BUY EXECUTED, Price: {order.executed.price:,.2f}, Cost: {order.executed.value:,.2f}, Comm {order.executed.comm:,.2f}")

            elif order.issell():
                self.log(txt=f"SELL EXECUTED, Price: {order.executed.price:,.2f}, Cost: {order.executed.value:,.2f}, Comm {order.executed.comm:,.2f}")

            # if DEBUG: logger.debug(f"Get position SPXL:\n{self.getposition(self.datas[0])}")
            # if DEBUG: logger.debug(f"Get position SPXS:\n{self.getposition(self.datas[1])}")

            self.bar_executed = len(self)

        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            if DEBUG: logger.debug(f"Order canceled/margin/rejected: status {order.status}")
            self.log(txt=f" *** Order Canceled/Margin/Rejected ***")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(txt=f"OPERATION PROFIT, GROSS {trade.pnl:,.2f}, NET {trade.pnlcomm:,.2f}")

    def next(self):
        # if DEBUG: logger.debug(f"buy signal:{self.buy_sig.__dict__}, sell signal: {self.sell_sig.__dict__}")
        self.log(txt=f"SPXL: {self.SPXL[0]:,.2f}, SPXS: {self.SPXS[0]:,.2f}")

        # Check if we are in the market
        if not self.getposition(self.datas[1]):
            # if DEBUG: logger.debug(f"Get position:\n{self.getposition(self.dnames.SPXS)}")
            self.log(f"Position size {self.position.size}")
            # Not yet ... we MIGHT BUY if ...
            if self.buy_sig:
                    # if sma[0]<top[-5]:
                # BUY, BUY, BUY!!! (with default parameters)
                self.log(f"CREATE BUY SPXL @ {self.SPXL[0]:,.2f}")

                # Keep track of the created order to avoid a 2nd order
                # self.order = self.buy(self.datas[0])
                self.order = self.buy(self.dnames.SPXL)
                # self.order = self.sell(self.datas[1])
            elif self.sell_sig:
                self.log(f"CREATE BUY SPXS @ {self.SPXS[0]:,.2f}")
                # self.order = self.buy(self.datas[1])
                self.order = self.buy(self.dnames.SPXS)

        # Already in the market ... we might sell
        else:
            self.log(f"Position size {self.position.size}")
            if self.buy_sig:
                self.log(f"CREATE SELL SPXL @ {self.SPXL[0]:,.2f}")

                self.order = self.close(self.datas[1])
                self.order = self.buy(self.datas[0])

            elif self.sell_sig:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log(f"CREATE SELL SPXL @ {self.SPXL[0]:,.2f}")

                # Keep track of the created order to avoid a 2nd order
                self.order = self.close(self.datas[0])
                self.order = self.buy(self.datas[1])


def main() -> None:
    if DEBUG: logger.debug(f"main()")


if __name__ == "__main__":
    if DEBUG: logger.debug(f"******* START BACKTEST *******")

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100_000.00)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    cerebro.addstrategy(TradeSPXLorSPXS)

    SPXL = bt.feeds.PandasData(dataname=data.SPXL, datetime=-1, name="SPXL")
    SPXS = bt.feeds.PandasData(dataname=data.SPXS, datetime=-1, name="SPXS")

    cerebro.adddata(data=SPXL, )
    cerebro.adddata(data=SPXS, )

    [print(f"{d._name} data:\n{d._dataname}\n") for d in cerebro.datas]
    # if DEBUG: logger.debug(f"cerebro.__dict__: {cerebro.__dict__}")

    print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")
    cerebro.run()
    print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")

    # cerebro.plot()
