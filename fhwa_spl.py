"""
Effectively the “main” class of the program
Includes code for the MainWindow application
Also defines the core Project class
Has leftover code defining the FlaskThread for potential future web/d3js visualizations
"""


import sys
import os
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QThread, Qt, QDate
# from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QDialog, QFormLayout, QDialogButtonBox, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QLineEdit, QTreeWidgetItem, QWidget, QLabel, QColorDialog, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QColor, QFont
from mainwindow import Ui_MainWindow
from chart_panel_options import Ui_Dialog as Ui_CPD
from Stage2GridPanel import Stage2GridPanel
from DQGridPanel import DataQualityGridPanel
# from mpl_panels import ChartGridPanel, SpatialGridPanel
from Stage1Panel import Stage1GridPanel, SpatialGridPanel
from chart_defaults import ChartOptions, SPEED_BIN_DEFAULTS, generate_color_button_style, CHART1_TYPES
# import sql_helper
# from chart_defaults import generate_vega_lite
from DataHelper import Project
from ImportHelper import ImportDialog

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

        self.dq_chart_panel = None
        self.chart_panel_spatial = None
        self.chart_panel1_3 = None
        self.chart_panel1_4 = None
        self.chart_panel2 = None
        self.stage2panel = None
        self.summary_panel = None
        self.summ_table1 = None
        self.summ_table2 = None

        self.map_exists = False
        self.minimap_exists = False
        self.map_tmc_to_pl_index = dict()
        #self.web = QWebView()
        #self.container = ConnectionContainer()

        new_file_action = QAction('&New Project', self)
        new_file_action.setShortcut('Ctrl+N')
        new_file_action.setToolTip('Create New Project File')
        new_file_action.triggered.connect(self.create_new)
        self.ui.menuFile.addAction(new_file_action)
        self.ui.pushButton_new_proj.clicked.connect(self.create_new)

        open_file_action = QAction('&Open Project', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.setToolTip('Open Project File')
        open_file_action.triggered.connect(self.open_sql_project)
        self.ui.menuFile.addAction(open_file_action)

        self.ui.menuFile.addSeparator()
        self.edit_project_info_action = QAction('&Edit Project Info', self)
        self.edit_project_info_action.setShortcut('Ctrl+I')
        self.edit_project_info_action.setToolTip('Edit Project Information')
        self.edit_project_info_action.triggered.connect(self.edit_project_info)
        self.ui.menuFile.addAction(self.edit_project_info_action)
        self.edit_project_info_action.setEnabled(False)
        self.ui.menuFile.addSeparator()

        exit_app_action = QAction('&Exit', self)
        exit_app_action.setShortcut(('Ctrl+Q'))
        exit_app_action.setToolTip('Exit Program')
        exit_app_action.triggered.connect(self.close)
        self.ui.menuFile.addAction(exit_app_action)

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
        # self.ui.menuAnalyze.addAction(load_flask_action)

        self.load_map_action = QAction('&Load Map', self)
        self.load_map_action.setToolTip('Load Web Map of TMC locations')
        self.load_map_action.triggered.connect(self.load_map)
        self.ui.menuAnalyze.addAction(self.load_map_action)
        self.load_map_action.setEnabled(False)

        self.toggle_floating_map_action = QAction('&Toggle Floating Map', self)
        self.toggle_floating_map_action.setToolTip('Pop out or dock map window.')
        self.toggle_floating_map_action.triggered.connect(self.toggle_floating_map)
        self.ui.menuAnalyze.addAction(self.toggle_floating_map_action)
        self.toggle_floating_map_action.setEnabled(False)

        # self.chart1_options_action = QAction('&Chart 1 Options', self)
        # self.chart1_options_action.setToolTip('Configure the Chart Panel 1 Options')
        # self.chart1_options_action.triggered.connect(self.edit_chart1_options)
        # self.chart1_options_action.setEnabled(False)
        # self.ui.menuChartOptions.addAction(self.chart1_options_action)
        self.ui.menuChartOptions.setDisabled(True)

        # self.create_table_action = QAction('&Create Summary Table', self)
        # self.create_table_action.setToolTip('Temporary Option')
        # self.create_table_action.triggered.connect(self.create_summary_table)
        # self.ui.menuAnalyze.addAction(self.create_table_action)

        self.ui.tabWidget.currentChanged.connect(self.tab_select_changed)

        self.ui.add_range_button.clicked.connect(self.add_date_range)
        self.ui.del_range_button.clicked.connect(self.del_date_range)

        self.ui.create_charts_button.clicked.connect(self.load_extra_time_charts)

        # self.ui.pushButton_first_chart.clicked.connect(self.create_chart_panel1)
        # self.ui.pushButton_first_chart.setText('Load Spatial Charts')
        self.ui.pushButton_first_chart.clicked.connect(self.load_spatial_charts)
        self.ui.pushButton_first_chart.setDisabled(True)

        self.ui.pushButton_sec_chart.clicked.connect(self.create_chart_panel1)
        self.ui.pushButton_sec_chart.setDisabled(True)

        self.ui.pushButton_open_proj.setEnabled(False)
        self.ui.pushButton_exit.clicked.connect(self.close)

        self.ui.create_charts_button.setEnabled(False)
        self.ui.del_range_button.setEnabled(False)

        f_name = os.path.realpath('templates/map_instructions.html')
        self.ui.webView_map.load(QUrl('file:///' + f_name.replace('\\', '/')))
        f_name = os.path.realpath('templates/minimap_instructions.html')
        self.ui.webView_minimap.load(QUrl('file:///' + f_name.replace('\\', '/')))

        self.ui.pushButton_5.clicked.connect(self.generate_summary_table)

        for item_idx in range(1, 7):
            self.ui.toolBox.setItemEnabled(item_idx, False)

        self.showMaximized()

    # def load_finished(self):
    #     self.ui.webView_map.page().mainFrame().addToJavaScriptWindowObject("container", self.container)

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

    def tab_select_changed(self):
        if self.ui.tabWidget.currentIndex() > 1 and self.ui.tabWidget.currentIndex() < 6:
            self.ui.toolBox.setCurrentIndex(self.ui.tabWidget.currentIndex() - 2)
        elif self.ui.tabWidget.currentIndex() >= 6:
            self.ui.toolBox.setCurrentIndex(5)

    def load_flask_chart(self):
        # Example of how to load a chart via Flask
        # self.ui.webView_3.load(QUrl(ROOT_URL))
        self.ui.webView_map.load(QUrl(ROOT_URL))

    def update_chart(self):
        # Not In Use, but example of how to fire javascript function
        print('action triggered')
        # self.ui.webView.page().mainFrame().evaluateJavaScript('transitionStacked()')
        # self.ui.webView_map.page().runJavaScript()
        # self.ui.webView_map.page().mainFrame().evaluateJavaScript('placeTMC(38.8016796, -77.5148428, test)')

    def load_map_chart(self, create_plots=False):
        if self.project is not None:
            pass

    def load_map(self):
        f_name = os.path.realpath('templates/map_gen.html')
        self.ui.webView_map.loadFinished.connect(self.map_loaded)
        self.ui.webView_map.load(QUrl('file:///' + f_name.replace('\\', '/')))

    def map_loaded(self):
        self.map_exists = True
        self.toggle_floating_map_action.setEnabled(True)
        self.load_minimap()

    def load_minimap(self):
        f_name = os.path.realpath('templates/map_gen.html')
        self.ui.webView_minimap.loadFinished.connect(self.minimap_loaded)
        self.ui.webView_minimap.load(QUrl('file:///' + f_name.replace('\\', '/')))

    def minimap_loaded(self):
        self.minimap_exists = True
        self.add_tmcs_to_map()

    def reset_maps(self):
        if self.map_exists:
            self.ui.webView_map.page().runJavaScript('clear_map()')
        if self.minimap_exists:
            self.ui.webView_minimap.page().runJavaScript('clear_map()')
        self.add_tmcs_to_map()

    def add_tmcs_to_map(self):
        self.map_tmc_to_pl_index = dict()
        for index, tmc_info in self.project.get_tmc().iterrows():
            self.map_tmc_to_pl_index[tmc_info[Project.ID_TMC_CODE]] = index
            js_string = 'placeTMC('
            js_string = js_string + str(tmc_info[Project.ID_TMC_SLAT]) + ','
            js_string = js_string + str(tmc_info[Project.ID_TMC_SLON]) + ','
            js_string = js_string + str(tmc_info[Project.ID_TMC_ELAT]) + ','
            js_string = js_string + str(tmc_info[Project.ID_TMC_ELON]) + ','
            js_string = js_string + ' \'' + tmc_info[Project.ID_TMC_CODE] + '\'' + ','
            js_string = js_string + '\'black\''
            js_string = js_string + ')'
            # print(js_string)
            if self.map_exists:
                self.ui.webView_map.page().runJavaScript(js_string)
            if self.minimap_exists:
                self.ui.webView_minimap.page().runJavaScript(js_string)
        self.ui.webView_map.page().runJavaScript('updateBounds(-1)')
        self.ui.webView_minimap.page().runJavaScript('updateBounds(-1)')

    def highlight_tmc(self, tmc_idx):
        js_string = 'highlightTMC(' + str(tmc_idx) + ')'
        if self.map_exists:
            # self.ui.webView_map.page().runJavaScript(js_string)
            pass
        if self.minimap_exists:
            self.ui.webView_minimap.page().runJavaScript(js_string)

    def toggle_floating_map(self):
        # index = self.tab.indexOf(self.ui.webView_3)
        index = self.ui.tabWidget.indexOf(self.ui.tab_3)
        print(index)
        if index != -1:
            self.ui.tabWidget.removeTab(index)
            self.ui.tab_3.setWindowFlags(Qt.Window)
            self.ui.tab_3.show()
        else:
            self.ui.tab_3.setWindowFlags(Qt.Widget)
            self.ui.tabWidget.insertTab(1, self.ui.tab_3, 'Facility Map')
            # self.ui.tabWidget.addTab(self.ui.tab_3, 'Web Panel')
            pass

    def create_new(self):
        project_dir_name = QFileDialog.getExistingDirectory(self, "Select Project/Data Folder")
        if project_dir_name != '':
            dlg = ImportDialog(self, project_dir_name)
            # dlg.setModal(True)
            # dlg.show()

    def create_new_deprecated(self):
        project_dir_name = QFileDialog.getExistingDirectory(self, "Select Project/Data Folder")
        if project_dir_name != '':
            # tokens = project_dir_name.split('/')
            # tmc_file_name = project_dir_name + '/tmc_identification.csv'
            # data_file_name = project_dir_name + '/' + tokens[-1] + '.csv'
            # project_name, ok = QInputDialog.getText(self, 'Project Name', 'Enter a project name:', QLineEdit.Normal, 'New Project')
            # if ok:
            #     self.ui.label_project_name.setText(project_name)
            #     self.project = Project(project_name, project_dir_name, self)
            #     self.project.set_tmc_file(tmc_file_name)
            #     self.project.set_data_file(data_file_name)
            #     self.project.load()
            dlg = QDialog(self)
            dlg.setWindowTitle('Enter Project Information')
            l = QFormLayout(dlg)
            project_dir_label = QLabel('Project Data Location')
            project_dir_label.setFont(QFont("Times", weight=QFont.Bold))
            if len(project_dir_name) > 35:
                project_dir_label2 = QLabel('..' + project_dir_name[len(project_dir_name) - 35:])
            else:
                project_dir_label2 = QLabel(project_dir_name)
            project_name_label = QLabel('Project Name: ')
            project_name_label.setFont(QFont("Times", weight=QFont.Bold))
            project_name_input = QLineEdit('New Project')
            analyst_label = QLabel('Enter Analyst Name: ')
            analyst_label.setFont(QFont("Times", weight=QFont.Bold))
            analyst_input = QLineEdit('--')
            agency_label = QLabel('Enter Agency: ')
            agency_label.setFont(QFont("Times", weight=QFont.Bold))
            agency_input = QLineEdit('FHWA')
            state_label = QLabel('Enter State: ')
            state_label.setFont(QFont("Times", weight=QFont.Bold))
            state_input = QLineEdit('')
            loc_label = QLabel('Enter Location: ')
            loc_label.setFont(QFont("Times", weight=QFont.Bold))
            loc_input = QLineEdit('')
            l.addRow(project_dir_label, project_dir_label2)
            l.addRow(project_name_label, project_name_input)
            l.addRow(analyst_label, analyst_input)
            l.addRow(agency_label, agency_input)
            l.addRow(state_label, state_input)
            l.addRow(loc_label, loc_input)
            buttons = QDialogButtonBox(Qt.Horizontal, dlg)
            buttons.addButton(QDialogButtonBox.Ok)
            buttons.addButton(QDialogButtonBox.Cancel)
            buttons.accepted.connect(lambda: self.new_project_accepted(dlg, project_dir_name,
                                                                       project_name_input, analyst_input,
                                                                       agency_input, state_input, loc_input))
            buttons.rejected.connect(dlg.close)
            l.addWidget(buttons)
            project_name_input.selectAll()
            dlg.setModal(True)
            dlg.show()

    def new_project_accepted(self, dlg, project_dir_name, project_name_input, analyst_input, agency_input, state_input, loc_input):
        tokens = project_dir_name.split('/')
        tmc_file_name = project_dir_name + '/tmc_identification.csv'
        data_file_name = project_dir_name + '/' + tokens[-1] + '.csv'
        self.edit_project_info_action.setEnabled(True)
        self.project = Project(project_name_input.text(), project_dir_name, self)
        self.set_project_info(analyst_input.text(), agency_input.text(), state=state_input.text(), location=loc_input.text())
        self.project.set_tmc_file(tmc_file_name)
        self.project.set_data_file(data_file_name)
        self.project.load()
        dlg.close()

    def edit_project_info(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('Enter Project Information')
        l = QFormLayout(dlg)
        project_name_label = QLabel('Project Name: ')
        project_name_label.setFont(QFont("Times", weight=QFont.Bold))
        project_name_input = QLineEdit(self.project.get_name())
        analyst_label = QLabel('Enter Analyst Name: ')
        analyst_label.setFont(QFont("Times", weight=QFont.Bold))
        analyst_input = QLineEdit('--')
        agency_label = QLabel('Enter Agency: ')
        agency_label.setFont(QFont("Times", weight=QFont.Bold))
        agency_input = QLineEdit('FHWA')
        l.addRow(project_name_label, project_name_input)
        l.addRow(analyst_label, analyst_input)
        l.addRow(agency_label, agency_input)
        buttons = QDialogButtonBox(Qt.Horizontal, dlg)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.set_project_info(analyst_input.text(), agency_input.text()))
        buttons.rejected.connect(dlg.close)
        l.addWidget(buttons)
        dlg.setModal(True)
        dlg.show()

    def set_project_info(self, analyst, agency, state=None, location=None):
        self.project.set_analyst(analyst)
        self.project.set_agency(agency)
        if state is not None:
            self.project.set_state(state)
        if location is not None:
            self.project.set_location(location)
        self.update_project_info()

    def update_project_info(self):
        self.ui.label_project_name.setText(self.project.get_name())
        self.ui.label_analyst.setText(self.project.get_analyst())
        self.ui.label_agency.setText(self.project.get_agency())

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
        all_tmc = project.get_tmc(full_list=True)
        for dir in directions:
            tmc_curr_dir = all_tmc[all_tmc[Project.ID_TMC_DIR] == dir]
            child = QTreeWidgetItem(proj_item)
            child.setText(0, dir)
            # child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            # child.setCheckState(0, Qt.Unchecked)
            for sub_tmc in tmc_curr_dir[Project.ID_TMC_CODE]:
                sub_child = QTreeWidgetItem(child)
                sub_child.setText(0, sub_tmc)

        # Enabling components
        self.load_map_action.setEnabled(True)
        self.ui.pushButton_first_chart.setEnabled(True)
        self.ui.pushButton_sec_chart.setEnabled(True)
        # self.chart1_load_action.setEnabled(True)
        proj_item.setExpanded(True)
        # proj_item.child(0).setCheckState(0, Qt.Checked)  # Uncomment to make checkable
        # self.ui.treeWidget_3.itemChanged.connect(self.setup_tmc_list)  # Uncomment to enable check listening via "itemChanged"
        self.ui.treeWidget_3.itemSelectionChanged.connect(self.update_dq_chart)


        # Updating Data Types
        # self.ui.listWidget_4.addItem('Start Date: ' + project.database.get_first_date())
        # self.ui.listWidget_4.addItem('End Date: ' + project.database.get_last_date())
        # self.ui.listWidget_4.addItem('Weekdays: ' + project.database.get_available_weekdays(as_string=True))
        # self.ui.listWidget_4.addItem('Weekends: ' + project.database.get_available_weekends(as_string=True))
        # self.ui.listWidget_4.addItem('Months: ' + project.database.get_available_months(as_string=True))

        # Updating analysis types
        # Updating date ranges
        s_date = project.database.get_first_date(as_datetime=True)
        e_date = project.database.get_last_date(as_datetime=True)
        s_qdate = QDate(s_date.year, s_date.month, s_date.day)
        e_qdate = QDate(e_date.year, e_date.month, e_date.day)
        self.ui.dateEdit_start.setDate(s_qdate)
        self.ui.dateEdit_start.setDateRange(s_qdate, e_qdate)
        self.ui.dateEdit_end.setDate(e_qdate)
        self.ui.dateEdit_end.setDateRange(s_qdate, e_qdate)
        # Setting up tmc list
        self.setup_tmc_list(is_init=True)
        self.load_data_density_charts('1.1 - Data Availability')

    def open_file(self):
        f_name = QFileDialog.getOpenFileName(self, 'Open file', '', "CSV files (*.csv)")
        print(f_name)
        print('done')

    def open_sql_project(self):
        f_name, file_filter = QFileDialog.getOpenFileName(self, 'Select the Data File', '', "CSV files (*.csv)")
        if f_name:
            # sql_helper.create_sql_db_from_file(f_name)
            pass

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
            range_item.setExpanded(True)
            child1 = QTreeWidgetItem(range_item)
            child1.setText(0, d_range[0].toString())
            child2 = QTreeWidgetItem(range_item)
            child2.setText(0, d_range[1].toString())
            range_idx += 1
            # proj_item.child(0).setCheckState(0, Qt.Checked)

        num_ranges = len(self.project.get_date_ranges())
        if num_ranges == 2:
            self.ui.add_range_button.setDisabled(True)
        else:
            self.ui.add_range_button.setDisabled(False)
        if num_ranges > 0:
            self.ui.del_range_button.setDisabled(False)
            self.ui.create_charts_button.setDisabled(False)
        else:
            self.ui.del_range_button.setDisabled(True)
            self.ui.create_charts_button.setDisabled(True)

    def del_date_range(self):
        model_indexes = self.ui.treeWidget.selectionModel().selectedIndexes()
        indexes = [m_idx.row() for m_idx in model_indexes]
        for d_range_idx in indexes:
            d_range = self.project.del_date_range(d_range_idx)
        self.update_date_range_tree()

    def load_data_density_charts(self, chart_panel_name):
        # temp_widget = QWidget(self)
        # v_layout = QVBoxLayout(temp_widget)
        # v_layout.addWidget(QLabel('Placeholder for data "density" chart panel.  This will provide basic information about the dataset, as well as '
        #                           'show charts giving a glimpse at the availability of data in the dataset.'))
        reply = QMessageBox.question(self, 'Data Quality Analysis', "Conduct analysis of sample size and data availability?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.dq_chart_panel = DataQualityGridPanel(self.project)
            new_tab_index = self.ui.tabWidget.addTab(self.dq_chart_panel, chart_panel_name)
            self.ui.tabWidget.setCurrentIndex(new_tab_index)

    def load_extra_time_charts(self):
        chart_panel_name = '2 - Extra Time/Speed Bands'
        self.stage2panel = Stage2GridPanel(self.project)
        new_tab_index = self.ui.tabWidget.addTab(self.stage2panel, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)
        self.ui.toolBox.setItemEnabled(5, True)
        self.ui.toolBox.setItemEnabled(6, True)
        self.ui.pushButton_5.setEnabled(True)
        # pass

    def generate_summary_table(self):
        if self.stage2panel is not None:
            self.stage2panel.generate_summary_data()

    def create_summary_table(self):
        if self.summary_panel is None:
            # Project information panel
            info_panel = QWidget()
            l = QGridLayout(info_panel)
            project_name_label = QLabel('Project Name: ')
            project_name_label.setFont(QFont("Times", weight=QFont.Bold))
            project_name_input = QLabel(self.project.get_name())
            analyst_label = QLabel('Analyst: ')
            analyst_label.setFont(QFont("Times", weight=QFont.Bold))
            analyst_input = QLabel(self.project.get_analyst())
            agency_label = QLabel('Agency: ')
            agency_label.setFont(QFont("Times", weight=QFont.Bold))
            agency_input = QLabel(self.project.get_agency())
            state_label = QLabel('State: ')
            state_label.setFont(QFont("Times", weight=QFont.Bold))
            state_input = QLabel(self.project.get_state())
            loc_label = QLabel('Location: ')
            loc_label.setFont(QFont("Times", weight=QFont.Bold))
            loc_input = QLabel(self.project.get_location())
            # l.addRow(project_dir_label, project_dir_label2)
            l.addWidget(project_name_label, 0, 0)
            l.addWidget(project_name_input, 0, 1)
            l.addWidget(analyst_label, 1, 0)
            l.addWidget(analyst_input, 1, 1)
            l.addWidget(agency_label, 2, 0)
            l.addWidget(agency_input, 2, 1)
            l.addWidget(state_label, 3, 0)
            l.addWidget(state_input, 3, 1)
            l.addWidget(loc_label, 4, 0)
            l.addWidget(loc_input, 4, 1)

        print('here1')
        # Summary Table 1
        if self.summ_table1 is None:
            self.summ_table1 = QTableWidget()
        else:
            self.summ_table1.setRowCount(0)
        print('here2')
        self.summ_table1.setRowCount(9)
        self.summ_table1.setColumnCount(3)

        print('here3')
        self.summ_table1.setItem(0, 0, QTableWidgetItem('TMC: '))
        self.summ_table1.setItem(0, 1, QTableWidgetItem(self.project.summary_data().tmc()))
        self.summ_table1.setItem(0, 2, QTableWidgetItem(self.project.summary_data().tmc()))
        self.summ_table1.setItem(1, 0, QTableWidgetItem('Start Date:'))
        self.summ_table1.setItem(1, 1, QTableWidgetItem(self.project.summary_data().start_date(0)))
        self.summ_table1.setItem(1, 2, QTableWidgetItem(self.project.summary_data().start_date(1)))
        self.summ_table1.setItem(2, 0, QTableWidgetItem('End Date:'))
        self.summ_table1.setItem(2, 1, QTableWidgetItem(self.project.summary_data().end_date(0)))
        self.summ_table1.setItem(2, 2, QTableWidgetItem(self.project.summary_data().end_date(1)))
        self.summ_table1.setItem(3, 0, QTableWidgetItem('Start Time:'))
        self.summ_table1.setItem(3, 1, QTableWidgetItem(self.project.summary_data().start_time(0)))
        self.summ_table1.setItem(3, 2, QTableWidgetItem(self.project.summary_data().start_time(1)))
        self.summ_table1.setItem(4, 0, QTableWidgetItem('End Time:'))
        self.summ_table1.setItem(4, 1, QTableWidgetItem(self.project.summary_data().end_time(0)))
        self.summ_table1.setItem(4, 2, QTableWidgetItem(self.project.summary_data().end_time(1)))
        self.summ_table1.setItem(5, 0, QTableWidgetItem('Sample Size:'))
        self.summ_table1.setItem(5, 1, QTableWidgetItem(self.project.summary_data().sample_size(0)))
        self.summ_table1.setItem(5, 2, QTableWidgetItem(self.project.summary_data().sample_size(1)))
        self.summ_table1.setItem(6, 0, QTableWidgetItem('Number of Days:'))
        self.summ_table1.setItem(6, 1, QTableWidgetItem(self.project.summary_data().num_days(0)))
        self.summ_table1.setItem(6, 2, QTableWidgetItem(self.project.summary_data().num_days(1)))
        self.summ_table1.setItem(7, 0, QTableWidgetItem('Potential Sample:'))
        self.summ_table1.setItem(7, 1, QTableWidgetItem(self.project.summary_data().ideal_sample(0)))
        self.summ_table1.setItem(7, 2, QTableWidgetItem(self.project.summary_data().ideal_sample(1)))
        self.summ_table1.setItem(8, 0, QTableWidgetItem('% Data Available:'))
        self.summ_table1.setItem(8, 1, QTableWidgetItem(self.project.summary_data().pct_sample_available(0)))
        self.summ_table1.setItem(8, 2, QTableWidgetItem(self.project.summary_data().pct_sample_available(1)))
        self.summ_table1.setHorizontalHeaderItem(0, QTableWidgetItem(''))
        self.summ_table1.setHorizontalHeaderItem(1, QTableWidgetItem('Period 1'))
        self.summ_table1.setHorizontalHeaderItem(2, QTableWidgetItem('Period 2'))
        for i in range(self.summ_table1.rowCount()):
            for j in range(self.summ_table1.columnCount()):
                self.summ_table1.item(i, j).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        print('here4')
        # Summary Table 2
        if self.summ_table2 is None:
            self.summ_table2 = QTableWidget()
        else:
            self.summ_table2.setRowCount(0)
        print('here5')
        self.summ_table2.setRowCount(6)
        self.summ_table2.setColumnCount(5)
        print('here6')
        self.summ_table2.setItem(0, 0, QTableWidgetItem('Mean - Am Peak (mph):'))
        self.summ_table2.setItem(0, 1, QTableWidgetItem(self.project.summary_data().am_mean(0)))
        self.summ_table2.setItem(0, 2, QTableWidgetItem(self.project.summary_data().am_mean(1)))
        self.summ_table2.setItem(0, 3, QTableWidgetItem(self.project.summary_data().am_mean(2)))
        self.summ_table2.setItem(0, 4, QTableWidgetItem(self.project.summary_data().am_mean(3)))
        self.summ_table2.setItem(1, 0, QTableWidgetItem('Mean - Midday (mph):'))
        self.summ_table2.setItem(1, 1, QTableWidgetItem(self.project.summary_data().md_mean(0)))
        self.summ_table2.setItem(1, 2, QTableWidgetItem(self.project.summary_data().md_mean(1)))
        self.summ_table2.setItem(1, 3, QTableWidgetItem(self.project.summary_data().md_mean(2)))
        self.summ_table2.setItem(1, 4, QTableWidgetItem(self.project.summary_data().md_mean(3)))
        self.summ_table2.setItem(2, 0, QTableWidgetItem('Mean - PM Peak (mph):'))
        self.summ_table2.setItem(2, 1, QTableWidgetItem(self.project.summary_data().pm_mean(0)))
        self.summ_table2.setItem(2, 2, QTableWidgetItem(self.project.summary_data().pm_mean(1)))
        self.summ_table2.setItem(2, 3, QTableWidgetItem(self.project.summary_data().pm_mean(2)))
        self.summ_table2.setItem(2, 4, QTableWidgetItem(self.project.summary_data().pm_mean(3)))
        self.summ_table2.setItem(3, 0, QTableWidgetItem('95th - AM Peak (mph):'))
        self.summ_table2.setItem(3, 1, QTableWidgetItem(self.project.summary_data().am_95(0)))
        self.summ_table2.setItem(3, 2, QTableWidgetItem(self.project.summary_data().am_95(1)))
        self.summ_table2.setItem(3, 3, QTableWidgetItem(self.project.summary_data().pm_mean(2)))
        self.summ_table2.setItem(3, 4, QTableWidgetItem(self.project.summary_data().pm_mean(3)))
        self.summ_table2.setItem(4, 0, QTableWidgetItem('95th - Midday (mph):'))
        self.summ_table2.setItem(4, 1, QTableWidgetItem(self.project.summary_data().md_95(0)))
        self.summ_table2.setItem(4, 2, QTableWidgetItem(self.project.summary_data().md_95(1)))
        self.summ_table2.setItem(4, 3, QTableWidgetItem(self.project.summary_data().pm_mean(2)))
        self.summ_table2.setItem(4, 4, QTableWidgetItem(self.project.summary_data().pm_mean(3)))
        self.summ_table2.setItem(5, 0, QTableWidgetItem('95th - PM Peak (mph):'))
        self.summ_table2.setItem(5, 1, QTableWidgetItem(self.project.summary_data().pm_95(0)))
        self.summ_table2.setItem(5, 2, QTableWidgetItem(self.project.summary_data().pm_95(1)))
        self.summ_table2.setItem(5, 3, QTableWidgetItem(self.project.summary_data().pm_mean(2)))
        self.summ_table2.setItem(5, 4, QTableWidgetItem(self.project.summary_data().pm_mean(3)))
        self.summ_table2.setHorizontalHeaderItem(0, QTableWidgetItem(''))
        self.summ_table2.setHorizontalHeaderItem(1, QTableWidgetItem('Wkdy Period 1'))
        self.summ_table2.setHorizontalHeaderItem(2, QTableWidgetItem('Wkdy Period 2'))
        self.summ_table2.setHorizontalHeaderItem(3, QTableWidgetItem('Wknd Period 1'))
        self.summ_table2.setHorizontalHeaderItem(4, QTableWidgetItem('Wknd Period 2'))
        print('here7')

        for i in range(self.summ_table2.rowCount()):
            for j in range(self.summ_table2.columnCount()):
                if self.summ_table2.item(i, j) is not None:
                    self.summ_table2.item(i, j).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        print('here8')
        if self.summary_panel is None:
            self.summary_panel = QWidget()
            summary_layout = QVBoxLayout(self.summary_panel)
            summary_layout.addWidget(info_panel)
            summary_layout.addWidget(self.summ_table1)
            summary_layout.addWidget(self.summ_table2)
            new_tab_idx = self.ui.tabWidget.addTab(self.summary_panel, 'Summary Data')
            self.ui.tabWidget.setCurrentIndex(new_tab_idx)
        else:
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 1)

    def load_time_time_charts(self):
        # chart_panel_name = self.project.get_name() + ' Temporal Exploration Charts'
        chart_panel_name = '1.3 - Temporal Scoping'
        # self.chart_panel1 = ChartGridPanel(self.project, options=self.project.chart_panel1_opts)
        self.chart_panel1_3 = Stage1GridPanel(self.project, panel_type=3, options=self.project.chart_panel1_opts)
        # self.chart1_options_action.setEnabled(True)
        new_tab_index = self.ui.tabWidget.addTab(self.chart_panel1_3, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)
        self.ui.pushButton_first_chart.setDisabled(True)
        self.ui.toolBox.setItemEnabled(2, True)
        self.ui.toolBox.setItemEnabled(3, True)
        self.ui.toolBox.setItemEnabled(4, True)
        self.ui.toolBox.setCurrentIndex(2)
        chart_panel_name_trend = '1.4 - Trend Analysis'
        self.chart_panel1_4 = Stage1GridPanel(self.project, panel_type=4, options=None)
        new_tab_index_trend = self.ui.tabWidget.addTab(self.chart_panel1_4, chart_panel_name_trend)

    def load_spatial_charts(self):
        # chart_panel_name = self.project.get_name() + ' Spatial Exploration Charts'
        chart_panel_name = '1.2 - Spatial Scoping'
        self.chart_panel_spatial = SpatialGridPanel(self.project, options=self.project.chart_panel1_opts)
        new_tab_index = self.ui.tabWidget.addTab(self.chart_panel_spatial, chart_panel_name)

        self.ui.tabWidget.setCurrentIndex(new_tab_index)
        self.ui.pushButton_first_chart.setDisabled(True)
        self.ui.toolBox.setItemEnabled(1, True)
        self.ui.toolBox.setCurrentIndex(1)
        # pass

    def create_chart_panel1(self):
        # cp1_dlg = ChartPanelOptionsDlg(self, self.load_time_time_charts)
        # cp1_dlg.show()
        self.load_time_time_charts()
        self.ui.pushButton_sec_chart.setDisabled(True)
        # self.chart1_options_action.setDisabled(False)

    def edit_chart1_options(self):
        cp1_dlg = ChartPanelOptionsDlg(self, self.update_chart_panel1)
        cp1_dlg.show()


    def update_chart_panel1(self):
        if self.chart_panel1_3 is not None:
            self.chart_panel1_3.options_updated()

    def update_dq_chart(self):
        all_direction_list = self.project.database.get_directions()
        get_selected = self.ui.treeWidget_3.selectedItems()
        if get_selected:
            is_facility = False
            is_project = False
            base_node = get_selected[0]
            get_child_node = base_node.text(0)
            if get_child_node in all_direction_list:
                is_facility = True
            elif get_child_node == self.project.get_name():
                is_project = True
            if is_project:
                self.dq_chart_panel.update_all(tmc_id=self.project.get_tmc(as_list=True, full_list=True))
                print('project selected')
                pass
            else:
                if self.dq_chart_panel is not None:
                    if is_facility:
                        print(get_child_node + ' selected')
                        old_dir = self.project.direction
                        new_dir = self.project.get_selected_directions()[0]
                        if old_dir != new_dir:
                            self.reset_maps()
                        self.highlight_tmc(-1)
                        # self.dq_chart_panel.update_plot_data(tmc_id=None)
                        self.dq_chart_panel.update_all(tmc_id=self.project.get_tmc(as_list=True))
                        pass
                    else:
                        print(get_child_node + ' selected')
                        old_dir = self.project.direction
                        new_dir = self.project.get_selected_directions()[0]
                        if old_dir != new_dir:
                            self.reset_maps()
                        self.highlight_tmc(self.map_tmc_to_pl_index.get(get_child_node))
                        # self.dq_chart_panel.update_plot_data(tmc_id=get_child_node)
                        self.dq_chart_panel.update_all(tmc_id=[get_child_node])
                        pass
        else:
            # do nothing as no node is selected
            pass

    def setup_tmc_list(self, is_init=False):
        subset_tmc = self.project.get_tmc()
        self.ui.treeWidget_2.clear()

        cumulative_mi = 0
        for index, row in subset_tmc.iterrows():
            tmc_item = QTreeWidgetItem(self.ui.treeWidget_2)
            # tmc_item.setFlags(tmc_item.flags() | Qt.ItemIsUserCheckable)
            # tmc_item.setCheckState(0, Qt.Checked)
            # tmc_item.setCheckState(0, Qt.Unchecked)
            tmc_item.setText(0, row[Project.ID_TMC_CODE])
            tmc_item.setText(1, row[Project.ID_TMC_INTX])
            tmc_item.setText(2, row[Project.ID_TMC_DIR][0] + 'B')
            tmc_item.setText(3, '{:1.1f}'.format(row[Project.ID_TMC_LEN]))
            cumulative_mi += row[Project.ID_TMC_LEN]
            tmc_item.setText(4, '{:1.1f}'.format(cumulative_mi))

        if is_init:
            # self.ui.treeWidget_2.itemChanged.connect(self.handle_tmc_item_check)
            self.ui.treeWidget_2.itemSelectionChanged.connect(self.handle_tmc_item_select)

    def handle_tmc_item_select(self):
        get_selected = self.ui.treeWidget_2.selectedItems()
        if get_selected:
            base_node = get_selected[0]
            get_child_node = base_node.text(0)
            # print(getChildNode)
            self.highlight_tmc(self.map_tmc_to_pl_index.get(get_child_node))
            if self.stage2panel is not None:
                self.stage2panel.select_tmc(get_child_node)

    def handle_tmc_item_check(self):
        cumulative_mi = 0
        tmc_list = self.project.database.get_tmcs()
        root_item = self.ui.treeWidget_2.invisibleRootItem()
        for tmc_idx in range(root_item.childCount()):
            if root_item.child(tmc_idx).checkState(0):
                cumulative_mi += tmc_list[Project.ID_TMC_LEN][tmc_idx]
        self.ui.label_6.setText('{:1.1f}'.format(cumulative_mi))
        # self.ui.pushButton_tmc_subset.setEnabled(False)

    def get_tmc_subset(self):
        tmc_subset = []
        tmc_list = self.project.database.get_tmcs()
        root_item = self.ui.treeWidget_2.invisibleRootItem()
        for tmc_idx in range(root_item.childCount()):
            if root_item.child(tmc_idx).checkState(0):
                tmc_subset.append(tmc_list[Project.ID_TMC_CODE][tmc_idx])

        return tmc_subset


class ConnectionContainer(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.manager = None

    def set_manager(self, manager):
        self.manager = manager

    @pyqtSlot(float)
    def change_page(self, page):
        print("changed page: " + str(page))


class ChartPanelOptionsDlg(QDialog):

    def __init__(self, main_window, update_func=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.update_func = update_func
        self.ui = Ui_CPD()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.ok_press)
        self.ui.buttonBox.rejected.connect(self.close_press)
        # self.chart_options = ChartOptions()
        self.chart_options = self.main_window.project.chart_panel1_opts
        self.color_list = self.chart_options.speed_bin_colors.copy()
        self.setup_panel()

    def setup_panel(self):
        self.ui.cb_rows.setCurrentIndex(self.chart_options.num_rows - 1)
        self.ui.cb_cols.setCurrentIndex(self.chart_options.num_cols - 1)
        chart_types = CHART1_TYPES
        self.ui.cb_chart1.addItems(chart_types)
        self.ui.cb_chart2.addItems(chart_types)
        self.ui.cb_chart3.addItems(chart_types)
        self.ui.cb_chart4.addItems(chart_types)
        self.ui.cb_chart1.setCurrentIndex(self.chart_options.chart_type[0][0])
        self.ui.cb_chart2.setCurrentIndex(self.chart_options.chart_type[0][1])
        self.ui.cb_chart3.setCurrentIndex(self.chart_options.chart_type[1][0])
        self.ui.cb_chart4.setCurrentIndex(self.chart_options.chart_type[1][1])
        self.ui.cb_chart1.setEnabled(self.chart_options.has_chart[0][0])
        self.ui.cb_chart2.setEnabled(self.chart_options.has_chart[0][1])
        self.ui.cb_chart3.setEnabled(self.chart_options.has_chart[1][0])
        self.ui.cb_chart4.setEnabled(self.chart_options.has_chart[1][1])
        self.ui.cb_num_bins.setCurrentIndex(self.chart_options.num_speed_bins - 1)
        self.ui.cb_bin_color_scheme.setCurrentIndex(1)
        self.ui.pb_bin1.setStyleSheet(generate_color_button_style(self.chart_options.speed_bin_colors[0]))
        self.ui.pb_bin2.setStyleSheet(generate_color_button_style(self.chart_options.speed_bin_colors[1]))
        self.ui.pb_bin3.setStyleSheet(generate_color_button_style(self.chart_options.speed_bin_colors[2]))
        self.ui.pb_bin4.setStyleSheet(generate_color_button_style(self.chart_options.speed_bin_colors[3]))
        self.ui.pb_bin5.setStyleSheet(generate_color_button_style(self.chart_options.speed_bin_colors[4]))
        self.ui.spin_min_bin1.setValue(self.chart_options.speed_bins[0])
        self.ui.spin_max_bin1.setValue(self.chart_options.speed_bins[1])
        self.ui.label_min_bin2.setText(str(self.chart_options.speed_bins[1]))
        self.ui.spin_max_bin2.setValue(self.chart_options.speed_bins[2])
        self.ui.label_min_bin3.setText(str(self.chart_options.speed_bins[2]))
        self.ui.spin_max_bin3.setValue(self.chart_options.speed_bins[3])
        self.ui.label_min_bin4.setText(str(self.chart_options.speed_bins[3]))
        self.ui.spin_max_bin4.setValue(self.chart_options.speed_bins[4])
        self.ui.label_min_bin5.setText(str(self.chart_options.speed_bins[4]))

        self.connect_cbs()
        self.connect_color_buttons()
        self.connect_bin_labels()

    def ok_press(self):
        rows = int(self.ui.cb_rows.currentText())
        cols = int(self.ui.cb_cols.currentText())
        num_speed_bins = int(self.ui.cb_num_bins.currentText())
        bin_vals = [int(self.ui.spin_min_bin1.text()),
                    int(self.ui.spin_max_bin1.text()),
                    int(self.ui.spin_max_bin2.text()),
                    int(self.ui.spin_max_bin3.text()),
                    int(self.ui.spin_max_bin4.text())]
        self.main_window.project.chart_panel1_opts = ChartOptions(rows=rows, cols=cols, num_speed_bins=num_speed_bins, speed_bins_vals=bin_vals,
                                                          speed_bin_colors=self.color_list)
        self.main_window.project.chart_panel1_opts.chart_type[0][0] = self.ui.cb_chart1.currentIndex()
        self.main_window.project.chart_panel1_opts.chart_type[0][1] = self.ui.cb_chart2.currentIndex()
        self.main_window.project.chart_panel1_opts.chart_type[1][0] = self.ui.cb_chart3.currentIndex()
        self.main_window.project.chart_panel1_opts.chart_type[1][1] = self.ui.cb_chart4.currentIndex()
        self.close()
        if self.update_func is not None:
            self.update_func()
            self.main_window.ui.pushButton_sec_chart.setDisabled(True)
            # self.main_window.chart1_options_action.setDisabled(False)

    def close_press(self):
        self.close()

    def connect_cbs(self):
        self.ui.cb_rows.currentIndexChanged.connect(self.update_chart_selection)
        self.ui.cb_cols.currentIndexChanged.connect(self.update_chart_selection)
        self.ui.cb_num_bins.currentIndexChanged.connect(self.update_bin_selections)
        self.ui.cb_bin_color_scheme.currentIndexChanged.connect(self.update_color_scheme)

    def update_chart_selection(self):
        num_rows = self.ui.cb_rows.currentIndex() + 1
        num_cols = self.ui.cb_cols.currentIndex() + 1
        # self.ui.cb_chart1.setEnabled(True)
        self.ui.cb_chart2.setEnabled(num_cols > 1)
        self.ui.cb_chart3.setEnabled(num_rows > 1)
        self.ui.cb_chart4.setEnabled(num_rows > 1 and num_cols > 1)

    def update_bin_selections(self):
        num_bins = self.ui.cb_num_bins.currentIndex() + 1
        self.ui.pb_bin2.setEnabled(num_bins > 1)
        self.ui.label_min_bin2.setEnabled(num_bins > 1)
        self.ui.spin_max_bin2.setEnabled(num_bins > 1)
        self.ui.pb_bin3.setEnabled(num_bins > 2)
        self.ui.label_min_bin3.setEnabled(num_bins > 2)
        self.ui.spin_max_bin3.setEnabled(num_bins > 2)
        self.ui.pb_bin4.setEnabled(num_bins > 3)
        self.ui.label_min_bin4.setEnabled(num_bins > 3)
        self.ui.spin_max_bin4.setEnabled(num_bins > 3)
        self.ui.pb_bin5.setEnabled(num_bins > 4)
        self.ui.label_min_bin5.setEnabled(num_bins > 4)
        # self.ui.label_max_bin5.setEnabled(num_bins > 4)

    def update_color_scheme(self):
        if self.ui.cb_bin_color_scheme.currentIndex() == 0:
            self.color_list = SPEED_BIN_DEFAULTS.copy()
            self.ui.pb_bin1.setStyleSheet(generate_color_button_style(self.color_list[0]))
            self.ui.pb_bin2.setStyleSheet(generate_color_button_style(self.color_list[1]))
            self.ui.pb_bin3.setStyleSheet(generate_color_button_style(self.color_list[2]))
            self.ui.pb_bin4.setStyleSheet(generate_color_button_style(self.color_list[3]))
            self.ui.pb_bin5.setStyleSheet(generate_color_button_style(self.color_list[4]))

    def connect_color_buttons(self):
        self.ui.pb_bin1.clicked.connect(lambda: self.set_speed_bin_color(0, self.ui.pb_bin1))
        self.ui.pb_bin2.clicked.connect(lambda: self.set_speed_bin_color(1, self.ui.pb_bin2))
        self.ui.pb_bin3.clicked.connect(lambda: self.set_speed_bin_color(2, self.ui.pb_bin3))
        self.ui.pb_bin4.clicked.connect(lambda: self.set_speed_bin_color(3, self.ui.pb_bin4))
        self.ui.pb_bin5.clicked.connect(lambda: self.set_speed_bin_color(4, self.ui.pb_bin5))

    def set_speed_bin_color(self, index, button):
        if index >=0 and index < len(self.color_list):
            dlg = QColorDialog()
            dlg.setCustomColor(1, QColor(SPEED_BIN_DEFAULTS[0]).toRgb())
            dlg.setCustomColor(3, QColor(SPEED_BIN_DEFAULTS[1]).toRgb())
            dlg.setCustomColor(5, QColor(SPEED_BIN_DEFAULTS[2]).toRgb())
            dlg.setCustomColor(7, QColor(SPEED_BIN_DEFAULTS[3]).toRgb())
            dlg.setCustomColor(9, QColor(SPEED_BIN_DEFAULTS[4]).toRgb())
            c_str = dlg.getColor(initial=QColor(self.color_list[index]), parent=self)

            if c_str.isValid():
                self.color_list[index] = c_str.name()
                button.setStyleSheet(generate_color_button_style(c_str.name()))
                self.ui.cb_bin_color_scheme.setCurrentIndex(1)

    def connect_bin_labels(self):
        self.ui.spin_max_bin1.valueChanged.connect(lambda: self.update_bin_label(self.ui.spin_max_bin1, self.ui.label_min_bin2))
        self.ui.spin_max_bin2.valueChanged.connect(lambda: self.update_bin_label(self.ui.spin_max_bin2, self.ui.label_min_bin3))
        self.ui.spin_max_bin3.valueChanged.connect(lambda: self.update_bin_label(self.ui.spin_max_bin3, self.ui.label_min_bin4))
        self.ui.spin_max_bin4.valueChanged.connect(lambda: self.update_bin_label(self.ui.spin_max_bin4, self.ui.label_min_bin5))

    def update_bin_label(self, bin_spin, bin_label):
        bin_label.setText(bin_spin.text())

def provide_gui_for(application):
    qt_app = QApplication(sys.argv)
    web_app = FlaskThread(application)
    web_app.start()

    qt_app.aboutToQuit.connect(web_app.terminate)
    mw = MainWindow()
    return qt_app.exec_()

# class CustomTabBar(QTabBar):
#
#     def __init__(self, parent=None):
#         QTabBar.__init__(parent=parent)
#
#     def paintEvent(self, event):
#         opt = QStyleOptionTab()
#         opt.
#         for i in range(self.count()):
#             self.initStyleOption(opt, i)
#             if i == 0:
#                 self.color


if __name__ == '__main__':
    from fhwa_spl_flask import app
    sys.exit(provide_gui_for(app))
