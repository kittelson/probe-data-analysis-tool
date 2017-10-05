import pandas as pd
import datetime
from data_import import create_casestudy
from stat_func import create_tt_analysis, create_tt_compare
import time


def extract_vals(date_str):
    # print(date_str)
    date, time = date_str.split(' ')
    [hour, minute, second] = [int(val) for val in time.split(':')]
    [year, month, day] = [int(val) for val in date.split('-')]
    day_type = datetime.datetime(year, month, day).weekday()
    ap = (hour * 12) + minute // 5
    return date, year, month, day, ap, day_type


def extract_vals2(date_str, open_date1, open_date2):
    #print(date_str)
    date, time = date_str.split(' ')
    [hour, minute, second] = [int(val) for val in time.split(':')]
    [year, month, day] = [int(val) for val in date.split('-')]
    region = 2
    day_type = datetime.datetime(year, month, day).weekday()
    if datetime.date(year, month, day) < open_date1:
        region = 1
    elif datetime.date(year, month, day) > open_date2:
        region = 3
    ap = (hour * 12) + minute // 5
    return date, year, month, day, ap, region, day_type
    # return date, ap, region, day_type


def extract_vals3(tstamp, open_date1, open_date2):
    region = 2
    day_type = tstamp.weekday()
    if tstamp < open_date1:
        region = 1
    elif tstamp > open_date2:
        region = 3
    ap = (tstamp.hour * 12) + tstamp.minute // 5
    return tstamp.date, ap, region, day_type


def create_columns(data, is_case_study=False):
    if is_case_study is False:
        dates, years, months, days, aps, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(weekday)
    else:
        dates, years, months, days, aps, regions, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(regions), list(weekday)


def run_viz(case_study_idx, print_csv=True):
    fname, tmc, site_name, start_date, open_date1, open_date2, end_date = create_casestudy(case_study_idx)

    title1 = site_name + ':  Before PTSU (' + start_date.strftime('%m/%d/%Y') + '-' + open_date1.strftime('%m/%d/%Y') + ')'
    title2 = site_name + ':  Interim/Construction of PTSU (' + open_date1.strftime('%m/%d/%Y') + '-' + open_date2.strftime('%m/%d/%Y') + ')'
    title3 = site_name + ':  Active PTSU (' + open_date2.strftime('%m/%d/%Y') + '-' + end_date.strftime('%m/%d/%Y') + ')'

    # Reading and dropping all null values
    df = pd.read_csv(fname)
    df = df[df.speed.notnull()]
    df['Date'], df['AP'], df['region'], df['weekday'] = create_columns(
        [extract_vals2(dStr, open_date1, open_date2) for dStr in df['measurement_tstamp']], is_case_study=True)

    # Creating Before Data
    df1 = df[df.region == 1]
    tt1 = create_tt_analysis(df1)
    # fig_tt1 = travel_time_band(tt1, title1)
    #fig_et1 = extra_time(tt1, title1)

    # Creating Interim Data
    df2 = df[df.region == 2]
    tt2 = create_tt_analysis(df2)
    # fig_tt2 = travel_time_band(tt2, title2)
    #fig_et2 = extra_time(tt2, title2)

    # Creating After/Active PTSU Data
    df3 = df[df.region == 3]
    tt3 = create_tt_analysis(df3)
    # fig_tt3 = travel_time_band(tt3, title3)
    #fig_et3 = extra_time(tt3, title3)

    # Creating before/after travel time percentile comparison
    #fig_tt_comp = pct_compare(tt1, tt3, site_name)
    tt_comp = create_tt_compare(tt1, tt3)
    if print_csv:
        tt_comp.to_csv('static/tt_pct_comp.csv')

    print('done')
    return [tt1, tt2, tt3], tt_comp


def run_viz_day(case_study_idx, day_list, include_tmc=None, print_csv=True, return_tt=True):
    fname, tmc, site_name, start_date, open_date1, open_date2, end_date = create_casestudy(case_study_idx)

    title1 = site_name + ':  Before PTSU (' + start_date.strftime('%m/%d/%Y') + '-' + open_date1.strftime('%m/%d/%Y') + ')'
    title2 = site_name + ':  Interim/Construction of PTSU (' + open_date1.strftime('%m/%d/%Y') + '-' + open_date2.strftime('%m/%d/%Y') + ')'
    title3 = site_name + ':  Active PTSU (' + open_date2.strftime('%m/%d/%Y') + '-' + end_date.strftime('%m/%d/%Y') + ')'

    # Reading and dropping all null values
    df = pd.read_csv(fname) # , parse_dates=['measurement_tstamp']
    df = df[df.speed.notnull()]

    time1 = time.time()
    new_mat = [extract_vals2(dStr, open_date1, open_date2) for dStr in df['measurement_tstamp']]
    # open_date1_tstamp = pd.Timestamp(open_date1)
    # open_date2_tstamp = pd.Timestamp(open_date2)
    # new_mat = [extract_vals3(ts, open_date1_tstamp, open_date2_tstamp) for ts in df['measurement_tstamp']]
    time2 = time.time()
    print('Mat Creation: ' + str(time2 - time1))
    time1 = time.time()
    df['Date'], df['AP'], df['region'], df['weekday'] = create_columns(new_mat, is_case_study=True)
    time2 = time.time()
    print('DF Creation: '+str(time2-time1))

    # Filtering to selected set of days
    if len(day_list) > 0:
        df = df[df['weekday'].isin(day_list)]

    if include_tmc is not None:
        df = df[df['tmc_code'].isin(include_tmc)]

    time1 = time.time()
    # Creating Before Data
    df1 = df[df.region == 1]

    # Creating Interim Data
    df2 = df[df.region == 2]

    # Creating After/Active PTSU Data
    df3 = df[df.region == 3]
    time2 = time.time()
    print('DF Region Filtering: ' + str(time2 - time1))

    time1 = time.time()
    if return_tt:
        tt1 = create_tt_analysis(df1)
        tt2 = create_tt_analysis(df2)
        tt3 = create_tt_analysis(df3)
        # Creating before/after travel time percentile comparison
        tt_comp = create_tt_compare(tt1, tt3)
        if print_csv:
            tt_comp.to_csv('static/tt_pct_comp.csv')
        return [tt1, tt2, tt3], tt_comp, df['weekday'].unique().tolist(), [title1, title2, title3]
    time2 = time.time()
    print('Run Viz TT Analysis: ' + str(time2 - time1))


    print('done')
    return tmc, [df1, df2, df3], None, df['weekday'].unique().tolist(), [title1, title2, title3]



