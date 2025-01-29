from data_view_publisher import DataViewPublisher
from widgets import DataPageInterface
from style_sheets import *
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel, QButtonGroup, QRadioButton, QTextEdit
from PyQt6.QtCore import Qt

class FeedbackPage(DataPageInterface):
    def __init__(self, dataSource: DataViewPublisher):
        super().__init__()
        self.setup()
        self.selectedExercise = None
        self.dataSource = dataSource
        self.dataSource.subscribe(self)

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
        feedbackText = QTextEdit()
        feedbackText.setText("Placeholder text")
        feedbackText.setReadOnly(True)
        feedbackText.setStyleSheet(PLACEHOLDER_STYLE_SHEET)
        self.feedBackText: QTextEdit = feedbackText
        self.startButton = QPushButton()
        self.startButton.setText("Start")
        self.startButton.clicked.connect(self.startButtonPressed)
        layout.setSpacing(10)
        layout.addWidget(self.feedBackText)
        layout.addWidget(self.startButton)
        feedbackBox.setMinimumHeight(700)
        feedbackBox.setStyleSheet(FEEDBACK_BOX_STYLE_SHEET)
        return feedbackBox

    def updateSelectedExercise(self, exercise: str):
        self.selectedExercise = exercise

    def startButtonPressed(self):
        if self.selectedExercise is None:
            print("debug: Doing nothing, no exercise was selected")
            return
        elif self.startButton.text() == "Start":
            self.startButton.setText("Stop")
        else:
            self.startButton.setText("Start")
        self.dataSource.toggleCollectData(self.selectedExercise)

    def updateData(self, data):
        # do something with updated data
        self.feedBackText.append("simulated data returned: " + str(data))