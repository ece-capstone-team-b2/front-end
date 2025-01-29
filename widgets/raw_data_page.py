from sensor_data_collector import SensorDataCollector
from data_view_publisher import DataViewPublisher
from widgets import DataPageInterface
from style_sheets import *
from PyQt6.QtWidgets import QGridLayout, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
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
        layout = QGridLayout()
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        
        # ==== start of an example ====
        self.randomData = []
        self.fig1 = Figure()
        self.fig2 = Figure()
        self.canvas1 = Canvas(self.fig1)
        self.canvas2 = Canvas(self.fig2)
        axes = self.fig1.add_subplot(1,1,1)
        axes.plot(self.data, self.randomData, 'r')
        axes = self.fig2.add_subplot(1,1,1)
        axes.scatter(self.randomData, self.data)

        self.rawData1 = QTextEdit()
        self.rawData1.setText("Placeholder text")
        self.rawData1.setReadOnly(True)
        self.rawData1.setStyleSheet(PLACEHOLDER_STYLE_SHEET)

        self.rawData2 = QTextEdit()
        self.rawData2.setText("Placeholder text")
        self.rawData2.setReadOnly(True)
        self.rawData2.setStyleSheet(PLACEHOLDER_STYLE_SHEET)
        
        
        layout.addWidget(self.canvas1, 0, 1)
        layout.addWidget(self.canvas2, 1, 1)
        layout.addWidget(self.rawData1, 0, 0)
        layout.addWidget(self.rawData2, 1, 0)

        # ==== end of example ====
        self.setLayout(layout)

    def updateData(self, data):
        # example of updating data
        rand = random.randint(1,10)
        self.randomData.append(rand)
        self.data.append(data)
        for ax in self.fig1.axes:
            ax.cla()
            ax.plot(self.data, self.randomData, 'r')
        for ax in self.fig2.axes:
            ax.cla()
            ax.scatter(self.randomData, self.data)
        self.canvas1.draw()
        self.canvas2.draw()
        self.rawData1.append(str(data))
        self.rawData2.append(str(rand))


