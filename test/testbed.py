import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
# from viz_qt import extract_vals, create_columns
from matplotlib.ticker import FuncFormatter
import calendar
from datetime import datetime, timedelta
from datetime import time as dtime

import matplotlib.mlab as mlab
import numpy as np
# import plotly.plotly as py
# py.sign_in('jlaketrask', 'OpWt250ytTOtcB233mB0')

def extract_vals(date_str):
    # ----NPMRDS----
    date, time = date_str.split(' ')[:2]
    time_tokens = time.split(':')
    hour = int(time_tokens[0])
    minute = int(time_tokens[1])
    [year, month, day] = [int(val) for val in date.split('-')]
    day_type = datetime(year, month, day).weekday()
    ap = (hour * (60 // 5)) + minute // 5
    # ----End NPMRDS----

    # ----BlueMAC----
    # date_tokens = date_str.strip('*').split(' ')
    # date, time = date_tokens[:2]
    # pm_offset = False
    # am_offset = False
    # if len(date_tokens) > 2:
    #     if date_tokens[-1].lower().endswith('pm'):
    #         pm_offset = True
    #     else:
    #         am_offset = True
    # time_tokens = time.split(':')
    # hour = int(time_tokens[0])
    # if hour == 12:
    #     hour -= (12 if am_offset else 0)
    # else:
    #     hour += (12 if pm_offset else 0)
    # minute = int(time_tokens[1])
    # [month, day, year] = [int(val) for val in date.split('/')]
    # date = str(year) + '-' + str(month) + '-' + str(day)
    # day_type = datetime.datetime(year, month, day).weekday()
    # ap = (hour * (60 // DataHelper.Project.ID_DATA_RESOLUTION)) + minute // DataHelper.Project.ID_DATA_RESOLUTION
    # ----END BlueMAC----
    return date, year, month, day, ap, day_type


def create_columns(data, is_case_study=False):
    if is_case_study is False:
        dates, years, months, days, aps, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(weekday)
    else:
        dates, years, months, days, aps, regions, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(regions), list(weekday)

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
# tmc = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_15Min_2016_AllDays/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_15Min_2016_AllDays/I95_PA_15Min_2016_AllDays.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_AllDays_NPMRDS/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_AllDays_NPMRDS/I66_EB_AllDays_NPMRDS.csv')
tmc = pd.read_csv('C:/Users/ltrask/Documents/18135 - FHWA Sketch Planning Methods/I66_Sample/' + tmc_path)
df = pd.read_csv('C:/Users/ltrask/Documents/18135 - FHWA Sketch Planning Methods/I66_Sample/I66_Sample.csv')
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


df_tmc = df_dir1[df_dir1['tmc_code'] == tmc['tmc'][0]]
df_lottr = df_tmc.groupby(['weekday', 'Hour'])['travel_time_minutes'].agg([percentile(50), percentile(80)])
df_lottr['LOTTR'] = df_lottr['percentile_80'] / df_lottr['percentile_50']
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
cmap = mpl.cm.get_cmap('Reds')

N = 24
width = (2 * np.pi) / N
theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
y_arr = [1 for el in range(len(theta))]
bars = []
for day, df in df_lottr.groupby(level=0):
    bars.append(
            ax.bar(theta,
                   y_arr,
                   width=width,
                   bottom=day
                   )
    )
    cong = [(el - 1.0) / 0.5 for el in df['LOTTR'].values]
    # print(cong)
    for val, bar in zip(cong, bars[-1]):
        bar.set_facecolor(cmap(val))
        # bar.set_alpha(0.8)


ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
plt.ylim(0, 7)
ax.set_yticks([0, 1, 2, 3, 4, 5, 6])
ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax.set_title('Time of Day Reliability (LOTTR) by Day of Week')

ax_cb = fig.add_axes([0.9, 0.1, 0.03, 0.8])
cNorm = mpl.colors.Normalize(vmin=1, vmax=2.0)
cb1 = mpl.colorbar.ColorbarBase(ax_cb, norm=cNorm, cmap='Reds')
plt.show()
# # plot_url = py.plot_mpl(fig)


# df_tmc = df_dir1[df_dir1['tmc_code'] == tmc['tmc'][29]]

df_am = df_dir1[(df_dir1['AP'] >= am_ap_start) & (df_dir1['AP'] < am_ap_end) & (df_dir1['weekday'].isin([0, 1, 2, 3, 4]))]
df_pm = df_dir1[(df_dir1['AP'] >= pm_ap_start) & (df_dir1['AP'] < pm_ap_end) & (df_dir1['weekday'].isin([0, 1, 2, 3, 4]))]
df_md = df_dir1[(df_dir1['AP'] >= md_ap_start) & (df_dir1['AP'] < md_ap_end) & (df_dir1['weekday'].isin([0, 1, 2, 3, 4]))]
df_we = df_dir1[(df_dir1['AP'] >= md_ap_start) & (df_dir1['AP'] < md_ap_end) & (df_dir1['weekday'].isin([5, 6]))]

df_lottr_am = df_am.groupby(['tmc_code'])['travel_time_minutes'].agg([percentile(50), percentile(80)])
df_lottr_pm = df_pm.groupby(['tmc_code'])['travel_time_minutes'].agg([percentile(50), percentile(80)])
df_lottr_md = df_md.groupby(['tmc_code'])['travel_time_minutes'].agg([percentile(50), percentile(80)])
df_lottr_we = df_we.groupby(['tmc_code'])['travel_time_minutes'].agg([percentile(50), percentile(80)])

df_lottr_am['LOTTR'] = df_lottr_am['percentile_80'] / df_lottr_am['percentile_50']
df_lottr_pm['LOTTR'] = df_lottr_pm['percentile_80'] / df_lottr_pm['percentile_50']
df_lottr_md['LOTTR'] = df_lottr_md['percentile_80'] / df_lottr_md['percentile_50']
df_lottr_we['LOTTR'] = df_lottr_we['percentile_80'] / df_lottr_we['percentile_50']

df_lottr_am = df_lottr_am.reindex(tmc['tmc'])
df_lottr_pm = df_lottr_pm.reindex(tmc['tmc'])
df_lottr_md = df_lottr_md.reindex(tmc['tmc'])
df_lottr_we = df_lottr_we.reindex(tmc['tmc'])

# FOUR SUBPLOTS
# fig, ax = plt.subplots(2, 2)
#
# ax[0][0].spines['top'].set_visible(False)
# ax[0][0].spines['right'].set_visible(False)
# ax[0][1].spines['top'].set_visible(False)
# ax[0][1].spines['right'].set_visible(False)
# ax[1][0].spines['top'].set_visible(False)
# ax[1][0].spines['right'].set_visible(False)
# ax[1][1].spines['top'].set_visible(False)
# ax[1][1].spines['right'].set_visible(False)
#
# x_arr = [el for el in range(tmc['tmc'].count())]
# ax[0][0].bar(x_arr, df_lottr_am['LOTTR'].values, color='navy')
# ax[0][1].bar(x_arr, df_lottr_pm['LOTTR'].values, color='green')
# ax[1][0].bar(x_arr, df_lottr_md['LOTTR'].values, color='firebrick')
# ax[1][1].bar(x_arr, df_lottr_we['LOTTR'].values, color='darkorange')
#
# target = [1.5 for el in range(len(x_arr))]
#
# ax[0][0].plot(x_arr, target, color='grey', linestyle=':')
# ax[0][1].plot(x_arr, target, color='grey', linestyle=':')
# ax[1][0].plot(x_arr, target, color='grey', linestyle=':')
# ax[1][1].plot(x_arr, target, color='grey', linestyle=':')
#
# ax[0][0].set_title('AM Period')
# ax[0][1].set_title('PM Period')
# ax[1][0].set_title('Weekday - Midday')
# ax[1][1].set_title('Weekend - Midday')
#
# ax[0][0].set_xlabel('TMC')
# ax[0][0].set_ylabel('LOTTR')
# ax[0][1].set_xlabel('TMC')
# ax[0][1].set_ylabel('LOTTR')
# ax[1][0].set_xlabel('TMC')
# ax[1][0].set_ylabel('LOTTR')
# ax[1][1].set_xlabel('TMC')
# ax[1][1].set_ylabel('LOTTR')
#
# fig.suptitle('LOTTR By Period')
#
# plt.show()

# GROUPED BAR
# fig = plt.figure()
# ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
#
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
#
# x_arr = np.arange(tmc['tmc'].count())
# width = 0.225
# ax.bar(x_arr, df_lottr_am['LOTTR'].values, width=width, label='AM', color='navy')
# ax.bar(x_arr + width, df_lottr_pm['LOTTR'].values, width=width, label='PM', color='green')
# ax.bar(x_arr + 2 * width, df_lottr_md['LOTTR'].values, width=width, label='Midday', color='firebrick')
# ax.bar(x_arr + 3 * width, df_lottr_we['LOTTR'].values, width=width, label='Weekend', color='darkorange')
#
# target = [1.5 for el in range(len(x_arr))]
#
# ax.plot(x_arr, target, color='grey', linestyle=':')
#
# ax.set_title('Update')
#
# ax.set_xlabel('TMC')
# ax.set_ylabel('LoTTR by TMC')
# ax.legend()
#
# plt.show()


# # % TMC UNDER LOTTR THRESHOLD BY PERIOD
# fig = plt.figure()
# ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
# x_arr = np.arange(1)
# width = 0.25
# ama = df_lottr_am['LOTTR'].values
# pma = df_lottr_pm['LOTTR'].values
# mda = df_lottr_md['LOTTR'].values
# wea = df_lottr_we['LOTTR'].values
# am_val = [100.0 * sum(ama < 1.5) / len(ama)]
# pm_val = [100.0 * sum(pma < 1.5) / len(pma)]
# md_val = [100.0 * sum(mda < 1.5) / len(mda)]
# we_val = [100.0 * sum(wea < 1.5) / len(wea)]
# ax.bar(x_arr, am_val, width=width, label='AM', color='navy')
# ax.bar(x_arr + width, pm_val, width=width, label='PM', color='green')
# ax.bar(x_arr + 2 * width, md_val, width=width, label='Midday', color='firebrick')
# ax.bar(x_arr + 3 * width, we_val, width=width, label='Weekend', color='darkorange')
# target = [80 for el in range(len(x_arr))]
# ax.plot(x_arr, target, color='grey', linestyle=':')
# ax.set_title('% of TMCs under LoTTR Target by Period')
# ax.set_ylabel('Percent')
# ax.set_ylim(0, 100)
# ax.set_xticklabels([])
# ax.set_xticks([])
# ax.legend()
# plt.show()


ax_top = plt.subplot2grid((2, 4), (0, 1), colspan=2)
ax1 = plt.subplot2grid((2, 4), (1, 0))
ax2 = plt.subplot2grid((2, 4), (1, 1))
ax3 = plt.subplot2grid((2, 4), (1, 2))
ax4 = plt.subplot2grid((2, 4), (1, 3))

# % TMC under LoTTR Threshold by Period
ax_top.spines['top'].set_visible(False)
ax_top.spines['right'].set_visible(False)
x_arr = np.arange(1)
width = 0.25
ama = df_lottr_am['LOTTR'].values
pma = df_lottr_pm['LOTTR'].values
mda = df_lottr_md['LOTTR'].values
wea = df_lottr_we['LOTTR'].values
am_val = [100.0 * sum(ama < 1.5) / len(ama)]
pm_val = [100.0 * sum(pma < 1.5) / len(pma)]
md_val = [100.0 * sum(mda < 1.5) / len(mda)]
we_val = [100.0 * sum(wea < 1.5) / len(wea)]
ax_top.bar(x_arr + 0 * width, am_val, width=width, label='AM', color='navy')
ax_top.bar(x_arr + 2 * width, pm_val, width=width, label='PM', color='green')
ax_top.bar(x_arr + 4 * width, md_val, width=width, label='Midday', color='firebrick')
ax_top.bar(x_arr + 6 * width, we_val, width=width, label='Weekend', color='darkorange')
x_arr2 = [0, 6 * width]
target = [80 for el in range(len(x_arr2))]
ax_top.plot(x_arr2, target, color='grey', linestyle=':', label='Target')
ax_top.set_title('% of TMCs under LoTTR Target by Period')
ax_top.set_ylabel('Percent')
ax_top.set_ylim(0, 100)
ax_top.set_xticklabels([])
ax_top.set_xticks([])
ax_top.legend(ncol=5, loc=9)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)

x_arr = [el for el in range(tmc['tmc'].count())]
ax1.bar(x_arr, df_lottr_am['LOTTR'].values, color='navy')
ax2.bar(x_arr, df_lottr_pm['LOTTR'].values, color='green')
ax3.bar(x_arr, df_lottr_md['LOTTR'].values, color='firebrick')
ax4.bar(x_arr, df_lottr_we['LOTTR'].values, color='darkorange')

target = [1.5 for el in range(len(x_arr))]

ax1.plot(x_arr, target, color='grey', linestyle=':')
ax2.plot(x_arr, target, color='grey', linestyle=':')
ax3.plot(x_arr, target, color='grey', linestyle=':')
ax4.plot(x_arr, target, color='grey', linestyle=':')

ax1.set_title('AM Period')
ax2.set_title('PM Period')
ax3.set_title('Weekday - Midday')
ax4.set_title('Weekend - Midday')

ax1.set_xlabel('TMC')
ax1.set_ylabel('LOTTR')
ax2.set_xlabel('TMC')
ax2.set_ylabel('LOTTR')
ax3.set_xlabel('TMC')
ax3.set_ylabel('LOTTR')
ax4.set_xlabel('TMC')
ax4.set_ylabel('LOTTR')

plt.show()