"""
Creates the matplotlib charts via FigureCanvas for the visualizations
All charts the MplChart class, but the visualization is determined by the “fig_type” field
Contains the ZoomPan class for dynamic interaction with the MPL charts without the need for the navigation toolbar.
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib import animation
import matplotlib.collections as collections
import calendar
from datetime import datetime, timedelta, time
from math import floor
from chart_defaults import TT_RED_BEFORE, TT_RED, TT_BLUE_BEFORE, TT_BLUE, BEFORE_LW, SB_BLUE, SB_RED, create_dq_cmap
from numpy import histogram as np_hist
from numpy import append as np_append
from numpy import pi as np_pi
from numpy import arange as np_arange
from numpy import linspace as np_linspace
from numpy import random as np_rand
from math import ceil
from pandas import DataFrame
import DataHelper

FIG_TYPE_TT_TREND_LINE = 0
FIG_TYPE_TT_TREND_BAR = 1
FIG_TYPE_SPD_HEAT_MAP = 2
FIG_TYPE_SPD_HEAT_MAP_FACILITY = 3
FIG_TYPE_PCT_CONG_DAY = 4
FIG_TYPE_PCT_CONG_TMC = 5

FIG_TYPE_EXTRA_TIME = 200
FIG_TYPE_SPD_BAND = 201
FIG_TYPE_TT_CDF = 202
FIG_TYPE_SPD_FREQ = 203

FIG_TYPE_LOTTR_CORR_SUMM = 300
FIG_TYPE_LOTTR_CORR_ALL = 301
FIG_TYPE_LOTTR_TMC = 302

FIG_DQ_WKDY = 100
FIG_DQ_TOD = 101
FIG_DQ_TMC = 102
FIG_DQ_SP = 103

PEAK_24HR = 0
PEAK_AM = 1
PEAK_MID = 2
PEAK_PM = 3

NONE = -1
AFTER = 0
BEFORE = 1


class MplChart(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, fig_type=0, panel=None, region=AFTER, region2=NONE, is_subset=False, width=5, height=4, dpi=100, **kwargs):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        is_polar = fig_type == FIG_DQ_TOD
        self.axes = self.fig.add_subplot(111, polar=is_polar)
        self.fig_type = fig_type

        FigureCanvas.__init__(self, self.fig)

        if parent is not None:
            self.setParent(parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setFocus()
        self.panel = None
        self.project = None
        self.fig_title_str = ''
        if panel is not None:
            self.panel = panel
            self.fig_title_str = self.panel.project.get_name()
            self.project = self.panel.project

        self.region = region
        self.region2 = region2
        self.is_subset = is_subset

        self.bbox_adjusted = False
        self.default_xlim = None
        self.default_ylim = None

        self.show_am = True
        self.show_pm = True
        self.show_mid = False

        self.frames = 9
        self.wkdy_bars = None
        self.tmc_bars = None
        self.tod_bars = None
        self.sp_bars1 = None
        self.sp_bars2 = None

        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='darkslategrey', alpha=0.5),
                                            color='white',
                                            annotation_clip=False)
        self.hover_ann.set_visible(False)
        self.tmc_ext = 0

        if kwargs is not None:
            if 'show_am' in kwargs:
                self.show_am = kwargs['show_am']
            if 'show_pm' in kwargs:
                self.show_pm = kwargs['show_pm']
            if 'show_mid' in kwargs:
                self.show_mid = kwargs['show_mid']
            if 'project' in kwargs:
                self.project = kwargs['project']

        start_date = self.project.database.get_first_date(as_datetime=True)

        self.f_x_to_month = lambda x, pos: convert_xval_to_month(x, pos, start_date.year, start_date.month)
        # self.f_x_to_day = lambda x, pos: convert_x_to_day(x, pos, self.project.database.get_first_date(as_datetime=True))
        self.f_x_to_day = lambda x, pos: convert_x_to_day(x, pos, start_date, two_lines=True)
        self.f_x_to_day_1l = lambda x, pos: convert_x_to_day(x, pos, start_date, two_lines=False)
        self.f_x_to_tmc = lambda x, pos: convert_x_to_tmc(x, pos, self.project.get_tmc(as_list=True))
        self.f_x_to_mile = lambda x, pos: convert_x_to_mile(x, pos, self.project.get_tmc(as_list=True), self.panel.facility_len)
        self.f_y_to_time = lambda y, pos: convert_xval_to_time(y, pos, self.project.data_res)

        self.color_bar1 = None
        self.color_bar2 = None

        self.compute_initial_figure()

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)

        FigureCanvas.updateGeometry(self)

        self.context_menu = QtWidgets.QMenu(self)

        self.edit_dq_thresholds_action = QtWidgets.QAction('Edit Thresholds')
        self.edit_dq_thresholds_action.setToolTip('Edit the threshold lines on the Data Availability Charts')
        self.edit_dq_thresholds_action.triggered.connect(self.project.main_window.edit_dq_thresholds)
        if self.fig_type == FIG_DQ_WKDY or self.fig_type == FIG_DQ_TMC or self.fig_type == FIG_DQ_WKDY:
            self.context_menu.addAction(self.edit_dq_thresholds_action)
            self.context_menu.addSeparator()

        self.adjust_speed_thresholds_action = QtWidgets.QAction('Adjust Color Range')
        self.adjust_speed_thresholds_action.triggered.connect(self.project.main_window.edit_stage1_options)
        if self.fig_type == FIG_TYPE_SPD_HEAT_MAP_FACILITY or self.fig_type == FIG_TYPE_SPD_HEAT_MAP:
            self.context_menu.addAction(self.adjust_speed_thresholds_action)
            self.context_menu.addSeparator()

        self.save_figure_action = QtWidgets.QAction('Save Chart as Image', self)
        self.save_figure_action.setToolTip('Save the chart as an image file (png, jpg, etc.)')
        self.save_figure_action.triggered.connect(self.save_figure)
        self.context_menu.addAction(self.save_figure_action)

        self.export_data_action = QtWidgets.QAction('Export Chart Data', self)
        self.export_data_action.setToolTip('Save the chart data as a csv file')
        self.export_data_action.triggered.connect(self.export_data)
        self.context_menu.addAction(self.export_data_action)

        if self.fig_type != FIG_DQ_TOD:
            self.context_menu.addSeparator()
            self.toggle_legend_action = QtWidgets.QAction('Toggle Chart Legend', self)
            self.toggle_legend_action.setToolTip('Toggle the chart legend on/off')
            self.toggle_legend_action.triggered.connect(self.toggle_legend)
            self.context_menu.addAction(self.toggle_legend_action)

            self.reset_axis_action = QtWidgets.QAction('Reset Axis Bounds', self)
            self.reset_axis_action.setToolTip('Reset the x and y bounds of the chart')
            self.reset_axis_action.triggered.connect(self.reset_axis_bounds)
            self.context_menu.addAction(self.reset_axis_action)

        if self.fig_type == FIG_TYPE_SPD_HEAT_MAP_FACILITY:
            self.toggle_scaled_action = QtWidgets.QAction('Scale Y-Axis by TMC Length', self)
            self.toggle_scaled_action.setToolTip('Set whether each TMC is displayed with a width relative to its ' +
                                                 'length or if all TMCs are scaled uniformly.')
            self.toggle_scaled_action.setCheckable(True)
            self.toggle_scaled_action.setChecked(True)
            self.toggle_scaled_action.triggered.connect(self.panel.toggle_data_scaled)
            self.context_menu.addAction(self.toggle_scaled_action)

        if self.fig_type == FIG_TYPE_SPD_HEAT_MAP_FACILITY or self.fig_type == FIG_TYPE_SPD_HEAT_MAP:
            self.context_menu.addSeparator()
            self.toggle_stacked_action = QtWidgets.QAction('Sort X-Axis by Date', self)
            self.toggle_stacked_action.setToolTip('Toggle between sorting the X-Axis by date versus sorting it by speed.')
            self.toggle_stacked_action.setCheckable(True)
            self.toggle_stacked_action.setChecked(True)
            self.toggle_stacked_action.triggered.connect(self.panel.toggle_data_stacked)
            self.context_menu.addAction(self.toggle_stacked_action)

        if self.fig_type == FIG_TYPE_SPD_HEAT_MAP_FACILITY or self.fig_type == FIG_TYPE_SPD_HEAT_MAP or self.fig_type == FIG_TYPE_PCT_CONG_DAY \
                or self.fig_type == FIG_TYPE_TT_TREND_LINE or self.fig_type == FIG_TYPE_TT_TREND_BAR:
            self.toggle_before_after_action = QtWidgets.QAction('Show Before/After Ranges', self)
            self.toggle_before_after_action.setToolTip('Set whether the before and after ranges are displayed on the chart.')
            self.toggle_before_after_action.setCheckable(True)
            self.toggle_before_after_action.setChecked(False)
            self.toggle_before_after_action.triggered.connect(self.panel.toggle_before_after)
            self.context_menu.addAction(self.toggle_before_after_action)

        scale = 1.1
        self.zp = ZoomPan()
        if self.fig_type != FIG_DQ_TOD:
            figZoom = self.zp.zoom_factory(self.axes, self, base_scale=scale)
        figPan = self.zp.pan_factory(self.axes, self)
        self.set_x_bounds(self.axes.get_xlim()[0], self.axes.get_xlim()[1], make_default=True)
        self.set_y_bounds(self.axes.get_ylim()[0], self.axes.get_ylim()[1], make_default=True)

    def manual_ani_tod(self, event):
        anim = animation.FuncAnimation(self.fig, self.animate_tod, frames=self.frames + 1, interval=1, repeat=False, blit=False)
        # anim.save('test_anim_file.html')
        self.draw_idle()

    def manual_ani_wkdy(self, event):
        anim = animation.FuncAnimation(self.fig, self.animate_wkdy, frames=self.frames + 1, interval=1, repeat=False, blit=False)
        self.draw()
        # self.draw_idle()

    def manual_ani_tmc(self, event):
        anim = animation.FuncAnimation(self.fig, self.animate_tmc, frames=self.frames + 1, interval=1, repeat=False, blit=False)
        self.draw()
        # self.draw_idle()

    def manual_ani_sp(self, event):
        anim = animation.FuncAnimation(self.fig, self.animate_sp, frames=self.frames + 1, interval=1, repeat=False, blit=False)
        self.draw()
        # self.draw_idle()

    def toggle_legend(self):
        if self.axes.legend_ is not None:
            self.axes.legend_ = None
        else:
            # self.axes.legend()
            if self.fig_type is not FIG_TYPE_TT_TREND_BAR:
                self.axes.legend()
            elif self.fig_type is FIG_TYPE_TT_TREND_BAR and not self.panel.plot_dfs[0].empty:
                self.axes.legend()
        self.draw()

    def set_x_bounds(self, x_min, x_max, make_default=False):
        self.axes.set_xbound([x_min, x_max])
        if make_default:
            self.default_xlim = [x_min, x_max]

    def set_y_bounds(self, y_min, y_max, make_default=False):
        self.axes.set_ybound([y_min, y_max])
        if make_default:
            self.default_ylim = [y_min, y_max]

    def reset_axis_bounds(self):
        if self.default_xlim is not None:
            self.axes.set_xlim(self.default_xlim)
        if self.default_ylim is not None:
            self.axes.set_ylim(self.default_ylim)
        self.draw()

    def set_fig_type(self, fig_type):
        self.fig_type = fig_type

    def save_figure(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '', 'PNG files (*.png);;PDF files (*.pdf);;JPEG files (*.jpg)',
                                                                    'PNG files (*.png)')
        if f_name:
            self.fig.savefig(f_name)

    def update_title(self):
        pass

    def compute_initial_figure(self):
        if self.fig_type == FIG_TYPE_TT_TREND_LINE:
            self.compute_trend_line()
        elif self.fig_type == FIG_TYPE_TT_TREND_BAR:
            self.compute_trend_bar()
        elif self.fig_type == FIG_TYPE_PCT_CONG_DAY:
            self.compute_pct_cong_day()
        elif self.fig_type == FIG_TYPE_PCT_CONG_TMC:
            self.compute_pct_cong_tmc()
        elif self.fig_type == FIG_TYPE_SPD_HEAT_MAP:
            self.compute_speed_heatmap()
        elif self.fig_type == FIG_TYPE_SPD_HEAT_MAP_FACILITY:
            self.compute_speed_tmc_heatmap()
        elif self.fig_type == FIG_TYPE_EXTRA_TIME:
            self.compute_extra_time_area()
        elif self.fig_type == FIG_TYPE_SPD_BAND:
            self.compute_speed_band()
        elif self.fig_type == FIG_TYPE_TT_CDF:
            # self.compute_tt_cdf()
            self.compute_speed_cdf()
        elif self.fig_type == FIG_TYPE_SPD_FREQ:
            self.compute_speed_freq()
        elif self.fig_type == FIG_DQ_WKDY:
            self.compute_dq_wkdy()
            # self.fig.canvas.mpl_connect('key_press_event', self.manual_ani_wkdy)
        elif self.fig_type == FIG_DQ_TOD:
            self.compute_dq_tod()
            # self.fig.canvas.mpl_connect('key_press_event', self.manual_ani_tod)
        elif self.fig_type == FIG_DQ_TMC:
            self.compute_dq_tmc()
            # self.fig.canvas.mpl_connect('key_press_event', self.manual_ani_tmc)
        elif self.fig_type == FIG_DQ_SP:
            self.compute_dq_sp()
            # self.fig.canvas.mpl_connect('key_press_event', self.manual_ani_sp)
        elif self.fig_type == FIG_TYPE_LOTTR_CORR_SUMM:
            self.compute_lottr_corr_summ()
        elif self.fig_type == FIG_TYPE_LOTTR_CORR_ALL:
            self.compute_lottr_corr_all()
        elif self.fig_type == FIG_TYPE_LOTTR_TMC:
            self.compute_lottr_tmc()

    def fire_animation(self):
        print('animation fired')
        # self.axes.cla()
        # self.axes.grid(animated=True)
        if self.fig_type == FIG_DQ_WKDY:
            # self.compute_dq_wkdy()
            self.manual_ani_wkdy(None)
        elif self.fig_type == FIG_DQ_TOD:
            # self.compute_dq_tod()
            self.manual_ani_tod(None)
        elif self.fig_type == FIG_DQ_TMC:
            # self.compute_dq_tmc(None)
            self.manual_ani_tmc(None)
        elif self.fig_type == FIG_DQ_SP:
            # self.compute_dq_sp()
            self.manual_ani_sp(None)
            # pass

    def animate_tod(self, i):
        # if i < self.frames:
        print(str(self.fig_type) + ' - ' + str(i))
        rs = [r for r in self.tod_bars]
        heights = [h * i / self.frames for h in self.panel.plot_dfs_dq[1].values]
        for h, r in zip(heights, rs):
            r.set_height(h)
        return rs
        # else:
        #     self.update_figure()
        #     return []

    def animate_wkdy(self, i):
        # if i < self.frames:
        print(str(self.fig_type) + ' - ' + str(i))
        rs = [r for r in self.wkdy_bars]
        heights = self.panel.plot_dfs_dq[0].values.reshape(self.panel.plot_dfs_dq[0].shape[0], )
        heights = [h * i / self.frames for h in heights]
        for h, r in zip(heights, rs):
            r.set_height(h)
        return rs
        # else:
        #     self.update_figure()
        #     return []

    def animate_tmc(self, i):
        # if i < self.frames:
        print(str(self.fig_type) + ' - ' + str(i))
        rs = [r for r in self.tmc_bars]
        heights = [h * i / self.frames for h in self.panel.plot_dfs_dq[2].values]
        for h, r in zip(heights, rs):
            r.set_height(h)
        return rs
        # else:
        #     self.update_figure()
        #     return []

    def animate_sp(self, i):
        if i < self.frames:
            print(str(self.fig_type) + ' - ' + str(i))
            rs1 = [r for r in self.sp_bars1]
            rs2 = [r for r in self.sp_bars2]
            heights1 = [h * i / self.frames for h in self.panel.plot_dfs_dq[3][0]]
            heights2 = [h * i / self.frames for h in self.panel.plot_dfs_dq[3][1]]
            for h, r in zip(heights1, rs1):
                r.set_height(h)
            for h, r in zip(heights2, rs2):
                r.set_height(h)
            return rs1 + rs2
        else:
            self.panel.update_figures()
            return []

    def update_figure(self):
        # print('updated')
        self.axes.cla()
        self.compute_initial_figure()

    def compute_trend_line(self):
        if self.show_am:
            tt_am_mean_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED]['mean']
            tt_am_pct5_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED]['percentile_5']
            tt_am_pct95_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED]['percentile_95']
            x = [el for el in range(len(tt_am_mean_dir1))]
            self.axes.plot(x, tt_am_mean_dir1, color='C0', linestyle='-', lw=2.0, label='AM-Mean')
            self.axes.plot(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.plot(x, tt_am_pct95_dir1, color='C0', linestyle='--', lw=1.0, label='AM-95th Pct')
        if self.show_pm:
            tt_pm_mean_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED + 'pm']['mean']
            tt_pm_pct5_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED + 'pm']['percentile_5']
            tt_pm_pct95_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED + 'pm']['percentile_95']
            x = [el for el in range(len(tt_pm_mean_dir1))]
            self.axes.plot(x, tt_pm_mean_dir1, color='C1', linestyle='-', lw=2.0, label='PM-Mean')
            self.axes.plot(x, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.plot(x, tt_pm_pct95_dir1, color='C1', linestyle='--', lw=1.0, label='PM-95th Pct')
        if self.show_mid:
            tt_md_mean_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED + 'mid']['mean']
            tt_md_pct5_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED + 'mid']['percentile_5']
            tt_md_pct95_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_SPEED + 'mid']['percentile_95']
            x = [el for el in range(len(tt_md_mean_dir1))]
            self.axes.plot(x, tt_md_mean_dir1, color='C2', linestyle='-', lw=2.0, label='Mid-Mean')
            self.axes.plot(x, tt_md_pct5_dir1, color='C2', linestyle='--', lw=1.0, label='Mid-5th Pct')
            self.axes.plot(x, tt_md_pct95_dir1, color='C2', linestyle='--', lw=1.0, label='Mid-95th Pct')

        self.axes.set_title(self.panel.peak_period_str + 'Speed Trends by Month'
                            + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_ylabel('Speed (mph)')
        self.axes.set_ylim(0, 85)
        self.axes.legend()
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_month))
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

        date_ranges = self.panel.project.get_date_ranges()
        if self.panel.show_before_after and date_ranges is not None and len(date_ranges) > 1:
            print('here')
            first_date = self.panel.project.database.get_first_date(as_datetime=True)
            first_date = QtCore.QDate(first_date.year, first_date.month, first_date.day)
            last_date = self.panel.project.database.get_last_date(as_datetime=True)
            last_date = QtCore.QDate(last_date.year, last_date.month, last_date.day)
            dr1 = date_ranges[0]
            dr2 = date_ranges[1]
            num_monts_p1 = compute_num_months(dr1[0], dr1[1]) - 1
            num_monts_p2 = compute_num_months(dr2[0], dr2[1]) - 1
            months_to_p1_start = compute_num_months(first_date, dr1[0]) - 1
            months_p1_end_to_p2_start = compute_num_months(dr1[1], dr2[0]) - 1
            print(months_to_p1_start)
            print(num_monts_p1)
            print(months_p1_end_to_p2_start)
            print(num_monts_p2)
            xr1 = (months_to_p1_start - 0.25, num_monts_p1 + 0.5)
            p2_start = months_to_p1_start + num_monts_p1 + months_p1_end_to_p2_start
            xr2 = (p2_start - 0.25, num_monts_p2 + 0.5)
            c1 = collections.BrokenBarHCollection([xr1, xr2], (0, 80),
                                                  edgecolors=['C0', 'navy'],
                                                  linewidths=[2.5, 2.5],
                                                  linestyles=['--', '--'],
                                                  facecolors=['none', 'none'],
                                                  # alpha=0.75
                                                  )
            self.axes.add_collection(c1)

        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='darkslategrey', alpha=0.75),
                                            color='white',
                                            annotation_clip=False)
        self.hover_ann.set_visible(False)
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover_datetime(event, self.f_x_to_month, label='mph'))
        self.fig.tight_layout()

    def export_data(self):
        if self.fig_type == FIG_TYPE_TT_TREND_LINE:
            self.export_trend_line()
        elif self.fig_type == FIG_TYPE_TT_TREND_BAR:
            self.export_trend_bar()
        elif self.fig_type == FIG_TYPE_SPD_BAND:
            self.export_speed_band()
        elif self.fig_type == FIG_TYPE_EXTRA_TIME:
            self.export_extra_time()
        elif self.fig_type == FIG_TYPE_TT_CDF:
            self.export_speed_cdf()
        elif self.fig_type == FIG_TYPE_SPD_FREQ:
            self.export_speed_freq()
        elif self.fig_type == FIG_DQ_WKDY:
            self.export_dq_wkdy()
        elif self.fig_type == FIG_DQ_TOD:
            self.export_dq_tod()
        elif self.fig_type == FIG_DQ_SP:
            self.export_dq_sp()
        elif self.fig_type == FIG_DQ_TMC:
            self.export_dq_tmc()
        elif self.fig_type == FIG_TYPE_SPD_HEAT_MAP_FACILITY:
            self.export_speed_tmc_heatmap()
        elif self.fig_type == FIG_TYPE_SPD_HEAT_MAP:
            self.export_speed_tod_heatmap()
        elif self.fig_type == FIG_TYPE_PCT_CONG_DAY:
            self.export_pct_cong_day()
        else:
            QtWidgets.QMessageBox.information(self, 'Function Not Implemented', 'Exporting the data for this chart is not yet supported.',
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            pass

    def export_trend_line(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            export_df = self.panel.plot_dfs[0][[DataHelper.Project.ID_DATA_SPEED,
                                                DataHelper.Project.ID_DATA_SPEED + 'pm',
                                                DataHelper.Project.ID_DATA_SPEED + 'mid']]
            export_df.rename(index=str, columns={DataHelper.Project.ID_DATA_SPEED: DataHelper.Project.ID_DATA_SPEED + 'am'}, inplace=True)
            if file_filter.count('h5') > 0:
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    export_df.to_csv(f_name)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_trend_line_deprecated(self):
        if self.show_am:
            tt_am_mean_dir1 = self.panel.plot_dfs[0]['mean']
            tt_am_pct5_dir1 = self.panel.plot_dfs[0]['percentile_5']
            tt_am_pct95_dir1 = self.panel.plot_dfs[0]['percentile_95']
            x = [el for el in range(len(tt_am_mean_dir1))]
            self.axes.plot(x, tt_am_mean_dir1, color='C0', linestyle='-', lw=2.0, label='AM-Mean')
            self.axes.plot(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.plot(x, tt_am_pct95_dir1, color='C0', linestyle='--', lw=1.0, label='AM-95th Pct')
        if self.show_pm:
            tt_pm_mean_dir1 = self.panel.plot_dfs[0]['meanpm']
            tt_pm_pct5_dir1 = self.panel.plot_dfs[0]['percentile_5pm']
            tt_pm_pct95_dir1 = self.panel.plot_dfs[0]['percentile_95pm']
            x = [el for el in range(len(tt_pm_mean_dir1))]
            self.axes.plot(x, tt_pm_mean_dir1, color='C1', linestyle='-', lw=2.0, label='PM-Mean')
            self.axes.plot(x, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.plot(x, tt_pm_pct95_dir1, color='C1', linestyle='--', lw=1.0, label='PM-95th Pct')
        if self.show_mid:
            tt_md_mean_dir1 = self.panel.plot_dfs[0]['meanmid']
            tt_md_pct5_dir1 = self.panel.plot_dfs[0]['percentile_5mid']
            tt_md_pct95_dir1 = self.panel.plot_dfs[0]['percentile_95mid']
            x = [el for el in range(len(tt_md_mean_dir1))]
            self.axes.plot(x, tt_md_mean_dir1, color='C2', linestyle='-', lw=2.0, label='Mid-Mean')
            self.axes.plot(x, tt_md_pct5_dir1, color='C2', linestyle='--', lw=1.0, label='Mid-5th Pct')
            self.axes.plot(x, tt_md_pct95_dir1, color='C2', linestyle='--', lw=1.0, label='Mid-95th Pct')

        # self.axes.set_title(self.panel.peak_period_str + 'Travel Time Trends by Month'
        #                     + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.set_title(self.panel.peak_period_str + 'Speed Trends by Month'
                            + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        # self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.set_ylabel('Speed (mph)')
        self.axes.legend()
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_month))
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='darkslategrey', alpha=0.75),
                                            color='white',
                                            annotation_clip=False)
        self.hover_ann.set_visible(False)
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover_datetime(event, self.f_x_to_month))
        self.fig.tight_layout()

    def compute_trend_bar(self):
        width = 0.35
        y_max = 0
        if self.show_am:
            tt_am_mean_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_TT]['mean']
            tt_am_pct95_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_TT]['percentile_95']
            x = [el for el in range(len(tt_am_mean_dir1))]
            self.axes.bar(x, tt_am_mean_dir1, width, color='C0', label='AM-Mean')
            self.axes.bar(x, [tt_am_pct95_dir1[i] - tt_am_mean_dir1[i] for i in range(len(tt_am_mean_dir1))], width, bottom=tt_am_mean_dir1,
                          color='#aec7e8',
                          label='AM-95th Pct')
            y_max = max(y_max, max(tt_am_pct95_dir1))
        if self.show_pm:
            tt_pm_mean_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_TT + 'pm']['mean']
            tt_pm_pct95_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_TT + 'pm']['percentile_95']
            x = [el for el in range(len(tt_pm_mean_dir1))]
            offset = 0
            if self.show_am:
                offset += width
            self.axes.bar([el + offset for el in x], tt_pm_mean_dir1, width, color='C1', label='PM-Mean')
            self.axes.bar([el + offset for el in x], [tt_pm_pct95_dir1[i] - tt_pm_mean_dir1[i] for i in range(len(tt_pm_mean_dir1))], width,
                          bottom=tt_pm_mean_dir1, color='#ffbb78', label='PM-95th Pct')
            y_max = max(y_max, max(tt_pm_pct95_dir1))
        if self.show_mid:
            tt_md_mean_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_TT + 'mid']['mean']
            tt_md_pct95_dir1 = self.panel.plot_dfs[0][DataHelper.Project.ID_DATA_TT + 'mid']['percentile_95']
            x = [el for el in range(len(tt_md_mean_dir1))]
            offset = 0
            if self.show_am:
                offset += width
            if self.show_pm:
                offset += width
            self.axes.bar([el + offset for el in x], tt_md_mean_dir1, width, color='C2', label='Mid-Mean')
            self.axes.bar([el + offset for el in x], [tt_md_pct95_dir1[i] - tt_md_mean_dir1[i] for i in range(len(tt_md_mean_dir1))], width,
                          bottom=tt_md_mean_dir1, color='#98df8a', label='Mid-95th Pct')
            y_max = max(y_max, max(tt_md_pct95_dir1))

        self.axes.set_title(self.panel.peak_period_str + 'Travel Time Trends by Month'
                            + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_ylabel('Travel Time (Minutes)')
        if not self.panel.plot_dfs[0].empty:
            self.axes.legend()
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_month))

        date_ranges = self.panel.project.get_date_ranges()
        if self.panel.show_before_after and date_ranges is not None and len(date_ranges) > 1:
            first_date = self.panel.project.database.get_first_date(as_datetime=True)
            first_date = QtCore.QDate(first_date.year, first_date.month, first_date.day)
            last_date = self.panel.project.database.get_last_date(as_datetime=True)
            last_date = QtCore.QDate(last_date.year, last_date.month, last_date.day)
            dr1 = date_ranges[0]
            dr2 = date_ranges[1]
            num_monts_p1 = compute_num_months(dr1[0], dr1[1]) - 1
            num_monts_p2 = compute_num_months(dr2[0], dr2[1]) - 1
            months_to_p1_start = compute_num_months(first_date, dr1[0]) - 1
            months_p1_end_to_p2_start = compute_num_months(dr1[1], dr2[0]) - 1
            xr1 = (months_to_p1_start - 0.25, num_monts_p1 + 0.825)
            p2_start = months_to_p1_start + num_monts_p1 + months_p1_end_to_p2_start
            xr2 = (p2_start - 0.25, num_monts_p2 + 0.825)
            c1 = collections.BrokenBarHCollection([xr1, xr2], (0, y_max * 1.01),
                                                  edgecolors=['C0', 'navy'],
                                                  linewidths=[2.5, 2.5],
                                                  linestyles=['--', '--'],
                                                  facecolors=['none', 'none'],
                                                  # alpha=0.75
                                                  )
            self.axes.add_collection(c1)

        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='darkslategrey', alpha=0.75),
                                            color='white',
                                            annotation_clip=False)
        self.hover_ann.set_visible(False)
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover_datetime(event, self.f_x_to_month))
        self.fig.tight_layout()

    def export_trend_bar(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            export_df = self.panel.plot_dfs[0][[DataHelper.Project.ID_DATA_TT,
                                                DataHelper.Project.ID_DATA_TT + 'pm',
                                                DataHelper.Project.ID_DATA_TT + 'mid']]
            export_df.rename(index=str, columns={DataHelper.Project.ID_DATA_TT: DataHelper.Project.ID_DATA_TT + 'am'}, inplace=True)
            if file_filter.count('h5') > 0:
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    export_df.to_csv(f_name)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_trend_bar_deprecated(self):
        width = 0.35
        if self.show_am:
            tt_am_mean_dir1 = self.panel.plot_dfs[0]['mean']
            # tt_am_pct5_dir1 = self.panel.plot_dfs[0]['percentile_5']
            tt_am_pct95_dir1 = self.panel.plot_dfs[0]['percentile_95']
            x = [el for el in range(len(tt_am_mean_dir1))]
            self.axes.bar(x, tt_am_mean_dir1, width, color='C0', label='AM-Mean')
            # ax3.bar(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.bar(x, [tt_am_pct95_dir1[i] - tt_am_mean_dir1[i] for i in range(len(tt_am_mean_dir1))], width, bottom=tt_am_mean_dir1,
                          color='#aec7e8',
                          label='AM-95th Pct')
        if self.show_pm:
            tt_pm_mean_dir1 = self.panel.plot_dfs[0]['meanpm']
            # tt_pm_pct5_dir1 = self.panel.plot_dfs[0]['percentile_5pm']
            tt_pm_pct95_dir1 = self.panel.plot_dfs[0]['percentile_95pm']
            x = [el for el in range(len(tt_pm_mean_dir1))]
            offset = 0
            if self.show_am:
                offset += width
            self.axes.bar([el + offset for el in x], tt_pm_mean_dir1, width, color='C1', label='PM-Mean')
            # ax1.bar(x + width, tt_pm_pct5_dir1, color='C1', linestyle='--', lw=1.0, label='PM-5th Pct')
            self.axes.bar([el + offset for el in x], [tt_pm_pct95_dir1[i] - tt_pm_mean_dir1[i] for i in range(len(tt_pm_mean_dir1))], width,
                          bottom=tt_pm_mean_dir1, color='#ffbb78', label='PM-95th Pct')
        if self.show_mid:
            tt_md_mean_dir1 = self.panel.plot_dfs[0]['meanmid']
            # tt_md_pct5_dir1 = self.panel.plot_dfs[0]['percentile_5mid']
            tt_md_pct95_dir1 = self.panel.plot_dfs[0]['percentile_95mid']
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

        self.axes.set_title(self.panel.peak_period_str + 'Travel Time Trends by Month'
                            + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_ylabel('Travel Time (Minutes)')
        if not self.panel.plot_dfs[0].empty:
            self.axes.legend()
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_month))
        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='darkslategrey', alpha=0.75),
                                            color='white',
                                            annotation_clip=False)
        self.hover_ann.set_visible(False)
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover_datetime(event, self.f_x_to_month))
        self.fig.tight_layout()

    def compute_pct_cong_day(self):
        BIN0 = self.panel.options.speed_bins[0]
        BIN1 = self.panel.options.speed_bins[1]
        BIN2 = self.panel.options.speed_bins[2]
        BIN3 = self.panel.options.speed_bins[3]
        BIN4 = self.panel.options.speed_bins[4]
        bin_limits = [BIN0, BIN1, BIN2, BIN3, BIN4]
        bin_labels = [str(bin_limits[i]) + 'mph-' + str(bin_limits[i + 1]) + 'mph' for i in range(len(bin_limits) - 1)]
        # bin_labels.insert(0, '<' + str(BIN1) + 'mph')
        bin_labels.append(str(BIN4) + '+')
        cl = self.panel.options.speed_bin_colors
        bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
        data = self.panel.plot_dfs[1]
        x_study_period = [el for el in range(len(data[bin_list[0]]))]

        self.axes.stackplot(x_study_period,
                            data[bin_list[0]],
                            data[bin_list[1]],
                            data[bin_list[2]],
                            data[bin_list[3]],
                            data[bin_list[4]],
                            labels=bin_labels,
                            colors=cl)
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_day))
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=0))
        # self.axes.set_xlabel('Date')
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.2%}'.format(y)))
        self.axes.set_ylabel('Percent Congested')
        self.axes.set_title('Percent Congested over Time: ' + convert_xval_to_time(self.panel.ap_start, None, self.panel.project.data_res)
                            + '-' + convert_xval_to_time(self.panel.ap_end, None, self.panel.project.data_res)
                            + '\n' + self.panel.selected_tmc_name + ' (' + '{:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.legend()

        date_ranges = self.panel.project.get_date_ranges()
        if not self.panel.is_stack and self.panel.show_before_after and date_ranges is not None and len(date_ranges) > 1:
            first_date = self.panel.project.database.get_first_date(as_datetime=True)
            first_date = QtCore.QDate(first_date.year, first_date.month, first_date.day)
            last_date = self.panel.project.database.get_last_date(as_datetime=True)
            last_date = QtCore.QDate(last_date.year, last_date.month, last_date.day)
            dr1 = date_ranges[0]
            dr2 = date_ranges[1]
            num_days_p1 = dr1[0].daysTo(dr1[1]) + 1
            num_days_p2 = dr2[0].daysTo(dr2[1]) + 1
            days_to_p1_start = first_date.daysTo(dr1[0])
            days_p1_end_to_p2_start = dr1[1].daysTo(dr2[0])
            # days_p2_end_to_data_end = dr2[1].daysTo(last_date)
            xr1 = (days_to_p1_start, num_days_p1)
            p2_start = days_to_p1_start + num_days_p1 + days_p1_end_to_p2_start - 1
            xr2 = (p2_start, num_days_p2 - 1)
            c1 = collections.BrokenBarHCollection([xr1, xr2], (0, 1),
                                                  edgecolors=['C0', 'navy'],
                                                  linewidths=[2.5, 2.5],
                                                  linestyles=['--', '--'],
                                                  facecolors=['none', 'none'],
                                                  # alpha=0.75
                                                  )
            self.axes.add_collection(c1)

        self.fig.tight_layout()

    def export_pct_cong_day(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            BIN0 = self.panel.options.speed_bins[0]
            BIN1 = self.panel.options.speed_bins[1]
            BIN2 = self.panel.options.speed_bins[2]
            BIN3 = self.panel.options.speed_bins[3]
            BIN4 = self.panel.options.speed_bins[4]
            bin_limits = [BIN0, BIN1, BIN2, BIN3, BIN4]
            bin_labels = [str(bin_limits[i]) + 'mph-' + str(bin_limits[i + 1]) + 'mph' for i in range(len(bin_limits) - 1)]
            # bin_labels.insert(0, '<' + str(BIN1) + 'mph')
            bin_labels.append(str(BIN4) + '+')
            export_df = self.panel.plot_dfs[1]
            export_df.rename(index=str, columns={'bin1': bin_labels[0],
                                                 'bin2': bin_labels[1],
                                                 'bin3': bin_labels[2],
                                                 'bin4': bin_labels[3],
                                                 'bin5': bin_labels[4]},
                             inplace=True)
            if file_filter.count('h5') > 0:
                # self.panel.plot_dfs[1].to_hdf(f_name, 'table')
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    # self.panel.plot_dfs[1].to_csv(f_name, index=False)
                    export_df.reset_index(level=[0, 1, 2], inplace=True)
                    export_df.to_csv(f_name, index=False)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_pct_cong_tmc(self):
        BIN0 = self.panel.options.speed_bins[0]
        BIN1 = self.panel.options.speed_bins[1]
        BIN2 = self.panel.options.speed_bins[2]
        BIN3 = self.panel.options.speed_bins[3]
        BIN4 = self.panel.options.speed_bins[4]
        bin_limits = [BIN0, BIN1, BIN2, BIN3, BIN4]
        bin_labels = [str(bin_limits[i]) + 'mph-' + str(bin_limits[i + 1]) + 'mph' for i in range(len(bin_limits) - 1)]
        # bin_labels.insert(0, '<' + str(BIN1) + 'mph')
        bin_labels.append(str(BIN4) + '+')
        cl = self.panel.options.speed_bin_colors
        bin_list = ['bin1', 'bin2', 'bin3', 'bin4', 'bin5']
        data = self.panel.plot_dfs[2]
        x_study_period = [el for el in range(len(data[bin_list[0]]))]
        self.axes.stackplot(x_study_period,
                            data[bin_list[0]],
                            data[bin_list[1]],
                            data[bin_list[2]],
                            data[bin_list[3]],
                            data[bin_list[4]],
                            labels=bin_labels,
                            colors=cl)
        # self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_tmc))
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_mile))
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=0))
        self.axes.set_xlabel('Milepost')
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.2%}'.format(y)))
        self.axes.set_ylabel('Percent Congested')
        self.axes.set_title('Average Hourly Congestion by TMC')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.legend()
        self.fig.tight_layout()

    def compute_speed_heatmap(self):
        imshow_data = self.panel.plot_dfs[3]
        if imshow_data != []:
            y_argmax = imshow_data.shape[0]
        else:
            y_argmax = 0
            QtWidgets.QMessageBox.warning(self.panel, 'No Data Available', 'The selected TMC does not have any data.')

        im = self.axes.imshow(imshow_data, cmap='RdYlGn', aspect='auto',
                                      vmin=self.panel.project.min_speed,
                                      vmax=self.panel.project.max_speed)
        if self.color_bar1 is not None:
            self.color_bar1.remove()
        self.color_bar1 = self.fig.colorbar(im, ax=self.axes, shrink=0.8, use_gridspec=True)
        self.color_bar1.set_label('Speed (mph)')
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_day))
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.f_y_to_time))
        self.axes.set_title('Daily Speed Heatmap for ' + self.panel.selected_tmc_name + ' (' + '{:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        date_ranges = self.panel.project.get_date_ranges()
        if not self.panel.is_stack and self.panel.show_before_after and date_ranges is not None and len(date_ranges) > 1:
            first_date = self.panel.project.database.get_first_date(as_datetime=True)
            first_date = QtCore.QDate(first_date.year, first_date.month, first_date.day)
            last_date = self.panel.project.database.get_last_date(as_datetime=True)
            last_date = QtCore.QDate(last_date.year, last_date.month, last_date.day)
            dr1 = date_ranges[0]
            dr2 = date_ranges[1]
            num_days_p1 = dr1[0].daysTo(dr1[1]) + 1
            num_days_p2 = dr2[0].daysTo(dr2[1]) + 1
            days_to_p1_start = first_date.daysTo(dr1[0])
            days_p1_end_to_p2_start = dr1[1].daysTo(dr2[0])
            # days_p2_end_to_data_end = dr2[1].daysTo(last_date)
            xr1 = (days_to_p1_start, num_days_p1)
            p2_start = days_to_p1_start + num_days_p1 + days_p1_end_to_p2_start - 1
            xr2 = (p2_start, num_days_p2)
            c1 = collections.BrokenBarHCollection([xr1, xr2], (0, y_argmax),
                                                  edgecolors=['C0', 'navy'],
                                                  linewidths=[2.5, 2.5],
                                                  linestyles=['--', '--'],
                                                  facecolors=['none', 'none'],
                                                  # alpha=0.75
                                                  )
            self.axes.add_collection(c1)

        self.fig.tight_layout()

    def export_speed_tod_heatmap(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            imshow_data = self.panel.plot_dfs[3]
            num_aps, num_days = imshow_data.shape
            if file_filter.count('h5') > 0:
                QtWidgets.QMessageBox.information(self, 'Function Not Implemented', 'Exporting this chart to the HDF5 format is not yet supported.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                return
            else:
                try:
                    wf = open(f_name, 'w')
                    wf.write('Daily Speed Heatmap for ' + self.panel.selected_tmc_name + ' (' + '{:1.2f} mi'.format(self.panel.selected_tmc_len) + ')\n')
                    wf.write('Time of Day/Date')
                    for di in range(num_days):
                        wf.write(',' + self.f_x_to_day_1l(di, None))
                    wf.write('\n')
                    for ti in range(num_aps):
                        wf.write(self.f_y_to_time(ti, None))
                        for di in range(num_days):
                            wf.write(', {:1.2f}'.format(imshow_data[ti][di]))
                        wf.write('\n')
                    wf.close()
                    QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                                      'Time of Day Heatmap Matrix successfully written to CSV file.',
                                                      QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_speed_tmc_heatmap(self):
        peak_idx = 4
        if self.show_am:
            hour_str = convert_xval_to_time(self.panel.ap_start1, None, self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.ap_end1,
                                                                                                                                  None,
                                                                                                                                  self.panel.project.data_res)
            imshow_data = self.panel.plot_dfs[4]
        elif self.show_mid:
            hour_str = convert_xval_to_time(self.panel.ap_start2, None, self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.ap_end2,
                                                                                                                                  None,
                                                                                                                                  self.panel.project.data_res)
            imshow_data = self.panel.plot_dfs[5]
            peak_idx = 5
        else:
            hour_str = convert_xval_to_time(self.panel.ap_start3, None, self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.ap_end3,
                                                                                                                                  None,
                                                                                                                                  self.panel.project.data_res)
            imshow_data = self.panel.plot_dfs[6]
            peak_idx = 6
        num_tmc, num_days = imshow_data.shape
        self.tmc_ext = num_days / 5
        cb_shrink = 0.8
        # im = self.axes.imshow(imshow_data, extent=[0, num_days, 0, self.tmc_ext], cmap='RdYlGn')
        last_val = 0
        row_idx = 0
        tmc = self.panel.project.get_tmc()
        if self.panel.is_scaled:
            for row in imshow_data:
                curr_tmc_len = tmc[DataHelper.Project.ID_TMC_LEN][row_idx]
                im = self.axes.imshow(row.reshape((1, num_days)),
                                      extent=[0, num_days, last_val, last_val + curr_tmc_len],
                                      cmap='RdYlGn', aspect='auto',
                                      vmin=self.panel.project.min_speed,
                                      vmax=self.panel.project.max_speed
                                      )
                last_val += curr_tmc_len
                row_idx += 1
            y_max = tmc[DataHelper.Project.ID_TMC_LEN].sum()

            self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:1.1f} mi'.format(y)))
            self.axes.set_ylabel('Milepost')
        else:
            im = self.axes.imshow(imshow_data,
                                  # extent=[0, num_days, 0, self.tmc_ext],
                                  cmap='RdYlGn', aspect='auto',
                                  vmin=self.panel.project.min_speed,
                                  vmax=self.panel.project.max_speed
                                  )
            # f_tmc_label2 = lambda x, pos: convert_extent_to_mile(x, pos, self.panel.facility_len, self.tmc_ext)
            # self.axes.yaxis.set_major_formatter(FuncFormatter(f_tmc_label2))
            y_max = num_tmc - 1
            self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '#{:1.0f}'.format(y + 1)))
            self.axes.set_ylabel('TMC #')

        self.axes.set_ylim(0, y_max)

        if self.color_bar2 is not None:
            self.color_bar2.remove()
        self.color_bar2 = self.fig.colorbar(im, ax=self.axes, shrink=cb_shrink, use_gridspec=True)
        self.color_bar2.set_label('Speed (mph)')
        # self.color_bar2.set_clim(35, 65)
        if not self.panel.is_stack:
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_day))
        else:
            self.axes.xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.1%}'.format(x / num_days)))
            self.axes.set_xlabel('Percent Congested')

        self.axes.set_title(self.panel.project.get_name() + ' Spatial Speed Heatmap: ' + hour_str)
        # self.fig.tight_layout()
        # tmc_list = self.panel.project.get_tmc(as_list=True).tolist()
        # tmc_list = tmc[DataHelper.Project.ID_TMC_CODE].tolist()
        # tmc_list.reverse()
        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='darkslategrey', alpha=0.75),
                                            color='white',
                                            annotation_clip=False)
        self.hover_ann.set_visible(False)
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover_tmc(event, tmc, peak_idx))

        date_ranges = self.panel.project.get_date_ranges()
        if not self.panel.is_stack and self.panel.show_before_after and date_ranges is not None and len(date_ranges) > 1:
            first_date = self.panel.project.database.get_first_date(as_datetime=True)
            first_date = QtCore.QDate(first_date.year, first_date.month, first_date.day)
            last_date = self.panel.project.database.get_last_date(as_datetime=True)
            last_date = QtCore.QDate(last_date.year, last_date.month, last_date.day)
            dr1 = date_ranges[0]
            dr2 = date_ranges[1]
            num_days_p1 = dr1[0].daysTo(dr1[1]) + 1
            num_days_p2 = dr2[0].daysTo(dr2[1]) + 1
            days_to_p1_start = first_date.daysTo(dr1[0])
            days_p1_end_to_p2_start = dr1[1].daysTo(dr2[0])
            # days_p2_end_to_data_end = dr2[1].daysTo(last_date)
            xr1 = (days_to_p1_start, num_days_p1)
            p2_start = days_to_p1_start + num_days_p1 + days_p1_end_to_p2_start - 1
            xr2 = (p2_start, num_days_p2)
            c1 = collections.BrokenBarHCollection([xr1, xr2], (0, y_max),
                                                  edgecolors=['C0', 'navy'],
                                                  linewidths=[2.5, 2.5],
                                                  linestyles=['--', '--'],
                                                  facecolors=['none', 'none'],
                                                  # alpha=0.75
                                                  )
            self.axes.add_collection(c1)

        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        # if not self.bbox_adjusted:
        box = self.axes.get_position()
        self.axes.set_position([box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95])
            # self.bbox_adjusted = True

    def export_speed_tmc_heatmap(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            if self.show_am:
                hour_str = convert_xval_to_time(self.panel.ap_start1, None, self.panel.project.data_res) + '-' + convert_xval_to_time(
                    self.panel.ap_end1, None, self.panel.project.data_res)
                imshow_data = self.panel.plot_dfs[4]
            elif self.show_mid:
                hour_str = convert_xval_to_time(self.panel.ap_start2, None, self.panel.project.data_res) + '-' + convert_xval_to_time(
                    self.panel.ap_end2, None, self.panel.project.data_res)
                imshow_data = self.panel.plot_dfs[5]
            else:
                hour_str = convert_xval_to_time(self.panel.ap_start3, None, self.panel.project.data_res) + '-' + convert_xval_to_time(
                    self.panel.ap_end3, None, self.panel.project.data_res)
                imshow_data = self.panel.plot_dfs[6]
            num_tmc, num_days = imshow_data.shape
            if file_filter.count('h5') > 0:
                QtWidgets.QMessageBox.information(self, 'Function Not Implemented', 'Exporting this chart to the HDF5 format is not yet supported.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                pass
            else:
                try:
                    wf = open(f_name, 'w')
                    wf.write('Spatial Heatmap Matrix for "' + self.panel.project.get_name() + '" for ' + hour_str + '\n')
                    wf.write('TMC/Day')
                    for di in range(num_days):
                        wf.write(',' + self.f_x_to_day_1l(di, None))
                    wf.write('\n')
                    tmc = self.panel.project.get_tmc()
                    for ti in range(num_tmc - 1, -1, -1):
                        wf.write(tmc[DataHelper.Project.ID_TMC_CODE][ti])
                        for di in range(num_days):
                            wf.write(', {:1.2f}'.format(imshow_data[ti][di]))
                        wf.write('\n')
                    wf.close()
                    QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                                      'Spatial Heatmap Matrix successfully written to CSV file.',
                                                      QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_extra_time_area(self):
        day_type = self.panel.day_select
        offset = 9
        # tmc_list = self.panel.project.get_tmc(as_list=True)
        tmc1 = self.panel.selected_tmc_name
        data_before = self.panel.plot_dfs[day_type]
        data_after = self.panel.plot_dfs[day_type + offset]

        if self.region == AFTER:
            data1 = data_after
            data2 = data_before
        else:
            data1 = data_before
            data2 = data_after

        index = data1['mean'][tmc1].index
        self.axes.stackplot(index,
                            data1['mean'][tmc1].values,
                            data1['extra_time'][tmc1].values,
                            labels=['After-Average', 'After-95th Pct'],
                            colors=[TT_BLUE, TT_RED])
        if self.region2 != NONE:
            index2 = data2['mean'][tmc1].index
            self.axes.plot(index2, data2['mean'][tmc1].values,
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(index2, data2['percentile_95'][tmc1].values,
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Pct')
        title_str = 'Extra Time: ' + self.panel.project.get_name()
        title_str = title_str + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')'
        title_str = title_str + '\n'
        if self.region2 != 0:
            title_str = title_str + 'Before/After: ' + self.panel.period1 + ' vs ' + self.panel.period2
        elif self.region == BEFORE:
            title_str = title_str + 'Period 1: ' + self.panel.period1
        else:
            title_str = title_str + 'Period 2: ' + self.panel.period2
        self.axes.set_title(title_str)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_y_to_time))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.fig.tight_layout()

    def export_extra_time(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            day_type = self.panel.day_select
            offset = 9
            # tmc_list = self.panel.project.get_tmc(as_list=True)
            tmc1 = self.panel.selected_tmc_name
            data_before = self.panel.plot_dfs[day_type]
            data_after = self.panel.plot_dfs[day_type + offset]
            # print(data_before)
            export_df = data_before.reset_index(level=[0, 1])
            export_df.rename(index=str, columns={'mean': 'mean_before',
                                                 'percentile_95': 'percentile_95_before',
                                                 'percentile_5': 'percentile_5_before',
                                                 'extra_time': 'extra_time_before'},
                             inplace=True)
            dfa = data_after.reset_index(level=[0, 1])
            export_df['mean_after'] = dfa['mean']
            export_df['percentile_95_after'] = dfa['percentile_95']
            export_df['percentile_5_after'] = dfa['percentile_5']
            export_df['extra_time_after'] = dfa['extra_time']
            export_df['Time'] = export_df['AP'].apply(lambda ap: time((ap * 5) // 60, (ap * 5) % 60, 0).strftime('%I:%M%p'))
            export_df = export_df[['tmc_code', 'AP', 'Time',
                                   'percentile_5_before', 'mean_before', 'percentile_95_before', 'extra_time_before',
                                   'percentile_5_after', 'mean_after', 'percentile_95_after', 'extra_time_after']]
            dfa_export = dfa.rename(index=str, columns={'mean': 'mean_before',
                                                 'percentile_95': 'percentile_95_after',
                                                 'percentile_5': 'percentile_5_after',
                                                 'extra_time': 'extra_time_after'})
            if file_filter.count('h5') > 0:
                # data_before.to_hdf(f_name, 'before')
                # data_after.to_hdf(f_name, 'after')
                export_df.to_hdf(f_name, 'table')
                dfa_export.to_hdf(f_name, 'after')
            else:
                try:
                    export_df.to_csv(f_name, index=False)
                    pass
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_speed_band(self):
        day_type = self.panel.day_select
        offset = 9
        # tmc_list = self.panel.project.get_tmc(as_list=True)
        tmc1 = self.panel.selected_tmc_name
        data_before = self.panel.plot_dfs2[day_type]
        data_after = self.panel.plot_dfs2[day_type + offset]

        if self.region == AFTER:
            data1 = data_after
            data2 = data_before
        else:
            data1 = data_before
            data2 = data_after

        index = data1['mean'][tmc1].index
        self.axes.fill_between(index,
                               data1['percentile_5'][tmc1].values,
                               data1['mean'][tmc1].values,
                               color=SB_BLUE)
        self.axes.fill_between(index,
                               data1['mean'][tmc1].values,
                               data1['percentile_95'][tmc1].values,
                               color=SB_BLUE)
        self.axes.plot(index, data1['percentile_5'][tmc1].values, color=SB_BLUE, label='5th Percentile')
        self.axes.plot(index, data1['mean'][tmc1].values, color=SB_RED, label='Average')
        self.axes.plot(index, data1['percentile_95'][tmc1].values, color=SB_BLUE, label='95th Percentile')
        if self.region2 != NONE:
            index2 = data2['mean'][tmc1].index
            self.axes.plot(index2, data2['mean'][tmc1].values,
                           color=TT_RED_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-Average')
            self.axes.plot(index2, data2['percentile_5'][tmc1].values,
                           color=TT_BLUE_BEFORE,
                           linestyle='--',
                           lw=BEFORE_LW,
                           label='Before-95th Pct')
        title_str = 'Speed Band: ' + self.panel.project.get_name()
        title_str = title_str + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')'
        title_str = title_str + '\n'
        if self.region2 >= 0:
            title_str = title_str + 'Before/After: ' + self.panel.period1 + ' vs ' + self.panel.period2
        elif self.region == BEFORE:
            title_str = title_str + 'Period 1: ' + self.panel.period1
        else:
            title_str = title_str + 'Period 2: ' + self.panel.period2
        self.axes.set_title(title_str)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Speed (mph)')
        self.axes.set_ylim(0, 85)
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_y_to_time))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.fig.tight_layout()

    def export_speed_band(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        day_type = self.panel.day_select
        offset = 9
        tmc1 = self.panel.selected_tmc_name
        data_before = self.panel.plot_dfs2[day_type]
        data_after = self.panel.plot_dfs2[day_type + offset]
        export_df = DataFrame()
        export_df['mean_before'] = data_before['mean'][tmc1]
        export_df['pct95_before'] = data_before['percentile_95'][tmc1]
        export_df['pct5_before'] = data_before['percentile_5'][tmc1]
        export_df['mean_after'] = data_after['mean'][tmc1]
        export_df['pct95_after'] = data_after['percentile_95'][tmc1]
        export_df['pct5_after'] = data_after['percentile_5'][tmc1]
        if f_name:
            # export_df.to_csv(f_name)
            if file_filter.count('h5') > 0:
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    export_df.to_csv(f_name, index=False)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_tt_cdf(self):
        day_type = self.panel.day_select
        offset = 9
        # tmc_list = self.panel.project.get_tmc(as_list=True)
        tmc1 = self.panel.selected_tmc_name
        data_before = self.panel.plot_dfs3[day_type]
        data_after = self.panel.plot_dfs3[day_type + offset]

        if self.region == AFTER:
            data1 = data_after
            data2 = data_before
        else:
            data1 = data_before
            data2 = data_after

        # Before Data  # if self.region2 != NONE:
        max_y2 = len(data2[DataHelper.Project.ID_DATA_TT][tmc1])
        self.axes.plot(data2[DataHelper.Project.ID_DATA_TT][tmc1].values, [el / max_y2 for el in range(max_y2)], color=TT_BLUE, label='Before')
        # After Data
        max_y = len(data1[DataHelper.Project.ID_DATA_TT][tmc1])
        self.axes.plot(data1[DataHelper.Project.ID_DATA_TT][tmc1].values, [el / max_y for el in range(max_y)], color=SB_RED, label='After')

        title_str = 'Travel Time Distribution: ' + self.panel.project.get_name()
        title_str = title_str + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')'
        title_str = title_str + '\n'
        if self.region2 != 0:
            title_str = title_str + 'Before/After: ' + self.panel.period1 + ' vs ' + self.panel.period2
        elif self.region == BEFORE:
            title_str = title_str + 'Period 1: ' + self.panel.period1
        else:
            title_str = title_str + 'Period 2: ' + self.panel.period2
        self.axes.set_title(title_str)
        self.axes.set_xlabel('Travel Time Minutes')
        self.axes.set_ylabel('Distribution')
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.fig.tight_layout()

    def compute_speed_cdf(self):
        day_type = self.panel.day_select
        offset = 9
        tmc1 = self.panel.selected_tmc_name
        if self.panel.selected_peak == PEAK_24HR:
            color_str = 'C3'
            title_preamble = '24 Hour '
            data_before = self.panel.plot_dfs3[day_type]
            data_after = self.panel.plot_dfs3[day_type + offset]
        elif self.panel.selected_peak == PEAK_AM:
            color_str = 'C0'
            title_preamble = 'AM Peak (' + convert_xval_to_time(self.panel.am_ap_start, None,
                                                                self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.am_ap_end, None,
                                                                                                                          self.panel.project.data_res) + ') '
            data_before = self.panel.plot_dfs5[day_type]
            data_after = self.panel.plot_dfs5[day_type + offset]
        elif self.panel.selected_peak == PEAK_MID:
            color_str = 'C2'
            title_preamble = 'Midday (' + convert_xval_to_time(self.panel.md_ap_start, None,
                                                               self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.md_ap_end, None,
                                                                                                                         self.panel.project.data_res) + ') '
            data_before = self.panel.plot_dfs5[18 + day_type]
            data_after = self.panel.plot_dfs5[18 + day_type + offset]
        else:
            color_str = 'C1'
            title_preamble = 'PM Peak (' + convert_xval_to_time(self.panel.pm_ap_start, None,
                                                                self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.pm_ap_end, None,
                                                                                                                          self.panel.project.data_res) + ') '
            data_before = self.panel.plot_dfs5[36 + day_type]
            data_after = self.panel.plot_dfs5[36 + day_type + offset]

        if self.region == AFTER:
            data1 = data_after
            data2 = data_before
        else:
            data1 = data_before
            data2 = data_after

        # Before Data  # if self.region2 != NONE:
        max_y2 = len(data2[DataHelper.Project.ID_DATA_SPEED][tmc1])
        self.axes.plot(data2[DataHelper.Project.ID_DATA_SPEED][tmc1].values, [el / max_y2 for el in range(max_y2)], color=color_str, label='Before',
                       ls='--')
        # After Data
        max_y = len(data1[DataHelper.Project.ID_DATA_SPEED][tmc1])
        self.axes.plot(data1[DataHelper.Project.ID_DATA_SPEED][tmc1].values, [el / max_y for el in range(max_y)], color=color_str, label='After')
        title_str = title_preamble + 'Speed Distribution: ' + self.panel.project.get_name()
        title_str = title_str + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')'
        title_str = title_str + '\n'
        if self.region2 != 0:
            title_str = title_str + 'Before/After: ' + self.panel.period1 + ' vs ' + self.panel.period2
        elif self.region == BEFORE:
            title_str = title_str + 'Period 1: ' + self.panel.period1
        else:
            title_str = title_str + 'Period 2: ' + self.panel.period2
        self.axes.set_title(title_str)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_xlabel('Speed (mph)')
        self.axes.set_ylabel('Distribution')
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        # self.fig.tight_layout()

    def export_speed_cdf(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            day_type = self.panel.day_select
            offset = 9
            tmc1 = self.panel.selected_tmc_name
            if self.panel.selected_peak == PEAK_24HR:
                data_before = self.panel.plot_dfs3[day_type]
                data_after = self.panel.plot_dfs3[day_type + offset]
            elif self.panel.selected_peak == PEAK_AM:
                data_before = self.panel.plot_dfs5[day_type]
                data_after = self.panel.plot_dfs5[day_type + offset]
            elif self.panel.selected_peak == PEAK_MID:
                data_before = self.panel.plot_dfs5[18 + day_type]
                data_after = self.panel.plot_dfs5[18 + day_type + offset]
            else:
                data_before = self.panel.plot_dfs5[36 + day_type]
                data_after = self.panel.plot_dfs5[36 + day_type + offset]
            data_before = data_before[data_before[DataHelper.Project.ID_DATA_TMC] == tmc1]
            data_after = data_after[data_after[DataHelper.Project.ID_DATA_TMC] == tmc1]
            export_dfb = data_before[[DataHelper.Project.ID_DATA_SPEED]].reset_index()[DataHelper.Project.ID_DATA_SPEED].to_frame()
            export_dfa = data_after[[DataHelper.Project.ID_DATA_SPEED]].reset_index()[DataHelper.Project.ID_DATA_SPEED].to_frame()
            export_df = DataFrame()
            if export_dfa.count()[0] > export_dfb.count()[0]:
                export_df[DataHelper.Project.ID_DATA_SPEED + '_after'] = export_dfa[DataHelper.Project.ID_DATA_SPEED]
                export_df[DataHelper.Project.ID_DATA_SPEED + '_before'] = export_dfb[DataHelper.Project.ID_DATA_SPEED]
            else:
                export_df[DataHelper.Project.ID_DATA_SPEED + '_before'] = export_dfb[DataHelper.Project.ID_DATA_SPEED]
                export_df[DataHelper.Project.ID_DATA_SPEED + '_after'] = export_dfa[DataHelper.Project.ID_DATA_SPEED]
            export_df[DataHelper.Project.ID_DATA_TMC] = tmc1
            export_df = export_df[[DataHelper.Project.ID_DATA_TMC,
                                   DataHelper.Project.ID_DATA_SPEED + '_before',
                                   DataHelper.Project.ID_DATA_SPEED + '_after']]
            if file_filter.count('h5') > 0:
                # data_before.to_hdf(f_name, 'before')
                # data_after.to_hdf(f_name, 'after')
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    export_df.to_csv(f_name, index=False)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_speed_freq(self):
        bin_extend = 10
        day_type = self.panel.day_select
        offset = 9
        # tmc_list = self.panel.project.get_tmc(as_list=True)
        tmc1 = self.panel.selected_tmc_name
        # data_before = self.panel.plot_dfs3[day_type]
        # data_after = self.panel.plot_dfs3[day_type + offset]
        if self.panel.selected_peak == PEAK_24HR:
            color_str = 'C3'
            title_preamble = '24 Hour '
            data_before = self.panel.plot_dfs3[day_type]
            data_after = self.panel.plot_dfs3[day_type + offset]
        elif self.panel.selected_peak == PEAK_AM:
            color_str = 'C0'
            title_preamble = 'AM Peak (' + convert_xval_to_time(self.panel.am_ap_start, None,
                                                                self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.am_ap_end, None,
                                                                                                                          self.panel.project.data_res) + ') '
            data_before = self.panel.plot_dfs5[day_type]
            data_after = self.panel.plot_dfs5[day_type + offset]
        elif self.panel.selected_peak == PEAK_MID:
            color_str = 'C2'
            title_preamble = 'Midday (' + convert_xval_to_time(self.panel.md_ap_start, None,
                                                               self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.md_ap_end, None,
                                                                                                                         self.panel.project.data_res) + ') '
            data_before = self.panel.plot_dfs5[18 + day_type]
            data_after = self.panel.plot_dfs5[18 + day_type + offset]
        else:
            color_str = 'C1'
            title_preamble = 'PM Peak (' + convert_xval_to_time(self.panel.pm_ap_start, None,
                                                                self.panel.project.data_res) + '-' + convert_xval_to_time(self.panel.pm_ap_end, None,
                                                                                                                          self.panel.project.data_res) + ') '
            data_before = self.panel.plot_dfs5[36 + day_type]
            data_after = self.panel.plot_dfs5[36 + day_type + offset]

        if self.region == AFTER:
            data1 = data_after
            data2 = data_before
        else:
            data1 = data_before
            data2 = data_after
        # Before Data # if self.region2 != NONE:
        max_speed2 = int(ceil(max(data2[DataHelper.Project.ID_DATA_SPEED][tmc1].values)))
        y2, x2 = np_hist(data2[DataHelper.Project.ID_DATA_SPEED][tmc1].values, bins=[el for el in range(max_speed2 + bin_extend)])
        y2 = np_append(y2, [0])
        sum_y2 = sum(y2)
        self.axes.plot(x2, y2 / sum(y2), color=color_str, label='Before', ls='--')
        # After Data
        max_speed = int(ceil(max(data1[DataHelper.Project.ID_DATA_SPEED][tmc1].values)))
        y, x = np_hist(data1[DataHelper.Project.ID_DATA_SPEED][tmc1].values, bins=[el for el in range(max_speed + bin_extend)])
        y = np_append(y, [0])
        sum_y = sum(y)
        self.axes.plot(x, y / sum(y), color=color_str, label='After')

        title_str = title_preamble + 'Speed Frequency: ' + self.panel.project.get_name()
        title_str = title_str + ' (' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')'
        title_str = title_str + '\n'
        if self.region2 != 0:
            title_str = title_str + 'Before/After: ' + self.panel.period1 + ' vs ' + self.panel.period2
        elif self.region == BEFORE:
            title_str = title_str + 'Period 1: ' + self.panel.period1
        else:
            title_str = title_str + 'Period 2: ' + self.panel.period2
        self.axes.set_title(title_str)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_xlabel('Speed (mph)')
        self.axes.set_ylabel('% Frequency')
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        # self.fig.tight_layout()

    def export_speed_freq(self):
        response = QtWidgets.QMessageBox.information(self, 'Speed Frequency Export',
                                                     'The underlying data for the Speed Frequency chart is the same as that for the Speed CDF chart, '
                                                     'but organized as a histogram.  This will export the Speed CDF data, and the user will be '
                                                     'responsible for creating the histogram in a program such as Microsoft Excel.\n\nExport data?',
                                                     QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Ok)
        if response == QtWidgets.QMessageBox.Ok:
            self.export_speed_cdf()

    def compute_dq_wkdy(self):
        data = self.panel.plot_dfs_dq[0]
        # self.axes.set_yticks([0.5, 0.8])
        # self.axes.set_yticklabels(['50%', '80%'])
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        title_str = '% Data Available by Day of Week'
        if self.panel.chart_title_str is not None:
            title_str = title_str + ' ' + '(' + self.panel.chart_title_str + ')'
        self.axes.set_title(title_str, y=1.08)
        self.axes.set_ylim(0, 1)
        self.axes.set_xticks([el for el in range(data.shape[0])])
        self.axes.set_xticklabels([calendar.day_abbr[el] for el in range(data.shape[0])], rotation='vertical')
        y_values = data.values.reshape(data.shape[0], )
        threshold_upper = self.project.data_avail_threshold_upper
        threshold_lower = self.project.data_avail_threshold_lower
        upper_label = str(int(threshold_upper * 100)) + '%'
        lower_label = str(int(threshold_lower * 100)) + '%'
        self.axes.plot([el for el in range(len(y_values))], [threshold_upper for el in range(len(y_values))], label=upper_label, c='green', ls=':')
        self.axes.plot([el for el in range(len(y_values))], [threshold_lower for el in range(len(y_values))], label=lower_label, c='firebrick', ls=':')
        self.axes.legend()
        self.wkdy_bars = self.axes.bar([el for el in range(data.shape[0])], y_values)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        # Use custom colors and opacity
        dq_cm = create_dq_cmap()
        for r, bar in zip(y_values, self.wkdy_bars):
            # bar.set_facecolor(plt.cm.RdYlGn(r / 10.))
            bar.set_facecolor(dq_cm(r))
            bar.set_alpha(0.8)

    def export_dq_wkdy(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            export_df = self.panel.plot_dfs_dq[0].to_frame('Wkdy_Pct_Data_Avail')
            export_df.reset_index(inplace=True)
            export_df['day_name'] = export_df['weekday'].apply(lambda day_id: calendar.day_abbr[day_id])
            export_df = export_df[['weekday', 'day_name', 'Wkdy_Pct_Data_Avail']]
            if file_filter.count('h5') > 0:
                # self.panel.plot_dfs_dq[0].to_hdf(f_name, 'table')
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    # self.panel.plot_dfs_dq[0].to_csv(f_name)
                    export_df.to_csv(f_name, index=False)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_dq_tod(self):
        data = self.panel.plot_dfs_dq[1]
        radii = data.values
        N = len(radii)
        bottom = 0
        if N > 0:
            width = (2 * np_pi) / N
        else:
            width = 0
        theta = np_linspace(0.0, 2 * np_pi, N, endpoint=False)
        self.axes.set_theta_zero_location('N')
        self.axes.set_theta_direction(-1)
        self.axes.set_xticklabels(['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'])
        # self.axes.set_yticks([0.5, 0.8])
        # self.axes.set_yticklabels(['50%', '80%'])
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        title_str = '% Data Available by Time of Day'
        if self.panel.chart_title_str is not None:
            title_str = title_str + ' ' + '(' + self.panel.chart_title_str + ')'
        self.axes.set_title(title_str, y=1.08)
        self.axes.set_ylim(0, 1)
        self.tod_bars = self.axes.bar(theta, radii, width=width, bottom=bottom)
        # Use custom colors and opacity
        dq_cm = create_dq_cmap()
        for r, bar in zip(radii, self.tod_bars):
            bar.set_facecolor(dq_cm(r))
            bar.set_alpha(0.8)

    def export_dq_tod(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            export_df = self.panel.plot_dfs_dq[1].to_frame('TimeOfDay_Pct_Data_Avail')
            export_df.reset_index(inplace=True)
            export_df['Hour'] = export_df['Hour'].apply(lambda hour: time(hour, 0, 0).strftime('%I:%M%p'))
            # export_df = export_df[['weekday', 'day_name', 'Wkdy_Pct_Data_Avail']]
            if file_filter.count('h5') > 0:
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    export_df.to_csv(f_name, index=False)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_dq_tmc(self):
        data = self.panel.plot_dfs_dq[2]
        data.fillna(0, inplace=True)
        num_tmc = len(data.values)
        # self.axes.set_yticks([0.5, 0.8])
        # self.axes.set_yticklabels(['50%', '80%'])
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        self.axes.set_title('% Data Available by TMC')
        self.axes.set_ylim(0, 1)
        threshold_upper = self.project.data_avail_threshold_upper
        threshold_lower = self.project.data_avail_threshold_lower
        upper_label = str(int(threshold_upper * 100)) + '%'
        lower_label = str(int(threshold_lower * 100)) + '%'
        self.axes.plot([el for el in range(num_tmc)], [threshold_upper for el in range(num_tmc)], label=upper_label, c='green', ls=':')
        self.axes.plot([el for el in range(num_tmc)], [threshold_lower for el in range(num_tmc)], label=lower_label, c='firebrick', ls=':')
        self.axes.legend()
        self.tmc_bars = self.axes.bar([el for el in range(num_tmc)], data.values)
        self.axes.set_xticks([el for el in range(num_tmc)])
        self.axes.set_xticklabels(data.index.tolist(), rotation='vertical')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        # Use custom colors and opacity
        dq_cm = create_dq_cmap()
        for r, bar in zip(data.values, self.tmc_bars):
            bar.set_facecolor(dq_cm(r))
            bar.set_alpha(0.8)

        if not self.bbox_adjusted:
            box = self.axes.get_position()
            self.axes.set_position([box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85])
            self.bbox_adjusted = True

    def export_dq_tmc(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            export_df = self.panel.plot_dfs_dq[2].to_frame('TMC_Pct_Data_Avail')
            export_df.reset_index(inplace=True)
            if file_filter.count('h5') > 0:
                # self.panel.plot_dfs_dq[2].to_hdf(f_name, 'table')
                export_df.to_hdf(f_name, 'table')
            else:
                # self.panel.plot_dfs_dq[2].to_csv(f_name)
                try:
                    export_df.to_csv(f_name, index=False)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_dq_sp(self):
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        y_wd = self.panel.plot_dfs_dq[3][0]  # Weekday data
        y_we = self.panel.plot_dfs_dq[3][1]  # Weekend data
        x_labels = []
        start_date = self.panel.project.database.get_first_date(as_datetime=True)
        year = start_date.year
        month = start_date.month
        for i in range(len(y_wd)):
            x_labels.append(str(month) + '/' + str(year))
            month += 1
            if month > 12:
                month = 1
                year += 1
        self.axes.set_xticks([el for el in range(len(y_wd))])
        self.axes.set_xticklabels(x_labels, rotation='vertical')
        title_str = 'Monthly % Data Available over Time'
        if self.panel.chart_title_str is not None:
            title_str = title_str + ' ' + '(' + self.panel.chart_title_str + ')'
        self.axes.set_title(title_str)
        self.axes.set_ylim(0, 1)
        self.axes.plot([el for el in range(len(y_wd))], y_wd, c='grey', label='Weekdays')
        self.axes.plot([el for el in range(len(y_we))], y_we, c='grey', ls='--', label='Weekends')
        threshold_upper = self.project.data_avail_threshold_upper
        threshold_lower = self.project.data_avail_threshold_lower
        upper_label = str(int(threshold_upper * 100)) + '%'
        lower_label = str(int(threshold_lower * 100)) + '%'
        self.axes.plot([el for el in range(len(y_wd))], [threshold_upper for el in range(len(y_wd))], label=upper_label, c='green', ls=':')
        self.axes.plot([el for el in range(len(y_wd))], [threshold_lower for el in range(len(y_wd))], label=lower_label, c='firebrick', ls=':')
        self.axes.legend()
        width = 0.35
        self.sp_bars1 = self.axes.bar([el for el in range(len(y_wd))], y_wd, width, label='Weekdays')
        self.sp_bars2 = self.axes.bar([el + width for el in range(len(y_we))], y_we, width, label='Weekends')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        # Use custom colors and opacity
        dq_cm = create_dq_cmap()
        for r, bar in zip(y_wd, self.sp_bars1):
            bar.set_facecolor(dq_cm(r))
            bar.set_alpha(0.8)
        for r, bar in zip(y_we, self.sp_bars2):
            bar.set_facecolor(dq_cm(r))
            bar.set_alpha(0.8)

        if not self.bbox_adjusted:
            box = self.axes.get_position()
            self.axes.set_position([box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85])
            self.bbox_adjusted = True

    def export_dq_sp(self):
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                                    '',
                                                                    'CSV files (*.csv);;HDF5 files (*.h5)',
                                                                    'CSV files (*.csv)')
        if f_name:
            export_df = DataFrame()
            export_df['weekday'] = self.panel.plot_dfs_dq[3][0]
            export_df['weekend'] = self.panel.plot_dfs_dq[3][1]
            labels = []
            start_date = self.panel.project.database.get_first_date(as_datetime=True)
            year = start_date.year
            month = start_date.month
            for i in range(export_df['weekday'].count()):
                labels.append(str(month) + '/' + str(year))
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            export_df['YearMonth'] = labels
            export_df = export_df[['YearMonth', 'weekday', 'weekend']]
            if file_filter.count('h5') > 0:
                export_df.to_hdf(f_name, 'table')
            else:
                try:
                    export_df.to_csv(f_name, index=False)
                except IOError:
                    QtWidgets.QMessageBox.warning(self, 'Export Failed',
                                                  'File was unable to be written.  If a file with the same name is open in Excel, it must be closed' +
                                                  ' before it can be written.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return
            QtWidgets.QMessageBox.information(self, 'Export Successful!',
                                              'Data successfully written to:\n' + f_name,
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def compute_lottr_corr_summ(self):
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        x_arr = np_arange(1)
        width = 0.25
        ama = self.project.summary_data().get_lottr_dict_am(0)
        pma = self.project.summary_data().get_lottr_dict_pm(0)
        mda = self.project.summary_data().get_lottr_dict_md_wkdy(0)
        wea = self.project.summary_data().get_lottr_dict_md_wknd(0)
        am_cnt = [1 if v < 1.5 else 0 for v in ama.values()]
        pm_cnt = [1 if v < 1.5 else 0 for v in pma.values()]
        md_cnt = [1 if v < 1.5 else 0 for v in mda.values()]
        we_cnt = [1 if v < 1.5 else 0 for v in wea.values()]
        am_val1 = [100.0 * sum(am_cnt) / len(am_cnt)]
        pm_val1 = [100.0 * sum(pm_cnt) / len(pm_cnt)]
        md_val1 = [100.0 * sum(md_cnt) / len(md_cnt)]
        we_val1 = [100.0 * sum(we_cnt) / len(we_cnt)]
        ama = self.project.summary_data().get_lottr_dict_am(1)
        pma = self.project.summary_data().get_lottr_dict_pm(1)
        mda = self.project.summary_data().get_lottr_dict_md_wkdy(1)
        wea = self.project.summary_data().get_lottr_dict_md_wknd(1)
        am_cnt = [1 if v < 1.5 else 0 for v in ama.values()]
        pm_cnt = [1 if v < 1.5 else 0 for v in pma.values()]
        md_cnt = [1 if v < 1.5 else 0 for v in mda.values()]
        we_cnt = [1 if v < 1.5 else 0 for v in wea.values()]
        am_val2 = [100.0 * sum(am_cnt) / len(am_cnt)]
        pm_val2 = [100.0 * sum(pm_cnt) / len(pm_cnt)]
        md_val2 = [100.0 * sum(md_cnt) / len(md_cnt)]
        we_val2 = [100.0 * sum(we_cnt) / len(we_cnt)]
        self.axes.bar(x_arr + 0 * width, am_val1, width=width, label='AM (Before)', color='#1f77b4')
        self.axes.bar(x_arr + 1 * width, am_val2, width=width, label='AM (After)', color='#aec7e8')
        self.axes.bar(x_arr + 3 * width, pm_val1, width=width, label='PM (Before)', color='#ff7f0e')
        self.axes.bar(x_arr + 4 * width, pm_val2, width=width, label='PM (After)', color='#ffbb78')
        self.axes.bar(x_arr + 6 * width, md_val1, width=width, label='Midday (Before)', color='#2ca02c')
        self.axes.bar(x_arr + 7 * width, md_val2, width=width, label='Midday (After)', color='#98df8a')
        self.axes.bar(x_arr + 9 * width, we_val1, width=width, label='Weekend (Before)', color='#d62728')
        self.axes.bar(x_arr + 10 * width, we_val2, width=width, label='Weekend (After)', color='#ff9896')
        x_arr2 = [0, 10 * width]
        target = [80 for el in range(len(x_arr2))]
        self.axes.plot(x_arr2, target, color='grey', linestyle=':', label='Target')
        self.axes.set_title('% of TMCs under LoTTR Target by Period')
        self.axes.set_ylabel('Percent')
        self.axes.set_ylim(0, 100)
        self.axes.set_xticklabels([])
        self.axes.set_xticks([])
        # self.axes.legend(ncol=5, loc=9)

        if not self.bbox_adjusted:
            box = self.axes.get_position()
            self.axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            self.bbox_adjusted = True
        self.axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def compute_lottr_corr_all(self):
        pass

    def compute_lottr_tmc(self):
        pass

    def hover_tmc(self, event, tmc_list, peak_idx):
        if event.xdata is not None and event.ydata is not None:
            # print(str(int(event.xdata)) + ',' + str(int(event.ydata)))
            self.hover_ann.set_x(int(event.xdata))
            self.hover_ann.set_y(event.ydata)
            hover_idx = 0
            iter_len = tmc_list[DataHelper.Project.ID_TMC_LEN][hover_idx]
            while hover_idx < len(tmc_list) - 1 and event.ydata > iter_len:
                hover_idx += 1
                iter_len += tmc_list[DataHelper.Project.ID_TMC_LEN][hover_idx]

            if hover_idx < len(tmc_list) and hover_idx >= 0:
                if floor(event.xdata) < self.panel.plot_dfs[peak_idx].shape[1] and floor(event.xdata) >= 0:
                    self.hover_ann.set_text(tmc_list[DataHelper.Project.ID_TMC_CODE][hover_idx]
                                            + '\n' + self.f_x_to_day_1l(event.xdata, None)
                                            + '\n' + '{:1.2f} mph'.format(
                        # self.panel.plot_dfs[peak_idx][(self.panel.plot_dfs[peak_idx].shape[0] - hover_idx - 1)][floor(event.xdata)])
                        self.panel.plot_dfs[peak_idx][hover_idx][floor(event.xdata)])
                                            )
            else:
                self.hover_ann.set_text('')
            self.hover_ann.set_visible(True)
            event.canvas.draw()
        else:
            self.hover_ann.set_visible(False)
            event.canvas.draw()

    def hover_tmc_unscaled(self, event, tmc_list, peak_idx):
        if event.xdata is not None and event.ydata is not None:
            # print(str(int(event.xdata)) + ',' + str(int(event.ydata)))
            self.hover_ann.set_x(int(event.xdata))
            self.hover_ann.set_y(int(event.ydata))
            hover_idx = floor(event.ydata * len(tmc_list) / self.tmc_ext)
            # print(self.panel.plot_dfs[3])
            if hover_idx < len(tmc_list) and hover_idx >= 0:
                if floor(event.xdata) < self.panel.plot_dfs[peak_idx].shape[1] and floor(event.xdata) >= 0:
                    self.hover_ann.set_text(tmc_list[hover_idx]
                                            + '\n' + self.f_x_to_day_1l(event.xdata, None)
                                            + '\n' + '{:1.2f} mph'.format(
                        self.panel.plot_dfs[peak_idx][(self.panel.plot_dfs[peak_idx].shape[0] - hover_idx - 1)][floor(event.xdata)]))
            else:
                self.hover_ann.set_text('')
            self.hover_ann.set_visible(True)
            event.canvas.draw()
        else:
            self.hover_ann.set_visible(False)
            event.canvas.draw()

    def hover_datetime(self, event, convert_func, label='minutes'):
        if event.xdata is not None and event.ydata is not None:
            # print(str(int(event.xdata)) + ',' + str(int(event.ydata)))
            # self.hover_ann.set_x(event.xdata)
            # self.hover_ann.set_y(event.ydata)
            self.hover_ann.set_position((event.xdata, event.ydata))
            # '{:1.1f} mi'.format(mile_post)
            # print('{:1.2f} minutes'.format(event.ydata) + '\n' + convert_func(event.xdata, None))
            temp_str = '{:1.2f} ' + label
            # self.hover_ann.set_text('{:1.2f} minutes'.format(event.ydata) + '\n' + convert_func(event.xdata, None))
            self.hover_ann.set_text(temp_str.format(event.ydata) + '\n' + convert_func(event.xdata, None))
            self.hover_ann.set_visible(True)
            event.canvas.draw()
        else:
            self.hover_ann.set_visible(False)
            event.canvas.draw()


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
        self.default_xlim = None
        self.default_ylim = None

    def set_default_xlim(self, new_xlim):
        self.default_xlim = new_xlim

    def set_default_ylim(self, new_ylim):
        self.default_ylim = new_ylim

    def zoom_factory(self, ax, mpl_panel, base_scale=2.0):
        def zoom(event):
            allow_key_zoom = True
            if mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP_FACILITY or mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP:
                allow_key_zoom = False

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            if new_width < 1.0:
                return

            if allow_key_zoom and event.key is "control":
                if xdata is not None:
                    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
                    ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
            elif allow_key_zoom and event.key is "shift":
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

        fig = ax.get_figure()  # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax, mpl_panel):
        def onPress(event):
            if event.button == 3:
                cursor = QCursor()
                mpl_panel.context_menu.popup(cursor.pos())
            else:
                if mpl_panel.fig_type is FIG_DQ_TOD:
                    return
                if ax.get_navigate_mode() is None:
                    if event.dblclick:
                        mpl_panel.reset_axis_bounds()
                    else:
                        if event.inaxes != ax: return
                        self.cur_xlim = ax.get_xlim()
                        self.cur_ylim = ax.get_ylim()
                        self.press = self.x0, self.y0, event.xdata, event.ydata
                        self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            if event.button == 3:
                pass
            else:
                if mpl_panel.fig_type is FIG_DQ_TOD:
                    return
                if ax.get_navigate_mode() is None:
                    self.press = None
                    ax.figure.canvas.draw()

        def onMotion(event):
            if event.button == 3:
                pass
            else:
                # if mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP_FACILITY or mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP:
                #     return
                if mpl_panel.fig_type is FIG_DQ_TOD:
                    return
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

        fig = ax.get_figure()  # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMotion)

        # return the function
        return onMotion


def create_spacer_line(parent):
    line = QtWidgets.QFrame(parent)
    line.setFrameShape(QtWidgets.QFrame.VLine)
    line.setLineWidth(5)
    line.setMidLineWidth(5)
    return line


def convert_x_to_day(x, pos, start_date, two_lines=True):
    # if int(x) - x != 0:
    #     return ''
    # new_date = start_date + timedelta(days=int(x))
    new_date = start_date + timedelta(days=x)
    # return new_date.strftime('%m/%d/%Y') + '\n' + calendar.day_abbr[new_date.weekday()]
    # return new_date.strftime('%m/%d') + '\n' + new_date.strftime('%Y') + '\n' + calendar.day_abbr[new_date.weekday()]
    if two_lines is True:
        mid_string = '\n'
    else:
        mid_string = ' '
    return new_date.strftime('%m/%d/%y') + mid_string + calendar.day_abbr[new_date.weekday()]


def convert_x_to_tmc(x, pos, tmc_list):
    if x >= 0 and x < len(tmc_list):
        return tmc_list[int(x)]
    else:
        return 0


def convert_x_to_mile(x, pos, tmc_list, facilit_len):
    if x >= 0 and x < len(tmc_list):
        return '{:1.1f} mi'.format(x / len(tmc_list) * facilit_len)
    else:
        return ''


def convert_extent_to_tmc(x, pos, tmc_list, tmc_extent):
    tmc_span = tmc_extent / len(tmc_list)
    c_idx = x // tmc_span
    return tmc_list[min(c_idx, len(tmc_list) - 1)]


def convert_extent_to_mile(x, pos, facility_len, tmc_ext):
    mile_post = facility_len - x * facility_len / tmc_ext
    return '{:1.1f} mi'.format(mile_post)


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


def convert_xval_to_month(x, pos, first_year, first_month):
    first_month -= 1  # decrementing to help with modulus
    if x < 0:
        return ''
    x = int(x)
    return str(first_year + ((first_month + x) // 12)) + '-' + calendar.month_abbr[((first_month + x) % 12) + 1]


def compute_num_months(qdate1, qdate2):
    m1 = qdate1.month()
    m2 = qdate2.month()

    y1 = qdate1.year()
    y2 = qdate2.year()

    if y1 == y2:
        return m2 - m1 + 1
    else:
        month_count = 12 - m1 + 1
        y1 += 1
        while y1 < y2:
            month_count += 12
            y1 += 1
        month_count += m2
        return month_count
