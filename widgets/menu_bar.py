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
        self.rawDataButton = QPushButton("Raw Data")

        menuButtons = [self.homeButton, self.feedbackButton, self.rawDataButton]

        for button in menuButtons:
            button.setFixedSize(100, 25)
            button.setFont(QFont("Times", 10))
            layout.addWidget(button)
            
        self.setLayout(layout)

