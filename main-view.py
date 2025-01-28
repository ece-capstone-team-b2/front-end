# 3D visual of leg
# tad for raw sesnor data
# text for feedback
# start with squats
# menu to select exercise
# plots

from PageViews import FeedbackPage, RawDataPage, HomePage
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

class Page:
    def __init__(self):
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

    # start the application
    def startApp(self):
        self.app.exec()
    
    # set up the pages and connect them to their corresponding buttons
    def setUpPages(self):
        self.homePage = HomePage()
        self.feedbackPage = FeedbackPage()
        self.rawDataPage = RawDataPage()
        self.pages += [self.homePage, self.feedbackPage, self.rawDataPage]

        for page in self.pages:
            self.layout.addWidget(page)

        button_to_page = {
            self.homeButton: self.homePage,
            self.feedbackButton: self.feedbackPage,
            self.rawDataButton: self.rawDataPage
        }

        for button, currentPage in button_to_page.items():
            button.clicked.connect(lambda _, page = currentPage: self.showPage(page))

    # set up the menu of buttons
    def setUpMenu(self):
        self.menu = QWidget()
        self.menu.setFixedHeight(35)
        self.menuLayout = QHBoxLayout()
        self.menuLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.initializeButtons()

        menuButtons = [self.homeButton, self.feedbackButton, self.rawDataButton]

        for button in menuButtons:
            button.setFixedSize(100, 25)
            button.setFont(QFont("Times", 10))
            self.menuLayout.addWidget(button)

        self.menu.setLayout(self.menuLayout)
        self.layout.addWidget(self.menu)

    # instantiates the buttons
    def initializeButtons(self):
        self.homeButton = QPushButton("Home")
        self.feedbackButton = QPushButton("Feedback")
        self.rawDataButton = QPushButton("Raw Data")

page = Page()
page.startApp()