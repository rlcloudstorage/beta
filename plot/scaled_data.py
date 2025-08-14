"""use scikit-learn preprocessing to normalize data"""

import logging, logging.config
import sqlite3

import matplotlib as mpl
import matplotlib.pyplot as plt

# mpl.style.use('seaborn-v0_8-bright')
mpl.style.use("seaborn-v0_8-pastel")
import pandas as pd
import seaborn as sns

from sklearn.preprocessing import (
    MinMaxScaler,
    RobustScaler,
    StandardScaler,
)


DEBUG = True
table = "cwap"
# table = "volume"

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

ctx = {
    "database": "/home/la/dev/stomartat/temp/data/xyfinance.db",
    "table": table,
    "distribution": [
        "MinMaxScaler",
        "RobustScaler",
        "StandardScaler",
    ],
    "dataframe": None,
    "dataframe_cols": list(),
    "dataframe_dict": dict(),
}


def create_df_from_sqlite(ctx: dict) -> None:
    if DEBUG:
        logger.debug(
            f"create_df_from_sqlite(database={ctx['database']}, table={ctx['table']})"
        )

    db_con = sqlite3.connect(database=ctx["database"])
    df = pd.read_sql(f"SELECT * FROM {ctx['table']}", db_con, index_col="Date")
    df.index = pd.to_datetime(df.index, unit="s")
    ctx["dataframe"] = df
    ctx["dataframe_cols"] = df.columns


def create_scaled_dataframe_dict(ctx: dict) -> None:
    if DEBUG:
        logger.debug(f"create_scaled_dataframe_dict(ctx={ctx})")

    df = ctx["dataframe"]

    scaler = MinMaxScaler(feature_range=(0, 1))
    minmax_df = scaler.fit_transform(df)
    minmax_df += 10
    ctx["dataframe_dict"]["minmax_df"] = pd.DataFrame(minmax_df, columns=df.columns)

    scaler = RobustScaler(quantile_range=(0.0, 100.0))
    robust_df = scaler.fit_transform(df)
    robust_df += 10
    ctx["dataframe_dict"]["robust_df"] = pd.DataFrame(robust_df, columns=df.columns)

    scaler = StandardScaler()
    standard_df = scaler.fit_transform(df)
    standard_df += 10
    ctx["dataframe_dict"]["standard_df"] = pd.DataFrame(standard_df, columns=df.columns)


def plot_dataframes(ctx: dict) -> None:
    if DEBUG:
        logger.debug(f"plot_dataframes(ctx={ctx}")

    minmax_df = ctx["dataframe_dict"]["minmax_df"]
    robust_df = ctx["dataframe_dict"]["robust_df"]
    standard_df = ctx["dataframe_dict"]["standard_df"]

    fig, (minmax, robust, standard) = plt.subplots(ncols=3, nrows=1, figsize=(18, 10))

    minmax.set_title("MinmaxScaler")
    sns.kdeplot(minmax_df, ax=minmax)
    minmax.legend_.remove()

    robust.set_title("RobustScaler")
    sns.kdeplot(robust_df, ax=robust)
    robust.legend_.remove()

    standard.set_title("StandartScaler")
    sns.kdeplot(standard_df, ax=standard, legend=True, label=" ")
    standard.legend(loc="upper right")

    plt.legend(standard_df.columns, loc="upper right", title="stonk", fontsize=8)
    plt.savefig(f"{table}.png")


def main(ctx: dict) -> None:
    if DEBUG:
        logger.debug(f"main(ctx={ctx})")
    create_df_from_sqlite(ctx=ctx)
    create_scaled_dataframe_dict(ctx=ctx)
    plot_dataframes(ctx=ctx)


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - scale.py.main() *******")
    main(ctx=ctx)
