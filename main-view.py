# 3D visual of leg
# tad for raw sesnor data
# text for feedback
# start with squats
# menu to select exercise
# plots

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
        self.window.setWindowTitle("Smart Wearable Exercize Activity Trainer (SWEAT)")

        # making the menu
        self.setUpMenu()

        # array of all pages
        self.pages = []
        
        # setting up homepage
        self.homePage = QWidget()
        self.homePageLayout = QVBoxLayout()
        self.setUpPage(self.homePage, self.homePageLayout, self.homeButton)
        self.setUpHomePage()

        # setting up feedback page
        self.feedbackPage = QWidget()
        self.feedbackPageLayout = QVBoxLayout()
        self.setUpPage(self.feedbackPage, self.feedbackPageLayout, self.feedbackButton)
        self.setUpFeedbackPage()

        # setting up rawdata page
        self.rawDataPage = QWidget()
        self.rawDataPageLayout = QVBoxLayout()
        self.setUpPage(self.rawDataPage, self.rawDataPageLayout, self.rawDataButton)
        self.setUpRawDataPage()

        # hide the page to start
        self.showPage(self.homePage)

        # showing the window
        self.window.setLayout(self.layout)
        self.window.show()
    
    def showPage(self, page):
        for p in self.pages:
            if p != page:
                p.hide()
        page.show()

    def startApp(self):
        self.app.exec()
    
    def setUpPage(self, page, layout, button):
        page.setLayout(layout)
        self.layout.addWidget(page)
        self.pages += [page]

        #linking button to page
        button.clicked.connect(lambda: self.showPage(page))

    def setUpHomePage(self):
        # adding welcome message
        self.welcomeMessage = QLabel("Welcome to SWEAT!")
        self.welcomeMessage.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.welcomeMessage.setFont(QFont("Times", 20))
        self.homePageLayout.addWidget(self.welcomeMessage)

    def setUpFeedbackPage(self):
        # adding welcome message
        self.feedbackMessage = QLabel("feedback")
        self.feedbackMessage.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.feedbackMessage.setFont(QFont("Times", 20))
        self.feedbackPageLayout.addWidget(self.feedbackMessage)

    def setUpRawDataPage(self):
        # adding welcome message
        self.rawDataMessage = QLabel("rawdata")
        self.rawDataMessage.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.rawDataMessage.setFont(QFont("Times", 20))
        self.rawDataPageLayout.addWidget(self.rawDataMessage)
        
    def setUpMenu(self):
        self.menu = QWidget()
        self.menu.setFixedHeight(35)
        self.menuLayout = QHBoxLayout()
        self.menuLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.homeButton = QPushButton("Home")
        self.feedbackButton = QPushButton("Feedback")
        self.rawDataButton = QPushButton("Raw Data")

        self.menuButtons = [self.homeButton, self.feedbackButton, self.rawDataButton]

        for button in self.menuButtons:
            button.setFixedSize(100, 25)
            button.setFont(QFont("Times", 10))
            self.menuLayout.addWidget(button)

        self.menu.setLayout(self.menuLayout)
        self.layout.addWidget(self.menu)

page = Page()
page.startApp()