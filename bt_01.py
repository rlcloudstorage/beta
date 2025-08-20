""""""
import logging, logging.config

import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import pandas as pd

import utils_pd


DEBUG = True
DB = "/home/la/dev/data/tiingo_sm.db"

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)

ctx = {}


def main(self) -> None:
    if DEBUG:
        logger.debug(f"main(self={self})")
    import utils_sig
    usa_sig = utils_sig.savgol_filter_slope_change_signal(dataframe=self.usa_df, win_length=3, poly_order=2)
    usa_sig_dict = usa_sig.to_dict()
    print(f"usa_sig_dict = {usa_sig_dict}")


if __name__ == "__main__":
    import datetime, unittest

    if DEBUG:
        logger.debug(f"******* START *******")


    class TestBacktestingFunctions(unittest.TestCase):
        """"""
        @classmethod
        def setUpClass(cls):
            print(f"-setUp({cls})")

            usa_dict = {
                'index': [datetime.date(2025, 7, 2), datetime.date(2025, 7, 3), datetime.date(2025, 7, 7), datetime.date(2025, 7, 8), datetime.date(2025, 7, 9), datetime.date(2025, 7, 10), datetime.date(2025, 7, 11), datetime.date(2025, 7, 14), datetime.date(2025, 7, 15), datetime.date(2025, 7, 16), datetime.date(2025, 7, 17), datetime.date(2025, 7, 18), datetime.date(2025, 7, 21), datetime.date(2025, 7, 22), datetime.date(2025, 7, 23), datetime.date(2025, 7, 24), datetime.date(2025, 7, 25), datetime.date(2025, 7, 28), datetime.date(2025, 7, 29), datetime.date(2025, 7, 30), datetime.date(2025, 7, 31), datetime.date(2025, 8, 1), datetime.date(2025, 8, 4), datetime.date(2025, 8, 5), datetime.date(2025, 8, 6), datetime.date(2025, 8, 7), datetime.date(2025, 8, 8), datetime.date(2025, 8, 11), datetime.date(2025, 8, 12)],
                'columns': ['HYG', 'SPXL', 'SPXS', 'XLF', 'XLY'],
                'data': [[7986, 17468, 466, 5258, 21969], [7994, 17902, 455, 5309, 22117], [7975, 17552, 465, 5276, 21828], [7961, 17528, 466, 5230, 21803], [7978, 17763, 459, 5236, 21882], [7975, 17927, 454, 5261, 22096], [7961, 17739, 460, 5220, 22116], [7966, 17796, 458, 5242, 22191], [7953, 17740, 460, 5185, 22001], [7959, 17669, 462, 5185, 21908], [7971, 18035, 452, 5236, 22006], [7985, 18074, 452, 5254, 22190], [7997, 18208, 448, 5252, 22331], [8006, 18118, 450, 5264, 22504], [8011, 18519, 440, 5296, 22643], [8005, 18662, 437, 5315, 22319], [8009, 18808, 434, 5334, 22458], [8006, 18826, 434, 5314, 22618], [8009, 18732, 436, 5289, 22490], [7995, 18610, 439, 5272, 22343], [7999, 18526, 441, 5250, 22216], [7996, 17516, 465, 5140, 21606], [8020, 18140, 450, 5180, 21832], [8019, 18062, 450, 5171, 21910], [8026, 18296, 445, 5190, 22244], [8023, 18375, 443, 5155, 22333], [8021, 18680, 436, 5179, 22396], [8022, 18670, 437, 5185, 22455], [8035, 19093, 426, 5238, 22623]],
                'index_names': ['date'], 'column_names': [None]
            }
            cls.usa_df = pd.DataFrame.from_dict(data=usa_dict, orient="tight")
            cls.usa_df.name = "usa"
            cls.spx_df = cls.usa_df[["SPXL", "SPXS"]]
            cls.spx_df.name = "spx"

            usa_sig_dict = {
                datetime.date(2025, 7, 2): 0, datetime.date(2025, 7, 3): -2, datetime.date(2025, 7, 7): -3, datetime.date(2025, 7, 8): 1, datetime.date(2025, 7, 9): 3, datetime.date(2025, 7, 10): -1, datetime.date(2025, 7, 11): -1, datetime.date(2025, 7, 14): -3, datetime.date(2025, 7, 15): -3, datetime.date(2025, 7, 16): 3, datetime.date(2025, 7, 17): 3, datetime.date(2025, 7, 18): 3, datetime.date(2025, 7, 21): 3, datetime.date(2025, 7, 22): 3, datetime.date(2025, 7, 23): -1, datetime.date(2025, 7, 24): -1, datetime.date(2025, 7, 25): 1, datetime.date(2025, 7, 28): -1, datetime.date(2025, 7, 29): -3, datetime.date(2025, 7, 30): -3, datetime.date(2025, 7, 31): -1, datetime.date(2025, 8, 1): -1, datetime.date(2025, 8, 4): 3, datetime.date(2025, 8, 5): 3, datetime.date(2025, 8, 6): 1, datetime.date(2025, 8, 7): -1, datetime.date(2025, 8, 8): 1, datetime.date(2025, 8, 11): 3, datetime.date(2025, 8, 12): 3
            }
            cls.usa_sig = pd.Series(data=usa_sig_dict, index=usa_sig_dict.keys(), name="usa_sig")

        @unittest.skip
        def test_main(self):
            main(self)

        # @unittest.skip
        def test_pandas_data(self):
            if DEBUG: logger.debug(
                f"usa_df:\n{self.usa_df}\n\nspx_df:\n{self.spx_df}\n\nusa_sig_series:\n{self.usa_sig}"
            )

        @classmethod
        def tearDownClass(cls):
            print(f"\n-tearDown({cls})")

    unittest.main()
