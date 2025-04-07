import random
import time

from PyQt6.QtCore import Qt
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from data_processing import DerivedLegMetrics
from data_processor import DataProcessor
from squat_tracking import SquatTracker
from style_sheets import *
from widgets import DataPageInterface
from widgets.leg_display import FrontLegFunctions, LegDisplay, SideLegFunctions


class FeedbackPage(DataPageInterface):
    def __init__(
        self,
        dataSource,
        squat_tracker: SquatTracker,
        data_processor: DataProcessor,
        visible: bool = False,
    ):
        super().__init__()
        self.setup()
        self.selectedExercise = None
        self.dataSource = dataSource
        self.dataSource.subscribe(self)
        self.visible = visible
        self.squat_tracker = squat_tracker
        self.data_processor = data_processor
        self.data_processor.add_callback(self.new_data)
        self.squats_performed = 0
        self.squats_attempted = 0

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
        self.last_draw_time = time.time() * 1000

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
        frontvisualizationbox = QWidget(self)
        sidevisualizationbox = QWidget(self)
        layout = QVBoxLayout(visualizationBox)
        toplayout = QHBoxLayout(frontvisualizationbox)
        sidelayout = QHBoxLayout(sidevisualizationbox)
        self.parent = QOpenGLWidget()

        self.leftfrontlegfunctions = FrontLegFunctions()
        self.rightfrontlegfunctions = FrontLegFunctions()
        self.leftfrontview = LegDisplay(self.parent)
        self.rightfrontview = LegDisplay(self.parent)

        self.leftsidelegfunctions = SideLegFunctions("left")
        self.rightsidelegfunctions = SideLegFunctions("right")
        self.leftsideview = LegDisplay(self.parent)
        self.rightsideview = LegDisplay(self.parent)

        leftlabel = QLabel("Left")
        leftlabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        rightlabel = QLabel("Right")
        rightlabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        labelbox = QWidget(self)
        labelbox.setFixedHeight(40)
        labellayout = QHBoxLayout(labelbox)
        labellayout.addWidget(leftlabel)
        labellayout.addWidget(rightlabel)

        toplayout.addWidget(self.leftfrontview)
        toplayout.addWidget(self.rightfrontview)
        sidelayout.addWidget(self.leftsideview)
        sidelayout.addWidget(self.rightsideview)
        layout.addWidget(labelbox)
        layout.addWidget(frontvisualizationbox)
        layout.addWidget(sidevisualizationbox)
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
        feedbackText.setText("Please select an exercise")
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
            self.feedBackText.append("No exercise was selected")
            return
        elif self.startButton.text() == "Start":
            self.feedBackText.clear()
            self.startButton.setText("Stop")
            self.squat_tracker.reset()
            self.squat_tracker.start()
        else:
            self.startButton.setText("Start")
            self.squat_tracker.reset()
            self.squat_tracker.start()
            self.squats_performed = 0
            self.squats_attempted = 0

    def squat_performed(self, results):
        self.feedbackText.clear()
        self.feedbackText.append(
            f"Squats attempted: {self.squats_attempted}, perfect form: {self.squats_performed}"
        )
        if results["max_l_angle"] < 60 or results["max_r_angle"] < 60:
            self.feedbackText.append(
                "Squat too shallow! Try to bend your knees closer to 90 degrees!"
            )
        elif results["max_l_angle"] > 140 or results["max_r_angle"] > 140:
            self.feedbackText.append(
                "Squat too deep! Try to bend your knees closer to 90 degrees!"
            )
        elif results["average_thigh_angle"] > 45:
            self.feedbackText.append(
                "The angle between your legs is too high! Try to make your legs parallel to each other during the squat motion."
            )
        elif results["average_r_foot_cy"] < -5 or results["average_r_foot_cy"] < -5:
            self.feedbackText.append(
                ""
                "Your weight is too far forward! Try to lean back more and balance right over your ankles."
            )
        elif results["average_r_foot_cy"] > 8 or results["average_r_foot_cy"] > 8:
            self.feedbackText.append(
                ""
                "Your weight is too far backwards! Try to lean forward more and balance right over your ankles."
            )
        else:
            self.feedbackText.append("Good form!")
            self.squats_performed += 1
        self.squats_attempted += 1

    def new_data(self, metrics: DerivedLegMetrics):
        if time.time() * 1000 - self.last_draw_time < 300:
            return
        self.last_draw_time = time.time() * 1000
        # do something with updated data

        left_knee = max(min(180, metrics.l_knee_angle + 90), 0)
        left_foot_balance_y = metrics.l_force_cy / 11.75
        left_foot_balance_x = metrics.l_force_cx / 4.5

        right_knee = max(min(180, metrics.r_knee_angle + 90), 0)
        right_foot_balance_y = metrics.r_force_cy / 11.75
        right_foot_balance_x = metrics.r_force_cx / 4.5

        print(left_knee)
        print(right_knee)

        self.leftfrontlegfunctions.updateLeg(left_knee, 90, left_foot_balance_x)
        self.leftfrontview.updatePoints(self.leftfrontlegfunctions.getPoints())
        self.leftfrontview.update()

        self.rightfrontlegfunctions.updateLeg(right_knee, 90, right_foot_balance_x)
        self.rightfrontview.updatePoints(self.rightfrontlegfunctions.getPoints())
        self.rightfrontview.update()

        self.leftsidelegfunctions.updateLeg(left_knee, 90, left_foot_balance_y)
        self.leftsideview.updatePoints(self.leftsidelegfunctions.getPoints())
        self.leftsideview.update()

        self.rightsidelegfunctions.updateLeg(right_knee, 90, right_foot_balance_y)
        self.rightsideview.updatePoints(self.rightsidelegfunctions.getPoints())
        self.rightsideview.update()
