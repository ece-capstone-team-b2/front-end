import sys
import time
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QMatrix4x4, QVector3D
from PyQt6.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *

import struct
import serial
import serial.tools.list_ports

def list_serial_ports():
    """List available serial ports."""
    ports = serial.tools.list_ports.comports()
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

def read_serial_data(port, baudrate=115200):
    """Read data continuously from the selected serial port."""
    try:
        with serial.Serial(port, baudrate) as ser:
            print(f"Reading from {port}... (Press Ctrl+C to stop)")
            data = ser.read(204)
            print(len(data))

            return data
    except serial.SerialException as e:
        print(f"Serial error: {e}")

class NavballWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.euler_angles = [0.0, 0.0, 0.0]  # Yaw, Pitch, Roll

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height if height else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        
        glRotatef(self.euler_angles[0], 0, 1, 0)  # Yaw
        glRotatef(self.euler_angles[1], 1, 0, 0)  # Pitch
        glRotatef(self.euler_angles[2], 0, 0, 1)  # Roll
        
        self.draw_cube()
    
    def draw_cube(self):
        glBegin(GL_QUADS)
        glColor3f(1.0, 0.0, 0.0)  # Red
        glVertex3f( 1.0, 1.0,-1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f( 1.0, 1.0, 1.0)
        
        glColor3f(0.0, 1.0, 0.0)  # Green
        glVertex3f( 1.0,-1.0, 1.0)
        glVertex3f(-1.0,-1.0, 1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f( 1.0,-1.0,-1.0)
        
        glColor3f(0.0, 0.0, 1.0)  # Blue
        glVertex3f( 1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0,-1.0, 1.0)
        glVertex3f( 1.0,-1.0, 1.0)
        
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        glVertex3f( 1.0,-1.0,-1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f( 1.0, 1.0,-1.0)
        
        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f(-1.0,-1.0, 1.0)
        
        glColor3f(0.0, 1.0, 1.0)  # Cyan
        glVertex3f( 1.0, 1.0,-1.0)
        glVertex3f( 1.0, 1.0, 1.0)
        glVertex3f( 1.0,-1.0, 1.0)
        glVertex3f( 1.0,-1.0,-1.0)
        glEnd()
    
    def set_orientation(self, yaw, pitch, roll):
        self.euler_angles = [yaw, pitch, roll]
        self.update()

class MainWindow(QMainWindow):
    def __init__(self, port):
        super().__init__()
        self.setWindowTitle("3D Navball Simulation")
        self.setGeometry(100, 100, 800, 600)
        self.navball = NavballWidget(self)
        self.setCentralWidget(self.navball)
        
        # Timer for updating
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # Approx 60 FPS
        self.port = port
        self.show()
    
    def update_scene(self):
        """Update the 3D scene and perform other tasks."""

        x,y,z = read_serial_data(self.port)
        self.navball.set_orientation(
            -x,y,z
        )

if __name__ == "__main__":
    ports = list_serial_ports()
    if not ports:
        print("No serial devices found.")
    else:
        selected_port = select_serial_port(ports)
    app = QApplication(sys.argv)
    window = MainWindow(selected_port)
    sys.exit(app.exec())



