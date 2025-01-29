from sensor_data_collector import SensorDataCollector
from data_view_publisher import DataViewPublisher
from widgets import DataPageInterface
from typing import List
from style_sheets import *
from PyQt6.QtWidgets import QLabel, QGridLayout, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import random

class RawDataPage(DataPageInterface):
    def __init__(self, data_source: DataViewPublisher):
        super().__init__()
        self.sensor_data_collector = SensorDataCollector()
        self.data_source = data_source
        self.data_source.subscribe(self)
        self.data = []
        
        self.setup()
    
    def setup(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setStretch(0,1)

        # as an example
        self.randomData = []
        self.fig = Figure()
        self.canvas = Canvas(self.fig)
        #self.axes: List[Axes] = []
        for i in range(1,5):
            axes = self.fig.add_subplot(2,2,i)
            axes.plot([], [], 'r')
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def updateData(self, data):
        self.randomData.append(random.randint(1,10))
        self.data.append(data)
        for ax in self.fig.axes:
            ax.cla()
            ax.plot(self.data, self.randomData, 'r')
        self.canvas.draw()


