from PyQt6.QtWidgets import QWidget, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


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
