""""""
import logging, logging.config

import pandas as pd

from scipy.signal import savgol_filter


DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


def savgol_filter_slope_change_signal(dataframe: pd.DataFrame, win_length: int, poly_order: int=2, deriv: int=1):
    """"""
    if DEBUG:
        logger.debug(f"savgol_filter_slope_change_signal(dataframe={type(dataframe)}, win_length={win_length}, poly_order={poly_order}, deriv={deriv})")

    # create empty dataframe with index as a timestamp
    slope_df = pd.DataFrame(index=dataframe.index.values)
    slope_df.index.name = "datetime"
    sig_df = pd.DataFrame(index=dataframe.index.values)
    sig_df.index.name = "datetime"
    sig_df.name = f"sig_{dataframe.name}"

    # slope (first derivitive) of filtered timeseries
    for col in dataframe.columns:
        slope_df[col] = savgol_filter(
            x=dataframe[col].values, window_length=win_length,
            polyorder=poly_order, deriv=deriv
        )
    if DEBUG: logger.debug(f"{dataframe.name}_df savgol slope:\n{slope_df}\n")

    for col in slope_df.columns:
        data = slope_df[col].values
        zero_list = list()

        for i, cur_item in enumerate(data):
            prev_item = data[i - 1]
            if i == 0:
                # reset starting value
                zero_list.append(0)
                continue
            elif cur_item > 0 and prev_item <= 0:
                # derivative crosses zero to upside
                zero_list.append(1)
            elif cur_item < 0 and prev_item >= 0:
                # derivative crosses zero to downside
                zero_list.append(-1)
            else:
                # no crossing maintain status
                zero_list.append(zero_list[i - 1])

        sig_df[f"{col}"] = zero_list

    sig_df["sum"] = sig_df.sum(axis=1)

    return sig_df


def main():
    if DEBUG:
        logger.debug(f"main()")


if __name__ == "__main__":
    import unittest
    from pandas import Timestamp

    if DEBUG:
        logger.debug(f"******* START - beta/sig_utils.py *******")


    class TestSignalUtilityFunctions(unittest.TestCase):
        """"""
        @classmethod
        def setUpClass(cls):
            print(f"-setUp({cls})")

            china_list = ["ECNS", "FXI"]
            usa_list = ["HYG", "XLF", "XLY"]

            cwap_dict = {
                'index': [Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00'), Timestamp('2025-08-13 04:00:00'), Timestamp('2025-08-14 04:00:00'), Timestamp('2025-08-15 04:00:00'), Timestamp('2025-08-18 04:00:00'), Timestamp('2025-08-19 04:00:00'), Timestamp('2025-08-20 04:00:00'), Timestamp('2025-08-21 04:00:00'), Timestamp('2025-08-22 04:00:00')],
                'columns': ['ASEA', 'ECNS', 'FXI', 'HYG', 'SPXL', 'SPXS', 'XLF', 'XLY', 'YANG', 'YINN'],
                'data': [[1651, 3326, 3685, 7966, 17796, 458, 5242, 22191, 3055, 4096], [1649, 3362, 3752, 7953, 17740, 460, 5185, 22001, 2892, 4317], [1651, 3367, 3739, 7959, 17669, 462, 5185, 21908, 2916, 4275], [1665, 3434, 3749, 7971, 18035, 452, 5236, 22006, 2895, 4302], [1673, 3456, 3813, 7985, 18074, 452, 5254, 22190, 2753, 4524], [1681, 3470, 3822, 7997, 18208, 448, 5252, 22331, 2734, 4556], [1681, 3484, 3864, 8006, 18118, 450, 5264, 22504, 2647, 4700], [1697, 3474, 3906, 8011, 18519, 440, 5296, 22643, 2562, 4846], [1708, 3551, 3895, 8005, 18662, 437, 5315, 22319, 2581, 4808], [1696, 3533, 3860, 8009, 18808, 434, 5334, 22458, 2656, 4676], [1690, 3536, 3852, 8006, 18826, 434, 5314, 22618, 2674, 4643], [1678, 3583, 3832, 8009, 18732, 436, 5289, 22490, 2716, 4569], [1662, 3538, 3784, 7995, 18610, 439, 5272, 22343, 2815, 4406], [1638, 3486, 3743, 7999, 18526, 441, 5250, 22216, 2912, 4255], [1655, 3416, 3684, 7996, 17516, 465, 5140, 21606, 3056, 4053], [1673, 3479, 3747, 8020, 18140, 450, 5180, 21832, 2901, 4252], [1680, 3560, 3768, 8019, 18062, 450, 5171, 21910, 2849, 4327], [1696, 3583, 3772, 8026, 18296, 445, 5190, 22244, 2845, 4336], [1704, 3574, 3777, 8023, 18375, 443, 5155, 22333, 2834, 4352], [1715, 3576, 3763, 8021, 18680, 436, 5179, 22396, 2865, 4299], [1713, 3575, 3736, 8022, 18670, 437, 5185, 22455, 2929, 4214], [1737, 3585, 3785, 8035, 19093, 426, 5238, 22623, 2813, 4377], [1763, 3664, 3904, 8057, 19392, 420, 5273, 22931, 2558, 4780], [1739, 3624, 3837, 8041, 19364, 420, 5290, 22936, 2688, 4531], [1741, 3721, 3836, 8044, 19300, 422, 5262, 22933, 2688, 4529], [1723, 3797, 3859, 8042, 19232, 423, 5246, 22970, 2646, 4604], [1720, 3763, 3829, 8040, 18990, 428, 5263, 23027, 2710, 4495], [1732, 3726, 3839, 8036, 18675, 436, 5281, 22806, 2688, 4522], [1732, 3744, 3835, 8022, 18541, 439, 5264, 22606, 2695, 4512], [1753, 3830, 3911, 8072, 19214, 423, 5344, 23160, 2544, 4772]],
                'index_names': ['datetime'], 'column_names': [None]
            }
            cls.cwap_df = pd.DataFrame.from_dict(data=cwap_dict, orient="tight")
            cls.cwap_df.name = "all_cwap"
            cls.china_df = cls.cwap_df[china_list]
            cls.china_df.name = "china_cwap"
            cls.usa_df = cls.cwap_df[usa_list]
            cls.usa_df.name = "usa_cwap"

        @unittest.skip
        def test_main(self):
            if DEBUG: logger.debug(f"test_main()")

        # @unittest.skip
        def test_savgol_filter_slope_change_signal(self):
            for df in [self.china_df, self.usa_df]:
                sg_slope_sig_df = savgol_filter_slope_change_signal(
                    # dataframe=self.usa_df, win_length=3, poly_order=2
                    dataframe=df, win_length=3, poly_order=2
                )
                if DEBUG: logger.debug(
                    f"{sg_slope_sig_df.name} dataframe:\n{sg_slope_sig_df}\n{type(sg_slope_sig_df)}"
                )

        @classmethod
        def tearDownClass(cls):
            print(f"\n-tearDown({cls})")

    unittest.main()
