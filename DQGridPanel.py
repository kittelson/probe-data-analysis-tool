from PyQt5 import QtWidgets
from stat_func import create_dq_weekday, create_dq_time_of_day, create_dq_tmc, create_dq_study_period
from chart_defaults import ChartOptions, AnalysisOptions
from viz_qt import LoadDataQualityQT
from mpl_charts import MplChart, FIG_DQ_WKDY, FIG_DQ_TOD, FIG_DQ_TMC, FIG_DQ_SP


class DataQualityGridPanel(QtWidgets.QWidget):
    def __init__(self, project, chart_options=None, analysis_options=None):
        QtWidgets.QWidget.__init__(self)

        self.f_dq_weekday = create_dq_weekday
        self.f_dq_time_of_day = create_dq_time_of_day
        self.f_dq_tmc = create_dq_tmc
        self.f_dq_study_period = create_dq_study_period

        self.chart11 = None
        self.chart21 = None
        self.chart12 = None
        self.chart22 = None
        self.panel_col1 = QtWidgets.QWidget(self)
        self.panel_col2 = QtWidgets.QWidget(self)
        self.chart_panel = QtWidgets.QWidget(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout(self.chart_panel)

        self.init_mode = True
        self.project = project
        df = self.project.database.get_data()
        tmc = self.project.database.get_tmcs()
        self.facility_len = tmc['miles'].sum()
        self.dfs = [df]
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

        self.chart_options.chart_type[0][0] = FIG_DQ_WKDY
        self.chart_options.chart_type[0][1] = FIG_DQ_TOD
        self.chart_options.chart_type[1][0] = FIG_DQ_TMC
        self.chart_options.chart_type[1][1] = FIG_DQ_SP

        # Filter Components
        self.day_select = 0
        self.plot_dfs_dq = []
        self.update_plot_data()

    def plot_data_updated(self):
        if self.init_mode:
            self.create_charts()
            self.add_charts_to_layouts()
            self.v_layout.addWidget(self.chart_panel)
            # self.v_layout.addWidget(self.check_bar_day)
            self.update_chart_visibility()
            self.init_mode = False
        else:
            self.update_figures()
            # self.chart11.fire_animation()
            # self.chart12.fire_animation()
            # self.chart21.fire_animation()
            # self.chart22.fire_animation()

    def update_all(self, tmc_id=None):
        self.update_plot_data(tmc_id=tmc_id)
        # self.chart11.fire_animation()
        # self.chart12.fire_animation()
        # self.chart21.fire_animation()
        # self.chart22.fire_animation()

    def update_plot_data(self, tmc_id=None, **kwargs):
        # self.plot_dfs_dq = [self.f_dq_weekday(self.dfs[0]),
        #                     self.f_dq_time_of_day(self.dfs[0]),
        #                     self.f_dq_tmc(self.dfs[0], tmc_index=self.project.get_tmc()),
        #                     [self.f_dq_study_period(self.dfs[0], day_list=[0, 1, 2, 3, 4]),
        #                      self.f_dq_study_period(self.dfs[0], day_list=[5, 6])]
        #                     ]
        dq_funcs = [lambda: self.f_dq_weekday(self.dfs[0]),
                    lambda: self.f_dq_time_of_day(self.dfs[0]),
                    lambda: self.f_dq_tmc(self.dfs[0], tmc_index=self.project.get_tmc()),
                    lambda: self.f_dq_study_period(self.dfs[0], day_list=[0, 1, 2, 3, 4]),
                    lambda: self.f_dq_study_period(self.dfs[0], day_list=[5, 6])]

        LoadDataQualityQT(self, self.project.main_window, dq_funcs, data=self.dfs[0], tmc=tmc_id)
        # LoadDataQualityQT(self, self.project.main_window, dq_funcs)

    def create_charts(self):
        self.chart11 = MplChart(self, fig_type=self.chart_options.chart_type[0][0], panel=self)
        self.chart21 = MplChart(self, fig_type=self.chart_options.chart_type[1][0], panel=self)
        self.chart12 = MplChart(self, fig_type=self.chart_options.chart_type[0][1], panel=self)
        self.chart22 = MplChart(self, fig_type=self.chart_options.chart_type[1][1], panel=self)

    def update_figures(self):
        if self.chart11 is not None:
            self.chart11.update_figure()
            self.chart11.draw()
        if self.chart21 is not None:
            self.chart21.update_figure()
            self.chart21.draw()
        if self.chart12 is not None:
            self.chart12.update_figure()
            self.chart12.draw()
        if self.chart22 is not None:
            self.chart22.update_figure()
            self.chart22.draw()

    def update_chart_visibility(self):
        self.chart11.setVisible(True)
        self.chart12.setVisible(self.chart_options.num_cols > 1)
        self.chart21.setVisible(self.chart_options.num_rows > 1)
        self.chart22.setVisible(self.chart_options.num_rows > 1 and self.chart_options.num_cols > 1)

    def add_charts_to_layouts(self):
        # Chart 1
        self.grid_layout.addWidget(self.chart11, 0, 0)
        # Chart 2
        self.grid_layout.addWidget(self.chart12, 0, 1)
        # Chart 3
        self.grid_layout.addWidget(self.chart21, 1, 0)
        # Chart 4
        self.grid_layout.addWidget(self.chart22, 1, 1)

    def options_updated(self):
        self.chart_options = self.project.chart_panel1_opts
        # self.update_plot_data()
        self.update_chart_types()
        self.update_figures()
        self.update_chart_visibility()

    def update_chart_types(self):
        self.chart11.set_fig_type(self.chart_options.chart_type[0][0])
        self.chart12.set_fig_type(self.chart_options.chart_type[0][1])
        self.chart21.set_fig_type(self.chart_options.chart_type[1][0])
        self.chart22.set_fig_type(self.chart_options.chart_type[1][1])

    def connect_radio_buttons(self):
        pass

    def connect_combo_boxes(self):
        pass

    def tmc_selection_changed(self):
        pass

    def connect_check_boxes(self):
        pass

    def check_weekday(self):
        pass

    def check_weekend(self):
        pass

    def toggle_func(self, day_select, button):
        pass

    def check_func(self):
        pass

