"""
Module that houses some Qt-based data-loading classes.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QProgressBar
from DataHelper import Database
import datetime
import pandas as pd
import time


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
