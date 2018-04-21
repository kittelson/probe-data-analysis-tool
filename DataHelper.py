"""
Module for the Database class used by the Project class to store the project data
"""

import calendar
import datetime
from chart_defaults import ChartOptions
import viz_qt
import mpl_charts
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class Project:
    ID_DATA_TMC = 'tmc_code'
    ID_DATA_TIMESTAMP = 'measurement_tstamp'
    ID_DATA_SPEED = 'speed'
    ID_DATA_TT = 'travel_time_minutes'
    ID_DATA_RESOLUTION = 5

    ID_TMC_CODE = 'tmc'
    ID_TMC_DIR = 'direction'
    ID_TMC_LEN = 'miles'
    ID_TMC_INTX = 'intersection'
    ID_TMC_SLAT = 'start_latitude'
    ID_TMC_SLON = 'start_longitude'
    ID_TMC_ELAT = 'end_latitude'
    ID_TMC_ELON = 'end_longitude'

    def __init__(self, project_name, directory, main_window):
        self.main_window = main_window
        self._project_name = project_name
        self._project_analyst = ''
        self._project_agency = ''
        self._project_state = ''
        self._project_location = ''
        self._project_dir = directory
        self._tmc_file_name = None
        self._adj_tmc_list = []
        self._data_file_name = None
        self.database = None
        self._date_ranges = []
        self.chart_panel1_opts = ChartOptions()
        # self.chart_panel1_opts = None  # _Delete
        self.data_res = Project.ID_DATA_RESOLUTION
        self.direction = None
        self._summary_data = None
        self.speed_limit = 65
        self.min_speed = 15
        self.max_speed = 70
        self.data_avail_threshold_lower = 0.5
        self.data_avail_threshold_upper = 0.8

    def set_name(self, new_name):
        self._project_name = new_name

    def get_name(self):
        return self._project_name

    def set_analyst(self, new_analyst):
        self._project_analyst = new_analyst

    def get_analyst(self):
        return self._project_analyst

    def get_agency(self):
        return self._project_agency

    def set_agency(self, new_agency):
        self._project_agency = new_agency

    def get_state(self):
        return self._project_state

    def set_state(self, new_state):
        self._project_state = new_state

    def get_location(self):
        return self._project_location

    def set_location(self, new_location):
        self._project_location = new_location

    def set_tmc_file(self, new_name):
        self._tmc_file_name = new_name

    def get_tmc_file_name(self):
        return self._tmc_file_name

    def set_tmc_list_adj(self, adj_tmc_list):
        self._adj_tmc_list = adj_tmc_list

    def get_tmc_list_adj(self):
        return self._adj_tmc_list

    def set_data_file(self, new_name):
        self._data_file_name = new_name

    def get_data_file_name(self):
        return self._data_file_name

    def add_date_range(self, new_date_range):
        self._date_ranges.append(new_date_range)

    def del_date_range(self, index):
        return self._date_ranges.pop(index)

    def get_date_ranges(self):
        return self._date_ranges

    def get_date_range(self, index):
        return self._date_ranges[index]

    def get_selected_directions(self):
        # direction_list = []
        # root = self.main_window.ui.treeWidget_3.invisibleRootItem()
        # for ti in range(root.child(0).childCount()):
        #     if root.child(0).child(ti).checkState(0):
        #         direction_list.append(root.child(0).child(ti).text(0))

        all_direction_list = self.database.get_directions()
        direction_list = []
        get_selected = self.main_window.ui.treeWidget_3.selectedItems()
        if get_selected:
            base_node = get_selected[0]
            get_child_node = base_node.text(0)
            if get_child_node in all_direction_list:
                direction_list.append(get_child_node)
            elif get_child_node == self._project_name:
                direction_list.append(all_direction_list[0])
            else:
                direction_list.append(base_node.parent().text(0))
        else:
            direction_list.append(all_direction_list[0])
        self.direction = direction_list[0]
        return direction_list

    def get_tmc(self, full_list=False, as_list=False):
        if full_list:
            return self.database.get_tmcs(as_list=as_list)
        else:
            tmc_list = self.database.get_tmcs()
            if self.direction is None:
                subset_dirs = self.get_selected_directions()
            else:
                subset_dirs = [self.direction]
            subset_tmc = tmc_list[tmc_list[Project.ID_TMC_DIR].isin(subset_dirs)]
            subset_tmc.reset_index(inplace=True)
            if as_list:
                return subset_tmc[Project.ID_TMC_CODE]
            else:
                return subset_tmc

    def load(self):
        viz_qt.LoadProjectQT(self.main_window, create_database=True, print_csv=False)

    def loaded(self):
        self.main_window.add_project(self)

    def summary_data(self):
        return self._summary_data

    def set_summary_data(self, summary):
        self._summary_data = summary

    def compute_sample_size(self, period_idx, tmc_code):
        if self.database is not None and len(self._date_ranges) > period_idx and tmc_code in self.get_tmc(full_list=True, as_list=True).tolist():
            dr1 = self.get_date_range(period_idx)
            df = self.database.get_data()
            df_tmc = df[(df[Project.ID_DATA_TMC].isin([tmc_code]))]
            df_period = df_tmc[(df_tmc['Date'] >= dr1[0].toString('yyyy-MM-dd')) & (df_tmc['Date'] <= dr1[1].toString('yyyy-MM-dd'))]
            return df_period[Project.ID_DATA_SPEED].count()
        else:
            return 0


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
            return self._tmcs[Project.ID_TMC_CODE]
        else:
            return self._tmcs

    def get_directions(self):
        return self._tmcs[Project.ID_TMC_DIR].unique()

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
        tmc_df = project.get_tmc(full_list=True)
        self._tmc_len = tmc_df[tmc_df[Project.ID_TMC_CODE] == tmc][Project.ID_TMC_LEN].iloc[0]
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
        self._lottr_corr = dict()
        self._lottr_corr['AM'] = [dict(), dict()]
        self._lottr_corr['PM'] = [dict(), dict()]
        self._lottr_corr['MD-WD'] = [dict(), dict()]
        self._lottr_corr['MD-WE'] = [dict(), dict()]
        self._lott_tmc = dict()
        self._lott_tmc['AM'] = [-1, -1]
        self._lott_tmc['PM'] = [-1, -1]
        self._lott_tmc['MD-WD'] = [-1, -1]
        self._lott_tmc['MD-WE'] = [-1, -1]

    def tmc(self):
        return self._tmc

    def tmc_len(self, as_string=True):
        if as_string:
            return '{:1.2f} mi'.format(self._tmc_len)
        else:
            return self._tmc_len

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

    def set_tmc_lottr_am(self, val, period):
        self._lott_tmc['AM'][period] = val

    def set_tmc_lottr_pm(self, val, period):
        self._lott_tmc['PM'][period] = val

    def set_tmc_lottr_md_wkdy(self, val, period):
        self._lott_tmc['MD-WD'][period] = val

    def set_tmc_lottr_md_wknd(self, val, period):
        self._lott_tmc['MD-WE'][period] = val

    def get_tmc_lottr_am(self, period, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lott_tmc['AM'][period])
        else:
            return self._lott_tmc['AM'][period]

    def get_tmc_lottr_pm(self, period, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lott_tmc['PM'][period])
        else:
            return self._lott_tmc['PM'][period]

    def get_tmc_lottr_md_wkdy(self, period, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lott_tmc['MD-WD'][period])
        else:
            return self._lott_tmc['MD-WD'][period]

    def get_tmc_lottr_md_wknd(self, period, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lott_tmc['MD-WE'][period])
        else:
            return self._lott_tmc['MD-WE'][period]

    def set_lottr_dict_am(self, lottr_dict, period):
        self._lottr_corr['AM'][period] = lottr_dict

    def set_lottr_dict_pm(self, lottr_dict, period):
        self._lottr_corr['PM'][period] = lottr_dict

    def set_lottr_dict_md_wkdy(self, lottr_dict, period):
        self._lottr_corr['MD-WD'][period] = lottr_dict

    def set_lottr_dict_md_wknd(self, lottr_dict, period):
        self._lottr_corr['MD-WE'][period] = lottr_dict

    def get_lottr_dict_am(self, period):
        return self._lottr_corr['AM'][period]

    def get_lottr_dict_pm(self, period):
        return self._lottr_corr['PM'][period]

    def get_lottr_dict_md_wkdy(self, period):
        return self._lottr_corr['MD-WD'][period]

    def get_lottr_dict_md_wknd(self, period):
        return self._lottr_corr['MD-WE'][period]

    def set_corr_lottr_am(self, tmc, val):
        self._lottr_corr['AM'][tmc] = val

    def set_corr_lottr_pm(self, tmc, val):
        self._lottr_corr['PM'][tmc] = val

    def set_corr_lottr_md_wkdy(self, tmc, val):
        self._lottr_corr['MD-WD'][tmc] = val

    def set_corr_lottr_md_wknd(self, tmc, val):
        self._lottr_corr['MD-WE'][tmc] = val

    def get_corr_lottr_am(self, tmc, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lottr_corr['AM'][tmc])
        else:
            return self._lottr_corr['AM'][tmc]

    def get_corr_lottr_pm(self, tmc, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lottr_corr['PM'][tmc])
        else:
            return self._lottr_corr['PM'][tmc]

    def get_corr_lottr_md_wkdy(self, tmc, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lottr_corr['MD-WD'])
        else:
            return self._lottr_corr['MD-WD']

    def get_corr_lottr_md_wknd(self, tmc, as_string=True):
        if as_string:
            return '{:1.2f}'.format(self._lottr_corr['MD-WE'][tmc])
        else:
            return self._lottr_corr['MD-WE'][tmc]

    def generate_lottr_chart(self, project):
        # chart_panel = QWidget()
        chart = mpl_charts.MplChart(None, fig_type=mpl_charts.FIG_TYPE_LOTTR_CORR_SUMM, project=project)
        # layout = QVBoxLayout(chart_panel)
        # layout.addWidget(chart)
        return chart

