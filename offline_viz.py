"""
Originally a testbed file to create matplotlib charts, but now holds a few of the currently used charts
In the process of migrating key functionality into the more streamlined mpl_charts module
Currently only has code for the Extra Time and Speed band charts, as well as a 2x2 grid panel to hold them
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from stat_func import create_facility_et_analysis
from chart_defaults import TT_RED_BEFORE, TT_RED, TT_BLUE_BEFORE, TT_BLUE, BEFORE_LW, SB_BLUE, SB_RED


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, app=None, region=0, region2=-1, is_subset=False, width=5, height=4, dpi=100, **kwargs):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setFocus()
        self.app = None
        self.title_str = ''
        if app is not None:
            self.app = app
            self.title_str = self.app.project.get_name()
        self.region = region
        self.region2 = region2
        self.is_subset = is_subset

        self.show_am = True
        self.show_pm = True
        self.show_mid = False
        self.xlabel_func = None
        if kwargs is not None:
            if 'show_am' in kwargs:
                self.show_am = kwargs['show_am']
            if 'show_pm' in kwargs:
                self.show_pm = kwargs['show_pm']
            if 'show_mid' in kwargs:
                self.show_mid = kwargs['show_mid']
            if 'xlabel_func' in kwargs:
                self.xlabel_func = kwargs['xlabel_func']

        self.compute_initial_figure()

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)

        FigureCanvas.updateGeometry(self)
        scale = 1.1
        self.zp = ZoomPan()
        figZoom = self.zp.zoom_factory(self.axes, base_scale=scale)
        figPan = self.zp.pan_factory(self.axes)

    def compute_initial_figure(self):
        pass

    def set_x_bounds(self, x_min, x_max, make_default=False):
        self.axes.set_xbound([x_min, x_max])
        if make_default:
            self.zp.set_default_xlim([x_min, x_max])

    def set_y_bounds(self, y_min, y_max, make_default=False):
        self.axes.set_ybound([y_min, y_max])
        if make_default:
            self.zp.set_default_ylim([y_min, y_max])


class ExtraTimeBarChartCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.bar(self.app.plot_dfs[self.region].index, self.app.plot_dfs[self.region]['mean'], label='Mean')
        self.axes.bar(self.app.plot_dfs[self.region].index, self.app.plot_dfs[self.region]['extra_time'], bottom=self.app.plot_dfs[self.region]['mean'], label='95th Percentile')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def update_figure(self):
        self.axes.cla()
        self.axes.bar(self.app.plot_dfs[self.region].index, self.app.plot_dfs[self.region]['mean'], label='Mean')
        self.axes.bar(self.app.plot_dfs[self.region].index, self.app.plot_dfs[self.region]['extra_time'],
                      bottom=self.app.plot_dfs[self.region]['mean'], label='95th Percentile')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)


class ExtraTimeAreaChartCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.title_str = self.app.project.get_name() + ' ('
        if self.is_subset:
            self.title_str = self.title_str + '{:1.1f}'.format(self.app.facility_len_subset) + 'mi'
        else:
            self.title_str = self.title_str + '{:1.1f}'.format(self.app.facility_len) + 'mi'
        self.title_str = self.title_str + ')\n'
        if self.region2 >= 0:
            self.title_str = self.title_str + 'Before/After: ' + self.app.period1 + ' vs ' + self.app.period1
        elif self.region == 0:
            self.title_str = self.title_str + 'Period 1: ' + self.app.period1
        else:
            self.title_str = self.title_str + 'Period 2: ' + self.app.period2
        self.axes.set_title(self.title_str)

    def compute_initial_figure(self):
        if self.is_subset:
            data = self.app.plot_subset_dfs
        else:
            data = self.app.plot_dfs
        print(data[self.region]['mean'])
        self.axes.stackplot(data[self.region].index,
                            data[self.region]['mean'],
                            data[self.region]['extra_time'],
                            labels=['After-Average', 'After-95th Pct'], colors=[TT_BLUE, TT_RED])
        if self.region2 >= 0:
            self.axes.plot(data[self.region2].index,
                            data[self.region2]['mean'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(data[self.region2].index,
                           data[self.region2]['percentile_95'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Pct')
        self.title_str = self.app.project.get_name() + ' ('
        if self.is_subset:
            self.title_str = self.title_str + '{:1.1f}'.format(self.app.facility_len_subset) + 'mi'
        else:
            self.title_str = self.title_str + '{:1.1f}'.format(self.app.facility_len) + 'mi'
        self.title_str = self.title_str + ')\n'
        if self.region2 >= 0:
            self.title_str = self.title_str + 'Before/After: ' + self.app.period1 + ' vs ' + self.app.period2
        elif self.region == 0:
            self.title_str = self.title_str + 'Period 1: ' + self.app.period1
        else:
            self.title_str = self.title_str + 'Period 2: ' + self.app.period2
        self.axes.set_title(self.title_str)
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.fig.tight_layout()

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()

    def get_y_max(self):
        return self.axes.get_ylim()[1]


class SpeedBandCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.title_str = 'Reliability Speed Band'

    def compute_initial_figure(self):
        if self.is_subset:
            data = self.app.plot_subset_dfs
            fl = self.app.facility_len_subset
        else:
            data = self.app.plot_dfs
            fl = self.app.facility_len

        self.axes.fill_between(data[self.region].index,
                               (60 * fl) / data[self.region]['percentile_5'],
                               (60 * fl) / data[self.region]['mean'],
                               color=SB_BLUE)
        self.axes.fill_between(data[self.region].index,
                               (60 * fl) / data[self.region]['mean'],
                               (60 * fl) / data[self.region]['percentile_95'],
                               color=SB_BLUE)
        self.axes.plot(data[self.region].index,
                       (60 * fl) / data[self.region]['percentile_5'], color=SB_BLUE, label='5th Percentile')
        self.axes.plot(data[self.region].index,
                       (60 * fl) / data[self.region]['mean'], color=SB_RED, label='Average')
        self.axes.plot(data[self.region].index,
                       (60 * fl) / data[self.region]['percentile_95'], color=SB_BLUE, label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(data[self.region2].index,
                           (60 * fl) / data[self.region2]['mean'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(data[self.region2].index,
                           (60 * fl) / data[self.region2]['percentile_95'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Percentile')
        self.axes.set_title(self.title_str)
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([0, 80])
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.fig.tight_layout()

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()


class FourByFourPanel(QtWidgets.QWidget):
    def __init__(self, project):
        QtWidgets.QWidget.__init__(self)

        self.f_extra_time = create_facility_et_analysis

        self.init_mode = True
        self.project = project
        df = self.project.database.get_data()
        dr1 = self.project.get_date_range(0)
        df_period1 = df[(df['Date'] >= dr1[0].toString('yyyy-MM-dd')) & (df['Date'] <= dr1[1].toString('yyyy-MM-dd'))]
        dr2 = self.project.get_date_range(1)
        df_period2 = df[(df['Date'] > dr2[0].toString('yyyy-MM-dd')) & (df['Date'] < dr2[1].toString('yyyy-MM-dd'))]
        self.period1 = dr1[0].toString('yyyy-MM-dd') + ' to ' + dr1[1].toString('yyyy-MM-dd')
        self.period2 = dr2[0].toString('yyyy-MM-dd') + ' to ' + dr2[1].toString('yyyy-MM-dd')
        tmc = self.project.database.get_tmcs()
        self.facility_len = tmc['miles'].sum()
        self.dfs = [df_period1, None, df_period2]
        self.tt_comp = None
        self.tmc_subset = []
        self.facility_len_subset = tmc[tmc['tmc'].isin(self.tmc_subset)]['miles'].sum()
        self.available_days = self.project.database.get_available_days()
        self.plot_days = self.available_days.copy()
        self.titles = ['Period 1: ' + dr1[0].toString('yyyy-MM-dd') + ' to ' + dr1[1].toString('yyyy-MM-dd'),
                       'Interim: ',
                       'Period 2: ' + dr2[0].toString('yyyy-MM-dd') + ' to ' + dr2[1].toString('yyyy-MM-dd')]
        self.plot_tt = self.tt_comp
        self.plot_dfs = [self.f_extra_time(df) for df in self.dfs]
        self.plot_subset_dfs = []
        self.update_tmc_subset_dfs()
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.before_bar = QtWidgets.QWidget(self)
        self.after_bar = QtWidgets.QWidget(self)
        self.analysis_bar = QtWidgets.QWidget(self)
        self.v_layout_before = QtWidgets.QVBoxLayout(self.before_bar)
        self.v_layout_after = QtWidgets.QVBoxLayout(self.after_bar)
        self.h_layout_analysis = QtWidgets.QHBoxLayout(self.analysis_bar)
        l_func = lambda x, pos:  convert_xval_to_time(x, pos, 5)
        self.chart11 = ExtraTimeAreaChartCanvas(self, app=self, xlabel_func=l_func, region=2, region2=0)
        self.chart21 = SpeedBandCanvas(self, app=self, xlabel_func=l_func, region=2, region2=0)
        self.chart12 = ExtraTimeAreaChartCanvas(self, xlabel_func=l_func, app=self, region=2, region2=0, is_subset=True)
        self.chart22 = SpeedBandCanvas(self, app=self, xlabel_func=l_func, region=2, region2=0, width=5, is_subset=True)
        self.setup_figure_bounds()
        self.navi_toolbar11 = NavigationToolbar(self.chart11, self)
        self.navi_toolbar21 = NavigationToolbar(self.chart21, self)
        self.navi_toolbar12 = NavigationToolbar(self.chart12, self)
        self.navi_toolbar22 = NavigationToolbar(self.chart22, self)
        self.check_bar_day = QtWidgets.QWidget(self)
        self.before_after_cb = QtWidgets.QComboBox()
        self.before_after_cb.addItems(['Before & After', 'Before Only', "After Only"])
        self.tmc_start_cb = QtWidgets.QComboBox()
        self.tmc_end_cb = QtWidgets.QComboBox()
        # self.tmc_start_cb.addItems(self.project.database.get_tmcs(as_list=True))
        # self.tmc_end_cb.addItems(self.project.database.get_tmcs(as_list=True))
        self.tmc_subset_button = self.project.main_window.ui.pushButton_tmc_subset
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar_day)
        self.check_wkdy = QtWidgets.QCheckBox('Weekdays')
        self.check_wknd = QtWidgets.QCheckBox("Weekends")
        self.check_mon = QtWidgets.QCheckBox('Mon')
        self.check_tue = QtWidgets.QCheckBox('Tue')
        self.check_wed = QtWidgets.QCheckBox('Wed')
        self.check_thu = QtWidgets.QCheckBox('Thu')
        self.check_fri = QtWidgets.QCheckBox('Fri')
        self.check_sat = QtWidgets.QCheckBox('Sat')
        self.check_sun = QtWidgets.QCheckBox('Sun')
        self.connect_check_boxes()
        self.connect_combo_box()
        self.connect_tmc_subset_widgets()
        self.h_layout.addWidget(QtWidgets.QLabel('Show:'))
        self.h_layout.addWidget(self.before_after_cb)
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
        # self.h_layout.addWidget(create_spacer_line(self))
        # self.h_layout.addWidget(self.tmc_start_cb)
        # self.h_layout.addWidget(self.tmc_end_cb)
        # self.h_layout.addWidget(self.tmc_subset_button)
        self.v_layout_before.addWidget(self.navi_toolbar11)
        self.v_layout_before.addWidget(self.chart11)
        self.v_layout_before.addWidget(self.navi_toolbar21)
        self.v_layout_before.addWidget(self.chart21)
        self.v_layout_after.addWidget(self.navi_toolbar12)
        self.v_layout_after.addWidget(self.chart12)
        self.v_layout_after.addWidget(self.navi_toolbar22)
        self.v_layout_after.addWidget(self.chart22)
        self.h_layout_analysis.addWidget(self.before_bar)
        self.h_layout_analysis.addWidget(self.after_bar)
        self.v_layout.addWidget(self.analysis_bar)
        self.v_layout.addWidget(self.check_bar_day)

        self.init_mode = False
        self.no_compute = False

    def connect_check_boxes(self):
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

    def connect_combo_box(self):
        self.before_after_cb.currentIndexChanged.connect(self.before_after_changed)

    def before_after_changed(self):
        # print('Index changed: ' + str(self.before_after_cb.currentIndex()))
        cb_idx = self.before_after_cb.currentIndex()
        if cb_idx == 0:
            self.chart11.region = 2
            self.chart11.region2 = 0
            self.chart21.region = 2
            self.chart21.region2 = 0
            self.chart12.region = 2
            self.chart12.region2 = 0
            self.chart22.region = 2
            self.chart22.region2 = 0
        elif cb_idx == 1:
            self.chart11.region = 0
            self.chart11.region2 = -1
            self.chart21.region = 0
            self.chart21.region2 = -1
            self.chart12.region = 0
            self.chart12.region2 = -1
            self.chart22.region = 0
            self.chart22.region2 = -1
        elif cb_idx == 2:
            self.chart11.region = 2
            self.chart11.region2 = -1
            self.chart21.region = 2
            self.chart21.region2 = -1
            self.chart12.region = 2
            self.chart12.region2 = -1
            self.chart22.region = 2
            self.chart22.region2 = -1
        self.update_all_charts()

    def connect_tmc_subset_widgets(self):
        self.tmc_start_cb.currentIndexChanged.connect(self.tmc_start_changed)
        self.tmc_end_cb.currentIndexChanged.connect(self.tmc_end_changed)
        self.tmc_subset_button.clicked.connect(self.update_tmc_subset)

    def tmc_start_changed(self):
        self.tmc_subset_button.setEnabled(True)

    def tmc_end_changed(self):
        self.tmc_subset_button.setEnabled(True)

    def update_tmc_subset(self):
        self.tmc_subset_button.setEnabled(False)
        tmc_start_idx = self.tmc_start_cb.currentIndex()
        tmc_end_idx = self.tmc_end_cb.currentIndex()
        self.tmc_subset = self.project.main_window.get_tmc_subset()
        self.update_tmc_subset_dfs()
        self.update_all_charts()

    def setup_figure_bounds(self):
        zoom_full = True
        if zoom_full:
            x_min = 0
            x_max = 288
        else:
            x_min = 192
            x_max = 240

        y_max = max(self.chart11.get_y_max(), self.chart12.get_y_max())
        self.chart11.set_x_bounds(x_min, x_max, make_default=True)
        self.chart11.set_y_bounds(0, y_max, make_default=True)
        self.chart12.set_x_bounds(x_min, x_max, make_default=True)
        self.chart12.set_y_bounds(0, y_max, make_default=True)
        self.chart21.set_x_bounds(x_min, x_max, make_default=True)
        self.chart21.set_y_bounds(0, 80, make_default=True)
        self.chart22.set_x_bounds(x_min, x_max, make_default=True)
        self.chart22.set_y_bounds(0, 80, make_default=True)

    def check_weekday(self):
        self.no_compute = True
        weekday_checked =  self.check_wkdy.isChecked()
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
                self.plot_dfs = [self.f_extra_time(df[df['weekday'].isin(self.plot_days)]) if df is not None else None for df in self.dfs]
                self.update_tmc_subset_dfs()
                self.update_all_charts()

    def update_all_charts(self):
        self.chart11.update_figure()
        self.chart21.update_figure()
        self.chart11.draw()
        self.chart21.draw()
        self.chart12.update_figure()
        self.chart22.update_figure()
        self.chart12.draw()
        self.chart22.draw()

    def update_tmc_subset_dfs(self):
        tmc = self.project.database.get_tmcs()
        print(self.tmc_subset)
        self.facility_len_subset = tmc[tmc['tmc'].isin(self.tmc_subset)]['miles'].sum()
        self.plot_subset_dfs = [self.f_extra_time(df[(df['tmc_code'].isin(self.tmc_subset)) & (df['weekday'].isin(self.plot_days))]) if df is not None else None for df in self.dfs]


class ZoomPan:
    """
    https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
    """
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
        self.default_xlim=None
        self.default_ylim=None

    def set_default_xlim(self, new_xlim):
        self.default_xlim = new_xlim

    def set_default_ylim(self, new_ylim):
        self.default_ylim = new_ylim

    def zoom_factory(self, ax, base_scale=2.0):
        def zoom(event):

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            if new_width < 1.0:
                return

            if event.key is "control":
                if xdata is not None:
                    relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
                    ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            elif event.key is "shift":
                if ydata is not None:
                    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
                    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
            else:
                if xdata is not None and ydata is not None:
                    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
                    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
                    ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
                    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if ax.get_navigate_mode() is None:
                if event.dblclick:
                    if self.default_xlim is not None:
                        ax.set_xlim(self.default_xlim)
                    if self.default_ylim is not None:
                        ax.set_ylim(self.default_ylim)
                else:
                    if event.inaxes != ax: return
                    self.cur_xlim = ax.get_xlim()
                    self.cur_ylim = ax.get_ylim()
                    self.press = self.x0, self.y0, event.xdata, event.ydata
                    self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            if ax.get_navigate_mode() is None:
                self.press = None
                ax.figure.canvas.draw()

        def onMotion(event):
            if ax.get_navigate_mode() is None:
                if self.press is None: return
                if event.inaxes != ax: return
                dx = event.xdata - self.xpress
                dy = event.ydata - self.ypress
                self.cur_xlim -= dx
                self.cur_ylim -= dy
                ax.set_xlim(self.cur_xlim)
                ax.set_ylim(self.cur_ylim)

                ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)

        #return the function
        return onMotion


def create_spacer_line(parent):
    line = QtWidgets.QFrame(parent)
    line.setFrameShape(QtWidgets.QFrame.VLine)
    line.setLineWidth(5)
    line.setMidLineWidth(5)
    return line


def convert_xval_to_time(x, pos, min_resolution):
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

