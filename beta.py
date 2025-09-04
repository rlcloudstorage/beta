""""""
import logging, logging.config

import pandas as pd

import utils_pd, utils_sig
from temp import data


logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

DEBUG = True

ctx = {
    "COLUMN": ["clop", "clv", "cwap", "hilo", "volume"],
    "OHLC_DB": "tiingo_ohlc_sm.db",
    "SIGNAL_DB": "tiingo_signal_sm.db",
    "DB_PATH": "/home/la/dev/rl/stonk_cli/work_dir/data/",
    "OHLC_TABLE": ["SPXL", "SPXS"],
    "SIGNAL_TABLE": ["HYG", "XLF", "XLY"],
}


def get_df_dict(ctx: dict) -> None:
    if DEBUG: logger.debug(f"get_df_dict(ctx={ctx})")

    for table in ctx["OHLC_TABLE"]:
        df = utils_pd.create_df_from_database_table(db_path=ctx["DB_PATH"] + ctx["OHLC_DB"], table=table)
        if DEBUG: logger.debug(f"{df.name} dataframe:\n{df}\n")
        df_dict = df.to_dict(orient="tight", index=True)
        if DEBUG: logger.debug(f"{table}_dict = {df_dict}")

    # for table in ctx["SIGNAL_TABLE"]:
    for column in ctx["COLUMN"]:
        df = utils_pd.create_df_from_one_column_in_each_table(db_path=ctx["DB_PATH"] + ctx["SIGNAL_DB"], column=column)
        if DEBUG: logger.debug(f"{df.name} dataframe:\n{df}\n")
        df_dict = df.to_dict(orient="tight", index=True)
        if DEBUG: logger.debug(f"{column}_dict = {df_dict}")

    usa_cwap = utils_pd.create_df_from_one_column_in_each_table(db_path=ctx["DB_PATH"] + ctx["SIGNAL_DB"], column="cwap", table_list=["HYG", "XLF", "XLY"])
    signal_df = utils_sig.savgol_filter_slope_change_signal(dataframe=usa_cwap, win_length=3)
    if DEBUG: logger.debug(f"signal_df:\n{signal_df}\n")
    signal_dict = signal_df.to_dict(orient="tight", index=True)
    if DEBUG: logger.debug(f"signal_dict = {signal_dict}")


def add_line_to_ohlc_df(line_s: pd.Series, ohlc_df: pd.DataFrame, name: str) -> pd.DataFrame:
    """add_line_to_ohlc_df(line_s=pd.Series(signal["sum"]), ohlc_df=spxl, name="TS")"""
    if DEBUG:
        logger.debug(f"add_line_to_ohlc_df(line_s={type(line_s)}, ohlc_df={type(ohlc_df)}, name={name})")

    ohlc_df[name] = line_s
    return ohlc_df


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - beta/beta.py.main() *******")

    SPXL_sig_df = add_line_to_ohlc_df(ohlc_df=data.SPXL, line_s=data.signal[["TS"]], name="TS")
    SPXL_sig_dict = SPXL_sig_df.to_dict(orient="tight", index=True)
    if DEBUG: logger.debug(f"SPXL_sig_dict = {SPXL_sig_dict}")
