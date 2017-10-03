import numpy as np
import pandas as pd
import time

def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


def multi_percentile():
    def multi_percentile_(x):
        return np.percentile(x, [95, 50, 5])
    multi_percentile_.__name__ = 'multipct'
    return multi_percentile_


def create_speed_band_analysis(data):
    sb = data.groupby(['AP', 'tmc_code'])['travel_time_minutes'].agg(
        [np.mean, percentile(95), percentile(90), percentile(80), percentile(70), percentile(60), percentile(50), percentile(5)]
    ).groupby(level=0).sum()

    return sb


def create_tt_analysis(data):
    tt = data.groupby(['AP', 'tmc_code'])['travel_time_minutes'].agg(
        [np.mean, percentile(95), percentile(90), percentile(80), percentile(70), percentile(60), percentile(50), percentile(5)]
    ).groupby(level=0).sum()
    tt['extra_time'] = tt['percentile_95']-tt['mean']
    return tt


def create_et_analysis(data):
    if not data.columns.contains('travel_time_minutes'):
        data['travel_time_minutes'] = data['travel_time_seconds']/60
    time1 = time.time()
    et = data.groupby(['AP', 'tmc_code'])['travel_time_minutes'].agg([np.mean, percentile(95), percentile(5)]).groupby(level=0).sum()
    et['extra_time'] = et['percentile_95'] - et['mean']
    time2 = time.time()
    print('Extra Time Analysis: ' + str(time2 - time1))
    return et


def create_tt_compare(data_before, data_after):
    deltas = pd.DataFrame()
    deltas['delta_50'] = data_before['percentile_50'] - data_after['percentile_50']
    deltas['delta_60'] = data_before['percentile_60'] - data_after['percentile_60']
    deltas['delta_70'] = data_before['percentile_70'] - data_after['percentile_70']
    deltas['delta_80'] = data_before['percentile_80'] - data_after['percentile_80']
    deltas['delta_90'] = data_before['percentile_90'] - data_after['percentile_90']
    deltas['delta_95'] = data_before['percentile_95'] - data_after['percentile_95']
    return deltas
