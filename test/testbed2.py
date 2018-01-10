import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from viz_qt import extract_vals, create_columns
from matplotlib.ticker import FuncFormatter
import calendar
from datetime import datetime, timedelta
from datetime import time as dtime

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

am_peak_str = dtime(am_start_hour, am_start_min, 0).strftime('%I:%M%p') + '-' + dtime(am_end_hour, am_end_min, 0).strftime('%I:%M%p')
pm_peak_str = dtime(pm_start_hour, pm_start_min, 0).strftime('%I:%M%p') + '-' + dtime(pm_end_hour, pm_end_min, 0).strftime('%I:%M%p')
md_peak_str = dtime(md_start_hour, md_start_min, 0).strftime('%I:%M%p') + '-' + dtime(md_end_hour, md_end_min, 0).strftime('%I:%M%p')

path = 'C:/Users/ltrask/Documents/21383 - NCDOT SPM/CaseStudies/'
path1 = 'Site'
path2 = '_20140301_20170930'
#path2 = '_NPMRDS_20140301_20170131'
tmc_path = 'TMC_Identification.csv'
data_path = path1 + str(cs_idx) + path2 + '.csv'

# tmc = pd.read_csv(path + path1 + str(cs_idx) + path2 + '/' + tmc_path)
# df = pd.read_csv(path + path1 + str(cs_idx) + path2 + '/' + data_path)
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Ext13Mi_20130701_20170131/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Ext13Mi_20130701_20170131/I495_VA_NB_Ext13Mi_20130701_20170131.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_NB_Extended_20140901_20170131/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_NB_Extended_20140901_20170131/TX161_TX_NB_Extended_20140901_20170131.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_SB_Extended_20140901_20170131/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_SB_Extended_20140901_20170131/TX161_TX_SB_Extended_20140901_20170131.csv')
tmc = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_15Min_2016_AllDays/' + tmc_path)
df = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_15Min_2016_AllDays/I95_PA_15Min_2016_AllDays.csv')
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

month_idx = 3

df_dir11 = df_dir1[df_dir1['Month'].isin([month_idx])]
df_dir11 = df_dir11[df_dir11['weekday'].isin([0, 1, 2, 3, 4])]
# df_dir11 = df_dir11[df_dir11['weekday'].isin([1, 2, 3])]
sc1 = df_dir11.groupby(['AP', 'tmc_code'])['speed'].agg(np.mean)
sc1 = sc1.reindex(tmc['tmc'], level=1)
sc1_mat = sc1.unstack().values[:, :, np.newaxis]
np.savetxt('dir1_' + calendar.month_abbr[month_idx] + '.csv', sc1_mat, delimiter=',')

if len(dirs) > 1:
    df_dir22 = df_dir2[df_dir2['Month'].isin([month_idx])]
    df_dir22 = df_dir22[df_dir22['weekday'].isin([0, 1, 2, 3, 4])]
    # df_dir22 = df_dir22[df_dir22['weekday'].isin([1, 2, 3])]
    sc2 = df_dir22.groupby(['AP', 'tmc_code'])['speed'].agg(np.mean)
    sc2 = sc2.reindex(tmc['tmc'], level=1)
    sc2_mat = sc2.unstack().values[:, :, np.newaxis]
    np.savetxt('dir2_' + calendar.month_abbr[month_idx] + '.csv', sc2_mat, delimiter=',')

# tmc1 = df_dir1[df_dir1['tmc_code'].isin([tmc['tmc'][tmc_1_idx]])]
# test1 = tmc1.groupby(['Date', 'AP'])['speed'].agg(np.mean)
# df_dir1 = df_dir1[df_dir1['weekday'].isin([0, 1, 2, 3, 4])]
# df_dir1 = df_dir1[df_dir1['weekday'].isin([5, 6])]
tmc11 = df_dir1[(df_dir1['AP'] >= am_ap_start) & (df_dir1['AP'] <= am_ap_end)]
test11 = tmc11.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
d11 = test11.to_frame()
d11.reindex(tmc_subset1, level=1)
imshow_data11 = d11.unstack().values[:, :]
imshow_data11 = imshow_data11.T

tmc12 = df_dir1[(df_dir1['AP'] >= pm_ap_start) & (df_dir1['AP'] <= pm_ap_end)]
test12 = tmc12.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
d12 = test12.to_frame()
imshow_data12 = d12.unstack().values[:, :]
imshow_data12 = imshow_data12.T

tmc13 = df_dir1[(df_dir1['AP'] >= md_ap_start) & (df_dir1['AP'] <= md_ap_end)]
test13 = tmc13.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
d13 = test13.to_frame()
imshow_data13 = d13.unstack().values[:, :]
imshow_data13 = imshow_data13.T

if len(dirs) > 1:
    tmc21 = df_dir2[(df_dir2['AP'] >= am_ap_start) & (df_dir2['AP'] <= am_ap_end)]
    test21 = tmc21.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
    d21 = test21.to_frame()
    imshow_data21 = d21.unstack().values[:, :]
    imshow_data21 = imshow_data21.T

    tmc22 = df_dir2[(df_dir2['AP'] >= pm_ap_start) & (df_dir2['AP'] <= pm_ap_end)]
    test22 = tmc22.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
    d22 = test22.to_frame()
    imshow_data22 = d22.unstack().values[:, :]
    imshow_data22 = imshow_data22.T

    tmc23 = df_dir2[(df_dir2['AP'] >= md_ap_start) & (df_dir2['AP'] <= md_ap_end)]
    test23 = tmc23.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
    d23 = test23.to_frame()
    imshow_data23 = d23.unstack().values[:, :]
    imshow_data23 = imshow_data23.T

def convert_xval_to_time(x, pos, min_resolution):
    if x < 0:
        return ''

    if x - int(x) != 0:
        return ''
    aps_per_hour = int(60 / min_resolution)
    hour = int(x // aps_per_hour)
    hour = hour % 24
    ampm_str = 'am'
    if hour >= 12:
        ampm_str = 'pm'
        hour -= 12
    if hour == 0:
        hour = 12
    minute = int(x % aps_per_hour) * min_resolution
    return str(hour) + ':' + '{num:02d}'.format(num=minute) + ampm_str

def convert_x_to_day(x, pos, start_date):
    # if int(x) - x != 0:
    #     return ''
    # new_date = start_date + timedelta(days=int(x))
    new_date = start_date + timedelta(days=x)
    return new_date.strftime('%m/%d/%Y') + '\n' + calendar.day_abbr[new_date.weekday()]


def convert_extent_to_tmc(x, pos, tmc_list, tmc_extent):
    tmc_span = tmc_extent / len(tmc_list)
    c_idx = x // tmc_span
    return tmc_list[min(c_idx, len(tmc_list)-1)]

fig = plt.figure(figsize=(12, 8))
if len(dirs) > 1:
    ax11 = fig.add_subplot(3, 2, 1)
    ax12 = fig.add_subplot(3, 2, 3)
    ax13 = fig.add_subplot(3, 2, 5)
    ax21 = fig.add_subplot(3, 2, 2)
    ax22 = fig.add_subplot(3, 2, 4)
    ax23 = fig.add_subplot(3, 2, 6)
else:
    ax11 = fig.add_subplot(3, 1, 1)
    ax12 = fig.add_subplot(3, 1, 2)
    ax13 = fig.add_subplot(3, 1, 3)
    # ax21 = fig.add_subplot(3, 1, 2)
    # ax22 = fig.add_subplot(3, 1, 4)
    # ax23 = fig.add_subplot(3, 1, 6)

# Direction #1
num_tmc, num_days = imshow_data11.shape
tmc_ext = num_days / 4
cb_shrink = 0.95
tokens = start_date.split('-')
start_datetime = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
f_x_label = lambda x, pos: convert_x_to_day(x, pos, start_datetime)
f_y_label = lambda y, pos: convert_xval_to_time(y, pos, 5)
f_tmc_label1 = lambda x, pos: convert_extent_to_tmc(x, pos, tmc_subset1, tmc_ext)
f_tmc_label2 = lambda x, pos: convert_extent_to_tmc(x, pos, tmc_subset2, tmc_ext)
# imshow_data11.sort(axis=1)
# imshow_data12.sort(axis=1)
# imshow_data13.sort(axis=1)
# imshow_data11 = imshow_data11.T
# imshow_data12 = imshow_data12.T
# imshow_data13 = imshow_data13.T
# im11 = ax11.imshow(imshow_data11, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
last_val = 0
row_idx = 0
tmc_l1 = tmc[tmc['direction'] == dirs[0]]
for row in imshow_data11:
    curr_tmc_len = tmc_l1['miles'][row_idx]
    im11 = ax11.imshow(row.reshape((1, num_days)), extent=[0, num_days, last_val, last_val + curr_tmc_len], cmap='RdYlGn', origin='lower', interpolation='nearest', aspect='auto')
    last_val += curr_tmc_len
    row_idx += 1
# im12 = ax12.imshow(imshow_data12, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
# im13 = ax13.imshow(imshow_data13, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
ax11.set_ylim(0, tmc_l1['miles'].sum())
ax11.set_title(dirs[0] + ': AM Peak')
ax12.set_title(dirs[0] + ': PM Peak')
ax13.set_title(dirs[0] + ': Midday Peak')
cbar11 = fig.colorbar(im11, ax=ax11, shrink=cb_shrink)
cbar11.set_label('Speed (mph)')
# cbar12 = fig.colorbar(im12, ax=ax12, shrink=cb_shrink)
# cbar12.set_label('Speed (mph)')
# cbar13 = fig.colorbar(im13, ax=ax13, shrink=cb_shrink)
# cbar13.set_label('Speed (mph)')
# ax11.xaxis.set_major_formatter(FuncFormatter(f_x_label))
# ax11.yaxis.set_major_formatter(FuncFormatter(f_tmc_label1))
# ax11.set_ylabel('TMC')
# ax12.xaxis.set_major_formatter(FuncFormatter(f_x_label))
# ax12.yaxis.set_major_formatter(FuncFormatter(f_tmc_label1))
# ax12.set_ylabel('TMC')
# ax13.xaxis.set_major_formatter(FuncFormatter(f_x_label))
# ax13.yaxis.set_major_formatter(FuncFormatter(f_tmc_label1))
# ax13.set_ylabel('TMC')

# Direction #2
if len(dirs) > 1:
    im21 = ax21.imshow(imshow_data21, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
    im22 = ax22.imshow(imshow_data22, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
    im23 = ax23.imshow(imshow_data23, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
    ax21.set_title(dirs[1] + ': AM Peak' + ' (' + am_peak_str + ')')
    ax22.set_title(dirs[1] + ': PM Peak' + ' (' + pm_peak_str + ')')
    ax23.set_title(dirs[1] + ': Midday Peak' + ' (' + md_peak_str + ')')
    cbar21 = fig.colorbar(im21, ax=ax21, shrink=cb_shrink)
    cbar21.set_label('Speed (mph)')
    cbar22 = fig.colorbar(im22, ax=ax22, shrink=cb_shrink)
    cbar22.set_label('Speed (mph)')
    cbar23 = fig.colorbar(im23, ax=ax23, shrink=cb_shrink)
    cbar23.set_label('Speed (mph)')
    ax21.xaxis.set_major_formatter(FuncFormatter(f_x_label))
    ax21.yaxis.set_major_formatter(FuncFormatter(f_tmc_label2))
    ax21.set_ylabel('TMC')
    ax22.xaxis.set_major_formatter(FuncFormatter(f_x_label))
    ax22.yaxis.set_major_formatter(FuncFormatter(f_tmc_label2))
    ax22.set_ylabel('TMC')
    ax23.xaxis.set_major_formatter(FuncFormatter(f_x_label))
    ax23.yaxis.set_major_formatter(FuncFormatter(f_tmc_label2))
    ax23.set_ylabel('TMC')

fig.suptitle(main_title)
fig.tight_layout()

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


plot_df_dir1 = am_gp1

x = [el for el in range(len(plot_df_dir1[bin_list[0]]))]
x_study_period = [el for el in range(len(plot_df_dir1[bin_list[0]]))]

fig = plt.figure(figsize=(12, 8))
ax11 = fig.add_subplot(2, 1, 1)
ax12 = fig.add_subplot(2, 1, 2)
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
ax11.stackplot(x_study_period,
               am_gp1[bin_list[0]],
               am_gp1[bin_list[1]],
               am_gp1[bin_list[2]],
               am_gp1[bin_list[3]],
               am_gp1[bin_list[4]],
               labels=bin_list, colors=cl)
ax11.xaxis.set_major_formatter(FuncFormatter(convert_x_to_day))
ax11.set_title(start_date + ' to ' + end_date)
ax11.legend()

x_facility = [el for el in range(len(pm_gp1[bin_list[0]]))]
ax12.stackplot(x_facility,
               pm_gp1[bin_list[0]],
               pm_gp1[bin_list[1]],
               pm_gp1[bin_list[2]],
               pm_gp1[bin_list[3]],
               pm_gp1[bin_list[4]],
               labels=bin_list, colors=cl)
ax12.legend()

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
