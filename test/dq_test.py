import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from viz_qt import extract_vals, create_columns
import matplotlib.colors as mcolors
from matplotlib.ticker import FuncFormatter
import calendar
from datetime import datetime, timedelta
from datetime import time as dtime

def make_colormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
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


c = mcolors.ColorConverter().to_rgb
rvb1 = make_colormap(
    [c('indigo'), c('red'), 0.5, c('red'), c('orange'), 0.6, c('orange'), c('yellow'), 0.7, c('yellow'), c('lightgreen'), 0.8, c('lightgreen'), c('green'), 0.9, c('green')])
rvb2 = make_colormap(
    [c('indigo'), c('indigo'), 0.25, c('indigo'), c('red'), 0.5, c('red'), c('orange'), 0.6, c('orange'), c('yellow'), 0.7, c('yellow'), c('lightgreen'), 0.8, c('lightgreen'), c('green'), 0.9, c('green')])
# N = 1000
# array_dg = np.random.uniform(0, 10, size=(N, 2))
# colors = np.random.uniform(-2, 2, size=(N,))
# plt.scatter(array_dg[:, 0], array_dg[:, 1], c=colors, cmap=rvb)
# plt.colorbar()
# plt.show()


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


fig_title = 'PTSU Case Study: I-66 EB - Facility Data Quality'
tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_AllDays_NPMRDS/' + tmc_path)
df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_AllDays_NPMRDS/I66_EB_AllDays_NPMRDS.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Ext13Mi_20130701_20170131/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Ext13Mi_20130701_20170131/I495_VA_NB_Ext13Mi_20130701_20170131.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_NB_Extended_20140901_20170131/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_NB_Extended_20140901_20170131/TX161_TX_NB_Extended_20140901_20170131.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_SB_Extended_20140901_20170131/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_SB_Extended_20140901_20170131/TX161_TX_SB_Extended_20140901_20170131.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_15Min_2016_AllDays/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/21538 - STOL Freeway Merge Analysis/I95_PA_15Min_2016_AllDays/I95_PA_15Min_2016_AllDays.csv')
# tmc = pd.read_csv('C:/Users/ltrask/PycharmProjects/NPMRDS_Data_Tool/AlaskanWayVia_NB_20140101_20170131/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/PycharmProjects/NPMRDS_Data_Tool/AlaskanWayVia_NB_20140101_20170131/AlaskanWayVia_NB_20140101_20170131.csv')
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

num_dates = len(df_dir1['Date'].unique())

facility = True
facility_comp = False
all_tmc = False

if facility:
    rows = 2
    cols = 2
    num_tmc = len(df_dir1['tmc_code'].unique())

    # Creating Facility Data
    # Data Quality by Month
    # td_facility_Month = df_dir1.groupby(['Month', 'Date']).agg(['count'])['speed'] / ((12 * 24) * num_tmc)
    # td1_facility_Month = td_facility_Month.groupby(['Month']).agg(np.mean)
    # Data Quality by Day of Week
    td_facility_Wkdy = df_dir1.groupby(['weekday', 'Date']).agg(['count'])['speed'] / ((12 * 24) * num_tmc)
    td1_facility_Wkdy = td_facility_Wkdy.groupby(['weekday']).agg(np.mean)
    # Data Quality by Time of Day
    td_facility_ToD = df_dir1.groupby(['Hour']).agg(['count'])
    td1_facility_ToD = td_facility_ToD['speed']['count'] / (12 * num_dates * num_tmc)
    radii = td1_facility_ToD.values
    N = len(radii)
    bottom = 0
    width = (2 * np.pi) / N
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    # Data Quality by TMC
    td_facility_TMC = df_dir1.groupby(['tmc_code']).agg(['count'])
    td1_facility_TMC = td_facility_TMC['speed']['count'] / ((12 * 24) * num_dates)
    td1_facility_TMC = td1_facility_TMC.reindex(tmc['tmc'])
    # Data Quality by Month over Time
    # td_facility_SP = df_dir1.groupby(['Date']).agg(['count'])['speed'] / ((12*24) * num_tmc)
    s_date = df_dir1['Date'].min()
    date_tokens = s_date.split('-')
    s_year = int(date_tokens[0])
    s_month = int(date_tokens[1])
    wd = df_dir1[df_dir1['weekday'].isin([0, 1, 2, 3, 4])].groupby(['Year', 'Month', 'Date']).agg(['count'])['speed'] / ((12 * 24) * num_tmc)
    wdv = wd.groupby(['Year', 'Month']).agg(np.mean)
    y_wd = wdv.values.reshape((wdv.shape[0],))
    we = df_dir1[df_dir1['weekday'].isin([5, 6])].groupby(['Year', 'Month', 'Date']).agg(['count'])['speed'] / ((12 * 24) * num_tmc)
    wev = we.groupby(['Year', 'Month']).agg(np.mean)
    y_we = wev.values.reshape((wev.shape[0],))

    # # Data Quality by Month
    # td_facility_Month = df_dir1.groupby(['Month', 'Date']).agg(['count'])['speed'] / ((12 * 24) * num_tmc)
    # td1_facility_Month = td_facility_Month.groupby(['Month']).agg(np.mean)
    # ax1 = plt.subplot(rows, cols, 1)
    # # ax1.get_yaxis().set_visible(False)
    # ax1.set_yticks([0.5, 0.8])
    # ax1.set_yticklabels(['50%', '80%'])
    # ax1.set_title('Data Quality by Month of Year')
    # ax1.set_ylim(0, 1)
    # ax1.set_xticks([el for el in range(1, 13)])
    # ax1.set_xticklabels([calendar.month_abbr[el] for el in range(1, 13)], rotation='vertical')
    # y_values = td1_facility_Month.values.reshape(12,)
    # ax1.plot([el+1 for el in range(len(y_values))], [0.8 for el in range(len(y_values))], label='80%', c='green', ls=':')
    # ax1.plot([el+1 for el in range(len(y_values))], [0.5 for el in range(len(y_values))], label='50%', c='firebrick', ls=':')
    # ax1.legend()
    # bars1 = ax1.bar([el+1 for el in range(12)], y_values)
    # # Use custom colors and opacity
    # for r, bar in zip(y_values, bars1):
    #     # bar.set_facecolor(plt.cm.RdYlGn(r / 10.))
    #     bar.set_facecolor(rvb2(r))
    #     bar.set_alpha(0.8)

    # Data Quality by Day of Week
    ax1 = plt.subplot(rows, cols, 1)
    # ax1.get_yaxis().set_visible(False)
    ax1.set_yticks([0.5, 0.8])
    ax1.set_yticklabels(['50%', '80%'])
    ax1.set_title('Data Quality by Day of Week')
    ax1.set_ylim(0, 1)
    ax1.set_xticks([el for el in range(td1_facility_Wkdy.shape[0])])
    ax1.set_xticklabels([calendar.day_abbr[el] for el in range(td1_facility_Wkdy.shape[0])], rotation='vertical')
    y_values = td1_facility_Wkdy.values.reshape(td1_facility_Wkdy.shape[0], )
    ax1.plot([el for el in range(len(y_values))], [0.8 for el in range(len(y_values))], label='80%', c='green', ls=':')
    ax1.plot([el for el in range(len(y_values))], [0.5 for el in range(len(y_values))], label='50%', c='firebrick', ls=':')
    ax1.legend()
    bars1 = ax1.bar([el for el in range(td1_facility_Wkdy.shape[0])], y_values)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    # Use custom colors and opacity
    for r, bar in zip(y_values, bars1):
        # bar.set_facecolor(plt.cm.RdYlGn(r / 10.))
        bar.set_facecolor(rvb2(r))
        bar.set_alpha(0.8)

    # Data Quality by Time of Day
    ax2 = plt.subplot(rows, cols, 2, polar=True)
    ax2.set_theta_zero_location('N')
    ax2.set_theta_direction(-1)
    ax2.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
    # ax2.get_yaxis().set_visible(False)
    ax2.set_yticks([0.5, 0.8])
    ax2.set_yticklabels(['50%', '80%'])
    ax2.set_title('Data Quality by Time of Day')
    ax2.set_ylim(0, 1)
    bars2 = ax2.bar(theta, radii, width=width, bottom=bottom)
    # Use custom colors and opacity
    for r, bar in zip(radii, bars2):
        bar.set_facecolor(rvb2(r))
        bar.set_alpha(0.8)

    # Data Quality by TMC
    ax3 = plt.subplot(rows, cols, 3)
    # ax3.get_yaxis().set_visible(False)
    ax3.set_yticks([0.5, 0.8])
    ax3.set_yticklabels(['50%', '80%'])
    ax3.set_title('Data Quality by TMC')
    ax3.set_ylim(0, 1)
    ax3.plot([el for el in range(num_tmc)], [0.8 for el in range(num_tmc)], label='80%', c='green', ls=':')
    ax3.plot([el for el in range(num_tmc)], [0.5 for el in range(num_tmc)], label='50%', c='firebrick', ls=':')
    ax3.legend()
    bars3 = ax3.bar([el for el in range(num_tmc)], td1_facility_TMC.values)
    ax3.set_xticks([el for el in range(num_tmc)])
    ax3.set_xticklabels(td1_facility_TMC.index.tolist(), rotation='vertical')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    # Use custom colors and opacity
    for r, bar in zip(td1_facility_TMC.values, bars3):
        bar.set_facecolor(rvb2(r))
        bar.set_alpha(0.8)

    # Data Quality over Study Period
    ax4 = plt.subplot(rows, cols, 4)
    # ax4.get_yaxis().set_visible(False)
    # ax4.set_yticks([0.5, 0.8])
    # ax4.set_yticklabels(['50%', '80%'])
    ax4.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    x_labels = []
    year = s_year
    month = s_month
    for i in range(len(y_wd)):
        x_labels.append(str(month) + '/' + str(year))
        month += 1
        if month > 12:
            month = 1
            year += 1
    ax4.set_xticks([el for el in range(len(y_wd))])
    ax4.set_xticklabels(x_labels, rotation='vertical')
    ax4.set_title('Monthly Data Quality over Time')
    ax4.set_ylim(0, 1)
    # ax4.grid(color='grey')
    lines4a = ax4.plot([el for el in range(len(y_wd))], y_wd, c='grey',  label='Weekdays')
    lines4b = ax4.plot([el for el in range(len(y_we))], y_we, c='grey', ls='--', label='Weekends')
    ax4.plot([el for el in range(len(y_wd))], [0.8 for el in range(len(y_wd))], label='80%', c='green', ls=':')
    ax4.plot([el for el in range(len(y_wd))], [0.5 for el in range(len(y_wd))], label='50%', c='firebrick', ls=':')
    ax4.legend()
    width = 0.35
    bars_wd = ax4.bar([el for el in range(len(y_wd))], y_wd, width, label='Weekdays')
    bars_we = ax4.bar([el+width for el in range(len(y_we))], y_we, width, label='Weekends')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    for r, bar in zip(y_wd, bars_wd):
        bar.set_facecolor(rvb2(r))
        # bar.set_alpha(0.8)
    for r, bar in zip(y_we, bars_we):
        bar.set_facecolor(rvb2(r))
        # bar.set_alpha(0.8)

    plt.suptitle(fig_title)
    plt.show()


if facility_comp:
    rows = 2
    cols = 3
    num_tmc = len(df_dir1['tmc_code'].unique())
    td_facility = df_dir1.groupby(['Hour']).agg(['count'])
    td1_facility = td_facility['speed']['count'] / (12 * num_dates * num_tmc)

    radii = td1_facility.values
    N = len(radii)
    bottom = 0
    width = (2 * np.pi) / N
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    # Default RdYlGn
    ax1 = plt.subplot(rows, cols, 1, polar=True)
    ax1.set_theta_zero_location('N')
    ax1.set_theta_direction(-1)
    ax1.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
    # ax1.get_yaxis().set_visible(False)
    ax1.set_yticks([0.5, 0.8])
    ax1.set_yticklabels(['50%', '80%'])
    ax1.set_title('Default Red-Yellow-Green')
    ax1.set_ylim(0, 1)
    bars1 = ax1.bar(theta, radii, width=width, bottom=bottom)
    # Use custom colors and opacity
    for r, bar in zip(radii, bars1):
        # bar.set_facecolor(plt.cm.RdYlGn(r / 10.))
        bar.set_facecolor(plt.cm.RdYlGn(r))
        bar.set_alpha(0.8)

    # Custom colormap #1
    ax2 = plt.subplot(rows, cols, 2, polar=True)
    ax2.set_theta_zero_location('N')
    ax2.set_theta_direction(-1)
    ax2.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
    # ax2.get_yaxis().set_visible(False)
    ax2.set_yticks([0.5, 0.8])
    ax2.set_yticklabels(['50%', '80%'])
    ax2.set_title('Custom Colormap #1')
    ax2.set_ylim(0, 1)
    bars2 = ax2.bar(theta, radii, width=width, bottom=bottom)
    # Use custom colors and opacity
    for r, bar in zip(radii, bars2):
        bar.set_facecolor(rvb1(r))
        bar.set_alpha(0.8)

    # Custom colormap #2
    ax3 = plt.subplot(rows, cols, 3, polar=True)
    ax3.set_theta_zero_location('N')
    ax3.set_theta_direction(-1)
    ax3.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
    # ax3.get_yaxis().set_visible(False)
    ax3.set_yticks([0.5, 0.8])
    ax3.set_yticklabels(['50%', '80%'])
    ax3.set_title('Custom Colormap #2')
    ax3.set_ylim(0, 1)
    bars3 = ax3.bar(theta, radii, width=width, bottom=bottom)
    # Use custom colors and opacity
    for r, bar in zip(radii, bars3):
        bar.set_facecolor(rvb2(r))
        bar.set_alpha(0.8)

    # Default colormap w/ min 50%
    ax4 = plt.subplot(rows, cols, 4, polar=True)
    ax4.set_theta_zero_location('N')
    ax4.set_theta_direction(-1)
    ax4.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
    # ax4.get_yaxis().set_visible(False)
    ax4.set_yticks([0.5, 0.8])
    ax4.set_yticklabels(['50%', '80%'])
    ax4.set_title('Default Red-Yellow-Green w/ min 50%')
    ax4.set_ylim(0, 1)
    ax4.grid(color='grey')
    radii_min50 = [np.max([0.5, el]) for el in radii]
    bars4 = ax4.bar(theta, radii_min50, width=width, bottom=bottom)
    # Use custom colors and opacity
    for r, bar in zip(radii, bars4):
        bar.set_facecolor(plt.cm.RdYlGn(r))
        bar.set_alpha(0.8)

    # Custom colormap w/ min 50%
    ax5 = plt.subplot(rows, cols, 5, polar=True)
    ax5.set_theta_zero_location('N')
    ax5.set_theta_direction(-1)
    ax5.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
    # ax5.get_yaxis().set_visible(False)
    ax5.set_yticks([0.5, 0.8])
    ax5.set_yticklabels(['50%', '80%'])
    ax5.set_title('Custom Colormap #1 w/ min 50%')
    ax5.set_ylim(0, 1)
    ax5.grid(color='grey')
    radii_min50 = [np.max([0.5, el]) for el in radii]
    bars5 = ax5.bar(theta, radii_min50, width=width, bottom=bottom)
    # Use custom colors and opacity
    for r, bar in zip(radii, bars5):
        bar.set_facecolor(rvb1(r))
        bar.set_alpha(0.8)

    # Custom colormap w/ min 50%
    ax6 = plt.subplot(rows, cols, 6, polar=True)
    ax6.set_theta_zero_location('N')
    ax6.set_theta_direction(-1)
    ax6.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
    # ax6.get_yaxis().set_visible(False)
    ax6.set_yticks([0.5, 0.8])
    ax6.set_yticklabels(['50%', '80%'])
    ax6.set_title('Custom Colormap #2 w/ min 50%')
    ax6.set_ylim(0, 1)
    ax6.grid(color='grey')
    radii_min50 = [np.max([0.5, el]) for el in radii]
    bars6 = ax6.bar(theta, radii_min50, width=width, bottom=bottom)
    # Use custom colors and opacity
    for r, bar in zip(radii, bars6):
        bar.set_facecolor(rvb2(r))
        bar.set_alpha(0.8)

    plt.show()
    # ax1.get_figure().tight_layout()


if all_tmc:
    td_tmc = df_dir1.groupby(['tmc_code', 'Hour']).agg(['count'])
    td1_tmc = td_tmc['speed']['count'] / (12 * num_dates)

    num_tmc = len(td1_tmc.index.levels[0])
    bottom = 0
    idx = 1
    for tmc, new_df in td1_tmc.groupby(level=0):
        radii = new_df[tmc].values
        N = len(radii)
        width = (2 * np.pi) / N
        theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
        ax = plt.subplot(5, 4, idx, polar=True)
        idx += 1
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
        ax.get_yaxis().set_visible(False)
        ax.set_title('TMC: ' + tmc)
        ax.set_ylim(0, 1)
        if len(theta) == len(radii):
            bars = ax.bar(theta, radii, width=width, bottom=bottom)

        # Use custom colors and opacity
        for r, bar in zip(radii, bars):
            # bar.set_facecolor(plt.cm.jet(r / 10.))
            bar.set_facecolor(rvb1(r))
            bar.set_alpha(0.8)

    plt.show()


