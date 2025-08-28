""""""
import logging, logging.config

import backtrader as bt

import pandas as pd
from pandas import Timestamp


DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

ctx = {}


class PandasDataUSA(bt.feeds.PandasData):

    lines = ("SIGNAL", "SPXL", "SPXS")
    params = (
        ("datetime", None),
        ("SIGNAL", -1), ("SPXL", -1), ("SPXS", -1),
        ("open", -1), ("high", -1), ("low", -1), ("close", -1),
        ("volume", -1), ("openinterest", None),
    )
    datafields = bt.feeds.PandasData.datafields + (["SIGNAL", "SPXL", "SPXS"])


class TestStrategy(bt.Strategy):

    def log(self, txt: str, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        self.dataclose = self.datas[0]
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

    SPXL_dict = {
        'index': [Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00'), Timestamp('2025-08-13 04:00:00'), Timestamp('2025-08-14 04:00:00'), Timestamp('2025-08-15 04:00:00'), Timestamp('2025-08-18 04:00:00'), Timestamp('2025-08-19 04:00:00'), Timestamp('2025-08-20 04:00:00'), Timestamp('2025-08-21 04:00:00'), Timestamp('2025-08-22 04:00:00')],
        'columns': ['open', 'high', 'low', 'close', 'volume'],
        'data': [[177.15, 178.84, 176.0, 178.49, 2292399], [180.87, 181.09, 176.15, 176.18, 2427809], [177.56, 178.33, 172.71, 177.86, 2619509], [178.11, 181.46, 177.87, 181.04, 2267964], [182.05, 182.13, 179.63, 180.6, 1946603], [181.6, 184.0, 181.21, 181.55, 2388254], [181.78, 182.29, 179.37, 181.54, 1938576], [183.91, 186.18, 182.3, 186.14, 2471951], [186.5, 187.8, 185.96, 186.37, 2018385], [186.78, 188.91, 186.55, 188.43, 1606586], [188.84, 189.31, 187.14, 188.29, 1925650], [189.56, 189.79, 185.97, 186.76, 2123889], [187.4, 188.87, 183.42, 186.06, 2895477], [190.37, 190.72, 182.71, 183.8, 3018674], [178.71, 178.71, 172.63, 174.65, 4788396], [178.02, 182.63, 177.9, 182.53, 2112648], [183.15, 183.84, 179.0, 179.83, 1928098], [180.71, 184.41, 179.92, 183.76, 1941909], [186.85, 187.47, 180.66, 183.43, 2431137], [184.76, 187.88, 184.53, 187.4, 1965573], [187.66, 188.99, 185.24, 186.29, 5326281], [188.34, 192.38, 187.05, 192.15, 7148865], [194.13, 195.28, 192.18, 194.12, 2437479], [192.22, 194.72, 191.74, 194.04, 2379721], [194.89, 194.99, 191.78, 192.62, 2427694], [192.04, 193.0, 191.43, 192.43, 1579757], [192.23, 193.1, 188.08, 189.21, 3094078], [188.75, 188.89, 183.05, 187.53, 2976422], [185.91, 187.4, 183.77, 185.24, 2419647], [187.09, 194.7, 186.7, 193.59, 3024987]],
        'index_names': ['datetime'], 'column_names': [None]
    }
    SPXL = pd.DataFrame.from_dict(data=SPXL_dict, orient="tight")
    SPXL.name = "SPXL"
    # print(f"SPXL dataframe:\n{SPXL}, type(datetime):\n{type(SPXL.index[0])}")

    SPXS_dict = {
        'index': [Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00'), Timestamp('2025-08-13 04:00:00'), Timestamp('2025-08-14 04:00:00'), Timestamp('2025-08-15 04:00:00'), Timestamp('2025-08-18 04:00:00'), Timestamp('2025-08-19 04:00:00'), Timestamp('2025-08-20 04:00:00'), Timestamp('2025-08-21 04:00:00'), Timestamp('2025-08-22 04:00:00')],
        'columns': ['open', 'high', 'low', 'close', 'volume'],
        'data': [[4.6, 4.64, 4.56, 4.56, 36876427], [4.51, 4.63, 4.5, 4.63, 51472163], [4.59, 4.72, 4.57, 4.59, 70329645], [4.59, 4.59, 4.49, 4.5, 50043115], [4.48, 4.55, 4.48, 4.52, 45574244], [4.49, 4.51, 4.44, 4.49, 41520349], [4.49, 4.56, 4.48, 4.49, 39248065], [4.44, 4.48, 4.38, 4.38, 47758456], [4.38, 4.39, 4.34, 4.38, 46646433], [4.38, 4.38, 4.32, 4.33, 33342005], [4.32, 4.37, 4.31, 4.34, 41741568], [4.31, 4.39, 4.3, 4.37, 54366151], [4.37, 4.46, 4.32, 4.39, 73168483], [4.3, 4.47, 4.28, 4.45, 90139385], [4.57, 4.72, 4.57, 4.66, 114429200], [4.58, 4.59, 4.46, 4.47, 59147206], [4.45, 4.55, 4.43, 4.52, 86250301], [4.51, 4.53, 4.41, 4.43, 65115917], [4.36, 4.51, 4.34, 4.44, 88369455], [4.41, 4.42, 4.33, 4.34, 49585544], [4.34, 4.4, 4.31, 4.38, 39017677], [4.32, 4.36, 4.23, 4.23, 44360974], [4.19, 4.24, 4.16, 4.19, 37759767], [4.23, 4.24, 4.18, 4.19, 42015976], [4.17, 4.25, 4.17, 4.23, 39811850], [4.24, 4.25, 4.22, 4.23, 26394353], [4.24, 4.33, 4.21, 4.3, 43493376], [4.31, 4.45, 4.31, 4.34, 68207103], [4.38, 4.43, 4.34, 4.4, 51172897], [4.36, 4.36, 4.17, 4.19, 64337395]],
        'index_names': ['datetime'], 'column_names': [None]
    }
    SPXS = pd.DataFrame.from_dict(data=SPXS_dict, orient="tight")
    SPXS.name = "SPXS"


    signal_dict = {
        'index': [Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00'), Timestamp('2025-08-13 04:00:00'), Timestamp('2025-08-14 04:00:00'), Timestamp('2025-08-15 04:00:00'), Timestamp('2025-08-18 04:00:00'), Timestamp('2025-08-19 04:00:00'), Timestamp('2025-08-20 04:00:00'), Timestamp('2025-08-21 04:00:00'), Timestamp('2025-08-22 04:00:00')],
        'columns': ['HYG', 'XLF', 'XLY', 'sum'],
        'data': [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [-1, 1, -1, -1], [-1, 1, -1, -1], [1, -1, 1, 1], [-1, -1, 1, -1], [-1, -1, -1, -3], [-1, -1, -1, -3], [1, -1, -1, -1], [1, -1, -1, -1], [1, 1, 1, 3], [1, 1, 1, 3], [1, -1, 1, 1], [-1, -1, 1, -1], [-1, 1, 1, 1], [1, 1, 1, 3], [1, 1, 1, 3], [1, 1, 1, 3], [-1, -1, 1, -1], [1, -1, 1, 1], [-1, 1, 1, 1], [-1, 1, -1, -1], [-1, 1, -1, -1], [1, 1, 1, 3], [1, 1, 1, 3]],
        'index_names': ['datetime'], 'column_names': [None]
    }
    SIGNAL = pd.DataFrame.from_dict(data=signal_dict, orient="tight")
    SIGNAL.name = "SIGNAL"

# =======

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100_000.00)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(TestStrategy)

    signal = bt.feeds.PandasData(dataname=SIGNAL, datetime=-1)
    # signal = PandasDataUSA(dataname=SIGNAL, datetime=-1)
    # cerebro.adddata(data=signal, name="SIGNAL")

    spxl = bt.feeds.PandasData(dataname=SPXL, datetime=-1)
    # spxl = PandasDataUSA(dataname=SPXL, datetime=-1)
    cerebro.adddata(data=spxl, name="SPXL")

    spxs = bt.feeds.PandasData(dataname=SPXS, datetime=-1)
    # spxs = PandasDataUSA(dataname=SPXS, datetime=-1)
    cerebro.adddata(data=spxs, name="SPXS")

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
