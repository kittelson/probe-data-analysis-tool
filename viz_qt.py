"""
Module that houses some Qt-based data-loading classes.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QProgressBar
from DataHelper import Database
import datetime
import pandas as pd
import time
from numpy import mean as np_mean


class ProgressHelper:
    """
    Simple Class to help the progress bar updating between threads
    """
    def __init__(self):
        self.bar = None
        self.emitter = None

    def set_bar(self, bar):
        self.bar = bar

    def set_emitter(self, emitter):
        self.emitter = emitter


class ProjectLoadThread(QThread):
    """
    Loads and extracts the data with a QT progress bar
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    countChanged = pyqtSignal(int)
    progress_helper = None

    def __init__(self, main_window, create_database=True, print_csv=True):
        QThread.__init__(self)
        self.main_window = main_window
        self.print_csv = print_csv

    def set_progress_helper(self, progress_helper):
        self.progress_helper = progress_helper
        self.progress_helper.set_emitter(self.countChanged)

    def run(self):
        database = load_project_data(self.main_window.project, progress_tracker=self.progress_helper)
        self.main_window.project.database = database
        self.countChanged.emit(-1)


class DQDataLoadThread(QThread):
    """
    Loads and extracts the data with a QT progress bar
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    countChanged = pyqtSignal(int)
    progress_helper = None

    def __init__(self, chart_panel, funcs, data=None, tmc=None):
        QThread.__init__(self)
        self.chart_panel = chart_panel
        self.funcs = funcs
        self.data = data
        self.tmc = tmc

    def set_progress_helper(self, progress_helper):
        self.progress_helper = progress_helper
        self.progress_helper.set_emitter(self.countChanged)

    def run(self):
        if self.data is None:
            plot_dfs = compute_data_quality(self.funcs, progress_tracker=self.progress_helper)
        else:
            plot_dfs = compute_data_quality2(self.data, tmc=self.tmc, progress_tracker=self.progress_helper)
        self.chart_panel.plot_dfs_dq = plot_dfs
        self.countChanged.emit(-1)


class Stage2LoadThread(QThread):
    """
    Loads and extracts the data with a QT progress bar
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    countChanged = pyqtSignal(int)
    progress_helper = None

    def __init__(self, chart_panel, dialog, func_dict):
        QThread.__init__(self)
        self.dialog = dialog
        self.chart_panel = chart_panel
        self.func_dict = func_dict

    def set_progress_helper(self, progress_helper):
        self.progress_helper = progress_helper
        self.progress_helper.set_emitter(self.countChanged)

    def run(self):
        stage2_dfs = compute_stage2(self.func_dict, dialog=self.dialog, progress_tracker=self.progress_helper)
        self.chart_panel.plot_dfs = stage2_dfs[0]
        self.chart_panel.plot_dfs2 = stage2_dfs[1]
        self.chart_panel.plot_dfs3 = stage2_dfs[2]
        self.chart_panel.plot_dfs4 = stage2_dfs[3]
        self.countChanged.emit(-1)


class SpatialLoadThread(QThread):
    """
    Loads and extracts the data with a QT progress bar
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    countChanged = pyqtSignal(int)
    progress_helper = None

    def __init__(self, chart_panel, funcs):
        QThread.__init__(self)
        self.chart_panel = chart_panel
        self.funcs = funcs

    def set_progress_helper(self, progress_helper):
        self.progress_helper = progress_helper
        self.progress_helper.set_emitter(self.countChanged)

    def run(self):
        spatial_dfs = compute_spatial_charts(self.funcs, progress_tracker=self.progress_helper)
        self.chart_panel.plot_dfs_temp = spatial_dfs
        self.countChanged.emit(-1)


class TemporalLoadThread(QThread):
    """
    Loads and extracts the data with a QT progress bar
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    countChanged = pyqtSignal(int)
    progress_helper = None

    def __init__(self, chart_panel, funcs):
        QThread.__init__(self)
        self.chart_panel = chart_panel
        self.funcs = funcs

    def set_progress_helper(self, progress_helper):
        self.progress_helper = progress_helper
        self.progress_helper.set_emitter(self.countChanged)

    def run(self):
        temporal_dfs = compute_temporal_charts(self.funcs, progress_tracker=self.progress_helper)
        self.chart_panel.plot_dfs = temporal_dfs
        self.countChanged.emit(-1)


class LoadProjectQT(QDialog):
    """
    Dialog with a Progress Bar marking the progress of loading the data.
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    def __init__(self, main_window, create_database=True, print_csv=True):
        super().__init__(main_window)
        self.main_window = main_window
        self.progress_helper = ProgressHelper()
        self.create_database = create_database
        self.print_csv = print_csv
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Reading Data File...')
        self.progress = QProgressBar(self)
        self.progress_helper.set_bar(self.progress)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.show()

        self.calc = ProjectLoadThread(self.main_window, create_database=self.create_database, print_csv=self.print_csv)
        self.calc.set_progress_helper(self.progress_helper)
        self.calc.countChanged.connect(self.on_count_changed)
        self.calc.start()

    def on_count_changed(self, value):
        if value < 0:
            #self.hide()
            self.accept()
            self.main_window.project.loaded()
        elif value == 1:
            self.setWindowTitle("Compiling Data...")
            self.progress.setValue(value)
        else:
            self.progress.setValue(value)


def load_project_data(project, progress_tracker=None):

    tmc = pd.read_csv(project.get_tmc_file_name())

    # Reading and dropping all null values
    df = pd.read_csv(project.get_data_file_name())  # , parse_dates=['measurement_tstamp']
    df = df[df.speed.notnull()]

    if progress_tracker is not None:
        progress_tracker.bar.setTextVisible(True)
        progress_tracker.bar.setMaximum(len(df) // 10000)
        print(str(len(df) // 10000))

    time1 = time.time()  # Print_Delete
    new_mat = []
    progress = 0
    view_progress = 0
    if progress_tracker is not None:
        for dStr in df['measurement_tstamp']:
            new_mat.append(extract_vals(dStr))
            progress += 1
            if progress == 10000:
                view_progress += 1
                progress = 0
                progress_tracker.emitter.emit(view_progress)
        progress_tracker.bar.setRange(0, 0)
        progress_tracker.emitter.emit(0)
        progress_tracker.bar.setTextVisible(False)
    else:
        new_mat = [extract_vals(dStr) for dStr in df['measurement_tstamp']]

    time2 = time.time()  # Print_Delete
    print('Mat Creation: ' + str(time2 - time1))  # Print_Delete

    # Joining dataframe
    time1 = time.time()  # Print_Delete
    df['Date'], df['Year'], df['Month'], df['Day'], df['AP'], df['weekday'] = create_columns(new_mat)
    df['Hour'] = df['AP'] // 12
    time2 = time.time()  # Print_Delete
    print('DF Creation: '+str(time2-time1))  # Print_Delete

    db = Database(project.get_name(), tmc, df)
    db.set_first_date(df['Date'].min())
    db.set_last_date(df['Date'].max())
    ad = df['weekday'].unique()
    wd = [el for el in ad if el < 5]
    wd.sort()
    we = [el for el in ad if el > 4]
    we.sort()
    db.set_available_weekdays(wd)
    db.set_available_weekends(we)
    m = df['Month'].unique()
    m.sort()
    db.set_available_months(m)

    return db


class LoadDataQualityQT(QDialog):
    """
    Dialog with a Progress Bar marking the progress of loading the data.
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    def __init__(self, chart_panel, mainwindow, funcs, data=None, tmc=None):
        super().__init__(mainwindow)
        self.chart_panel = chart_panel
        self.progress_helper = ProgressHelper()
        self.funcs = funcs
        self.data = data
        self.tmc = tmc
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Analyzing data...')
        self.progress = QProgressBar(self)
        self.progress_helper.set_bar(self.progress)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.show()

        self.calc = DQDataLoadThread(self.chart_panel, self.funcs, data=self.data, tmc=self.tmc)
        self.calc.set_progress_helper(self.progress_helper)
        self.calc.countChanged.connect(self.on_count_changed)
        self.calc.start()

    def on_count_changed(self, value):
        if value < 0:
            self.accept()
            self.chart_panel.plot_data_updated()
        elif value == 1:
            self.setWindowTitle("Computing statistics...")
            self.progress.setValue(value)
        else:
            self.progress.setValue(value)


class LoadStage2QT(QDialog):
    """
    Dialog with a Progress Bar marking the progress of loading the data.
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    def __init__(self, chart_panel, mainwindow, func_dict):
        super().__init__(mainwindow)
        self.chart_panel = chart_panel
        self.progress_helper = ProgressHelper()
        self.func_dict = func_dict
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Initializing...')
        self.progress = QProgressBar(self)
        self.progress_helper.set_bar(self.progress)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.show()

        self.calc = Stage2LoadThread(self.chart_panel, self, self.func_dict)
        self.calc.set_progress_helper(self.progress_helper)
        self.calc.countChanged.connect(self.on_count_changed)
        self.calc.start()

    def on_count_changed(self, value):
        if value < 0:
            self.accept()
            self.chart_panel.plot_data_updated()
        elif value == 1:
            self.setWindowTitle("Computing analysis...")
            self.progress.setValue(value)
        else:
            self.progress.setValue(value)


def compute_data_quality(funcs, progress_tracker=None):
    if progress_tracker is not None:
        progress_tracker.bar.setTextVisible(True)
        progress_tracker.bar.setMaximum(5)

    chart_data = []
    progress = 0
    if progress_tracker is not None:
        chart_data.append(funcs[0]())
        progress += 1
        progress_tracker.emitter.emit(progress)
        chart_data.append(funcs[1]())
        progress += 1
        progress_tracker.emitter.emit(progress)
        chart_data.append(funcs[2]())
        progress += 1
        progress_tracker.emitter.emit(progress)
        chart_data_sub = []
        chart_data_sub.append(funcs[3]())
        progress += 1
        progress_tracker.emitter.emit(progress)
        chart_data_sub.append(funcs[4]())
        chart_data.append(chart_data_sub)
        progress += 1
        progress_tracker.emitter.emit(progress)

    return chart_data


def compute_data_quality2(data, tmc=None, progress_tracker=None):
    # if progress_tracker is not None:
    #     progress_tracker.bar.setTextVisible(True)
    #     progress_tracker.bar.setMaximum(8)

    chart_data = []
    progress = 0
    if progress_tracker is not None:
        # print(data)
        if tmc is not None:
            agg_data = data[data['tmc_code'].isin(tmc)]
            agg_data = agg_data.groupby(['tmc_code', 'Year', 'Month', 'weekday', 'Hour', 'Date']).agg(['count'])['speed'] / 12
        else:
            agg_data = data.groupby(['tmc_code', 'Year', 'Month', 'weekday', 'Hour', 'Date']).agg(['count'])['speed'] / 12
        progress_tracker.bar.setTextVisible(True)
        progress_tracker.bar.setMaximum(8)
        progress += 1
        progress_tracker.emitter.emit(progress)
        agg_data = agg_data['count'].groupby(['tmc_code', 'Year', 'Month', 'weekday', 'Hour']).agg([np_mean])['mean']
        progress += 1
        progress_tracker.emitter.emit(progress)
        wkdy_data = agg_data.groupby(['weekday']).agg([np_mean])['mean']
        # print(wkdy_data)
        chart_data.append(wkdy_data)
        progress += 1
        progress_tracker.emitter.emit(progress)
        tod_data = agg_data.groupby(['Hour']).agg([np_mean])['mean']
        # print(tod_data)
        chart_data.append(tod_data)
        progress += 1
        progress_tracker.emitter.emit(progress)
        tmc_data = agg_data.groupby(['tmc_code']).agg([np_mean])['mean']
        if tmc is not None:
            tmc_data = tmc_data.reindex(tmc)
        # print(tmc_data)
        chart_data.append(tmc_data)
        progress += 1
        progress_tracker.emitter.emit(progress)
        sp_data = agg_data.groupby(['Year', 'Month', 'weekday']).agg([np_mean])['mean']
        sp_data = sp_data.reset_index()
        sp_data.rename({"mean":"data_pct"}, axis='columns', inplace=True)
        progress += 1
        progress_tracker.emitter.emit(progress)
        # print(sp_data)
        chart_data_sub = []
        chart_data_sub.append(sp_data[sp_data['weekday'].isin([0, 1, 2, 3, 4])].groupby(['Year', 'Month']).agg([np_mean])['data_pct'].values)
        chart_data_sub[0].resize((chart_data_sub[0].shape[0],))
        # print(chart_data_sub[0])
        progress += 1
        progress_tracker.emitter.emit(progress)
        chart_data_sub.append(sp_data[sp_data['weekday'].isin([5, 6])].groupby(['Year', 'Month']).agg([np_mean])['data_pct'].values)
        chart_data_sub[1].resize((chart_data_sub[1].shape[0],))
        # print(chart_data_sub[1])
        progress += 1
        progress_tracker.emitter.emit(progress)
        chart_data.append(chart_data_sub)

    return chart_data


def compute_stage2(func_dict, dialog=None, progress_tracker=None):
    if progress_tracker is not None:
        progress_tracker.bar.setTextVisible(True)

    chart_data = []
    for func_type, func_list in func_dict.items():
        # if dialog is not None:
        #     print("Computing " + func_type + " analysis...")
        #     dialog.setWindowTitle("Computing " + func_type + " analysis...")
        if progress_tracker is not None:
            progress_tracker.bar.setMaximum(len(func_list))
        sub_chart_data = []
        progress = 0
        progress_tracker.emitter.emit(progress)
        if progress_tracker is not None:
            for func in func_list:
                sub_chart_data.append(func())
                progress += 1
                progress_tracker.emitter.emit(progress)
            chart_data.append(sub_chart_data)

    return chart_data


def compute_spatial_charts(func_list, progress_tracker=None):
    if progress_tracker is not None:
        progress_tracker.bar.setTextVisible(True)
        progress_tracker.bar.setMaximum(len(func_list)+1)

    chart_data = []
    progress = 0
    if progress_tracker is not None:
        for f in func_list:
            if f is not None:
                chart_data.append(f())
            else:
                chart_data.append(None)
            progress += 1
            progress_tracker.emitter.emit(progress)

    return chart_data


class LoadSpatialQT(QDialog):
    """
    Dialog with a Progress Bar marking the progress of loading the data.
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    def __init__(self, chart_panel, mainwindow, funcs):
        super().__init__(mainwindow)
        self.chart_panel = chart_panel
        self.progress_helper = ProgressHelper()
        self.funcs = funcs
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Initializing...')
        self.progress = QProgressBar(self)
        self.progress_helper.set_bar(self.progress)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.show()

        self.calc = SpatialLoadThread(self.chart_panel, self.funcs)
        self.calc.set_progress_helper(self.progress_helper)
        self.calc.countChanged.connect(self.on_count_changed)
        self.calc.start()

    def on_count_changed(self, value):
        if value < 0:
            self.accept()
            self.chart_panel.plot_data_updated()
        elif value == 1:
            self.setWindowTitle("Analyzing TMCs...")
            self.progress.setValue(value)
            pass
        else:
            self.progress.setValue(value)


def compute_temporal_charts(func_list, progress_tracker=None):
    if progress_tracker is not None:
        progress_tracker.bar.setTextVisible(True)
        progress_tracker.bar.setMaximum(5)

    chart_data = []
    progress = 0
    if progress_tracker is not None:
        for f in func_list:
            if f is not None:
                chart_data.append(f())
            else:
                chart_data.append(None)
            progress += 1
            progress_tracker.emitter.emit(progress)

    return chart_data


class LoadTemporalQT(QDialog):
    """
    Dialog with a Progress Bar marking the progress of loading the data.
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    def __init__(self, chart_panel, mainwindow, funcs):
        super().__init__(mainwindow)
        self.chart_panel = chart_panel
        self.progress_helper = ProgressHelper()
        self.funcs = funcs
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Initializing...')
        self.progress = QProgressBar(self)
        self.progress_helper.set_bar(self.progress)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.show()

        self.calc = TemporalLoadThread(self.chart_panel, self.funcs)
        self.calc.set_progress_helper(self.progress_helper)
        self.calc.countChanged.connect(self.on_count_changed)
        self.calc.start()

    def on_count_changed(self, value):
        if value < 0:
            self.accept()
            self.chart_panel.plot_data_updated()
        elif value == 1:
            self.setWindowTitle("Analyzing data...")
            self.progress.setValue(value)
        else:
            self.progress.setValue(value)


def extract_vals(date_str):
    # print(date_str)
    date, time = date_str.split(' ')
    [hour, minute, second] = [int(val) for val in time.split(':')]
    [year, month, day] = [int(val) for val in date.split('-')]
    day_type = datetime.datetime(year, month, day).weekday()
    ap = (hour * 12) + minute // 5
    return date, year, month, day, ap, day_type


def create_columns(data, is_case_study=False):
    if is_case_study is False:
        dates, years, months, days, aps, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(weekday)
    else:
        dates, years, months, days, aps, regions, weekday = zip(*data)
        return list(dates), list(years), list(months), list(days), list(aps), list(regions), list(weekday)
