from sensor_data_collector import SensorDataCollector
from data_view_publisher import DataViewPublisher
from widgets import DataPageInterface
from style_sheets import *
from PyQt6.QtWidgets import QGridLayout, QTextEdit, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QSlider, QTableWidgetItem
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from data_structures import *
from typing import List

class RawDataPage(DataPageInterface):
    def __init__(self, data_source: DataViewPublisher):
        super().__init__()
        self.sensor_data_collector = SensorDataCollector()
        self.data_source = data_source
        self.data_source.subscribe(self)
        self.data: List[ImuData] = []
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

        self.setupTable()

        self.rawData2 = QTextEdit()
        self.rawData2.setText("Placeholder text")
        self.rawData2.setReadOnly(True)
        self.rawData2.setStyleSheet(PLACEHOLDER_STYLE_SHEET)
        
        
        layout.addWidget(self.canvas1, 0, 1)
        layout.addWidget(self.canvas2, 1, 1)
        layout.addLayout(self.tables_imu, 0, 0)
        layout.addWidget(self.rawData2, 1, 0)

        # ==== end of example ====
        self.setLayout(layout)
    
    def setupTable(self):
        layout = QVBoxLayout()
        
        self.axis3d_table = create_formatted_table(
            rowHeaders=['accelData', 'linearAccelData', 'gravityAccel', 'gyroData', 'magData'],
            colHeaders=['x', 'y', 'z'])

        self.position_table = create_formatted_table(
            rowHeaders=['x', 'y', 'z'],
            colHeaders=['position']
        )

        self.quat_table = create_formatted_table(
            rowHeaders=['w', 'x', 'y', 'z'],
            colHeaders=['quat orientation']
        )

        self.euler_table = create_formatted_table(
            rowHeaders=['roll', 'pitch', 'yaw'],
            colHeaders=['euler orientation']
        )

        position_tables_layout = QHBoxLayout()
        position_tables_layout.addWidget(self.position_table)
        position_tables_layout.addWidget(self.quat_table)
        position_tables_layout.addWidget(self.euler_table)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0,0)
        self.slider.valueChanged.connect(self.update_tables)
    
        layout.addWidget(self.axis3d_table)
        layout.addLayout(position_tables_layout)
        layout.addWidget(self.slider)
        self.tables_imu = layout

    def update_tables(self, value):
        imu_data = self.data[value]
        self.populate_axis3d_row(0, imu_data.accelData)
        self.populate_axis3d_row(1, imu_data.linearAccelData)
        self.populate_axis3d_row(2, imu_data.gravityAccel)
        self.populate_axis3d_row(3, imu_data.gyroData)
        self.populate_axis3d_row(4, imu_data.magData)
        self.populate_position(imu_data.positionData)

    def populate_axis3d_row(self, row: int, data: Axis3d):
        self.axis3d_table.setItem(row, 0, QTableWidgetItem(f'{data.x:.5f}'))
        self.axis3d_table.setItem(row, 1, QTableWidgetItem(f'{data.y:.5f}'))
        self.axis3d_table.setItem(row, 2, QTableWidgetItem(f'{data.z:.5f}'))

    def populate_position(self, data: PositionData):
        self.position_table.setItem(0, 0, QTableWidgetItem(f'{data.position.x:.5f}'))
        self.position_table.setItem(0, 1, QTableWidgetItem(f'{data.position.y:.5f}'))
        self.position_table.setItem(0, 2, QTableWidgetItem(f'{data.position.z:.5f}'))
        self.quat_table.setItem(0, 0, QTableWidgetItem(f'{data.quatOrientation.w:.5f}'))
        self.quat_table.setItem(0, 1, QTableWidgetItem(f'{data.quatOrientation.x:.5f}'))
        self.quat_table.setItem(0, 2, QTableWidgetItem(f'{data.quatOrientation.y:.5f}'))
        self.quat_table.setItem(0, 3, QTableWidgetItem(f'{data.quatOrientation.z:.5f}'))
        self.euler_table.setItem(0, 0, QTableWidgetItem(f'{data.eulerOrientation.roll:.5f}'))
        self.euler_table.setItem(0, 1, QTableWidgetItem(f'{data.eulerOrientation.pitch:.5f}'))
        self.euler_table.setItem(0, 2, QTableWidgetItem(f'{data.eulerOrientation.yaw:.5f}'))
        


    def updateData(self, data: ImuData):
        self.data.append(data)
        self.slider.setRange(0, len(self.data) - 1)
        self.slider.setValue(len(self.data) - 1)
        self.update_tables(len(self.data) - 1)


def create_formatted_table(rowHeaders: List[str], colHeaders: List[str]):
    table = QTableWidget()
    table.setRowCount(len(rowHeaders))
    table.setColumnCount(len(colHeaders))
    table.setHorizontalHeaderLabels(colHeaders)
    table.setVerticalHeaderLabels(rowHeaders)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return table

