"""
Module for the Database class used by the Project class to store the project data
"""

import calendar
import datetime


class Database:
    def __init__(self, name, tmcs=None, data=None):
        self._name = name
        self._tmcs = tmcs
        self._data = data
        self._first_date = None
        self._last_date = None
        self._months = None
        self._weekdays = None
        self._weekends = None

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def set_tmcs(self, tmcs):
        self._tmcs = tmcs

    def get_tmcs(self, as_list=False):
        if as_list:
            return self._tmcs['tmc']
        else:
            return self._tmcs

    def get_directions(self):
        return self._tmcs['direction'].unique()

    def set_first_date(self, date):
        self._first_date = date

    def get_first_date(self, as_datetime=False):
        if not as_datetime:
            return self._first_date
        else:
            return datetime.datetime.strptime(self._first_date, '%Y-%m-%d')

    def set_last_date(self, date):
        self._last_date = date

    def get_last_date(self, as_datetime=False):
        if not as_datetime:
            return self._last_date
        else:
            return datetime.datetime.strptime(self._last_date, '%Y-%m-%d')

    def set_available_months(self, months):
        self._months = months

    def get_available_months(self, as_string=False):
        if not as_string:
            return self._months
        else:
            if len(self._months) > 0:
                month_str = calendar.month_abbr[self._months[0]]
                for d in range(1, len(self._months)):
                    month_str += ',' + calendar.month_abbr[self._months[d]]
                return month_str
            else:
                return 'None'

    def set_available_weekdays(self, weekdays):
        self._weekdays = weekdays

    def get_available_weekdays(self, as_string=False):
        if not as_string:
            return self._weekdays
        else:
            if len(self._weekdays) > 0:
                weekday_str = calendar.day_abbr[self._weekdays[0]]
                for d in range(1, len(self._weekdays)):
                    weekday_str += ',' + calendar.day_abbr[self._weekdays[d]]
                return weekday_str
            else:
                return 'None'

    def set_available_weekends(self, weekends):
        self._weekends = weekends

    def get_available_weekends(self, as_string=False):
        if not as_string:
            return self._weekends
        else:
            if len(self._weekends) > 0:
                weekend_str = calendar.day_abbr[self._weekends[0]]
                for d in range(1, len(self._weekends)):
                    weekend_str += ',' + calendar.day_abbr[self._weekends[d]]
                return weekend_str
            else:
                return 'None'

    def get_available_days(self):
        return self._weekdays + self._weekends


class SummaryData:
    def __init__(self, project, tmc):
        self._project = project
        self._tmc = tmc
        self._start_date = []
        self._end_date = []
        self._start_time = []
        self._end_time = []
        self._sample_size = []
        self._num_days = []
        self._am_mean = []
        self._pm_mean = []
        self._md_mean = []
        self._am_95 = []
        self._pm_95 = []
        self._md_95 = []

    def tmc(self):
        return self._tmc

    def start_date(self, period_idx, as_string=True):
        if self._start_date is not None and len(self._start_date) > period_idx:
            if as_string:
                return self._start_date[period_idx].toString('yyyy-MM-dd')
            else:
                return self._start_date[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return None

    def end_date(self, period_idx, as_string=True):
        if self._end_date is not None and len(self._end_date) > period_idx:
            if as_string:
                return self._end_date[period_idx].toString('yyyy-MM-dd')
            else:
                return self._end_date[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return None

    def start_time(self, period_idx, as_string=True):
        if self._start_time is not None and len(self._start_time) > period_idx:
            return self._start_time[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return None

    def end_time(self, period_idx, as_string=True):
        if self._end_time is not None and len(self._end_time) > period_idx:
            return self._end_time[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return None

    def sample_size(self, period_idx, as_string=True):
        if self._sample_size is not None and len(self._sample_size) > period_idx:
            if as_string:
                return str(self._sample_size[period_idx])
            else:
                return self._sample_size[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

    def num_days(self, period_idx, as_string=True):
        if self._num_days is not None and len(self._num_days) > period_idx:
            if as_string:
                return str(self._num_days[period_idx])
            else:
                return self._num_days[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

    def ideal_sample(self, period_idx, as_string=True):
        if self._num_days is not None and len(self._num_days) > period_idx:
            ideal_sample_size = self._num_days[period_idx] * 24 * int(60 / self._project.data_res)
            if as_string:
                return str(ideal_sample_size)
            else:
                return ideal_sample_size
        else:
            if as_string:
                return '--'
            else:
                return 0

    def pct_sample_available(self, period_idx, as_string=True):
        if self._sample_size is not None and len(self._sample_size) > period_idx:
            pct_avail = self._sample_size[period_idx] / self.ideal_sample(period_idx, as_string=False) * 100.0
            if as_string:
                return '{:1.2f}%'.format(pct_avail)
            else:
                return pct_avail
        else:
            if as_string:
                return '--'
            else:
                return 0

    def am_mean(self, period_idx, as_string=True):
        if self._am_mean is not None and len(self._am_mean) > period_idx:
            if as_string:
                return '{:1.2f}'.format(self._am_mean[period_idx])
            else:
                return self._am_mean[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

    def pm_mean(self, period_idx, as_string=True):
        if self._pm_mean is not None and len(self._pm_mean) > period_idx:
            if as_string:
                return '{:1.2f}'.format(self._pm_mean[period_idx])
            else:
                return self._pm_mean[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

    def md_mean(self, period_idx, as_string=True):
        if self._md_mean is not None and len(self._md_mean) > period_idx:
            if as_string:
                return '{:1.2f}'.format(self._md_mean[period_idx])
            else:
                return self._md_mean[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

    def am_95(self, period_idx, as_string=True):
        if self._am_95 is not None and len(self._am_95) > period_idx:
            if as_string:
                return '{:1.2f}'.format(self._am_95[period_idx])
            else:
                return self._am_95[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

    def pm_95(self, period_idx, as_string=True):
        if self._pm_95 is not None and len(self._pm_95) > period_idx:
            if as_string:
                return '{:1.2f}'.format(self._pm_95[period_idx])
            else:
                return self._pm_95[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

    def md_95(self, period_idx, as_string=True):
        if self._md_95 is not None and len(self._md_95) > period_idx:
            if as_string:
                return '{:1.2f}'.format(self._md_95[period_idx])
            else:
                return self._md_95[period_idx]
        else:
            if as_string:
                return '--'
            else:
                return 0

