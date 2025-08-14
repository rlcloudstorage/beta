""""""
import logging, logging.config
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.signal import savgol_filter


DEBUG = True

logging.config.fileConfig(fname='../logger.ini')
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ctx = {
    "database": "/home/la/dev/beta/data/default.db",
    # "database": "/home/la/dev/stomartat/temp/data/xdefault.db",
    "dataframe": None,
    # "table": "data_line",
    "indicator": "cwap",
    "window_length_list": [21, 63],
    "poly_order_list": [2,],
    "slope_param": [21, 63],
    "target": ["SPXL", "SPXS", "YINN", "YANG"],
    "china": ["ECNS", "FXI"],
    "usa": ["HYG", "XLF", "XLY"]

}


def create_df_from_one_column_in_each_table(ctx: dict, indicator: str) -> pd.DataFrame:
    """Select data from the named column out of each table in the sqlite database"""
    if DEBUG:
        logger.debug(f"create_df_from_sqlite_table_data(ctx={type(ctx)}, indicator={indicator})")

    db_con = sqlite3.connect(database=ctx["database"])

    # get a numpy ndarray of table names
    db_table_array = pd.read_sql(
        f"SELECT name FROM sqlite_schema WHERE type='table' AND name NOT like 'sqlite%'", db_con,
    ).name.values

    index_array = pd.read_sql(  # get a numpy ndarray of Date index
        f"SELECT date FROM {db_table_array[0]}", db_con
    ).date.values

    df = pd.DataFrame(index=index_array)

    for table in db_table_array:
        if table not in (ctx["target"] + ctx["china"]):
            df[table] = pd.read_sql(
                f"SELECT date, {indicator} FROM {table}", db_con, index_col="date"
            )
    df.index = pd.to_datetime(df.index, unit="s")
    # df.index = pd.to_datetime(df.index, unit="s").date
    df.index.names = ['date']

    return df


def create_sav_gol_deriv_dataframe(ctx: dict, deriv:int)->pd.DataFrame:
    """"""
    if DEBUG:
        logger.debug(f"create_sav_gol_derivati_dataframe(ctx={type(ctx)})")

    # create empty dataframe with index as a timestamp
    df = pd.DataFrame(index=ctx["dataframe"].index.values)
    df.index.name = "date"

    # insert values for each ticker into df
    for col in ctx["dataframe"].columns:
        # if col in ['ECNS', 'FXI', 'SPXL', 'SPXS', 'YINN']:
        #     continue
        df[col] = savgol_filter(
            x=ctx["dataframe"][col].values,
            window_length=ctx["window_length_list"][0],
            polyorder=ctx["poly_order_list"][0],
            deriv=deriv
        )
    return df


def create_stonk_dataframe(ctx: dict)->None:
    """"""
    if DEBUG: logger.debug(f"create_stonk_dataframe(ctx={type(ctx)})")

    # create empty dataframe with index as a timestamp
    df = pd.DataFrame(index=ctx["dataframe"].index.values)
    df.index.name = "date"

    # insert values for each ticker into df
    for col in ctx["dataframe"].columns:
        if col not in ['SPXL', 'SPXS',]:
            continue
        df[col] = ctx["dataframe"][col].values

    if DEBUG: logger.debug(f"stonk_df:\n{df} {type(df)}")
    df.to_pickle("../data/stonk_df.pkl")
    return df


def plot_alternate_filter_params(ctx: dict)->None:
    """"""
    if DEBUG:
        logger.debug(f"plot_alternate_filter_params(ctx={type(ctx)})")

    for col in ctx["dataframe"].columns:
        fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(12.5, 7))
        plt.xlabel("Date")
        plt.ylabel("Value")

        series_raw = pd.Series(data=ctx["dataframe"][col], name=ctx["dataframe"][col].name)
        if DEBUG: logger.debug(f"{col} series_raw {type(series_raw)}")

        for i, poly_order in enumerate(ctx["poly_order_list"]):
            for j, window_length in enumerate(ctx["window_length_list"]):
                series_smoothed = savgol_filter(
                    x=series_raw, window_length=window_length, polyorder=poly_order, deriv=0
                )
                axs[i, j].plot(series_raw.index, series_raw, label=f"raw {ctx['indicator']} data")
                axs[i, j].plot(series_raw.index, series_smoothed, label="filtered data")
                axs[i, j].legend()
                axs[i, j].set_title(
                    f"{series_raw.name} window_length: {window_length},  poly_order: {poly_order}"
                )
            for j, window_length in enumerate(ctx["window_length_list"]):
                series_slope = savgol_filter(
                    x=series_raw, window_length=window_length, polyorder=poly_order, deriv=1
                )
                axs[i+1, j].plot(series_raw.index, series_slope, label=f"derivitave 1")
                axs[i+1, j].legend()
                axs[i+1, j].set_title(
                    f"{series_raw.name} window_length: {window_length},  poly_order: {poly_order}"
                )
        plt.tight_layout()
        plt.savefig(f"../img/filter/{series_raw.name}_{ctx['indicator']}")
        plt.close()


def zero_crossing_dataframe(ctx: dict):
    if DEBUG: logger.debug(f"zero_crossing_dataframe(ctx={type(ctx)}")

    slope_df = create_sav_gol_deriv_dataframe(ctx=ctx, deriv=1)

    # create empty dataframe with index as a timestamp
    signal_df = pd.DataFrame(index=slope_df.index.values)
    signal_df.index.name = "date"

    for col in slope_df.columns:
        data = slope_df[col].values
        zero_list = list()

        for i, cur_item in enumerate(data):
            prev_item = data[i - 1]
            if i == 0:
                # reset starting value
                zero_list.append(0)
                continue
            elif cur_item > 0 and prev_item < 0:
                # derivative crosses zero to upside
                zero_list.append(1)
            elif cur_item < 0 and prev_item > 0:
                # derivative crosses zero to downside
                zero_list.append(-1)
            else:
                # no crossing maintain status
                zero_list.append(zero_list[i - 1])

        signal_df[f"{col}x"] = zero_list

    signal_df["signal"] = signal_df.sum(axis=1, numeric_only=True)

    if DEBUG: logger.debug(f"signal_df:\n{signal_df}")
    signal_df.to_pickle("../data/signal_df.pkl")
    return signal_df


def main(ctx: dict) -> None:
    if DEBUG: logger.debug(f"main(ctx={ctx})")

    df = create_df_from_one_column_in_each_table(ctx=ctx, indicator="cwap")
    if DEBUG: logger.debug(f"dataframe:\n{df} {type(df)}")
    ctx["dataframe"] = df
    # plot_alternate_filter_params(ctx=ctx)
    # create_sav_gol_deriv_dataframe(ctx=ctx, deriv=1)
    # create_stonk_dataframe(ctx=ctx)
    zero_crossing_dataframe(ctx=ctx)


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - filter/beta.py.main() *******")

    main(ctx=ctx)
