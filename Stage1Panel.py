from PyQt5 import QtWidgets
from stat_func import create_pct_congested_sp, create_pct_congested_tmc, create_speed_heatmap, create_speed_tmc_heatmap
from stat_func import convert_time_to_ap, create_trend_analysis
from chart_defaults import ChartOptions
from mpl_charts import MplChart, FIG_TYPE_SPD_HEAT_MAP_FACILITY, FIG_TYPE_SPD_HEAT_MAP, FIG_TYPE_PCT_CONG_DAY, FIG_TYPE_TT_TREND_LINE, FIG_TYPE_TT_TREND_BAR
from datetime import datetime, timedelta
from viz_qt import LoadSpatialQT, LoadTemporalQT


TYPE_S1_2 = 2
TYPE_S1_3 = 3
TYPE_S1_4 = 4


class Stage1GridPanel(QtWidgets.QWidget):
    def __init__(self, project, panel_type=TYPE_S1_3, options=None):
        QtWidgets.QWidget.__init__(self)
        self.panel_type = panel_type
        self.chart11 = None
        self.chart21 = None
        self.panel_col1 = QtWidgets.QWidget(self)
        self.chart_panel = QtWidgets.QWidget(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout(self.chart_panel)

        self.init_mode = True
        self.no_compute = True

        self.project = project
        facility_tmcs = self.project.get_tmc()  # Gets the tmc list for the selected direction(s)
        self.facility_len = facility_tmcs['miles'].sum()
        self.selected_tmc_name = facility_tmcs['tmc'][0]
        self.selected_tmc_len = facility_tmcs['miles'][0]
        self.dfs = [self.project.database.get_data(), None, None]
        self.available_days = self.project.database.get_available_days()
        self.plot_days = self.available_days.copy()
        self.ap_start = 0
        self.ap_end = 287
        self.peak_period_str = 'Peak Period '
        self.am_ap_start = convert_time_to_ap(6, 0, 5)
        self.am_ap_end = convert_time_to_ap(9, 0, 5)
        self.pm_ap_start = convert_time_to_ap(16, 0, 5)
        self.pm_ap_end = convert_time_to_ap(18, 0, 5)
        self.md_ap_start = convert_time_to_ap(10, 0, 5)
        self.md_ap_end = convert_time_to_ap(16, 0, 5)
        self.titles = ['Period 1: ', 'Period 2: ', 'Period 3: ']
        if options is not None:
            self.options = options
        else:
            self.options = ChartOptions()
        self.speed_bins = self.options.speed_bins.copy()

        # Filter Components
        if self.panel_type == TYPE_S1_3:
            self.cb_tmc_select = self.project.main_window.ui.cb_tmc_select
            self.cb_tmc_select.addItems(self.project.get_tmc(as_list=True))
            self.cb_peak_hour_start = self.project.main_window.ui.cb_stack_start
            self.cb_peak_hour_end = self.project.main_window.ui.cb_stack_end
            midnight = datetime(2000, 1, 1, 0, 0, 0)
            self.cb_peak_hour_start.addItems([(midnight + timedelta(minutes=15 * i)).strftime('%I:%M%p') for i in range(93)])
            self.cb_peak_hour_start.setCurrentIndex(0)
            self.cb_peak_hour_end.addItems([(midnight + timedelta(minutes=15 * i)).strftime('%I:%M%p') for i in range(1, 97)])
            self.cb_peak_hour_end.setCurrentIndex(self.cb_peak_hour_end.count() - 1)
            self.check_am = None
            self.check_pm = None
            self.check_mid = None
            self.check_wkdy = None
            self.check_wknd = None
            self.check_mon = None
            self.check_tue = None
            self.check_wed = None
            self.check_thu = None
            self.check_fri = None
            self.check_sat = None
            self.check_sun = None
            self.connect_tmc_combo_box()
            self.connect_time_combo_box()
        else:
            self.cb_tmc_select = self.project.main_window.ui.cb_tmc_select_trend
            self.cb_tmc_select.addItems(self.project.get_tmc(as_list=True))
            self.cb_peak_hour_start = None
            self.cb_peak_hour_end = None
            self.check_am = self.project.main_window.ui.check_am
            self.check_pm = self.project.main_window.ui.check_pm
            self.check_mid = self.project.main_window.ui.check_mid
            self.project.main_window.ui.trend_label_am.setText(convert_ap_to_time(self.am_ap_start, 5) + '-' + convert_ap_to_time(self.am_ap_end, 5))
            self.project.main_window.ui.trend_label_pm.setText(convert_ap_to_time(self.pm_ap_start, 5) + '-' + convert_ap_to_time(self.pm_ap_end, 5))
            self.project.main_window.ui.trend_label_mid.setText(convert_ap_to_time(self.md_ap_start, 5) + '-' + convert_ap_to_time(self.md_ap_end, 5))
            self.check_wkdy = self.project.main_window.ui.check_wkdy
            self.check_wknd = self.project.main_window.ui.check_wknd
            self.check_mon = self.project.main_window.ui.check_mon
            self.check_tue = self.project.main_window.ui.check_tue
            self.check_wed = self.project.main_window.ui.check_wed
            self.check_thu = self.project.main_window.ui.check_thu
            self.check_fri = self.project.main_window.ui.check_fri
            self.check_sat = self.project.main_window.ui.check_sat
            self.check_sun = self.project.main_window.ui.check_sun
            self.connect_check_boxes()
            self.connect_tmc_combo_box()

        self.plot_dfs = []
        self.update_plot_data()

    def create_charts(self):
        if self.panel_type == TYPE_S1_3:
            chart1_type = FIG_TYPE_SPD_HEAT_MAP
            chart2_type = FIG_TYPE_PCT_CONG_DAY
        else:
            chart1_type = FIG_TYPE_TT_TREND_LINE
            chart2_type = FIG_TYPE_TT_TREND_BAR
        self.chart11 = MplChart(self, fig_type=chart1_type, panel=self, region=0)
        self.chart21 = MplChart(self, fig_type=chart2_type, panel=self, region=0)

    def add_charts_to_layouts(self):
        # Chart 1
        self.grid_layout.addWidget(self.chart11, 0, 0)
        # Chart 2
        self.grid_layout.addWidget(self.chart21, 1, 0)

    def connect_check_boxes(self):
        self.check_am.stateChanged.connect(self.check_peak_func)
        self.check_pm.stateChanged.connect(self.check_peak_func)
        self.check_mid.stateChanged.connect(self.check_peak_func)
        self.check_am.setChecked(True)
        self.check_pm.setChecked(True)
        self.check_mid.setChecked(False)

        self.check_wkdy.stateChanged.connect(self.check_weekday)
        if sum([self.available_days.count(el) for el in range(5)]) > 0:
            self.check_wkdy.setChecked(True)
        else:
            self.check_wkdy.setDisabled(True)

        self.check_wknd.stateChanged.connect(self.check_weekend)
        if sum([self.available_days.count(el) for el in range(5, 7)]) > 0:
            self.check_wknd.setChecked(True)
        else:
            self.check_wknd.setDisabled(True)

        self.check_mon.stateChanged.connect(self.check_func)
        if self.available_days.count(0) > 0:
            self.check_mon.setChecked(True)
        else:
            self.check_mon.setDisabled(True)

        self.check_tue.stateChanged.connect(self.check_func)
        if self.available_days.count(1) > 0:
            self.check_tue.setChecked(True)
        else:
            self.check_tue.setDisabled(True)

        self.check_wed.stateChanged.connect(self.check_func)
        if self.available_days.count(2) > 0:
            self.check_wed.setChecked(True)
        else:
            self.check_wed.setDisabled(True)

        self.check_thu.stateChanged.connect(self.check_func)
        if self.available_days.count(3) > 0:
            self.check_thu.setChecked(True)
        else:
            self.check_thu.setDisabled(True)

        self.check_fri.stateChanged.connect(self.check_func)
        if self.available_days.count(4) > 0:
            self.check_fri.setChecked(True)
        else:
            self.check_fri.setDisabled(True)

        self.check_sat.stateChanged.connect(self.check_func)
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(True)
        else:
            self.check_sat.setDisabled(True)

        self.check_sun.stateChanged.connect(self.check_func)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(True)
        else:
            self.check_sun.setDisabled(True)

    def check_weekday(self):
        self.no_compute = True
        weekday_checked = self.check_wkdy.isChecked()
        if self.available_days.count(0) > 0:
            self.check_mon.setChecked(weekday_checked)
        if self.available_days.count(1) > 0:
            self.check_tue.setChecked(weekday_checked)
        if self.available_days.count(2) > 0:
            self.check_wed.setChecked(weekday_checked)
        if self.available_days.count(3) > 0:
            self.check_thu.setChecked(weekday_checked)
        if self.available_days.count(4) > 0:
            self.check_fri.setChecked(weekday_checked)
        self.no_compute = False
        self.check_func()

    def check_weekend(self):
        self.no_compute = True
        weekend_checked = self.check_wknd.isChecked()
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(weekend_checked)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(weekend_checked)
        self.no_compute = False
        self.check_func()

    def check_func(self):
        if not (self.init_mode or self.no_compute):
            self.plot_days.clear()
            if self.check_mon.isChecked() is True:
                self.plot_days.append(0)
            if self.check_tue.isChecked() is True:
                self.plot_days.append(1)
            if self.check_wed.isChecked() is True:
                self.plot_days.append(2)
            if self.check_thu.isChecked() is True:
                self.plot_days.append(3)
            if self.check_fri.isChecked() is True:
                self.plot_days.append(4)
            if self.check_sat.isChecked() is True:
                self.plot_days.append(5)
            if self.check_sun.isChecked() is True:
                self.plot_days.append(6)

            if len(self.plot_days) > 0:
                self.update_plot_data()
                # self.update_figures()

    def check_peak_func(self):
        if not (self.init_mode or self.no_compute):
            include_am = self.check_am.isChecked()
            include_pm = self.check_pm.isChecked()
            include_mid = self.check_mid.isChecked()
            if self.chart11 is not None:
                self.chart11.show_am = include_am
                self.chart11.show_pm = include_pm
                self.chart11.show_mid = include_mid
            if self.chart21 is not None:
                self.chart21.show_am = include_am
                self.chart21.show_pm = include_pm
                self.chart21.show_mid = include_mid
            included_peaks = include_am + include_pm + include_mid
            if included_peaks == 0 or included_peaks > 1:
                self.peak_period_str = 'Peak Period '
            elif include_am:
                self.peak_period_str = 'AM Peak '
            elif include_pm:
                self.peak_period_str = 'PM Peak '
            elif include_mid:
                self.peak_period_str = 'Midday '
            self.update_figures()

    def connect_tmc_combo_box(self):
        self.cb_tmc_select.currentIndexChanged.connect(self.options_updated)

    def connect_time_combo_box(self):
        self.cb_peak_hour_start.currentIndexChanged.connect(self.options_updated)
        self.cb_peak_hour_end.currentIndexChanged.connect(self.options_updated)

    def update_plot_data(self, **kwargs):
        full_df = self.dfs[0]
        dir_tmc = self.project.get_tmc()
        dir_df = full_df[full_df['tmc_code'].isin(dir_tmc['tmc'])]
        filtered_df = dir_df[dir_df['weekday'].isin(self.plot_days)]
        selected_tmc = self.cb_tmc_select.currentIndex()
        self.selected_tmc_name = dir_tmc['tmc'][selected_tmc]
        tmc_df = filtered_df[filtered_df['tmc_code'].isin([self.selected_tmc_name])]
        self.selected_tmc_len = dir_tmc['miles'][selected_tmc]

        if self.panel_type == TYPE_S1_3:
            self.ap_start = self.cb_peak_hour_start.currentIndex() * 3
            self.ap_end = (self.cb_peak_hour_end.currentIndex()+1) * 3
            print(self.ap_start)
            print(self.ap_end)
            func_list = [None,
                         lambda: create_pct_congested_sp(tmc_df, self.speed_bins, aps=[self.ap_start, self.ap_end]),  # filtered_df
                         None,
                         lambda: create_speed_heatmap(self.dfs[0], dir_tmc['tmc'][selected_tmc]),
                         None]
        else:
            am_aps = [self.am_ap_start, self.am_ap_end]
            pm_aps = [self.pm_ap_start, self.pm_ap_end]
            md_aps = [self.md_ap_start, self.md_ap_end]
            func_list = [lambda: create_trend_analysis(tmc_df, am_aps, pm_aps, md_aps),
                         None,
                         None,
                         None,
                         None]
        LoadTemporalQT(self, self.project.main_window, func_list)

    def plot_data_updated(self):
        if self.init_mode is True:
            self.create_charts()
            self.add_charts_to_layouts()
            self.v_layout.addWidget(self.chart_panel)
            self.update_chart_visibility()
            self.init_mode = False
            self.no_compute = False
        else:
            self.update_chart_types()
            self.update_figures()
            self.update_chart_visibility()

    def update_figures(self):
        if self.chart11 is not None:
            self.chart11.update_figure()
            self.chart11.draw()
        if self.chart21 is not None:
            self.chart21.update_figure()
            self.chart21.draw()

    def options_updated(self):
        self.options = self.project.chart_panel1_opts
        self.speed_bins = self.options.speed_bins.copy()
        self.update_plot_data()

    def update_chart_visibility(self):
        self.chart11.setVisible(True)
        self.chart21.setVisible(True)

    def update_chart_types(self):
        if self.panel_type == TYPE_S1_3:
            self.chart11.set_fig_type(2)
            self.chart21.set_fig_type(4)
        else:
            self.chart11.set_fig_type(0)
            self.chart21.set_fig_type(1)


class SpatialGridPanel(QtWidgets.QWidget):
    def __init__(self, project, options=None):
        QtWidgets.QWidget.__init__(self)
        self.chart11 = None
        self.chart21 = None
        self.chart12 = None
        self.chart22 = None
        self.panel_col1 = QtWidgets.QWidget(self)
        self.panel_col2 = QtWidgets.QWidget(self)
        self.chart_panel = QtWidgets.QWidget(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout(self.chart_panel)

        self.init_mode = True
        self.no_compute = True

        self.project = project
        facility_tmcs = self.project.get_tmc()  # Gets the tmc list for the selected direction(s)
        self.facility_len = facility_tmcs['miles'].sum()
        self.selected_tmc_name = facility_tmcs['tmc'][0]
        self.selected_tmc_len = facility_tmcs['miles'][0]
        self.dfs = [self.project.database.get_data(), None, None]
        self.available_days = self.project.database.get_available_days()
        self.plot_days = self.available_days.copy()
        self.peak_period_str = 'Peak Period '
        self.ap_start1 = convert_time_to_ap(6, 0, 5)
        self.ap_end1 = convert_time_to_ap(10, 0, 5)
        self.ap_start2 = convert_time_to_ap(10, 0, 5)
        self.ap_end2 = convert_time_to_ap(15, 0, 5)
        self.ap_start3 = convert_time_to_ap(15, 0, 5)
        self.ap_end3 = convert_time_to_ap(19, 0, 5)
        self.titles = ['Period 1: ', 'Period 2: ', 'Period 3: ']
        if options is not None:
            self.options = options
        else:
            self.options = ChartOptions()
        self.speed_bins = self.options.speed_bins.copy()

        # Filter Components
        self.cb_peak_hour_start1 = self.project.main_window.ui.ap_start1
        self.cb_peak_hour_end1 = self.project.main_window.ui.ap_end1
        self.cb_peak_hour_start2 = self.project.main_window.ui.ap_start2
        self.cb_peak_hour_end2 = self.project.main_window.ui.ap_end2
        self.cb_peak_hour_start3 = self.project.main_window.ui.ap_start3
        self.cb_peak_hour_end3 = self.project.main_window.ui.ap_end3
        midnight = datetime(2000, 1, 1, 0, 0, 0)
        ap_list = [(midnight + timedelta(minutes=15*i)).strftime('%I:%M%p') for i in range(93)]
        self.cb_peak_hour_start1.addItems(ap_list)
        self.cb_peak_hour_start1.setCurrentIndex(24)
        self.cb_peak_hour_end1.addItems(ap_list)
        self.cb_peak_hour_end1.setCurrentIndex(40)
        self.cb_peak_hour_start2.addItems(ap_list)
        self.cb_peak_hour_start2.setCurrentIndex(40)
        self.cb_peak_hour_end2.addItems(ap_list)
        self.cb_peak_hour_end2.setCurrentIndex(60)
        self.cb_peak_hour_start3.addItems(ap_list)
        self.cb_peak_hour_start3.setCurrentIndex(60)
        self.cb_peak_hour_end3.addItems(ap_list)
        self.cb_peak_hour_end3.setCurrentIndex(76)
        self.connect_combo_boxes()
        self.plot_dfs = [None, None, None, None, None, None, None]
        self.plot_dfs_temp = []
        self.update_plot_data()

    def create_charts(self):
        self.chart11 = MplChart(self, fig_type=FIG_TYPE_SPD_HEAT_MAP_FACILITY, panel=self, show_am=True, show_mid=False, show_pm=False)
        self.chart21 = MplChart(self, fig_type=FIG_TYPE_SPD_HEAT_MAP_FACILITY, panel=self, show_am=False, show_mid=True, show_pm=False)
        self.chart12 = MplChart(self, fig_type=FIG_TYPE_SPD_HEAT_MAP_FACILITY, panel=self, show_am=False, show_mid=False, show_pm=True)

    def add_charts_to_layouts(self):
        # Chart 1
        self.grid_layout.addWidget(self.chart11, 0, 0)
        # Chart 2
        self.grid_layout.addWidget(self.chart21, 1, 0)
        # Chart 3
        self.grid_layout.addWidget(self.chart12, 2, 0)

    def connect_combo_boxes(self):
        self.cb_peak_hour_start1.currentIndexChanged.connect(lambda: self.options_updated(fig_num=0))
        self.cb_peak_hour_end1.currentIndexChanged.connect(lambda: self.options_updated(fig_num=0))
        self.cb_peak_hour_start2.currentIndexChanged.connect(lambda: self.options_updated(fig_num=1))
        self.cb_peak_hour_end2.currentIndexChanged.connect(lambda: self.options_updated(fig_num=1))
        self.cb_peak_hour_start3.currentIndexChanged.connect(lambda: self.options_updated(fig_num=2))
        self.cb_peak_hour_end3.currentIndexChanged.connect(lambda: self.options_updated(fig_num=2))

    def update_plot_data(self, **kwargs):

        fig_num = -1
        if kwargs is not None:
            if 'fig_num' in kwargs:
                fig_num = kwargs['fig_num']

        full_df = self.dfs[0]
        dir_tmc = self.project.get_tmc()
        dir_df = full_df[full_df['tmc_code'].isin(dir_tmc['tmc'])]
        self.ap_start1 = self.cb_peak_hour_start1.currentIndex() * 3
        self.ap_end1 = self.cb_peak_hour_end1.currentIndex() * 3
        self.ap_start2 = self.cb_peak_hour_start2.currentIndex() * 3
        self.ap_end2 = self.cb_peak_hour_end2.currentIndex() * 3
        self.ap_start3 = self.cb_peak_hour_start3.currentIndex() * 3
        self.ap_end3 = self.cb_peak_hour_end3.currentIndex() * 3

        if fig_num == 0:
            func_list = [None, None, None, None,
                         lambda: create_speed_tmc_heatmap(dir_df, [self.ap_start1, self.ap_end1], dir_tmc['tmc']),
                         None,
                         None]
        elif fig_num == 1:
            func_list = [None, None, None, None,
                         None,
                         lambda: create_speed_tmc_heatmap(dir_df, [self.ap_start2, self.ap_end2], dir_tmc['tmc']),
                         None]
        elif fig_num == 2:
            func_list = [None, None, None, None,
                         None,
                         None,
                         lambda: create_speed_tmc_heatmap(dir_df, [self.ap_start3, self.ap_end3], dir_tmc['tmc'])]
        else:
            func_list = [None, None, None, None,
                         lambda: create_speed_tmc_heatmap(dir_df, [self.ap_start1, self.ap_end1], dir_tmc['tmc']),
                         lambda: create_speed_tmc_heatmap(dir_df, [self.ap_start2, self.ap_end2], dir_tmc['tmc']),
                         lambda: create_speed_tmc_heatmap(dir_df, [self.ap_start3, self.ap_end3], dir_tmc['tmc'])]

        LoadSpatialQT(self, self.project.main_window, func_list)

    def plot_data_updated(self):

        if self.plot_dfs_temp[4] is not None:
            self.plot_dfs[4] = self.plot_dfs_temp[4]
        if self.plot_dfs_temp[5] is not None:
            self.plot_dfs[5] = self.plot_dfs_temp[5]
        if self.plot_dfs_temp[6] is not None:
            self.plot_dfs[6] = self.plot_dfs_temp[6]
        if self.init_mode is True:
            self.create_charts()
            self.add_charts_to_layouts()
            self.v_layout.addWidget(self.chart_panel)
            self.update_chart_visibility()
            self.init_mode = False
            self.no_compute = False
        else:
            self.update_figures()
            self.update_chart_visibility()

    def update_figures(self):
        if self.chart11 is not None:
            self.chart11.update_figure()
            self.chart11.draw()
        if self.chart21 is not None:
            self.chart21.update_figure()
            self.chart21.draw()
        if self.chart12 is not None:
            self.chart12.update_figure()
            self.chart12.draw()

    def options_updated(self, fig_num=-1):
        self.update_plot_data(fig_num=fig_num)

    def update_chart_visibility(self):
        # if not self.init_mode:
            # self.chart11.setVisible(self.check_am.isChecked())
            # self.chart12.setVisible(self.check_mid.isChecked())
            # self.chart21.setVisible(self.check_pm.isChecked())
        pass

    def update_chart_types(self):
        pass


def convert_ap_to_time(x, min_resolution):
    if x < 0:
        return ''

    if x - int(x) != 0:
        return ''
    aps_per_hour = int(60 / min_resolution)
    hour = int(x // aps_per_hour)
    hour = hour % 24
    ampm_str = 'am'
    if hour >= 12:
        ampm_str = 'pm'
        hour -= 12
    if hour == 0:
        hour = 12
    minute = int(x % aps_per_hour) * min_resolution
    return str(hour) + ':' + '{num:02d}'.format(num=minute) + ampm_str