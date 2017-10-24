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

