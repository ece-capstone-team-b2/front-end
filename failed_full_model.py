import sys
import serial
from serial.tools import list_ports
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


def list_serial_ports():
    """List available serial ports."""
    ports = list_ports.comports()
    return [port.device for port in ports]

def select_serial_port(ports):
    """Ask user to select a serial port."""
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")

    while True:
        try:
            index = int(input("Select a port by number: "))
            if 0 <= index < len(ports):
                return ports[index]
        except ValueError:
            pass
        print("Invalid selection. Try again.")

def rotate_point_around_axis(xyz, axis_phi, axis_theta, rotation_angle_degrees):
    """
    Rotate a point (x, y, z) by 'rotation_angle_degrees' around an arbitrary axis 
    defined by spherical coordinates (axis_phi, axis_theta).
    
    Parameters:
    - x, y, z: Coordinates of the point.
    - axis_phi: Azimuthal angle (in degrees) of the rotation axis measured from the positive x-axis.
    - axis_theta: Polar angle (in degrees) of the rotation axis measured from the positive z-axis.
    - rotation_angle_degrees: The angle (in degrees) to rotate the point.
    
    Returns:
    A tuple (x_rot, y_rot, z_rot) representing the rotated point.
    """
    x, y, z = xyz
    # Convert spherical angles from degrees to radians
    phi = axis_phi
    theta = axis_theta

    print(f"Phi {phi}, theta {theta}")
    
    # Convert the spherical axis to a Cartesian unit vector
    u_x = np.sin(theta) * np.cos(phi)
    u_y = np.sin(theta) * np.sin(phi)
    u_z = np.cos(theta)
    u = np.array([u_x, u_y, u_z])
    
    # Ensure the axis is a unit vector (should already be the case from spherical conversion)
    u = u / np.linalg.norm(u)
    
    print(f"Rotating around {u}")

    # Convert the rotation angle from degrees to radians
    angle = rotation_angle_degrees
    
    # Define the original point as a numpy array
    v = np.array([x, y, z])
    
    # Apply Rodrigues' rotation formula
    v_rot = (v * np.cos(angle) +
             np.cross(u, v) * np.sin(angle) +
             u * np.dot(u, v) * (1 - np.cos(angle)))
    
    return np.array([v_rot[0], v_rot[1], v_rot[2]])


class LegVisualizer(QMainWindow):
    def __init__(self, ser):
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

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(16)  # ~60 FPS
        self.ser = ser

        self.lower_leg_angle_knee = 0
        self.thigh_angle_knee = 0
        self.thigh_horizontal_angle = 0
        self.lower_leg_roll = 0
        self.knee_angle = 0

    
    def update_loop(self):
        try:
            data = self.ser.readline().decode().strip()
            if data:
                vals = [float(d) for d in data.split(",")]
                print(vals)
                print(data)
                if int(vals[0]) == 0:
                    self.lower_leg_roll = -1 * (90 - vals[3])
                    self.lower_leg_angle_knee = 90 + vals[2]
                    if (vals[1] < 100):
                        self.thigh_horizontal_angle = vals[1]
                    else:
                        self.thigh_horizontal_angle = vals[1] - 360
                else:
                    self.thigh_angle_knee = vals[2]
                self.knee_angle = self.thigh_angle_knee - self.lower_leg_angle_knee

                self.update_plot()
        except:
            pass
        

    def rot(self,xyz, theta):
        (x, y, z) = xyz
        return np.array([
            x,
            y * np.cos(theta) - z * np.sin(theta),
            y * np.sin(theta) + z * np.cos(theta)
        ]
        )

    def update_plot(self):
        self.ax.clear()

        # Read slider values
        # self.hip_angle = self.hip_slider.value()
        # self.hip_y_angle = self.hip_y_slider.value()
        # self.knee_angle = self.knee_slider.value()
        # self.ankle_angle = self.ankle_slider.value()
        # self.hip_roll_angle = self.hip_roll_slider.value()

        self.hip_angle = self.thigh_angle_knee
        self.hip_y_angle = 0#self.thigh_horizontal_angle
        self.ankle_angle = 90
        self.hip_roll_angle = 0#self.lower_leg_roll

        phi_thigh = np.deg2rad(self.hip_angle)
        phi_lower = phi_thigh + np.deg2rad(-1 * self.knee_angle)
        phi_foot = phi_lower  + np.deg2rad(self.ankle_angle)
        roll_angle = np.deg2rad(self.hip_roll_angle)

        print(f"Roll: {self.hip_roll_angle}")
        theta = np.deg2rad(self.hip_y_angle)


        # Define joint positions:
        # Hip is at the origin.
        hip = np.array([0, 0, 0])
        # Thigh (hip to knee)
        knee = hip + np.array([self.thigh_length * np.cos(theta) * np.sin(phi_thigh),
                                 
                                 self.thigh_length * np.sin(theta) * np.sin(phi_thigh), 
                                 self.thigh_length * np.cos(phi_thigh)])
        # Lower leg (knee to ankle)
        ankle = knee + rotate_point_around_axis([self.lower_leg_length * np.cos(theta) * np.sin(phi_lower),
                                 
                                 self.lower_leg_length * np.sin(theta) * np.sin(phi_lower), 
                                 self.lower_leg_length * np.cos(phi_lower)], theta, phi_thigh, roll_angle)
        # Foot (ankle to toe)
        toe = ankle + rotate_point_around_axis([self.foot_length * np.cos(theta) * np.sin(phi_foot),
                                 
                                  self.foot_length * np.sin(theta) * np.sin(phi_foot), 
                                  self.foot_length * np.cos(phi_foot)], theta, phi_thigh, roll_angle)
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
    ports = list_serial_ports()
    if not ports:
        print("No serial devices found.")
    else:
        selected_port = select_serial_port(ports)
    app = QApplication(sys.argv)
    window = LegVisualizer(serial.Serial(selected_port, 115200, timeout=1))
    window.show()
    sys.exit(app.exec())