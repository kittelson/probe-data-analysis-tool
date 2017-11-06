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
import calendar
from datetime import datetime, timedelta
from math import floor


FIG_TYPE_TT_TREND_LINE = 0
FIG_TYPE_TT_TREND_BAR = 1
FIG_TYPE_SPD_HEAT_MAP = 2
FIG_TYPE_SPD_HEAT_MAP_FACILITY = 3
FIG_TYPE_PCT_CONG_DAY = 4
FIG_TYPE_PCT_CONG_TMC = 5


class MplChart(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, fig_type=0, panel=None, region=0, region2=-1, is_subset=False, width=5, height=4, dpi=100, **kwargs):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig_type = fig_type

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setFocus()
        self.panel = None
        self.fig_title_str = ''
        if panel is not None:
            self.panel = panel
            self.fig_title_str = self.panel.project.get_name()
        # self.fig.suptitle(self.fig_title_str)
        self.region = region
        self.region2 = region2
        self.is_subset = is_subset

        self.default_xlim = None
        self.default_ylim = None

        self.show_am = True
        self.show_pm = True
        self.show_mid = False

        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
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

        start_date = self.panel.project.database.get_first_date(as_datetime=True)

        self.f_x_to_month = lambda x, pos: convert_xval_to_month(x, pos, start_date.year, start_date.month)
        # self.f_x_to_day = lambda x, pos: convert_x_to_day(x, pos, self.project.database.get_first_date(as_datetime=True))
        self.f_x_to_day = lambda x, pos: convert_x_to_day(x, pos, start_date)
        self.f_x_to_tmc = lambda x, pos: convert_x_to_tmc(x, pos, self.panel.project.get_tmc(as_list=True))
        self.f_y_to_time = lambda y, pos: convert_xval_to_time(y, pos, 5)

        self.color_bar1 = None
        self.color_bar2 = None

        self.compute_initial_figure()

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)

        FigureCanvas.updateGeometry(self)

        self.context_menu = QtWidgets.QMenu(self)
        self.toggle_legend_action = QtWidgets.QAction('Toggle Chart Legend', self)
        self.toggle_legend_action.setToolTip('Toggle the chart legend on/off')
        self.toggle_legend_action.triggered.connect(self.toggle_legend)
        self.context_menu.addAction(self.toggle_legend_action)

        self.save_figure_action = QtWidgets.QAction('Save Chart as Image', self)
        self.save_figure_action.setToolTip('Save the chart as an image file (png, jpg, etc.)')
        self.save_figure_action.triggered.connect(self.save_figure)
        self.context_menu.addAction(self.save_figure_action)

        self.reset_axis_action = QtWidgets.QAction('Reset Axis Bounds', self)
        self.reset_axis_action.setToolTip('Reset the x and y bounds of the chart')
        self.reset_axis_action.triggered.connect(self.reset_axis_bounds)
        self.context_menu.addAction(self.reset_axis_action)

        scale = 1.1
        self.zp = ZoomPan()
        figZoom = self.zp.zoom_factory(self.axes, self, base_scale=scale)
        figPan = self.zp.pan_factory(self.axes, self)
        self.set_x_bounds(self.axes.get_xlim()[0], self.axes.get_xlim()[1], make_default=True)
        self.set_y_bounds(self.axes.get_ylim()[0], self.axes.get_ylim()[1], make_default=True)

    def toggle_legend(self):
        if self.axes.legend_ is not None:
            self.axes.legend_ = None
        else:
            # self.axes.legend()
            if self.fig_type is FIG_TYPE_TT_TREND_BAR and not self.panel.plot_dfs[0].empty:
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
        f_name, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '', 'PNG files (*.png);;PDF files (*.pdf);;JPEG files (*.jpg)', 'PNG files (*.png)')
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

    def update_figure(self):
        self.axes.cla()
        self.compute_initial_figure()

    def compute_trend_line(self):
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

        self.axes.set_title(self.panel.peak_period_str + 'Travel Time Trends by Month'
                            + '(' + self.panel.selected_tmc_name + ', {:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')
        self.axes.set_ylabel('Travel Time (Minutes)')
        self.axes.legend()
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_month))
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)
        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
                                            annotation_clip=False)
        self.hover_ann.set_visible(False)
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover_datetime(event, self.f_x_to_month))
        self.fig.tight_layout()

    def compute_trend_bar(self):
        width = 0.35
        if self.show_am:
            tt_am_mean_dir1 = self.panel.plot_dfs[0]['mean']
            # tt_am_pct5_dir1 = self.app.plot_dfs[0]['percentile_5']
            tt_am_pct95_dir1 = self.panel.plot_dfs[0]['percentile_95']
            x = [el for el in range(len(tt_am_mean_dir1))]
            self.axes.bar(x, tt_am_mean_dir1, width, color='C0', label='AM-Mean')
            # ax3.bar(x, tt_am_pct5_dir1, color='C0', linestyle='--', lw=1.0, label='AM-5th Pct')
            self.axes.bar(x, [tt_am_pct95_dir1[i] - tt_am_mean_dir1[i] for i in range(len(tt_am_mean_dir1))], width, bottom=tt_am_mean_dir1, color='#aec7e8',
                    label='AM-95th Pct')
        if self.show_pm:
            tt_pm_mean_dir1 = self.panel.plot_dfs[0]['meanpm']
            # tt_pm_pct5_dir1 = self.app.plot_dfs[0]['percentile_5pm']
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
            # tt_md_pct5_dir1 = self.app.plot_dfs[0]['percentile_5mid']
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
        self.axes.set_ylabel('Travel Time (Minutes)')
        if not self.panel.plot_dfs[0].empty:
            self.axes.legend()
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_month))
        self.hover_ann = self.axes.annotate('', xy=(2, 1), xytext=(3, 1.5),
                                            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
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
        #bin_labels.insert(0, '<' + str(BIN1) + 'mph')
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
        self.axes.set_title('Facility Speeds over Time')
        self.axes.legend()
        self.fig.tight_layout()

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
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_tmc))
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=0))
        self.axes.set_xlabel('TMC ID')
        self.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.2%}'.format(y)))
        self.axes.set_ylabel('Percent Congested')
        self.axes.set_title(self.panel.project.get_name() + ' - Facility Speeds by TMC')
        self.axes.legend()
        self.fig.tight_layout()

    def compute_speed_heatmap(self):
        imshow_data = self.panel.plot_dfs[3]
        im = self.axes.imshow(imshow_data, cmap='RdYlGn')
        if self.color_bar1 is not None:
            self.color_bar1.remove()
        self.color_bar1 = self.fig.colorbar(im, ax=self.axes, shrink=0.8)
        self.color_bar1.set_label('Speed (mph)')
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_day))
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.f_y_to_time))
        self.axes.set_title('Daily Speed Heatmap for ' + self.panel.selected_tmc_name + ' (' + '{:1.2f} mi'.format(self.panel.selected_tmc_len) + ')')

    def compute_speed_tmc_heatmap(self):
        if self.show_am:
            hour_str = convert_xval_to_time(self.panel.ap_start1, None, 5) + '-' + convert_xval_to_time(self.panel.ap_end1, None, 5)
            imshow_data = self.panel.plot_dfs[4]
        elif self.show_mid:
            hour_str = convert_xval_to_time(self.panel.ap_start2, None, 5) + '-' + convert_xval_to_time(self.panel.ap_end2, None, 5)
            imshow_data = self.panel.plot_dfs[5]
        else:
            hour_str = convert_xval_to_time(self.panel.ap_start3, None, 5) + '-' + convert_xval_to_time(self.panel.ap_end3, None, 5)
            imshow_data = self.panel.plot_dfs[6]
        num_tmc, num_days = imshow_data.shape
        self.tmc_ext = num_days / 5
        cb_shrink = 0.95
        im = self.axes.imshow(imshow_data, extent=[0, num_days, 0, self.tmc_ext], cmap='RdYlGn')
        if self.color_bar2 is not None:
            self.color_bar2.remove()
        self.color_bar2 = self.fig.colorbar(im, ax=self.axes, shrink=cb_shrink)
        self.color_bar2.set_label('Speed (mph)')
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.f_x_to_day))
        # f_tmc_label2 = lambda x, pos: convert_extent_to_tmc(x, pos, self.panel.project.get_tmc(as_list=True), self.tmc_ext)
        f_tmc_label2 = lambda x, pos: convert_extent_to_mile(x, pos, self.panel.facility_len, self.tmc_ext)
        self.axes.yaxis.set_major_formatter(FuncFormatter(f_tmc_label2))
        self.axes.set_title(self.panel.project.get_name() + ' Spatial Speed Heatmap: ' + hour_str)
        # self.fig.tight_layout()
        tmc_list = self.panel.project.get_tmc(as_list=True).tolist()
        tmc_list.reverse()
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover_tmc(event, tmc_list))

    def hover_tmc(self, event, tmc_list):
        if event.xdata is not None and event.ydata is not None:
            # print(str(int(event.xdata)) + ',' + str(int(event.ydata)))
            self.hover_ann.set_x(int(event.xdata))
            self.hover_ann.set_y(int(event.ydata))
            hover_idx = floor(event.ydata*len(tmc_list) / self.tmc_ext)
            if hover_idx < len(tmc_list):
                self.hover_ann.set_text(tmc_list[hover_idx])
            else:
                self.hover_ann.set_text('')
            self.hover_ann.set_visible(True)
            event.canvas.draw()
        else:
            self.hover_ann.set_visible(False)
            event.canvas.draw()

    def hover_datetime(self, event, convert_func):
        if event.xdata is not None and event.ydata is not None:
            # print(str(int(event.xdata)) + ',' + str(int(event.ydata)))
            # self.hover_ann.set_x(event.xdata)
            # self.hover_ann.set_y(event.ydata)
            self.hover_ann.set_position((event.xdata, event.ydata))
            # '{:1.1f} mi'.format(mile_post)
            # print('{:1.2f} minutes'.format(event.ydata) + '\n' + convert_func(event.xdata, None))
            self.hover_ann.set_text('{:1.2f} minutes'.format(event.ydata) + '\n' + convert_func(event.xdata, None))
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
        self.default_xlim=None
        self.default_ylim=None

    def set_default_xlim(self, new_xlim):
        self.default_xlim = new_xlim

    def set_default_ylim(self, new_ylim):
        self.default_ylim = new_ylim

    def zoom_factory(self, ax, mpl_panel, base_scale=2.0):
        def zoom(event):
            # if mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP_FACILITY or mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP:
            #     return

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

        fig = ax.get_figure()  # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax, mpl_panel):
        def onPress(event):
            if event.button == 3:
                cursor = QCursor()
                mpl_panel.context_menu.popup(cursor.pos())
            else:
                # if mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP_FACILITY or mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP:
                #     return
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
                # if mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP_FACILITY or mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP:
                #     return
                if ax.get_navigate_mode() is None:
                    self.press = None
                    ax.figure.canvas.draw()

        def onMotion(event):
            if event.button == 3:
                pass
            else:
                # if mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP_FACILITY or mpl_panel.fig_type is FIG_TYPE_SPD_HEAT_MAP:
                #     return
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
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMotion)

        #return the function
        return onMotion


def create_spacer_line(parent):
    line = QtWidgets.QFrame(parent)
    line.setFrameShape(QtWidgets.QFrame.VLine)
    line.setLineWidth(5)
    line.setMidLineWidth(5)
    return line


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


def convert_extent_to_tmc(x, pos, tmc_list, tmc_extent):
    tmc_span = tmc_extent / len(tmc_list)
    c_idx = x // tmc_span
    return tmc_list[min(c_idx, len(tmc_list)-1)]


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

