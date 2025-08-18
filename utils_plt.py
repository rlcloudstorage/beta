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

    if DEBUG:
        logger.debug(f"******* START - plt_utils.py *******")


    class TestPlotterUtilityFunctions(unittest.TestCase):
        """"""
        @classmethod
        def setUpClass(cls):
            print(f"-setUp({cls})")

            cwap_dict = {
                'index': [datetime.date(2025, 7, 2), datetime.date(2025, 7, 3), datetime.date(2025, 7, 7), datetime.date(2025, 7, 8), datetime.date(2025, 7, 9), datetime.date(2025, 7, 10), datetime.date(2025, 7, 11), datetime.date(2025, 7, 14), datetime.date(2025, 7, 15), datetime.date(2025, 7, 16), datetime.date(2025, 7, 17), datetime.date(2025, 7, 18), datetime.date(2025, 7, 21), datetime.date(2025, 7, 22), datetime.date(2025, 7, 23), datetime.date(2025, 7, 24), datetime.date(2025, 7, 25), datetime.date(2025, 7, 28), datetime.date(2025, 7, 29), datetime.date(2025, 7, 30), datetime.date(2025, 7, 31), datetime.date(2025, 8, 1), datetime.date(2025, 8, 4), datetime.date(2025, 8, 5), datetime.date(2025, 8, 6), datetime.date(2025, 8, 7), datetime.date(2025, 8, 8), datetime.date(2025, 8, 11), datetime.date(2025, 8, 12)],
                'columns': ['AFK', 'ASEA', 'ECNS', 'EZU', 'FXI', 'HYG', 'SPXL', 'SPXS', 'XLF', 'XLY', 'YANG', 'YINN'],
                'data': [[2049, 1633, 3162, 5956, 3664, 7986, 17468, 466, 5258, 21969, 3096, 4058], [2064, 1638, 3179, 5962, 3630, 7994, 17903, 455, 5309, 22117, 3188, 3945], [2062, 1630, 3176, 5931, 3636, 7975, 17553, 465, 5276, 21828, 3174, 3959], [2051, 1627, 3206, 5978, 3667, 7961, 17528, 465, 5230, 21803, 3094, 4055], [2048, 1631, 3216, 6056, 3620, 7978, 17763, 459, 5236, 21882, 3214, 3896], [2068, 1639, 3242, 6026, 3646, 7975, 17927, 454, 5261, 22096, 3148, 3977], [2056, 1651, 3254, 5970, 3651, 7961, 17739, 460, 5220, 22116, 3136, 3991], [2071, 1651, 3327, 5954, 3685, 7966, 17796, 458, 5243, 22192, 3055, 4096], [2058, 1649, 3362, 5910, 3752, 7953, 17740, 460, 5185, 22001, 2892, 4317], [2072, 1651, 3367, 5897, 3740, 7959, 17669, 462, 5185, 21908, 2916, 4274], [2070, 1665, 3434, 5918, 3749, 7971, 18035, 452, 5236, 22007, 2895, 4302], [2084, 1673, 3457, 5920, 3813, 7985, 18074, 452, 5254, 22190, 2753, 4524], [2095, 1681, 3470, 5935, 3822, 7997, 18208, 448, 5252, 22331, 2734, 4555], [2141, 1681, 3484, 5940, 3864, 8006, 18118, 450, 5265, 22504, 2648, 4700], [2167, 1697, 3474, 6056, 3906, 8011, 18519, 441, 5296, 22643, 2562, 4845], [2154, 1708, 3551, 6016, 3895, 8005, 18662, 437, 5315, 22319, 2581, 4808], [2157, 1696, 3533, 6015, 3860, 8009, 18808, 434, 5334, 22458, 2655, 4677], [2121, 1690, 3536, 5920, 3851, 8006, 18826, 434, 5313, 22618, 2674, 4643], [2126, 1678, 3583, 5930, 3832, 8010, 18732, 436, 5289, 22490, 2716, 4569], [2111, 1662, 3538, 5885, 3784, 7995, 18610, 439, 5272, 22343, 2815, 4406], [2101, 1637, 3486, 5813, 3743, 7999, 18526, 441, 5250, 22216, 2912, 4255], [2085, 1655, 3416, 5742, 3684, 7996, 17516, 465, 5140, 21606, 3056, 4053], [2124, 1674, 3480, 5818, 3748, 8020, 18140, 450, 5181, 21832, 2901, 4252], [2129, 1680, 3560, 5827, 3768, 8019, 18062, 450, 5171, 21910, 2849, 4327], [2159, 1696, 3583, 5877, 3772, 8026, 18296, 445, 5190, 22244, 2845, 4336], [2173, 1704, 3574, 5948, 3777, 8024, 18375, 443, 5155, 22333, 2834, 4352], [2178, 1715, 3577, 5975, 3763, 8021, 18680, 436, 5179, 22396, 2865, 4299], [2168, 1713, 3576, 5934, 3736, 8023, 18670, 437, 5185, 22455, 2930, 4214], [2181, 1737, 3585, 5980, 3785, 8035, 19093, 426, 5238, 22624, 2813, 4377]],
                'index_names': ['date'], 'column_names': [None]
            }
            sc_cwap_dict = {
                'index': [datetime.date(2025, 7, 2), datetime.date(2025, 7, 3), datetime.date(2025, 7, 7), datetime.date(2025, 7, 8), datetime.date(2025, 7, 9), datetime.date(2025, 7, 10), datetime.date(2025, 7, 11), datetime.date(2025, 7, 14), datetime.date(2025, 7, 15), datetime.date(2025, 7, 16), datetime.date(2025, 7, 17), datetime.date(2025, 7, 18), datetime.date(2025, 7, 21), datetime.date(2025, 7, 22), datetime.date(2025, 7, 23), datetime.date(2025, 7, 24), datetime.date(2025, 7, 25), datetime.date(2025, 7, 28), datetime.date(2025, 7, 29), datetime.date(2025, 7, 30), datetime.date(2025, 7, 31), datetime.date(2025, 8, 1), datetime.date(2025, 8, 4), datetime.date(2025, 8, 5), datetime.date(2025, 8, 6), datetime.date(2025, 8, 7), datetime.date(2025, 8, 8), datetime.date(2025, 8, 11), datetime.date(2025, 8, 12)],
                'columns': ['AFK', 'ASEA', 'ECNS', 'EZU', 'FXI', 'HYG', 'SPXL', 'SPXS', 'XLF', 'XLY', 'YANG', 'YINN'],
                'data': [[1013, 1029, 1058, 996, 1009, 1011, 1028, 969, 1011, 1029, 990, 1009], [1013, 1029, 1058, 996, 1009, 1011, 1028, 969, 1011, 1029, 990, 1009], [1000, 925, 1000, 838, 1000, 884, 1000, 1000, 1000, 902, 1000, 1000], [830, 945, 1180, 1068, 1167, 915, 986, 1000, 883, 984, 829, 1174], [957, 1050, 1050, 1124, 931, 1035, 1178, 800, 1000, 1136, 1066, 920], [1170, 1133, 1144, 1000, 1000, 1000, 1082, 909, 1161, 1146, 1000, 1000], [1000, 1120, 1063, 869, 1032, 835, 974, 1033, 921, 1017, 969, 1029], [1040, 1000, 1171, 955, 1174, 1000, 1000, 1000, 1000, 1158, 825, 1176], [1000, 800, 1064, 853, 1132, 876, 1000, 1000, 879, 879, 866, 1135], [1014, 1000, 1025, 954, 1000, 1000, 888, 1100, 1000, 934, 1000, 1000], [1000, 1175, 1186, 1076, 1000, 1133, 1161, 840, 1200, 1012, 1000, 1000], [1171, 1072, 1051, 1017, 1175, 1107, 1019, 1000, 1052, 1129, 825, 1177], [1088, 1100, 1072, 1176, 1024, 1092, 1154, 800, 1000, 1087, 976, 1024], [1161, 1000, 1103, 1050, 1164, 1085, 1000, 1000, 1169, 1110, 836, 1164], [1072, 1200, 1000, 1191, 1100, 1071, 1155, 844, 1140, 1089, 900, 1100], [1000, 1081, 1174, 1000, 1000, 966, 1052, 938, 1076, 885, 1000, 1000], [1000, 983, 1000, 995, 847, 1000, 1101, 914, 1100, 1000, 1159, 844], [816, 933, 1000, 802, 959, 1000, 1021, 1000, 980, 1107, 1040, 958], [1000, 866, 1188, 1000, 864, 1050, 838, 1200, 893, 1000, 1137, 862], [866, 885, 1000, 844, 856, 853, 887, 1120, 917, 893, 1140, 862], [919, 878, 892, 876, 907, 1000, 918, 1080, 887, 907, 1098, 903], [876, 1000, 885, 900, 882, 1000, 815, 1184, 833, 834, 1119, 885], [1117, 1102, 1000, 1013, 1015, 1175, 1000, 1000, 1000, 1000, 985, 1000], [1022, 1048, 1111, 1021, 1047, 1000, 1000, 1000, 1000, 1051, 949, 1054], [1171, 1145, 1044, 1169, 1033, 1171, 1133, 800, 1094, 1162, 985, 1021], [1063, 1066, 1000, 1117, 1111, 1000, 1050, 942, 908, 1042, 853, 1128], [1052, 1115, 1000, 1055, 871, 880, 1158, 844, 1000, 1082, 1129, 860], [900, 1000, 1000, 931, 868, 1000, 1000, 1000, 1040, 1096, 1135, 876], [1046, 1183, 1177, 1021, 1089, 1171, 1195, 818, 1179, 1148, 911, 1095]],
                'index_names': ['date'], 'column_names': [None]
            }
            cls.cwap_df = pd.DataFrame.from_dict(data=cwap_dict, orient="tight")
            cls.cwap_df.name = "cwap"
            cls.sc_cwap_df = pd.DataFrame.from_dict(data=sc_cwap_dict, orient="tight")
            cls.sc_cwap_df.name = "sc_cwap"

        @unittest.skip
        def test_correlate_data(self):
            # if DEBUG: logger.debug(f"test_correlate_data(self={self})")
            correlate_data(dataframe=self.cwap_df, target_list=["SPXL", "SPXS", "YINN", "YANG"], shift_period=3)

        @unittest.skip
        def test_plt_all_columns_from_dataframe(self):
            # if DEBUG: logger.debug(f"test_plt_all_columns_from_dataframe(self={self})")
            plt_all_columns_from_dataframe(dataframe=self.sc_cwap_df)

        @unittest.skip
        def test_plt_savgol_filter_alt_params(self):
            # if DEBUG: logger.debug(f"test_plt_savgol_filter_alt_params()")
            plt_savgol_filter_alt_params(dataframe=self.cwap_df, win_sz_list=[7, 14], polyorder=2)

        @unittest.skip
        def test_plt_target_vs_indicator_timeseries(self):
            # if DEBUG: logger.debug(f"test_plt_target_vs_indicator_timeseries(self={self})")
            plt_target_vs_indicator_timeseries(dataframe=self.sc_cwap_df, target_list=["SPXL", "SPXS", "YINN", "YANG"], shift_period=3)

        @classmethod
        def tearDownClass(cls):
            print(f"\n-tearDown({cls})")

    unittest.main()
