from SensorDataCollector import SensorDataCollector
from StyleSheets import *
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel, QButtonGroup, QRadioButton, QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys

class FeedbackPage(QWidget):
    def __init__(self):
        super().__init__()
        self.sensorDataCollector = SensorDataCollector()
        self.setup()
        self.selectedExercise = None
        self.timer = QTimer(self)
        # timer ticks every second
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.retrieveData)

    def setup(self):
        layout = QHBoxLayout()
        self.exerciseSelector = self.createExerciseSelector()
        self.visualizationBox = self.createVisualizationBox()
        self.feedbackBox = self.createFeedbackBox()
        layout.addWidget(self.exerciseSelector)
        layout.addWidget(self.visualizationBox)
        layout.addWidget(self.feedbackBox)
        layout.setSpacing(10)
        layout.setStretchFactor(self.exerciseSelector, 1)
        layout.setStretchFactor(self.visualizationBox, 2)
        layout.setStretchFactor(self.feedbackBox, 2)
        self.setLayout(layout)

    def createExerciseSelector(self):
        selectorBox = QWidget(self)
        selectorBox.setStyleSheet(EXERCISE_SELECTOR_STYLE_SHEET)
        layout = QVBoxLayout(selectorBox)
        label = QLabel("Exercise Selector")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label)
        layout.setSpacing(10)
        buttons = QButtonGroup()
        self.squatsButton = QRadioButton("Squats")
        self.lungeButton = QRadioButton("Lunge")
        self.squatsButton.clicked.connect(lambda: self.updateSelectedExercise("Squats"))
        self.lungeButton.clicked.connect(lambda: self.updateSelectedExercise("Lunge"))
        buttons.addButton(self.squatsButton)
        buttons.addButton(self.lungeButton)
        layout.addWidget(self.squatsButton)
        layout.addWidget(self.lungeButton)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        selectorBox.setLayout(layout)
        selectorBox.setMinimumHeight(700)
        
        return selectorBox

    def createVisualizationBox(self):
        visualizationBox = QWidget(self)
        layout = QVBoxLayout(visualizationBox)
        placeholder1 = QWidget()
        placeholder2 = QWidget()
        placeholder1.setStyleSheet(PLACEHOLDER_STYLE_SHEET)
        placeholder2.setStyleSheet(PLACEHOLDER_STYLE_SHEET)
        layout.addWidget(placeholder1)
        layout.addWidget(placeholder2)
        layout.setSpacing(10)
        visualizationBox.setMinimumHeight(700)
        visualizationBox.setStyleSheet(VISUALIZATION_BOX_STYLE_SHEET)
        return visualizationBox

    def createFeedbackBox(self):
        feedbackBox = QWidget(self)
        layout = QVBoxLayout(feedbackBox)
        label = QLabel("Feedback")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        placeholder1 = QTextEdit()
        placeholder1.setText("Placeholder text")
        placeholder1.setReadOnly(True)
        placeholder1.setStyleSheet(PLACEHOLDER_STYLE_SHEET)
        self.startButton = QPushButton()
        self.startButton.setText("Start")
        self.startButton.clicked.connect(lambda: self.startButtonPressed())
        layout.setSpacing(10)
        layout.addWidget(placeholder1)
        layout.addWidget(self.startButton)
        feedbackBox.setMinimumHeight(700)
        feedbackBox.setStyleSheet(FEEDBACK_BOX_STYLE_SHEET)
        return feedbackBox

    def updateSelectedExercise(self, exercise: str):
        self.selectedExercise = exercise

    def startButtonPressed(self):
        print(self.startButton.text())
        if self.selectedExercise is None:
            print("debug: Doing nothing, no exercise was selected")
        elif self.startButton.text() == "Start":
            self.timer.start()
            print(f"data collection for {self.selectedExercise} started")
            self.startButton.setText("Stop")
        else:
            self.timer.stop()
            print(f"data collection for {self.selectedExercise} stopped")
            self.startButton.setText("Start")


    def retrieveData(self):
        # do something with retrieved data
        self.sensorDataCollector.readData()




        

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
