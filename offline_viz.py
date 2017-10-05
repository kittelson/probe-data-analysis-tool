from PyQt5 import QtWidgets
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from stat_func import create_et_analysis, create_timetime_analysis


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

    def __init__(self, parent=None, app=None, region=0, region2=-1, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setFocus()
        self.app = None
        if app is not None:
            self.app = app
        self.region = region
        self.region2 = region2

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
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)


class ExtraTimeAreaChartCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.stackplot(self.app.plot_dfs[self.region].index,
                            self.app.plot_dfs[self.region]['mean'],
                            self.app.plot_dfs[self.region]['extra_time'],
                            labels=['Average', '95th Percentile'], colors=[TT_BLUE, TT_RED])
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                            self.app.plot_dfs[self.region2]['mean'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           self.app.plot_dfs[self.region2]['percentile_95'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th PCT')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def update_figure(self):
        self.axes.cla()
        self.axes.stackplot(self.app.plot_dfs[self.region].index,
                            self.app.plot_dfs[self.region]['mean'],
                            self.app.plot_dfs[self.region]['extra_time'],
                            labels=['Average', '95th Percentile'], colors=[TT_BLUE, TT_RED])
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                            self.app.plot_dfs[self.region2]['mean'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           self.app.plot_dfs[self.region2]['percentile_95'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th PCT')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def get_y_max(self):
        return self.axes.get_ylim()[1]


class SpeedBandCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               color=SB_BLUE)
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'],
                               color=SB_BLUE)
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'], color=SB_BLUE, label='5th Percentile')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'], color=SB_RED, label='Average')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'], color=SB_BLUE, label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['mean'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['percentile_95'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Percentile')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([0, 80])
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def update_figure(self):
        self.axes.cla()
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               color=SB_BLUE)
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'],
                               color=SB_BLUE)
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'], color=SB_BLUE, label='5th Percentile')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'], color=SB_RED, label='Average')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'], color=SB_BLUE, label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['mean'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['percentile_95'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Percentile')
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([0, 80])
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)


class TimeTimeLineChartCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.show_am = True
        self.show_pm = True

    def compute_initial_figure(self):
        tt_am_mean_dir1 = self.app.plot_dfs[0]['mean']
        tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
        tt_am_pct95_dir1 = self.app.plot_dfs[0]['percentile_95']
        tt_pm_mean_dir1 = self.app.plot_dfs[0]['meanpm']
        tt_pm_pct5_dir1 = self.app.plot_dfs[0]['percentile_5pm']
        tt_pm_pct95_dir1 = self.app.plot_dfs[0]['percentile_95pm']

        x = [el for el in range(len(tt_am_mean_dir1))]

        self.axes.plot(x, tt_am_mean_dir1, color='C0', linestyle='-', lw=2.0, label='AM-Mean')
        self.axes.plot(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
        self.axes.plot(x, tt_am_pct95_dir1, color='C0', linestyle='--', lw=1.0, label='AM-95th Pct')

        self.axes.plot(x, tt_pm_mean_dir1, color='C1', linestyle='-', lw=2.0, label='PM-Mean')
        self.axes.plot(x, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
        self.axes.plot(x, tt_pm_pct95_dir1, color='C1', linestyle='--', lw=1.0, label='PM-95th Pct')

        #self.axes.set_title(dirs[0] + ' Peak Travel Times over Time' + ' (' + '{:1.2f}'.format(facility_len1) + ' mi)')
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        self.axes.set_xticks([0, 5, 10, 15, 20])
        self.axes.set_xticklabels(['2015 Dec', '2016 May', '2016 Oct', '2017 March', '2017 Aug'])
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def update_figure(self):
        self.axes.cla()
        tt_am_mean_dir1 = self.app.plot_dfs[0]['mean']
        tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
        tt_am_pct95_dir1 = self.app.plot_dfs[0]['percentile_95']
        tt_pm_mean_dir1 = self.app.plot_dfs[0]['meanpm']
        tt_pm_pct5_dir1 = self.app.plot_dfs[0]['percentile_5pm']
        tt_pm_pct95_dir1 = self.app.plot_dfs[0]['percentile_95pm']

        x = [el for el in range(len(tt_am_mean_dir1))]

        if self.show_am:
            self.axes.plot(x, tt_am_mean_dir1, color='C0', linestyle='-', lw=2.0, label='AM-Mean')
            self.axes.plot(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.plot(x, tt_am_pct95_dir1, color='C0', linestyle='--', lw=1.0, label='AM-95th Pct')

        if self.show_pm:
            self.axes.plot(x, tt_pm_mean_dir1, color='C1', linestyle='-', lw=2.0, label='PM-Mean')
            self.axes.plot(x, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.plot(x, tt_pm_pct95_dir1, color='C1', linestyle='--', lw=1.0, label='PM-95th Pct')

        #self.axes.set_title(dirs[0] + ' Peak Travel Times over Time' + ' (' + '{:1.2f}'.format(facility_len1) + ' mi)')
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        self.axes.set_xticks([0, 5, 10, 15, 20])
        self.axes.set_xticklabels(['2015 Dec', '2016 May', '2016 Oct', '2017 March', '2017 Aug'])
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def get_y_max(self):
        return self.axes.get_ylim()[1]


class TimeTimeBarChartCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.show_am = True
        self.show_pm = True

    def compute_initial_figure(self):
        tt_am_mean_dir1 = self.app.plot_dfs[0]['mean']
        tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
        tt_am_pct95_dir1 = self.app.plot_dfs[0]['percentile_95']
        tt_pm_mean_dir1 = self.app.plot_dfs[0]['meanpm']
        tt_pm_pct5_dir1 = self.app.plot_dfs[0]['percentile_5pm']
        tt_pm_pct95_dir1 = self.app.plot_dfs[0]['percentile_95pm']

        x = [el for el in range(len(tt_am_mean_dir1))]

        width = 0.35
        self.axes.bar(x, tt_am_mean_dir1, width, color='C0', label='AM-Mean')
        # ax3.bar(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
        self.axes.bar(x, [tt_am_pct95_dir1[i] - tt_am_mean_dir1[i] for i in range(len(tt_am_mean_dir1))], width, bottom=tt_am_mean_dir1, color='#aec7e8',
                label='AM-95th Pct')

        self.axes.bar([el + width for el in x], tt_pm_mean_dir1, width, color='C1', label='PM-Mean')
        # ax1.bar(x + width, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
        self.axes.bar([el + width for el in x], [tt_pm_pct95_dir1[i] - tt_pm_mean_dir1[i] for i in range(len(tt_pm_mean_dir1))], width,
                bottom=tt_pm_mean_dir1, color='#ffbb78', label='PM-95th Pct')

        # self.axes.set_title(dirs[0] + ' Peak Travel Times over Time' + ' (' + '{:1.2f}'.format(facility_len1) + ' mi)')
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        self.axes.set_xticks([0, 5, 10, 15, 20])
        self.axes.set_xticklabels(['2015 Dec', '2016 May', '2016 Oct', '2017 March', '2017 Aug'])

    def update_figure(self):
        self.axes.cla()
        tt_am_mean_dir1 = self.app.plot_dfs[0]['mean']
        tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
        tt_am_pct95_dir1 = self.app.plot_dfs[0]['percentile_95']
        tt_pm_mean_dir1 = self.app.plot_dfs[0]['meanpm']
        tt_pm_pct5_dir1 = self.app.plot_dfs[0]['percentile_5pm']
        tt_pm_pct95_dir1 = self.app.plot_dfs[0]['percentile_95pm']

        x = [el for el in range(len(tt_am_mean_dir1))]

        width = 0.35
        if self.show_am:
            self.axes.bar(x, tt_am_mean_dir1, width, color='C0', label='AM-Mean')
            # ax3.bar(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.bar(x, [tt_am_pct95_dir1[i] - tt_am_mean_dir1[i] for i in range(len(tt_am_mean_dir1))], width, bottom=tt_am_mean_dir1,
                          color='#aec7e8',
                          label='AM-95th Pct')

        if self.show_pm:
            self.axes.bar([el + width for el in x], tt_pm_mean_dir1, width, color='C1', label='PM-Mean')
            # ax1.bar(x + width, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.bar([el + width for el in x], [tt_pm_pct95_dir1[i] - tt_pm_mean_dir1[i] for i in range(len(tt_pm_mean_dir1))], width,
                          bottom=tt_pm_mean_dir1, color='#ffbb78', label='PM-95th Pct')

        # self.axes.set_title(dirs[0] + ' Peak Travel Times over Time' + ' (' + '{:1.2f}'.format(facility_len1) + ' mi)')
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        self.axes.set_xticks([0, 5, 10, 15, 20])
        self.axes.set_xticklabels(['2015 Dec', '2016 May', '2016 Oct', '2017 March', '2017 Aug'])

    def get_y_max(self):
        return self.axes.get_ylim()[1]


class ReliabilityCDFCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               color=SB_BLUE)
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'],
                               color=SB_BLUE)
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'], color=SB_BLUE, label='5th Percentile')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'], color=SB_RED, label='Average')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'], color=SB_BLUE, label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['mean'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['percentile_95'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Percentile')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([0, 80])
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def update_figure(self):
        self.axes.cla()
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               color=SB_BLUE)
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'],
                               (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'],
                               color=SB_BLUE)
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_5'], color=SB_BLUE, label='5th Percentile')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['mean'], color=SB_RED, label='Average')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * self.app.facility_len) / self.app.plot_dfs[self.region]['percentile_95'], color=SB_BLUE, label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['mean'],
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * self.app.facility_len) / self.app.plot_dfs[self.region2]['percentile_95'],
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Percentile')
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([0, 80])
        self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
        self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)


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
    def __init__(self, tmcs, data, travel_time_comp, available_days, titles):
        QtWidgets.QWidget.__init__(self)
        self.init_mode = True

        self.facility_len = tmcs['miles'].sum()
        #print(self.facility_len)
        self.dfs = data
        self.tt_comp = travel_time_comp
        self.available_days = available_days
        self.titles = titles

        self.plot_tt = self.tt_comp
        self.plot_dfs = [create_et_analysis(df) for df in self.dfs]
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.before_bar = QtWidgets.QWidget(self)
        self.after_bar = QtWidgets.QWidget(self)
        self.analysis_bar = QtWidgets.QWidget(self)
        self.v_layout_before = QtWidgets.QVBoxLayout(self.before_bar)
        self.v_layout_after = QtWidgets.QVBoxLayout(self.after_bar)
        self.h_layout_analysis = QtWidgets.QHBoxLayout(self.analysis_bar)
        self.chart11 = ExtraTimeAreaChartCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        self.chart21 = SpeedBandCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        self.chart12 = ExtraTimeAreaChartCanvas(self, app=self, region=2, region2=0, width=5, height=4, dpi=100)
        self.chart22 = SpeedBandCanvas(self, app=self, region=2, region2=0, width=5, height=4, dpi=100)
        self.setup_figure_bounds()
        self.navi_toolbar11 = NavigationToolbar(self.chart11, self)
        self.navi_toolbar21 = NavigationToolbar(self.chart21, self)
        self.navi_toolbar12 = NavigationToolbar(self.chart12, self)
        self.navi_toolbar22 = NavigationToolbar(self.chart22, self)
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


class FourByFourPanelTimeTime(QtWidgets.QWidget):
    def __init__(self, tmcs, data, travel_time_comp, available_days, titles):
        QtWidgets.QWidget.__init__(self)
        self.init_mode = True

        self.facility_len = tmcs['miles'].sum()
        #print(self.facility_len)
        self.dfs = data
        self.tt_comp = travel_time_comp
        self.available_days = available_days
        self.titles = titles

        self.plot_tt = self.tt_comp
        self.plot_dfs = [create_timetime_analysis(df) for df in self.dfs]
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.before_bar = QtWidgets.QWidget(self)
        self.after_bar = QtWidgets.QWidget(self)
        self.analysis_bar = QtWidgets.QWidget(self)
        self.v_layout_before = QtWidgets.QVBoxLayout(self.before_bar)
        self.v_layout_after = QtWidgets.QVBoxLayout(self.after_bar)
        self.h_layout_analysis = QtWidgets.QHBoxLayout(self.analysis_bar)
        self.chart11 = TimeTimeLineChartCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        self.chart21 = TimeTimeBarChartCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        self.chart12 = TimeTimeLineChartCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        self.chart22 = TimeTimeBarChartCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        #self.setup_figure_bounds()
        self.navi_toolbar11 = NavigationToolbar(self.chart11, self)
        self.navi_toolbar21 = NavigationToolbar(self.chart21, self)
        self.navi_toolbar12 = NavigationToolbar(self.chart12, self)
        self.navi_toolbar22 = NavigationToolbar(self.chart22, self)
        self.check_bar_day = QtWidgets.QWidget(self)
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar_day)
        self.check_wkdy = QtWidgets.QCheckBox('Weekdays')
        self.check_wknd = QtWidgets.QCheckBox("Weekends")
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setLineWidth(5)
        line.setMidLineWidth(5)
        line2 = QtWidgets.QFrame(self)
        line2.setFrameShape(QtWidgets.QFrame.VLine)
        line2.setLineWidth(5)
        line2.setMidLineWidth(5)
        self.check_am = QtWidgets.QCheckBox('AM')
        self.check_pm = QtWidgets.QCheckBox('PM')
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
        self.h_layout.addWidget(line)
        self.h_layout.addWidget(self.check_wkdy)
        self.h_layout.addWidget(self.check_wknd)
        self.h_layout.addWidget(line2)
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

    def check_peak_func(self):
        if not (self.init_mode or self.no_compute):
            include_am = self.check_am.isChecked()
            include_pm = self.check_pm.isChecked()
            self.chart11.show_am = include_am
            self.chart21.show_am = include_am
            self.chart12.show_am = include_am
            self.chart22.show_am = include_am
            self.chart11.show_pm = include_pm
            self.chart21.show_pm = include_pm
            self.chart12.show_pm = include_pm
            self.chart22.show_pm = include_pm
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
        self.chart11 = ExtraTimeAreaChartCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        self.chart21 = SpeedBandCanvas(self, app=self, region=0, width=5, height=4, dpi=100)
        self.chart12 = ExtraTimeAreaChartCanvas(self, app=self, region=2, region2=0, width=5, height=4, dpi=100)
        self.chart22 = SpeedBandCanvas(self, app=self, region=2, region2=0, width=5, height=4, dpi=100)
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

            if event.key is "control":
                new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                if xdata is not None:
                    relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
                    ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            elif event.key is "shift":
                new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
                if ydata is not None:
                    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
                    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
            else:
                new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
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


class ShortNaviToolbar(NavigationToolbar):
    toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home', 'Zoom', 'Save')]
