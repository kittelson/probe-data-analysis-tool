from PyQt5 import QtWidgets
from stat_func import create_et_analysis, create_speed_band, create_travel_time_cdf, create_speed_cdf, create_speed_freq
from chart_defaults import ChartOptions, AnalysisOptions
from mpl_panels import create_spacer_line
from mpl_charts import MplChart, FIG_TYPE_SPD_BAND, FIG_TYPE_EXTRA_TIME, FIG_TYPE_SPD_FREQ, FIG_TYPE_TT_CDF
from mpl_charts import PEAK_24HR, PEAK_AM, PEAK_PM, PEAK_MID
from viz_qt import LoadStage2QT, LoadSummaryQT
from DataHelper import SummaryData, Project
import datetime
import pandas as pd
from numpy import mean, percentile


class Stage2GridPanel(QtWidgets.QWidget):
    def __init__(self, project, chart_options=None, analysis_options=None):
        QtWidgets.QWidget.__init__(self)

        self.f_extra_time = create_et_analysis
        self.f_speed_band = create_speed_band
        # self.f_tt_cdf = create_travel_time_cdf
        self.f_tt_cdf = create_speed_cdf
        self.f_speed_freq = create_speed_freq

        self.chart_et = None
        self.chart_sb_before = None
        self.chart_sb_after = None
        self.chart_speed_freq = None
        self.chart_cdf = None

        self.panel_col1 = QtWidgets.QWidget(self)
        self.panel_col2 = QtWidgets.QWidget(self)
        self.chart_panel = QtWidgets.QWidget(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout(self.chart_panel)

        self.panel2 = None

        self.init_mode = True
        self.no_compute = True
        self.project = project
        full_df = self.project.database.get_data()
        df = full_df[full_df[Project.ID_DATA_TMC].isin(self.project.get_tmc()[Project.ID_TMC_CODE])]
        # dr1 = self.project.get_date_range(0)
        # df_period1 = df[(df['Date'] >= dr1[0].toString('yyyy-MM-dd')) & (df['Date'] <= dr1[1].toString('yyyy-MM-dd'))]
        # dr2 = self.project.get_date_range(1)
        # df_period2 = df[(df['Date'] > dr2[0].toString('yyyy-MM-dd')) & (df['Date'] < dr2[1].toString('yyyy-MM-dd'))]
        dr1 = self.project.get_date_range(0)
        dr2 = self.project.get_date_range(1)
        per1_sdate = datetime.datetime(dr1[0].year(), dr1[0].month(), dr1[0].day())
        per1_edate = datetime.datetime(dr1[1].year(), dr1[1].month(), dr1[1].day())
        per2_sdate = datetime.datetime(dr2[0].year(), dr2[0].month(), dr2[0].day())
        per2_edate = datetime.datetime(dr2[1].year(), dr2[1].month(), dr2[1].day())
        temp_date_col = pd.to_datetime(df['Date'])
        df_period1 = df[(temp_date_col >= per1_sdate) & (temp_date_col <= per1_edate)]
        df_period2 = df[(temp_date_col >= per2_sdate) & (temp_date_col <= per2_edate)]
        self.period1 = dr1[0].toString('yyyy-MM-dd') + ' to ' + dr1[1].toString('yyyy-MM-dd')
        self.period2 = dr2[0].toString('yyyy-MM-dd') + ' to ' + dr2[1].toString('yyyy-MM-dd')
        tmc = self.project.database.get_tmcs()
        self.facility_len = tmc[Project.ID_TMC_LEN].sum()
        self.dfs = [df_period1, df_period2]
        # self.dfs = [self.f_extra_time(df) for df in self.dfs]
        # self.dfs = [self.f_extra_time(df_period1), self.f_extra_time(df_period2)]
        # self.tmc_subset = []
        # self.facility_len_subset = tmc[tmc['tmc'].isin(self.tmc_subset)]['miles'].sum()
        tmc = self.project.get_tmc()
        self.selected_tmc_name = tmc[Project.ID_TMC_CODE][0]
        self.selected_tmc_len = tmc[Project.ID_TMC_LEN][0]
        self.selected_peak = PEAK_24HR
        self.am_ap_start = convert_time_to_ap(6, 0, self.project.data_res)
        self.am_ap_end = convert_time_to_ap(9, 0, self.project.data_res)
        self.pm_ap_start = convert_time_to_ap(16, 0, self.project.data_res)
        self.pm_ap_end = convert_time_to_ap(18, 0, self.project.data_res)
        self.md_ap_start = convert_time_to_ap(10, 0, self.project.data_res)
        self.md_ap_end = convert_time_to_ap(16, 0, self.project.data_res)
        self.available_days = self.project.database.get_available_days()
        self.plot_days = self.available_days.copy()
        if chart_options is not None:
            self.chart_options = chart_options
        else:
            self.chart_options = ChartOptions()

        if analysis_options is not None:
            self.analysis_options = analysis_options
        else:
            self.analysis_options = AnalysisOptions()

        self.chart_options.chart_type[0][0] = FIG_TYPE_EXTRA_TIME
        self.chart_options.chart_type[0][1] = FIG_TYPE_TT_CDF
        self.chart_options.chart_type[1][0] = FIG_TYPE_SPD_BAND
        self.chart_options.chart_type[1][1] = FIG_TYPE_SPD_BAND  # FIG_TYPE_SPD_FREQ

        # Filter Components
        # self.cb_tmc_select = QtWidgets.QComboBox()
        # self.cb_tmc_select.addItems(self.project.get_tmc(as_list=True))
        self.bg_day_select = QtWidgets.QButtonGroup(self)
        self.check_wkdy = QtWidgets.QRadioButton('Weekdays')
        self.check_wknd = QtWidgets.QRadioButton("Weekends")
        self.check_mon = QtWidgets.QRadioButton('Mon')
        self.check_tue = QtWidgets.QRadioButton('Tue')
        self.check_wed = QtWidgets.QRadioButton('Wed')
        self.check_thu = QtWidgets.QRadioButton('Thu')
        self.check_fri = QtWidgets.QRadioButton('Fri')
        self.check_sat = QtWidgets.QRadioButton('Sat')
        self.check_sun = QtWidgets.QRadioButton('Sun')
        self.bg_day_select.addButton(self.check_wkdy)
        self.bg_day_select.addButton(self.check_wknd)
        self.bg_day_select.addButton(self.check_mon)
        self.bg_day_select.addButton(self.check_tue)
        self.bg_day_select.addButton(self.check_wed)
        self.bg_day_select.addButton(self.check_thu)
        self.bg_day_select.addButton(self.check_fri)
        self.bg_day_select.addButton(self.check_sat)
        self.bg_day_select.addButton(self.check_sun)
        self.check_bar_day = QtWidgets.QWidget(self)
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar_day)
        # self.h_layout.addWidget(self.cb_tmc_select)
        # self.h_layout.addWidget(create_spacer_line(self))
        self.h_layout.addWidget(self.check_wkdy)
        self.h_layout.addWidget(self.check_wknd)
        self.h_layout.addWidget(create_spacer_line(self))
        self.h_layout.addWidget(self.check_mon)
        self.h_layout.addWidget(self.check_tue)
        self.h_layout.addWidget(self.check_wed)
        self.h_layout.addWidget(self.check_thu)
        self.h_layout.addWidget(self.check_fri)
        self.h_layout.addWidget(self.check_sat)
        self.h_layout.addWidget(self.check_sun)
        # self.connect_check_boxes()
        self.connect_radio_buttons()
        # self.connect_combo_boxes()

        self.day_select = 0
        self.plot_dfs = []
        self.plot_dfs2 = []
        self.plot_dfs3 = []
        self.plot_dfs4 = []
        self.plot_dfs5 = []
        self.update_plot_data()
        # self.create_charts()
        # self.add_charts_to_layouts()
        # self.v_layout.addWidget(self.chart_panel)
        # self.v_layout.addWidget(self.check_bar_day)
        # self.update_chart_visibility()
        # self.init_mode = False
        # self.no_compute = False

    def create_second_panel(self):
        self.panel2 = QtWidgets.QWidget()
        v_layout = QtWidgets.QVBoxLayout(self.panel2)
        v_layout.addWidget(self.chart_cdf)
        v_layout.addWidget(self.chart_speed_freq)
        bg_day_select = QtWidgets.QButtonGroup(self.panel2)
        self.check_wkdy2 = QtWidgets.QRadioButton('Weekdays')
        self.check_wknd2 = QtWidgets.QRadioButton("Weekends")
        self.check_mon2 = QtWidgets.QRadioButton('Mon')
        self.check_tue2 = QtWidgets.QRadioButton('Tue')
        self.check_wed2 = QtWidgets.QRadioButton('Wed')
        self.check_thu2 = QtWidgets.QRadioButton('Thu')
        self.check_fri2 = QtWidgets.QRadioButton('Fri')
        self.check_sat2 = QtWidgets.QRadioButton('Sat')
        self.check_sun2 = QtWidgets.QRadioButton('Sun')
        bg_day_select.addButton(self.check_wkdy2)
        bg_day_select.addButton(self.check_wknd2)
        bg_day_select.addButton(self.check_mon2)
        bg_day_select.addButton(self.check_tue2)
        bg_day_select.addButton(self.check_wed2)
        bg_day_select.addButton(self.check_thu2)
        bg_day_select.addButton(self.check_fri2)
        bg_day_select.addButton(self.check_sat2)
        bg_day_select.addButton(self.check_sun2)
        bg_peak_select = QtWidgets.QButtonGroup(self.panel2)
        self.check_24hr2 = QtWidgets.QRadioButton('24-Hour')
        self.check_am2 = QtWidgets.QRadioButton('AM')
        self.check_md2 = QtWidgets.QRadioButton('Midday')
        self.check_pm2 = QtWidgets.QRadioButton('PM')
        bg_peak_select.addButton(self.check_24hr2)
        bg_peak_select.addButton(self.check_am2)
        bg_peak_select.addButton(self.check_md2)
        bg_peak_select.addButton(self.check_pm2)
        check_bar_day = QtWidgets.QWidget(self.panel2)
        h_layout = QtWidgets.QHBoxLayout(check_bar_day)
        h_layout.addWidget(self.check_wkdy2)
        h_layout.addWidget(self.check_wknd2)
        h_layout.addWidget(create_spacer_line(self.panel2))
        h_layout.addWidget(self.check_mon2)
        h_layout.addWidget(self.check_tue2)
        h_layout.addWidget(self.check_wed2)
        h_layout.addWidget(self.check_thu2)
        h_layout.addWidget(self.check_fri2)
        h_layout.addWidget(self.check_sat2)
        h_layout.addWidget(self.check_sun2)
        h_layout.addWidget(create_spacer_line(self.panel2))
        h_layout.addWidget(self.check_24hr2)
        h_layout.addWidget(self.check_am2)
        h_layout.addWidget(self.check_md2)
        h_layout.addWidget(self.check_pm2)
        # self.connect_radio_buttons()
        self.check_wkdy2.setChecked(True)
        self.check_24hr2.setChecked(True)
        self.check_wkdy2.toggled.connect(lambda: self.toggle_func2(0, self.check_wkdy2))
        self.check_wknd2.toggled.connect(lambda: self.toggle_func2(1, self.check_wknd2))
        self.check_mon2.toggled.connect(lambda: self.toggle_func2(2, self.check_mon2))
        self.check_tue2.toggled.connect(lambda: self.toggle_func2(3, self.check_tue2))
        self.check_wed2.toggled.connect(lambda: self.toggle_func2(4, self.check_wed2))
        self.check_thu2.toggled.connect(lambda: self.toggle_func2(5, self.check_thu2))
        self.check_fri2.toggled.connect(lambda: self.toggle_func2(6, self.check_fri2))
        self.check_sat2.toggled.connect(lambda: self.toggle_func2(7, self.check_sat2))
        self.check_sun2.toggled.connect(lambda: self.toggle_func2(8, self.check_sun2))
        self.check_24hr2.toggled.connect(lambda: self.toggle_func_peak2(PEAK_24HR, self.check_24hr2))
        self.check_am2.toggled.connect(lambda: self.toggle_func_peak2(PEAK_AM, self.check_am2))
        self.check_md2.toggled.connect(lambda: self.toggle_func_peak2(PEAK_MID, self.check_md2))
        self.check_pm2.toggled.connect(lambda: self.toggle_func_peak2(PEAK_PM, self.check_pm2))
        v_layout.addWidget(check_bar_day)
        self.project.main_window.ui.tabWidget.addTab(self.panel2, '2 - Speed CDF/Frequency')
        self.project.main_window.stage2panel_2 = self.panel2

    def update_plot_data(self, **kwargs):
        before_df = self.dfs[0]
        after_df = self.dfs[1]

        func_dict = dict()

        wkdy_data_b = before_df[before_df['weekday'].isin([0, 1, 2, 3, 4])]
        wknd_data_b = before_df[before_df['weekday'].isin([5, 6])]
        mon_data_b = wkdy_data_b[wkdy_data_b['weekday'] == 0]
        tue_data_b = wkdy_data_b[wkdy_data_b['weekday'] == 1]
        wed_data_b = wkdy_data_b[wkdy_data_b['weekday'] == 2]
        thu_data_b = wkdy_data_b[wkdy_data_b['weekday'] == 3]
        fri_data_b = wkdy_data_b[wkdy_data_b['weekday'] == 4]
        sat_data_b = wknd_data_b[wknd_data_b['weekday'] == 5]
        sun_data_b = wknd_data_b[wknd_data_b['weekday'] == 6]

        wkdy_data_a = after_df[after_df['weekday'].isin([0, 1, 2, 3, 4])]
        wknd_data_a = after_df[after_df['weekday'].isin([5, 6])]
        mon_data_a = wkdy_data_a[wkdy_data_a['weekday'] == 0]
        tue_data_a = wkdy_data_a[wkdy_data_a['weekday'] == 1]
        wed_data_a = wkdy_data_a[wkdy_data_a['weekday'] == 2]
        thu_data_a = wkdy_data_a[wkdy_data_a['weekday'] == 3]
        fri_data_a = wkdy_data_a[wkdy_data_a['weekday'] == 4]
        sat_data_a = wknd_data_a[wknd_data_a['weekday'] == 5]
        sun_data_a = wknd_data_a[wknd_data_a['weekday'] == 6]
        # time4 = time.time()
        # print('Day filter: ' + str(time4 - time3))

        func_dict['Extra Time'] = [lambda: self.f_extra_time(wkdy_data_b),
                                   lambda: self.f_extra_time(wknd_data_b),
                                   lambda: self.f_extra_time(mon_data_b),
                                   lambda: self.f_extra_time(tue_data_b),
                                   lambda: self.f_extra_time(wed_data_b),
                                   lambda: self.f_extra_time(thu_data_b),
                                   lambda: self.f_extra_time(fri_data_b),
                                   lambda: self.f_extra_time(sat_data_b),
                                   lambda: self.f_extra_time(sun_data_b),
                                   lambda: self.f_extra_time(wkdy_data_a),
                                   lambda: self.f_extra_time(wknd_data_a),
                                   lambda: self.f_extra_time(mon_data_a),
                                   lambda: self.f_extra_time(tue_data_a),
                                   lambda: self.f_extra_time(wed_data_a),
                                   lambda: self.f_extra_time(thu_data_a),
                                   lambda: self.f_extra_time(fri_data_a),
                                   lambda: self.f_extra_time(sat_data_a),
                                   lambda: self.f_extra_time(sun_data_a)
                                   ]

        func_dict['Speed Band'] = [lambda: self.f_speed_band(wkdy_data_b),
                                   lambda: self.f_speed_band(wknd_data_b),
                                   lambda: self.f_speed_band(mon_data_b),
                                   lambda: self.f_speed_band(tue_data_b),
                                   lambda: self.f_speed_band(wed_data_b),
                                   lambda: self.f_speed_band(thu_data_b),
                                   lambda: self.f_speed_band(fri_data_b),
                                   lambda: self.f_speed_band(sat_data_b),
                                   lambda: self.f_speed_band(sun_data_b),
                                   lambda: self.f_speed_band(wkdy_data_a),
                                   lambda: self.f_speed_band(wknd_data_a),
                                   lambda: self.f_speed_band(mon_data_a),
                                   lambda: self.f_speed_band(tue_data_a),
                                   lambda: self.f_speed_band(wed_data_a),
                                   lambda: self.f_speed_band(thu_data_a),
                                   lambda: self.f_speed_band(fri_data_a),
                                   lambda: self.f_speed_band(sat_data_a),
                                   lambda: self.f_speed_band(sun_data_a)
                                   ]

        func_dict['Cumulative Distribution'] = [lambda: self.f_tt_cdf(wkdy_data_b),
                                                lambda: self.f_tt_cdf(wknd_data_b),
                                                lambda: self.f_tt_cdf(mon_data_b),
                                                lambda: self.f_tt_cdf(tue_data_b),
                                                lambda: self.f_tt_cdf(wed_data_b),
                                                lambda: self.f_tt_cdf(thu_data_b),
                                                lambda: self.f_tt_cdf(fri_data_b),
                                                lambda: self.f_tt_cdf(sat_data_b),
                                                lambda: self.f_tt_cdf(sun_data_b),
                                                lambda: self.f_tt_cdf(wkdy_data_a),
                                                lambda: self.f_tt_cdf(wknd_data_a),
                                                lambda: self.f_tt_cdf(mon_data_a),
                                                lambda: self.f_tt_cdf(tue_data_a),
                                                lambda: self.f_tt_cdf(wed_data_a),
                                                lambda: self.f_tt_cdf(thu_data_a),
                                                lambda: self.f_tt_cdf(fri_data_a),
                                                lambda: self.f_tt_cdf(sat_data_a),
                                                lambda: self.f_tt_cdf(sun_data_a)
                                                ]

        func_dict['Speed Frequency'] = [lambda: self.f_speed_freq(wkdy_data_b),
                                        lambda: self.f_speed_freq(wknd_data_b),
                                        lambda: self.f_speed_freq(mon_data_b),
                                        lambda: self.f_speed_freq(tue_data_b),
                                        lambda: self.f_speed_freq(wed_data_b),
                                        lambda: self.f_speed_freq(thu_data_b),
                                        lambda: self.f_speed_freq(fri_data_b),
                                        lambda: self.f_speed_freq(sat_data_b),
                                        lambda: self.f_speed_freq(sun_data_b),
                                        lambda: self.f_speed_freq(wkdy_data_a),
                                        lambda: self.f_speed_freq(wknd_data_a),
                                        lambda: self.f_speed_freq(mon_data_a),
                                        lambda: self.f_speed_freq(tue_data_a),
                                        lambda: self.f_speed_freq(wed_data_a),
                                        lambda: self.f_speed_freq(thu_data_a),
                                        lambda: self.f_speed_freq(fri_data_a),
                                        lambda: self.f_speed_freq(sat_data_a),
                                        lambda: self.f_speed_freq(sun_data_a)
                                        ]

        ams = convert_time_to_ap(6, 0, self.project.data_res)
        ame = convert_time_to_ap(10, 0, self.project.data_res)
        mds = convert_time_to_ap(10, 0, self.project.data_res)
        mde = convert_time_to_ap(15, 0, self.project.data_res)
        pms = convert_time_to_ap(15, 0, self.project.data_res)
        pme = convert_time_to_ap(19, 0, self.project.data_res)
        func_dict['Speed CDF Peak'] = [lambda: self.f_tt_cdf(wkdy_data_b[(wkdy_data_b['AP'] >= ams) & (wkdy_data_b['AP'] < ame)]),  # AM Peak
                                       lambda: self.f_tt_cdf(wknd_data_b[(wknd_data_b['AP'] >= ams) & (wknd_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(mon_data_b[(mon_data_b['AP'] >= ams) & (mon_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(tue_data_b[(tue_data_b['AP'] >= ams) & (tue_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(wed_data_b[(wed_data_b['AP'] >= ams) & (wed_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(thu_data_b[(thu_data_b['AP'] >= ams) & (thu_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(fri_data_b[(fri_data_b['AP'] >= ams) & (fri_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(sat_data_b[(sat_data_b['AP'] >= ams) & (sat_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(sun_data_b[(sun_data_b['AP'] >= ams) & (sun_data_b['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(wkdy_data_a[(wkdy_data_a['AP'] >= ams) & (wkdy_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(wknd_data_a[(wknd_data_a['AP'] >= ams) & (wknd_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(mon_data_a[(mon_data_a['AP'] >= ams) & (mon_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(tue_data_a[(tue_data_a['AP'] >= ams) & (tue_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(wed_data_a[(wed_data_a['AP'] >= ams) & (wed_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(thu_data_a[(thu_data_a['AP'] >= ams) & (thu_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(fri_data_a[(fri_data_a['AP'] >= ams) & (fri_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(sat_data_a[(sat_data_a['AP'] >= ams) & (sat_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(sun_data_a[(sun_data_a['AP'] >= ams) & (sun_data_a['AP'] < ame)]),
                                       lambda: self.f_tt_cdf(wkdy_data_b[(wkdy_data_b['AP'] >= mds) & (wkdy_data_b['AP'] < mde)]),  # Md Peak
                                       lambda: self.f_tt_cdf(wknd_data_b[(wknd_data_b['AP'] >= mds) & (wknd_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(mon_data_b[(mon_data_b['AP'] >= mds) & (mon_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(tue_data_b[(tue_data_b['AP'] >= mds) & (tue_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(wed_data_b[(wed_data_b['AP'] >= mds) & (wed_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(thu_data_b[(thu_data_b['AP'] >= mds) & (thu_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(fri_data_b[(fri_data_b['AP'] >= mds) & (fri_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(sat_data_b[(sat_data_b['AP'] >= mds) & (sat_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(sun_data_b[(sun_data_b['AP'] >= mds) & (sun_data_b['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(wkdy_data_a[(wkdy_data_a['AP'] >= mds) & (wkdy_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(wknd_data_a[(wknd_data_a['AP'] >= mds) & (wknd_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(mon_data_a[(mon_data_a['AP'] >= mds) & (mon_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(tue_data_a[(tue_data_a['AP'] >= mds) & (tue_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(wed_data_a[(wed_data_a['AP'] >= mds) & (wed_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(thu_data_a[(thu_data_a['AP'] >= mds) & (thu_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(fri_data_a[(fri_data_a['AP'] >= mds) & (fri_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(sat_data_a[(sat_data_a['AP'] >= mds) & (sat_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(sun_data_a[(sun_data_a['AP'] >= mds) & (sun_data_a['AP'] < mde)]),
                                       lambda: self.f_tt_cdf(wkdy_data_b[(wkdy_data_b['AP'] >= pms) & (wkdy_data_b['AP'] < pme)]),  # PM Peak
                                       lambda: self.f_tt_cdf(wknd_data_b[(wknd_data_b['AP'] >= pms) & (wknd_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(mon_data_b[(mon_data_b['AP'] >= pms) & (mon_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(tue_data_b[(tue_data_b['AP'] >= pms) & (tue_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(wed_data_b[(wed_data_b['AP'] >= pms) & (wed_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(thu_data_b[(thu_data_b['AP'] >= pms) & (thu_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(fri_data_b[(fri_data_b['AP'] >= pms) & (fri_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(sat_data_b[(sat_data_b['AP'] >= pms) & (sat_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(sun_data_b[(sun_data_b['AP'] >= pms) & (sun_data_b['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(wkdy_data_a[(wkdy_data_a['AP'] >= pms) & (wkdy_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(wknd_data_a[(wknd_data_a['AP'] >= pms) & (wknd_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(mon_data_a[(mon_data_a['AP'] >= pms) & (mon_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(tue_data_a[(tue_data_a['AP'] >= pms) & (tue_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(wed_data_a[(wed_data_a['AP'] >= pms) & (wed_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(thu_data_a[(thu_data_a['AP'] >= pms) & (thu_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(fri_data_a[(fri_data_a['AP'] >= pms) & (fri_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(sat_data_a[(sat_data_a['AP'] >= pms) & (sat_data_a['AP'] < pme)]),
                                       lambda: self.f_tt_cdf(sun_data_a[(sun_data_a['AP'] >= pms) & (sun_data_a['AP'] < pme)])
                                       ]

        LoadStage2QT(self, self.project.main_window, func_dict)

    def plot_data_updated(self):
        if self.init_mode is True:
            self.create_charts()
            self.add_charts_to_layouts()
            self.v_layout.addWidget(self.chart_panel)
            self.v_layout.addWidget(self.check_bar_day)
            # self.update_chart_visibility()
            self.create_second_panel()
            self.init_mode = False
            self.no_compute = False
            # self.generate_summary_data()
            # self.project.main_window.create_summary_table()

    def create_charts(self):
        self.chart_et = MplChart(self, fig_type=FIG_TYPE_EXTRA_TIME, panel=self, region=0, region2=1)
        self.chart_sb_before = MplChart(self, fig_type=FIG_TYPE_SPD_BAND, panel=self, region=1, region2=-1)
        self.chart_sb_after = MplChart(self, fig_type=FIG_TYPE_SPD_BAND, panel=self, region=0, region2=-1)

        self.chart_speed_freq = MplChart(self, fig_type=FIG_TYPE_SPD_FREQ, panel=self, region=0, region2=1)
        self.chart_cdf = MplChart(self, fig_type=FIG_TYPE_TT_CDF, panel=self, region=0, region2=1)

    def update_figures(self):
        if self.chart_et is not None:
            self.chart_et.update_figure()
            self.chart_et.draw()
        if self.chart_sb_before is not None:
            self.chart_sb_before.update_figure()
            self.chart_sb_before.draw()
        if self.chart_sb_after is not None:
            self.chart_sb_after.update_figure()
            self.chart_sb_after.draw()
        if self.chart_speed_freq is not None:
            self.chart_speed_freq.update_figure()
            self.chart_speed_freq.draw()
        if self.chart_cdf is not None:
            self.chart_cdf.update_figure()
            self.chart_cdf.draw()
        # self.generate_summary_data()
        # self.project.main_window.create_summary_table()

    def add_charts_to_layouts(self):
        # Chart 1
        self.grid_layout.addWidget(self.chart_et, 0, 0, 1, 2)
        # Chart 2
        # self.grid_layout.addWidget(self.chart12, 0, 1)
        # Chart 3
        self.grid_layout.addWidget(self.chart_sb_before, 1, 0)
        # Chart 4
        self.grid_layout.addWidget(self.chart_sb_after, 1, 1)

    def options_updated(self):
        self.chart_options = self.project.chart_panel1_opts
        # self.update_plot_data()
        self.update_figures()
        # self.update_chart_visibility()

    def connect_radio_buttons(self):
        self.check_wkdy.setChecked(True)
        self.check_wkdy.toggled.connect(lambda: self.toggle_func(0, self.check_wkdy))
        self.check_wknd.toggled.connect(lambda: self.toggle_func(1, self.check_wknd))
        self.check_mon.toggled.connect(lambda: self.toggle_func(2, self.check_mon))
        self.check_tue.toggled.connect(lambda: self.toggle_func(3, self.check_tue))
        self.check_wed.toggled.connect(lambda: self.toggle_func(4, self.check_wed))
        self.check_thu.toggled.connect(lambda: self.toggle_func(5, self.check_thu))
        self.check_fri.toggled.connect(lambda: self.toggle_func(6, self.check_fri))
        self.check_sat.toggled.connect(lambda: self.toggle_func(7, self.check_sat))
        self.check_sun.toggled.connect(lambda: self.toggle_func(8, self.check_sun))

        self.check_wkdy.setEnabled(sum([self.available_days.count(el) for el in range(5)]) > 0)
        self.check_wknd.setEnabled(sum([self.available_days.count(el) for el in range(5, 7)]) > 0)
        self.check_mon.setEnabled(self.available_days.count(0) > 0)
        self.check_tue.setEnabled(self.available_days.count(1) > 0)
        self.check_wed.setEnabled(self.available_days.count(2) > 0)
        self.check_thu.setEnabled(self.available_days.count(3) > 0)
        self.check_fri.setEnabled(self.available_days.count(4) > 0)
        self.check_sat.setEnabled(self.available_days.count(5) > 0)
        self.check_sun.setEnabled(self.available_days.count(6) > 0)

    # def connect_combo_boxes(self):
    #     self.cb_tmc_select.currentIndexChanged.connect(self.tmc_selection_changed)

    def tmc_selection_changed(self):
        if not (self.init_mode or self.no_compute):
            # tmc_idx = self.cb_tmc_select.currentIndex()
            # self.selected_tmc_name = self.project.get_tmc()['tmc'][tmc_idx]
            # self.selected_tmc_len = self.project.get_tmc()['miles'][tmc_idx]
            self.update_figures()

    def select_tmc(self, tmc_code):
        # self.cb_tmc_select.setCurrentText(tmc_code)
        self.selected_tmc_name = tmc_code
        self.project.selected_tmc = tmc_code
        tmc = self.project.get_tmc(full_list=True)
        self.selected_tmc_len = tmc.loc[tmc[Project.ID_TMC_CODE] == tmc_code, Project.ID_TMC_LEN].iloc[0]
        self.tmc_selection_changed()

    def toggle_func(self, day_select, button):
        if not (self.init_mode or self.no_compute):
            if button.isChecked():
                self.no_compute = True
                if day_select is 0:
                    self.check_wkdy2.setChecked(True)
                elif day_select is 1:
                    self.check_wknd2.setChecked(True)
                elif day_select is 2:
                    self.check_mon2.setChecked(True)
                elif day_select is 3:
                    self.check_tue2.setChecked(True)
                elif day_select is 4:
                    self.check_wed2.setChecked(True)
                elif day_select is 5:
                    self.check_thu2.setChecked(True)
                elif day_select is 6:
                    self.check_fri2.setChecked(True)
                elif day_select is 7:
                    self.check_sat2.setChecked(True)
                elif day_select is 8:
                    self.check_sun2.setChecked(True)
                self.no_compute = False
                self.day_select = day_select
                self.update_figures()

    def toggle_func2(self, day_select, button):
        if not (self.init_mode or self.no_compute):
            if button.isChecked():
                if day_select is 0:
                    self.check_wkdy.setChecked(True)
                elif day_select is 1:
                    self.check_wknd.setChecked(True)
                elif day_select is 2:
                    self.check_mon.setChecked(True)
                elif day_select is 3:
                    self.check_tue.setChecked(True)
                elif day_select is 4:
                    self.check_wed.setChecked(True)
                elif day_select is 5:
                    self.check_thu.setChecked(True)
                elif day_select is 6:
                    self.check_fri.setChecked(True)
                elif day_select is 7:
                    self.check_sat.setChecked(True)
                elif day_select is 8:
                    self.check_sun.setChecked(True)

    def toggle_func_peak2(self, peak_select, button):
        if not (self.init_mode or self.no_compute):
            if button.isChecked():
                self.selected_peak = peak_select
                self.update_figures()

    def generate_summary_data(self):
        sd = SummaryData(self.project, self.selected_tmc_name)
        dr1 = self.project.get_date_range(0)
        dr2 = self.project.get_date_range(1)
        sd._start_date = [dr1[0], dr2[0]]
        sd._end_date = [dr1[1], dr2[1]]
        sd._start_time = ['12:00AM', '12:00AM']
        sd._end_time = ['11:59PM', '11:59PM']
        sd._num_days = [dr1[0].daysTo(dr1[1]) + 1, dr2[0].daysTo(dr2[1]) + 1]
        func_summ = dict()
        func_summ['sample_size'] = [lambda: self.project.compute_sample_size(0, self.selected_tmc_name),
                                    lambda: self.project.compute_sample_size(1, self.selected_tmc_name)]
        func_summ['am_mean'] = [lambda: mean(self.plot_dfs5[0][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[9][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[1][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[10][Project.ID_DATA_SPEED][self.selected_tmc_name].values)]
        func_summ['md_mean'] = [lambda: mean(self.plot_dfs5[18][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[27][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[19][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[28][Project.ID_DATA_SPEED][self.selected_tmc_name].values)]
        func_summ['pm_mean'] = [lambda: mean(self.plot_dfs5[36][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[45][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[37][Project.ID_DATA_SPEED][self.selected_tmc_name].values),
                                lambda: mean(self.plot_dfs5[46][Project.ID_DATA_SPEED][self.selected_tmc_name].values)]
        pctile = 5  # 100 - 95
        func_summ['am_95'] = [lambda: percentile(self.plot_dfs5[0][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[9][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[1][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[10][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile)]
        func_summ['md_95'] = [lambda: percentile(self.plot_dfs5[18][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[27][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[19][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[28][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile)]
        func_summ['pm_95'] = [lambda: percentile(self.plot_dfs5[36][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[45][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[37][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile),
                                lambda: percentile(self.plot_dfs5[46][Project.ID_DATA_SPEED][self.selected_tmc_name].values, pctile)]
        pctile80 = 80
        pctile50 = 50

        func_summ['tmc_am_lottr'] = [lambda: percentile(self.plot_dfs5[0][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[9][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[0][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50),
                                     lambda: percentile(self.plot_dfs5[9][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50)]
        func_summ['tmc_md_lottr'] = [lambda: percentile(self.plot_dfs5[18][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[27][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[18][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50),
                                     lambda: percentile(self.plot_dfs5[27][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50)]
        func_summ['tmc_pm_lottr'] = [lambda: percentile(self.plot_dfs5[36][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[45][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[36][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50),
                                     lambda: percentile(self.plot_dfs5[45][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50)]
        func_summ['tmc_we_lottr'] = [lambda: percentile(self.plot_dfs5[19][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[28][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile80),
                                     lambda: percentile(self.plot_dfs5[19][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50),
                                     lambda: percentile(self.plot_dfs5[28][Project.ID_DATA_TT][self.selected_tmc_name].values, pctile50)]

        func_summ['cor_am_lottr'] = [lambda: compute_corr_lottr(self.plot_dfs5[0]),   # Weekday Period 1
                                     lambda: compute_corr_lottr(self.plot_dfs5[9])]   # Weekday Period 2
        func_summ['cor_md_lottr'] = [lambda: compute_corr_lottr(self.plot_dfs5[18]),  # Weekday Period 1
                                     lambda: compute_corr_lottr(self.plot_dfs5[27])]  # Weekday Period 2
        func_summ['cor_pm_lottr'] = [lambda: compute_corr_lottr(self.plot_dfs5[36]),  # Weekday Period 1
                                     lambda: compute_corr_lottr(self.plot_dfs5[45])]  # Weekday Period 2
        func_summ['cor_we_lottr'] = [lambda: compute_corr_lottr(self.plot_dfs5[19]),  # Weekend Period 1
                                     lambda: compute_corr_lottr(self.plot_dfs5[28])]  # Weekend Period 2

        LoadSummaryQT(self, self.project.main_window, func_summ, sd)


def convert_time_to_ap(start_hour, start_min, ap_increment):
    return (start_hour * (60 // ap_increment)) + start_min // ap_increment


def compute_corr_lottr(df):
    lottr_dict = dict()
    for tmc, vals in df.groupby(level=0):
        tt_80 = percentile(vals[Project.ID_DATA_TT], 80)
        tt_50 = percentile(vals[Project.ID_DATA_TT], 50)
        lottr_dict[tmc] = tt_80 / tt_50
    return lottr_dict

