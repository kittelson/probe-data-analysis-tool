"""
Panel to hold a grid of MplChart objects
Has additional filtering controls built in
TMC selection combo box
Peak hour selection combo box
Weekday/Weekend/Day of week checkboxes
Currently limited to a 2x2 grid
Interacts the with ChartOptions object of the project that is created/edited by the chart_panel_options dialog
"""
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from stat_func import create_pct_congested_sp, create_pct_congested_tmc, create_speed_heatmap, create_speed_tmc_heatmap
from stat_func import create_timetime_analysis, convert_time_to_ap
from chart_defaults import ChartOptions
from mpl_charts import MplChart
from datetime import datetime, timedelta


class ChartGridPanel(QtWidgets.QWidget):
    def __init__(self, project, options=None):
        QtWidgets.QWidget.__init__(self)
        self.chart11 = None
        self.chart21 = None
        self.chart12 = None
        self.chart22 = None
        self.nav_toolbar11 = None
        self.nav_toolbar21 = None
        self.nav_toolbar12 = None
        self.nav_toolbar22 = None
        self.panel_col1 = QtWidgets.QWidget(self)
        self.panel_col2 = QtWidgets.QWidget(self)
        self.chart_panel = QtWidgets.QWidget(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout(self.chart_panel)

        self.init_mode = True

        self.project = project
        facility_tmcs = self.project.get_tmc()  # Gets the tmc list for the selected direction(s)
        self.facility_len = facility_tmcs['miles'].sum()
        self.selected_tmc_name = facility_tmcs['tmc'][0]
        self.selected_tmc_len = facility_tmcs['miles'][0]
        self.dfs = [self.project.database.get_data(), None, None]
        self.tt_comp = None
        self.available_days = self.project.database.get_available_days()
        self.plot_days = self.available_days.copy()
        self.peak_period_str = 'Peak Period '
        self.ap_start = convert_time_to_ap(8, 0, 5)
        self.ap_end = convert_time_to_ap(9, 0, 5)
        self.titles = ['Period 1: ', 'Period 2: ', 'Period 3: ']
        self.plot_tt = self.tt_comp
        if options is not None:
            self.options = options
        else:
            self.options = ChartOptions()
        self.speed_bins = self.options.speed_bins.copy()

        # Filter Components
        self.cb_tmc_select = QtWidgets.QComboBox()
        self.cb_tmc_select.addItems(self.project.get_tmc(as_list=True))
        self.cb_peak_hour_select = QtWidgets.QComboBox()
        midnight = datetime(2000, 1, 1, 0, 0, 0)
        self.cb_peak_hour_select.addItems([(midnight + timedelta(minutes=15*i)).strftime('%I:%M%p') for i in range(93)])
        self.cb_peak_hour_select.setCurrentIndex(24)
        self.check_am = QtWidgets.QCheckBox('AM')
        self.check_pm = QtWidgets.QCheckBox('PM')
        self.check_mid = QtWidgets.QCheckBox('Midday')
        self.check_wkdy = QtWidgets.QCheckBox('Weekdays')
        self.check_wknd = QtWidgets.QCheckBox("Weekends")
        self.check_mon = QtWidgets.QCheckBox('Mon')
        self.check_tue = QtWidgets.QCheckBox('Tue')
        self.check_wed = QtWidgets.QCheckBox('Wed')
        self.check_thu = QtWidgets.QCheckBox('Thu')
        self.check_fri = QtWidgets.QCheckBox('Fri')
        self.check_sat = QtWidgets.QCheckBox('Sat')
        self.check_sun = QtWidgets.QCheckBox('Sun')
        self.check_bar_day = QtWidgets.QWidget(self)
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar_day)
        self.h_layout.addWidget(self.cb_peak_hour_select)
        self.h_layout.addWidget(self.cb_tmc_select)
        self.h_layout.addWidget(create_spacer_line(self))
        self.h_layout.addWidget(self.check_am)
        self.h_layout.addWidget(self.check_pm)
        self.h_layout.addWidget(self.check_mid)
        self.h_layout.addWidget(create_spacer_line(self))
        self.h_layout.addWidget(self.check_wkdy)
        self.h_layout.addWidget(self.check_wknd)
        self.h_layout.addWidget(create_spacer_line(self))
        self.h_layout.addWidget(self.check_mon)
        self.h_layout.addWidget(self.check_tue)
        self.h_layout.addWidget(self.check_wed)
        self.h_layout.addWidget(self.check_thu)
        self.h_layout.addWidget(self.check_fri)
        self.h_layout.addWidget(self.check_sat)
        self.h_layout.addWidget(self.check_sun)
        self.connect_check_boxes()
        self.connect_combo_boxes()

        self.plot_dfs = []
        self.update_plot_data()
        self.create_charts()
        self.add_charts_to_layouts()

        self.v_layout.addWidget(self.chart_panel)
        self.v_layout.addWidget(self.check_bar_day)
        self.update_chart_visibility()

        self.init_mode = False
        self.no_compute = False

    def create_charts(self):
        self.chart11 = MplChart(self, fig_type=self.options.chart_type[0][0], panel=self, region=0)
        self.chart21 = MplChart(self, fig_type=self.options.chart_type[1][0], panel=self, region=0)
        self.chart12 = MplChart(self, fig_type=self.options.chart_type[0][1], panel=self, region=1)
        self.chart22 = MplChart(self, fig_type=self.options.chart_type[1][1], panel=self, region=2)
        # self.nav_toolbar11 = NavigationToolbar(self.chart11, self)
        # self.nav_toolbar21 = NavigationToolbar(self.chart21, self)
        # self.nav_toolbar12 = NavigationToolbar(self.chart12, self)
        # self.nav_toolbar22 = NavigationToolbar(self.chart22, self)

    def add_charts_to_layouts(self):
        # Chart 1
        self.grid_layout.addWidget(self.chart11, 0, 0)
        # Chart 2
        self.grid_layout.addWidget(self.chart12, 0, 1)
        # Chart 3
        self.grid_layout.addWidget(self.chart21, 1, 0)
        # Chart 4
        self.grid_layout.addWidget(self.chart22, 1, 1)

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

    def connect_combo_boxes(self):
        self.cb_tmc_select.currentIndexChanged.connect(self.options_updated)
        self.cb_peak_hour_select.currentIndexChanged.connect(self.options_updated)

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
                self.update_figures()

    def check_peak_func(self):
        if not (self.init_mode or self.no_compute):
            include_am = self.check_am.isChecked()
            include_pm = self.check_pm.isChecked()
            include_mid = self.check_mid.isChecked()
            if self.chart11 is not None:
                self.chart11.show_am = include_am
                self.chart11.show_pm = include_pm
                self.chart11.show_mid = include_mid
            if self.chart12 is not None:
                self.chart12.show_am = include_am
                self.chart12.show_pm = include_pm
                self.chart12.show_mid = include_mid
            if self.chart21 is not None:
                self.chart21.show_am = include_am
                self.chart21.show_pm = include_pm
                self.chart21.show_mid = include_mid
            if self.chart22 is not None:
                self.chart22.show_am = include_am
                self.chart22.show_pm = include_pm
                self.chart22.show_mid = include_mid
            included_peaks = self.show_am + self.show_pm + self.show_mid
            if included_peaks == 0 or included_peaks > 1:
                self.peak_period_str = 'Peak Period '
            elif self.show_am:
                self.peak_period_str = 'AM Peak '
            elif self.show_pm:
                self.peak_period_str = 'PM Peak '
            elif self.show_mid:
                self.peak_period_str = 'Midday '
            self.update_figures()

    def update_plot_data(self, **kwargs):
        full_df = self.dfs[0]
        dir_tmc = self.project.get_tmc()
        dir_df = full_df[full_df['tmc_code'].isin(dir_tmc['tmc'])]
        filtered_df = dir_df[dir_df['weekday'].isin(self.plot_days)]
        selected_tmc = self.cb_tmc_select.currentIndex()
        self.selected_tmc_name = dir_tmc['tmc'][selected_tmc]
        self.selected_tmc_len = dir_tmc['miles'][selected_tmc]
        self.ap_start = self.cb_peak_hour_select.currentIndex() * 3
        self.ap_end = self.ap_start + 12
        self.plot_dfs = [create_timetime_analysis(filtered_df),
                         create_pct_congested_sp(filtered_df, self.speed_bins),
                         create_pct_congested_tmc(filtered_df, self.speed_bins),
                         create_speed_heatmap(self.dfs[0], dir_tmc['tmc'][selected_tmc]),
                         create_speed_tmc_heatmap(dir_df, [self.ap_start, self.ap_end])]

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
        if self.chart22 is not None:
            self.chart22.update_figure()
            self.chart22.draw()


    def options_updated(self):
        self.options = self.project.chart_panel1_opts
        self.speed_bins = self.options.speed_bins.copy()
        self.update_plot_data()
        self.update_chart_types()
        self.update_figures()
        self.update_chart_visibility()

    def update_chart_visibility(self):
        self.chart11.setVisible(True)
        self.chart12.setVisible(self.options.num_cols > 1)
        self.chart21.setVisible(self.options.num_rows > 1)
        self.chart22.setVisible(self.options.num_rows > 1 and self.options.num_cols > 1)

    def update_chart_types(self):
        self.chart11.set_fig_type(self.options.chart_type[0][0])
        self.chart12.set_fig_type(self.options.chart_type[0][1])
        self.chart21.set_fig_type(self.options.chart_type[1][0])
        self.chart22.set_fig_type(self.options.chart_type[1][1])


def create_spacer_line(parent):
    line = QtWidgets.QFrame(parent)
    line.setFrameShape(QtWidgets.QFrame.VLine)
    line.setLineWidth(5)
    line.setMidLineWidth(5)
    return line

