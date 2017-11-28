import time
import numpy as np
import datetime
import pandas as pd


def convert_hour_to_ap(start_hour, start_min, end_hour, end_min):
    ap_start = (start_hour * 12) + start_min // 5
    ap_end = (end_hour * 12) + end_min // 5
    return ap_start, ap_end


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


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
    # et = data.groupby(['AP', 'tmc_code'])['travel_time_minutes'].agg([np.mean, percentile(95), percentile(5)])
    et = data.groupby(['tmc_code', 'AP'])['travel_time_minutes'].agg([np.mean, percentile(95), percentile(5)])
    et['extra_time'] = et['percentile_95'] - et['mean']
    time2 = time.time()
    print('Extra Time Analysis: ' + str(time2 - time1))
    return et


def create_tt_trend_analysis(data, tmc_id=None):
    """
    Function to create a travel time trend over time analysis.
    :param data: Pandas dataframe of travel time data
    :param tmc_id: List of one or more tmcs to include in trend analysis
    :return: Pandas dataframe of aggregate travel time trend data
    """
    if data is None:
        return None
    am_ap_start, am_ap_end = convert_hour_to_ap(8, 0, 9, 0)
    pm_ap_start, pm_ap_end = convert_hour_to_ap(17, 0, 18, 0)
    md_ap_start, md_ap_end = convert_hour_to_ap(10, 0, 14, 0)
    if tmc_id is not None:
        tmc_data = data[data['tmc_code'].isin(tmc_id)]
    else:
        tmc_data = data
    df_dir1_am = tmc_data[(tmc_data['AP'] >= am_ap_start) & (tmc_data['AP'] < am_ap_end)]
    df_dir1_pm = tmc_data[(tmc_data['AP'] >= pm_ap_start) & (tmc_data['AP'] < pm_ap_end)]
    df_dir1_md = tmc_data[(tmc_data['AP'] >= md_ap_start) & (tmc_data['AP'] < md_ap_end)]

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


def extract_vals(date_str):
    # print(date_str)
    date, time = date_str.split(' ')
    [hour, minute, second] = [int(val) for val in time.split(':')]
    [year, month, day] = [int(val) for val in date.split('-')]
    day_type = datetime.datetime(year, month, day).weekday()
    ap = (hour * 12) + minute // 5
    return date, year, month, day, ap, day_type


def create_columns(data, is_case_study=False):
    if is_case_study is False:
        dates, years, months, days, aps, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(weekday)
    else:
        dates, years, months, days, aps, regions, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(regions), list(weekday)

day_subset = [0, 1, 2, 3, 4, 5, 6]  # Monday = 0, ..., Sunday = 6
am_start_hour = 8
am_start_min = 0
am_end_hour = 9
am_end_min = 0
am_ap_start = (am_start_hour * 12) + am_start_min // 5
am_ap_end = (am_end_hour * 12) + am_end_min // 5
pm_start_hour = 17
pm_start_min = 0
pm_end_hour = 18
pm_end_min = 0
pm_ap_start = (pm_start_hour * 12) + pm_start_min // 5
pm_ap_end = (pm_end_hour * 12) + pm_end_min // 5
md_start_hour = 10
md_start_min = 0
md_end_hour = 14
md_end_min = 0
md_ap_start = (md_start_hour * 12) + md_start_min // 5
md_ap_end = (md_end_hour * 12) + md_end_min // 5

# am_peak_str = datetime.datetime(am_start_hour, am_start_min, 0).strftime('%I:%M%p') + '-' + datetime.datetime(am_end_hour, am_end_min, 0).strftime('%I:%M%p')
# pm_peak_str = datetime.datetime(pm_start_hour, pm_start_min, 0).strftime('%I:%M%p') + '-' + datetime.datetime(pm_end_hour, pm_end_min, 0).strftime('%I:%M%p')
# md_peak_str = datetime.datetime(md_start_hour, md_start_min, 0).strftime('%I:%M%p') + '-' + datetime.datetime(md_end_hour, md_end_min, 0).strftime('%I:%M%p')

tmc = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_2016_AllDays/TMC_Identification.csv')
df = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_2016_AllDays/I95_PA_2016_AllDays.csv')

df = df[df.travel_time_minutes.notnull()]

dirs = tmc['direction'].unique()
tmc_subset1 = tmc[tmc['direction'] == dirs[0]]['tmc']
df_dir1 = df[df['tmc_code'].isin(tmc_subset1)]
facility_len1 = tmc[tmc['direction'] == dirs[0]].miles.sum()
if len(dirs) > 1:
    tmc_subset2 = tmc[tmc['direction'] == dirs[1]]['tmc']
    df_dir2 = df[df['tmc_code'].isin(tmc_subset2)]
    facility_len2 = tmc[tmc['direction'] == dirs[1]].miles.sum()


# Creating data for direction #1
time1 = time.time()
new_mat = [extract_vals(dStr) for dStr in df_dir1['measurement_tstamp']]
time2 = time.time()
print('Mat Creation: ' + str(time2 - time1))
time1 = time.time()
df_dir1['Date'], df_dir1['Year'], df_dir1['Month'], df_dir1['Day'], df_dir1['AP'], df_dir1['weekday'] = create_columns(new_mat)
start_date = df_dir1['Date'].min()
end_date = df_dir1['Date'].max()
df_dir1['Hour'] = df_dir1['AP'] // 12
time2 = time.time()
print('df_dir1 Creation: '+str(time2-time1))

# Creating data for direction #2
if len(dirs) > 1:
    time1 = time.time()
    new_mat2 = [extract_vals(dStr) for dStr in df_dir2['measurement_tstamp']]
    time2 = time.time()
    print('Mat Creation: ' + str(time2 - time1))
    time1 = time.time()
    df_dir2['Date'], df_dir2['Year'], df_dir2['Month'], df_dir2['Day'], df_dir2['AP'], df_dir2['weekday'] = create_columns(new_mat2)
    start_date = df_dir2['Date'].min()
    end_date = df_dir2['Date'].max()
    df_dir2['Hour'] = df_dir2['AP'] // 12
    time2 = time.time()
    print('df_dir2 Creation: '+str(time2-time1))

tt_trend_data1 = create_tt_trend_analysis(df_dir1, [tmc['tmc'][0]])
tt_trend_data1.to_csv('tt_trend_data.csv')
et_data1 = create_et_analysis(df_dir1)
extra_time = pd.DataFrame()
extra_time['mean'] = et_data1['mean'][tmc['tmc'][0]]
extra_time['percentile_95'] = et_data1['percentile_95'][tmc['tmc'][0]]
extra_time['percentile_5'] = et_data1['percentile_5'][tmc['tmc'][0]]
extra_time['extra_time'] = et_data1['extra_time'][tmc['tmc'][0]]
extra_time.to_csv('extra_time_data.csv')

