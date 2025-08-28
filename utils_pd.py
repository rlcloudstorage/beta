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
        f"SELECT datetime FROM {db_table_array[0]}", db_con
    ).datetime.values
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
            f"SELECT datetime, {column} FROM {table}", db_con, index_col="datetime"
        )
    df.index = pd.to_datetime(df.index, unit="s")
    df.index.names = ['datetime']

    return df


def create_df_from_database_table(db_path: str, table: str) -> pd.DataFrame:
    """"""
    if DEBUG:
        logger.debug(f"create_df_from_database_table(db_path={db_path}, table={table})")

    db_con = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table}", db_con, index_col="datetime")
    df.name = table
    df.index = pd.to_datetime(df.index, unit="s")
    df.index.names = ['datetime']

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

            cls.data_line_list = ["cwap", "sc_cwap"]
            cls.ohlc_list = ["SPXL", "SPXS"]
            cls.signal_list = ["HYG", "SPXL", "SPXS", "XLF", "XLY"]

            with sqlite3.connect("file:ohlc.db?mode=memory&cache=shared", uri=True) as cls.con1:

                for table in cls.ohlc_list:
                    cls.con1.execute(
                        f"""
                        CREATE TABLE {table} (
                            datetime      INTEGER    NOT NULL,
                            open          INTEGER,
                            high          INTEGER,
                            low           INTEGER,
                            close         INTEGER,
                            volume        INTEGER,
                            PRIMARY KEY (datetime)
                            )"""
                    )

                cls.con1.executescript(
                    """
                    INSERT INTO SPXL (datetime, open, high, low, close, volume) VALUES (1754625600, 184.76, 187.88, 184.53, 187.4, 1965573);
                    INSERT INTO SPXL (datetime, open, high, low, close, volume) VALUES (1754884800, 187.66, 188.99, 185.24, 186.29, 5326281);
                    INSERT INTO SPXL (datetime, open, high, low, close, volume) VALUES (1754971200, 188.34, 192.38, 187.05, 192.15, 7148865);

                    INSERT INTO SPXS (datetime, open, high, low, close, volume) VALUES (1754625600, 4.41, 4.42, 4.33, 4.34, 49585544);
                    INSERT INTO SPXS (datetime, open, high, low, close, volume) VALUES (1754884800, 4.34, 4.4, 4.31, 4.38, 39017677);
                    INSERT INTO SPXS (datetime, open, high, low, close, volume) VALUES (1754971200, 4.32, 4.36, 4.23, 4.23, 44360974);
                    """
                )
                cls.ohlc_table_array = pd.read_sql(
                    f"SELECT name FROM sqlite_schema WHERE type='table' AND name NOT like 'sqlite%'", cls.con1,
                ).name.values

            with sqlite3.connect("file:signal.db?mode=memory&cache=shared", uri=True) as cls.con2:

                for table in cls.signal_list:
                    cls.con2.execute(
                        f"""
                        CREATE TABLE {table} (
                            datetime    INTEGER    NOT NULL,
                            cwap        INTEGER,
                            sc_cwap     INTEGER,
                            PRIMARY KEY (datetime)
                        )"""
                    )
                cls.con2.executescript(
                    """
                    INSERT INTO HYG (datetime, cwap, sc_cwap) VALUES (1754625600, 8021, 919);
                    INSERT INTO HYG (datetime, cwap, sc_cwap) VALUES (1754884800, 8022, 1000);
                    INSERT INTO HYG (datetime, cwap, sc_cwap) VALUES (1754971200, 8035, 1185);

                    INSERT INTO SPXL (datetime, cwap, sc_cwap) VALUES (1754625600, 18680, 1158);
                    INSERT INTO SPXL (datetime, cwap, sc_cwap) VALUES (1754884800, 18670, 1000);
                    INSERT INTO SPXL (datetime, cwap, sc_cwap) VALUES (1754971200, 19093, 1195);

                    INSERT INTO SPXS (datetime, cwap, sc_cwap) VALUES (1754625600, 436, 844);
                    INSERT INTO SPXS (datetime, cwap, sc_cwap) VALUES (1754884800, 437, 1000);
                    INSERT INTO SPXS (datetime, cwap, sc_cwap) VALUES (1754971200, 426, 818);

                    INSERT INTO XLF (datetime, cwap, sc_cwap) VALUES (1754625600, 5179, 1000);
                    INSERT INTO XLF (datetime, cwap, sc_cwap) VALUES (1754884800, 5185, 1040);
                    INSERT INTO XLF (datetime, cwap, sc_cwap) VALUES (1754971200, 5238, 1179);

                    INSERT INTO XLY (datetime, cwap, sc_cwap) VALUES (1754625600, 22396, 1082);
                    INSERT INTO XLY (datetime, cwap, sc_cwap) VALUES (1754884800, 22455, 1096);
                    INSERT INTO XLY (datetime, cwap, sc_cwap) VALUES (1754971200, 22623, 1148);
                    """
                )
                cls.signal_table_array = pd.read_sql(
                    f"SELECT name FROM sqlite_schema WHERE type='table' AND name NOT like 'sqlite%'", cls.con2,
                ).name.values

        @unittest.skip
        def test_ohlc_database_exists(self):
            self.assertListEqual(list(self.ohlc_table_array), self.ohlc_list)
            for table in self.ohlc_list:
                try:
                    cursor = sqlite3.connect("file:ohlc.db?mode=memory&cache=shared").cursor()
                    cursor.execute(f"""SELECT * FROM {table}""")
                    print(f"\n{table}")
                    data = cursor.fetchall()
                    [print(row) for row in data]
                except sqlite3.Error as e:
                    print(f"*** ERROR *** {e}")
                finally:
                    cursor.close()

        @unittest.skip
        def test_signal_database_exists(self):
            self.assertListEqual(list(self.signal_table_array), self.signal_list)
            for table in self.signal_list:
                try:
                    cursor = sqlite3.connect("file:signal.db?mode=memory&cache=shared").cursor()
                    cursor.execute(f"""SELECT * FROM {table}""")
                    print(f"\n{table}")
                    data = cursor.fetchall()
                    [print(row) for row in data]
                except sqlite3.Error as e:
                    print(f"*** ERROR *** {e}")
                finally:
                    cursor.close()

        # @unittest.skip
        def test_create_df_from_ohlc_database_table(self):
            for table in self.ohlc_list:
                df = create_df_from_database_table(
                    db_path="file:ohlc.db?mode=memory&cache=shared", table=table
                )
                if DEBUG: logger.debug(
                    f"Dataframe {df.name}:\n{df}\ntype(df.index[0]): {type(df.index[0])}"
                )

        # @unittest.skip
        def test_create_df_from_one_column_in_each_table(self):
            print(f"self.data_line_list: {self.data_line_list}")
            for col in self.data_line_list:  # use default table_list
                print(f"col: {col}")
                df = create_df_from_one_column_in_each_table(
                    db_path="file:signal.db?mode=memory&cache=shared", column=col
                )
                if DEBUG: logger.debug(
                    f"Dataframe {df.name}:\n{df}\ntype(df.index[0]): {type(df.index[0])}\n"
                )
            # for col in self.data_line_list:  # use provided table_list
            #     df = create_df_from_one_column_in_each_table(
            #         db_path="file:signal.db?mode=memory&cache=shared", column=col, table_list=["SPXL", "SPXS"]
            #     )
            #     if DEBUG: logger.debug(
            #         f"Dataframe {df.name}:\n{df}\ntype(df.index[0]): {type(df.index[0])}\n"
            #     )
            # for col in self.data_line_list:  # use table_list with mistakes
            #     df = create_df_from_one_column_in_each_table(
            #         db_path="file:signal.db?mode=memory&cache=shared", column=col, table_list=["YINN", "XXX"]
            #     )
            #     if DEBUG: logger.debug(f"Dataframe {df.name}:\n{df}\n")

        @classmethod
        def tearDownClass(cls):
            print(f"\n-tearDown({cls})")

    unittest.main()
