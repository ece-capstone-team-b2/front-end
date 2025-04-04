# 3D visual of leg
# tad for raw sesnor data
# text for feedback
# start with squats
# menu to select exercise
# plots

import struct
import sys

import serial
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from data_view_publisher import DataViewPublisher
from widgets import *


class DataCaptureThread(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.capture = False

    def run(self):
        self.capture = True


class Page:
    def __init__(self, dataSource: DataViewPublisher):
        # source of data for the view
        self.dataSource = dataSource

        # making the window
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setFixedSize(1000, 800)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.window.setWindowTitle("Smart Wearable Exercise Activity Trainer (SWEAT)")
        self.pages = []

        # making the menu
        self.setUpMenu()

        # setting up homepage, feedback page, and raw data page
        self.setUpPages()

        # hide the page to start
        self.showPage(self.homePage)

        # showing the window
        self.window.setLayout(self.layout)
        self.window.show()

    # switch to the provided page
    def showPage(self, page):
        for p in self.pages:
            if p != page:
                p.hide()
                p.visible = False
        page.show()
        page.visible = True
        try:
            page.updateLines()
        except:
            pass
        # if page == self.rawDataPage:
        #     self.rawDataPage.visible = True
        #     # self.rawDataPage.update_graphs()
        #     self.rawDataPage.updateLines()
        # else:
        #     self.rawDataPage.visible = False

    # start the application
    def startApp(self):
        self.app.exec()
        self.dataSource.stop_reading()

    # set up the pages and connect them to their corresponding buttons
    def setUpPages(self):
        self.homePage = HomePage()
        self.dataControls = DataControlsPage(self.dataSource, visible=False)
        self.feedbackPage = FeedbackPage(self.dataSource, visible=False)
        self.ankleImuPage = ImuRawDataPage(
            self.dataSource,
            visible=False,
            label="Ankle",
            left_node_id=3,
            right_node_id=4,
        )
        self.kneeImuPage = ImuRawDataPage(
            self.dataSource,
            visible=False,
            label="Knee",
            left_node_id=1,
            right_node_id=2,
        )
        self.kneeAnglePage = FlexSensorRawDataPage(
            self.dataSource, visible=False, label="Angle"
        )
        self.feetDataPage = ForceRawDataPage(
            self.dataSource, visible=False, label="Feet"
        )
        self.pages += [
            self.homePage,
            self.dataControls,
            self.feedbackPage,
            self.ankleImuPage,
            self.kneeImuPage,
            self.kneeAnglePage,
            self.feetDataPage,
        ]

        for page in self.pages:
            self.layout.addWidget(page)

        button_to_page = {
            self.menuBar.homeButton: self.homePage,
            self.menuBar.dataButton: self.dataControls,
            self.menuBar.feedbackButton: self.feedbackPage,
            self.menuBar.ankleImuDataButton: self.ankleImuPage,
            self.menuBar.kneeImuDataButton: self.kneeImuPage,
            self.menuBar.kneeAngleDataButton: self.kneeAnglePage,
            self.menuBar.feetDataButton: self.feetDataPage,
        }

        for button, currentPage in button_to_page.items():
            button.clicked.connect(lambda _, page=currentPage: self.showPage(page))

    # set up the menu of buttons
    def setUpMenu(self):
        self.menuBar = MenuBar()
        self.layout.addWidget(self.menuBar)


dataSource = DataViewPublisher()
page = Page(dataSource)
page.startApp()
