import sys
import time
import serial
from serial.tools import list_ports
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
)
from data_logging import DataLogger
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from quaternion_math import *
from serial_port_capture import *


class LegVisualizer(QMainWindow):
    def __init__(self, data_queue, datalogger):
        super().__init__()
        self.setWindowTitle("Leg Model Visualization")

        # Segment lengths (arbitrary units)
        self.thigh_length = 4
        self.lower_leg_length = 4
        self.foot_length = 1

        # Set up the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create a matplotlib figure with a 3D axes
        self.fig = plt.figure(figsize=(10, 10))
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)

        # Draw the initial plot

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(1)  # ~60 FPS
        self.r_thigh_quat = (1, 0, 0, 0)
        self.r_leg_quat = (1, 0, 0, 0)

        self.l_thigh_quat = (1, 0, 0, 0)
        self.l_leg_quat = (1, 0, 0, 0)
        self.last_time = time.time()
        self.last_draw_time = time.time()
        self.data_queue = data_queue
        self.datalogger: DataLogger = datalogger

    def update_loop(self):
        data = None
        while not self.data_queue.empty():
            print(self.data_queue.qsize())
            data = self.data_queue.get()
            self.datalogger.update(data)
            if isinstance(data, ImuData):
                break
            else:
                data = None
        if data is None:
            return
        imu_data = data

        device_num = imu_data.nodeId
        if device_num == 2:
            # Thigh/knee nod
            self.r_thigh_quat = imu_data.positionData.quatOrientation

            theta = -90
            theta_rad = np.radians(theta)
            q_rotation = np.array(
                [np.cos(theta_rad / 2), 0, 0, np.sin(theta_rad / 2)]  # w  # x  # y  # z
            )

            self.r_thigh_quat = rotate_quaternion_by_quaternion(
                self.r_thigh_quat, q_rotation
            )

        if device_num == 4:
            self.r_leg_quat = imu_data.positionData.quatOrientation
            theta = -90
            theta_rad = np.radians(theta)
            q_rotation = np.array(
                [np.cos(theta_rad / 2), 0, 0, np.sin(theta_rad / 2)]  # w  # x  # y  # z
            )

            self.r_leg_quat = rotate_quaternion_by_quaternion(
                self.r_leg_quat, q_rotation
            )
        if device_num == 1:

            self.l_thigh_quat = imu_data.positionData.quatOrientation

            theta = -90
            theta_rad = np.radians(theta)
            q_rotation = np.array(
                [np.cos(theta_rad / 2), 0, 0, np.sin(theta_rad / 2)]  # w  # x  # y  # z
            )

            self.l_thigh_quat = rotate_quaternion_by_quaternion(
                self.l_thigh_quat, q_rotation
            )
        if device_num == 3:

            self.l_leg_quat = imu_data.positionData.quatOrientation
            theta = -90
            theta_rad = np.radians(theta)
            q_rotation = np.array(
                [np.cos(theta_rad / 2), 0, 0, np.sin(theta_rad / 2)]  # w  # x  # y  # z
            )

            self.l_leg_quat = rotate_quaternion_by_quaternion(
                self.l_leg_quat, q_rotation
            )

        self.update_plot()

    def update_plot(self):
        if time.time() - self.last_draw_time < 0.1:
            return
        self.last_draw_time = time.time()
        self.ax.clear()

        # Define joint positions:
        # Hip is at the origin.
        r_hip = np.array([0, 0, 0])
        # Thigh (hip to knee)
        r_thigh_vector = standard_vector(self.thigh_length)
        r_knee = r_hip + rotate_vector_by_quaternion(r_thigh_vector, self.r_thigh_quat)
        r_leg_vector = standard_vector(self.lower_leg_length)

        r_ankle = r_knee + rotate_vector_by_quaternion(r_leg_vector, self.r_leg_quat)

        r_q_thigh_conj = quaternion_conjugate(self.r_thigh_quat)
        r_q_rel = quaternion_multiply(self.r_leg_quat, r_q_thigh_conj)
        _, r_knee_angle = quaternion_to_axis_angle(r_q_rel)

        print("Effective right knee rotation angle (radians):", r_knee_angle)
        print(
            "Effective right knee rotation angle (degrees):",
            360 - np.degrees(r_knee_angle),
        )

        # Plot the segments as lines
        self.ax.plot(
            [r_hip[0], r_knee[0]],
            [r_hip[1], r_knee[1]],
            [r_hip[2], r_knee[2]],
            "r-",
            lw=3,
            label="R Thigh",
        )
        self.ax.plot(
            [r_knee[0], r_ankle[0]],
            [r_knee[1], r_ankle[1]],
            [r_knee[2], r_ankle[2]],
            "g-",
            lw=3,
            label="R Lower Leg",
        )
        # self.ax.plot([ankle[0], toe[0]], [ankle[1], toe[1]], [ankle[2], toe[2]], 'b-', lw=3, label="Foot")

        l_hip = np.array([0, 0, 0])
        # Thigh (hip to knee)
        l_thigh_vector = standard_vector(self.thigh_length)
        l_knee = l_hip + rotate_vector_by_quaternion(l_thigh_vector, self.l_thigh_quat)
        l_leg_vector = standard_vector(self.lower_leg_length)

        l_ankle = l_knee + rotate_vector_by_quaternion(l_leg_vector, self.l_leg_quat)

        l_q_thigh_conj = quaternion_conjugate(self.l_thigh_quat)
        l_q_rel = quaternion_multiply(self.l_leg_quat, l_q_thigh_conj)
        _, l_knee_angle = quaternion_to_axis_angle(l_q_rel)

        print("Effective right knee rotation angle (radians):", l_knee_angle)
        print(
            "Effective right knee rotation angle (degrees):",
            360 - np.degrees(l_knee_angle),
        )

        # Plot the segments as lines
        self.ax.plot(
            [l_hip[0], l_knee[0]],
            [l_hip[1], l_knee[1]],
            [l_hip[2], l_knee[2]],
            "b-",
            lw=3,
            label="L Thigh",
        )
        self.ax.plot(
            [l_knee[0], l_ankle[0]],
            [l_knee[1], l_ankle[1]],
            [l_knee[2], l_ankle[2]],
            "b-",
            lw=3,
            label="L Lower Leg",
        )
        # self.ax.plot([ankle[0], toe[0]], [ankle[1], toe[1]], [ankle[2], toe[2]], 'b-', lw=3, label="Foot")

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
    ports = list_serial_ports()
    if not ports:
        print("No serial devices found.")
    else:
        selected_port = select_serial_port(ports)
    app = QApplication(sys.argv)
    queue = Queue()
    file_prefix = "log_full_data_2"
    datalogger = DataLogger(csv_file=f"{file_prefix}.csv")
    window = LegVisualizer(queue, datalogger)

    serial_monitor = SerialPortCapture(
        serial.Serial(selected_port, 115200, timeout=1), queue, f"{file_prefix}.bin"
    )
    window.show()
    serial_monitor.start()
    sys.exit(app.exec())
