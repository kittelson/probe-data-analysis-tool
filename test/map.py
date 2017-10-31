#!/usr/local/bin/python36
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.form_widget = FormWidget(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)


class FormWidget(QWidget):
    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.__controls()
        self.__layout()

    def __controls(self):
        self.browser = QWebView()
        self.browser.load(QUrl('file:///C:/Users/ltrask/PycharmProjects/NPMRDS_Data_Tool/test/map3.html'))

    def __layout(self):
        self.vbox = QVBoxLayout()
        self.hBox = QVBoxLayout()
        self.getboundsbutton = QPushButton()
        self.hBox.addWidget(self.browser)
        # self.hBox.addWidget(self.getboundsbutton)
        self.vbox.addLayout(self.hBox)
        self.setLayout(self.vbox)

        self.getboundsbutton.clicked.connect(self.getBounds)

    def getBounds(self):
        self.bounds = self.browser.page().runJavaScript("[map.getBounds().getSouthWest().lat, map.getBounds().getSouthWest().lng, map.getBounds().getNorthEast().lat, map.getBounds().getNorthEast().lng]")
        print(self.bounds)
        # this is where I get stuck .. the result is None
        # the same js code in the html file prints the bounds values
        # that I want to store on the python side of the app


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())