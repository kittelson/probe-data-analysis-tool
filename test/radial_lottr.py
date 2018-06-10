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


def make_colormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    import matplotlib.colors as mcolors
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)


def create_dq_cmap():
    import matplotlib.colors as mcolors
    c = mcolors.ColorConverter().to_rgb
    # custom_cmap = make_colormap(
    #     [c('indigo'), c('indigo'), 0.25, c('indigo'), c('red'), 0.5, c('red'), c('orange'), 0.6, c('orange'), c('yellow'), 0.7, c('yellow'),
    #      c('lightgreen'), 0.8, c('lightgreen'), c('green'), 0.9, c('green')])
    custom_cmap = make_colormap(
        # [c('white'), c('white'), 0.25, c('white'), c('red'), 0.5, c('red'), c('indigo'), 0.9, c('indigo'), c('indigo')]
        [c('palegreen'), c('palegreen'), 0.17,
         c('palegreen'), c('yellow'), 0.34,
         c('yellow'), c('red'), 0.5,
         c('red'), c('indigo'), 0.9,
         c('indigo'), c('indigo')]
    )
    return custom_cmap

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
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18135 - FHWA Sketch Planning Methods/I66_Sample/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18135 - FHWA Sketch Planning Methods/I66_Sample/I66_Sample.csv')
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
# cmap = mpl.cm.get_cmap('RdYlGn_r')
dq_cm = create_dq_cmap()

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
                   bottom=(day+1)
                   )
    )
    cong = [(el - 1.0) / 0.5 for el in df['LOTTR'].values]
    # print(cong)
    for val, bar in zip(cong, bars[-1]):
        bar.set_facecolor(dq_cm(val))  # cmap(val)
        # bar.set_alpha(0.8)


ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
# plt.ylim(0, 7)
# ax.set_yticks([0, 1, 2, 3, 4, 5, 6])
plt.ylim(0, 8)
ax.set_yticks([1, 2, 3, 4, 5, 6, 7])
ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax.set_title('Time of Day Reliability (LOTTR) by Day of Week')
ax.xaxis.grid(False)

ax_cb = fig.add_axes([0.9, 0.1, 0.03, 0.8])
cNorm = mpl.colors.Normalize(vmin=1, vmax=2.0)
cb1 = mpl.colorbar.ColorbarBase(ax_cb, norm=cNorm, cmap=dq_cm, ticks=[1, 1.5, 2.0])  # cmap='Reds' or cmap='RdYlGn_r'
cb1.ax.set_yticklabels(['1.0', '1.5', '2+'])
plt.show()