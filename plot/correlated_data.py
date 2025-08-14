""""""

import logging, logging.config
# import sqlite3

# import matplotlib as mpl
import matplotlib.pyplot as plt

# # mpl.style.use('seaborn-v0_8-bright')
# mpl.style.use("seaborn-v0_8-pastel")
import numpy as np
# import pandas as pd
import seaborn as sns

import pd_utils


DEBUG = True

logging.config.fileConfig(fname="../logger.ini")
logger = logging.getLogger(__name__)

ctx = {
    "database": None,
    "table": "data_line",
    "stonk_indicator": "cwap",
    # "stonk_indicator": "mass",
    "target_indicator": "cwap",
    # "scaler": "MinMax",
    "scaler": "Robust",
    "shift_period": 3
}

def main(ctx: dict) -> None:
    if DEBUG:
        logger.debug(f"main(ctx={ctx})")

    if ctx["scaler"].lower() == "minmax".lower():
        DB = "/home/la/dev/stomartat/temp/data/xminmax.db"
    elif ctx["scaler"].lower() == "robust".lower():
        DB = "/home/la/dev/stomartat/temp/data/xrobust.db"
    if DEBUG: logger.debug(f"database: {DB}")

    ctx["database"] = DB

    stonk_df = utils_pd.create_df_from_one_column_in_each_table(ctx=ctx, indicator=ctx["stonk_indicator"])
    if DEBUG: logger.debug(f"stonk_df\n{type(stonk_df)}\ncolumns: {stonk_df.columns}")

    # df_mask = (stonk_df.columns.isin(["EURL", "GDXU", "SPXL", "TNA", "YINN"]))
    df_mask = ~(stonk_df.columns.isin(["EURL", "GDXU", "SPXL", "TNA", "YINN"]))
    shift_cols = stonk_df.columns[df_mask]
    stonk_df[shift_cols] = stonk_df[shift_cols].shift(periods=ctx["shift_period"], freq=None)

    if DEBUG: logger.debug(f"shifted_df\n{stonk_df}\ncolumns: {stonk_df.columns}")

    corr = stonk_df.corr(method='kendall')
    corr = (corr * 100).round().astype(int)
    if DEBUG: logger.debug(f"correlation: {type(corr)}")

    plt_mask = np.triu(np.ones_like(corr, dtype=bool))

    plt.figure(figsize=(11, 8.5))
    # plt.figure(figsize=(16, 9))

    sns.color_palette('pastel')
    sns.set_context('paper')
    sns.heatmap(
        data=corr, mask=plt_mask, annot=True,
        vmin=-100, vmax=100, center=0,
        square=True, linewidths=.5,
        cbar_kws={"shrink": .2}
    ).set_title(
        f"{ctx['stonk_indicator']}/{ctx['target_indicator']} {ctx['shift_period']} period - {ctx['scaler']}Scaler"
    )

    # plt.show()
    plt.savefig(f"../img/hm/{ctx['stonk_indicator']}_{ctx['target_indicator']}_{ctx['scaler'].lower()}_{ctx['shift_period']}")
    plt.close()


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - df_correlate.py.main() *******")
    main(ctx=ctx)
