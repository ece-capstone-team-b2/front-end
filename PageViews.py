from SensorDataCollector import SensorDataCollector
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

class FeedbackPage(QWidget):
    def __init__(self):
        super().__init__()
        self.sensorDataCollector = SensorDataCollector()
        self.setup()

    def setup(self):
        self.setLayout(QVBoxLayout())

        feedbackMessage = QLabel("feedback")
        feedbackMessage.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        feedbackMessage.setFont(QFont("Times", 20))
        self.layout().addWidget(feedbackMessage)

        

class RawDataPage(QWidget):
    def __init__(self):
        super().__init__()
        self.sensorDataCollector = SensorDataCollector()
        self.setup()
    
    def setup(self):
        self.setLayout(QVBoxLayout())

        rawDataMessage = QLabel("rawdata")
        rawDataMessage.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        rawDataMessage.setFont(QFont("Times", 20))
        self.layout().addWidget(rawDataMessage)

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        self.setLayout(QVBoxLayout())

        welcomeMessage = QLabel("Welcome to SWEAT!")
        welcomeMessage.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        welcomeMessage.setFont(QFont("Times", 20))
        self.layout().addWidget(welcomeMessage)
