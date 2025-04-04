from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class MenuBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        self.setFixedHeight(35)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.homeButton = QPushButton("Home")
        self.dataButton = QPushButton("Data Source")
        self.feedbackButton = QPushButton("Feedback")
        self.ankleImuDataButton = QPushButton("Ankle IMU")
        self.kneeImuDataButton = QPushButton("Knee IMU")
        self.kneeAngleDataButton = QPushButton("Knee Angle")
        self.feetDataButton = QPushButton("Feet Pressure")

        menuButtons = [
            self.homeButton,
            self.dataButton,
            self.feedbackButton,
            self.ankleImuDataButton,
            self.kneeImuDataButton,
            self.kneeAngleDataButton,
            self.feetDataButton,
        ]

        for button in menuButtons:
            button.setFixedSize(120, 30)
            button.setFont(QFont("Times", 18))
            layout.addWidget(button)

        self.setLayout(layout)
