import struct
from typing import List, Dict

import serial.tools.list_ports as list_ports
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QGridLayout,
    QTextEdit,
    QTableWidget,
    QVBoxLayout,
    QHBoxLayout,
    QHeaderView,
    QSlider,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
)
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

from data_structures import *
from data_view_publisher import DataViewPublisher
from sensor_data_collector import (
    SensorDataCollector,
    unpack_imu_data,
    imu_struct_format,
)
from serial_example_code import read_serial_data
from style_sheets import *
from widgets import DataPageInterface


class RawDataPage(DataPageInterface):
    def __init__(self, data_source: DataViewPublisher):
        super().__init__()
        self.sensor_data_collector = SensorDataCollector()
        self.data_source = data_source
        self.data_source.subscribe(self)
        self.data: List[ImuData] = []
        self.ports = [port.device for port in list_ports.comports()]
        self.record_data = False

        self.port_dropdown = QComboBox()
        self.record_button = QPushButton()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_data)
        self.timer.start(100)

        self.setup()

    def capture_data(self):
        if self.record_data:
            data = read_serial_data(self.port_dropdown.currentText())
            unpacked: ImuData = unpack_imu_data(data)

            print(unpacked.accelData.z)

            self.update_data(unpacked)

    def toggle_recording(self):
        self.record_data = not self.record_data

    def setup(self):
        layout = QGridLayout()
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setup_graphs()
        self.setup_table()

        self.raw_data_2 = QTextEdit()
        self.raw_data_2.setText("Placeholder text")
        self.raw_data_2.setReadOnly(True)
        self.raw_data_2.setStyleSheet(PLACEHOLDER_STYLE_SHEET)

        self.port_dropdown.addItems(self.ports)

        self.record_button.setText("Start/stop recording")
        self.record_button.clicked.connect(self.toggle_recording)

        layout.addWidget(self.canvas1, 0, 1)
        layout.addWidget(self.canvas2, 1, 1)
        layout.addLayout(self.tables_imu, 0, 0)
        layout.addWidget(self.raw_data_2, 1, 0)
        layout.addWidget(self.port_dropdown, 2, 0)
        layout.addWidget(self.record_button, 2, 1)

        # ==== end of example ====
        self.setLayout(layout)

    def setup_graphs(self):
        self.fig1 = Figure()
        self.canvas1 = Canvas(self.fig1)
        self.accel_axes = self.fig1.add_subplot(2, 2, 1)
        self.linear_accel_axes = self.fig1.add_subplot(2, 2, 2)
        self.gravity_accel_axes = self.fig1.add_subplot(2, 2, 3)
        self.gyro_axes = self.fig1.add_subplot(2, 2, 4)
        self.fig1.tight_layout()

        self.fig2 = Figure()
        self.canvas2 = Canvas(self.fig2)
        self.mag_axes = self.fig2.add_subplot(2, 2, 1)
        self.position_axes = self.fig2.add_subplot(2, 2, 2)
        self.quat_axes = self.fig2.add_subplot(2, 2, 3)
        self.euler_axes = self.fig2.add_subplot(2, 2, 4)
        self.fig2.tight_layout()

        self.axes_to_name_mapping = {
            self.accel_axes: "accelData",
            self.linear_accel_axes: "linearAccelData",
            self.gravity_accel_axes: "gravityAccel",
            self.gyro_axes: "gyroData",
            self.mag_axes: "magData",
            self.position_axes: "position",
            self.quat_axes: "quatOrientation",
            self.euler_axes: "eulerOrientation",
        }

        format_axes(self.axes_to_name_mapping)

    def setup_table(self):
        layout = QVBoxLayout()

        self.axis3d_table = create_formatted_table(
            rowHeaders=[
                "accelData",
                "linearAccelData",
                "gravityAccel",
                "gyroData",
                "magData",
            ],
            colHeaders=["x", "y", "z"],
        )

        self.position_table = create_formatted_table(
            rowHeaders=["x", "y", "z"], colHeaders=["position"]
        )

        self.quat_table = create_formatted_table(
            rowHeaders=["w", "x", "y", "z"], colHeaders=["quat orientation"]
        )

        self.euler_table = create_formatted_table(
            rowHeaders=["roll", "pitch", "yaw"], colHeaders=["euler orientation"]
        )

        position_tables_layout = QHBoxLayout()
        position_tables_layout.addWidget(self.position_table)
        position_tables_layout.addWidget(self.quat_table)
        position_tables_layout.addWidget(self.euler_table)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
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
        self.axis3d_table.setItem(row, 0, QTableWidgetItem(f"{data.x:.5f}"))
        self.axis3d_table.setItem(row, 1, QTableWidgetItem(f"{data.y:.5f}"))
        self.axis3d_table.setItem(row, 2, QTableWidgetItem(f"{data.z:.5f}"))

    def populate_position(self, data: PositionData):
        self.position_table.setItem(0, 0, QTableWidgetItem(f"{data.position.x:.5f}"))
        self.position_table.setItem(0, 1, QTableWidgetItem(f"{data.position.y:.5f}"))
        self.position_table.setItem(0, 2, QTableWidgetItem(f"{data.position.z:.5f}"))
        self.quat_table.setItem(0, 0, QTableWidgetItem(f"{data.quatOrientation.w:.5f}"))
        self.quat_table.setItem(0, 1, QTableWidgetItem(f"{data.quatOrientation.x:.5f}"))
        self.quat_table.setItem(0, 2, QTableWidgetItem(f"{data.quatOrientation.y:.5f}"))
        self.quat_table.setItem(0, 3, QTableWidgetItem(f"{data.quatOrientation.z:.5f}"))
        self.euler_table.setItem(
            0, 0, QTableWidgetItem(f"{data.eulerOrientation.roll:.5f}")
        )
        self.euler_table.setItem(
            0, 1, QTableWidgetItem(f"{data.eulerOrientation.pitch:.5f}")
        )
        self.euler_table.setItem(
            0, 2, QTableWidgetItem(f"{data.eulerOrientation.yaw:.5f}")
        )

    def update_data(self, data: ImuData):
        self.data.append(data)
        self.slider.setRange(0, len(self.data) - 1)
        self.slider.setValue(len(self.data) - 1)
        self.update_tables(len(self.data) - 1)
        self.update_graphs()

    def update_graphs(self):
        for ax in self.fig1.axes + self.fig2.axes:
            name = self.axes_to_name_mapping[ax]
            ax.cla()
            if name not in ["quatOrientation", "eulerOrientation"]:
                data_to_plot = [
                    (
                        getattr(imudata, name)
                        if name != "position"
                        else imudata.positionData.position
                    )
                    for imudata in self.data
                ]
                # data_to_plot = [getattr(imudata, name) for imudata in self.data if name ]
                x = [data.x for data in data_to_plot]
                y = [data.y for data in data_to_plot]
                z = [data.z for data in data_to_plot]
                ln1 = ax.plot(x, color="r")
                ln2 = ax.plot(y, color="b")
                ln3 = ax.plot(z, color="g")
                ax.set_title(name, fontsize=5)
                ax.legend(["x", "y", "z"], fontsize=5, loc="upper right")
            elif name == "quatOrientation":
                data_to_plot = [
                    imudata.positionData.quatOrientation for imudata in self.data
                ]
                w = [data.w for data in data_to_plot]
                x = [data.x for data in data_to_plot]
                y = [data.y for data in data_to_plot]
                z = [data.z for data in data_to_plot]
                ax.plot(w, color="k")
                ax.plot(x, color="r")
                ax.plot(y, color="g")
                ax.plot(z, color="b")
                ax.legend(["w", "x", "y", "z"], fontsize=5, loc="upper right")
            elif name == "eulerOrientation":
                data_to_plot = [
                    imudata.positionData.eulerOrientation for imudata in self.data
                ]
                roll = [data.roll for data in data_to_plot]
                pitch = [data.pitch for data in data_to_plot]
                yaw = [data.yaw for data in data_to_plot]
                ax.plot(roll, color="r")
                ax.plot(pitch, color="g")
                ax.plot(yaw, color="b")
                ax.legend(["roll", "pitch", "yaw"], fontsize=5, loc="upper right")
                # ax.draw_artist(ln1)
                # ax.draw_artist(ln2)
                # ax.draw_artist(ln3)
        # self.fig1.canvas.blit(self.fig1.bbox)
        # self.fig1.canvas.flush_events()
        self.canvas1.draw()
        self.canvas2.draw()


def create_formatted_table(rowHeaders: List[str], colHeaders: List[str]):
    table = QTableWidget()
    table.setRowCount(len(rowHeaders))
    table.setColumnCount(len(colHeaders))
    table.setHorizontalHeaderLabels(colHeaders)
    table.setVerticalHeaderLabels(rowHeaders)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    return table


def format_axes(axes: Dict[Axes, str]):
    for axis, name in axes.items():
        axis.tick_params(axis="both", labelsize=5)
        axis.set_title(name, fontsize=5)
