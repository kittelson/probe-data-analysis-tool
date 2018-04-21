"""
Module that houses various statistical and data aggregation functions for the tool.
"""

import numpy as np
import pandas as pd
import time
import DataHelper

BIN1 = 15
BIN2 = 30
BIN3 = 45
BIN4 = 60


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


def create_speed_band_analysis(data):
    sb = data.groupby(['AP', DataHelper.Project.ID_DATA_TMC])[DataHelper.Project.ID_DATA_TT].agg(
        [np.mean, percentile(95), percentile(90), percentile(80), percentile(70), percentile(60), percentile(50), percentile(5)]
    ).groupby(level=0).sum()

    return sb


def create_tt_analysis(data):
    tt = data.groupby(['AP', DataHelper.Project.ID_DATA_TMC])[DataHelper.Project.ID_DATA_TT].agg(
        [np.mean, percentile(95), percentile(90), percentile(80), percentile(70), percentile(60), percentile(50), percentile(5)]
    ).groupby(level=0).sum()
    tt['extra_time'] = tt['percentile_95']-tt['mean']
    return tt


def create_et_analysis_deprecated(data):
    """
    Deprecated function to create extra-time analysis for a dataframe. No longer used as it incorrectly aggregates by TMC last
    :param data: pandas dataframe with AP, tmc_code, and travel_time (minutes or seconds)
    :return: pandas data frame with extra time analysis
    """
    if data is None:
        return None
    if not data.columns.contains(DataHelper.Project.ID_DATA_TT):
        data[DataHelper.Project.ID_DATA_TT] = data['travel_time_seconds']/60
    time1 = time.time()
    et = data.groupby(['AP', DataHelper.Project.ID_DATA_TMC])[DataHelper.Project.ID_DATA_TT].agg([np.mean, percentile(95), percentile(5)]).groupby(level=0).sum()
    et['extra_time'] = et['percentile_95'] - et['mean']
    time2 = time.time()
    print('Extra Time Analysis: ' + str(time2 - time1))
    return et


def create_et_analysis(data):
    """
    Function to create an Extra-Time analysis for a dataframe.
    :param data: pandas dataframe with AP, tmc_code, and travel_time (minutes or seconds)
    :return: pandas data frame with extra time analysis
    """
    if data is None:
        return None
    if not data.columns.contains(DataHelper.Project.ID_DATA_TT):
        data[DataHelper.Project.ID_DATA_TT] = data['travel_time_seconds']/60
    time1 = time.time()
    et = data.groupby([DataHelper.Project.ID_DATA_TMC, 'AP'])[DataHelper.Project.ID_DATA_TT].agg([np.mean, percentile(95), percentile(5)])
    et['extra_time'] = et['percentile_95'] - et['mean']
    time2 = time.time()
    print('Extra Time Analysis: ' + str(time2 - time1))
    return et


def create_facility_et_analysis(data):
    """
    Function to create tan Extra-Time analysis for a dataframe.  
    Creates the analyis based on the "instantaneous" travel time across a facility or subset of tmcs included in dataframe.
    :param data: pandas dataframe with AP, tmc_code, and travel_time (minutes or seconds)
    :return: pandas data frame with extra time analysis
    """
    if data is None:
        return None
    if not data.columns.contains(DataHelper.Project.ID_DATA_TT):
        data[DataHelper.Project.ID_DATA_TT] = data['travel_time_seconds']/60
    time1 = time.time()
    et = data.groupby(['Date', 'AP', DataHelper.Project.ID_DATA_TMC])[DataHelper.Project.ID_DATA_TT].agg(np.mean)
    et = et.groupby(['Date', 'AP']).agg(np.sum)
    et = et.groupby(['AP']).agg([np.mean, percentile(95), percentile(5)])  # .groupby(level=0).sum()
    et['extra_time'] = et['percentile_95'] - et['mean']
    time2 = time.time()
    print('Extra Time Analysis: ' + str(time2 - time1))
    return et


def create_trend_analysis(data, am_ap, pm_ap, mid_ap, tmc_list=None, day_list=None):
    """
    Function to create a travel time trend over time analysis.
    :param data: Pandas dataframe of travel time data
    :param am_ap: List of first/last analysis periods representing AM Peak
    :param pm_ap: List of first/last analysis periods representing PM Peak
    :param mid_ap: List of first/last analysis periods representing midday Peak
    :param tmc_list: List of one or more tmcs to include in trend analysis
    :param day_list: LIst of the days of week to include in trend analysis (Mon: 0, Tue: 1, etc.)
    :return: Pandas dataframe of aggregate travel time trend data
    """
    if data is None:
        return None

    am_ap_start = am_ap[0]
    am_ap_end = am_ap[1]
    pm_ap_start = pm_ap[0]
    pm_ap_end = pm_ap[1]
    md_ap_start = mid_ap[0]
    md_ap_end = mid_ap[1]

    if tmc_list is not None:
        tmc_data = data[data[DataHelper.Project.ID_DATA_TMC].isin(tmc_list)]
    else:
        tmc_data = data
    if day_list is not None:
        filter_df = tmc_data[tmc_data['weekday'].isin(day_list)]
    else:
        filter_df = tmc_data

    df_dir1_am = filter_df[(filter_df['AP'] >= am_ap_start) & (filter_df['AP'] < am_ap_end)]
    df_dir1_pm = filter_df[(filter_df['AP'] >= pm_ap_start) & (filter_df['AP'] < pm_ap_end)]
    df_dir1_md = filter_df[(filter_df['AP'] >= md_ap_start) & (filter_df['AP'] < md_ap_end)]

    # AM Peak Period
    am_gp2 = df_dir1_am.groupby(['Year', 'Month'])[DataHelper.Project.ID_DATA_SPEED, DataHelper.Project.ID_DATA_TT].agg([np.mean, percentile(95), percentile(5)])

    # PM Peak Period
    pm_gp2 = df_dir1_pm.groupby(['Year', 'Month'])[DataHelper.Project.ID_DATA_SPEED, DataHelper.Project.ID_DATA_TT].agg([np.mean, percentile(95), percentile(5)])

    # Midday Period
    md_gp2 = df_dir1_md.groupby(['Year', 'Month'])[DataHelper.Project.ID_DATA_SPEED, DataHelper.Project.ID_DATA_TT].agg([np.mean, percentile(95), percentile(5)])

    plot_df_dir1 = pm_gp2.join(am_gp2, lsuffix='pm')
    plot_df_dir1 = md_gp2.join(plot_df_dir1, lsuffix='mid')
    return plot_df_dir1


def create_tt_compare(data_before, data_after):
    deltas = pd.DataFrame()
    deltas['delta_50'] = data_before['percentile_50'] - data_after['percentile_50']
    deltas['delta_60'] = data_before['percentile_60'] - data_after['percentile_60']
    deltas['delta_70'] = data_before['percentile_70'] - data_after['percentile_70']
    deltas['delta_80'] = data_before['percentile_80'] - data_after['percentile_80']
    deltas['delta_90'] = data_before['percentile_90'] - data_after['percentile_90']
    deltas['delta_95'] = data_before['percentile_95'] - data_after['percentile_95']
    return deltas


def create_pct_congested_sp(data, selected_tmc_list, speed_bins, dates=None, aps=None):

    bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
    # Filtering data
    data = data[data[DataHelper.Project.ID_DATA_TMC].isin(selected_tmc_list)]
    if dates is not None and len(dates) == 2:
        data = data[(data['Date'] >= dates[0]) & (data['Date'] <= dates[1])]
    if aps is not None and len(aps) == 2:
        data = data[(data['AP'] >= aps[0]) & (data['AP'] < aps[1])]
    # Aggregating data
    # data[bin_list[0]] = data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[0]
    data[bin_list[0]] = (data[DataHelper.Project.ID_DATA_SPEED] >= speed_bins[0]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[1])
    data[bin_list[1]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[1]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[2])
    data[bin_list[2]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[2]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[3])
    data[bin_list[3]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[3]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[4])
    data[bin_list[4]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[4])
    # sp_pct_con = data.groupby(['Year', 'Month', 'Day', 'Hour', 'AP', DataHelper.Project.ID_DATA_TMC])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
    # sp_pct_con1 = sp_pct_con.groupby(['Year', 'Month', 'Day']).agg(np.sum)
    sp_pct_con1 = data.groupby(['Year', 'Month', 'Day'])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
    sp_pct_con1['bin_sum'] = sp_pct_con1[bin_list].sum(axis=1)
    sp_pct_con1 = sp_pct_con1[bin_list].div(sp_pct_con1['bin_sum'], axis=0)

    return sp_pct_con1


def create_pct_congested_tmc(data, speed_bins, times=None, dates=None, tmc_index_list=None):
    bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
    # Potential data filtering her
    if dates is not None and len(dates) == 2:
        data = data[(data['Date'] >= dates[0]) & (data['Date'] <= dates[1])]
    if times is not None and len(times) == 2:
        ap_start = times[0]
        ap_end = times[1]
        data = data[(data['AP'] >= ap_start) & (data['AP'] < ap_end)]
    # data[bin_list[0]] = data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[0]
    data[bin_list[0]] = (data[DataHelper.Project.ID_DATA_SPEED] >= speed_bins[0]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[1])
    data[bin_list[1]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[1]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[2])
    data[bin_list[2]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[2]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[3])
    data[bin_list[3]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[3]) & (data[DataHelper.Project.ID_DATA_SPEED] <= speed_bins[4])
    data[bin_list[4]] = (data[DataHelper.Project.ID_DATA_SPEED] > speed_bins[4])
    # tmc_gp = data.groupby(['Year', 'Month', 'Day', 'Hour', 'AP', DataHelper.Project.ID_DATA_TMC])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
    # tmc_gp1 = tmc_gp.groupby([DataHelper.Project.ID_DATA_TMC]).agg(np.sum)
    tmc_gp1 = data.groupby([DataHelper.Project.ID_DATA_TMC])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
    tmc_gp1['bin_sum'] = tmc_gp1[bin_list].sum(axis=1)
    tmc_gp1 = tmc_gp1[bin_list].div(tmc_gp1['bin_sum'], axis=0)
    if tmc_index_list is not None:
        tmc_gp1 = tmc_gp1.reindex(tmc_index_list)
    return tmc_gp1


def create_speed_heatmap(data, tmc_id, stacked=False):
    tmc = data[data[DataHelper.Project.ID_DATA_TMC].isin([tmc_id])]
    test = tmc.groupby(['Date', 'AP'])[DataHelper.Project.ID_DATA_SPEED].agg(np.mean)
    df_mat = test.to_frame()
    imshow_data = df_mat.unstack().values[:, :]
    imshow_data = imshow_data.T
    if stacked:
        imshow_data.sort(axis=1)
    return imshow_data


def create_speed_tmc_heatmap(data, period, tmc_index_list, stacked=False):
    tmc = data[(data['AP'] >= period[0]) & (data['AP'] <= period[1])]
    test = tmc.groupby(['Date', DataHelper.Project.ID_DATA_TMC])[DataHelper.Project.ID_DATA_SPEED].agg(np.mean)
    df_mat = test.to_frame()
    # print(df_mat)
    if tmc_index_list is not None:
        df_mat = df_mat.reindex(tmc_index_list, level=1)
    imshow_data = df_mat.unstack().values[:, :]
    imshow_data = imshow_data.T
    if stacked:
        imshow_data.sort(axis=1)
    return imshow_data


def create_speed_band(data):
    """
    Function to create an Extra-Time analysis for a dataframe.
    :param data: pandas dataframe with AP, tmc_code, and travel_time (minutes or seconds)
    :return: pandas data frame with extra time analysis
    """
    if data is None:
        return None
    time1 = time.time()
    sb = data.groupby([DataHelper.Project.ID_DATA_TMC, 'AP'])[DataHelper.Project.ID_DATA_SPEED].agg([np.mean, percentile(95), percentile(5)])
    time2 = time.time()
    print('Speed Band Analysis: ' + str(time2 - time1))
    return sb


def create_travel_time_cdf(data):
    if data is None:
        return None
    time1 = time.time()
    tt_cdf = data.groupby(DataHelper.Project.ID_DATA_TMC).apply(pd.DataFrame.sort_values, DataHelper.Project.ID_DATA_TT)
    time2 = time.time()
    print('TT CDF Analysis: ' + str(time2 - time1))
    return tt_cdf


def create_speed_cdf(data):
    if data is None:
        return None
    time1 = time.time()
    sp_cdf = data.groupby(DataHelper.Project.ID_DATA_TMC).apply(pd.DataFrame.sort_values, DataHelper.Project.ID_DATA_SPEED)
    time2 = time.time()
    print('Speed CDF Analysis: ' + str(time2 - time1))
    return sp_cdf


def create_speed_freq(data):
    # if data is None:
    #     return None
    # time1 = time.time()
    # speed_freq = data.groupby([DataHelper.Project.ID_DATA_TMC, pd.cut(data.speed, [el for el in range(80)])]).size().unstack()
    # time2 = time.time()
    # print('Speed Freq Analysis: ' + str(0.0))
    return None


def create_dq_weekday(data, data_res):
    print(data_res)
    num_tmc = len(data[DataHelper.Project.ID_DATA_TMC].unique())
    td_facility_Wkdy = data.groupby(['weekday', 'Date']).agg(['count'])[DataHelper.Project.ID_DATA_SPEED] / ((24 * 60 / data_res) * num_tmc)
    td1_facility_Wkdy = td_facility_Wkdy.groupby(['weekday']).agg(np.mean)
    return td1_facility_Wkdy


def create_dq_time_of_day(data, data_res):
    num_tmc = len(data[DataHelper.Project.ID_DATA_TMC].unique())
    num_dates = len(data['Date'].unique())
    td_facility_ToD = data.groupby(['Hour']).agg(['count'])
    td1_facility_ToD = td_facility_ToD[DataHelper.Project.ID_DATA_SPEED]['count'] / (60 / data_res * num_dates * num_tmc)
    return td1_facility_ToD


def create_dq_tmc(data, data_res, tmc_index=None):
    num_tmc = len(data[DataHelper.Project.ID_DATA_TMC].unique())
    num_dates = len(data['Date'].unique())
    td_facility_TMC = data.groupby([DataHelper.Project.ID_DATA_TMC]).agg(['count'])
    td1_facility_TMC = td_facility_TMC[DataHelper.Project.ID_DATA_SPEED]['count'] / ((24 * 60 / data_res) * num_dates)
    if tmc_index is not None:
        td1_facility_TMC = td1_facility_TMC.reindex(tmc_index[DataHelper.Project.ID_TMC_CODE])
    return td1_facility_TMC


def create_dq_study_period(data, data_res, day_list=None):
    num_tmc = len(data[DataHelper.Project.ID_DATA_TMC].unique())
    if day_list is not None:
        wd = data[data['weekday'].isin(day_list)].groupby(['Year', 'Month', 'Date']).agg(['count'])[DataHelper.Project.ID_DATA_SPEED] / ((24 * 60 / data_res) * num_tmc)
    else:
        wd = data.groupby(['Year', 'Month', 'Date']).agg(['count'])[DataHelper.Project.ID_DATA_SPEED] / ((24 * 60 / data_res) * num_tmc)
    wdv = wd.groupby(['Year', 'Month']).agg(np.mean)
    y_wd = wdv.values.reshape((wdv.shape[0],))
    return y_wd


def convert_time_to_ap(start_hour, start_min, ap_increment):
    return (start_hour * (60 // ap_increment)) + start_min // ap_increment

