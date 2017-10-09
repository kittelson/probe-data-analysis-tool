import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import calendar
from viz import extract_vals, create_columns
from matplotlib.ticker import FuncFormatter
from stat_func import percentile


cs_idx = 2
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
path = 'C:/Users/ltrask/Documents/21383 - NCDOT SPM/CaseStudies/'
path1 = 'Site'
path2 = '_20140301_20170930'
#path2 = '_NPMRDS_20140301_20170131'
tmc_path = 'TMC_Identification.csv'
data_path = path1 + str(cs_idx) + path2 + '.csv'

tmc = pd.read_csv(path + path1 + str(cs_idx) + path2 + '/' + tmc_path)
df = pd.read_csv(path + path1 + str(cs_idx) + path2 + '/' + data_path)

df = df[df.travel_time_minutes.notnull()]

dirs = tmc['direction'].unique()
tmc_subset1 = tmc[tmc['direction'] == dirs[0]]['tmc']
df_dir1 = df[df['tmc_code'].isin(tmc_subset1)]
facility_len1 = tmc[tmc['direction'] == dirs[0]].miles.sum()
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
# Filtering to selected set of days
if len(day_subset) > 0:
  df_dir1 = df_dir1[df_dir1['weekday'].isin(day_subset)]

df_dir1 = df_dir1[df_dir1['Date'] < '2015-12-25']

# df_dir1_am = df_dir1[(df_dir1['AP'] >= am_ap_start) & (df_dir1['AP'] < am_ap_end)]
# df_dir1_pm = df_dir1[(df_dir1['AP'] >= pm_ap_start) & (df_dir1['AP'] < pm_ap_end)]
# df_dir1_md = df_dir1[(df_dir1['AP'] >= md_ap_start) & (df_dir1['AP'] < md_ap_end)]

BIN1 = 25
BIN2 = 35
BIN3 = 45
BIN4 = 55

# AM Peak Period
bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
#df_dir1_am = df_dir1[(df_dir1['AP'] >= am_ap_start) & (df_dir1['AP'] < am_ap_end)]
df_dir1_am = df_dir1
df_dir1_am[bin_list[0]] = df_dir1_am['speed'] <= BIN1
df_dir1_am[bin_list[1]] = (df_dir1_am['speed'] > BIN1) & (df_dir1_am['speed'] <= BIN2)
df_dir1_am[bin_list[2]] = (df_dir1_am['speed'] > BIN2) & (df_dir1_am['speed'] <= BIN3)
df_dir1_am[bin_list[3]] = (df_dir1_am['speed'] > BIN3) & (df_dir1_am['speed'] <= BIN4)
df_dir1_am[bin_list[4]] = (df_dir1_am['speed'] > BIN4)
am_gp = df_dir1_am.groupby(['Year', 'Month', 'Day', 'Hour', 'AP', 'tmc_code'])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
am_gp1 = am_gp.groupby(['Year', 'Month', 'Day', 'Hour']).agg(np.sum)
am_gp1['bin_sum'] = am_gp1[bin_list].sum(axis=1)
am_gp1 = am_gp1[bin_list].div(am_gp1['bin_sum'], axis=0)
# PM Peak Period
df_dir1_pm = df_dir1[(df_dir1['AP'] >= am_ap_start) & (df_dir1['AP'] < am_ap_end)]
df_dir1_pm[bin_list[0]] = df_dir1_pm['speed'] <= BIN1
df_dir1_pm[bin_list[1]] = (df_dir1_pm['speed'] > BIN1) & (df_dir1_pm['speed'] <= BIN2)
df_dir1_pm[bin_list[2]] = (df_dir1_pm['speed'] > BIN2) & (df_dir1_pm['speed'] <= BIN3)
df_dir1_pm[bin_list[3]] = (df_dir1_pm['speed'] > BIN3) & (df_dir1_pm['speed'] <= BIN4)
df_dir1_pm[bin_list[4]] = (df_dir1_pm['speed'] > BIN4)
pm_gp = df_dir1_pm.groupby(['Year', 'Month', 'Day', 'Hour', 'AP', 'tmc_code'])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
pm_gp1 = am_gp.groupby(['tmc_code']).agg(np.sum)
pm_gp1['bin_sum'] = pm_gp1[bin_list].sum(axis=1)
pm_gp1 = pm_gp1[bin_list].div(pm_gp1['bin_sum'], axis=0)
# Midday Peak Period
df_dir1_md = df_dir1[(df_dir1['AP'] >= md_ap_start) & (df_dir1['AP'] < md_ap_end)]
df_dir1_md[bin_list[0]] = df_dir1_md['speed'] <= BIN1
df_dir1_md[bin_list[1]] = (df_dir1_md['speed'] > BIN1) & (df_dir1_md['speed'] <= BIN2)
df_dir1_md[bin_list[2]] = (df_dir1_md['speed'] > BIN2) & (df_dir1_md['speed'] <= BIN3)
df_dir1_md[bin_list[3]] = (df_dir1_md['speed'] > BIN3) & (df_dir1_md['speed'] <= BIN4)
df_dir1_md[bin_list[4]] = (df_dir1_md['speed'] > BIN4)
md_gp = df_dir1_md.groupby(['Year', 'Month', 'AP', 'tmc_code'])['bin1', 'bin2', 'bin3', 'bin4', 'bin5'].agg(np.sum)
md_gp1 = am_gp.groupby(['Year', 'Month']).agg(np.sum)
md_gp1['bin_sum'] = md_gp1[bin_list].sum(axis=1)
md_gp1 = md_gp1[bin_list].div(md_gp1['bin_sum'], axis=0)

# plot_df_dir1 = am_gp1.join(pm_gp1, lsuffix='_pm')
# plot_df_dir1 = plot_df_dir1.join(md_gp1, lsuffix='_mid')

def convert_x_to_day(x, pos):
  if x < 0:
    return ''
  first_year = int(start_date.split('-')[0])
  first_month = int(start_date.split('-')[1])
  first_month -= 1  # decrementing to help with modulus
  x = int(x)
  month = x // (24*31)
  hour = (x + 10) % 24
  ampm_str = 'am'
  if hour >= 12:
    ampm_str = 'pm'
    hour -= 12
  if hour == 0:
    hour = 12
  return str(first_year + ((first_month + month) // 12)) + '-' + calendar.month_abbr[((first_month + month) % 12) + 1] + ' ' + str(hour) + ':' + '00' + ampm_str


plot_df_dir1 = am_gp1

x = [el for el in range(len(plot_df_dir1[bin_list[0]]))]
x_study_period = [el for el in range(len(plot_df_dir1[bin_list[0]]))]

fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)
#ax3 = fig.add_subplot(2, 2, 3)
#ax4 = fig.add_subplot(2, 2, 4)

cl = ['#d62728', '#ff7f0e', '#dbdb8d', '#98df8a',  '#2ca02c']

width = 0.35
# ax1.bar(x, plot_df_dir1[bin_list[0]], width, color=cl[0], label='AM-'+bin_list[0])
# bott_arr = plot_df_dir1[bin_list[0]]
# ax1.bar(x, plot_df_dir1[bin_list[1]], width, color=cl[1], label='AM-'+bin_list[1], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[1]]
# ax1.bar(x, plot_df_dir1[bin_list[2]], width, color=cl[2], label='AM-'+bin_list[2], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[2]]
# ax1.bar(x, plot_df_dir1[bin_list[3]], width, color=cl[3], label='AM-'+bin_list[3], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[3]]
# ax1.bar(x, plot_df_dir1[bin_list[4]], width, color=cl[4], label='AM-'+bin_list[4], bottom=bott_arr)
ax1.stackplot(x_study_period,
              am_gp1[bin_list[0]],
              am_gp1[bin_list[1]],
              am_gp1[bin_list[2]],
              am_gp1[bin_list[3]],
              am_gp1[bin_list[4]],
              labels=bin_list, colors=cl)
ax1.xaxis.set_major_formatter(FuncFormatter(convert_x_to_day))
ax1.set_title(start_date + ' to ' + end_date)
ax1.legend()

x_facility = [el for el in range(len(pm_gp1[bin_list[0]]))]
ax2.stackplot(x_facility,
              pm_gp1[bin_list[0]],
              pm_gp1[bin_list[1]],
              pm_gp1[bin_list[2]],
              pm_gp1[bin_list[3]],
              pm_gp1[bin_list[4]],
              labels=bin_list, colors=cl)
ax2.legend()

# ax2.bar(x, plot_df_dir1[bin_list[0] + '_pm'], width, color=cl[0], label='PM-'+bin_list[0])
# bott_arr = plot_df_dir1[bin_list[0] + '_pm']
# ax2.bar(x, plot_df_dir1[bin_list[1] + '_pm'], width, color=cl[1], label='PM-'+bin_list[1], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[1] + '_pm']
# ax2.bar(x, plot_df_dir1[bin_list[2] + '_pm'], width, color=cl[2], label='PM-'+bin_list[2], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[2] + '_pm']
# ax2.bar(x, plot_df_dir1[bin_list[3] + '_pm'], width, color=cl[3], label='PM-'+bin_list[3], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[3] + '_pm']
# ax2.bar(x, plot_df_dir1[bin_list[4] + '_pm'], width, color=cl[4], label='PM-'+bin_list[4], bottom=bott_arr)
# ax2.legend()
#
# ax3.bar(x, plot_df_dir1[bin_list[0] + '_mid'], width, color=cl[0], label='Mid-'+bin_list[0])
# bott_arr = plot_df_dir1[bin_list[0] + '_mid']
# ax3.bar(x, plot_df_dir1[bin_list[1] + '_mid'], width, color=cl[1], label='Mid-'+bin_list[1], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[1] + '_mid']
# ax3.bar(x, plot_df_dir1[bin_list[2] + '_mid'], width, color=cl[2], label='Mid-'+bin_list[2], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[2] + '_mid']
# ax3.bar(x, plot_df_dir1[bin_list[3] + '_mid'], width, color=cl[3], label='Mid-'+bin_list[3], bottom=bott_arr)
# bott_arr += plot_df_dir1[bin_list[3] + '_mid']
# ax3.bar(x, plot_df_dir1[bin_list[4] + '_mid'], width, color=cl[4], label='Mid-'+bin_list[4], bottom=bott_arr)
# ax3.legend()


