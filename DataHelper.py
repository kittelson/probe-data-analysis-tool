import calendar

class DataHelper:
    def __init__(self):
        self.curr_cs_idx = -1
        self.curr_subset_idx = -1
        self.site_name = ''
        self.tmc_df = None
        self.data = None
        self.tt_comp = None
        self.available_days = None
        self.available_months = None
        self.titles = None
        self.tmc_subset = []

    def set_curr_cs_idx(self, index):
        self.curr_cs_idx = index

    def set_site_name(self, name):
        self.site_name = name

    def set_tmc_list(self, tmc_list):
        self.tmc_df = tmc_list

    def set_data(self, data):
        self.data = data

    def set_tt_comp(self, tt_comp):
        self.tt_comp = tt_comp

    def set_available_days(self, available_days):
        self.available_days = available_days

    def set_available_months(self, available_months):
        self.available_months = available_months

    def set_titles(self, titles):
        self.titles = titles

    def add_tmc_subset(self, tmc_subset):
        self.tmc_subset.append(tmc_subset)
        return len(self.tmc_subset) - 1

    def get_tmc_subset(self, subset_idx):
        if subset_idx < len(self.tmc_subset):
            return self.tmc_subset[subset_idx]
        else:
            return []

    def set_active_subset(self, subset_idx):
        self.curr_subset_idx = subset_idx

    def get_active_subset(self):
        return self.curr_subset_idx

    def get_tmc_list(self):
        if self.curr_subset_idx < 0:
            return self.tmc_df
        else:
            return self.tmc_df[self.tmc_df['tmc'].isin(self.tmc_subset[self.curr_subset_idx])]


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

    def get_tmcs(self):
        return self._tmcs

    def get_directions(self):
        return self._tmcs['direction'].unique()

    def set_first_date(self, date):
       self._first_date = date

    def get_first_date(self):
        return self._first_date

    def set_last_date(self, date):
        self._last_date = date

    def get_last_date(self):
        return self._last_date

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

