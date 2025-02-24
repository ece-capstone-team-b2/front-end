from abc import abstractmethod
import math
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import random

import numpy as np

class LegDisplay(QOpenGLWidget,):
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        self.points = [[random.random()%1,0.5],[-0.5, -0.5], [0.5, -0.5]]
    
    def updatePoints(self, new_points):
        self.points = new_points

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBegin(GL_LINES)
        
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
        self.thigh_start = [0, (self.thigh_end[1] + 0.289)]
        self.shank_start = self.thigh_end
        self.shank_end = [0, self.thigh_end[1] - 0.238]
        self.foot_top = self.shank_end

        # these do change

        # knee degree is always considered in the posterior/anterior direction
        # it represents the ankle between the shank and thigh
        self.knee_deg = 0 

        # ankle degree from the side is in the posterior/anterior direction
        # ankle degree from the front is in the medial/lateral direction
        # it represents the angle between the plane of the foot and the shank
        self.ankle_deg = 90 

        # foot com from the side is in the posterior/anterior direction
        # foot com from the front is in the medial/lateral direction
        # it represents the coordinate on the plane of the foot where the center of mass is on a range of [-1,1]
        # -1 is posterior or left; +1 is anterior or right
        self.foot_com = 0

    def updateLeg(self, knee_deg, ankle_deg, foot_com):
        self.knee_deg = knee_deg - 90
        self.ankle_deg = ankle_deg
        self.foot_com = foot_com

    def getSomePoints(self, start, end, top_width, bottom_width):
        pass

    @abstractmethod
    def getPoints(self):
        # returns array of all points to draw
        pass

class SideLegFunctions(LegFunctions):
    def __init__(self):
        super().__init__()
        self.foot_bottom = [0.1515, (self.foot_top[1] - 0.0455)]

    def getPoints(self):
        current_thigh_end = [0, self.thigh_end[1]]
        current_thigh_start = [math.sqrt((self.thigh_start[1])**2)-((self.thigh_start[1]*self.knee_deg/90)**2), (self.thigh_start[1]*self.knee_deg/90)]
        current_shank_end = self.shank_end
        if(self.foot_com < 0):
            current_foot_left = [-self.foot_bottom[0]/2, self.foot_bottom[1]]
            current_foot_right = [self.foot_bottom[0]/2, self.foot_bottom[1]-(self.foot_bottom[1]-self.foot_top[1])*abs(self.foot_com)]
        else:
            current_foot_left = [-self.foot_bottom[0]/2, self.foot_bottom[1]-(self.foot_bottom[1]-self.foot_top[1])*self.foot_com]
            current_foot_right = [self.foot_bottom[0]/2, self.foot_bottom[1]]
        return [current_thigh_start, current_thigh_end, current_thigh_end, current_shank_end, current_shank_end, current_foot_left, current_foot_left, current_foot_right, current_foot_right, current_shank_end]
    
class FrontLegFunctions(LegFunctions):
    def __init__(self):
        super().__init__()
        self.foot_bottom = [0.0455, (self.foot_top[1] - 0.0455)]

    def getPoints(self):
        current_thigh_end = [0, self.thigh_end[1]]
        current_thigh_start = [0, (self.thigh_start[1]*self.knee_deg/90)]
        current_shank_end = self.shank_end
        if(self.foot_com < 0):
            current_foot_left = [-self.foot_bottom[0]/2, self.foot_bottom[1]]
            current_foot_right = [self.foot_bottom[0]/2, self.foot_bottom[1]-(self.foot_bottom[1]-self.foot_top[1])*abs(self.foot_com)]
        else:
            current_foot_left = [-self.foot_bottom[0]/2, self.foot_bottom[1]-(self.foot_bottom[1]-self.foot_top[1])*self.foot_com]
            current_foot_right = [self.foot_bottom[0]/2, self.foot_bottom[1]]

        
        points = []

        hip_width = 0.23
        thigh_width = 0.25
        knee_width = 0.2
        shank_width = 0.22
        ankle_width = 0.15
        step_size = 0.001

        if not self.knee_deg < 1:
            rangie = math.ceil((current_thigh_start[1]-current_thigh_end[1])/step_size)
            
            width = np.arange(hip_width, thigh_width, (thigh_width-hip_width)/rangie).tolist()

            i = current_thigh_start[1]
            while(i >= current_thigh_end[1]):
                print((i - current_thigh_start[1])/(-step_size))
                location = int((i - current_thigh_start[1])/(-step_size))
                points += [[-width[location], i]]
                i -= step_size

            if(len(points)%2 == 1):
                points = points[:-1]
            
            i = current_thigh_start[1]
            while(i >= current_thigh_end[1]):
                location = int((i - current_thigh_start[1])/(-step_size))
                points += [[width[location], i]]
                i -= step_size
            
            if(len(points)%2 == 1):
                points = points[:-1]

        return points + [current_thigh_end, current_shank_end, current_shank_end, current_foot_left, current_foot_left, current_foot_right, current_foot_right, current_shank_end]