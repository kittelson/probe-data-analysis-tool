"""
Dialog that helps with importing data
"""

import os
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QThread, Qt, QDate
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QDialog, QWidget, QTabWidget, QDialogButtonBox, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import QLabel, QComboBox, QPushButton, QLineEdit, QSpinBox, QCheckBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import QFont
import pandas as pd
from DataHelper import Project
import datetime


NUM_DATA_PREV = 10


class ImportDialog(QDialog):
    def __init__(self, main_window, proj_dir_name):
        super().__init__(main_window)
        self.main_window = main_window
        self.project_dir_name = proj_dir_name
        tokens = self.project_dir_name.split('/')
        self.indicator_revert_to_master = True
        if os.path.isfile(self.project_dir_name + '/tmc_identification_master.csv'):
            self.master_file_exists = True
            response = QMessageBox.question(self.main_window, 'Custom TMC File Found',
                                            'An adjusted TMC identification file and a master TMC identification file have both been found.\n\n' +
                                            'Use the adjusted TMC list?\n(Choosing "No" will revert to the master TMC list).',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if response == QMessageBox.Yes:
                self.tmc_file_name = self.project_dir_name + '/tmc_identification.csv'
            else:
                self.tmc_file_name = self.project_dir_name + '/tmc_identification_master.csv'
                self.indicator_revert_to_master = False
        else:
            self.master_file_exists = False
            self.tmc_file_name = self.project_dir_name + '/tmc_identification.csv'
        self.data_file_name = self.project_dir_name + '/' + tokens[-1] + '.csv'
        if not os.path.isfile(self.data_file_name):
            QMessageBox.warning(None,
                                'Default Data File Not Found',
                                'A data file with the default name was not found. Please select the desired dataset file.',
                                QMessageBox.Ok, QMessageBox.Ok)
            filename, _ = QFileDialog.getOpenFileName(self, 'Select Data File', self.project_dir_name, "CSV files (*.csv)")
            if filename:
                self.data_file_name = filename
            else:
                return
        self.setWindowTitle("Import Project Data")

        self.data_inspected = False
        self.map_exists = False
        self.init_map_load = True
        self.tmc_order_adjusted = False
        self.tmc_table_init = False
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
        self.loc_label = QLabel('Enter Facility: ')
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
        self.data_res_input = QLineEdit('5')
        self.data_table = QTableWidget()
        self.data_label = QLabel("Use this controls below to ensure that the Probe Data Analytics tool is correctly reading the dataset and "
                                 "identify data columns correctly. If a data column exists,\nbut is not automatically identified, please use "
                                 "the dropdown boxes to select the correct column name.  Additionally please ensure that the resolution of the\n"
                                 "data is correct.")
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
        self.map_panel = QWidget(self.tmc_panel)
        self.map_view = QWebEngineView(self.map_panel)
        self.tmc_table = QTableWidget()
        self.tmc_table.itemSelectionChanged.connect(self.handle_table_select_changed)
        self.table_panel = QWidget(self.tmc_panel)
        self.table_button_panel = QWidget(self.table_panel)
        self.button_tmc_up = QPushButton("Move TMC Up")
        self.button_tmc_down = QPushButton("Move TMC Down")
        self.button_include_all_tmc = QPushButton("Select All TMC")
        self.button_deselect_all_tmc = QPushButton("Deselect All TMC")
        if self.indicator_revert_to_master:
            self.button_revert_to_master = QPushButton("Revert to Master List")
        else:
            self.button_revert_to_master = QPushButton('Revert to Saved Custom')
        self.tmc_label = QLabel("Use this panel to inspect the TMC data.  The TMCs can be plotted on the map below, and can be selected for inclusion"
                                "/exclusions in the table.  The TMC ordering\ncan also be adjusted if any are out of order.")
        # Creating Layouts
        self.tmc_col_layout = QGridLayout(self.tmc_col_select_panel)
        self.tmc_panel_layout = QVBoxLayout(self.tmc_panel)
        self.map_panel_layout = QHBoxLayout(self.map_panel)
        self.table_panel_layout = QHBoxLayout(self.table_panel)
        self.table_button_panel_layout = QVBoxLayout(self.table_button_panel)

        # -------- Adding tabs
        self.tab_panel.addTab(self.tmc_panel, "TMC List")
        self.tab_panel.addTab(self.data_panel, "Data Preview")

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
        self.preview_data_button.setEnabled(False)
        self.data_preview = pd.read_csv(self.data_file_name, nrows=NUM_DATA_PREV)
        self.tmc_preview = pd.read_csv(self.tmc_file_name)
        self.setup_data_panel()
        self.setup_tmc_panel()
        self.move(self.x(), self.y() - 250)

    def setup_project_info(self):
        # self.project_name_input.selectAll()
        pass

    def ok_press(self):
        adj_tmc_list = None
        if self.data_inspected:
            # Setting Dataframe column names
            Project.ID_DATA_TMC = self.cb_data_col_tmc.currentText()
            Project.ID_DATA_TIMESTAMP = self.cb_data_col_timestamp.currentText()
            Project.ID_DATA_SPEED = self.cb_data_col_speed.currentText()
            Project.ID_DATA_TT = self.cb_data_col_travel_time.currentText()
            Project.ID_DATA_RESOLUTION = int(self.data_res_input.text())
            Project.ID_TMC_CODE = self.cb_tmc_col_tmc.currentText()
            Project.ID_TMC_DIR = self.cb_tmc_col_dir.currentText()
            Project.ID_TMC_LEN = self.cb_tmc_col_len.currentText()
            Project.ID_TMC_INTX = self.cb_tmc_col_intx.currentText()
            Project.ID_TMC_SLAT = self.cb_tmc_col_slat.currentText()
            Project.ID_TMC_SLON = self.cb_tmc_col_slon.currentText()
            Project.ID_TMC_ELAT = self.cb_tmc_col_elat.currentText()
            Project.ID_TMC_ELON = self.cb_tmc_col_elon.currentText()

            #Updating TMC Inclusion and Ordering
            adj_tmc_list = []
            for ri in range(self.tmc_table.rowCount()):
                if self.tmc_table.item(ri, 0).checkState() == Qt.Checked:
                    adj_tmc_list.append(self.tmc_table.item(ri, 1).text())
            if len(adj_tmc_list) is 0:
                QMessageBox.warning(self, 'Invalid TMC Selection', 'At least one TMC must be included in the analysis.',
                                     QMessageBox.Ok, QMessageBox.Ok)
                return

        proj_info_dict = dict()
        proj_info_dict['dir'] = self.project_dir_name
        proj_info_dict['data_file_name'] = self.data_file_name
        proj_info_dict['tmc_file_name'] = self.tmc_file_name
        proj_info_dict['name'] = self.project_name_input.text()
        proj_info_dict['analyst'] = self.analyst_input.text()
        proj_info_dict['agency'] = self.agency_input.text()
        proj_info_dict['state'] = self.state_input.text()
        proj_info_dict['location'] = self.loc_input.text()
        if adj_tmc_list is not None:
            proj_info_dict['adj_tmc_list'] = adj_tmc_list
            if self.tmc_order_adjusted or len(adj_tmc_list) != self.tmc_preview[Project.ID_TMC_CODE].count():
                response = QMessageBox.question(self, 'Save TMC Adjustments?',
                                                'Save any manual reordering or inclusion/exclusion of TMCs for future use?',
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if response == QMessageBox.Yes:
                    if not os.path.isfile(self.project_dir_name + '/tmc_identification_master.csv'):
                        os.rename(self.project_dir_name + '/tmc_identification.csv', self.project_dir_name + '/tmc_identification_master.csv')

                    self.tmc_preview = self.tmc_preview[self.tmc_preview[Project.ID_TMC_CODE].isin(adj_tmc_list)]
                    self.tmc_preview.set_index(Project.ID_TMC_CODE, inplace=True)
                    self.tmc_preview = self.tmc_preview.reindex(adj_tmc_list)
                    self.tmc_preview.reset_index(level=0, inplace=True)
                    self.tmc_preview.to_csv(self.project_dir_name + '/tmc_identification.csv', index=False)
                    QMessageBox.information(self, 'TMC File Updated',
                                            'The default "tmc_identification.csv" file has now been updated.  However, the original ' +
                                            'file still exists as "tmc_identification_master.csv" in the data folder.',
                                            QMessageBox.Ok, QMessageBox.Ok)

        self.main_window.new_project_accepted(proj_info_dict, dlg=self)

    def close_press(self):
        self.close()

    def setup_data_panel(self):
        # Adding widgets to layouts
        self.data_form_layout.addRow(QLabel("TMC Column:"), self.cb_data_col_tmc)
        self.data_form_layout.addRow(QLabel("Timestamp Column:"), self.cb_data_col_timestamp)
        self.data_form_layout.addRow(QLabel("Speed Column:"), self.cb_data_col_speed)
        self.data_form_layout.addRow(QLabel("Travel Time Column:"), self.cb_data_col_travel_time)
        self.data_form_layout.addRow(QLabel('Timestep Resolution (min): '), self.data_res_input)
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

            cl2 = col_list.tolist()
            col_data_tmc = cl2.index(Project.ID_DATA_TMC) if cl2.count(Project.ID_DATA_TMC) > 0 else -1
            col_data_timestamp = cl2.index(Project.ID_DATA_TIMESTAMP) if cl2.count(Project.ID_DATA_TIMESTAMP) > 0 else -1
            col_data_speed = cl2.index(Project.ID_DATA_SPEED) if cl2.count(Project.ID_DATA_SPEED) > 0 else -1
            col_data_travel_time = cl2.index(Project.ID_DATA_TT) if cl2.count(Project.ID_DATA_TT) > 0 else -1

            self.cb_data_col_tmc.setCurrentIndex(col_data_tmc)
            self.cb_data_col_timestamp.setCurrentIndex(col_data_timestamp)
            self.cb_data_col_speed.setCurrentIndex(col_data_speed)
            self.cb_data_col_travel_time.setCurrentIndex(col_data_travel_time)

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
        self.map_panel_layout.addWidget(self.tmc_col_select_panel)
        self.map_panel_layout.addWidget(self.map_view)
        self.tmc_panel_layout.addWidget(self.tmc_label)
        self.tmc_panel_layout.addWidget(self.map_panel)
        self.tmc_table.setMinimumHeight(250)
        self.table_button_panel_layout.addWidget(self.button_tmc_up)
        self.table_button_panel_layout.addWidget(self.button_tmc_down)
        self.button_tmc_up.setEnabled(False)
        self.button_tmc_down.setEnabled(False)
        self.table_button_panel_layout.addWidget(self.button_include_all_tmc)
        self.table_button_panel_layout.addWidget(self.button_deselect_all_tmc)
        if self.master_file_exists:
            self.table_button_panel_layout.addWidget(self.button_revert_to_master)
        self.table_panel_layout.addWidget(self.tmc_table)
        self.table_panel_layout.addWidget(self.table_button_panel)
        self.tmc_panel_layout.addWidget(self.table_panel)

        # Setting up panel
        self.setup_tmc_col_select_panel()
        self.setup_tmc_preview_table()
        self.load_map_button.clicked.connect(self.add_tmcs_to_map)
        self.button_include_all_tmc.clicked.connect(self.select_all_tmcs)
        self.button_deselect_all_tmc.clicked.connect(self.deselect_all_tmcs)
        self.button_tmc_up.clicked.connect(self.move_tmc_up)
        self.button_tmc_down.clicked.connect(self.move_tmc_down)
        self.button_revert_to_master.clicked.connect(self.handle_revert_to_master)

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

            cl2 = col_list.tolist()
            col_tmc_tmc = cl2.index(Project.ID_TMC_CODE) if cl2.count(Project.ID_TMC_CODE) > 0 else -1
            col_tmc_dir = cl2.index(Project.ID_TMC_DIR) if cl2.count(Project.ID_TMC_DIR) > 0 else -1
            col_tmc_len = cl2.index(Project.ID_TMC_LEN) if cl2.count(Project.ID_TMC_LEN) > 0 else -1
            col_tmc_intx = cl2.index(Project.ID_TMC_INTX) if cl2.count(Project.ID_TMC_INTX) > 0 else -1
            col_tmc_slat = cl2.index(Project.ID_TMC_SLAT) if cl2.count(Project.ID_TMC_SLAT) > 0 else -1
            col_tmc_slon = cl2.index(Project.ID_TMC_SLON) if cl2.count(Project.ID_TMC_SLON) > 0 else -1
            col_tmc_elat = cl2.index(Project.ID_TMC_ELAT) if cl2.count(Project.ID_TMC_ELAT) > 0 else -1
            col_tmc_elon = cl2.index(Project.ID_TMC_ELON) if cl2.count(Project.ID_TMC_ELON) > 0 else -1

            self.cb_tmc_col_tmc.setCurrentIndex(col_tmc_tmc)
            self.cb_tmc_col_dir.setCurrentIndex(col_tmc_dir)
            self.cb_tmc_col_len.setCurrentIndex(col_tmc_len)
            self.cb_tmc_col_intx.setCurrentIndex(col_tmc_intx)
            self.cb_tmc_col_slat.setCurrentIndex(col_tmc_slat)
            self.cb_tmc_col_slon.setCurrentIndex(col_tmc_slon)
            self.cb_tmc_col_elat.setCurrentIndex(col_tmc_elat)
            self.cb_tmc_col_elon.setCurrentIndex(col_tmc_elon)

    def setup_tmc_preview_table(self):
        if self.tmc_preview is not None:
            self.tmc_table_init = True
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
                    self.tmc_table.setItem(index, col_idx + 1, item)
            self.tmc_table_init = False
            self.tmc_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tmc_table.cellChanged.connect(self.handle_cell_changed)
            self.tmc_table.resizeColumnsToContents()

    def load_map(self):
        f_name = os.path.realpath('templates/map_gen.html')
        self.map_view.loadFinished.connect(self.map_loaded)
        self.map_view.load(QUrl('file:///' + f_name.replace('\\', '/')))

    def map_loaded(self):
        self.map_exists = True
        self.add_tmcs_to_map()


    def zoom_map_to_full_extent(self):
        if self.map_exists:
            self.map_view.page().runJavaScript('updateBounds(-1)')

    def reset_map(self):
        if self.map_exists:
            self.map_view.page().runJavaScript('clear_map()')
            self.add_tmcs_to_map()

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
            js_string = js_string + ' \'#' + str(index + 1) + ') ' + tmc_info[field_tmc] + '\'' + ','
            js_string = js_string + curr_color
            js_string = js_string + ')'
            if self.map_exists:
                self.map_view.page().runJavaScript(js_string)
        print('createLegend(' + label_str + ',' + color_str + ')')
        self.map_view.page().runJavaScript('createLegend(' + label_str + ',' + color_str + ')')
        self.map_view.page().runJavaScript('updateBounds(-1)')
        if self.init_map_load:
            self.init_map_load = False
            self.load_map_button.setText('Zoom to Full Extent')
            self.load_map_button.clicked.disconnect()
            self.load_map_button.clicked.connect(self.zoom_map_to_full_extent)

    def handle_cell_changed(self, row, col):
        if not self.tmc_table_init and self.map_exists and col == 0:
            if self.tmc_table.item(row, col).checkState() == Qt.Unchecked:
                self.map_view.page().runJavaScript('hideTMC(' + str(row) + ')')
            else:
                self.map_view.page().runJavaScript('showTMC(' + str(row) + ')')

    def handle_table_select_changed(self):
        sel_row = self.tmc_table.currentRow()
        if sel_row > 0:
            self.button_tmc_up.setEnabled(True)
        else:
            self.button_tmc_up.setEnabled(False)
        if 0 <= sel_row < self.tmc_table.rowCount() - 1:
            self.button_tmc_down.setEnabled(True)
        else:
            self.button_tmc_down.setEnabled(False)
        if self.map_exists:
            if 0 <= sel_row < self.tmc_table.rowCount():
                self.map_view.page().runJavaScript('highlightTMC(' + str(sel_row) + ')')
            else:
                self.button_tmc_down.setEnabled('highlightTMC(-1)')


    def select_all_tmcs(self):
        self.change_all_tmc_selection(True)

    def deselect_all_tmcs(self):
        self.change_all_tmc_selection(False)

    def change_all_tmc_selection(self, isSelected):
        if isSelected:
            cs = Qt.Checked
        else:
            cs = Qt.Unchecked
        if self.tmc_table is not None:
            for ri in range(self.tmc_table.rowCount()):
                self.tmc_table.item(ri, 0).setCheckState(cs)

    def move_tmc_up(self):
        sel_row = self.tmc_table.currentItem().row()
        self.adjust_tmc_order(sel_row, -1)

    def move_tmc_down(self):
        sel_row = self.tmc_table.currentItem().row()
        self.adjust_tmc_order(sel_row, 1)

    def adjust_tmc_order(self, tmc_idx, pos_adj):
        if self.tmc_table is not None:
            self.tmc_table_init = True
            self.tmc_order_adjusted = True
            new_row_i = tmc_idx + pos_adj
            for ci in range(self.tmc_table.columnCount()):
                src_row_item = self.tmc_table.takeItem(tmc_idx, ci)
                dest_row_item = self.tmc_table.takeItem(new_row_i, ci)
                self.tmc_table.setItem(tmc_idx, ci, dest_row_item)
                self.tmc_table.setItem(new_row_i, ci, src_row_item)
            self.tmc_table_init = False
            self.tmc_table.selectRow(new_row_i)

    def handle_revert_to_master(self):
        if self.indicator_revert_to_master:
            response = QMessageBox.question(self,
                                             'Revert to Master TMC List',
                                             'This will load in the list of TMCs from the full "master" TMC identification file located in the '+
                                             'data directory and override any ordering adjustment or inclusion/exclusion preferences.\n\n' +
                                             'Proceed?',
                                             QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            if response == QMessageBox.Ok:
                self.tmc_file_name = self.project_dir_name + '/tmc_identification_master.csv'
                self.tmc_preview = pd.read_csv(self.tmc_file_name)
                self.setup_tmc_preview_table()
                self.button_revert_to_master.setText('Revert to Saved Custom')
                self.indicator_revert_to_master = False
        else:
            response = QMessageBox.question(self,
                                            'Revert to Saved Custom TMC List',
                                            'This will load in the list of TMCs from the saved "custom" TMC identification file located in the ' +
                                            'data directory and apply any ordering adjustment or inclusion/exclusion preferences.\n\n' +
                                            'Proceed?',
                                            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            if response == QMessageBox.Ok:
                self.tmc_file_name = self.project_dir_name + '/tmc_identification.csv'
                self.tmc_preview = pd.read_csv(self.tmc_file_name)
                self.setup_tmc_preview_table()
                self.button_revert_to_master.setText('Revert to Master TMC List')
                self.indicator_revert_to_master = True
        self.reset_map()


class EditInfoDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.project = main_window.project
        self.setWindowTitle('Enter Project Information')

        l = QFormLayout(self)
        project_name_label = QLabel('Project Name: ')
        project_name_label.setFont(QFont("Times", weight=QFont.Bold))
        self.project_name_input = QLineEdit(self.project.get_name())
        analyst_label = QLabel('Enter Analyst Name: ')
        analyst_label.setFont(QFont("Times", weight=QFont.Bold))
        self.analyst_input = QLineEdit(self.project.get_analyst())
        agency_label = QLabel('Enter Agency: ')
        agency_label.setFont(QFont("Times", weight=QFont.Bold))
        self.agency_input = QLineEdit(self.project.get_agency())
        speed_limit_label = QLabel('Speed Limit (mph): ')
        speed_limit_label.setFont(QFont("Times", weight=QFont.Bold))
        self.speed_limit_input = QLineEdit(str(self.project.speed_limit))
        # speed_lower_label = QLabel('Lower Limit Speed (mph): ')
        # speed_lower_label.setFont(QFont("Times", weight=QFont.Bold))
        # self.speed_lower_input = QLineEdit(str(self.project.min_speed))
        # speed_upper_label = QLabel('Upper Limit Speed (mph): ')
        # speed_upper_label.setFont(QFont("Times", weight=QFont.Bold))
        # self.speed_upper_input = QLineEdit(str(self.project.max_speed))
        l.addRow(project_name_label, self.project_name_input)
        l.addRow(analyst_label, self.analyst_input)
        l.addRow(agency_label, self.agency_input)
        l.addRow(speed_limit_label, self.speed_limit_input)
        # l.addRow(speed_lower_label, self.speed_lower_input)
        # l.addRow(speed_upper_label, self.speed_upper_input)
        buttons = QDialogButtonBox(Qt.Horizontal, self)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.ok_press)
        buttons.rejected.connect(self.close_press)
        l.addWidget(buttons)

    def ok_press(self):
        proj_info_dict = dict()
        proj_info_dict['name'] = self.project_name_input.text()
        proj_info_dict['analyst'] = self.analyst_input.text()
        proj_info_dict['agency'] = self.agency_input.text()
        # proj_info_dict['state'] = self.state_input
        # proj_info_dict['location'] = self.loc_input
        proj_info_dict['speed_limit'] = float(self.speed_limit_input.text())
        # proj_info_dict['speed_lower'] = float(self.speed_lower_input.text())
        # proj_info_dict['speed_upper'] = float(self.speed_upper_input.text())

        self.main_window.set_project_info(proj_info_dict, dlg=self)

    def close_press(self):
        self.close()


class EditDQChartOptionsDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.project = main_window.project
        self.setWindowTitle('Edit Data Availability Chart Options')

        l = QFormLayout(self)
        title_label = QLabel('Specify the desired data quality thresholds:')
        title_label.setFont(QFont("Times", weight=QFont.Bold))
        show_thresh_label = QLabel('Show Thresholds on Chart: ')
        show_thresh_label.setFont(QFont("Times", weight=QFont.Bold))
        self.show_thresh_check = QCheckBox()
        self.show_thresh_check.setChecked(self.project.show_avail_threshold)
        upper_thresh_label = QLabel('Desired Threshold: ')
        upper_thresh_label.setFont(QFont("Times", weight=QFont.Bold))
        self.upper_thresh_input = QSpinBox()
        self.upper_thresh_input.setRange(0, 100)
        self.upper_thresh_input.setValue(int(self.project.data_avail_threshold_upper * 100))
        self.upper_thresh_input.setSingleStep(5)
        self.upper_thresh_input.setSuffix(' %')
        lower_thresh_label = QLabel('Warning Threshold: ')
        lower_thresh_label.setFont(QFont("Times", weight=QFont.Bold))
        self.lower_thresh_input = QSpinBox()
        self.lower_thresh_input.setRange(0, 100)
        self.lower_thresh_input.setValue(int(self.project.data_avail_threshold_lower * 100))
        self.lower_thresh_input.setSingleStep(5)
        self.lower_thresh_input.setSuffix(' %')

        l.addRow(title_label)
        l.addRow(show_thresh_label, self.show_thresh_check)
        l.addRow(upper_thresh_label, self.upper_thresh_input)
        l.addRow(lower_thresh_label, self.lower_thresh_input)
        buttons = QDialogButtonBox(Qt.Horizontal, self)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.ok_press)
        buttons.rejected.connect(self.close_press)
        l.addWidget(buttons)

    def ok_press(self):
        if self.upper_thresh_input.value() >= self.lower_thresh_input.value():
            self.project.data_avail_threshold_upper = self.upper_thresh_input.value() / 100.0
            self.project.data_avail_threshold_lower = self.lower_thresh_input.value() / 100.0
            self.project.show_avail_threshold = self.show_thresh_check.isChecked()
            self.main_window.dq_chart_panel.update_figures()
            self.close()
        else:
            QMessageBox.warning(self,
                                'Invalid Values',
                                'The Desired Threshold must be greater than or equal to the Warning Threshold.',
                                QMessageBox.Ok, QMessageBox.Ok)

    def close_press(self):
        self.close()


class EditStage1ChartsDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.project = main_window.project
        self.setWindowTitle('Edit Stage 1.2 - 1.4 Chart Options')

        l = QFormLayout(self)
        speed_lower_label = QLabel('Lower Limit Speed (mph): ')
        speed_lower_label.setFont(QFont("Times", weight=QFont.Bold))
        self.speed_lower_input = QSpinBox()
        self.speed_lower_input.setRange(5, 100)
        self.speed_lower_input.setValue(int(self.project.min_speed))
        self.speed_lower_input.setSingleStep(5)
        self.speed_lower_input.setSuffix(' mph')
        speed_upper_label = QLabel('Upper Limit Speed (mph): ')
        speed_upper_label.setFont(QFont("Times", weight=QFont.Bold))
        self.speed_upper_input = QSpinBox()
        self.speed_upper_input.setRange(5, 100)
        self.speed_upper_input.setValue(int(self.project.max_speed))
        self.speed_upper_input.setSingleStep(5)
        self.speed_upper_input.setSuffix(' mph')
        l.addRow(speed_lower_label, self.speed_lower_input)
        l.addRow(speed_upper_label, self.speed_upper_input)
        buttons = QDialogButtonBox(Qt.Horizontal, self)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.ok_press)
        buttons.rejected.connect(self.close_press)
        l.addWidget(buttons)

    def ok_press(self):
        if self.speed_upper_input.value() > self.speed_lower_input.value():
            self.project.max_speed = self.speed_upper_input.value()
            self.project.min_speed = self.speed_lower_input.value()
            self.main_window.redraw_charts()
            self.close()
        else:
            QMessageBox.warning(self,
                                'Invalid Values',
                                'The upper limit speed must be greater than or equal to the lower limit.',
                                QMessageBox.Ok, QMessageBox.Ok)

    def close_press(self):
        self.close()


class EditPeriodOptionsDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.project = main_window.project
        self.setWindowTitle('Edit Trend Time Periods')

        l = QFormLayout(self)
        title_label = QLabel('Specify start and end times for each period:')
        title_label.setFont(QFont("Times", weight=QFont.Bold))
        midnight = datetime.datetime(2000, 1, 1, 0, 0, 0)
        ap_list = [(midnight + datetime.timedelta(minutes=self.project.data_res * i)).strftime('%I:%M%p') for i in
                   range(24 * 60 // self.project.data_res)]
        p1_start_label = QLabel('AM (Period 1) Start:')
        p1_start_label.setFont(QFont("Times", weight=QFont.Bold))
        self.p1_start_cb = QComboBox()
        self.p1_start_cb.addItems(ap_list)
        p1_end_label = QLabel('AM (Period 1) End:')
        p1_end_label.setFont(QFont("Times", weight=QFont.Bold))
        self.p1_end_cb = QComboBox()
        self.p1_end_cb.addItems(ap_list)
        p2_start_label = QLabel('Midday (Period 2) Start:')
        p2_start_label.setFont(QFont("Times", weight=QFont.Bold))
        self.p2_start_cb = QComboBox()
        self.p2_start_cb.addItems(ap_list)
        p2_end_label = QLabel('Midday (Period 2) End:')
        p2_end_label.setFont(QFont("Times", weight=QFont.Bold))
        self.p2_end_cb = QComboBox()
        self.p2_end_cb.addItems(ap_list)
        p3_start_label = QLabel('PM (Period 3) Start:')
        p3_start_label.setFont(QFont("Times", weight=QFont.Bold))
        self.p3_start_cb = QComboBox()
        self.p3_start_cb.addItems(ap_list)
        p3_end_label = QLabel('PM (Period 3) End:')
        p3_end_label.setFont(QFont("Times", weight=QFont.Bold))
        self.p3_end_cb = QComboBox()
        self.p3_end_cb.addItems(ap_list)

        self.p1_start_cb.setCurrentIndex(self.project.p1_ap_start)
        self.p1_end_cb.setCurrentIndex(self.project.p1_ap_end)
        self.p2_start_cb.setCurrentIndex(self.project.p2_ap_start)
        self.p2_end_cb.setCurrentIndex(self.project.p2_ap_end)
        self.p3_start_cb.setCurrentIndex(self.project.p3_ap_start)
        self.p3_end_cb.setCurrentIndex(self.project.p3_ap_end)

        l.addRow(title_label)
        l.addRow(p1_start_label, self.p1_start_cb)
        l.addRow(p1_end_label, self.p1_end_cb)
        l.addRow(p2_start_label, self.p2_start_cb)
        l.addRow(p2_end_label, self.p2_end_cb)
        l.addRow(p3_start_label, self.p3_start_cb)
        l.addRow(p3_end_label, self.p3_end_cb)
        buttons = QDialogButtonBox(Qt.Horizontal, self)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.ok_press)
        buttons.rejected.connect(self.close_press)
        l.addWidget(buttons)

    def ok_press(self):
        if self.p1_start_cb.currentIndex() < self.p1_end_cb.currentIndex() \
                and self.p2_start_cb.currentIndex() < self.p2_end_cb.currentIndex() \
                and self.p3_start_cb.currentIndex() < self.p3_end_cb.currentIndex():
            self.project.p1_ap_start = self.p1_start_cb.currentIndex()
            self.project.p1_ap_end = self.p1_end_cb.currentIndex()
            self.project.p2_ap_start = self.p2_start_cb.currentIndex()
            self.project.p2_ap_end = self.p2_end_cb.currentIndex()
            self.project.p3_ap_start = self.p3_start_cb.currentIndex()
            self.project.p3_ap_end = self.p3_end_cb.currentIndex()
            self.main_window.chart_panel1_4.check_time_periods_changed(True)
            self.close()
        else:
            QMessageBox.warning(self,
                                'Invalid Values',
                                'All period end times must be after the period start times.',
                                QMessageBox.Ok, QMessageBox.Ok)

    def close_press(self):
        self.close()

