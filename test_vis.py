import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class LegVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leg Model Visualization")

        # Segment lengths (arbitrary units)
        self.thigh_length = 4
        self.lower_leg_length = 4
        self.foot_length = 1

        # Default angles (in degrees)
        self.hip_angle = 90      # Hip (thigh) angle relative to the x-axis.
        self.hip_y_angle = 0
        self.hip_roll_angle = 0
        self.knee_angle = 45    # Knee angle relative to the thigh.
        self.ankle_angle = 90    # Ankle angle relative to the lower leg.

        # Set up the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create a matplotlib figure with a 3D axes
        self.fig = plt.figure(figsize=(10, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)

        # Create a horizontal layout for the sliders
        slider_layout = QHBoxLayout()
        main_layout.addLayout(slider_layout)

        # Hip angle slider
        hip_label = QLabel("Hip Angle")
        slider_layout.addWidget(hip_label)
        self.hip_slider = QSlider(Qt.Orientation.Horizontal)
        self.hip_slider.setRange(-90, 150)
        self.hip_slider.setValue(self.hip_angle)
        self.hip_slider.setTickInterval(5)
        self.hip_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hip_slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(self.hip_slider)

        hip_horizontal_label = QLabel("Hip Y Angle")
        slider_layout.addWidget(hip_horizontal_label)
        self.hip_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.hip_y_slider.setRange(-150, 150)
        self.hip_y_slider.setValue(self.hip_y_angle)
        self.hip_y_slider.setTickInterval(5)
        self.hip_y_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hip_y_slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(self.hip_y_slider)

        hip_roll_label = QLabel("Hip Roll Angle")
        slider_layout.addWidget(hip_roll_label)
        self.hip_roll_slider = QSlider(Qt.Orientation.Horizontal)
        self.hip_roll_slider.setRange(-150, 150)
        self.hip_roll_slider.setValue(self.hip_roll_angle)
        self.hip_roll_slider.setTickInterval(5)
        self.hip_roll_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hip_roll_slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(self.hip_roll_slider)

        # Knee angle slider
        knee_label = QLabel("Knee Angle")
        slider_layout.addWidget(knee_label)
        self.knee_slider = QSlider(Qt.Orientation.Horizontal)
        self.knee_slider.setRange(0, 180)
        self.knee_slider.setValue(self.knee_angle)
        self.knee_slider.setTickInterval(5)
        self.knee_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.knee_slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(self.knee_slider)

        # Ankle angle slider
        ankle_label = QLabel("Ankle Angle")
        slider_layout.addWidget(ankle_label)
        self.ankle_slider = QSlider(Qt.Orientation.Horizontal)
        self.ankle_slider.setRange(0, 140)
        self.ankle_slider.setValue(self.ankle_angle)
        self.ankle_slider.setTickInterval(5)
        self.ankle_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ankle_slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(self.ankle_slider)

        # Draw the initial plot
        self.update_plot()

    def update_plot(self):
        self.ax.clear()

        # Read slider values
        print(self.hip_angle)
        print(self.hip_y_angle)
        self.hip_angle = self.hip_slider.value()
        self.hip_y_angle = self.hip_y_slider.value()
        self.knee_angle = self.knee_slider.value()
        self.ankle_angle = self.ankle_slider.value()


        phi_thigh = np.deg2rad(self.hip_angle)
        phi_lower = phi_thigh + np.deg2rad(-1 * self.knee_angle)
        phi_foot = phi_lower  + np.deg2rad(self.ankle_angle)
        roll_angle = np.deg2rad(self.hip_roll_angle)

        theta = np.deg2rad(self.hip_y_angle)


        # Define joint positions:
        # Hip is at the origin.
        hip = np.array([0, 0, 0])
        # Thigh (hip to knee)
        knee = hip + np.array([self.thigh_length * np.cos(theta) * np.sin(phi_thigh),
                                 
                                 self.thigh_length * np.sin(theta) * np.sin(phi_thigh), 
                                 self.thigh_length * np.cos(phi_thigh)])
        # Lower leg (knee to ankle)
        ankle = knee + np.array([self.lower_leg_length * np.cos(theta) * np.sin(phi_lower),
                                 
                                 self.lower_leg_length * np.sin(theta) * np.sin(phi_lower), 
                                 self.lower_leg_length * np.cos(phi_lower)])
        # Foot (ankle to toe)
        toe = ankle + np.array([self.foot_length * np.cos(theta) * np.sin(phi_foot),
                                 
                                 self.foot_length * np.sin(theta) * np.sin(phi_foot), 
                                 self.foot_length * np.cos(phi_foot)])
        # Plot the segments as lines
        self.ax.plot([hip[0], knee[0]], [hip[1], knee[1]], [hip[2], knee[2]], 'r-', lw=3, label="Thigh")
        self.ax.plot([knee[0], ankle[0]], [knee[1], ankle[1]], [knee[2], ankle[2]], 'g-', lw=3, label="Lower Leg")
        self.ax.plot([ankle[0], toe[0]], [ankle[1], toe[1]], [ankle[2], toe[2]], 'b-', lw=3, label="Foot")

        # Set plot limits and labels
        total_length = self.thigh_length + self.lower_leg_length + self.foot_length
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_zlim(-10, 10)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.legend()

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LegVisualizer()
    window.show()
    sys.exit(app.exec())