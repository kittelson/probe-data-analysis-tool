"""
Module that houses various statistical and data aggregation functions for the tool.
"""

import numpy as np
import pandas as pd
import time

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
    sb = data.groupby(['AP', 'tmc_code'])['travel_time_minutes'].agg(
        [np.mean, percentile(95), percentile(90), percentile(80), percentile(70), percentile(60), percentile(50), percentile(5)]
    ).groupby(level=0).sum()

    return sb


def create_tt_analysis(data):
    tt = data.groupby(['AP', 'tmc_code'])['travel_time_minutes'].agg(
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
    if not data.columns.contains('travel_time_minutes'):
        data['travel_time_minutes'] = data['travel_time_seconds']/60
    time1 = time.time()
    et = data.groupby(['AP', 'tmc_code'])['travel_time_minutes'].agg([np.mean, percentile(95), percentile(5)]).groupby(level=0).sum()
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
    if not data.columns.contains('travel_time_minutes'):
        data['travel_time_minutes'] = data['travel_time_seconds']/60
    time1 = time.time()
    et = data.groupby(['Date', 'AP', 'tmc_code'])['travel_time_minutes'].agg(np.mean)
    et = et.groupby(['Date', 'AP']).agg(np.sum)
    et = et.groupby(['AP']).agg([np.mean, percentile(95), percentile(5)])  # .groupby(level=0).sum()
    et['extra_time'] = et['percentile_95'] - et['mean']
    time2 = time.time()
    print('Extra Time Analysis: ' + str(time2 - time1))
    return et


def create_timetime_analysis_deprecated(data):
    """
    Function to create a travel time trenc over time analysis.  Deprecated as it incorrectly aggregates by TMC last.
    :param data: 
    :return: 
    """
    if data is None:
        return None
    am_ap_start, am_ap_end = convert_hour_to_ap(8, 0, 9, 0)
    pm_ap_start, pm_ap_end = convert_hour_to_ap(17, 0, 18, 0)
    md_ap_start, md_ap_end = convert_hour_to_ap(10, 0, 14, 0)

    df_dir1_am = data[(data['AP'] >= am_ap_start) & (data['AP'] < am_ap_end)]
    df_dir1_pm = data[(data['AP'] >= pm_ap_start) & (data['AP'] < pm_ap_end)]
    df_dir1_md = data[(data['AP'] >= md_ap_start) & (data['AP'] < md_ap_end)]

    # AM Peak Period
    am_gp0 = df_dir1_am.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
    am_num_observations = am_gp0.count()
    # am_num_observations.groupby(['Year', 'Month']).agg(np.mean)
    am_gp = am_gp0.agg([np.mean, percentile(95), percentile(5)])
    am_gp1 = am_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
    am_gp2 = am_gp1.groupby(['Year', 'Month']).agg(np.mean)

    # PM Peak Period
    pm_gp0 = df_dir1_pm.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
    pm_num_observations = pm_gp0.count()
    # Pm_num_observations.groupby(['Year', 'Month']).agg(np.mean)
    pm_gp = pm_gp0.agg([np.mean, percentile(95), percentile(5)])
    pm_gp1 = pm_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
    pm_gp2 = pm_gp1.groupby(['Year', 'Month']).agg(np.mean)

    # Midday Period
    md_gp0 = df_dir1_md.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
    md_num_observations = md_gp0.count()
    # md_num_observations.groupby(['Year', 'Month']).agg(np.mean)
    md_gp = md_gp0.agg([np.mean, percentile(95), percentile(5)])
    md_gp1 = md_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
    md_gp2 = md_gp1.groupby(['Year', 'Month']).agg(np.mean)

    plot_df_dir1 = am_gp2.join(pm_gp2, lsuffix='pm')
    plot_df_dir1 = plot_df_dir1.join(md_gp2, lsuffix='mid')
    return plot_df_dir1


def create_timetime_analysis(data):
    """
    Function to create a travel time trend over time analysis.
    :param data: 
    :return: 
    """
    if data is None:
        return None
    am_ap_start, am_ap_end = convert_hour_to_ap(8, 0, 9, 0)
    pm_ap_start, pm_ap_end = convert_hour_to_ap(17, 0, 18, 0)
    md_ap_start, md_ap_end = convert_hour_to_ap(10, 0, 14, 0)

    df_dir1_am = data[(data['AP'] >= am_ap_start) & (data['AP'] < am_ap_end)]
    df_dir1_pm = data[(data['AP'] >= pm_ap_start) & (data['AP'] < pm_ap_end)]
    df_dir1_md = data[(data['AP'] >= md_ap_start) & (data['AP'] < md_ap_end)]

    # AM Peak Period
    am_gp0 = df_dir1_am.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
    am_num_observations = am_gp0.count()
    # am_num_observations.groupby(['Year', 'Month']).agg(np.mean)
    am_gp = am_gp0.agg(np.mean)
    am_gp1 = am_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
    am_gp2 = am_gp1.groupby(['Year', 'Month']).agg([np.mean, percentile(95), percentile(5)])

    # PM Peak Period
    pm_gp0 = df_dir1_pm.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
    pm_num_observations = pm_gp0.count()
    # Pm_num_observations.groupby(['Year', 'Month']).agg(np.mean)
    pm_gp = pm_gp0.agg(np.mean)
    pm_gp1 = pm_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
    pm_gp2 = pm_gp1.groupby(['Year', 'Month']).agg([np.mean, percentile(95), percentile(5)])

    # Midday Period
    md_gp0 = df_dir1_md.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
    md_num_observations = md_gp0.count()
    # md_num_observations.groupby(['Year', 'Month']).agg(np.mean)
    md_gp = md_gp0.agg(np.mean)
    md_gp1 = md_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
    md_gp2 = md_gp1.groupby(['Year', 'Month']).agg([np.mean, percentile(95), percentile(5)])

    plot_df_dir1 = am_gp2.join(pm_gp2, lsuffix='pm')
    plot_df_dir1 = plot_df_dir1.join(md_gp2, lsuffix='mid')
    return plot_df_dir1


def convert_hour_to_ap(start_hour, start_min, end_hour, end_min):
    ap_start = (start_hour * 12) + start_min // 5
    ap_end = (end_hour * 12) + end_min // 5
    return ap_start, ap_end


def create_tt_compare(data_before, data_after):
    deltas = pd.DataFrame()
    deltas['delta_50'] = data_before['percentile_50'] - data_after['percentile_50']
    deltas['delta_60'] = data_before['percentile_60'] - data_after['percentile_60']
    deltas['delta_70'] = data_before['percentile_70'] - data_after['percentile_70']
    deltas['delta_80'] = data_before['percentile_80'] - data_after['percentile_80']
    deltas['delta_90'] = data_before['percentile_90'] - data_after['percentile_90']
    deltas['delta_95'] = data_before['percentile_95'] - data_after['percentile_95']
    return deltas


def create_pct_congested_sp(data, speed_bins, dates=[]):

    bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
    # Potential data filtering her
    if len(dates) == 2:
        data = data[(data['Date'] >= dates[0]) & (data['Date'] <= dates[1])]
    # Aggregating data
    # data[bin_list[0]] = data['speed'] <= speed_bins[0]
    data[bin_list[0]] = (data['speed'] >= speed_bins[0]) & (data['speed'] <= speed_bins[1])
    data[bin_list[1]] = (data['speed'] > speed_bins[1]) & (data['speed'] <= speed_bins[2])
    data[bin_list[2]] = (data['speed'] > speed_bins[2]) & (data['speed'] <= speed_bins[3])
    data[bin_list[3]] = (data['speed'] > speed_bins[3]) & (data['speed'] <= speed_bins[4])
    data[bin_list[4]] = (data['speed'] > speed_bins[4])
    sp_pct_con = data.groupby(['Year', 'Month', 'Day', 'Hour', 'AP', 'tmc_code'])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
    # sp_pct_con1 = sp_pct_con.groupby(['Year', 'Month', 'Day', 'Hour']).agg(np.sum)
    sp_pct_con1 = sp_pct_con.groupby(['Year', 'Month', 'Day']).agg(np.sum)
    sp_pct_con1['bin_sum'] = sp_pct_con1[bin_list].sum(axis=1)
    sp_pct_con1 = sp_pct_con1[bin_list].div(sp_pct_con1['bin_sum'], axis=0)

    return sp_pct_con1


def create_pct_congested_tmc(data, speed_bins, times=None, dates=None):
    bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
    # Potential data filtering her
    if dates is not None and len(dates) == 2:
        data = data[(data['Date'] >= dates[0]) & (data['Date'] <= dates[1])]
    if times is not None and len(times) == 2:
        ap_start, ap_end = convert_hour_to_ap(times[0].hour, times[0].minute, times[1].hour, times[1].minute)
        data = data[(data['AP'] >= ap_start) & (data['AP'] < ap_end)]
    # data[bin_list[0]] = data['speed'] <= speed_bins[0]
    data[bin_list[0]] = (data['speed'] >= speed_bins[0]) & (data['speed'] <= speed_bins[1])
    data[bin_list[1]] = (data['speed'] > speed_bins[1]) & (data['speed'] <= speed_bins[2])
    data[bin_list[2]] = (data['speed'] > speed_bins[2]) & (data['speed'] <= speed_bins[3])
    data[bin_list[3]] = (data['speed'] > speed_bins[3]) & (data['speed'] <= speed_bins[4])
    data[bin_list[4]] = (data['speed'] > speed_bins[4])
    tmc_gp = data.groupby(['Year', 'Month', 'Day', 'Hour', 'AP', 'tmc_code'])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
    tmc_gp1 = tmc_gp.groupby(['tmc_code']).agg(np.sum)
    tmc_gp1['bin_sum'] = tmc_gp1[bin_list].sum(axis=1)
    tmc_gp1 = tmc_gp1[bin_list].div(tmc_gp1['bin_sum'], axis=0)
    return tmc_gp1


def create_speed_heatmap(data, tmc_id):
    tmc = data[data['tmc_code'].isin([tmc_id])]
    test = tmc.groupby(['Date', 'AP'])['speed'].agg(np.mean)
    df_mat = test.to_frame()
    imshow_data = df_mat.unstack().values[:, :]
    imshow_data = imshow_data.T
    return imshow_data


def create_speed_tmc_heatmap(data, period):
    tmc = data[(data['AP'] >= period[0]) & (data['AP'] <= period[1])]
    test = tmc.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
    df_mat = test.to_frame()
    imshow_data = df_mat.unstack().values[:, :]
    imshow_data = imshow_data.T
    return imshow_data


def convert_time_to_ap(start_hour, start_min, ap_increment):
    return (start_hour * 12) + start_min // ap_increment

