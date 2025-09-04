""""""
import logging, logging.config

import backtrader as bt

from temp import data

BULL = data.SPXL
BEAR = data.SPXS
SIGNAL = data.signal
DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
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
        self.lines.TS = self.data
        super(LongShortIndicator, self).__init__()


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
    params = ()

    def __init__(self):
        self.buyprice = None
        self.buycomm = None
        self.order = None
        self.ts_sig = None
        self.ts_sig = LongShortIndicator(self.datas[2].TS)
        if DEBUG:
            logger.debug(f"self.ts_sig: {[i for i in self.ts_sig.data]}")

    def log(self, txt, dt=None):
        """"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def next(self):
        """"""
        in_bull = self.getposition(self.datas[0])
        in_bear = self.getposition(self.datas[1])

        # check bear (short) position
        match bool(in_bear):
            case True:  # already short
                if self.ts_sig > 0:  # take profit
                    self.log(txt=f"CREATE SELL bear @ {self.datas[1][0]:,.2f}")
                elif self.ts_sig <= 0:  # hold
                    pass
            case False:  # might short
                if self.ts_sig >= 0:  # not yet
                    pass
                elif self.ts_sig < 0:  # short now
                    self.log(txt=f"CREATE BUY bear @ {self.datas[1][0]:,.2f}")

        # check bull (long) position
        match bool(in_bull):
            case True:  # already long
                if self.ts_sig <= 0:  # take profit
                    self.log(txt=f"CREATE SELL bull @ {self.datas[0][0]:,.2f}")
                elif self.ts_sig > 0:  # hold
                    pass
            case False:  # might long
                if self.ts_sig <= 0:  # not yet
                    pass
                elif self.ts_sig > 0:  # long now
                    self.log(txt=f"CREATE BUY bull @ {self.datas[0][0]:,.2f}")

        if in_bull or in_bear:
            self.log(txt=f"{in_bull.size} shares bull @ {in_bull.price:.2f}, {in_bear.size} shares bear @ {in_bear.price:.2f}")


if __name__ == "__main__":
    if DEBUG: logger.debug(f"******* bt_beta.py - START BACKTRADER *******")

    bull = bt.feeds.PandasData(dataname=BULL, datetime=-1)
    bear = bt.feeds.PandasData(dataname=BEAR, datetime=-1)
    signal = PandasSignalData(dataname=SIGNAL, datetime=-1)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100_000.00)
    cerebro.adddata(data=bull,  name="bull")
    cerebro.adddata(data=bear, name="bear")
    cerebro.adddata(data=signal, name="signal")
    cerebro.addsizer(ApproximatePercentSizer, percents=40)
    cerebro.addstrategy(TradeLongShort)

    if DEBUG: [logger.debug(f"cerebro.datas: {cerebro.datas[i]}, {d._name} data:\n{d._dataname}\n")  for i, d in enumerate(cerebro.datas)]

    print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")
    cerebro.run()
    print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")

    # cerebro.plot()
