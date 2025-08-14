""""""
import logging, logging.config
import sqlite3

import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA


DEBUG = True

logging.config.fileConfig(fname='../logger.ini')
logger = logging.getLogger(__name__)

ctx = {
    "database": "../data/default.db",
    "data_line": ['CWAP',],
    "signal_df": pd.read_pickle("../data/signal_df.pkl"),
    "stonk_df": pd.read_pickle("../data/stonk_df.pkl"),
}

signal_df = ctx["signal_df"]

stonk_df = ctx["stonk_df"]
stonk_df["signal"] = signal_df["signal"]


def create_stonk_dataframe(ctx: dict, stonk:str)->pd.DataFrame:
    """"""
    if DEBUG: logger.debug(f"create_stonk_dataframe(ctx={type(ctx)}")

    con = sqlite3.connect(database=ctx["database"])
    df = pd.read_sql_query(sql=f"SELECT * FROM {stonk}", con=con, index_col='date')
    con.close()

    df = df.drop(columns=[item.lower() for item in ctx["data_line"]])
    df.index = pd.to_datetime(df.index, unit='s')
    df.to_pickle("../data/stonk_df.pkl")

    return stonk, df


class SignalStrategy(Strategy):
    """"""
    def init(self):
        pass

    def next(self):
        current_signal = self.data.signal[-1]
        if current_signal >= 1:
            if not self.position:
                self.buy()
        elif current_signal <= 0:
            if self.position:
                self.position.close()


def main(ctx: dict) -> None:
    if DEBUG: logger.debug(f"main(ctx={type(ctx)})")

    # stonk, stonk_df = create_stonk_dataframe(ctx=ctx, stonk="SPXL")
    # if DEBUG: logger.debug(f"stonk_df:\n{stonk_df} {type(stonk_df.index)}")

    bt = Backtest(data=stonk_df, strategy=SignalStrategy, cash=1_000_000, commission=.002, exclusive_orders=True)
    stats = bt.run()
    if DEBUG: logger.debug(f"stats:\n{stats}")
    bt.plot()


if __name__ == "__main__":
    if DEBUG: logger.debug(f"******* START - backtest/backtesting_.py.main() *******")

    main(ctx=ctx)
