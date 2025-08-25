""""""
import logging, logging.config

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


DEBUG = True

logging.config.fileConfig(fname="logger.ini")
logger = logging.getLogger(__name__)


def correlate_data(dataframe: pd.DataFrame, target_list: list, shift_period: int):
    """log correlation matrix to debug.log, plot correlation matrix heatmap"""
    if DEBUG:
        logger.debug(f"correlate_data(dataframe={type(dataframe)}, target_list={target_list}, shift_period={shift_period})")

    dataframe = _timeshift_dataframe_columns(df=dataframe, tl=target_list, sp=shift_period)

    # create pandas correlation matrix
    corr_df = (dataframe.corr(method="kendall") * 100).round().astype(int)
    if DEBUG: logger.debug(f"correlation matrix:\n{corr_df}")

    # plot correlation matrix
    plt.figure(figsize=(10, 7.5))
    sns.set_context("paper")
    sns.heatmap(
        data=corr_df, mask=np.triu(np.ones_like(corr_df, dtype=bool)),
        annot=True, vmax=100, vmin=-100, center=0, square=True,
        linewidths=0.5, cbar_kws={"shrink": 0.2}, cmap="coolwarm",
    ).set_title(
        f"Correlation - {shift_period} Period Timeshift {(', '.join(target_list))}"
    )
    plt.show()
    plt.close()


def plt_all_columns_from_dataframe(dataframe: pd.DataFrame):
    """plot dataframe"""
    if DEBUG:
        logger.debug(f"plt_all_columns_from_dataframe({dataframe.name} dataframe:\n{dataframe})")

    plt.figure(figsize=(10, 7.5))
    sns.set_context("paper")
    sns.lineplot(
        data=dataframe, palette="pastel", linewidth=2.5,
    ).set_title(f"{dataframe.name} Dataframe")

    plt.show()
    plt.close()


def plt_savgol_filter_alt_params(dataframe: pd.DataFrame, win_sz_list: list, polyorder: int):
    """"""
    from scipy.signal import savgol_filter

    if DEBUG:
        logger.debug(f"plt_savgol_filter_alt_params(dataframe'{type(dataframe)}, win_sz_list={win_sz_list}, poly_list={polyorder})")

    for col in dataframe.columns:
        fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(10, 7.5))
        plt.xlabel("Date")
        plt.ylabel("Value")

        raw = pd.Series(data=dataframe[col], name=dataframe[col].name)

        for j, w in enumerate(win_sz_list):
            smooth = savgol_filter(x=raw, window_length=w, polyorder=polyorder, deriv=0)

            axs[0, j].plot(raw.index, raw, label=f"raw {dataframe.name} data")
            axs[0, j].plot(raw.index, smooth, label=f"smooth {dataframe.name} data")
            axs[0, j].legend()
            axs[0, j].set_title(f"{raw.name} - window {w}, polyorder {polyorder}")

        for j, w in enumerate(win_sz_list):
            slope = savgol_filter(x=raw, window_length=w, polyorder=polyorder, deriv=1)

            # axs[i+1, j].plot(raw.index, raw, label=f"raw {dataframe.name} data")
            axs[1, j].plot(raw.index, slope, label=f"smooth data slope")
            axs[1, j].legend()
            axs[1, j].set_title(f"{raw.name} - window {w}, polyorder {polyorder}")

        plt.tight_layout()
        plt.show()
        plt.close()


def plt_target_vs_indicator_timeseries(dataframe: pd.DataFrame, target_list: list, shift_period: int):
    """create series of lineplots comparing timeseries"""
    if DEBUG:
        logger.debug(f"plt_target_vs_indicator_timeseries(dataframe={type(dataframe)}, target_list={target_list}, shift_period={shift_period})")

    dataframe = _timeshift_dataframe_columns(df=dataframe, tl=target_list, sp=shift_period)
    target_df = dataframe[target_list].copy()
    total = len(dataframe.columns)- len(target_df.columns)
    i = 0

    for col in dataframe.columns:
        if dataframe[col].name in target_list:
            continue
        i += 1
        plot_df = pd.concat(objs=[dataframe[col], target_df], axis=1)
        if DEBUG: logger.debug(f"plot_df ({i}/{total}):\n{plot_df}\n")

        # plot timeseries
        plt.figure(figsize=(10, 7.5))
        sns.set_context("paper")
        sns.lineplot(
            data=plot_df, palette="pastel", linewidth=2.5,
        ).set_title(
            f"{shift_period} Period Timeshift {dataframe[col].name} vs. {(', '.join(target_list))} ({i}/{total})"
        )
        plt.show()
        plt.close()


def _timeshift_dataframe_columns(df: pd.DataFrame, tl: list, sp: int):
    """mask columns in tl, then shift columns not in target list by sp"""

    shift_cols = df.columns[~(df.columns.isin(tl))]
    df[shift_cols] = df[shift_cols].shift(periods=sp)

    return df


if __name__ == "__main__":
    import datetime, unittest
    from pandas import Timestamp

    if DEBUG:
        logger.debug(f"******* START - plt_utils.py *******")


    class TestPlotterUtilityFunctions(unittest.TestCase):
        """"""
        @classmethod
        def setUpClass(cls):
            print(f"-setUp({cls})")

            cwap_dict = {
                'index': [Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00'), Timestamp('2025-08-13 04:00:00'), Timestamp('2025-08-14 04:00:00'), Timestamp('2025-08-15 04:00:00'), Timestamp('2025-08-18 04:00:00'), Timestamp('2025-08-19 04:00:00'), Timestamp('2025-08-20 04:00:00'), Timestamp('2025-08-21 04:00:00'), Timestamp('2025-08-22 04:00:00')],
                'columns': ['ASEA', 'ECNS', 'FXI', 'HYG', 'SPXL', 'SPXS', 'XLF', 'XLY', 'YANG', 'YINN'],
                'data': [[1651, 3326, 3685, 7966, 17796, 458, 5242, 22191, 3055, 4096], [1649, 3362, 3752, 7953, 17740, 460, 5185, 22001, 2892, 4317], [1651, 3367, 3739, 7959, 17669, 462, 5185, 21908, 2916, 4275], [1665, 3434, 3749, 7971, 18035, 452, 5236, 22006, 2895, 4302], [1673, 3456, 3813, 7985, 18074, 452, 5254, 22190, 2753, 4524], [1681, 3470, 3822, 7997, 18208, 448, 5252, 22331, 2734, 4556], [1681, 3484, 3864, 8006, 18118, 450, 5264, 22504, 2647, 4700], [1697, 3474, 3906, 8011, 18519, 440, 5296, 22643, 2562, 4846], [1708, 3551, 3895, 8005, 18662, 437, 5315, 22319, 2581, 4808], [1696, 3533, 3860, 8009, 18808, 434, 5334, 22458, 2656, 4676], [1690, 3536, 3852, 8006, 18826, 434, 5314, 22618, 2674, 4643], [1678, 3583, 3832, 8009, 18732, 436, 5289, 22490, 2716, 4569], [1662, 3538, 3784, 7995, 18610, 439, 5272, 22343, 2815, 4406], [1638, 3486, 3743, 7999, 18526, 441, 5250, 22216, 2912, 4255], [1655, 3416, 3684, 7996, 17516, 465, 5140, 21606, 3056, 4053], [1673, 3479, 3747, 8020, 18140, 450, 5180, 21832, 2901, 4252], [1680, 3560, 3768, 8019, 18062, 450, 5171, 21910, 2849, 4327], [1696, 3583, 3772, 8026, 18296, 445, 5190, 22244, 2845, 4336], [1704, 3574, 3777, 8023, 18375, 443, 5155, 22333, 2834, 4352], [1715, 3576, 3763, 8021, 18680, 436, 5179, 22396, 2865, 4299], [1713, 3575, 3736, 8022, 18670, 437, 5185, 22455, 2929, 4214], [1737, 3585, 3785, 8035, 19093, 426, 5238, 22623, 2813, 4377], [1763, 3664, 3904, 8057, 19392, 420, 5273, 22931, 2558, 4780], [1739, 3624, 3837, 8041, 19364, 420, 5290, 22936, 2688, 4531], [1741, 3721, 3836, 8044, 19300, 422, 5262, 22933, 2688, 4529], [1723, 3797, 3859, 8042, 19232, 423, 5246, 22970, 2646, 4604], [1720, 3763, 3829, 8040, 18990, 428, 5263, 23027, 2710, 4495], [1732, 3726, 3839, 8036, 18675, 436, 5281, 22806, 2688, 4522], [1732, 3744, 3835, 8022, 18541, 439, 5264, 22606, 2695, 4512], [1753, 3830, 3911, 8072, 19214, 423, 5344, 23160, 2544, 4772]],
                'index_names': ['datetime'], 'column_names': [None]
            }
            cls.cwap_df = pd.DataFrame.from_dict(data=cwap_dict, orient="tight")
            cls.cwap_df.name = "cwap"

            sc_cwap_dict = {
                'index': [Timestamp('2025-07-14 04:00:00'), Timestamp('2025-07-15 04:00:00'), Timestamp('2025-07-16 04:00:00'), Timestamp('2025-07-17 04:00:00'), Timestamp('2025-07-18 04:00:00'), Timestamp('2025-07-21 04:00:00'), Timestamp('2025-07-22 04:00:00'), Timestamp('2025-07-23 04:00:00'), Timestamp('2025-07-24 04:00:00'), Timestamp('2025-07-25 04:00:00'), Timestamp('2025-07-28 04:00:00'), Timestamp('2025-07-29 04:00:00'), Timestamp('2025-07-30 04:00:00'), Timestamp('2025-07-31 04:00:00'), Timestamp('2025-08-01 04:00:00'), Timestamp('2025-08-04 04:00:00'), Timestamp('2025-08-05 04:00:00'), Timestamp('2025-08-06 04:00:00'), Timestamp('2025-08-07 04:00:00'), Timestamp('2025-08-08 04:00:00'), Timestamp('2025-08-11 04:00:00'), Timestamp('2025-08-12 04:00:00'), Timestamp('2025-08-13 04:00:00'), Timestamp('2025-08-14 04:00:00'), Timestamp('2025-08-15 04:00:00'), Timestamp('2025-08-18 04:00:00'), Timestamp('2025-08-19 04:00:00'), Timestamp('2025-08-20 04:00:00'), Timestamp('2025-08-21 04:00:00'), Timestamp('2025-08-22 04:00:00')],
                'columns': ['ASEA', 'ECNS', 'FXI', 'HYG', 'SPXL', 'SPXS', 'XLF', 'XLY', 'YANG', 'YINN'],
                'data': [[1038, 1048, 1009, 1022, 1007, 992, 1026, 1031, 989, 1009], [1038, 1048, 1009, 1022, 1007, 992, 1026, 1031, 989, 1009], [1000, 1024, 1000, 1000, 888, 1100, 1000, 934, 1000, 1000], [1175, 1186, 1000, 1133, 1161, 840, 1200, 1010, 1000, 1000], [1072, 1049, 1172, 1107, 1019, 1000, 1052, 1130, 825, 1178], [1100, 1077, 1024, 1092, 1154, 800, 1000, 1086, 976, 1025], [1000, 1100, 1164, 1085, 1000, 1000, 1166, 1110, 835, 1163], [1200, 1000, 1100, 1071, 1155, 840, 1145, 1089, 901, 1100], [1081, 1174, 1000, 966, 1052, 953, 1074, 885, 1000, 1000], [983, 1000, 847, 1000, 1101, 900, 1100, 1000, 1159, 844], [933, 1000, 962, 1000, 1021, 1000, 990, 1107, 1038, 960], [866, 1188, 857, 1000, 838, 1200, 888, 1000, 1140, 861], [885, 1000, 858, 842, 887, 1120, 919, 893, 1140, 862], [880, 892, 907, 1000, 918, 1080, 887, 907, 1098, 903], [1000, 885, 882, 1000, 815, 1184, 833, 834, 1119, 885], [1102, 1000, 1012, 1175, 1000, 1000, 1000, 1000, 985, 1000], [1056, 1112, 1050, 1000, 1000, 1000, 1000, 1051, 949, 1054], [1139, 1044, 1032, 1171, 1133, 800, 1105, 1162, 985, 1021], [1066, 1000, 1111, 1000, 1050, 942, 908, 1042, 853, 1128], [1115, 1000, 871, 919, 1158, 844, 1000, 1082, 1129, 860], [1000, 1000, 868, 1000, 1000, 1000, 1040, 1096, 1134, 876], [1183, 1180, 1089, 1185, 1195, 818, 1179, 1148, 910, 1095], [1104, 1177, 1141, 1125, 1082, 929, 1079, 1129, 862, 1142], [1000, 1000, 1000, 1000, 1000, 1000, 1065, 1003, 1000, 1000], [1000, 1117, 997, 1000, 860, 1200, 921, 1000, 1000, 998], [822, 1087, 1191, 1000, 896, 1066, 927, 1183, 800, 1194], [971, 1000, 953, 900, 843, 1166, 1011, 1121, 1068, 937], [1150, 895, 1000, 866, 886, 1123, 1102, 851, 1000, 1000], [1000, 1000, 1000, 844, 940, 1054, 1000, 904, 1000, 1000], [1200, 1165, 1189, 1144, 1160, 837, 1157, 1127, 809, 1192]],
                'index_names': ['datetime'], 'column_names': [None]
            }
            cls.sc_cwap_df = pd.DataFrame.from_dict(data=sc_cwap_dict, orient="tight")
            cls.sc_cwap_df.name = "sc_cwap"

        # @unittest.skip
        def test_correlate_data(self):
            # if DEBUG: logger.debug(f"test_correlate_data(self={self})")
            correlate_data(dataframe=self.cwap_df, target_list=["SPXL", "SPXS", "YINN", "YANG"], shift_period=3)

        # @unittest.skip
        def test_plt_all_columns_from_dataframe(self):
            # if DEBUG: logger.debug(f"test_plt_all_columns_from_dataframe(self={self})")
            plt_all_columns_from_dataframe(dataframe=self.sc_cwap_df)

        # @unittest.skip
        def test_plt_savgol_filter_alt_params(self):
            # if DEBUG: logger.debug(f"test_plt_savgol_filter_alt_params()")
            plt_savgol_filter_alt_params(dataframe=self.cwap_df, win_sz_list=[7, 14], polyorder=2)

        # @unittest.skip
        def test_plt_target_vs_indicator_timeseries(self):
            # if DEBUG: logger.debug(f"test_plt_target_vs_indicator_timeseries(self={self})")
            plt_target_vs_indicator_timeseries(dataframe=self.sc_cwap_df, target_list=["SPXL", "SPXS", "YINN", "YANG"], shift_period=3)

        @classmethod
        def tearDownClass(cls):
            print(f"\n-tearDown({cls})")

    unittest.main()
