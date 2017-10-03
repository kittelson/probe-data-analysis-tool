# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#               2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

import sys
import os
import random
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from pandas import DataFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from stat_func import create_et_analysis
from data_import import create_casestudy
from viz import run_viz, run_viz_day

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


cs_idx = 11
facility_len = 8.129638  # 34.729669
zoom_full = True
if zoom_full:
    y_min = 0
    y_max = 35  # 145
    x_min = 0
    x_max = 288
else:
    y_min = 20
    y_max = 40
    x_min = 192
    x_max = 240


def convert_index(indexes):
    return [convert_val(int(ap.get_text())) if ap.get_text() != '' else '' for ap in indexes]


def convert_val(idx):
    hour = idx // 12
    ampm = 'am'
    if hour >=12:
        ampm = 'pm'
        hour = hour-12
    if hour == 0:
        hour = 12
    min = (idx % 12) * 5

    return str(hour)+':'+str(min)+ampm


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, app=None, region=0, region2=-1, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
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

    def compute_initial_figure(self):
        pass


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
        self.axes.set_ybound([y_min, y_max])
        self.axes.set_xbound([x_min, x_max])
        if zoom_full:
            self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
            self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        else:
            self.axes.set_xticks([192, 204, 216, 228, 240])
            self.axes.set_xticklabels(['4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm'])
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
        self.axes.set_ybound([y_min, y_max])
        self.axes.set_xbound([x_min, x_max])
        if zoom_full:
            self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
            self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        else:
            self.axes.set_xticks([192, 204, 216, 228, 240])
            self.axes.set_xticklabels(['4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm'])
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
                            labels=['Average', '95th Percentile'])
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                            self.app.plot_dfs[self.region2]['mean'], 'r--', label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           self.app.plot_dfs[self.region2]['percentile_95'], 'c--', label='Before-95th PCT')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([y_min, y_max])
        self.axes.set_xbound([x_min, x_max])
        if zoom_full:
            self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
            self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        else:
            self.axes.set_xticks([192, 204, 216, 228, 240])
            self.axes.set_xticklabels(['4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def update_figure(self):
        self.axes.cla()
        self.axes.stackplot(self.app.plot_dfs[self.region].index,
                            self.app.plot_dfs[self.region]['mean'],
                            self.app.plot_dfs[self.region]['extra_time'],
                            labels=['Average', '95th Percentile'])
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                            self.app.plot_dfs[self.region2]['mean'], 'r--', label='Before-Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           self.app.plot_dfs[self.region2]['percentile_95'], 'c--', label='Before-95th PCT')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([y_min, y_max])
        self.axes.set_xbound([x_min, x_max])
        if zoom_full:
            self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
            self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        else:
            self.axes.set_xticks([192, 204, 216, 228, 240])
            self.axes.set_xticklabels(['4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)


class SpeedBandCanvas(MyMplCanvas):
    """Extra-Time Bar Chart Plot"""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * facility_len) / self.app.plot_dfs[self.region]['percentile_5'],
                               (60 * facility_len) / self.app.plot_dfs[self.region]['mean'],
                               color='#B0C4DE')
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * facility_len) / self.app.plot_dfs[self.region]['mean'],
                               (60 * facility_len) / self.app.plot_dfs[self.region]['percentile_95'],
                               color='#B0C4DE')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60*facility_len) / self.app.plot_dfs[self.region]['percentile_5'], color='#B0C4DE', label='5th Percentile')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * facility_len) / self.app.plot_dfs[self.region]['mean'], color='#cd5c5c', label='Average')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * facility_len) / self.app.plot_dfs[self.region]['percentile_95'], color='#B0C4DE', label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * facility_len) / self.app.plot_dfs[self.region2]['mean'], 'r--', label='Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * facility_len) / self.app.plot_dfs[self.region2]['percentile_95'], 'c--', label='95th Percentile')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([0, 80])
        self.axes.set_xbound([x_min, x_max])
        if zoom_full:
            self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
            self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        else:
            self.axes.set_xticks([192, 204, 216, 228, 240])
            self.axes.set_xticklabels(['4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)

    def update_figure(self):
        self.axes.cla()
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * facility_len) / self.app.plot_dfs[self.region]['percentile_5'],
                               (60 * facility_len) / self.app.plot_dfs[self.region]['mean'],
                               color='#B0C4DE')
        self.axes.fill_between(self.app.plot_dfs[self.region].index,
                               (60 * facility_len) / self.app.plot_dfs[self.region]['mean'],
                               (60 * facility_len) / self.app.plot_dfs[self.region]['percentile_95'],
                               color='#B0C4DE')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * facility_len) / self.app.plot_dfs[self.region]['percentile_5'], color='#B0C4DE', label='5th Percentile')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * facility_len) / self.app.plot_dfs[self.region]['mean'], color='#cd5c5c', label='Average')
        self.axes.plot(self.app.plot_dfs[self.region].index,
                       (60 * facility_len) / self.app.plot_dfs[self.region]['percentile_95'], color='#B0C4DE', label='95th Percentile')
        if self.region2 >= 0:
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * facility_len) / self.app.plot_dfs[self.region2]['mean'], 'r--', label='Average')
            self.axes.plot(self.app.plot_dfs[self.region2].index,
                           (60 * facility_len) / self.app.plot_dfs[self.region2]['percentile_95'], 'c--', label='95th Percentile')
        self.axes.set_title(self.app.titles[self.region])
        self.axes.set_xlabel('Time of Day')
        self.axes.set_ylabel('Travel Time Minutes')
        self.axes.set_ybound([0, 80])
        self.axes.set_xbound([x_min, x_max])
        if zoom_full:
            self.axes.set_xticks([0, 48, 96, 144, 192, 240, 288])
            self.axes.set_xticklabels(['12:00am', '4:00am', '8:00am', '12:00pm', '4:00pm', '8:00pm', '11:55pm'])
        else:
            self.axes.set_xticks([192, 204, 216, 228, 240])
            self.axes.set_xticklabels(['4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm'])
        self.axes.legend()
        self.axes.grid(color='0.85', linestyle='-', linewidth=0.5)


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.init_mode = True
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        self.tmcs, self.dfs, self.tt_comp, self.available_days, self.titles = run_viz_day(cs_idx, [], print_csv=False, return_tt=False)
        self.plot_tt = self.tt_comp
        self.plot_dfs = [create_et_analysis(df) for df in self.dfs]

        self.v_layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.before_bar = QtWidgets.QWidget(self)
        self.after_bar = QtWidgets.QWidget(self)
        self.analysis_bar = QtWidgets.QWidget(self)
        self.v_layout_before = QtWidgets.QVBoxLayout(self.before_bar)
        self.v_layout_after = QtWidgets.QVBoxLayout(self.after_bar)
        self.h_layout_analysis = QtWidgets.QHBoxLayout(self.analysis_bar)
        self.sc = ExtraTimeAreaChartCanvas(self.main_widget, app=self, region=0, width=5, height=4, dpi=100)
        self.dc = SpeedBandCanvas(self.main_widget, app=self, region=0, width=5, height=4, dpi=100)
        self.sc_after = ExtraTimeAreaChartCanvas(self.main_widget, app=self, region=2, region2=0, width=5, height=4, dpi=100)
        self.dc_after = SpeedBandCanvas(self.main_widget, app=self, region=2, region2=0, width=5, height=4, dpi=100)
        self.navi_toolbar = NavigationToolbar(self.sc, self)
        self.navi_toolbar2 = NavigationToolbar(self.dc, self)
        self.navi_toolbar3 = NavigationToolbar(self.sc_after, self)
        self.navi_toolbar4 = NavigationToolbar(self.dc_after, self)
        self.check_bar = QtWidgets.QWidget(self)
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar)

        self.check_mon = QtWidgets.QCheckBox('Mon')
        self.check_mon.stateChanged.connect(self.check_func)
        if self.available_days.count(0) > 0:
            self.check_mon.setChecked(True)
        else:
            self.check_mon.setDisabled(True)

        self.check_tue = QtWidgets.QCheckBox('Tue')
        self.check_tue.stateChanged.connect(self.check_func)
        if self.available_days.count(1) > 0:
            self.check_tue.setChecked(True)
        else:
            self.check_tue.setDisabled(True)

        self.check_wed = QtWidgets.QCheckBox('Wed')
        self.check_wed.stateChanged.connect(self.check_func)
        if self.available_days.count(2) > 0:
            self.check_wed.setChecked(True)
        else:
            self.check_wed.setDisabled(True)

        self.check_thu = QtWidgets.QCheckBox('Thu')
        self.check_thu.stateChanged.connect(self.check_func)
        if self.available_days.count(3) > 0:
            self.check_thu.setChecked(True)
        else:
            self.check_thu.setDisabled(True)

        self.check_fri = QtWidgets.QCheckBox('Fri')
        self.check_fri.stateChanged.connect(self.check_func)
        if self.available_days.count(4) > 0:
            self.check_fri.setChecked(True)
        else:
            self.check_fri.setDisabled(True)

        self.check_sat = QtWidgets.QCheckBox('Sat')
        self.check_sat.stateChanged.connect(self.check_func)
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(True)
        else:
            self.check_sat.setDisabled(True)

        self.check_sun = QtWidgets.QCheckBox('Sun')
        self.check_sun.stateChanged.connect(self.check_func)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(True)
        else:
            self.check_sun.setDisabled(True)

        self.h_layout.addWidget(self.check_mon)
        self.h_layout.addWidget(self.check_tue)
        self.h_layout.addWidget(self.check_wed)
        self.h_layout.addWidget(self.check_thu)
        self.h_layout.addWidget(self.check_fri)
        self.h_layout.addWidget(self.check_sat)
        self.h_layout.addWidget(self.check_sun)

        # self.v_layout.addWidget(self.navi_toolbar)
        # self.v_layout.addWidget(self.sc)
        # self.v_layout.addWidget(self.navi_toolbar2)
        # self.v_layout.addWidget(self.dc)
        # self.v_layout.addWidget(self.check_bar)

        self.v_layout_before.addWidget(self.navi_toolbar)
        self.v_layout_before.addWidget(self.sc)
        self.v_layout_before.addWidget(self.navi_toolbar2)
        self.v_layout_before.addWidget(self.dc)
        self.v_layout_after.addWidget(self.navi_toolbar3)
        self.v_layout_after.addWidget(self.sc_after)
        self.v_layout_after.addWidget(self.navi_toolbar4)
        self.v_layout_after.addWidget(self.dc_after)
        self.h_layout_analysis.addWidget(self.before_bar)
        self.h_layout_analysis.addWidget(self.after_bar)
        self.v_layout.addWidget(self.analysis_bar)
        self.v_layout.addWidget(self.check_bar)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        #self.statusBar().showMessage("All hail matplotlib!", 2000)

        self.init_mode = False

    def check_func(self):
        if not self.init_mode:
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
        self.sc.update_figure()
        self.dc.update_figure()
        self.sc.draw()
        self.dc.draw()
        self.sc_after.update_figure()
        self.dc_after.update_figure()
        self.sc_after.draw()
        self.dc_after.draw()

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    """embedding_in_qt5.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale, 2015 Jens H Nielsen

This program is a simple example of a Qt5 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation.

This is modified from the embedding in qt4 example to show the difference
between qt4 and qt5"""
                                )


qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()