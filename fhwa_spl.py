import sys
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QThread
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog, QDialog, QListWidget, QAbstractItemView, QVBoxLayout
from PyQt5.QtWidgets import QDialogButtonBox, QLineEdit
from mw_test import Ui_MainWindow
from viz import run_viz, run_viz_day
from viz_qt import DataLoadQT
from data_import import get_case_study_list, get_spm_study_list

from offline_viz import FourByFourPanel


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

        self.database = DataHelper()

        #self.web = QWebView()
        #self.container = ConnectionContainer()

        open_file_action = QAction('&Open', self)
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

        self.show()

    # def load_finished(self):
    #     self.ui.webView.page().mainFrame().addToJavaScriptWindowObject("container", self.container)

    # def load_browser(self):
    #     print('Action Triggered')
    #     f_name = QFileDialog.getOpenFileName(self, 'Open file', '', "HTML files (*.html)")
    #     print(f_name[0])
    #     self.ui.webView.loadFinished.connect(self.load_finished)
    #     self.ui.webView.load(QUrl('file:///' + f_name[0]))

    def load_reader(self):
        print('Action Triggered')
        f_name = QFileDialog.getOpenFileName(self, 'Open file', '', "HTML files (*.html)")
        print(f_name[0])
        self.ui.webView_2.load(QUrl('file:///' + f_name[0]))  # 'file:///C:/Users/ltrask/PycharmProjects/BrowserTest/index.html'

    def load_flask_chart(self):
        print('Action Triggered')
        self.ui.webView_3.load(QUrl(ROOT_URL))

    def update_chart(self):
        print('action triggered')
        self.ui.webView.page().mainFrame().evaluateJavaScript('transitionStacked()')

    def open_file(self):
        f_name = QFileDialog.getOpenFileName(self, 'Open file', '', "CSV files (*.csv)")
        print(f_name)
        print('done')

    def run_case_study(self):
        case_studies = get_case_study_list()
        case_study, ok = QInputDialog.getItem(self, "Case Study Selection", "Select the Case Study:", case_studies, 0, False)
        if ok:
            run_viz(case_studies.index(case_study) + 1)

    def select_case_study(self):
        case_studies = get_case_study_list()
        case_study, ok = QInputDialog.getItem(self, "Case Study Selection", "Select the Case Study:", case_studies, 0, False)
        return case_studies.index(case_study) + 1, ok

    def select_case_study_spm(self):
        case_studies = get_spm_study_list()
        case_study, ok = QInputDialog.getItem(self, "Case Study Selection", "Select the Case Study:", case_studies, 0, False)
        return case_studies.index(case_study) + 1, ok

    def extract_case_study(self):
        cs_idx, ok = self.select_case_study()
        if ok:
            self.database.set_active_subset(-1)
            DataLoadQT(self, cs_idx, [], print_csv=False, return_tt=False)

    def extract_case_study_spm(self):
        cs_idx, ok = self.select_case_study_spm()
        if ok:
            self.database.set_active_subset(-1)
            DataLoadQT(self, cs_idx, [], print_csv=False, return_tt=False)

    def load_mpl_charts(self, chart_panel_name):
        mpl_widget = FourByFourPanel(self.database.get_tmc_list(), self.database.data, self.database.tt_comp, self.database.available_days,
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

class DataHelper():
    def __init__(self):
        self.curr_cs_idx = -1
        self.curr_subset_idx = -1
        self.site_name = ''
        self.tmc_df = None
        self.data = None
        self.tt_comp = None
        self.available_days = None
        self.available_months = None
        self.titles = None
        self.tmc_subset = []

    def set_curr_cs_idx(self, index):
        self.curr_cs_idx = index

    def set_site_name(self, name):
        self.site_name = name

    def set_tmc_list(self, tmc_list):
        self.tmc_df = tmc_list

    def set_data(self, data):
        self.data = data

    def set_tt_comp(self, tt_comp):
        self.tt_comp = tt_comp

    def set_available_days(self, available_days):
        self.available_days = available_days

    def set_available_months(self, available_months):
        self.available_months = available_months

    def set_titles(self, titles):
        self.titles = titles

    def add_tmc_subset(self, tmc_subset):
        self.tmc_subset.append(tmc_subset)
        return len(self.tmc_subset) - 1

    def get_tmc_subset(self, subset_idx):
        if subset_idx < len(self.tmc_subset):
            return self.tmc_subset[subset_idx]
        else:
            return []

    def set_active_subset(self, subset_idx):
        self.curr_subset_idx = subset_idx

    def get_active_subset(self):
        return self.curr_subset_idx

    def get_tmc_list(self):
        if self.curr_subset_idx < 0:
            return self.tmc_df
        else:
            return self.tmc_df[self.tmc_df['tmc'].isin(self.tmc_subset[self.curr_subset_idx])]


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
