"""pandas utilities"""
import logging, logging.config
import sqlite3

import pandas as pd

# DEBUG = False
DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


def create_df_from_one_column_in_every_table(db_path: str, column: str) -> pd.DataFrame:
    """Select data from the named column out of each table in the sqlite database"""
    if DEBUG:
        logger.debug(f"create_df_from_one_column_in_every_table(db_path={db_path}, column={column})")

    db_con = sqlite3.connect(db_path)

    # get a numpy ndarray of table names
    db_table_array = pd.read_sql(
        f"SELECT name FROM sqlite_schema WHERE type='table' AND name NOT like 'sqlite%'", db_con,
    ).name.values

    index_array = pd.read_sql(  # get a numpy ndarray of Date index
        f"SELECT date FROM {db_table_array[0]}", db_con
    ).date.values
    # ).values

    df = pd.DataFrame(index=index_array)
    # df.index = pd.to_datetime(df.index, unit="s")

    for table in db_table_array:
        df[table] = pd.read_sql(
            f"SELECT date, {column} FROM {table}", db_con, index_col="date"
        )
    df.index = pd.to_datetime(df.index, unit="s").date
    df.index.names = ['date']

    return df


def create_df_from_database_table(db_path: str, table: str) -> pd.DataFrame:
    """"""
    if DEBUG:
        logger.debug(f"create_df_from_database_table(db_path={db_path}, table={table})")

    db_con = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table}", db_con, index_col="date")
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
            cls.table_list = ["YINN", "YANG"]

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
                    INSERT INTO YINN (date, cwap, sc_cwap) VALUES (1754625600, 4299, 860);
                    INSERT INTO YINN (date, cwap, sc_cwap) VALUES (1754884800, 4214, 876);
                    INSERT INTO YINN (date, cwap, sc_cwap) VALUES (1754971200, 4377, 1095);

                    INSERT INTO YANG (date, cwap, sc_cwap) VALUES (1754625600, 2865, 1129);
                    INSERT INTO YANG (date, cwap, sc_cwap) VALUES (1754884800, 2929, 1134);
                    INSERT INTO YANG (date, cwap, sc_cwap) VALUES (1754971200, 2813, 910);
                    """
                )
                cls.db_table_array = pd.read_sql(
                    f"SELECT name FROM sqlite_schema WHERE type='table' AND name NOT like 'sqlite%'", cls.con,
                ).name.values

        def test_database_exists(self):
            self.assertListEqual(list(self.db_table_array), self.table_list)

        def test_create_df_from_database_table(self):
            df = create_df_from_database_table(db_path="file:temp.db?mode=memory&cache=shared", table=self.table_list[0])
            print(f"{self.table_list[0]} dataframe:\n{df}")

            df = create_df_from_database_table(db_path="file:temp.db?mode=memory&cache=shared", table=self.table_list[1])
            print(f"{self.table_list[1]} dataframe:\n{df}")

        def test_create_df_from_one_column_in_each_table(self):
            df = create_df_from_one_column_in_every_table(db_path="file:temp.db?mode=memory&cache=shared", column=self.data_list[0])
            print(f"{self.data_list[0]} dataframe:\n{df}")

            df = create_df_from_one_column_in_every_table(db_path="file:temp.db?mode=memory&cache=shared", column=self.data_list[1])
            print(f"{self.data_list[1]} dataframe:\n{df}")

        @classmethod
        def tearDownClass(cls):
            print(f"tearDown({cls})")

    unittest.main()
