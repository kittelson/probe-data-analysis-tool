from PyQt5 import QtWidgets
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator
from stat_func import create_et_analysis, create_timetime_analysis, create_pct_congested_sp, create_pct_congested_tmc
from stat_func import create_et_analysis_v2, create_timetime_analysis_v2
import calendar
from datetime import datetime, timedelta

TT_BLUE = '#6e97c8'  # '#4f81bd'
TT_RED = '#da9694'  # '#c0504d'
TT_BLUE_BEFORE = '#032548'  # '#08519c'
TT_ORANGE_BEFORE = '#d95f0e'
TT_RED_BEFORE = '#c00000'
SB_BLUE = '#B0C4DE'
SB_RED = '#cd5c5c'
BEFORE_LW = 1.0

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
        self.axes.stackplot(data[self.region].index,
                            data[self.region]['mean'],
                            data[self.region]['extra_time'],
                            labels=['Average', '95th Percentile'], colors=[TT_BLUE, TT_RED])
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
                           label='Before-95th PCT')
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
        else:
            data = self.app.plot_dfs
        self.axes.fill_between(data[self.region].index,
                               (60 * self.app.facility_len) / data[self.region]['percentile_5'],
                               (60 * self.app.facility_len) / data[self.region]['mean'],
                               color=SB_BLUE)
        self.axes.fill_between(data[self.region].index,
                               (60 * self.app.facility_len) / data[self.region]['mean'],
                               (60 * self.app.facility_len) / data[self.region]['percentile_95'],
                               color=SB_BLUE)
        self.axes.plot(data[self.region].index,
                       (60 * self.app.facility_len) / data[self.region]['percentile_5'], color=SB_BLUE, label='5th Percentile')
        self.axes.plot(data[self.region].index,
                       (60 * self.app.facility_len) / data[self.region]['mean'], color=SB_RED, label='Average')
        self.axes.plot(data[self.region].index,
                       (60 * self.app.facility_len) / data[self.region]['percentile_95'], color=SB_BLUE, label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(data[self.region2].index,
                           (60 * self.app.facility_len) / data[self.region2]['mean'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(data[self.region2].index,
                           (60 * self.app.facility_len) / data[self.region2]['percentile_95'],
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


class TimeTimeLineChartCanvas(MyMplCanvas):
    """Travel Time over Time Line Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.update_title()

    def compute_initial_figure(self):
        if self.show_am:
            tt_am_mean_dir1 = self.app.plot_dfs[0]['mean']
            tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
            tt_am_pct95_dir1 = self.app.plot_dfs[0]['percentile_95']
            x = [el for el in range(len(tt_am_mean_dir1))]
            self.axes.plot(x, tt_am_mean_dir1, color='C0', linestyle='-', lw=2.0, label='AM-Mean')
            self.axes.plot(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.plot(x, tt_am_pct95_dir1, color='C0', linestyle='--', lw=1.0, label='AM-95th Pct')
        if self.show_pm:
            tt_pm_mean_dir1 = self.app.plot_dfs[0]['meanpm']
            tt_pm_pct5_dir1 = self.app.plot_dfs[0]['percentile_5pm']
            tt_pm_pct95_dir1 = self.app.plot_dfs[0]['percentile_95pm']
            x = [el for el in range(len(tt_pm_mean_dir1))]
            self.axes.plot(x, tt_pm_mean_dir1, color='C1', linestyle='-', lw=2.0, label='PM-Mean')
            self.axes.plot(x, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.plot(x, tt_pm_pct95_dir1, color='C1', linestyle='--', lw=1.0, label='PM-95th Pct')
        if self.show_mid:
            tt_md_mean_dir1 = self.app.plot_dfs[0]['meanmid']
            tt_md_pct5_dir1 = self.app.plot_dfs[0]['percentile_5mid']
            tt_md_pct95_dir1 = self.app.plot_dfs[0]['percentile_95mid']
            x = [el for el in range(len(tt_md_mean_dir1))]
            self.axes.plot(x, tt_md_mean_dir1, color='C2', linestyle='-', lw=2.0, label='Mid-Mean')
            self.axes.plot(x, tt_md_pct5_dir1, color='C2', linestyle='--', lw=1.0, label='Mid-5th Pct')
            self.axes.plot(x, tt_md_pct95_dir1, color='C2', linestyle='--', lw=1.0, label='Mid-95th Pct')

        self.update_title()
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.fig.tight_layout()

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()

    def update_title(self):
        self.title_str = self.app.project.get_name() + ': '
        included_peaks = self.show_am + self.show_pm + self.show_mid
        if included_peaks == 0 or included_peaks > 1:
            self.title_str = self.title_str + 'Peak Period '
        elif self.show_am:
            self.title_str = self.title_str + 'AM Peak '
        elif self.show_pm:
            self.title_str = self.title_str + 'PM Peak '
        elif self.show_mid:
            self.title_str = self.title_str + 'Midday '
        self.title_str = self.title_str + 'Travel Times by Month'
        self.axes.set_title(self.title_str)

    def get_y_max(self):
        return self.axes.get_ylim()[1]


class TimeTimeBarChartCanvas(MyMplCanvas):
    """Travel Time over Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.update_title()

    def compute_initial_figure(self):

        width = 0.35
        if self.show_am:
            tt_am_mean_dir1 = self.app.plot_dfs[0]['mean']
            tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
            tt_am_pct95_dir1 = self.app.plot_dfs[0]['percentile_95']
            x = [el for el in range(len(tt_am_mean_dir1))]
            self.axes.bar(x, tt_am_mean_dir1, width, color='C0', label='AM-Mean')
            # ax3.bar(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.bar(x, [tt_am_pct95_dir1[i] - tt_am_mean_dir1[i] for i in range(len(tt_am_mean_dir1))], width, bottom=tt_am_mean_dir1, color='#aec7e8',
                    label='AM-95th Pct')

        if self.show_pm:
            tt_pm_mean_dir1 = self.app.plot_dfs[0]['meanpm']
            tt_pm_pct5_dir1 = self.app.plot_dfs[0]['percentile_5pm']
            tt_pm_pct95_dir1 = self.app.plot_dfs[0]['percentile_95pm']
            x = [el for el in range(len(tt_pm_mean_dir1))]
            offset = 0
            if self.show_am:
                offset += width
            self.axes.bar([el + offset for el in x], tt_pm_mean_dir1, width, color='C1', label='PM-Mean')
            # ax1.bar(x + width, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.bar([el + offset for el in x], [tt_pm_pct95_dir1[i] - tt_pm_mean_dir1[i] for i in range(len(tt_pm_mean_dir1))], width,
                    bottom=tt_pm_mean_dir1, color='#ffbb78', label='PM-95th Pct')

        if self.show_mid:
            tt_md_mean_dir1 = self.app.plot_dfs[0]['meanmid']
            tt_md_pct5_dir1 = self.app.plot_dfs[0]['percentile_5mid']
            tt_md_pct95_dir1 = self.app.plot_dfs[0]['percentile_95mid']
            x = [el for el in range(len(tt_md_mean_dir1))]
            offset = 0
            if self.show_am:
                offset += width
            if self.show_pm:
                offset += width
            self.axes.bar([el + offset for el in x], tt_md_mean_dir1, width, color='C2', label='Mid-Mean')
            # ax1.bar(x + width, tt_pm_pct5_dir1, color='C2', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.bar([el + offset for el in x], [tt_md_pct95_dir1[i] - tt_md_mean_dir1[i] for i in range(len(tt_md_mean_dir1))], width,
                    bottom=tt_md_mean_dir1, color='#98df8a', label='Mid-95th Pct')

        self.update_title()
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.fig.tight_layout()

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()

    def update_title(self):
        self.title_str = self.app.project.get_name() + ': '
        included_peaks = self.show_am + self.show_pm + self.show_mid
        if included_peaks == 0 or included_peaks > 1:
            self.title_str = self.title_str + 'Peak Period '
        elif self.show_am:
            self.title_str = self.title_str + 'AM Peak '
        elif self.show_pm:
            self.title_str = self.title_str + 'PM Peak '
        elif self.show_mid:
            self.title_str = self.title_str + 'Midday '
        self.title_str = self.title_str + 'Travel Times by Month'
        self.axes.set_title(self.title_str)

    def get_y_max(self):
        return self.axes.get_ylim()[1]


class PctCongestedTimeCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.title_str = self.app.project.get_name() + ':'
        self.title_str = self.title_str + ' Percent of Day Congested over Time'
        self.axes.set_title(self.title_str)

    def compute_initial_figure(self):
        BIN1 = 25
        BIN2 = 35
        BIN3 = 45
        BIN4 = 55
        bin_limits = [BIN1, BIN2, BIN3, BIN4]
        bin_labels = [str(bin_limits[i]) + 'mph-' + str(bin_limits[i + 1]) + 'mph' for i in range(len(bin_limits) - 1)]
        bin_labels.insert(0, '<' + str(BIN1))
        bin_labels.append(str(BIN4) + '+')
        cl = ['#d62728', '#ff7f0e', '#dbdb8d', '#98df8a', '#2ca02c']
        bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
        data = self.app.plot_dfs[self.region]
        x_study_period = [el for el in range(len(data[bin_list[0]]))]

        self.axes.stackplot(x_study_period,
                            data[bin_list[0]],
                            data[bin_list[1]],
                            data[bin_list[2]],
                            data[bin_list[3]],
                            data[bin_list[4]],
                            labels=bin_labels,
                            colors=cl)
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=0))
        # self.axes.set_xlabel('Date')
        self.axes.set_ylabel('Percent Congested')
        self.axes.set_title(self.title_str)
        self.axes.legend()
        self.fig.tight_layout()

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()


class PctCongestedTMCCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.title_str = self.app.project.get_name() + ': '
        self.title_str = self.title_str + ' Percent Congested by TMC'
        self.axes.set_title(self.title_str)

    def compute_initial_figure(self):
        BIN1 = 25
        BIN2 = 35
        BIN3 = 45
        BIN4 = 55
        bin_limits = [BIN1, BIN2, BIN3, BIN4]
        bin_labels = [str(bin_limits[i]) + 'mph-' + str(bin_limits[i+1])+'mph' for i in range(len(bin_limits)-1)]
        bin_labels.insert(0, '<' + str(BIN1))
        bin_labels.append(str(BIN4) + '+')
        cl = ['#d62728', '#ff7f0e', '#dbdb8d', '#98df8a', '#2ca02c']
        bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
        data = self.app.plot_dfs[self.region]
        x_study_period = [el for el in range(len(data[bin_list[0]]))]

        self.axes.stackplot(x_study_period,
                            data[bin_list[0]],
                            data[bin_list[1]],
                            data[bin_list[2]],
                            data[bin_list[3]],
                            data[bin_list[4]],
                            labels=bin_labels,
                            colors=cl)
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=0))
        # self.axes.set_xlabel('TMC ID')
        self.axes.set_ylabel('Percent Congested')
        self.axes.set_title(self.title_str)
        self.axes.legend()
        self.fig.tight_layout()

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()


class ReliabilityCDFCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.title_str = self.app.project.get_name() + ': '
        if self.show_am:
            self.title_str = self.title_str + 'AM'
        if self.show_am and self.show_pm:
            self.title_str = self.title_str + '/'
        if self.show_pm:
            self.title_str = self.title_str + 'PM'
        self.title_str = self.title_str + ' Peak Travel Time CDFs by Month'
        self.axes.set_title(self.title_str)

        self.color_list = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', '#393b79', '#e7ba52']

    def compute_initial_figure(self):
        include_month = []
        for i in range(len(include_month)):
            if self.include_month[i]:
                tt_am_mean_dir1 = self.app.plot_dfs[0]['mean']
                tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
                tt_am_pct95_dir1 = self.app.plot_dfs[0]['percentile_95']
                x = [el for el in range(len(tt_am_mean_dir1))]
                self.axes.plot(x, tt_am_mean_dir1, color=self.color_list[i], linestyle='-', lw=2.0, label=calendar.month_abbr[i+1])

        self.axes.set_title(self.title_str)
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        if self.xlabel_func is not None:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.xlabel_func))
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.fig.tight_layout()

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()


def convert_index(indexes):
    return [convert_val(int(ap.get_text())) if ap.get_text() != '' else '' for ap in indexes]


def convert_val(idx):
    hour = idx // 12
    ampm = 'am'
    if hour >= 12:
        ampm = 'pm'
        hour = hour - 12
    if hour == 0:
        hour = 12
    min = (idx % 12) * 5

    return str(hour) + ':' + str(min) + ampm


class FourByFourPanel(QtWidgets.QWidget):
    def __init__(self, project):
        QtWidgets.QWidget.__init__(self)

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
        self.titles = ['Period 1: ' + dr1[0].toString('yyyy-MM-dd') + ' to ' + dr1[1].toString('yyyy-MM-dd'),
                       'Interim: ',
                       'Period 2: ' + dr2[0].toString('yyyy-MM-dd') + ' to ' + dr2[1].toString('yyyy-MM-dd')]
        self.plot_tt = self.tt_comp
        self.plot_dfs = [create_et_analysis(df) for df in self.dfs]
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
        elif cb_idx == 1:
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
            plot_days = []
            if self.check_mon.isChecked() is True:
                plot_days.append(0)
            if self.check_tue.isChecked() is True:
                plot_days.append(1)
            if self.check_wed.isChecked() is True:
                plot_days.append(2)
            if self.check_thu.isChecked() is True:
                plot_days.append(3)
            if self.check_fri.isChecked() is True:
                plot_days.append(4)
            if self.check_sat.isChecked() is True:
                plot_days.append(5)
            if self.check_sun.isChecked() is True:
                plot_days.append(6)

            if len(plot_days) > 0:
                self.plot_dfs = [create_et_analysis(df[df['weekday'].isin(plot_days)]) if df is not None else None for df in self.dfs]
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
        self.plot_subset_dfs = [create_et_analysis(df[df['tmc_code'].isin(self.tmc_subset)]) if df is not None else None for df in self.dfs]


class TwoByTwoPanelTimeTime(QtWidgets.QWidget):
    def __init__(self, project):
        QtWidgets.QWidget.__init__(self)

        self.init_mode = True

        self.project = project
        self.facility_len = self.project.database.get_tmcs()['miles'].sum()
        self.dfs = [self.project.database.get_data(), None, None]
        self.tt_comp = None
        self.available_days = self.project.database.get_available_days()
        self.titles = ['Period 1: ', 'Period 2: ', 'Period 3: ']
        self.plot_tt = self.tt_comp
        BIN1 = 25
        BIN2 = 35
        BIN3 = 45
        BIN4 = 55
        self.speed_bins = [BIN1, BIN2, BIN3, BIN4]
        self.plot_dfs = [create_timetime_analysis_v2(self.dfs[0]),
                         create_pct_congested_sp(self.dfs[0], self.speed_bins),
                         create_pct_congested_tmc(self.dfs[0], self.speed_bins)]
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.before_bar = QtWidgets.QWidget(self)
        self.after_bar = QtWidgets.QWidget(self)
        self.analysis_bar = QtWidgets.QWidget(self)
        self.v_layout_before = QtWidgets.QVBoxLayout(self.before_bar)
        self.v_layout_after = QtWidgets.QVBoxLayout(self.after_bar)
        self.h_layout_analysis = QtWidgets.QHBoxLayout(self.analysis_bar)
        start_date = self.project.database.get_first_date(as_datetime=True)
        l_func = lambda x, pos: convert_xval_to_month(x, pos, start_date.year, start_date.month)
        self.chart11 = TimeTimeLineChartCanvas(self, app=self, region=0, xlabel_func=l_func)
        self.chart21 = TimeTimeBarChartCanvas(self, app=self, region=0, xlabel_func=l_func)
        #self.chart12 = TimeTimeLineChartCanvas(self, app=self, region=0, xlabel_func=l_func, width=5, height=4, dpi=100)
        #self.chart22 = TimeTimeBarChartCanvas(self, app=self, region=0, xlabel_func=l_func, width=5, height=4, dpi=100)
        l_func_sp = lambda x, pos: convert_x_to_day(x, pos, self.project.database.get_first_date(as_datetime=True))
        self.chart12 = PctCongestedTimeCanvas(self, app=self, region=1, xlabel_func=l_func_sp)
        l_func_tmc = lambda x, pos: convert_x_to_tmc(x, pos, self.project.database.get_tmcs()['tmc'])
        self.chart22 = PctCongestedTMCCanvas(self, app=self, region=2, xlabel_func=l_func_tmc)
        #self.setup_figure_bounds()
        self.navi_toolbar11 = NavigationToolbar(self.chart11, self)
        self.navi_toolbar21 = NavigationToolbar(self.chart21, self)
        self.navi_toolbar12 = NavigationToolbar(self.chart12, self)
        self.navi_toolbar22 = NavigationToolbar(self.chart22, self)
        self.check_bar_day = QtWidgets.QWidget(self)
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar_day)
        self.check_wkdy = QtWidgets.QCheckBox('Weekdays')
        self.check_wknd = QtWidgets.QCheckBox("Weekends")
        self.check_am = QtWidgets.QCheckBox('AM')
        self.check_pm = QtWidgets.QCheckBox('PM')
        self.check_mid = QtWidgets.QCheckBox('Midday')
        self.check_mon = QtWidgets.QCheckBox('Mon')
        self.check_tue = QtWidgets.QCheckBox('Tue')
        self.check_wed = QtWidgets.QCheckBox('Wed')
        self.check_thu = QtWidgets.QCheckBox('Thu')
        self.check_fri = QtWidgets.QCheckBox('Fri')
        self.check_sat = QtWidgets.QCheckBox('Sat')
        self.check_sun = QtWidgets.QCheckBox('Sun')
        self.connect_check_boxes()
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
        weekend_checked =  self.check_wknd.isChecked()
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(weekend_checked)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(weekend_checked)
        self.no_compute = False
        self.check_func()

    def check_func(self):
        if not (self.init_mode or self.no_compute):
            plot_days = []
            if self.check_mon.isChecked() is True:
                plot_days.append(0)
            if self.check_tue.isChecked() is True:
                plot_days.append(1)
            if self.check_wed.isChecked() is True:
                plot_days.append(2)
            if self.check_thu.isChecked() is True:
                plot_days.append(3)
            if self.check_fri.isChecked() is True:
                plot_days.append(4)
            if self.check_sat.isChecked() is True:
                plot_days.append(5)
            if self.check_sun.isChecked() is True:
                plot_days.append(6)

            if len(plot_days) > 0:
                self.plot_dfs = [create_timetime_analysis_v2(self.dfs[0]),
                                 create_pct_congested_sp(self.dfs[0], self.speed_bins),
                                 create_pct_congested_tmc(self.dfs[0], self.speed_bins)]
                self.update_time_time()

    def check_peak_func(self):
        if not (self.init_mode or self.no_compute):
            include_am = self.check_am.isChecked()
            include_pm = self.check_pm.isChecked()
            include_mid = self.check_mid.isChecked()
            self.chart11.show_am = include_am
            self.chart21.show_am = include_am
            self.chart12.show_am = include_am
            self.chart22.show_am = include_am
            self.chart11.show_pm = include_pm
            self.chart21.show_pm = include_pm
            self.chart12.show_pm = include_pm
            self.chart22.show_pm = include_pm
            self.chart11.show_mid = include_mid
            self.chart21.show_mid = include_mid
            self.chart12.show_mid = include_mid
            self.chart22.show_mid = include_mid
            self.update_time_time()

    def update_time_time(self):
        self.chart11.update_figure()
        self.chart21.update_figure()
        self.chart11.draw()
        self.chart21.draw()
        self.chart12.update_figure()
        self.chart22.update_figure()
        self.chart12.draw()
        self.chart22.draw()


class FourByFourTimeTimePanel(QtWidgets.QWidget):
    def __init__(self, project):
        QtWidgets.QWidget.__init__(self)

        self.init_mode = True
        self.project = project
        self.facility_len = self.project.database.get_tmcs()['miles'].sum()
        self.dfs = [self.project.database.get_data(), None, None]
        self.tt_comp = None
        self.available_days = self.project.database.get_available_days()
        self.titles = ['Period 1: ', 'Period 2: ', 'Period 3: ']
        self.plot_tt = self.tt_comp
        self.plot_dfs = [create_timetime_analysis(df) for df in self.dfs]
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.before_bar = QtWidgets.QWidget(self)
        self.after_bar = QtWidgets.QWidget(self)
        self.analysis_bar = QtWidgets.QWidget(self)
        self.v_layout_before = QtWidgets.QVBoxLayout(self.before_bar)
        self.v_layout_after = QtWidgets.QVBoxLayout(self.after_bar)
        self.h_layout_analysis = QtWidgets.QHBoxLayout(self.analysis_bar)
        start_date = self.project.database.get_first_date(as_datetime=True)
        l_func = lambda x, pos: convert_xval_to_month(x, pos, start_date.year, start_date.month)
        self.chart11 = TimeTimeLineChartCanvas(self, app=self, region=0, xlabel_func=l_func, show_am=True, show_pm=False)
        self.chart21 = TimeTimeBarChartCanvas(self, app=self, region=0, xlabel_func=l_func, show_am=True, show_pm=False)
        self.chart12 = TimeTimeLineChartCanvas(self, app=self, region=0, xlabel_func=l_func, show_am=False, show_pm=True)
        self.chart22 = TimeTimeBarChartCanvas(self, app=self, region=0, xlabel_func=l_func, show_am=False, show_pm=True)
        #self.setup_figure_bounds()
        self.navi_toolbar11 = NavigationToolbar(self.chart11, self)
        self.navi_toolbar21 = NavigationToolbar(self.chart21, self)
        self.navi_toolbar12 = NavigationToolbar(self.chart12, self)
        self.navi_toolbar22 = NavigationToolbar(self.chart22, self)
        self.check_bar_day = QtWidgets.QWidget(self)
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
        weekend_checked =  self.check_wknd.isChecked()
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(weekend_checked)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(weekend_checked)
        self.no_compute = False
        self.check_func()

    def check_func(self):
        if not (self.init_mode or self.no_compute):
            plot_days = []
            if self.check_mon.isChecked() is True:
                plot_days.append(0)
            if self.check_tue.isChecked() is True:
                plot_days.append(1)
            if self.check_wed.isChecked() is True:
                plot_days.append(2)
            if self.check_thu.isChecked() is True:
                plot_days.append(3)
            if self.check_fri.isChecked() is True:
                plot_days.append(4)
            if self.check_sat.isChecked() is True:
                plot_days.append(5)
            if self.check_sun.isChecked() is True:
                plot_days.append(6)

            if len(plot_days) > 0:
                self.plot_dfs = [create_timetime_analysis(df[df['weekday'].isin(plot_days)]) if df is not None else None for df in self.dfs]
                self.update_time_time()

    def update_time_time(self):
        self.chart11.update_figure()
        self.chart21.update_figure()
        self.chart11.draw()
        self.chart21.draw()
        self.chart12.update_figure()
        self.chart22.update_figure()
        self.chart12.draw()
        self.chart22.draw()


class FourByFourPanel2(QtWidgets.QWidget):
    def __init__(self, db):
        QtWidgets.QWidget.__init__(self)
        self.init_mode = True

        self.facility_len = db.tmc_df['miles'].sum()
        self.db = db
        ######## Create data
        self.plot_tt = self.db.tt_comp
        self.plot_dfs = [create_et_analysis(df) for df in self.db.data]
        ######## End create data
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.before_bar = QtWidgets.QWidget(self)
        self.after_bar = QtWidgets.QWidget(self)
        self.analysis_bar = QtWidgets.QWidget(self)
        self.v_layout_before = QtWidgets.QVBoxLayout(self.before_bar)
        self.v_layout_after = QtWidgets.QVBoxLayout(self.after_bar)
        self.h_layout_analysis = QtWidgets.QHBoxLayout(self.analysis_bar)
        ######### Create charts
        self.chart11 = ExtraTimeAreaChartCanvas(self, app=self, region=0)
        self.chart21 = SpeedBandCanvas(self, app=self, region=0)
        self.chart12 = ExtraTimeAreaChartCanvas(self, app=self, region=2, region2=0)
        self.chart22 = SpeedBandCanvas(self, app=self, region=2, region2=0)
        self.setup_figure_bounds()
        ######### End Create charts
        self.navi_toolbar11 = NavigationToolbar(self.chart11, self)
        self.navi_toolbar21 = NavigationToolbar(self.chart21, self)
        self.navi_toolbar12 = NavigationToolbar(self.chart12, self)
        self.navi_toolbar22 = NavigationToolbar(self.chart22, self)
        # Creating day filter checks
        self.check_bar_day = QtWidgets.QWidget(self)
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar_day)
        self.check_wkdy = QtWidgets.QCheckBox('Weekdays')
        self.check_wknd = QtWidgets.QCheckBox("Weekends")        
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setLineWidth(5)
        line.setMidLineWidth(5)
        self.check_mon = QtWidgets.QCheckBox('Mon')
        self.check_tue = QtWidgets.QCheckBox('Tue')
        self.check_wed = QtWidgets.QCheckBox('Wed')
        self.check_thu = QtWidgets.QCheckBox('Thu')
        self.check_fri = QtWidgets.QCheckBox('Fri')
        self.check_sat = QtWidgets.QCheckBox('Sat')
        self.check_sun = QtWidgets.QCheckBox('Sun')
        self.connect_check_boxes()
        self.h_layout.addWidget(self.check_wkdy)
        self.h_layout.addWidget(self.check_wknd)
        self.h_layout.addWidget(line)
        self.h_layout.addWidget(self.check_mon)
        self.h_layout.addWidget(self.check_tue)
        self.h_layout.addWidget(self.check_wed)
        self.h_layout.addWidget(self.check_thu)
        self.h_layout.addWidget(self.check_fri)
        self.h_layout.addWidget(self.check_sat)
        self.h_layout.addWidget(self.check_sun)
        # Creating month filter checks
        self.check_bar_month = QtWidgets.QWidget(self)
        self.h_layout2 = QtWidgets.QHBoxLayout(self.check_bar_month)
        self.check_jan = QtWidgets.QCheckBox('Jan')
        self.check_feb = QtWidgets.QCheckBox('Feb')
        self.check_mar = QtWidgets.QCheckBox('Mar')
        self.check_apr = QtWidgets.QCheckBox('Apr')
        self.check_may = QtWidgets.QCheckBox('May')
        self.check_jun = QtWidgets.QCheckBox('Jun')
        self.check_jul = QtWidgets.QCheckBox('Jul')
        self.check_aug = QtWidgets.QCheckBox('Aug')
        self.check_sep = QtWidgets.QCheckBox('Sep')
        self.check_oct = QtWidgets.QCheckBox('Oct')
        self.check_nov = QtWidgets.QCheckBox('Nov')
        self.check_dec = QtWidgets.QCheckBox('Dec')
        self.connect_check_boxes_month()
        self.h_layout2.addWidget(self.check_jan)
        self.h_layout2.addWidget(self.check_feb)
        self.h_layout2.addWidget(self.check_mar)
        self.h_layout2.addWidget(self.check_apr)
        self.h_layout2.addWidget(self.check_may)
        self.h_layout2.addWidget(self.check_jun)
        self.h_layout2.addWidget(self.check_jul)
        self.h_layout2.addWidget(self.check_aug)
        self.h_layout2.addWidget(self.check_sep)
        self.h_layout2.addWidget(self.check_oct)
        self.h_layout2.addWidget(self.check_nov)
        self.h_layout2.addWidget(self.check_dec)
        # Combining check-box bars
        self.check_bars = QtWidgets.QWidget()
        self.v_layout_checks = QtWidgets.QVBoxLayout(self.check_bars)
        self.v_layout_checks.addWidget(self.check_bar_day)
        self.v_layout_checks.addWidget(self.check_bar_month)
        # Creating full layout
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
        self.v_layout.addWidget(self.check_bars)

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

    def connect_check_boxes_month(self):
        print("implement this")


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
        weekend_checked =  self.check_wknd.isChecked()
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(weekend_checked)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(weekend_checked)
        self.no_compute = False
        self.check_func()


    def check_func(self):
        if not (self.init_mode or self.no_compute):
            plot_days = []
            if self.check_mon.isChecked() is True:
                plot_days.append(0)
            if self.check_tue.isChecked() is True:
                plot_days.append(1)
            if self.check_wed.isChecked() is True:
                plot_days.append(2)
            if self.check_thu.isChecked() is True:
                plot_days.append(3)
            if self.check_fri.isChecked() is True:
                plot_days.append(4)
            if self.check_sat.isChecked() is True:
                plot_days.append(5)
            if self.check_sun.isChecked() is True:
                plot_days.append(6)

            if len(plot_days) > 0:
                self.plot_dfs = [create_et_analysis(df[df['weekday'].isin(plot_days)]) for df in self.dfs]
                self.update_extra_time()

    def update_extra_time(self):
        self.chart11.update_figure()
        self.chart21.update_figure()
        self.chart11.draw()
        self.chart21.draw()
        self.chart12.update_figure()
        self.chart22.update_figure()
        self.chart12.draw()
        self.chart22.draw()


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


class ShortNaviToolbar(NavigationToolbar):
    toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home', 'Zoom', 'Save')]


def convert_xval_to_month(x, pos, first_year, first_month):
    first_month -= 1  # decrementing to help with modulus
    if x < 0:
        return ''
    x = int(x)
    return str(first_year + ((first_month + x) // 12)) + '-' + calendar.month_abbr[((first_month + x) % 12) + 1]


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

def convert_x_to_day_dep(x, pos, start_date):
  if x < 0:
    return ''
  first_year = start_date.year
  first_month = start_date.month
  first_month -= 1  # decrementing to help with modulus
  x = int(x)
  month = x // (31)
  #hour = (x + 10) % 24
  #ampm_str = 'am'
  #if hour >= 12:
  #  ampm_str = 'pm'
  #  hour -= 12
  #if hour == 0:
  #  hour = 12
  return str(first_year + ((first_month + month) // 12)) + '-' + calendar.month_abbr[((first_month + month) % 12) + 1]  # + '\n' + str(hour) + ':' + '00' + ampm_str


def convert_x_to_day(x, pos, start_date):
    # if int(x) - x != 0:
    #     return ''
    # new_date = start_date + timedelta(days=int(x))
    new_date = start_date + timedelta(days=x)
    return new_date.strftime('%m/%d/%Y') + '\n' + calendar.day_abbr[new_date.weekday()]


def convert_x_to_tmc(x, pos, tmc_list):
    if x >= 0 and x < len(tmc_list):
        return tmc_list[int(x)]
    else:
        return 0