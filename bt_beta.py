""""""
import logging, logging.config

import backtrader as bt

from temp import data

BULL = data.SPXL
BEAR = data.SPXS
SIGNAL = data.signal
DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


class ApproximatePercentSizer(bt.Sizer):
    """based on percent of starting cash, shares are rounded to nearest 100"""
    params = (('percents', 40), )

    def _getsizing(self, comminfo, cash, data, isbuy):
        return int(round(self.broker.startingcash * self.params.percents / 100 / data[0], -2))


class LongShortIndicator(bt.Indicator):
    """"""
    lines = ("TS", )

    def __init__(self):
        # ts = self.data
        # ts = [i for i in self.datas]
        # self.lines.TS = ts
        self.lines.TS = self.data
        super(LongShortIndicator, self).__init__()


class TradeLongShort(bt.Strategy):
    """"""
    params = ()

    def __init__(self):
        self.ts_sig = None
        self.ts_sig = LongShortIndicator(self.datas[2].TS)
        # self.ts_sig = LongShortIndicator(self.datas[2])
        # self.ts_sig = LongShortIndicator(self.signal)
        if DEBUG:
            logger.debug(f"self.ts_sig: {[i for i in self.ts_sig.data]}")
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def log(self, txt, dt=None):
        """"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def next(self):
        """"""
        in_bull = self.getposition(self.datas[0])
        in_bear = self.getposition(self.datas[1])

        match bool(in_bear):
            case True:
                pass
            case False:
                pass
        match bool(in_bull):
            case True:
                pass
            case False:
                pass

        if in_bull or in_bear:
            self.log(txt=f"{in_bull.size} shares SPXL @ {in_bull.price:.2f}, {in_bear.size} shares SPXS @ {in_bear.price:.2f}")


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


if __name__ == "__main__":
    if DEBUG: logger.debug(f"******* bt_beta.py - START BACKTRADER *******")

    bull = bt.feeds.PandasData(dataname=BULL, datetime=-1, name="bull")
    bear = bt.feeds.PandasData(dataname=BEAR, datetime=-1, name="bear")
    signal = PandasSignalData(dataname=SIGNAL, datetime=-1)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100_000.00)
    cerebro.adddata(data=bull, )
    cerebro.adddata(data=bear, )
    cerebro.adddata(data=signal, name="signal")
    cerebro.addsizer(ApproximatePercentSizer, percents=40)
    cerebro.addstrategy(TradeLongShort)

    if DEBUG: [logger.debug(f"cerebro.datas: {cerebro.datas[i]}, {d._name} data:\n{d._dataname}\n")  for i, d in enumerate(cerebro.datas)]

    print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")
    cerebro.run()
    print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")
