""""""
import logging, logging.config

import backtrader as bt

import utils_pd, utils_sig
from temp import data


logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

DEBUG = True

ctx = {
    "COLUMN": ["cwap", "sc_cwap"],
    "OHLC_DB": "tiingo_ohlc_sm.db",
    "SIGNAL_DB": "tiingo_signal_sm.db",
    "DB_PATH": "/home/la/dev/rl/stonk_cli/work_dir/data/",
    "OHLC_TABLE": ["SPXL", "SPXS"],
    "SIGNAL_TABLE": ["HYG", "XLF", "XLY"],
}


def get_df_dict(ctx: dict) -> None:
    if DEBUG: logger.debug(f"main(ctx={ctx})")

    for table in ctx["OHLC_TABLE"]:
        df = utils_pd.create_df_from_database_table(db_path=ctx["DB_PATH"] + ctx["OHLC_DB"], table=table)
        if DEBUG: logger.debug(f"{df.name} dataframe:\n{df}\n")
        df_dict = df.to_dict(orient="tight", index=True)
        if DEBUG: logger.debug(f"{table}_dict = {df_dict}")

    for table in ctx["SIGNAL_TABLE"]:
        for column in ctx["COLUMN"]:
            df = utils_pd.create_df_from_one_column_in_each_table(db_path=ctx["DB_PATH"] + ctx["SIGNAL_DB"], column=column)
            if DEBUG: logger.debug(f"{df.name} dataframe:\n{df}\n")
            df_dict = df.to_dict(orient="tight", index=True)
            if DEBUG: logger.debug(f"{table}_dict = {df_dict}")

    usa_cwap = utils_pd.create_df_from_one_column_in_each_table(db_path=ctx["DB_PATH"] + ctx["SIGNAL_DB"], column="cwap", table_list=["HYG", "XLF", "XLY"])
    signal_df = utils_sig.savgol_filter_slope_change_signal(dataframe=usa_cwap, win_length=3)
    if DEBUG: logger.debug(f"signal_df:\n{signal_df}\n")
    signal_dict = signal_df.to_dict(orient="tight", index=True)
    if DEBUG: logger.debug(f"signal_dict = {signal_dict}")


def main() -> None:
    if DEBUG: logger.debug(f"main()")



class AboutTwentyPercentSizer(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        return self.params.stake


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - beta/beta.py.main() *******")

    SPXS = bt.feeds.PandasData(dataname=data.SPXS, datetime=-1, name="SPXS")

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100_000.00)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.adddata(data=SPXS, )
    cerebro.addsizer(AboutTwentyPercentSizer)

    my_sizer = AboutTwentyPercentSizer()
    print(f"my_sizer.stake: {my_sizer.params.stake}")

    print(f"Starting Value: {cerebro.broker.getvalue():,.2f}")
    cerebro.run()
    print(f"Ending Value:   {cerebro.broker.getvalue():,.2f}")
