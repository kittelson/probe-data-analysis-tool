import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from viz import extract_vals, create_columns2
from stat_func import percentile


cs_idx = 5
day_subset = [0, 1, 2, 3, 4]  # Monday = 0, ..., Sunday = 6
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
df_dir1['Date'], df_dir1['Year'], df_dir1['Month'], df_dir1['Day'], df_dir1['AP'], df_dir1['weekday'] = create_columns2(new_mat)
time2 = time.time()
print('df_dir1 Creation: '+str(time2-time1))
# Filtering to selected set of days
if len(day_subset) > 0:
  df_dir1 = df_dir1[df_dir1['weekday'].isin(day_subset)]

df_dir1_am = df_dir1[(df_dir1['AP'] >= am_ap_start) & (df_dir1['AP'] < am_ap_end)]
df_dir1_pm = df_dir1[(df_dir1['AP'] >= pm_ap_start) & (df_dir1['AP'] < pm_ap_end)]

# AM Peak Period
am_gp0 = df_dir1_am.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
am_num_observations = am_gp0.count()
#am_num_observations.groupby(['Year', 'Month']).agg(np.mean)
am_gp = am_gp0.agg([np.mean, percentile(95), percentile(5)])
am_gp1 = am_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
am_gp2 = am_gp1.groupby(['Year', 'Month']).agg(np.mean)

# PM Peak Period
pm_gp0 = df_dir1_pm.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
pm_num_observations = pm_gp0.count()
#Pm_num_observations.groupby(['Year', 'Month']).agg(np.mean)
pm_gp = pm_gp0.agg([np.mean, percentile(95), percentile(5)])
pm_gp1 = pm_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
pm_gp2 = pm_gp1.groupby(['Year', 'Month']).agg(np.mean)

#plot_df = am_gp2.to_frame('AM').join(pm_gp2.to_frame('PM'))
plot_df_dir1 = am_gp2.join(pm_gp2, lsuffix='pm')

# Creating data for direction #2
time1 = time.time()
new_mat = [extract_vals(dStr) for dStr in df_dir2['measurement_tstamp']]
time2 = time.time()
print('Mat Creation: ' + str(time2 - time1))
time1 = time.time()
df_dir2['Date'], df_dir2['Year'], df_dir2['Month'], df_dir2['Day'], df_dir2['AP'], df_dir2['weekday'] = create_columns2(new_mat)
time2 = time.time()
print('df_dir2 Creation: '+str(time2-time1))
# Filtering to selected set of days
if len(day_subset) > 0:
  df_dir2 = df_dir2[df_dir2['weekday'].isin(day_subset)]

df_dir2_am = df_dir2[(df_dir2['AP'] >= am_ap_start) & (df_dir2['AP'] < am_ap_end)]
df_dir2_pm = df_dir2[(df_dir2['AP'] >= pm_ap_start) & (df_dir2['AP'] < pm_ap_end)]

# AM Peak Period
am_gp0 = df_dir2_am.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
am_num_observations = am_gp0.count()
#am_num_observations.groupby(['Year', 'Month']).agg(np.mean)
am_gp = am_gp0.agg([np.mean, percentile(95), percentile(5)])
am_gp1 = am_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
am_gp2 = am_gp1.groupby(['Year', 'Month']).agg(np.mean)

# PM Peak Period
pm_gp0 = df_dir2_pm.groupby(['Year', 'Month', 'AP', 'tmc_code'])['travel_time_minutes']
pm_num_observations = pm_gp0.count()
#Pm_num_observations.groupby(['Year', 'Month']).agg(np.mean)
pm_gp = pm_gp0.agg([np.mean, percentile(95), percentile(5)])
pm_gp1 = pm_gp.groupby(['Year', 'Month', 'AP']).agg(np.sum)
pm_gp2 = pm_gp1.groupby(['Year', 'Month']).agg(np.mean)

#plot_df = am_gp2.to_frame('AM').join(pm_gp2.to_frame('PM'))
plot_df_dir2 = am_gp2.join(pm_gp2, lsuffix='pm')

# facility_len = tmc.miles.sum()
# ax = plot_df.plot()
# ax.set_title('Peak Travel Times over Time' + ' (' + '{:1.2f}'.format(facility_len) + ' mi)')
# ax.set_ylabel('Travel Time (Minutes)')
# plt.show()

tt_am_mean_dir1 = plot_df_dir1['mean']
tt_am_pct5_dir1 = plot_df_dir1['percentile_5']
tt_am_pct95_dir1 = plot_df_dir1['percentile_95']
tt_pm_mean_dir1 = plot_df_dir1['meanpm']
tt_pm_pct5_dir1 = plot_df_dir1['percentile_5pm']
tt_pm_pct95_dir1 = plot_df_dir1['percentile_95pm']

tt_am_mean_dir2 = plot_df_dir2['mean']
tt_am_pct5_dir2 = plot_df_dir2['percentile_5']
tt_am_pct95_dir2 = plot_df_dir2['percentile_95']
tt_pm_mean_dir2 = plot_df_dir2['meanpm']
tt_pm_pct5_dir2 = plot_df_dir2['percentile_5pm']
tt_pm_pct95_dir2 = plot_df_dir2['percentile_95pm']

x = [el for el in range(len(tt_am_mean_dir1))]

fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)

ax1.plot(x, tt_am_mean_dir1, color='C0', linestyle='-', lw=2.0, label='AM-Mean')
ax1.plot(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
ax1.plot(x, tt_am_pct95_dir1, color='C0', linestyle='--', lw=1.0, label='AM-95th Pct')

ax1.plot(x, tt_pm_mean_dir1, color='C1', linestyle='-', lw=2.0, label='PM-Mean')
ax1.plot(x, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
ax1.plot(x, tt_pm_pct95_dir1, color='C1', linestyle='--', lw=1.0, label='PM-95th Pct')

ax1.set_title(dirs[0] + ' Peak Travel Times over Time' + ' (' + '{:1.2f}'.format(facility_len1) + ' mi)')
ax1.set_ylabel('Travel Time (Minutes)')
ax1.legend()
ax1.set_xticks([0, 5, 10, 15, 20])
ax1.set_xticklabels(['2015 Dec', '2016 May', '2016 Oct', '2017 March', '2017 Aug'])

ax2.plot(x, tt_am_mean_dir2, color='C2', linestyle='-', lw=2.0, label='AM-Mean')
ax2.plot(x, tt_am_pct5_dir2, color='C2', linestyle='--', lw=1.0, label='AM-5th Pct')
ax2.plot(x, tt_am_pct95_dir2, color='C2', linestyle='--', lw=1.0, label='AM-95th Pct')

ax2.plot(x, tt_pm_mean_dir2, color='C3', linestyle='-', lw=2.0, label='PM-Mean')
ax2.plot(x, tt_pm_pct5_dir2, color='C3', linestyle='--', lw=1.0, label='PM-5th Pct')
ax2.plot(x, tt_pm_pct95_dir2, color='C3', linestyle='--', lw=1.0, label='PM-95th Pct')

ax2.set_title(dirs[1] + ' Peak Travel Times over Time' + ' (' + '{:1.2f}'.format(facility_len2) + ' mi)')
ax2.set_ylabel('Travel Time (Minutes)')
ax2.legend()
ax2.set_xticks([0, 5, 10, 15, 20])
ax2.set_xticklabels(['2015 Dec', '2016 May', '2016 Oct', '2017 March', '2017 Aug'])