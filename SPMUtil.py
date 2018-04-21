import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from viz_qt import extract_vals, create_columns
from matplotlib.ticker import FuncFormatter
import calendar
from datetime import datetime, timedelta
from datetime import time as dtime

extract_subset = True
subset_1 = 10
subset_2 = 20
write_files = True
div_name = 'Division_2'


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_

# 1, 1, 6
# 2, 3, 15
# 3, 6, 10
# 4, 1, 5
# 5, 3, 4
cs_idx = 4
tmc_1_idx = 1
tmc_2_idx = 5
# main_title = 'Daily Speeds over Time: US-1 (Capital Blvd) - Wake Forest, NC'
# main_title = 'Peak Period Speeds by TMC: Case Study ' + str(cs_idx)
main_title = 'Peak Period Speeds by TMC: TX-161'

day_subset = [0, 1, 2, 3, 4, 5, 6]  # Monday = 0, ..., Sunday = 6
am_start_hour = 6
am_start_min = 0
am_end_hour = 9
am_end_min = 0
am_ap_start = (am_start_hour * 12) + am_start_min // 5
am_ap_end = (am_end_hour * 12) + am_end_min // 5
pm_start_hour = 16
pm_start_min = 0
pm_end_hour = 19
pm_end_min = 0
pm_ap_start = (pm_start_hour * 12) + pm_start_min // 5
pm_ap_end = (pm_end_hour * 12) + pm_end_min // 5
md_start_hour = 10
md_start_min = 0
md_end_hour = 15
md_end_min = 0
md_ap_start = (md_start_hour * 12) + md_start_min // 5
md_ap_end = (md_end_hour * 12) + md_end_min // 5

am_peak_str = dtime(am_start_hour, am_start_min, 0).strftime('%I:%M%p') + '-' + dtime(am_end_hour, am_end_min, 0).strftime('%I:%M%p')
pm_peak_str = dtime(pm_start_hour, pm_start_min, 0).strftime('%I:%M%p') + '-' + dtime(pm_end_hour, pm_end_min, 0).strftime('%I:%M%p')
md_peak_str = dtime(md_start_hour, md_start_min, 0).strftime('%I:%M%p') + '-' + dtime(md_end_hour, md_end_min, 0).strftime('%I:%M%p')

tmc_path = 'TMC_Identification.csv'

# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_AllDays_NPMRDS/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_AllDays_NPMRDS/I66_EB_AllDays_NPMRDS.csv')
# tmc = pd.read_csv('C:/Users/ltrask/PycharmProjects/NPMRDS_Data_Tool/I-66_Test/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/PycharmProjects/NPMRDS_Data_Tool/I-66_Test/I-66_Test.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/21383 - NCDOT SPM/Interface/SpeedData/SingleTMC_3Years/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/21383 - NCDOT SPM/Interface/SpeedData/SingleTMC_3Years/SingleTMC_3Years.csv')
tmc = pd.read_csv('C:/Users/ltrask/Documents/21383 - NCDOT SPM/Interface/SpeedData/System_3Years/' + tmc_path)
df = pd.read_csv('C:/Users/ltrask/Documents/21383 - NCDOT SPM/Interface/SpeedData/System_3Years/System_3Years.csv')
#C:\Users\ltrask\Documents\21383 - NCDOT SPM\Interface\SpeedData\SingleTMC_3Years

df = df[df.travel_time_minutes.notnull()]

if extract_subset:
    tmc.sort_values('tmc')
    tmc_subset = tmc['tmc'].values[subset_1:subset_2]
    tmc = tmc[tmc['tmc'].isin(tmc_subset)]
    df = df[df['tmc_code'].isin(tmc_subset)]

# dirs = tmc['direction'].unique()
# tmc_subset1 = tmc[tmc['direction'] == dirs[0]]['tmc']
# df_dir1 = df[df['tmc_code'].isin(tmc_subset1)]
# facility_len1 = tmc[tmc['direction'] == dirs[0]].miles.sum()

# Creating data for direction #1
time1 = time.time()
new_mat = [extract_vals(dStr) for dStr in df['measurement_tstamp']]
time2 = time.time()
print('Mat Creation: ' + str(time2 - time1))
time1 = time.time()
df['Date'], df['Year'], df['Month'], df['Day'], df['AP'], df['weekday'] = create_columns(new_mat)
start_date = df['Date'].min()
end_date = df['Date'].max()
df['Hour'] = df['AP'] // 12
time2 = time.time()
print('df_dir1 Creation: '+str(time2-time1))


df_wkdy = df[df['weekday'].isin([0, 1, 2, 3, 4])]
df_wknd = df[df['weekday'].isin([5, 6])]
# tmc_data = df[df['tmc_code'] == tmc['tmc'][0]]
tmc['TT_FF'] = tmc['miles'] / 40.0 * 60

# Splitting into time periods
df_am = df_wkdy[(df_wkdy['AP'] >= am_ap_start) & (df_wkdy['AP'] < am_ap_end)]
df_pm = df_wkdy[(df_wkdy['AP'] >= pm_ap_start) & (df_wkdy['AP'] < pm_ap_end)]
df_md = df_wkdy[(df_wkdy['AP'] >= md_ap_start) & (df_wkdy['AP'] < md_ap_end)]
df_we = df_wknd[(df_wknd['AP'] >= md_ap_start) & (df_wknd['AP'] < md_ap_end)]

# Aggregation by Year
am_sys = df_am.groupby(['Year', 'Month', 'measurement_tstamp']).sum()
md_sys = df_md.groupby(['Year', 'Month', 'measurement_tstamp']).sum()
pm_sys = df_pm.groupby(['Year', 'Month', 'measurement_tstamp']).sum()
we_sys = df_we.groupby(['Year', 'Month', 'measurement_tstamp']).sum()
am_sys_month = am_sys.groupby(['Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
md_sys_month = md_sys.groupby(['Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
pm_sys_month = pm_sys.groupby(['Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
we_sys_month = we_sys.groupby(['Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])

# Travel Time Metric
am_sys_month['TT_FF'] = tmc['TT_FF'].sum()
am_sys_month['NTT'] = am_sys_month['travel_time_minutes']['mean'] / am_sys_month['TT_FF']
am_sys_month['IQR'] = am_sys_month['travel_time_minutes']['percentile_75'] / am_sys_month['TT_FF'] - am_sys_month['travel_time_minutes']['percentile_25'] / am_sys_month['TT_FF']
am_sys_month['IQR'] = am_sys_month['IQR'] * 100
am_sys_month['LOTTR'] = am_sys_month['travel_time_minutes']['percentile_80'] / am_sys_month['travel_time_minutes']['percentile_50']
md_sys_month['TT_FF'] = tmc['TT_FF'].sum()
md_sys_month['NTT'] = md_sys_month['travel_time_minutes']['mean'] / md_sys_month['TT_FF']
md_sys_month['IQR'] = md_sys_month['travel_time_minutes']['percentile_75']/ md_sys_month['TT_FF'] - md_sys_month['travel_time_minutes']['percentile_25'] / md_sys_month['TT_FF']
md_sys_month['IQR'] = md_sys_month['IQR'] * 100
md_sys_month['LOTTR'] = md_sys_month['travel_time_minutes']['percentile_80'] / md_sys_month['travel_time_minutes']['percentile_50']
pm_sys_month['TT_FF'] = tmc['TT_FF'].sum()
pm_sys_month['NTT'] = pm_sys_month['travel_time_minutes']['mean'] / pm_sys_month['TT_FF']
pm_sys_month['IQR'] = pm_sys_month['travel_time_minutes']['percentile_75'] / pm_sys_month['TT_FF'] - pm_sys_month['travel_time_minutes']['percentile_25'] / pm_sys_month['TT_FF']
pm_sys_month['IQR'] = pm_sys_month['IQR'] * 100
pm_sys_month['LOTTR'] = pm_sys_month['travel_time_minutes']['percentile_80'] / pm_sys_month['travel_time_minutes']['percentile_50']
we_sys_month['TT_FF'] = tmc['TT_FF'].sum()
we_sys_month['NTT'] = we_sys_month['travel_time_minutes']['mean'] / we_sys_month['TT_FF']
we_sys_month['IQR'] = we_sys_month['travel_time_minutes']['percentile_75'] / we_sys_month['TT_FF'] - we_sys_month['travel_time_minutes']['percentile_25'] / we_sys_month['TT_FF']
we_sys_month['IQR'] = we_sys_month['IQR'] * 100
we_sys_month['LOTTR'] = we_sys_month['travel_time_minutes']['percentile_80'] / we_sys_month['travel_time_minutes']['percentile_50']

# Aggregation by Year
am_sys_year = am_sys.groupby(['Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
md_sys_year = md_sys.groupby(['Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
pm_sys_year = pm_sys.groupby(['Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
we_sys_year = we_sys.groupby(['Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])

# Travel Time Metric
am_sys_year['TT_FF'] = tmc['TT_FF'].sum()
am_sys_year['NTT'] = am_sys_year['travel_time_minutes']['mean'] / am_sys_year['TT_FF']
am_sys_year['IQR'] = am_sys_year['travel_time_minutes']['percentile_75'] / am_sys_year['TT_FF'] - am_sys_year['travel_time_minutes']['percentile_25'] / am_sys_year['TT_FF']
am_sys_year['IQR'] = am_sys_year['IQR'] * 100
am_sys_year['LOTTR'] = am_sys_year['travel_time_minutes']['percentile_80'] / am_sys_year['travel_time_minutes']['percentile_50']
md_sys_year['TT_FF'] = tmc['TT_FF'].sum()
md_sys_year['NTT'] = md_sys_year['travel_time_minutes']['mean'] / md_sys_year['TT_FF']
md_sys_year['IQR'] = md_sys_year['travel_time_minutes']['percentile_75'] / md_sys_year['TT_FF'] - md_sys_year['travel_time_minutes']['percentile_25'] / md_sys_year['TT_FF']
md_sys_year['IQR'] = md_sys_year['IQR'] * 100
md_sys_year['LOTTR'] = md_sys_year['travel_time_minutes']['percentile_80'] / md_sys_year['travel_time_minutes']['percentile_50']
pm_sys_year['TT_FF'] = tmc['TT_FF'].sum()
pm_sys_year['NTT'] = pm_sys_year['travel_time_minutes']['mean'] / pm_sys_year['TT_FF']
pm_sys_year['IQR'] = pm_sys_year['travel_time_minutes']['percentile_75'] / pm_sys_year['TT_FF'] - pm_sys_year['travel_time_minutes']['percentile_25'] / pm_sys_year['TT_FF']
pm_sys_year['IQR'] = pm_sys_year['IQR'] * 100
pm_sys_year['LOTTR'] = pm_sys_year['travel_time_minutes']['percentile_80'] / pm_sys_year['travel_time_minutes']['percentile_50']
we_sys_year['TT_FF'] = tmc['TT_FF'].sum()
we_sys_year['NTT'] = we_sys_year['travel_time_minutes']['mean'] / we_sys_year['TT_FF']
we_sys_year['IQR'] = we_sys_year['travel_time_minutes']['percentile_75'] / we_sys_year['TT_FF'] - we_sys_year['travel_time_minutes']['percentile_25'] / we_sys_year['TT_FF']
we_sys_year['IQR'] = we_sys_year['IQR'] * 100
we_sys_year['LOTTR'] = we_sys_year['travel_time_minutes']['percentile_80'] / we_sys_year['travel_time_minutes']['percentile_50']

# Aggregation by Year
am_sig_month = df_am.groupby(['tmc_code', 'Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
md_sig_month = df_pm.groupby(['tmc_code', 'Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
pm_sig_month = df_md.groupby(['tmc_code', 'Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
we_sig_month = df_we.groupby(['tmc_code', 'Year', 'Month'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])

# Travel Time Metric
for index, row in tmc.iterrows():
    am_sig_month.loc[row['tmc'], 'TT_FF'] = row['TT_FF']
    md_sig_month.loc[row['tmc'], 'TT_FF'] = row['TT_FF']
    pm_sig_month.loc[row['tmc'], 'TT_FF'] = row['TT_FF']
    we_sig_month.loc[row['tmc'], 'TT_FF'] = row['TT_FF']

    am_sig_month.loc[row['tmc'], 'miles'] = row['miles']
    md_sig_month.loc[row['tmc'], 'miles'] = row['miles']
    pm_sig_month.loc[row['tmc'], 'miles'] = row['miles']
    we_sig_month.loc[row['tmc'], 'miles'] = row['miles']

am_sig_month['NTT'] = am_sig_month['travel_time_minutes']['mean'] / am_sig_month['TT_FF']
am_sig_month['IQR'] = am_sig_month['travel_time_minutes']['percentile_75'] / am_sig_month['TT_FF'] - am_sig_month['travel_time_minutes']['percentile_25'] / am_sig_month['TT_FF']
am_sig_month['IQR'] = am_sig_month['IQR'] * 100
am_sig_month['LOTTR'] = am_sig_month['travel_time_minutes']['percentile_80'] / am_sig_month['travel_time_minutes']['percentile_50']

md_sig_month['NTT'] = md_sig_month['travel_time_minutes']['mean'] / md_sig_month['TT_FF']
md_sig_month['IQR'] = md_sig_month['travel_time_minutes']['percentile_75'] / md_sig_month['TT_FF'] - md_sig_month['travel_time_minutes']['percentile_25'] / md_sig_month['TT_FF']
md_sig_month['IQR'] = md_sig_month['IQR'] * 100
md_sig_month['LOTTR'] = md_sig_month['travel_time_minutes']['percentile_80'] / md_sig_month['travel_time_minutes']['percentile_50']

pm_sig_month['NTT'] = pm_sig_month['travel_time_minutes']['mean'] / pm_sig_month['TT_FF']
pm_sig_month['IQR'] = pm_sig_month['travel_time_minutes']['percentile_75']/ pm_sig_month['TT_FF'] - pm_sig_month['travel_time_minutes']['percentile_25'] / pm_sig_month['TT_FF']
pm_sig_month['IQR'] = pm_sig_month['IQR'] * 100
pm_sig_month['LOTTR'] = pm_sig_month['travel_time_minutes']['percentile_80'] / pm_sig_month['travel_time_minutes']['percentile_50']

we_sig_month['NTT'] = we_sig_month['travel_time_minutes']['mean'] / we_sig_month['TT_FF']
we_sig_month['IQR'] = we_sig_month['travel_time_minutes']['percentile_75'] / we_sig_month['TT_FF'] - we_sig_month['travel_time_minutes']['percentile_25'] / we_sig_month['TT_FF']
we_sig_month['IQR'] = we_sig_month['IQR'] * 100
we_sig_month['LOTTR'] = we_sig_month['travel_time_minutes']['percentile_80'] / we_sig_month['travel_time_minutes']['percentile_50']

# Aggregation by Year
am_sig_year = df_am.groupby(['tmc_code', 'Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
md_sig_year = df_md.groupby(['tmc_code', 'Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
pm_sig_year = df_pm.groupby(['tmc_code', 'Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])
we_sig_year = df_we.groupby(['tmc_code', 'Year'])['speed', 'travel_time_minutes'].agg([np.mean, percentile(80), percentile(75), percentile(50), percentile(25)])

# Travel Time Metric
for index, row in tmc.iterrows():
    am_sig_year.loc[row['tmc'], 'TT_FF'] = row['TT_FF']
    md_sig_year.loc[row['tmc'], 'TT_FF'] = row['TT_FF']
    pm_sig_year.loc[row['tmc'], 'TT_FF'] = row['TT_FF']
    we_sig_year.loc[row['tmc'], 'TT_FF'] = row['TT_FF']

    am_sig_year.loc[row['tmc'], 'miles'] = row['miles']
    md_sig_year.loc[row['tmc'], 'miles'] = row['miles']
    pm_sig_year.loc[row['tmc'], 'miles'] = row['miles']
    we_sig_year.loc[row['tmc'], 'miles'] = row['miles']

am_sig_year['NTT'] = am_sig_year['travel_time_minutes']['mean'] / am_sig_year['TT_FF']
am_sig_year['IQR'] = am_sig_year['travel_time_minutes']['percentile_75'] / am_sig_year['TT_FF'] - am_sig_year['travel_time_minutes']['percentile_25'] / am_sig_year['TT_FF']
am_sig_year['IQR'] = am_sig_year['IQR'] * 100
am_sig_year['LOTTR'] = am_sig_year['travel_time_minutes']['percentile_80'] / am_sig_year['travel_time_minutes']['percentile_50']

md_sig_year['NTT'] = md_sig_year['travel_time_minutes']['mean'] / md_sig_year['TT_FF']
md_sig_year['IQR'] = md_sig_year['travel_time_minutes']['percentile_75'] / md_sig_year['TT_FF'] - md_sig_year['travel_time_minutes']['percentile_25'] / md_sig_year['TT_FF']
md_sig_year['IQR'] = md_sig_year['IQR'] * 100
md_sig_year['LOTTR'] = md_sig_year['travel_time_minutes']['percentile_80'] / md_sig_year['travel_time_minutes']['percentile_50']

pm_sig_year['NTT'] = pm_sig_year['travel_time_minutes']['mean'] / pm_sig_year['TT_FF']
pm_sig_year['IQR'] = pm_sig_year['travel_time_minutes']['percentile_75'] / pm_sig_year['TT_FF'] - pm_sig_year['travel_time_minutes']['percentile_25'] / pm_sig_year['TT_FF']
pm_sig_year['IQR'] = pm_sig_year['IQR'] * 100
pm_sig_year['LOTTR'] = pm_sig_year['travel_time_minutes']['percentile_80'] / pm_sig_year['travel_time_minutes']['percentile_50']

we_sig_year['NTT'] = we_sig_year['travel_time_minutes']['mean'] / we_sig_year['TT_FF']
we_sig_year['IQR'] = we_sig_year['travel_time_minutes']['percentile_75']/ we_sig_year['TT_FF'] - we_sig_year['travel_time_minutes']['percentile_25'] / we_sig_year['TT_FF']
we_sig_year['IQR'] = we_sig_year['IQR'] * 100
we_sig_year['LOTTR'] = we_sig_year['travel_time_minutes']['percentile_80'] / we_sig_year['travel_time_minutes']['percentile_50']


if write_files:
    am_sys_month.to_hdf(div_name + '_month' + '.h5', 'am_sys_month')
    md_sys_month.to_hdf(div_name + '_month' + '.h5', 'md_sys_month')
    pm_sys_month.to_hdf(div_name + '_month' + '.h5', 'pm_sys_month')
    we_sys_month.to_hdf(div_name + '_month' + '.h5', 'we_sys_month')

    am_sys_year.to_hdf(div_name + '_year' + '.h5', 'am_sys_year')
    md_sys_year.to_hdf(div_name + '_year' + '.h5', 'md_sys_year')
    pm_sys_year.to_hdf(div_name + '_year' + '.h5', 'pm_sys_year')
    we_sys_year.to_hdf(div_name + '_year' + '.h5', 'we_sys_year')

    am_sig_month.to_hdf(div_name + '_month' + '.h5', 'am_sig_month')
    md_sig_month.to_hdf(div_name + '_month' + '.h5', 'md_sig_month')
    pm_sig_month.to_hdf(div_name + '_month' + '.h5', 'pm_sig_month')
    we_sig_month.to_hdf(div_name + '_month' + '.h5', 'we_sig_month')

    am_sig_year.to_hdf(div_name + '_year' + '.h5', 'am_sig_year')
    md_sig_year.to_hdf(div_name + '_year' + '.h5', 'md_sig_year')
    pm_sig_year.to_hdf(div_name + '_year' + '.h5', 'pm_sig_year')
    we_sig_year.to_hdf(div_name + '_year' + '.h5', 'we_sig_year')
