from abc import abstractmethod
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import random

class LegDisplay(QOpenGLWidget):
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBegin(GL_LINE_LOOP)
        points = [[random.random()%1,0.5],[-0.5, -0.5], [0.5, -0.5]]
        for point in points:
            glColor3f(1.0, 0.0, 0.0)
            glVertex3f(point[0], point[1], 0.0)
        glEnd()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

class LegFunctions:
    def __init__(self):
        self.thigh_start = 0
        self.thigh_end = self.thigh_start + 0.527
        self.shank_start = self.thigh_end
        self.shank_end = self.thigh_end + 0.2835
        self.foot_top = self.shank_end
        self.knee_deg = 0 
        self.ankle_deg = 90 
        self.foot_com = 0

    @abstractmethod
    def updateLeg(self):
        pass

    def getPoints(self):
        # returns array of all points to draw
        pass