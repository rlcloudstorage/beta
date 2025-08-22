"""pandas utilities"""
import logging, logging.config
import sqlite3

import numpy as np
import pandas as pd

# DEBUG = False
DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


def create_df_from_one_column_in_each_table(db_path: str, column: str, table_list: list=[]) -> pd.DataFrame:
    """Select data from the named column out of each table in the sqlite database"""
    if DEBUG:
        logger.debug(f"create_df_from_one_column_in_each_table(db_path={db_path}, column={column}, table_list={table_list})")

    db_con = sqlite3.connect(db_path)

    # get a numpy ndarray of table names
    db_table_array = pd.read_sql(
        f"SELECT name FROM sqlite_schema WHERE type='table' AND name NOT like 'sqlite%'", db_con,
    ).name.values

    # get a numpy ndarray of Date index
    index_array = pd.read_sql(
        f"SELECT date FROM {db_table_array[0]}", db_con
    ).date.values
    # ).values

    df = pd.DataFrame(index=index_array)
    df.name = column

    # if table_list is empty, use db_table_array
    table_list = db_table_array if not table_list else table_list

    # remove unwanted tables from db_table_array
    del_list = list()
    for i, table in enumerate(db_table_array):
        if table not in table_list:
            del_list.append(i)
    db_table_array = np.delete(arr=db_table_array, obj=del_list)

    for table in db_table_array:
        df[table] = pd.read_sql(
            f"SELECT date, {column} FROM {table}", db_con, index_col="date"
        )
    df.index = pd.to_datetime(df.index, unit="s")#.date
    df.index.names = ['datetime']

    return df


def create_df_from_database_table(db_path: str, table: str) -> pd.DataFrame:
    """"""
    if DEBUG:
        logger.debug(f"create_df_from_database_table(db_path={db_path}, table={table})")

    db_con = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table}", db_con, index_col="date")
    df.name = table
    df.index = pd.to_datetime(df.index, unit="s").date
    df.index.names = ['date']

    return df


if __name__ == "__main__":
    import unittest

    if DEBUG:
        logger.debug(f"******* START - pd_utils.py *******")


    class TestDataframeUtilityFunctions(unittest.TestCase):
        """"""
        @classmethod
        def setUpClass(cls):
            print(f" setUp({cls})")

            cls.data_list = ["cwap", "sc_cwap"]
            cls.table_list = ["HYG", "SPXL", "SPXS", "XLF", "XLY"]

            with sqlite3.connect("file:temp.db?mode=memory&cache=shared", uri=True) as cls.con:

                for table in cls.table_list:
                    cls.con.execute(
                        f"""
                        CREATE TABLE {table} (
                            date    INTEGER    NOT NULL,
                            cwap    INTEGER,
                            sc_cwap INTEGER,
                            PRIMARY KEY (date)
                        )"""
                    )
                cls.con.executescript(
                    """

                    INSERT INTO HYG (date, cwap, sc_cwap) VALUES (1754625600, 8021, 919);
                    INSERT INTO HYG (date, cwap, sc_cwap) VALUES (1754884800, 8022, 1000);
                    INSERT INTO HYG (date, cwap, sc_cwap) VALUES (1754971200, 8035, 1185);

                    INSERT INTO SPXL (date, cwap, sc_cwap) VALUES (1754625600, 18680, 1158);
                    INSERT INTO SPXL (date, cwap, sc_cwap) VALUES (1754884800, 18670, 1000);
                    INSERT INTO SPXL (date, cwap, sc_cwap) VALUES (1754971200, 19093, 1195);

                    INSERT INTO SPXS (date, cwap, sc_cwap) VALUES (1754625600, 436, 844);
                    INSERT INTO SPXS (date, cwap, sc_cwap) VALUES (1754884800, 437, 1000);
                    INSERT INTO SPXS (date, cwap, sc_cwap) VALUES (1754971200, 426, 818);

                    INSERT INTO XLF (date, cwap, sc_cwap) VALUES (1754625600, 5179, 1000);
                    INSERT INTO XLF (date, cwap, sc_cwap) VALUES (1754884800, 5185, 1040);
                    INSERT INTO XLF (date, cwap, sc_cwap) VALUES (1754971200, 5238, 1179);

                    INSERT INTO XLY (date, cwap, sc_cwap) VALUES (1754625600, 22396, 1082);
                    INSERT INTO XLY (date, cwap, sc_cwap) VALUES (1754884800, 22455, 1096);
                    INSERT INTO XLY (date, cwap, sc_cwap) VALUES (1754971200, 22623, 1148);
                    """
                )
                cls.db_table_array = pd.read_sql(
                    f"SELECT name FROM sqlite_schema WHERE type='table' AND name NOT like 'sqlite%'", cls.con,
                ).name.values

        @unittest.skip
        def test_database_exists(self):
            self.assertListEqual(list(self.db_table_array), self.table_list)

        @unittest.skip
        def test_create_df_from_database_table(self):
            for table in self.table_list:
                df = create_df_from_database_table(
                    db_path="file:temp.db?mode=memory&cache=shared", table=table
                )
                if DEBUG: logger.debug(f"Dataframe {df.name}:\n{df}\n")

        # @unittest.skip
        def test_create_df_from_one_column_in_each_table(self):
            for col in self.data_list:  # use default table_list
                df = create_df_from_one_column_in_each_table(
                    db_path="file:temp.db?mode=memory&cache=shared", column=col
                )
                if DEBUG: logger.debug(
                    f"Dataframe {df.name}:\n{df}\ntype(df.index[0]): {type(df.index[0])}\n"
                )
            for col in self.data_list:  # use provided table_list
                df = create_df_from_one_column_in_each_table(
                    db_path="file:temp.db?mode=memory&cache=shared", column=col, table_list=["SPXL", "SPXS"]
                )
                if DEBUG: logger.debug(
                    f"Dataframe {df.name}:\n{df}\ntype(df.index[0]): {type(df.index[0])}\n"
                )
            # for col in self.data_list:  # use table_list with mistakes
            #     df = create_df_from_one_column_in_each_table(
            #         db_path="file:temp.db?mode=memory&cache=shared", column=col, table_list=["YINN", "XXX"]
            #     )
            #     if DEBUG: logger.debug(f"Dataframe {df.name}:\n{df}\n")

        @classmethod
        def tearDownClass(cls):
            print(f"\n-tearDown({cls})")

    unittest.main()
