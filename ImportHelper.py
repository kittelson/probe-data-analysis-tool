"""
Dialog that helps with importing data
"""

import os
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QThread, Qt, QDate
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QDialog, QWidget, QTabWidget, QDialogButtonBox, QTableWidget, QTableWidgetItem, QSplitter
from PyQt5.QtWidgets import QLabel, QComboBox, QPushButton, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QFont
import pandas as pd
from DataHelper import Project


NUM_DATA_PREV = 10


class ImportDialog(QDialog):
    def __init__(self, main_window, proj_dir_name):
        super().__init__(main_window)
        self.main_window = main_window
        self.project_dir_name = proj_dir_name
        tokens = self.project_dir_name.split('/')
        self.tmc_file_name = self.project_dir_name + '/tmc_identification.csv'
        self.data_file_name = self.project_dir_name + '/' + tokens[-1] + '.csv'
        self.setWindowTitle("Project Data")

        self.data_inspected = False
        self.map_exists = False
        self.data_preview = None
        self.tmc_preview = None

        # -------- Creating central components
        self.tab_panel = QTabWidget(self)
        self.main_layout = QVBoxLayout(self)

        # -------- Build Project Info Panel
        self.info_panel = QWidget(self)
        self.info_layout = QGridLayout(self.info_panel)
        self.project_dir_label = QLabel('Project Data Location')
        self.project_dir_label.setFont(QFont("Times", weight=QFont.Bold))
        if len(self.project_dir_name) > 35:
            self.project_dir_label2 = QLabel('...' + self.project_dir_name[len(self.project_dir_name) - 35:])
        else:
            self.project_dir_label2 = QLabel(self.project_dir_name)
        self.project_name_label = QLabel('Project Name: ')
        self.project_name_label.setFont(QFont("Times", weight=QFont.Bold))
        self.project_name_input = QLineEdit('New Project')
        self.analyst_label = QLabel('Enter Analyst Name: ')
        self.analyst_label.setFont(QFont("Times", weight=QFont.Bold))
        self.analyst_input = QLineEdit('--')
        self.agency_label = QLabel('Enter Agency: ')
        self.agency_label.setFont(QFont("Times", weight=QFont.Bold))
        self.agency_input = QLineEdit('FHWA')
        self.state_label = QLabel('Enter State: ')
        self.state_label.setFont(QFont("Times", weight=QFont.Bold))
        self.state_input = QLineEdit('')
        self.loc_label = QLabel('Enter Location: ')
        self.loc_label.setFont(QFont("Times", weight=QFont.Bold))
        self.loc_input = QLineEdit('')
        self.data_file_label = QLabel('Data File: ')
        self.data_file_label.setFont(QFont("Times", weight=QFont.Bold))
        self.tmc_file_label = QLabel('TMC Info File: ')
        self.tmc_file_label.setFont(QFont("Times", weight=QFont.Bold))
        self.preview_data_button = QPushButton("Inspect and Configure Dataset")
        self.info_layout.addWidget(self.project_name_label, 0, 0)
        self.info_layout.addWidget(self.project_name_input, 0, 1)
        self.info_layout.addWidget(self.analyst_label, 1, 0)
        self.info_layout.addWidget(self.analyst_input, 1, 1)
        self.info_layout.addWidget(self.agency_label, 2, 0)
        self.info_layout.addWidget(self.agency_input, 2, 1)
        self.info_layout.addWidget(self.state_label, 0, 2)
        self.info_layout.addWidget(self.state_input, 0, 3)
        self.info_layout.addWidget(self.loc_label, 1, 2)
        self.info_layout.addWidget(self.loc_input, 1, 3)
        self.info_layout.addWidget(self.project_dir_label, 0, 4)
        self.info_layout.addWidget(self.project_dir_label2, 0, 5)
        self.info_layout.addWidget(self.data_file_label, 1, 4)
        self.info_layout.addWidget(QLabel('.../' + self.data_file_name.split('/')[-1]), 1, 5)
        self.info_layout.addWidget(self.tmc_file_label, 2, 4)
        self.info_layout.addWidget(QLabel('.../' + self.tmc_file_name.split('/')[-1]), 2, 5)
        self.info_layout.addWidget(self.preview_data_button, 3, 4, 1, 2)

        # -------- Build Data Panel
        # Creating Components
        self.data_panel = QWidget(self)
        self.data_sub_panel = QWidget(self.data_panel)
        self.data_col_select_panel = QWidget(self.data_sub_panel)
        self.cb_data_col_tmc = QComboBox()
        self.cb_data_col_timestamp = QComboBox()
        self.cb_data_col_speed = QComboBox()
        self.cb_data_col_travel_time = QComboBox()
        self.data_table = QTableWidget()
        self.data_label = QLabel("Placeholder description")
        # Creating Layouts
        self.data_layout1 = QVBoxLayout(self.data_panel)
        self.data_layout2 = QHBoxLayout(self.data_sub_panel)
        self.data_form_layout = QFormLayout(self.data_col_select_panel)

        # -------- Build TMC Panel
        # Creating Components
        # self.tmc_panel = QSplitter(Qt.Vertical, self)
        self.tmc_panel = QWidget(self)
        self.tmc_col_select_panel = QWidget(self.tmc_panel)
        self.cb_tmc_col_tmc = QComboBox()
        self.cb_tmc_col_dir = QComboBox()
        self.cb_tmc_col_len = QComboBox()
        self.cb_tmc_col_intx = QComboBox()
        self.cb_tmc_col_slat = QComboBox()
        self.cb_tmc_col_slon = QComboBox()
        self.cb_tmc_col_elat = QComboBox()
        self.cb_tmc_col_elon = QComboBox()
        self.load_map_button = QPushButton("Add TMCs to Map")
        self.map_table_panel = QWidget(self.tmc_panel)
        self.map_view = QWebEngineView(self.map_table_panel)
        self.tmc_table = QTableWidget()
        self.tmc_label = QLabel("Placeholder description")
        # Creating Layouts
        self.tmc_col_layout = QGridLayout(self.tmc_col_select_panel)
        self.tmc_layout1 = QVBoxLayout(self.tmc_panel)
        self.tmc_layout2 = QHBoxLayout(self.map_table_panel)

        # -------- Adding tabs
        self.tab_panel.addTab(self.data_panel, "Data Preview")
        self.tab_panel.addTab(self.tmc_panel, "TMC List")

        # -------- Creating ButtonBox
        self.button_box = QDialogButtonBox(Qt.Horizontal, self)
        self.button_box.addButton(QDialogButtonBox.Ok)
        self.button_box.addButton(QDialogButtonBox.Cancel)

        # -------- Adding dialog components
        self.main_layout.addWidget(self.info_panel)
        self.main_layout.addWidget(self.tab_panel)
        self.main_layout.addWidget(self.button_box)

        # -------- Set up dialog
        self.setup_panel()
        self.setModal(True)
        self.show()
        self.project_name_input.selectAll()

    def setup_panel(self):
        self.preview_data_button.clicked.connect(self.inspect_data)

        self.button_box.accepted.connect(self.ok_press)
        self.button_box.rejected.connect(self.close_press)

        self.setup_project_info()

    def inspect_data(self):
        self.data_inspected = True
        self.data_preview = pd.read_csv(self.data_file_name, nrows=NUM_DATA_PREV)
        self.tmc_preview = pd.read_csv(self.tmc_file_name)
        self.setup_data_panel()
        self.setup_tmc_panel()
        self.move(self.x(), self.y() - 250)

    def setup_project_info(self):
        # self.project_name_input.selectAll()
        pass

    def ok_press(self):
        if self.data_inspected:
            Project.ID_DATA_TMC = self.cb_data_col_tmc.currentText()
            Project.ID_DATA_TIMESTAMP = self.cb_data_col_timestamp.currentText()
            Project.ID_DATA_SPEED = self.cb_data_col_speed.currentText()
            Project.ID_DATA_TT = self.cb_data_col_travel_time.currentText()
            Project.ID_TMC_CODE = self.cb_tmc_col_tmc.currentText()
            Project.ID_TMC_DIR = self.cb_tmc_col_dir.currentText()
            Project.ID_TMC_LEN = self.cb_tmc_col_len.currentText()
            Project.ID_TMC_INTX = self.cb_tmc_col_intx.currentText()
            Project.ID_TMC_SLAT = self.cb_tmc_col_slat.currentText()
            Project.ID_TMC_SLON = self.cb_tmc_col_slon.currentText()
            Project.ID_TMC_ELAT = self.cb_tmc_col_elat.currentText()
            Project.ID_TMC_ELON = self.cb_tmc_col_elon.currentText()
        self.main_window.new_project_accepted(self,
                                              self.project_dir_name,
                                              self.project_name_input,
                                              self.analyst_input,
                                              self.agency_input,
                                              self.state_input,
                                              self.loc_input)
        # self.close()

    def close_press(self):
        self.close()

    def setup_data_panel(self):
        # Adding widgets to layouts
        self.data_form_layout.addRow(QLabel("TMC Column:"), self.cb_data_col_tmc)
        self.data_form_layout.addRow(QLabel("Timestamp Column:"), self.cb_data_col_timestamp)
        self.data_form_layout.addRow(QLabel("Speed Column:"), self.cb_data_col_speed)
        self.data_form_layout.addRow(QLabel("Travel Time Column:"), self.cb_data_col_travel_time)
        self.data_layout2.addWidget(self.data_col_select_panel)
        self.data_layout2.addWidget(self.data_table)
        self.data_layout1.addWidget(self.data_label)
        self.data_layout1.addWidget(self.data_sub_panel)
        # Setting up panel
        self.setup_data_col_select_panel()
        self.setup_data_preview_table()

    def setup_data_col_select_panel(self):
        if self.data_preview is not None:
            col_list = self.data_preview.columns
            self.cb_data_col_tmc.addItems(col_list)
            self.cb_data_col_timestamp.addItems(col_list)
            self.cb_data_col_speed.addItems(col_list)
            self.cb_data_col_travel_time.addItems(col_list)

            self.cb_data_col_tmc.setCurrentIndex(0)
            self.cb_data_col_timestamp.setCurrentIndex(1)
            self.cb_data_col_speed.setCurrentIndex(2)
            self.cb_data_col_travel_time.setCurrentIndex(5)

    def setup_data_preview_table(self):
        if self.data_preview is not None:
            num_cols = len(self.data_preview.columns)
            self.data_table.setRowCount(NUM_DATA_PREV)
            self.data_table.setColumnCount(num_cols)
            # Creating column headers
            col_count = 0
            for col_header in self.data_preview.columns:
                self.data_table.setHorizontalHeaderItem(col_count, QTableWidgetItem(col_header))
                col_count += 1

            # Adding data preview rows
            for index, row in self.data_preview.iterrows():
                for col_idx in range(num_cols):
                    item = QTableWidgetItem(str(row[col_idx]))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.data_table.setItem(index, col_idx, item)

            self.data_table.resizeColumnsToContents()

    def setup_tmc_panel(self):
        self.load_map()
        # Adding widgets to layouts
        self.tmc_col_layout.addWidget(QLabel("TMC Code:"), 0, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_tmc, 0, 1)
        self.tmc_col_layout.addWidget(QLabel("Direction:"), 1, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_dir, 1, 1)
        self.tmc_col_layout.addWidget(QLabel("Length:"), 2, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_len, 2, 1)
        self.tmc_col_layout.addWidget(QLabel("Intersection:"), 3, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_intx, 3, 1)
        self.tmc_col_layout.addWidget(QLabel("Start Lat:"), 4, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_slat, 4, 1)
        self.tmc_col_layout.addWidget(QLabel("Start Lon:"), 5, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_slon, 5, 1)
        self.tmc_col_layout.addWidget(QLabel("End Lat:"), 6, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_elat, 6, 1)
        self.tmc_col_layout.addWidget(QLabel("End Lon:"), 7, 0)
        self.tmc_col_layout.addWidget(self.cb_tmc_col_elon, 7, 1)
        self.tmc_col_layout.addWidget(self.load_map_button, 8, 0, 1, 2)
        self.tmc_layout2.addWidget(self.tmc_col_select_panel)
        self.tmc_layout2.addWidget(self.map_view)
        self.tmc_layout1.addWidget(self.tmc_label)
        self.tmc_layout1.addWidget(self.map_table_panel)
        self.tmc_table.setMinimumHeight(200)
        self.tmc_layout1.addWidget(self.tmc_table)
        # Setting up panel
        self.setup_tmc_col_select_panel()
        self.setup_tmc_preview_table()
        self.load_map_button.clicked.connect(self.add_tmcs_to_map)

    def setup_tmc_col_select_panel(self):
        if self.tmc_preview is not None:
            col_list = self.tmc_preview.columns
            self.cb_tmc_col_tmc.addItems(col_list)
            self.cb_tmc_col_dir.addItems(col_list)
            self.cb_tmc_col_len.addItems(col_list)
            self.cb_tmc_col_intx.addItems(col_list)
            self.cb_tmc_col_slat.addItems(col_list)
            self.cb_tmc_col_slon.addItems(col_list)
            self.cb_tmc_col_elat.addItems(col_list)
            self.cb_tmc_col_elon.addItems(col_list)

            self.cb_tmc_col_tmc.setCurrentIndex(0)
            self.cb_tmc_col_dir.setCurrentIndex(2)
            self.cb_tmc_col_len.setCurrentIndex(11)
            self.cb_tmc_col_intx.setCurrentIndex(3)
            self.cb_tmc_col_slat.setCurrentIndex(7)
            self.cb_tmc_col_slon.setCurrentIndex(8)
            self.cb_tmc_col_elat.setCurrentIndex(9)
            self.cb_tmc_col_elon.setCurrentIndex(10)

    def setup_tmc_preview_table(self):
        if self.tmc_preview is not None:
            num_rows = len(self.tmc_preview)
            num_cols = len(self.tmc_preview.columns)
            self.tmc_table.setRowCount(num_rows)
            self.tmc_table.setColumnCount(num_cols)
            # Creating column headers
            self.tmc_table.setHorizontalHeaderItem(0, QTableWidgetItem('Include'))
            col_count = 1
            for col_header in self.tmc_preview.columns:
                self.tmc_table.setHorizontalHeaderItem(col_count, QTableWidgetItem(col_header))
                col_count += 1

            # Adding data preview rows
            for index, row in self.tmc_preview.iterrows():
                check_item = QTableWidgetItem('')
                check_item.setFlags(check_item.flags() | Qt.ItemIsUserCheckable)
                check_item.setCheckState(Qt.Checked)
                check_item.setTextAlignment(Qt.AlignCenter)
                self.tmc_table.setItem(index, 0, check_item)
                for col_idx in range(num_cols):
                    item = QTableWidgetItem(str(row[col_idx]))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.tmc_table.setItem(index, col_idx+1, item)
            self.tmc_table.resizeColumnsToContents()

    def load_map(self):
        f_name = os.path.realpath('templates/map_gen.html')
        self.map_view.loadFinished.connect(self.map_loaded)
        self.map_view.load(QUrl('file:///' + f_name.replace('\\', '/')))

    def map_loaded(self):
        self.map_exists = True

    def add_tmcs_to_map(self):
        field_slat = self.cb_tmc_col_slat.currentText()
        field_slon = self.cb_tmc_col_slon.currentText()
        field_elat = self.cb_tmc_col_elat.currentText()
        field_elon = self.cb_tmc_col_elon.currentText()
        field_tmc = self.cb_tmc_col_tmc.currentText()
        dir_id = self.cb_tmc_col_dir.currentText()
        tmc_list = self.tmc_preview
        dir_list = tmc_list[dir_id].unique().tolist()
        self.map_tmc_to_pl_index = dict()
        label_str = str(dir_list)
        color_str = '[\'black\',\'red\']'
        for index, tmc_info in tmc_list.iterrows():
            if tmc_info[dir_id] == dir_list[0]:
                curr_color = '\'black\''
            else:
                curr_color = '\'red\''
            self.map_tmc_to_pl_index[tmc_info[field_tmc]] = index
            js_string = 'placeTMC('
            js_string = js_string + str(tmc_info[field_slat]) + ','
            js_string = js_string + str(tmc_info[field_slon]) + ','
            js_string = js_string + str(tmc_info[field_elat]) + ','
            js_string = js_string + str(tmc_info[field_elon]) + ','
            js_string = js_string + ' \'' + tmc_info[field_tmc] + '\'' + ','
            js_string = js_string + curr_color
            js_string = js_string + ')'
            if self.map_exists:
                self.map_view.page().runJavaScript(js_string)
        print('createLegend(' + label_str + ',' + color_str + ')')
        self.map_view.page().runJavaScript('createLegend(' + label_str + ',' + color_str + ')')
        self.map_view.page().runJavaScript('updateBounds(-1)')

