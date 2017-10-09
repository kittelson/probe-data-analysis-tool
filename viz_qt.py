from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QProgressBar
from data_import import create_case_study2, get_speed_contour_cs, get_spm_case_study
from DataHelper import Database
from viz import extract_vals2, create_columns, create_tt_analysis, create_tt_compare
from viz import extract_vals
import pandas as pd
import time


class ProgressHelper:
    def __init__(self):
        self.bar = None
        self.emitter = None

    def set_bar(self, bar):
        self.bar = bar

    def set_emitter(self, emitter):
        self.emitter = emitter


class DataLoadThread(QThread):
    """
    Loads and extracts the data with a QT progress bar
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    countChanged = pyqtSignal(int)
    progress_helper = None

    def __init__(self, main_window, case_study_idx, day_list, tmc_subset=None, print_csv=True, return_tt=True):
        QThread.__init__(self)
        self.main_window = main_window
        self.cs_idx = case_study_idx
        self.day_list = day_list
        self.tmc_subset = tmc_subset
        self.print_csv = print_csv
        self.return_tt = return_tt

    def set_progress_helper(self, progress_helper):
        self.progress_helper = progress_helper
        self.progress_helper.set_emitter(self.countChanged)

    def run(self):
        site_name, tmc_list, dfs, tt_comp, ad, am, titles = run_viz_day(self.cs_idx, self.day_list, tmc_subset=self.tmc_subset,
                                                                                print_csv=self.print_csv, return_tt=self.return_tt,
                                                                                progress_tracker=self.progress_helper)
        self.main_window.database.set_curr_cs_idx(self.cs_idx)
        self.main_window.database.set_site_name(site_name)
        if self.tmc_subset is None:
            self.main_window.database.set_tmc_list(tmc_list)
        self.main_window.database.set_data(dfs)
        self.main_window.database.set_tt_comp(tt_comp)
        self.main_window.database.set_available_days(ad)
        self.main_window.database.set_available_months(am)
        self.main_window.database.set_titles(titles)
        self.countChanged.emit(-1)


class DataLoadQT(QDialog):
    """
    Dialog that consists of a Progress Bar marking the progress of loading the data
    Adapted from: https://stackoverflow.com/documentation/pyqt5/9544/introduction-to-progress-bars#t=201709081442594430681
    """

    def __init__(self, main_window, case_study_idx, day_list, tmc_subset=None, subset_name='', print_csv=True, return_tt=True):
        super().__init__(main_window)
        self.main_window = main_window
        self.progress_helper = ProgressHelper()
        self.cs_idx = case_study_idx
        self.day_list = day_list
        self.tmc_subset = tmc_subset
        self.subset_name = subset_name
        self.print_csv = print_csv
        self.return_tt = return_tt
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Extracting Data')
        self.progress = QProgressBar(self)
        self.progress_helper.set_bar(self.progress)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        #self.progress.setMaximum(100)
        self.show()
        self.calc = DataLoadThread(self.main_window, self.cs_idx, self.day_list, tmc_subset=self.tmc_subset,
                                   print_csv=self.print_csv, return_tt=self.return_tt)
        self.calc.set_progress_helper(self.progress_helper)
        self.calc.countChanged.connect(self.onCountChanged)
        self.calc.start()

    def onCountChanged(self, value):
        if value < 0:
            if self.tmc_subset is not None:
                chart_name = self.subset_name
            else:
                chart_name = self.main_window.database.site_name
            self.main_window.load_mpl_charts(chart_name)
            self.hide()
        else:
            self.progress.setValue(value)


def run_viz_day(case_study_idx, day_list, tmc_subset=None, print_csv=True, return_tt=True, progress_tracker=None):
    fname, tmc, site_name, start_date, open_date1, open_date2, end_date = create_case_study2(case_study_idx)
    #fname, tmc, site_name, start_date, open_date1, open_date2, end_date = get_spm_case_study(case_study_idx)

    title1 = site_name + ':  Period #1 (' + start_date.strftime('%m/%d/%Y') + '-' + open_date1.strftime('%m/%d/%Y') + ')'
    title2 = site_name + ':  Interim (' + open_date1.strftime('%m/%d/%Y') + '-' + open_date2.strftime('%m/%d/%Y') + ')'
    title3 = site_name + ':  Period #2 (' + open_date2.strftime('%m/%d/%Y') + '-' + end_date.strftime('%m/%d/%Y') + ')'
    #title3 = site_name + ':  2016 vs 2017'

    # Reading and dropping all null values
    df = pd.read_csv(fname)  # , parse_dates=['measurement_tstamp']
    df = df[df.speed.notnull()]

    # Filtering TMCs if subset specified
    if tmc_subset is not None:
        df = df[df['tmc_code'].isin(tmc_subset)]
        tmc = tmc[tmc['tmc'].isin(tmc_subset)]

    if progress_tracker is not None:
        progress_tracker.bar.setTextVisible(True)
        progress_tracker.bar.setMaximum(len(df) // 10000)
        print(str(len(df) // 10000))
    time1 = time.time()
    #new_mat = [extract_vals2(dStr, open_date1, open_date2) for dStr in df['measurement_tstamp']]
    new_mat = []
    progress = 0
    view_progress = 0
    if progress_tracker is not None:
        for dStr in df['measurement_tstamp']:
            new_mat.append(extract_vals2(dStr, open_date1, open_date2))
            progress += 1
            if progress == 10000:
                view_progress += 1
                progress = 0
                progress_tracker.emitter.emit(view_progress)
        progress_tracker.bar.setRange(0, 0)
        progress_tracker.emitter.emit(0)
        progress_tracker.bar.setTextVisible(False)
    else:
        new_mat = [extract_vals2(dStr, open_date1, open_date2) for dStr in df['measurement_tstamp']]
    # open_date1_tstamp = pd.Timestamp(open_date1)
    # open_date2_tstamp = pd.Timestamp(open_date2)
    # new_mat = [extract_vals3(ts, open_date1_tstamp, open_date2_tstamp) for ts in df['measurement_tstamp']]
    time2 = time.time()
    print('Mat Creation: ' + str(time2 - time1))
    time1 = time.time()
    #df['Date'], df['AP'], df['region'], df['weekday'] = create_columns(new_mat, is_case_study=True)
    df['Date'], df['Year'], df['Month'], df['Day'], df['AP'], df['region'], df['weekday'] = create_columns(new_mat, is_case_study=True)
    time2 = time.time()
    print('DF Creation: '+str(time2-time1))

    # Filtering to selected set of days
    if len(day_list) > 0:
        df = df[df['weekday'].isin(day_list)]

    time1 = time.time()
    # Creating Before Data
    df1 = df[df.region == 1]

    # Creating Interim Data
    df2 = df[df.region == 2]

    # Creating After/Active PTSU Data
    df3 = df[df.region == 3]
    time2 = time.time()
    print('DF Region Filtering: ' + str(time2 - time1))

    time1 = time.time()
    if return_tt:
        tt1 = create_tt_analysis(df1)
        tt2 = create_tt_analysis(df2)
        tt3 = create_tt_analysis(df3)
        # Creating before/after travel time percentile comparison
        tt_comp = create_tt_compare(tt1, tt3)
        if print_csv:
            tt_comp.to_csv('static/tt_pct_comp.csv')
        return [tt1, tt2, tt3], tt_comp, df['weekday'].unique().tolist(), [title1, title2, title3]
    time2 = time.time()
    print('Run Viz TT Analysis: ' + str(time2 - time1))

    print('done')
    return site_name, tmc, [df1, df2, df3], None, df['weekday'].unique().tolist(), df['Month'].unique().tolist(), [title1, title2, title3]


def create_speed_contour(case_study_idx, day_list, tmc_subset=None, print_csv=True, return_tt=True, progress_tracker=None):
    fname, tmc, site_name, start_date, open_date1, open_date2, end_date = get_speed_contour_cs(case_study_idx)

    title1 = site_name + ' (EB):  ' + start_date.strftime('%m/%d/%Y') + '-' + open_date1.strftime('%m/%d/%Y')
    title2 = site_name + ' (EB):  ' + open_date1.strftime('%m/%d/%Y') + '-' + open_date2.strftime('%m/%d/%Y')
    title3 = site_name + ' (EB):  ' + open_date2.strftime('%m/%d/%Y') + '-' + end_date.strftime('%m/%d/%Y')

    # Reading and dropping all null values
    df = pd.read_csv(fname)  # , parse_dates=['measurement_tstamp']
    df = df[df.speed.notnull()]

    # Filtering TMCs if subset specified
    tmc_subset = tmc[tmc['direction']=='EASTBOUND']['tmc'].tolist()
    if tmc_subset is not None:
        df = df[df['tmc_code'].isin(tmc_subset)]
        tmc = tmc[tmc['tmc'].isin(tmc_subset)]

    if progress_tracker is not None:
        progress_tracker.bar.setTextVisible(True)
        progress_tracker.bar.setMaximum(len(df) // 10000)
        print(str(len(df) // 10000))
    time1 = time.time()
    #new_mat = [extract_vals2(dStr, open_date1, open_date2) for dStr in df['measurement_tstamp']]
    new_mat = []
    progress = 0
    view_progress = 0
    if progress_tracker is not None:
        for dStr in df['measurement_tstamp']:
            new_mat.append(extract_vals2(dStr, open_date1, open_date2))
            progress += 1
            if progress == 10000:
                view_progress += 1
                progress = 0
                progress_tracker.emitter.emit(view_progress)
        progress_tracker.bar.setRange(0, 0)
        progress_tracker.emitter.emit(0)
        progress_tracker.bar.setTextVisible(False)
    else:
        new_mat = [extract_vals2(dStr, open_date1, open_date2) for dStr in df['measurement_tstamp']]
    # open_date1_tstamp = pd.Timestamp(open_date1)
    # open_date2_tstamp = pd.Timestamp(open_date2)
    # new_mat = [extract_vals3(ts, open_date1_tstamp, open_date2_tstamp) for ts in df['measurement_tstamp']]
    time2 = time.time()
    print('Mat Creation: ' + str(time2 - time1))
    time1 = time.time()
    df['Date'], df['AP'], df['region'], df['weekday'] = create_columns(new_mat, is_case_study=True)
    time2 = time.time()
    print('DF Creation: '+str(time2-time1))

    # Filtering to selected set of days
    if len(day_list) > 0:
        df = df[df['weekday'].isin(day_list)]

    time1 = time.time()
    # Creating Before Data
    df1 = df[df.region == 1]

    # Creating Interim Data
    df2 = df[df.region == 2]

    # Creating After/Active PTSU Data
    df3 = df[df.region == 3]
    time2 = time.time()
    print('DF Region Filtering: ' + str(time2 - time1))

    time1 = time.time()
    if return_tt:
        tt1 = create_tt_analysis(df1)
        tt2 = create_tt_analysis(df2)
        tt3 = create_tt_analysis(df3)
        # Creating before/after travel time percentile comparison
        tt_comp = create_tt_compare(tt1, tt3)
        if print_csv:
            tt_comp.to_csv('static/tt_pct_comp.csv')
        return [tt1, tt2, tt3], tt_comp, df['weekday'].unique().tolist(), [title1, title2, title3]
    time2 = time.time()
    print('Run Viz TT Analysis: ' + str(time2 - time1))

    print('done')
    return site_name, tmc, [df1, df2, df3], None, df['weekday'].unique().tolist(), [title1, title2, title3]


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

