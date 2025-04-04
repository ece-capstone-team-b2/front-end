from PyQt6.QtWidgets import QWidget, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MenuBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        self.setFixedHeight(35)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.homeButton = QPushButton("Home")
        self.feedbackButton = QPushButton("Feedback")
        self.ankleImuDataButton = QPushButton("Ankle IMU")
        self.kneeImuDataButton = QPushButton("Knee IMU")
        self.kneeAngleDataButton = QPushButton("Knee Angle")
        self.feetDataButton = QPushButton("Feet Pressure")
        self.rawDataButton = QPushButton("Raw Data")

        menuButtons = [
            self.homeButton,
            self.feedbackButton,
            self.ankleImuDataButton,
            self.kneeImuDataButton,
            self.kneeAngleDataButton,
            self.feetDataButton,
            self.rawDataButton,
        ]

        for button in menuButtons:
            button.setFixedSize(120, 30)
            button.setFont(QFont("Times", 18))
            layout.addWidget(button)

        self.setLayout(layout)
