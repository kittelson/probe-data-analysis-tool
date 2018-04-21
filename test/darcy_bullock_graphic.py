import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from viz_qt import extract_vals, create_columns
from matplotlib.ticker import FuncFormatter
import calendar
from datetime import datetime, timedelta
from datetime import time as dtime
from matplotlib import collections

cs_idx = 4
tmc_1_idx = 1
tmc_2_idx = 5
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
# tmc = pd.read_csv('C:/Users/ltrask/Downloads/I-84_EB_20111001_20151231/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Downloads/I-84_EB_20111001_20151231/I-84_EB_20111001_20151231.csv')
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


# tmc11 = df_dir1[(df_dir1['AP'] >= am_ap_start) & (df_dir1['AP'] <= am_ap_end)]
# test11 = tmc11.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
# d11 = test11.to_frame()
# d11.reindex(tmc_subset1, level=1)
# imshow_data11 = d11.unstack().values[:, :]
# imshow_data11 = imshow_data11.T
#
# tmc12 = df_dir1[(df_dir1['AP'] >= pm_ap_start) & (df_dir1['AP'] <= pm_ap_end)]
# test12 = tmc12.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
# d12 = test12.to_frame()
# imshow_data12 = d12.unstack().values[:, :]
# imshow_data12 = imshow_data12.T
#
# tmc13 = df_dir1[(df_dir1['AP'] >= md_ap_start) & (df_dir1['AP'] <= md_ap_end)]
# test13 = tmc13.groupby(['Date', 'tmc_code'])['speed'].agg(np.mean)
# d13 = test13.to_frame()
# imshow_data13 = d13.unstack().values[:, :]
# imshow_data13 = imshow_data13.T

bins = [0, 15, 25, 35, 45, 55, 65, np.inf]
test11 = df_dir1.groupby(['Year', 'Month', 'tmc_code', pd.cut(df_dir1.speed, bins)])
d11 = test11.size().unstack()
d11.fillna(0.0, inplace=True)
d11 = d11.reindex(tmc_subset1, level=2)

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
# if len(dirs) > 1:
#     ax11 = fig.add_subplot(3, 2, 1)
#     ax12 = fig.add_subplot(3, 2, 3)
#     ax13 = fig.add_subplot(3, 2, 5)
#     ax21 = fig.add_subplot(3, 2, 2)
#     ax22 = fig.add_subplot(3, 2, 4)
#     ax23 = fig.add_subplot(3, 2, 6)
# else:
#     ax11 = fig.add_subplot(3, 1, 1)
#     ax12 = fig.add_subplot(3, 1, 2)
#     ax13 = fig.add_subplot(3, 1, 3)
#     # ax21 = fig.add_subplot(3, 1, 2)
#     # ax22 = fig.add_subplot(3, 1, 4)
#     # ax23 = fig.add_subplot(3, 1, 6)

ax11 = fig.add_subplot(1, 1, 1)

map_tmc_to_y = dict()
for index, row in tmc_subset1.to_frame().iterrows():
    map_tmc_to_y[row['tmc']] = index

base_val = np.zeros((1, 7))
# ind = tmc['tmc'].tolist()
xv1 = 0
last_year = None
last_month = None
num_tmc = len(tmc_subset1)
syear = int(start_date.split('-')[0])
smonth = int(start_date.split('-')[1])
eyear = int(end_date.split('-')[0])
emonth = int(end_date.split('-')[1])
if syear == eyear:
    num_months = emonth - smonth + 1
else:
    num_months = 12 - smonth + 1
    year_cnt = syear + 1
    while year_cnt < eyear:
        num_months += 12
        year_cnt += 1
    num_months += emonth

bar_mat = np.zeros((num_tmc, num_months*7))
clist = ['mediumorchid',
         'firebrick',
         'red',
         'darkorange',
         'yellow',
         'lightgreen',
         'green']
for bar_id, sub_df in d11.iterrows():

    if last_year is None:
        last_year = bar_id[0]

    if last_month is None:
        last_month = bar_id[1]

    if bar_id[0] != last_year or bar_id[1] != last_month:
        # print('xv_change')
        xv1 += 1

    sub_df = sub_df / sub_df.sum()
    heat_val = 0
    xv2 = 0
    # print(sub_df)
    for index, val in sub_df.iteritems():
        # im11 = ax11.imshow([[heat_val]],
        #             extent=[xv1 + xv2, xv1 + xv2 + val, map_tmc_to_y[bar_id[2]], map_tmc_to_y[bar_id[2]] + 1],
        #             cmap='RdYlGn', origin='lower', interpolation='nearest', aspect='auto')
        # print(str(bar_id) + ', ' + str(xv1 + xv2 + val) + ', ' + str(map_tmc_to_y[bar_id[2]] + 1))
        # print(str(map_tmc_to_y[bar_id[2]]) + ', ' + str(xv1 * 7 + xv2))
        bar_mat[map_tmc_to_y[bar_id[2]]][xv1 * 7 + xv2] = val

        heat_val += 1
        xv2 += 1

    last_year = bar_id[0]
    last_month = bar_id[1]

bwidth = 0.25
bar_id = np.arange(num_tmc) * (bwidth + 0.01)
bar_mat = bar_mat.T
bot = np.zeros((num_tmc,))
c_id = 0
for row in bar_mat:
    ax11.barh(bar_id, row, left=bot, color=clist[c_id], height=bwidth)
    bot = bot + row
    c_id = (c_id + 1) % 7


for i in range(num_months):
    c1 = collections.BrokenBarHCollection([(i, 1)], (-0.125, num_tmc * (bwidth + 0.01)),
                                                      edgecolors=['black'],
                                                      linewidths=[2.5, 2.5],
                                                      # linestyles=['--', '--'],
                                                      facecolors=['none'],
                                                      alpha=0.75)
    c1.set_zorder(10)
    ax11.add_collection(c1)

ax11.set_xlabel('Month/Year')
ax11.set_ylabel('TMC/Milepost')

# # Direction #1
# num_tmc, num_days = imshow_data11.shape
# tmc_ext = num_days / 4
# cb_shrink = 0.95
# tokens = start_date.split('-')
# start_datetime = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
# f_x_label = lambda x, pos: convert_x_to_day(x, pos, start_datetime)
# f_y_label = lambda y, pos: convert_xval_to_time(y, pos, 5)
# f_tmc_label1 = lambda x, pos: convert_extent_to_tmc(x, pos, tmc_subset1, tmc_ext)
# f_tmc_label2 = lambda x, pos: convert_extent_to_tmc(x, pos, tmc_subset2, tmc_ext)
# # imshow_data11.sort(axis=1)
# # imshow_data12.sort(axis=1)
# # imshow_data13.sort(axis=1)
# # imshow_data11 = imshow_data11.T
# # imshow_data12 = imshow_data12.T
# # imshow_data13 = imshow_data13.T
# # im11 = ax11.imshow(imshow_data11, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
# last_val = 0
# row_idx = 0
# tmc_l1 = tmc[tmc['direction'] == dirs[0]]
# for row in imshow_data11:
#     curr_tmc_len = tmc_l1['miles'][row_idx]
#     im11 = ax11.imshow(row.reshape((1, num_days)), extent=[0, num_days, last_val, last_val + curr_tmc_len], cmap='RdYlGn', origin='lower', interpolation='nearest', aspect='auto')
#     last_val += curr_tmc_len
#     row_idx += 1
#
# last_val = 0
# row_idx = 0
# for row in imshow_data12:
#     curr_tmc_len = tmc_l1['miles'][row_idx]
#     im12 = ax11.imshow(row.reshape((1, num_days)), extent=[num_days+1, num_days * 2, last_val, last_val + curr_tmc_len], cmap='RdYlGn', origin='lower', interpolation='nearest', aspect='auto')
#     last_val += curr_tmc_len
#     row_idx += 1
#
# last_val = 0
# row_idx = 0
# for row in imshow_data13:
#     curr_tmc_len = tmc_l1['miles'][row_idx]
#     im13 = ax11.imshow(row.reshape((1, num_days)), extent=[num_days*2 + 1, num_days * 3, last_val, last_val + curr_tmc_len], cmap='RdYlGn', origin='lower', interpolation='nearest', aspect='auto')
#     last_val += curr_tmc_len
#     row_idx += 1
#
# # im12 = ax12.imshow(imshow_data12, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
# # im13 = ax13.imshow(imshow_data13, extent=[0, num_days, 0, tmc_ext], cmap='RdYlGn')
# ax11.set_ylim(0, tmc_l1['miles'].sum())
# ax11.set_xlim(0, num_days * 3)
# ax11.set_title(dirs[0] + ': AM Peak')
# # ax12.set_title(dirs[0] + ': PM Peak')
# # ax13.set_title(dirs[0] + ': Midday Peak')
# cbar11 = fig.colorbar(im11, ax=ax11, shrink=cb_shrink)
# cbar11.set_label('Speed (mph)')
