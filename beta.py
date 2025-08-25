""""""

import logging, logging.config

import utils_pd


# COLUMN = "cwap"
COLUMN = "sc_cwap"
OHLC = "tiingo_ohlc_sm.db"
SIGNAL = "tiingo_signal_sm.db"
DB_PATH = "/home/la/dev/rl/stonk_cli/work_dir/data/"
DEBUG = True
TABLE = "SPXL"
TABLE_LIST = ["HYG", "XLF", "XLY"]

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

ctx = {}


def main(ctx: dict) -> None:
    if DEBUG: logger.debug(f"main(ctx={ctx})")

    # df = utils_pd.create_df_from_database_table(db_path=DB_PATH + OHLC, table=TABLE)
    df = utils_pd.create_df_from_one_column_in_each_table(db_path=DB_PATH + SIGNAL, column=COLUMN)
    if DEBUG: logger.debug(f"{df.name} dataframe:\n{df}\n")
    df_dict = df.to_dict(orient="tight", index=True)
    if DEBUG: logger.debug(f"df_dict = {df_dict}")


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - filter/beta.py.main() *******")

    main(ctx=ctx)
