""""""
import logging, logging.config

import backtrader as bt

import pandas
from pandas import Timestamp


DEBUG = True
DB = "/home/la/dev/data/tiingo_sm.db"

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

ctx = {}


class PandasDataUSA(bt.feeds.PandasData):

    lines = ("SPXL", "SPXS")
    params = (
        ("datetime", None),
        ("SPXL", -1), ("SPXS", -1),
        ("open", None), ("high", None), ("low", None), ("close", None),
        ("volume", None), ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["SPXL", "SPXS",])


class TestStrategy(bt.Strategy):

    def log(self, txt: str, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        self.dataclose = self.datas[0].SPXL
        self.order = None
        self.buyprice = None
        self.sellcomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(txt=f" *** BUY EXECUTED ***")
            elif order.issell():
                self.log(txt=f" *** SELL EXECUTED ***")

            self.bar_executed = len(self)

        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            self.log(txt=f" *** ORDER CANCEL ***")

        self.order = None

    def next(self):
        self.log(txt=f"close: {self.dataclose[0]}")

        if self.order:
            return

        if not self.position:

            if self.dataclose[0] < self.dataclose[-1]:
                # if self.dataclose[-1] < self.dataclose[-2]:
                    self.log(txt=f" *** CREATE BUY ***")
                    self.order = self.buy()

        else:
            # if len(self) >= (self.bar_executed + 5):
            if len(self) >= (self.bar_executed + 2):
                self.log(" *** CREATE SELL ***")

                self.order = self.sell()


def main() -> None:
    if DEBUG: logger.debug(f"main()")


if __name__ == "__main__":
    import unittest

    if DEBUG: logger.debug(f"******* START BACKTEST *******")

    spx_dict = {
        'index': [Timestamp('2025-07-02 04:00:00'), Timestamp('2025-07-03 04:00:00'), Timestamp('2025-07-07 04:00:00'), Timestamp('2025-07-08 04:00:00'), Timestamp('2025-07-09 04:00:00'), Timestamp('2025-07-10 04:00:00'), Timestamp('2025-07-11 04:00:00'), Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00')],
        'columns': ['SPXL', 'SPXS'],
        'data': [[17468, 466], [17902, 455], [17552, 465], [17528, 466], [17763, 459], [17927, 454], [17739, 460], [17796, 458], [17740, 460], [17669, 462], [18035, 452], [18074, 452], [18208, 448], [18118, 450], [18519, 440], [18662, 437], [18808, 434], [18826, 434], [18732, 436], [18610, 439], [18526, 441], [17516, 465], [18140, 450], [18062, 450], [18296, 445], [18375, 443], [18680, 436], [18670, 437], [19093, 426]],
        'index_names': ['datetime'], 'column_names': [None]
    }
    spx_df = pandas.DataFrame.from_dict(data=spx_dict, orient="tight")
    spx_df.name = "spx"
    sig_dict = {
        'index': [Timestamp('2025-07-02 04:00:00'), Timestamp('2025-07-03 04:00:00'), Timestamp('2025-07-07 04:00:00'), Timestamp('2025-07-08 04:00:00'), Timestamp('2025-07-09 04:00:00'), Timestamp('2025-07-10 04:00:00'), Timestamp('2025-07-11 04:00:00'), Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00')],
        'columns': ['HYG', 'XLF', 'XLY', 'sum'],
        'data': [[0, 0, 0, 0], [-1, 0, -1, -2], [-1, -1, -1, -3], [1, -1, 1, 1], [1, 1, 1, 3], [-1, -1, 1, -1], [-1, -1, 1, -1], [-1, -1, -1, -3], [-1, -1, -1, -3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [-1, 1, -1, -1], [-1, 1, -1, -1], [1, -1, 1, 1], [-1, -1, 1, -1], [-1, -1, -1, -3], [-1, -1, -1, -3], [1, -1, -1, -1], [1, -1, -1, -1], [1, 1, 1, 3], [1, 1, 1, 3], [1, -1, 1, 1], [-1, -1, 1, -1], [-1, 1, 1, 1], [1, 1, 1, 3], [1, 1, 1, 3]],
        'index_names': ['date'], 'column_names': [None]
    }
    sig_df = pandas.DataFrame.from_dict(data=sig_dict, orient="tight")
    sig_df.name = "sig"

    main()

# =======

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10_000_000.00)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(TestStrategy)

    data = PandasDataUSA(dataname=spx_df, datetime=-1)
    if DEBUG: logger.debug(f"data: {data.datafields}")

    cerebro.adddata(data=data, name="spx")
    print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")

    cerebro.run()
    print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")

# =======

    class TestBacktestingFunctions(unittest.TestCase):
        """"""
        @classmethod
        def setUpClass(cls):
            print(f"\n-setUp({cls})")

        @unittest.skip
        def test_main(self):
            main()

        @classmethod
        def tearDownClass(cls):
            print(f"\n-tearDown({cls})")

    unittest.main()
