# 3D visual of leg
# tad for raw sesnor data
# text for feedback
# start with squats
# menu to select exercise
# plots

from widgets import *
from data_view_publisher import DataViewPublisher
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
import sys

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
        page.show()
        if page == self.rawDataPage:
            self.rawDataPage.visible = True
            self.rawDataPage.update_graphs()
        else:
            self.rawDataPage.visible = False

    # start the application
    def startApp(self):
        self.app.exec()
    
    # set up the pages and connect them to their corresponding buttons
    def setUpPages(self):
        self.homePage = HomePage()
        self.feedbackPage = FeedbackPage(self.dataSource)
        self.rawDataPage = RawDataPage(self.dataSource, visible=False)
        self.pages += [self.homePage, self.feedbackPage, self.rawDataPage]

        for page in self.pages:
            self.layout.addWidget(page)

        button_to_page = {
            self.menuBar.homeButton: self.homePage,
            self.menuBar.feedbackButton: self.feedbackPage,
            self.menuBar.rawDataButton: self.rawDataPage
        }

        for button, currentPage in button_to_page.items():
            button.clicked.connect(lambda _, page = currentPage: self.showPage(page))

    # set up the menu of buttons
    def setUpMenu(self):
        self.menuBar = MenuBar()
        self.layout.addWidget(self.menuBar)

dataSource = DataViewPublisher()
page = Page(dataSource)
page.startApp()