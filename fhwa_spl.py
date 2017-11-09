"""
Effectively the “main” class of the program
Includes code for the MainWindow application
Also defines the core Project class
Has leftover code defining the FlaskThread for potential future web/d3js visualizations
"""


import sys
import os
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QThread, Qt, QDate
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog, QDialog, QVBoxLayout
from PyQt5.QtWidgets import QLineEdit, QTreeWidgetItem, QWidget, QLabel, QColorDialog
from PyQt5.QtGui import QColor
# from mw_test import Ui_MainWindow
from mainwindow import Ui_MainWindow
from chart_panel_options import Ui_Dialog as Ui_CPD
from viz_qt import LoadProjectQT
from offline_viz import FourByFourPanel
from Stage2GridPanel import Stage2GridPanel
from mpl_panels import ChartGridPanel, SpatialGridPanel
from chart_defaults import ChartOptions, SPEED_BIN_DEFAULTS, generate_color_button_style, CHART1_TYPES
import sql_helper
from chart_defaults import generate_vega_lite

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

        self.chart_panel_spatial = None
        self.chart_panel1 = None
        self.chart_panel2 = None

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
        self.ui.menuAnalyze.addAction(load_flask_action)

        load_map_action = QAction('&Load Map', self)
        load_map_action.setToolTip('Load Web Map of TMC locations')
        load_map_action.triggered.connect(self.load_map_chart)
        self.ui.menuAnalyze.addAction(load_map_action)

        toggle_floating_map_action = QAction('&Toggle Floating Map', self)
        toggle_floating_map_action.setToolTip('Pop out or dock map window.')
        toggle_floating_map_action.triggered.connect(self.toggle_floating_map)
        self.ui.menuAnalyze.addAction(toggle_floating_map_action)

        # load_mpl_action = QAction('&Load Offline Chart', self)
        # load_mpl_action.setToolTip('Load Charts in offline mode.')
        # load_mpl_action.triggered.connect(self.extract_case_study)
        # self.ui.menuAnalyze.addAction(load_mpl_action)

        # load_mpl_spm_action = QAction('&Load SPM Chart', self)
        # load_mpl_spm_action.setToolTip('Load Charts for SPM Case Study.')
        # load_mpl_spm_action.triggered.connect(self.extract_case_study_spm)
        # self.ui.menuAnalyze.addAction(load_mpl_spm_action)

        # edit_tmcs_action = QAction('&Create TMC Subset', self)
        # edit_tmcs_action.setToolTip('Edit the set of TMCs')
        # edit_tmcs_action.triggered.connect(self.edit_tmcs)
        # self.ui.menuAnalyze.addAction(edit_tmcs_action)

        # update_chart_action = QAction('&Update Chart', self)
        # update_chart_action.setShortcut('Ctrl+K')
        # update_chart_action.setToolTip('Update WebBrowser')
        # update_chart_action.triggered.connect(self.update_chart)
        # self.ui.menuAnalyze.addAction(update_chart_action)

        self.chart1_load_action = QAction('&Load Temporal Scoping Charts', self)
        self.chart1_load_action.setToolTip('Load the temporal scoping charts')
        self.chart1_load_action.triggered.connect(self.create_chart_panel1)
        # self.chart1_options_action.setEnabled(False)
        self.ui.menuAnalyze.addAction(self.chart1_load_action)

        self.chart1_options_action = QAction('&Chart 1 Options', self)
        self.chart1_options_action.setToolTip('Congifure the Chart Panel 1 Options')
        self.chart1_options_action.triggered.connect(self.edit_chart1_options)
        self.chart1_options_action.setEnabled(False)
        self.ui.menuChartOptions.addAction(self.chart1_options_action)

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

        self.ui.pushButton_tmc_subset.setEnabled(False)

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
        # Example of how to load a chart via Flask
        # self.ui.webView_3.load(QUrl(ROOT_URL))
        self.ui.webView_map.load(QUrl(ROOT_URL))

    def update_chart(self):
        # Not In Use, but example of how to fire javascript function
        print('action triggered')
        # self.ui.webView.page().mainFrame().evaluateJavaScript('transitionStacked()')
        self.ui.webView_map.page().mainFrame().evaluateJavaScript('transitionStacked()')

    def load_map_chart(self, create_plots=True):
        if self.project is not None:
            import folium
            import json
            from numpy import mean
            tmc_list = self.project.get_tmc()
            lat = tmc_list['start_latitude'][0]
            lon = tmc_list['start_longitude'][0]
            m = folium.Map(location=[lat, lon])
            if create_plots:
                df = self.project.database.get_data()
                tt_hour = df[df['weekday'] <= 4].groupby(['tmc_code', 'Hour']).agg(mean)['travel_time_minutes']
            else:
                tt_hour = None
            for index, row in tmc_list.iterrows():
                if create_plots:
                    # df = self.project.database.get_data()
                    # tt_hour = df[(df['weekday'] <= 4) & (df['tmc_code'].isin([row['tmc']]))].groupby('Hour').agg(mean)['travel_time_minutes']
                    if row['tmc'] in tt_hour:
                        vis_str = generate_vega_lite(tt_hour[row['tmc']].to_frame())
                        pu = folium.Popup(max_width=300).add_child(folium.VegaLite(vis_str, width=300, height=275))
                    else:
                        pu = row['tmc'] + ': No Travel Time Data Available'
                else:
                    vis_str = json.load(open('templates/vis1.json'))
                    pu = folium.Popup(max_width=300).add_child(folium.VegaLite(vis_str, width=300, height=275))

                folium.Marker(
                    location=[row['start_latitude'], row['start_longitude']],
                    popup=row['tmc'] + ' Start',
                    # popup=pu,
                    icon=folium.Icon(icon='cloud')
                ).add_to(m)
                folium.Marker(
                    location=[row['end_latitude'], row['end_longitude']],
                    popup=row['tmc'] + ' End',
                    icon=folium.Icon(icon='cloud')
                ).add_to(m)
                pl = folium.PolyLine(
                    [[row['start_latitude'], row['start_longitude']], [row['end_latitude'], row['end_longitude']]],
                    weight=3,
                    color='black',
                    # popup='TMC ID: ' + row['tmc'] + '\n' + 'Road/Route: ' + row['road'] + ' ' + row['direction'] + '\n' + 'Name/Intersection: ' + row['intersection']
                    popup=pu
                )
                pl.add_to(m)
            m.save('templates/map3.html')
            f_name = os.path.realpath('templates/map3.html')
            self.ui.webView_map.load(QUrl('file:///'+f_name))
            self.ui.webView_minimap.load(QUrl('file:///' + f_name))

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
            self.ui.tabWidget.insertTab(1, self.ui.tab_3, 'Web Panel')
            # self.ui.tabWidget.addTab(self.ui.tab_3, 'Web Panel')
            pass

    def create_new(self):
        project_dir_name = QFileDialog.getExistingDirectory(self, "Select Project/Data Folder")
        if project_dir_name != '':
            tokens = project_dir_name.split('/')
            tmc_file_name = project_dir_name + '/tmc_identification.csv'
            data_file_name = project_dir_name + '/' + tokens[-1] + '.csv'
            project_name, ok = QInputDialog.getText(self, 'Project Name', 'Enter a project name:', QLineEdit.Normal, 'New Project')
            if ok:
                self.ui.label_project_name.setText(project_name)
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
            self.ui.pushButton_first_chart.setDisabled(False)
            self.ui.pushButton_sec_chart.setDisabled(False)
            self.chart1_load_action.setDisabled(False)
        proj_item.setExpanded(True)
        proj_item.child(0).setCheckState(0, Qt.Checked)
        self.ui.treeWidget_3.itemChanged.connect(self.setup_tmc_list)

        # Updating Data Types
        self.ui.listWidget_4.addItem('Start Date: ' + project.database.get_first_date())
        self.ui.listWidget_4.addItem('End Date: ' + project.database.get_last_date())
        self.ui.listWidget_4.addItem('Weekdays: ' + project.database.get_available_weekdays(as_string=True))
        self.ui.listWidget_4.addItem('Weekends: ' + project.database.get_available_weekends(as_string=True))
        self.ui.listWidget_4.addItem('Months: ' + project.database.get_available_months(as_string=True))

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

        self.load_data_density_charts('Data Quality/Density')

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
        temp_widget = QWidget(self)
        v_layout = QVBoxLayout(temp_widget)
        v_layout.addWidget(QLabel('Placeholder for data "density" chart panel.  This will provide basic information about the dataset, as well as '
                                  'show charts giving a glimpse at the availability of data in the dataset.'))
        new_tab_index = self.ui.tabWidget.addTab(temp_widget, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)

    def load_mpl_charts(self, chart_panel_name):
        mpl_widget = FourByFourPanel(self.project)
        new_tab_index = self.ui.tabWidget.addTab(mpl_widget, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)

    def load_extra_time_charts(self):
        chart_panel_name = self.project.get_name() + ' Extra Time Charts'
        # mpl_widget = FourByFourPanel(self.project)
        mpl_widget = Stage2GridPanel(self.project)
        new_tab_index = self.ui.tabWidget.addTab(mpl_widget, chart_panel_name)
        self.ui.tabWidget.setCurrentIndex(new_tab_index)
        self.ui.toolBox.setCurrentIndex(self.ui.toolBox.currentIndex()+1)
        self.ui.pushButton_tmc_subset.setEnabled(False)

    def load_time_time_charts(self):
        chart_panel_name = self.project.get_name() + ' Temporal Exploration Charts'
        # self.chart_panel1 = TwoByTwoPanelTimeTime(self.project, options=self.project.chart_panel1_opts)
        self.chart_panel1 = ChartGridPanel(self.project, options=self.project.chart_panel1_opts)
        self.chart1_options_action.setEnabled(True)
        new_tab_index = self.ui.tabWidget.addTab(self.chart_panel1, chart_panel_name)

        self.ui.tabWidget.setCurrentIndex(new_tab_index)
        self.ui.pushButton_first_chart.setDisabled(True)
        self.ui.toolBox.setCurrentIndex(2)
        pass

    def load_spatial_charts(self):
        chart_panel_name = self.project.get_name() + ' Spatial Exploration Charts'
        self.chart_panel_spatial = SpatialGridPanel(self.project, options=self.project.chart_panel1_opts)
        # self.chart1_options_action.setEnabled(True)
        new_tab_index = self.ui.tabWidget.addTab(self.chart_panel_spatial, chart_panel_name)

        self.ui.tabWidget.setCurrentIndex(new_tab_index)
        # self.ui.pushButton_first_chart.setDisabled(True)
        self.ui.pushButton_first_chart.setDisabled(True)
        self.ui.toolBox.setCurrentIndex(1)

    def create_chart_panel1(self):
        cp1_dlg = ChartPanelOptionsDlg(self, self.load_time_time_charts)
        cp1_dlg.show()

    def edit_chart1_options(self):
        cp1_dlg = ChartPanelOptionsDlg(self, self.update_chart_panel1)
        cp1_dlg.show()

    def update_chart_panel1(self):
        if self.chart_panel1 is not None:
            self.chart_panel1.options_updated()

    def setup_tmc_list(self, is_init=False):
        subset_tmc = self.project.get_tmc()
        self.ui.treeWidget_2.clear()

        cumulative_mi = 0
        for index, row in subset_tmc.iterrows():
            tmc_item = QTreeWidgetItem(self.ui.treeWidget_2)
            tmc_item.setFlags(tmc_item.flags() | Qt.ItemIsUserCheckable)
            # tmc_item.setCheckState(0, Qt.Checked)
            tmc_item.setCheckState(0, Qt.Unchecked)
            tmc_item.setText(0, row['tmc'])
            tmc_item.setText(1, row['intersection'])
            tmc_item.setText(2, row['direction'][0] + 'B')
            tmc_item.setText(3, '{:1.1f}'.format(row['miles']))
            cumulative_mi += row['miles']
            tmc_item.setText(4, '{:1.1f}'.format(cumulative_mi))

        if is_init:
            self.ui.treeWidget_2.itemChanged.connect(self.handle_tmc_item_check)

    def handle_tmc_item_check(self):
        cumulative_mi = 0
        tmc_list = self.project.database.get_tmcs()
        root_item = self.ui.treeWidget_2.invisibleRootItem()
        for tmc_idx in range(root_item.childCount()):
            if root_item.child(tmc_idx).checkState(0):
                cumulative_mi += tmc_list['miles'][tmc_idx]
        self.ui.label_6.setText('{:1.1f}'.format(cumulative_mi))
        self.ui.pushButton_tmc_subset.setEnabled(False)

    def get_tmc_subset(self):
        tmc_subset = []
        tmc_list = self.project.database.get_tmcs()
        root_item = self.ui.treeWidget_2.invisibleRootItem()
        for tmc_idx in range(root_item.childCount()):
            if root_item.child(tmc_idx).checkState(0):
                tmc_subset.append(tmc_list['tmc'][tmc_idx])

        return tmc_subset


class Project:
    def __init__(self, project_name, directory, main_window):
        self.main_window = main_window
        self._project_name = project_name
        self._project_dir = directory
        self._tmc_file_name = None
        self._data_file_name = None
        self.database = None
        self._date_ranges = []
        self.chart_panel1_opts = ChartOptions()
        self.data_res = 5

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

    def get_selected_directions(self):
        direction_list = []
        root = self.main_window.ui.treeWidget_3.invisibleRootItem()
        for ti in range(root.child(0).childCount()):
            if root.child(0).child(ti).checkState(0):
                direction_list.append(root.child(0).child(ti).text(0))
        return direction_list

    def get_tmc(self, full_list=False, as_list=False):
        if full_list:
            return self.database.get_tmcs(as_list=as_list)
        else:
            tmc_list = self.database.get_tmcs()
            subset_dirs = self.get_selected_directions()
            subset_tmc = tmc_list[tmc_list['direction'].isin(subset_dirs)]
            subset_tmc.reset_index(inplace=True)
            if as_list:
                return subset_tmc['tmc']
            else:
                return subset_tmc

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
            self.main_window.chart1_options_action.setDisabled(False)

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


if __name__ == '__main__':
    from fhwa_spl_flask import app
    sys.exit(provide_gui_for(app))
