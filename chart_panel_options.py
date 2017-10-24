# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chart_panel_options.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

"""
The PyQt5 based user interface for the Chart Options dialog.
"""

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(784, 519)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_5 = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy)
        self.widget_5.setObjectName("widget_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_5)
        self.horizontalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame = QtWidgets.QFrame(self.widget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.widget_3 = QtWidgets.QWidget(self.frame)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.widget_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.cb_rows = QtWidgets.QComboBox(self.widget_3)
        self.cb_rows.setObjectName("cb_rows")
        self.cb_rows.addItem("")
        self.cb_rows.addItem("")
        self.horizontalLayout.addWidget(self.cb_rows)
        self.label_3 = QtWidgets.QLabel(self.widget_3)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.cb_cols = QtWidgets.QComboBox(self.widget_3)
        self.cb_cols.setObjectName("cb_cols")
        self.cb_cols.addItem("")
        self.cb_cols.addItem("")
        self.horizontalLayout.addWidget(self.cb_cols)
        self.verticalLayout_2.addWidget(self.widget_3)
        self.frame_4 = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.frame_4)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.cb_chart1 = QtWidgets.QComboBox(self.frame_4)
        self.cb_chart1.setObjectName("cb_chart1")
        self.horizontalLayout_2.addWidget(self.cb_chart1)
        self.label_5 = QtWidgets.QLabel(self.frame_4)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.cb_chart2 = QtWidgets.QComboBox(self.frame_4)
        self.cb_chart2.setObjectName("cb_chart2")
        self.horizontalLayout_2.addWidget(self.cb_chart2)
        self.label_6 = QtWidgets.QLabel(self.frame_4)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_2.addWidget(self.label_6)
        self.cb_chart3 = QtWidgets.QComboBox(self.frame_4)
        self.cb_chart3.setCurrentText("")
        self.cb_chart3.setObjectName("cb_chart3")
        self.horizontalLayout_2.addWidget(self.cb_chart3)
        self.label_7 = QtWidgets.QLabel(self.frame_4)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.cb_chart4 = QtWidgets.QComboBox(self.frame_4)
        self.cb_chart4.setObjectName("cb_chart4")
        self.horizontalLayout_2.addWidget(self.cb_chart4)
        self.verticalLayout_2.addWidget(self.frame_4)
        self.horizontalLayout_3.addWidget(self.frame)
        self.frame_6 = QtWidgets.QFrame(self.widget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setObjectName("frame_6")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_6)
        self.gridLayout.setObjectName("gridLayout")
        self.label_8 = QtWidgets.QLabel(self.frame_6)
        self.label_8.setFrameShape(QtWidgets.QFrame.Box)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.frame_6)
        self.label_10.setFrameShape(QtWidgets.QFrame.Box)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame_6)
        self.label_9.setFrameShape(QtWidgets.QFrame.Box)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 1, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.frame_6)
        self.label_11.setFrameShape(QtWidgets.QFrame.Box)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 1, 1, 1, 1)
        self.horizontalLayout_3.addWidget(self.frame_6)
        self.verticalLayout.addWidget(self.widget_5)
        self.frame_8 = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy)
        self.frame_8.setStyleSheet("border-color: rgb(0, 0, 0);")
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setMidLineWidth(0)
        self.frame_8.setObjectName("frame_8")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_8)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_13 = QtWidgets.QLabel(self.frame_8)
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 4, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.frame_8)
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 5, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.frame_8)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 6, 0, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.frame_8)
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.gridLayout_2.addWidget(self.label_16, 7, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.frame_8)
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.gridLayout_2.addWidget(self.label_17, 8, 0, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.frame_8)
        self.label_25.setAlignment(QtCore.Qt.AlignCenter)
        self.label_25.setObjectName("label_25")
        self.gridLayout_2.addWidget(self.label_25, 6, 4, 1, 1)
        self.label_min_bin3 = QtWidgets.QLabel(self.frame_8)
        self.label_min_bin3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_min_bin3.setObjectName("label_min_bin3")
        self.gridLayout_2.addWidget(self.label_min_bin3, 6, 3, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.frame_8)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_12 = QtWidgets.QLabel(self.frame_2)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_4.addWidget(self.label_12)
        self.cb_num_bins = QtWidgets.QComboBox(self.frame_2)
        self.cb_num_bins.setObjectName("cb_num_bins")
        self.cb_num_bins.addItem("")
        self.cb_num_bins.addItem("")
        self.cb_num_bins.addItem("")
        self.cb_num_bins.addItem("")
        self.cb_num_bins.addItem("")
        self.horizontalLayout_4.addWidget(self.cb_num_bins)
        self.label_32 = QtWidgets.QLabel(self.frame_2)
        self.label_32.setObjectName("label_32")
        self.horizontalLayout_4.addWidget(self.label_32)
        self.cb_bin_color_scheme = QtWidgets.QComboBox(self.frame_2)
        self.cb_bin_color_scheme.setObjectName("cb_bin_color_scheme")
        self.cb_bin_color_scheme.addItem("")
        self.cb_bin_color_scheme.addItem("")
        self.horizontalLayout_4.addWidget(self.cb_bin_color_scheme)
        self.gridLayout_2.addWidget(self.frame_2, 2, 0, 1, 6)
        self.label_24 = QtWidgets.QLabel(self.frame_8)
        self.label_24.setAlignment(QtCore.Qt.AlignCenter)
        self.label_24.setObjectName("label_24")
        self.gridLayout_2.addWidget(self.label_24, 5, 4, 1, 1)
        self.spin_min_bin1 = QtWidgets.QSpinBox(self.frame_8)
        self.spin_min_bin1.setObjectName("spin_min_bin1")
        self.gridLayout_2.addWidget(self.spin_min_bin1, 4, 3, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.frame_8)
        self.label_27.setAlignment(QtCore.Qt.AlignCenter)
        self.label_27.setObjectName("label_27")
        self.gridLayout_2.addWidget(self.label_27, 8, 4, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.frame_8)
        self.label_26.setAlignment(QtCore.Qt.AlignCenter)
        self.label_26.setObjectName("label_26")
        self.gridLayout_2.addWidget(self.label_26, 7, 4, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.frame_8)
        self.label_22.setObjectName("label_22")
        self.gridLayout_2.addWidget(self.label_22, 8, 2, 1, 1, QtCore.Qt.AlignRight)
        self.label_min_bin2 = QtWidgets.QLabel(self.frame_8)
        self.label_min_bin2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_min_bin2.setObjectName("label_min_bin2")
        self.gridLayout_2.addWidget(self.label_min_bin2, 5, 3, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.frame_8)
        self.label_21.setObjectName("label_21")
        self.gridLayout_2.addWidget(self.label_21, 7, 2, 1, 1, QtCore.Qt.AlignRight)
        self.label_23 = QtWidgets.QLabel(self.frame_8)
        self.label_23.setAlignment(QtCore.Qt.AlignCenter)
        self.label_23.setObjectName("label_23")
        self.gridLayout_2.addWidget(self.label_23, 4, 4, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.frame_8)
        self.label_18.setObjectName("label_18")
        self.gridLayout_2.addWidget(self.label_18, 4, 2, 1, 1, QtCore.Qt.AlignRight)
        self.label_min_bin5 = QtWidgets.QLabel(self.frame_8)
        self.label_min_bin5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_min_bin5.setObjectName("label_min_bin5")
        self.gridLayout_2.addWidget(self.label_min_bin5, 8, 3, 1, 1)
        self.spin_max_bin1 = QtWidgets.QSpinBox(self.frame_8)
        self.spin_max_bin1.setProperty("value", 25)
        self.spin_max_bin1.setObjectName("spin_max_bin1")
        self.gridLayout_2.addWidget(self.spin_max_bin1, 4, 5, 1, 1)
        self.spin_max_bin4 = QtWidgets.QSpinBox(self.frame_8)
        self.spin_max_bin4.setProperty("value", 55)
        self.spin_max_bin4.setObjectName("spin_max_bin4")
        self.gridLayout_2.addWidget(self.spin_max_bin4, 7, 5, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.frame_8)
        self.label_33.setAlignment(QtCore.Qt.AlignCenter)
        self.label_33.setObjectName("label_33")
        self.gridLayout_2.addWidget(self.label_33, 8, 5, 1, 1)
        self.label_min_bin4 = QtWidgets.QLabel(self.frame_8)
        self.label_min_bin4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_min_bin4.setObjectName("label_min_bin4")
        self.gridLayout_2.addWidget(self.label_min_bin4, 7, 3, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.frame_8)
        self.label_20.setObjectName("label_20")
        self.gridLayout_2.addWidget(self.label_20, 6, 2, 1, 1, QtCore.Qt.AlignRight)
        self.label_19 = QtWidgets.QLabel(self.frame_8)
        self.label_19.setObjectName("label_19")
        self.gridLayout_2.addWidget(self.label_19, 5, 2, 1, 1, QtCore.Qt.AlignRight)
        self.label_28 = QtWidgets.QLabel(self.frame_8)
        self.label_28.setObjectName("label_28")
        self.gridLayout_2.addWidget(self.label_28, 1, 0, 1, 3)
        self.spin_max_bin3 = QtWidgets.QSpinBox(self.frame_8)
        self.spin_max_bin3.setProperty("value", 45)
        self.spin_max_bin3.setObjectName("spin_max_bin3")
        self.gridLayout_2.addWidget(self.spin_max_bin3, 6, 5, 1, 1)
        self.spin_max_bin2 = QtWidgets.QSpinBox(self.frame_8)
        self.spin_max_bin2.setProperty("value", 35)
        self.spin_max_bin2.setObjectName("spin_max_bin2")
        self.gridLayout_2.addWidget(self.spin_max_bin2, 5, 5, 1, 1)
        self.frame_5 = QtWidgets.QFrame(self.frame_8)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_9.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.pb_bin4 = QtWidgets.QPushButton(self.frame_5)
        self.pb_bin4.setStyleSheet("QPushButton {\n"
"    border: 2px solid #8f8f91;\n"
"    border-radius: 1px;\n"
"    background-color: #98df8a;\n"
"    min-width: 80px;    \n"
"    border-width: 5px;\n"
"    border-color:white;\n"
"    \n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #dadbde, stop: 1 #98df8a);\n"
"}\n"
"\n"
"QPushButton:flat {\n"
"    border: none; /* no border for a flat push button */\n"
"}")
        self.pb_bin4.setObjectName("pb_bin4")
        self.horizontalLayout_9.addWidget(self.pb_bin4)
        self.gridLayout_2.addWidget(self.frame_5, 7, 1, 1, 1)
        self.frame_7 = QtWidgets.QFrame(self.frame_8)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_8.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.pb_bin3 = QtWidgets.QPushButton(self.frame_7)
        self.pb_bin3.setStyleSheet("QPushButton {\n"
"    border: 2px solid #8f8f91;\n"
"    border-radius: 1px;\n"
"    background-color: #dbdb8d;\n"
"    min-width: 80px;    \n"
"    border-width: 5px;\n"
"    border-color:white;\n"
"    \n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #dadbde, stop: 1 #dbdb8d);\n"
"}\n"
"\n"
"QPushButton:flat {\n"
"    border: none; /* no border for a flat push button */\n"
"}")
        self.pb_bin3.setObjectName("pb_bin3")
        self.horizontalLayout_8.addWidget(self.pb_bin3)
        self.gridLayout_2.addWidget(self.frame_7, 6, 1, 1, 1)
        self.frame_9 = QtWidgets.QFrame(self.frame_8)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_9.setObjectName("frame_9")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_9)
        self.horizontalLayout_7.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.pb_bin2 = QtWidgets.QPushButton(self.frame_9)
        self.pb_bin2.setStyleSheet("QPushButton {\n"
"    border: 2px solid #8f8f91;\n"
"    border-radius: 1px;\n"
"    background-color: #ff7f0e;\n"
"    min-width: 80px;    \n"
"    border-width: 5px;\n"
"    border-color:white;\n"
"    \n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #dadbde, stop: 1 #ff7f0e);\n"
"}\n"
"\n"
"QPushButton:flat {\n"
"    border: none; /* no border for a flat push button */\n"
"}")
        self.pb_bin2.setObjectName("pb_bin2")
        self.horizontalLayout_7.addWidget(self.pb_bin2)
        self.gridLayout_2.addWidget(self.frame_9, 5, 1, 1, 1)
        self.frame_10 = QtWidgets.QFrame(self.frame_8)
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_10.setObjectName("frame_10")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_10)
        self.horizontalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.pb_bin1 = QtWidgets.QPushButton(self.frame_10)
        self.pb_bin1.setStyleSheet("QPushButton {\n"
"    border: 2px solid #8f8f91;\n"
"    border-radius: 1px;\n"
"    background-color: #d62728;\n"
"    min-width: 80px;    \n"
"    border-width: 5px;\n"
"    border-color:white;\n"
"    \n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #dadbde, stop: 1 #d62728);\n"
"}\n"
"\n"
"QPushButton:flat {\n"
"    border: none; /* no border for a flat push button */\n"
"}")
        self.pb_bin1.setObjectName("pb_bin1")
        self.horizontalLayout_6.addWidget(self.pb_bin1)
        self.gridLayout_2.addWidget(self.frame_10, 4, 1, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.frame_8)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_5.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pb_bin5 = QtWidgets.QPushButton(self.frame_3)
        self.pb_bin5.setStyleSheet("QPushButton {\n"
"    border: 2px solid #8f8f91;\n"
"    border-radius: 1px;\n"
"    background-color: #2ca02c;\n"
"    min-width: 80px;    \n"
"    border-width: 5px;\n"
"    border-color:white;\n"
"    \n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #dadbde, stop: 1 #2ca02c);\n"
"}\n"
"\n"
"QPushButton:flat {\n"
"    border: none; /* no border for a flat push button */\n"
"}\n"
"\n"
"")
        self.pb_bin5.setObjectName("pb_bin5")
        self.horizontalLayout_5.addWidget(self.pb_bin5)
        self.gridLayout_2.addWidget(self.frame_3, 8, 1, 1, 1)
        self.line = QtWidgets.QFrame(self.frame_8)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_2.addWidget(self.line, 3, 0, 1, 6)
        self.verticalLayout.addWidget(self.frame_8)
        self.widget_7 = QtWidgets.QWidget(Dialog)
        self.widget_7.setObjectName("widget_7")
        self.verticalLayout.addWidget(self.widget_7)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.cb_rows.setCurrentIndex(1)
        self.cb_cols.setCurrentIndex(1)
        self.cb_chart2.setCurrentIndex(-1)
        self.cb_chart3.setCurrentIndex(-1)
        self.cb_chart4.setCurrentIndex(-1)
        self.cb_num_bins.setCurrentIndex(4)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Chart Panel Options"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">Chart Panel Grid and Display Options</span></p></body></html>"))
        self.label_2.setText(_translate("Dialog", "Rows:"))
        self.cb_rows.setItemText(0, _translate("Dialog", "1"))
        self.cb_rows.setItemText(1, _translate("Dialog", "2"))
        self.label_3.setText(_translate("Dialog", "Columns:"))
        self.cb_cols.setItemText(0, _translate("Dialog", "1"))
        self.cb_cols.setItemText(1, _translate("Dialog", "2"))
        self.label_4.setText(_translate("Dialog", "1."))
        self.label_5.setText(_translate("Dialog", "2."))
        self.label_6.setText(_translate("Dialog", "3."))
        self.label_7.setText(_translate("Dialog", "4."))
        self.label_8.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">1</span></p></body></html>"))
        self.label_10.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">2</span></p></body></html>"))
        self.label_9.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">3</span></p></body></html>"))
        self.label_11.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">4</span></p></body></html>"))
        self.label_13.setText(_translate("Dialog", "Speed Bin 1:"))
        self.label_14.setText(_translate("Dialog", "Speed Bin 2:"))
        self.label_15.setText(_translate("Dialog", "Speed Bin 3:"))
        self.label_16.setText(_translate("Dialog", "Speed Bin 4:"))
        self.label_17.setText(_translate("Dialog", "Speed Bin 5:"))
        self.label_25.setText(_translate("Dialog", "To"))
        self.label_min_bin3.setText(_translate("Dialog", "35"))
        self.label_12.setText(_translate("Dialog", "Number of Speed Bins:"))
        self.cb_num_bins.setItemText(0, _translate("Dialog", "1"))
        self.cb_num_bins.setItemText(1, _translate("Dialog", "2"))
        self.cb_num_bins.setItemText(2, _translate("Dialog", "3"))
        self.cb_num_bins.setItemText(3, _translate("Dialog", "4"))
        self.cb_num_bins.setItemText(4, _translate("Dialog", "5"))
        self.label_32.setText(_translate("Dialog", "Speed Bin Color Scheme:"))
        self.cb_bin_color_scheme.setItemText(0, _translate("Dialog", "Default"))
        self.cb_bin_color_scheme.setItemText(1, _translate("Dialog", "User"))
        self.label_24.setText(_translate("Dialog", "To"))
        self.label_27.setText(_translate("Dialog", "To"))
        self.label_26.setText(_translate("Dialog", "To"))
        self.label_22.setText(_translate("Dialog", "Speed Range:"))
        self.label_min_bin2.setText(_translate("Dialog", "25"))
        self.label_21.setText(_translate("Dialog", "Speed Range:"))
        self.label_23.setText(_translate("Dialog", "To"))
        self.label_18.setText(_translate("Dialog", "Speed Range:"))
        self.label_min_bin5.setText(_translate("Dialog", "55"))
        self.label_33.setText(_translate("Dialog", "Max"))
        self.label_min_bin4.setText(_translate("Dialog", "45"))
        self.label_20.setText(_translate("Dialog", "Speed Range:"))
        self.label_19.setText(_translate("Dialog", "Speed Range:"))
        self.label_28.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">Color and Value Options for Chart Speed Bins</span></p></body></html>"))
        self.pb_bin4.setToolTip(_translate("Dialog", "<html><head/><body><p>Click to change</p></body></html>"))
        self.pb_bin4.setText(_translate("Dialog", "Color 4"))
        self.pb_bin3.setToolTip(_translate("Dialog", "<html><head/><body><p>Click to change</p></body></html>"))
        self.pb_bin3.setText(_translate("Dialog", "Color 3"))
        self.pb_bin2.setToolTip(_translate("Dialog", "<html><head/><body><p>Click to change</p></body></html>"))
        self.pb_bin2.setText(_translate("Dialog", "Color 2"))
        self.pb_bin1.setToolTip(_translate("Dialog", "<html><head/><body><p>Click to change</p></body></html>"))
        self.pb_bin1.setText(_translate("Dialog", "Color 1"))
        self.pb_bin5.setToolTip(_translate("Dialog", "<html><head/><body><p>Click to change</p></body></html>"))
        self.pb_bin5.setText(_translate("Dialog", "Color 5"))

