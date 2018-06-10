import pandas as pd
import time
from datetime import datetime, timedelta
import datetime as dtime
import numpy as np

data_res = 15

def extract_vals(date_str):
    # ----NPMRDS----
    date, time = date_str.split(' ')[:2]
    time_tokens = time.split(':')
    hour = int(time_tokens[0])
    minute = int(time_tokens[1])
    [year, month, day] = [int(val) for val in date.split('-')]
    day_type = datetime(year, month, day).weekday()
    ap = (hour * (60 // data_res)) + minute // data_res
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


tmc_path = 'TMC_Identification.csv'

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
# tmc = pd.read_csv('C:/Users/ltrask/Documents/18135 - FHWA Sketch Planning Methods/I66_Sample/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/18135 - FHWA Sketch Planning Methods/I66_Sample/I66_Sample.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/13066 - I4 BtU/South Section/2016/I4-South-Section-EB-2016/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/13066 - I4 BtU/South Section/2016/I4-South-Section-EB-2016/I4-South-Section-EB-2016.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Documents/13066 - I4 BtU/South Section/2016/I4-South-Section-WB-2016/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Documents/13066 - I4 BtU/South Section/2016/I4-South-Section-WB-2016/I4-South-Section-WB-2016.csv')
# tmc = pd.read_csv('C:/Users/ltrask/Downloads/SR99-NB-20180301-20180430/' + tmc_path)
# df = pd.read_csv('C:/Users/ltrask/Downloads/SR99-NB-20180301-20180430/SR99-NB-20180301-20180430.csv')
tmc = pd.read_csv('C:/Users/ltrask/Downloads/SR99-SB-20180301-20180430/' + tmc_path)
df = pd.read_csv('C:/Users/ltrask/Downloads/SR99-SB-20180301-20180430/SR99-SB-20180301-20180430.csv')
df = df[df.travel_time_minutes.notnull()]

dirs = tmc['direction'].unique()
tmc_subset1 = tmc[tmc['direction'] == dirs[0]]['tmc']
df_dir1 = df[df['tmc_code'].isin(tmc_subset1)]

# Creating data for direction #1
time1 = time.time()
new_mat = [extract_vals(dStr) for dStr in df_dir1['measurement_tstamp']]
time2 = time.time()
print('Mat Creation: ' + str(time2 - time1))
time1 = time.time()
df_dir1['Date'], df_dir1['Year'], df_dir1['Month'], df_dir1['Day'], df_dir1['AP'], df_dir1['weekday'] = create_columns(new_mat)
start_date = df_dir1['Date'].min()
end_date = df_dir1['Date'].max()
df_dir1['Hour'] = df_dir1['AP'] // (60 / data_res)
time2 = time.time()
print('df_dir1 Creation: '+str(time2-time1))

month_list = [3, 4]
# month_list = [3]
# month_list = [4]
day_list = [1, 2, 3]

df_month = df_dir1[df_dir1['Month'].isin(month_list)]
df_wkdy = df_month[df_month['Day'].isin(day_list)]

df_contour = df_wkdy.groupby(['tmc_code', 'AP']).agg(np.mean)
df_contour = df_contour.reindex(tmc['tmc'].values, level=0)

f_name1 = 'C:/Users/ltrask/Desktop/Sacramento 99/SB_MarAprTWT.csv'
f_c = open(f_name1, 'w')

midnight = datetime(1, 1, 1, 0, 0, 0)
header_str = 'AP'
for tmc_id in tmc['tmc']:
    header_str = header_str + ',' + tmc_id
f_c.write(header_str + '\n')
for ap, row in df_contour.groupby(level=1):
    new_time = midnight + timedelta(minutes=ap*15)
    row_str = str(ap + 1) + ' (' + new_time.strftime('%H:%M%p') + ')'
    for key, val in row['speed'].iteritems():
        row_str = row_str + ',' + str(val)
    f_c.write(row_str + '\n')

f_c.close()

