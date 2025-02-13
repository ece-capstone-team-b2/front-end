from abc import abstractmethod
import math
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import random

class LegDisplay(QOpenGLWidget,):
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        self.points = [[random.random()%1,0.5],[-0.5, -0.5], [0.5, -0.5]]
    
    def updatePoints(self, new_points):
        self.points = new_points

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBegin(GL_LINE_LOOP)
        
        for point in self.points:
            glColor3f(1.0, 0.0, 0.0)
            glVertex3f(point[0], point[1], 0.0)

        glEnd()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

class LegFunctions:
    def __init__(self):
        # these do not change
        # starts (closer to head)
        
        self.thigh_end = [0, 0]
        self.thigh_start = [0, (self.thigh_end[1] + 0.527)]
        self.shank_start = self.thigh_end
        self.shank_end = [0, self.thigh_end[1] - 0.2835]
        self.foot_top = self.shank_end
        self.foot_bottom = [0.1515, (self.foot_top[1] - 0.0455)]

        # these do change
        self.knee_deg = 0 
        self.ankle_deg = 90 
        self.foot_com = 0

    def updateLeg(self, knee_deg, ankle_deg, foot_com):
        self.knee_deg = knee_deg - 90
        self.ankle_deg = ankle_deg
        self.foot_com = foot_com

    @abstractmethod
    def getPoints(self):
        # returns array of all points to draw
        pass

class SideLegFunctions(LegFunctions):
    def __init__(self):
        super().__init__()

    def getPoints(self):
        current_thigh_end = [0, self.thigh_end[1]]
        current_thigh_start = [math.sqrt((self.thigh_start[1])**2)-((self.thigh_start[1]*self.knee_deg/90)**2), (self.thigh_start[1]*self.knee_deg/90)]
        current_shank_start = []
        current_shank_end = []
        current_foot_start = []
        current_foot_end = []
        return [current_thigh_start, current_thigh_end]
    
class FrontLegFunctions(LegFunctions):
    def __init__(self):
        super().__init__()

    def getPoints(self):
        current_thigh_end = [0, self.thigh_end[1]]
        current_thigh_start = [0, (self.thigh_start[1]*self.knee_deg/90)]
        current_shank_start = []
        current_shank_end = []
        current_foot_start = []
        current_foot_end = []
        return [current_thigh_start, current_thigh_end]