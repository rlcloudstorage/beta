""""""

import logging, logging.config

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.style.use("seaborn-v0_8-pastel")
import pandas as pd
import seaborn as sns

import pd_utils


DEBUG = True

logging.config.fileConfig(fname="../logger.ini")
logger = logging.getLogger(__name__)

ctx = {
    "database": "/home/la/dev/stomartat/temp/data/xdefault.db",
    "table": "data_line",
    "stonk_indicator": "cwap",
    # "stonk_indicator": "mass",
    "target_indicator": "cwap",
    # "scaler": "MinMax",
    "scaler": "Robust",
    "shift_period": 5
}

def small_timeseries(ctx: dict):
    """"""
    if ctx["scaler"].lower() == "minmax".lower():
        DB = "/home/la/dev/stomartat/temp/data/xminmax.db"
    elif ctx["scaler"].lower() == "robust".lower():
        DB = "/home/la/dev/stomartat/temp/data/xrobust.db"
    if DEBUG: logger.debug(f"database: {DB}")

    ctx["database"] = DB
    # df = utils_pd.create_df_from_sqlite_table_data(ctx=ctx)
    df = pd_utils.create_df_from_database_table()
    if DEBUG: logger.debug(f"dataframe\n{df} {type(df)}")

    # pivot_df = df.pivot(index='date', columns='ticker', values='cwap')
    # if DEBUG: logger.debug(f"pivot_df:\n{pivot_df} {type(pivot_df)}")

    sub_df = df.query(
        "ticker=='EURL' or ticker=='GDXU' or ticker=='TNA' or ticker=='YINN'"
    )#.shift(periods=3)
    sub_df = sub_df[["ticker", "cwap"]]#.reset_index()

    if DEBUG: logger.debug(f"sub_df:\n{sub_df} {type(sub_df)}")

    grid = sns.relplot(
        data=df,
        x="date",
        y=ctx["indicator"],
        col="ticker",
        hue="ticker",
        kind="line",
        palette="pastel",
        linewidth=1,
        # zorder=5,
        col_wrap=3,
        height=2,
        aspect=1.5,
        legend=False,
    )

    for ticker, ax in grid.axes_dict.items():
        ax.text(.08, .8, ticker, transform=ax.transAxes)
        sns.lineplot(
            data=sub_df,
            x="date", y=ctx["indicator"], units="ticker",
            estimator=None, color=".2", linewidth=.2, ax=ax
        )

    ax.set_xticks(ax.get_xticks()[::2])

    grid.set_titles("")
    grid.set_axis_labels("", "")
    grid.tight_layout()

    # plt.xticks(rotation=30, ha="right", fontsize=.8)
    plt.savefig(f"img/{ctx['indicator']}")
    plt.show()


def timeseries(ctx: dict):
    """"""
    # if ctx["scaler"].lower() == "minmax".lower():
    #     DB = "/home/la/dev/stomartat/temp/data/xminmax.db"
    # elif ctx["scaler"].lower() == "robust".lower():
    #     DB = "/home/la/dev/stomartat/temp/data/xrobust.db"
    # if DEBUG: logger.debug(f"database: {DB}")

    # ctx["database"] = DB

    # stonk_df = utils_pd.create_df_from_one_column_in_each_table(ctx=ctx, indicator=ctx["target_indicator"])
    stonk_df = pd_utils.create_df_from_one_column_in_every_table()
    stonk_df = stonk_df.shift(periods=ctx["shift_period"], freq=None)
    if DEBUG: logger.debug(f"stonk_df\n{stonk_df}\ncolumns: {stonk_df.columns}")

    # target_df = utils_pd.create_df_from_one_column_in_each_table(ctx=ctx, indicator=ctx["target_indicator"])
    target_df = pd_utils.create_df_from_one_column_in_every_table()
    target_df = target_df[["SPXL", "YINN"]]
    # target_df = target_df.shift(periods=ctx["shift_period"], freq=None)
    if DEBUG: logger.debug(f"target_df:\n{target_df} {type(target_df)}")

    for i, col in enumerate(stonk_df.columns):
        if DEBUG: logger.debug(f"i: {i}, col: {stonk_df[col].name} {type(stonk_df[col])}")

        if stonk_df[col].name in ["SPXL", "YINN"]:
            continue
        print(f"column name: {stonk_df[col].name} {type(stonk_df[col].name)}")

        s = pd.Series(stonk_df[col], name=stonk_df[col].name)
        if DEBUG: logger.debug(f"i: {i}, series: {s.name} {type(s)}")

        plot_df = pd.concat([s, target_df], axis=1)
        if DEBUG: logger.debug(f"plot_df: {type(plot_df)}")

        plt.figure(num=i, figsize=(8, 5))

        sns.set_context(context='paper')
        sns.lineplot(
            data=plot_df,
            palette=['black', 'deepskyblue', 'red'],
            # palette=['black', 'magenta', 'gold', 'deepskyblue', 'green', 'red'],
            # sizes=[1,1,1,1,10],
        ).set_title(
            f"{stonk_df[col].name} ({ctx['stonk_indicator']} {ctx['shift_period']}) vs. SPXL, YINN ({ctx['target_indicator']}) - {ctx['scaler']}Scaler"
        )

        # plt.show()
        plt.savefig(f"../img/timeseries/{stonk_df[col].name}_{ctx['stonk_indicator']}_{ctx['shift_period']}_{ctx['scaler'].lower()}")
        mpl.pyplot.close()


def main(ctx: dict) -> None:
    if DEBUG:
        logger.debug(f"main(ctx={ctx})")
        # small_timeseries(ctx=ctx)
        timeseries(ctx=ctx)


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - timeseries.py.main() *******")
    main(ctx=ctx)
