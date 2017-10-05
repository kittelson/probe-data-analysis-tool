import sys
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QThread, Qt, QDate
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog, QDialog, QListWidget, QAbstractItemView, QVBoxLayout
from PyQt5.QtWidgets import QDialogButtonBox, QLineEdit, QTreeWidgetItem
from mw_test import Ui_MainWindow
from viz import run_viz, run_viz_day
from viz_qt import DataLoadQT, LoadProjectQT
from data_import import get_case_study_list, get_spm_study_list
from DataHelper import DataHelper
from offline_viz import FourByFourPanel, FourByFourPanelTimeTime

PORT = 5000
ROOT_URL = 'http://localhost:{}'.format(PORT)


class FlaskThread(QThread):
    def __init__(self, application):
        QThread.__init__(self)
        self.application = application

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=PORT)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.project = None
        self.database = DataHelper()

        #self.web = QWebView()
        #self.container = ConnectionContainer()

        new_file_action = QAction('&New Project', self)
        new_file_action.setShortcut('Ctrl+N')
        new_file_action.setToolTip('Create New Project File')
        new_file_action.triggered.connect(self.create_new)
        self.ui.menuFile.addAction(new_file_action)
        self.ui.pushButton.clicked.connect(self.create_new)

        open_file_action = QAction('&Open Project', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.setToolTip('Open Project File')
        open_file_action.triggered.connect(self.open_file)
        self.ui.menuFile.addAction(open_file_action)

        run_case_action = QAction('&Run Case Study', self)
        run_case_action.setShortcut('Ctrl+R')
        run_case_action.setToolTip('Select and Run Case Study')
        run_case_action.triggered.connect(self.run_case_study)
        self.ui.menuAnalyze.addAction(run_case_action)

        # load_chart_action = QAction('&Load Chart', self)
        # load_chart_action.setShortcut('Ctrl+L')
        # load_chart_action.setToolTip('Load WebBrowser')
        # load_chart_action.triggered.connect(self.load_browser)
        # self.ui.menuAnalyze.addAction(load_chart_action)

        # load_reader_action = QAction('&Load Reader Chart', self)
        # load_reader_action.setToolTip('Load WebBrowser')
        # load_reader_action.triggered.connect(self.load_reader)
        # self.ui.menuAnalyze.addAction(load_reader_action)
        #
        load_flask_action = QAction('&Load via Flask', self)
        load_flask_action.setToolTip('Load WebBrowser')
        load_flask_action.triggered.connect(self.load_flask_chart)
        self.ui.menuAnalyze.addAction(load_flask_action)

        load_mpl_action = QAction('&Load Offline Chart', self)
        load_mpl_action.setToolTip('Load Charts in offline mode.')
        load_mpl_action.triggered.connect(self.extract_case_study)
        self.ui.menuAnalyze.addAction(load_mpl_action)

        load_mpl_spm_action = QAction('&Load SPM Chart', self)
        load_mpl_spm_action.setToolTip('Load Charts for SPM Case Study.')
        load_mpl_spm_action.triggered.connect(self.extract_case_study_spm)
        self.ui.menuAnalyze.addAction(load_mpl_spm_action)

        edit_tmcs_action = QAction('&Create TMC Subset', self)
        edit_tmcs_action.setToolTip('Edit the set of TMCs')
        edit_tmcs_action.triggered.connect(self.edit_tmcs)
        self.ui.menuAnalyze.addAction(edit_tmcs_action)

        # update_chart_action = QAction('&Update Chart', self)
        # update_chart_action.setShortcut('Ctrl+K')
        # update_chart_action.setToolTip('Update WebBrowser')
        # update_chart_action.triggered.connect(self.update_chart)
        # self.ui.menuAnalyze.addAction(update_chart_action)

        self.ui.add_range_button.clicked.connect(self.add_date_range)
        self.ui.del_range_button.clicked.connect(self.del_date_range)

        #self.ui.create_charts_button.clicked.connect(self.load_extra_time_charts)
        self.ui.create_charts_button.clicked.connect(self.load_time_time_charts)

        self.show()

    # def load_finished(self):
    #     self.ui.webView.page().mainFrame().addToJavaScriptWindowObject("container", self.container)

    # def load_browser(self):
    #     print('Action Triggered')
    #     f_name = QFileDialog.getOpenFileName(self, 'Open file', '', "HTML files (*.html)")
    #     print(f_name[0])
    #     self.ui.webView.loadFinished.connect(self.load_finished)
    #     self.ui.webView.load(QUrl('file:///' + f_name[0]))

    # def load_reader(self):
    #     print('Action Triggered')
    #     f_name = QFileDialog.getOpenFileName(self, 'Open file', '', "HTML files (*.html)")
    #     print(f_name[0])
    #     self.ui.webView_2.load(QUrl('file:///' + f_name[0]))  # 'file:///C:/Users/ltrask/PycharmProjects/BrowserTest/index.html'

    def load_flask_chart(self):
        print('Action Triggered')
        self.ui.webView_3.load(QUrl(ROOT_URL))

    def update_chart(self):
        print('action triggered')
        self.ui.webView.page().mainFrame().evaluateJavaScript('transitionStacked()')

    def create_new(self):
        project_dir_name = QFileDialog.getExistingDirectory(self, "Select Project/Data Folder")
        tokens = project_dir_name.split('/')
        tmc_file_name = project_dir_name + '/tmc_identification.csv'
        data_file_name = project_dir_name + '/' + tokens[-1] + '.csv'
        project_name, ok = QInputDialog.getText(self, 'Project Name', 'Enter a project name:', QLineEdit.Normal, 'New Project')
        if ok:
            self.project = Project(project_name, project_dir_name, self)
            self.project.set_tmc_file(tmc_file_name)
            self.project.set_data_file(data_file_name)
            self.project.load()

    def add_project(self, project):
        # Updating Tool Labels
        # self.ui.label.setText(project.get_name)
        # Updating Dataset Tree
        if self.ui.treeWidget_3.model().hasChildren():
            self.ui.treeWidget_3.model().removeRows(0, self.ui.treeWidget_3.model().rowCount())
        proj_item = QTreeWidgetItem(self.ui.treeWidget_3)
        proj_item.setText(0, project.get_name())
        # proj_item.setFlags(proj_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        directions = project.database.get_directions()
        for dir in directions:
            child = QTreeWidgetItem(proj_item)
            child.setText(0, dir)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setCheckState(0, Qt.Unchecked)
        # proj_item.child(0).setCheckState(0, Qt.Checked)

        # Updating Data Types
        self.ui.listWidget_4.addItem('Start Date: ' + project.database.get_first_date())
        self.ui.listWidget_4.addItem('End Date: ' + project.database.get_last_date())
        self.ui.listWidget_4.addItem('Weekdays: ' + project.database.get_available_weekdays(as_string=True))
        self.ui.listWidget_4.addItem('Weekends: ' + project.database.get_available_weekends(as_string=True))
        self.ui.listWidget_4.addItem('Months: ' + project.database.get_available_months(as_string=True))

        # Updating analysis types
        # Updating date ranges
        s_date = project.database.get_first_date().split('-')
        e_date = project.database.get_last_date().split('-')
        s_qdate = QDate(int(s_date[0]), int(s_date[1]), int(s_date[2]))
        e_qdate = QDate(int(e_date[0]), int(e_date[1]), int(e_date[2]))
        self.ui.dateEdit_start.setDate(s_qdate)
        self.ui.dateEdit_start.setDateRange(s_qdate, e_qdate)
        self.ui.dateEdit_end.setDate(e_qdate)
        self.ui.dateEdit_end.setDateRange(s_qdate, e_qdate)

    def open_file(self):
        f_name = QFileDialog.getOpenFileName(self, 'Open file', '', "CSV files (*.csv)")
        print(f_name)
        print('done')

    def add_date_range(self):
        start_date = self.ui.dateEdit_start.date()
        end_date = self.ui.dateEdit_end.date()
        # print(start_date.toString())
        # print(end_date.toString())
        self.project.add_date_range([start_date, end_date])
        self.update_date_range_tree()

    def update_date_range_tree(self):
        if self.ui.treeWidget.model().hasChildren():
            self.ui.treeWidget.model().removeRows(0, self.ui.treeWidget.model().rowCount())
        range_idx = 1
        for d_range in self.project.get_date_ranges():
            range_item = QTreeWidgetItem(self.ui.treeWidget)
            range_item.setText(0, 'Period ' + str(range_idx))
            range_item.setFlags(range_item.flags() | Qt.ItemIsUserCheckable)
            child1 = QTreeWidgetItem(range_item)
            child1.setText(0, d_range[0].toString())
            child2 = QTreeWidgetItem(range_item)
            child2.setText(0, d_range[1].toString())
            range_idx += 1
            # proj_item.child(0).setCheckState(0, Qt.Checked)

    def del_date_range(self):
        model_indexes = self.ui.treeWidget.selectionModel().selectedIndexes()
        indexes = [m_idx.row() for m_idx in model_indexes]
        for d_range_idx in indexes:
            d_range = self.project.del_date_range(d_range_idx)
        self.update_date_range_tree()

    def run_case_study(self):
        case_studies = get_case_study_list()
        case_study, ok = QInputDialog.getItem(self, "Case Study Selection", "Select the Case Study:", case_studies, 0, False)
        if ok:
            run_viz(case_studies.index(case_study) + 1)

    def select_case_study(self):
        case_studies = get_case_study_list()
        case_study, ok = QInputDialog.getItem(self, "Case Study Selection", "Select the Case Study:", case_studies, 0, False)
        return case_studies.index(case_study) + 1, ok

    def extract_case_study(self):
        cs_idx, ok = self.select_case_study()
        if ok:
            self.database.set_active_subset(-1)
            DataLoadQT(self, cs_idx, [], print_csv=False, return_tt=False)

    def select_case_study_spm(self):
        case_studies = get_spm_study_list()
        case_study, ok = QInputDialog.getItem(self, "Case Study Selection", "Select the Case Study:", case_studies, 0, False)
        return case_studies.index(case_study) + 1, ok

    def extract_case_study_spm(self):
        cs_idx, ok = self.select_case_study_spm()
        if ok:
            self.database.set_active_subset(-1)
            DataLoadQT(self, cs_idx, [], print_csv=False, return_tt=False)

    def load_mpl_charts(self, chart_panel_name):
        mpl_widget = FourByFourPanel(self.database.get_tmc_list(),
                                     self.database.data,
                                     self.database.tt_comp,
                                     self.database.available_days,
                                     self.database.titles)
        new_tab_index = self.ui.tabWidget.addTab(mpl_widget, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)

    def generate_subset_charts(self, subset_idx, chart_name):
        self.database.set_active_subset(subset_idx)
        DataLoadQT(self, self.database.curr_cs_idx, [],
                   tmc_subset=self.database.get_tmc_subset(subset_idx),
                   subset_name=chart_name,
                   print_csv=False,
                   return_tt=False)

    def load_extra_time_charts(self):
        chart_panel_name = self.project.get_name() + ' Extra Time Charts'
        df = self.project.database.get_data()
        dr1 = self.project.get_date_range(0)
        df_period1 = df[(df['Date'] >= dr1[0].toString('yyyy-MM-dd')) & (df['Date'] <= dr1[1].toString('yyyy-MM-dd'))]
        dr2 = self.project.get_date_range(1)
        df_period2 = df[(df['Date'] > dr2[0].toString('yyyy-MM-dd')) & (df['Date'] < dr2[1].toString('yyyy-MM-dd'))]
        mpl_widget = FourByFourPanel(self.project.database.get_tmcs(),
                                     [df_period1, None, df_period2],
                                     None,
                                     self.project.database.get_available_days(),
                                     ['Period 1: ' + dr1[0].toString('yyyy-MM-dd') + ' to ' + dr1[1].toString('yyyy-MM-dd'),
                                      'Period 2: ',
                                      'Period 2: ' + dr2[0].toString('yyyy-MM-dd') + ' to ' + dr2[1].toString('yyyy-MM-dd')])
        new_tab_index = self.ui.tabWidget.addTab(mpl_widget, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)

    def load_time_time_charts(self):
        chart_panel_name = self.project.get_name() + ' Time / Time Charts'
        df = self.project.database.get_data()
        # dr1 = self.project.get_date_range(0)
        # df_period1 = df[(df['Date'] >= dr1[0].toString('yyyy-MM-dd')) & (df['Date'] <= dr1[1].toString('yyyy-MM-dd'))]
        # dr2 = self.project.get_date_range(1)
        # df_period2 = df[(df['Date'] > dr2[0].toString('yyyy-MM-dd')) & (df['Date'] < dr2[1].toString('yyyy-MM-dd'))]
        mpl_widget = FourByFourPanelTimeTime(self.project.database.get_tmcs(),
                                     [df, None, None],
                                     None,
                                     self.project.database.get_available_days(),
                                     ['Period 1: ',
                                      'Period 2: ',
                                      'Period 3: '])
        new_tab_index = self.ui.tabWidget.addTab(mpl_widget, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)

    def edit_tmcs(self):
        if self.database.tmc_df is not None:
            TMCList(self, self.database.tmc_df)


class TMCList(QDialog):
    def __init__(self, main_window, tmc_list):
        super().__init__(main_window)
        self.main_window = main_window
        self.tmc_list = tmc_list
        self.list_widget = QListWidget(self)
        self.initUI()

    def initUI(self):
        accum = 0
        for row in self.tmc_list.iterrows():
            accum += row[1]['miles']
            self.list_widget.addItem(row[1]['tmc'] + ',\t\t' + '{:1.1f}'.format(accum) + ',\t' + '{:1.1f}'.format(row[1]['miles']) + ',\t' + row[1]['intersection'])
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setWindowTitle('Select the TMC Set')
        self.button_box = QDialogButtonBox(self)
        self.button_box.setStandardButtons(QDialogButtonBox.Apply | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.ok_press)
        self.button_box.rejected.connect(self.close_press)
        self.button_box.clicked.connect(self.handleButtonClick)
        self.vlo = QVBoxLayout(self)
        self.vlo.addWidget(self.list_widget)
        self.vlo.addWidget(self.button_box)
        self.resize(600, 800)
        self.show()

    def handleButtonClick(self, button):
        sb = self.button_box.standardButton(button)
        if sb == QDialogButtonBox.Apply:
            self.apply_press()

    def apply_press(self):
        if len(self.list_widget.selectedIndexes()) > 0:
            tmc_ss = [self.tmc_list['tmc'][tmc_id.row()] for tmc_id in self.list_widget.selectedIndexes()]
            subset_idx = self.main_window.database.add_tmc_subset(tmc_ss)
            tab_name, ok = QInputDialog.getText(self.main_window, 'Enter Subset Name', 'Please specify the name of the TMC Subset',
                                                QLineEdit.Normal, self.main_window.database.site_name)
            if ok:
                self.main_window.generate_subset_charts(subset_idx, tab_name)
                self.close()

    def ok_press(self):
        print('accepted')

    def close_press(self):
        self.close()


class Project:
    def __init__(self, project_name, directory, main_window):
        self.main_window = main_window
        self._project_name = project_name
        self._project_dir = directory
        self._tmc_file_name = None
        self._data_file_name = None
        self.database = None
        self._date_ranges = []

    def set_name(self, new_name):
        self._project_name = new_name

    def get_name(self):
        return self._project_name

    def set_tmc_file(self, new_name):
        self._tmc_file_name = new_name

    def get_tmc_file_name(self):
        return self._tmc_file_name

    def set_data_file(self, new_name):
        self._data_file_name = new_name

    def get_data_file_name(self):
        return self._data_file_name

    def add_date_range(self, new_date_range):
        self._date_ranges.append(new_date_range)

    def del_date_range(self, index):
        return self._date_ranges.pop(index)

    def get_date_ranges(self):
        return self._date_ranges

    def get_date_range(self, index):
        return self._date_ranges[index]

    def load(self):
        LoadProjectQT(self.main_window, create_database=True, print_csv=False)

    def loaded(self):
        self.main_window.add_project(self)

class ConnectionContainer(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.manager = None

    def set_manager(self, manager):
        self.manager = manager

    @pyqtSlot(float)
    def change_page(self, page):
        print("changed page: " + str(page))


def provide_gui_for(application):
    qt_app = QApplication(sys.argv)
    web_app = FlaskThread(application)
    web_app.start()

    qt_app.aboutToQuit.connect(web_app.terminate)
    mw = MainWindow()
    return qt_app.exec_()

if __name__ == '__main__':
    from fhwa_spl_flask import app
    sys.exit(provide_gui_for(app))
